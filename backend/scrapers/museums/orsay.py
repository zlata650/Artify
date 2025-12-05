"""
🎭 Artify - Musée d'Orsay Scraper
Scrapes exhibitions and events from musee-orsay.fr
"""

import re
from typing import Generator, Optional, List
from urllib.parse import urljoin
from datetime import datetime

from backend.core.models import ScrapedEvent
from backend.scrapers.base import HTMLScraper, ScraperConfig


class OrsayScraper(HTMLScraper):
    """
    Scraper for Musée d'Orsay events and exhibitions.
    """
    
    BASE_URL = "https://www.musee-orsay.fr"
    EXHIBITIONS_URL = "https://www.musee-orsay.fr/fr/expositions"
    AGENDA_URL = "https://www.musee-orsay.fr/fr/agenda"
    
    def __init__(self, max_events: int = 100):
        config = ScraperConfig(
            name="orsay",
            source_url=self.EXHIBITIONS_URL,
            source_type="museum",
            category_hint="arts_visuels",
            requires_playwright=True,
            rate_limit_seconds=2.0,
            max_events=max_events,
        )
        super().__init__(config)
    
    def scrape(self) -> Generator[ScrapedEvent, None, None]:
        """Scrape exhibitions and events."""
        # Exhibitions
        html = self.fetch_page(self.EXHIBITIONS_URL)
        if html:
            soup = self.parse_html(html)
            if soup:
                for event in self._scrape_listing(soup, 'exposition'):
                    yield event
        
        # Agenda
        html = self.fetch_page(self.AGENDA_URL)
        if html:
            soup = self.parse_html(html)
            if soup:
                for event in self._scrape_listing(soup, 'event'):
                    yield event
    
    def _scrape_listing(self, soup, event_type: str) -> Generator[ScrapedEvent, None, None]:
        """Scrape a listing page."""
        urls = self.get_event_urls(soup)
        
        for url in urls:
            html = self.fetch_page(url)
            if html:
                event_soup = self.parse_html(html)
                if event_soup:
                    event = self.parse_event_page(event_soup, url)
                    if event:
                        yield event
    
    def get_event_urls(self, soup) -> List[str]:
        """Extract event URLs."""
        urls = []
        
        selectors = [
            'a[href*="/expositions/"]',
            'a[href*="/agenda/"]',
            '.expo-card a',
            '.event-card a',
            '.article-link',
        ]
        
        for selector in selectors:
            for link in soup.select(selector):
                href = link.get('href', '')
                if href:
                    full_url = urljoin(self.BASE_URL, href)
                    if full_url not in urls:
                        urls.append(full_url)
        
        return urls[:40]
    
    def parse_event_page(self, soup, url: str) -> Optional[ScrapedEvent]:
        """Parse event details."""
        try:
            # Title
            title_el = soup.select_one('h1')
            title = title_el.get_text(strip=True) if title_el else None
            
            if not title:
                return None
            
            # Description
            desc_el = soup.select_one('.chapo, .introduction, .description, article p')
            description = desc_el.get_text(strip=True)[:1500] if desc_el else ''
            
            # Dates
            date_start = None
            date_end = None
            
            date_el = soup.select_one('.dates, .date-range')
            if date_el:
                dates = self._parse_french_date_range(date_el.get_text())
                if dates:
                    date_start, date_end = dates
            
            if not date_start:
                text = soup.get_text()
                pattern = r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})'
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    date_start = self._parse_single_date(match.group(0))
            
            # Location
            location_name = "Musée d'Orsay"
            address = "1 Rue de la Légion d'Honneur, 75007 Paris"
            
            # Price
            price_from = 16.0  # Default Orsay ticket
            is_free = False
            
            price_el = soup.select_one('.price, .tarif')
            if price_el:
                price_text = price_el.get_text().lower()
                if 'gratuit' in price_text:
                    is_free = True
                    price_from = 0
                else:
                    prices = re.findall(r'(\d+(?:[.,]\d{2})?)\s*€', price_text)
                    if prices:
                        price_from = min(float(p.replace(',', '.')) for p in prices)
            
            # Image
            img_el = soup.select_one('.hero img, .visual img, figure img')
            image_url = None
            if img_el:
                image_url = img_el.get('src') or img_el.get('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(url, image_url)
            
            # Ticket
            ticket_url = "https://www.musee-orsay.fr/fr/informations-pratiques/tarifs"
            
            return ScrapedEvent(
                title=title,
                description=description,
                source_name='orsay',
                source_event_url=url,
                date_start=date_start or datetime.now().strftime('%Y-%m-%d'),
                date_end=date_end,
                location_name=location_name,
                address=address,
                price_from=price_from,
                is_free=is_free,
                image_url=image_url,
                ticket_url=ticket_url,
                has_direct_ticket_button=True,
                raw_category='exposition',
                raw_tags=['musee', 'orsay', 'impressionnisme', 'art'],
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to parse {url}: {e}")
            return None
    
    def _parse_french_date_range(self, text: str) -> Optional[tuple]:
        """Parse French date range."""
        months = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12,
        }
        
        pattern = r'(\d{1,2})\s+(' + '|'.join(months.keys()) + r')\s*(\d{4})?'
        matches = re.findall(pattern, text.lower())
        
        year = datetime.now().year
        year_match = re.search(r'\b(20\d{2})\b', text)
        if year_match:
            year = int(year_match.group(1))
        
        if len(matches) >= 2:
            d1, m1, y1 = matches[0]
            d2, m2, y2 = matches[1]
            
            date1 = f"{int(y1) if y1 else year}-{months[m1]:02d}-{int(d1):02d}"
            date2 = f"{int(y2) if y2 else year}-{months[m2]:02d}-{int(d2):02d}"
            return date1, date2
        elif len(matches) == 1:
            d, m, y = matches[0]
            date = f"{int(y) if y else year}-{months[m]:02d}-{int(d):02d}"
            return date, None
        
        return None
    
    def _parse_single_date(self, text: str) -> Optional[str]:
        """Parse a single date."""
        result = self._parse_french_date_range(text)
        return result[0] if result else None


def scrape_orsay(max_events: int = 100) -> List:
    """Scrape Orsay events."""
    with OrsayScraper(max_events=max_events) as scraper:
        return scraper.scrape_all()

