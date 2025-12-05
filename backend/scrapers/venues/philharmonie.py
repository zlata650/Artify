"""
🎭 Artify - Philharmonie de Paris Scraper
Scrapes concerts and events from philharmoniedeparis.fr
"""

import re
import json
from typing import Generator, Optional, Dict, List
from urllib.parse import urljoin
from datetime import datetime

from backend.core.models import ScrapedEvent
from backend.scrapers.base import HTMLScraper, ScraperConfig


class PhilharmonieScraper(HTMLScraper):
    """
    Scraper for Philharmonie de Paris events.
    
    Covers:
    - Grande salle Pierre Boulez
    - Salle des concerts - Cité de la musique
    - Various smaller halls
    """
    
    BASE_URL = "https://philharmoniedeparis.fr"
    AGENDA_URL = "https://philharmoniedeparis.fr/fr/agenda"
    
    def __init__(self, max_events: int = 100):
        config = ScraperConfig(
            name="philharmonie",
            source_url=self.AGENDA_URL,
            source_type="venue",
            category_hint="musique",  # Most events are music
            requires_playwright=True,  # Uses JavaScript
            rate_limit_seconds=1.5,
            max_events=max_events,
        )
        super().__init__(config)
    
    def get_listing_url(self, page: int = 1) -> str:
        """Get listing URL with pagination."""
        if page > 1:
            return f"{self.AGENDA_URL}?page={page}"
        return self.AGENDA_URL
    
    def get_event_urls(self, soup) -> List[str]:
        """Extract event URLs from listing page."""
        urls = []
        
        # Philharmonie event links
        selectors = [
            'a[href*="/fr/activite/"]',
            '.event-card a',
            '.agenda-item a',
            '.concert-link',
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                if '/activite/' in href or '/concert/' in href:
                    full_url = urljoin(self.BASE_URL, href)
                    if full_url not in urls:
                        urls.append(full_url)
        
        return urls[:40]
    
    def parse_event_page(self, soup, url: str) -> Optional[ScrapedEvent]:
        """Parse event details from event page."""
        try:
            # Title
            title_el = soup.select_one('h1, .event-title, .concert-title')
            title = title_el.get_text(strip=True) if title_el else None
            
            if not title:
                return None
            
            # Description
            desc_el = soup.select_one('.event-description, .concert-description, .content-text')
            description = ''
            if desc_el:
                description = desc_el.get_text(strip=True)[:1500]
            
            # Date and time
            date_start = None
            time_start = None
            
            # Look for structured date
            date_el = soup.select_one('[datetime], .event-date, .concert-date')
            if date_el:
                datetime_attr = date_el.get('datetime')
                if datetime_attr:
                    try:
                        dt = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                        date_start = dt.strftime('%Y-%m-%d')
                        time_start = dt.strftime('%H:%M')
                    except:
                        pass
            
            # Fallback date parsing
            if not date_start:
                date_text = soup.get_text()
                # French date pattern
                date_pattern = r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})'
                match = re.search(date_pattern, date_text, re.IGNORECASE)
                if match:
                    date_start = self._parse_french_date(match.group(0))
            
            # Time pattern
            if not time_start:
                time_pattern = r'(\d{1,2})[h:](\d{2})'
                time_match = re.search(time_pattern, soup.get_text())
                if time_match:
                    time_start = f"{time_match.group(1).zfill(2)}:{time_match.group(2)}"
            
            # Location - always Philharmonie
            location_name = "Philharmonie de Paris"
            address = "221 avenue Jean-Jaurès, 75019 Paris"
            
            # Check for specific hall
            hall_el = soup.select_one('.hall, .salle, .venue-name')
            if hall_el:
                hall_name = hall_el.get_text(strip=True)
                if hall_name and hall_name != location_name:
                    location_name = f"Philharmonie de Paris - {hall_name}"
            
            # Price
            price_from = None
            is_free = False
            
            price_el = soup.select_one('.price, .tarif, .prix')
            if price_el:
                price_text = price_el.get_text().lower()
                if 'gratuit' in price_text or 'libre' in price_text:
                    is_free = True
                    price_from = 0
                else:
                    # Extract lowest price
                    prices = re.findall(r'(\d+(?:[.,]\d{2})?)\s*€', price_text)
                    if prices:
                        price_from = min(float(p.replace(',', '.')) for p in prices)
            
            # Image
            img_el = soup.select_one('.event-image img, .concert-image img, .main-visual img')
            image_url = None
            if img_el:
                image_url = img_el.get('src') or img_el.get('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(url, image_url)
            
            # Ticket URL - Philharmonie has direct booking
            ticket_url = url
            has_ticket = False
            
            for link in soup.select('a[href]'):
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                if 'billet' in href or 'billet' in text or 'réserv' in text:
                    ticket_url = urljoin(url, link.get('href'))
                    has_ticket = True
                    break
            
            # Determine sub-category based on content
            sub_category = 'classique'  # Default for Philharmonie
            text_lower = (title + ' ' + description).lower()
            
            if any(w in text_lower for w in ['jazz', 'blues']):
                sub_category = 'jazz'
            elif any(w in text_lower for w in ['world', 'monde', 'africa', 'latin']):
                sub_category = 'world'
            elif any(w in text_lower for w in ['pop', 'rock', 'électro', 'electro']):
                sub_category = 'pop'
            elif any(w in text_lower for w in ['opéra', 'opera']):
                sub_category = 'opera'
            elif any(w in text_lower for w in ['symphon', 'orchestre', 'concerto']):
                sub_category = 'symphonique'
            
            return ScrapedEvent(
                title=title,
                description=description,
                source_name='philharmonie',
                source_event_url=url,
                date_start=date_start,
                time_start=time_start,
                location_name=location_name,
                address=address,
                price_from=price_from,
                is_free=is_free,
                image_url=image_url,
                ticket_url=ticket_url,
                has_direct_ticket_button=has_ticket or True,  # Philharmonie always has tickets
                raw_category='classique',
                raw_tags=[sub_category, 'concert', 'philharmonie'],
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


# Convenience function
def scrape_philharmonie(max_events: int = 100) -> List:
    """Scrape Philharmonie de Paris events."""
    with PhilharmonieScraper(max_events=max_events) as scraper:
        return scraper.scrape_all()

