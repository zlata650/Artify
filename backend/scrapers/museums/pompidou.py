"""
🎭 Artify - Centre Pompidou Scraper
Scrapes exhibitions and events from centrepompidou.fr
"""

import re
from typing import Generator, Optional, List
from urllib.parse import urljoin
from datetime import datetime

from backend.core.models import ScrapedEvent
from backend.scrapers.base import HTMLScraper, ScraperConfig


class PompidouScraper(HTMLScraper):
    """
    Scraper for Centre Pompidou events and exhibitions.
    """
    
    BASE_URL = "https://www.centrepompidou.fr"
    EXHIBITIONS_URL = "https://www.centrepompidou.fr/fr/programme/agenda"
    
    def __init__(self, max_events: int = 100):
        config = ScraperConfig(
            name="pompidou",
            source_url=self.EXHIBITIONS_URL,
            source_type="museum",
            category_hint="arts_visuels",
            requires_playwright=True,
            rate_limit_seconds=2.0,
            max_events=max_events,
        )
        super().__init__(config)
    
    def get_event_urls(self, soup) -> List[str]:
        """Extract event URLs."""
        urls = []
        
        selectors = [
            'a[href*="/exposition/"]',
            'a[href*="/evenement/"]',
            'a[href*="/spectacle/"]',
            '.event-card a',
            '.card-link',
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
            desc_el = soup.select_one('.introduction, .description, .chapo')
            description = desc_el.get_text(strip=True)[:1500] if desc_el else ''
            
            # Dates
            date_start = None
            date_end = None
            
            date_el = soup.select_one('.dates, .event-dates')
            if date_el:
                date_text = date_el.get_text()
                dates = self._parse_french_dates(date_text)
                if dates:
                    date_start, date_end = dates
            
            if not date_start:
                date_start = datetime.now().strftime('%Y-%m-%d')
            
            # Location
            location_name = "Centre Pompidou"
            address = "Place Georges-Pompidou, 75004 Paris"
            
            # Price
            price_from = 15.0  # Default Pompidou ticket
            is_free = False
            
            price_el = soup.select_one('.price, .tarif')
            if price_el:
                price_text = price_el.get_text().lower()
                if 'gratuit' in price_text or 'libre' in price_text:
                    is_free = True
                    price_from = 0
                else:
                    prices = re.findall(r'(\d+(?:[.,]\d{2})?)\s*€', price_text)
                    if prices:
                        price_from = min(float(p.replace(',', '.')) for p in prices)
            
            # Image
            img_el = soup.select_one('.visual img, .hero img, figure img')
            image_url = None
            if img_el:
                image_url = img_el.get('src') or img_el.get('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(url, image_url)
            
            # Ticket
            ticket_url = "https://billetterie.centrepompidou.fr/"
            
            for link in soup.select('a[href*="billet"], a[href*="ticket"]'):
                href = link.get('href', '')
                if href:
                    ticket_url = urljoin(url, href)
                    break
            
            # Category
            raw_category = 'exposition'
            text_lower = (title + ' ' + description).lower()
            
            if any(w in text_lower for w in ['concert', 'musique']):
                raw_category = 'concert'
            elif any(w in text_lower for w in ['cinéma', 'film']):
                raw_category = 'cinema'
            elif any(w in text_lower for w in ['performance', 'spectacle']):
                raw_category = 'spectacle'
            
            return ScrapedEvent(
                title=title,
                description=description,
                source_name='pompidou',
                source_event_url=url,
                date_start=date_start,
                date_end=date_end,
                location_name=location_name,
                address=address,
                price_from=price_from,
                is_free=is_free,
                image_url=image_url,
                ticket_url=ticket_url,
                has_direct_ticket_button=True,
                raw_category=raw_category,
                raw_tags=['musee', 'pompidou', 'art_contemporain', 'moderne'],
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to parse {url}: {e}")
            return None
    
    def _parse_french_dates(self, text: str) -> Optional[tuple]:
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
        
        if matches:
            d, m, y = matches[0]
            date1 = f"{int(y) if y else year}-{months[m]:02d}-{int(d):02d}"
            
            if len(matches) > 1:
                d2, m2, y2 = matches[-1]
                date2 = f"{int(y2) if y2 else year}-{months[m2]:02d}-{int(d2):02d}"
                return date1, date2
            
            return date1, None
        
        return None


def scrape_pompidou(max_events: int = 100) -> List:
    """Scrape Pompidou events."""
    with PompidouScraper(max_events=max_events) as scraper:
        return scraper.scrape_all()

