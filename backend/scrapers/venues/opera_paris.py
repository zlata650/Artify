"""
🎭 Artify - Opéra de Paris Scraper
Scrapes events from Opéra Garnier and Opéra Bastille
"""

import re
from typing import Generator, Optional, Dict, List
from urllib.parse import urljoin
from datetime import datetime

from backend.core.models import ScrapedEvent
from backend.scrapers.base import HTMLScraper, ScraperConfig


class OperaParisScraper(HTMLScraper):
    """
    Scraper for Opéra National de Paris events.
    
    Covers:
    - Opéra Bastille
    - Palais Garnier (Opéra Garnier)
    """
    
    BASE_URL = "https://www.operadeparis.fr"
    AGENDA_URL = "https://www.operadeparis.fr/saison-24-25"
    
    def __init__(self, max_events: int = 100):
        config = ScraperConfig(
            name="opera_paris",
            source_url=self.AGENDA_URL,
            source_type="venue",
            category_hint="spectacles",
            requires_playwright=True,
            rate_limit_seconds=2.0,
            max_events=max_events,
        )
        super().__init__(config)
    
    def get_event_urls(self, soup) -> List[str]:
        """Extract event URLs from listing page."""
        urls = []
        
        selectors = [
            'a[href*="/spectacle/"]',
            'a[href*="/opera/"]',
            'a[href*="/ballet/"]',
            '.show-card a',
            '.event-link',
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                if href and ('/spectacle/' in href or '/opera/' in href or '/ballet/' in href):
                    full_url = urljoin(self.BASE_URL, href)
                    if full_url not in urls:
                        urls.append(full_url)
        
        return urls[:50]
    
    def parse_event_page(self, soup, url: str) -> Optional[ScrapedEvent]:
        """Parse event details from event page."""
        try:
            # Title
            title_el = soup.select_one('h1, .show-title, .spectacle-titre')
            title = title_el.get_text(strip=True) if title_el else None
            
            if not title:
                return None
            
            # Description
            desc_el = soup.select_one('.show-description, .synopsis, .presentation')
            description = desc_el.get_text(strip=True)[:1500] if desc_el else ''
            
            # Date
            date_start = None
            time_start = None
            
            date_el = soup.select_one('.show-dates, .dates, [datetime]')
            if date_el:
                datetime_attr = date_el.get('datetime')
                if datetime_attr:
                    try:
                        dt = datetime.fromisoformat(datetime_attr)
                        date_start = dt.strftime('%Y-%m-%d')
                        time_start = dt.strftime('%H:%M')
                    except:
                        pass
                else:
                    date_text = date_el.get_text()
                    date_start = self._parse_french_date(date_text)
            
            # Fallback date parsing
            if not date_start:
                text = soup.get_text()
                date_pattern = r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})'
                match = re.search(date_pattern, text, re.IGNORECASE)
                if match:
                    date_start = self._parse_french_date(match.group(0))
            
            # Location
            location_name = "Opéra de Paris"
            address = "Paris"
            
            # Detect which venue
            text_lower = soup.get_text().lower()
            if 'bastille' in text_lower:
                location_name = "Opéra Bastille"
                address = "Place de la Bastille, 75012 Paris"
            elif 'garnier' in text_lower or 'palais garnier' in text_lower:
                location_name = "Palais Garnier"
                address = "Place de l'Opéra, 75009 Paris"
            
            # Price
            price_from = None
            is_free = False
            
            price_el = soup.select_one('.price, .tarif, .prix')
            if price_el:
                price_text = price_el.get_text().lower()
                prices = re.findall(r'(\d+(?:[.,]\d{2})?)\s*€', price_text)
                if prices:
                    price_from = min(float(p.replace(',', '.')) for p in prices)
            
            # Image
            img_el = soup.select_one('.show-image img, .visual img, picture img')
            image_url = None
            if img_el:
                image_url = img_el.get('src') or img_el.get('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(url, image_url)
            
            # Ticket URL
            ticket_url = url
            has_ticket = False
            
            for link in soup.select('a[href*="billet"], a[href*="reserv"], .booking-button'):
                href = link.get('href', '')
                if href:
                    ticket_url = urljoin(url, href)
                    has_ticket = True
                    break
            
            # Determine sub-category
            sub_category = 'opera'
            if 'ballet' in title.lower() or 'danse' in title.lower():
                sub_category = 'ballet'
            elif 'récital' in title.lower() or 'recital' in title.lower():
                sub_category = 'classique'
            
            return ScrapedEvent(
                title=title,
                description=description,
                source_name='opera_paris',
                source_event_url=url,
                date_start=date_start,
                time_start=time_start,
                location_name=location_name,
                address=address,
                price_from=price_from,
                is_free=is_free,
                image_url=image_url,
                ticket_url=ticket_url,
                has_direct_ticket_button=has_ticket or True,
                raw_category=sub_category,
                raw_tags=[sub_category, 'opera', 'spectacle'],
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to parse {url}: {e}")
            return None
    
    def _parse_french_date(self, date_text: str) -> Optional[str]:
        """Parse French date format to ISO date."""
        months = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12,
        }
        
        pattern = r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})'
        match = re.search(pattern, date_text.lower())
        
        if match:
            day = int(match.group(1))
            month = months.get(match.group(2), 1)
            year = int(match.group(3))
            return f"{year}-{month:02d}-{day:02d}"
        
        return None


def scrape_opera_paris(max_events: int = 100) -> List:
    """Scrape Opéra de Paris events."""
    with OperaParisScraper(max_events=max_events) as scraper:
        return scraper.scrape_all()

