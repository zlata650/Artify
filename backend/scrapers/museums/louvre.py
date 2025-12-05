"""
🎭 Artify - Louvre Museum Scraper
Scrapes exhibitions and events from louvre.fr
"""

import re
from typing import Generator, Optional, Dict, List
from urllib.parse import urljoin
from datetime import datetime

from backend.core.models import ScrapedEvent
from backend.scrapers.base import HTMLScraper, ScraperConfig


class LouvreScraper(HTMLScraper):
    """
    Scraper for Musée du Louvre events and exhibitions.
    
    Covers:
    - Temporary exhibitions
    - Concerts and performances
    - Guided tours
    - Special events
    """
    
    BASE_URL = "https://www.louvre.fr"
    EXHIBITIONS_URL = "https://www.louvre.fr/en/explore/exhibitions-events"
    AGENDA_URL = "https://www.louvre.fr/en/agenda"
    
    def __init__(self, max_events: int = 100):
        config = ScraperConfig(
            name="louvre",
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
        # Scrape exhibitions
        html = self.fetch_page(self.EXHIBITIONS_URL)
        if html:
            soup = self.parse_html(html)
            if soup:
                urls = self.get_event_urls(soup)
                for url in urls:
                    event_html = self.fetch_page(url)
                    if event_html:
                        event_soup = self.parse_html(event_html)
                        if event_soup:
                            event = self.parse_event_page(event_soup, url)
                            if event:
                                yield event
        
        # Also try agenda page
        html = self.fetch_page(self.AGENDA_URL)
        if html:
            soup = self.parse_html(html)
            if soup:
                urls = self.get_event_urls(soup)
                for url in urls:
                    event_html = self.fetch_page(url)
                    if event_html:
                        event_soup = self.parse_html(event_html)
                        if event_soup:
                            event = self.parse_event_page(event_soup, url)
                            if event:
                                yield event
    
    def get_event_urls(self, soup) -> List[str]:
        """Extract event URLs from listing page."""
        urls = []
        
        selectors = [
            'a[href*="/expositions/"]',
            'a[href*="/exhibitions/"]',
            'a[href*="/evenement/"]',
            'a[href*="/event/"]',
            '.exhibition-card a',
            '.event-card a',
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                if href and ('exposition' in href or 'exhibition' in href or 
                           'evenement' in href or 'event' in href):
                    full_url = urljoin(self.BASE_URL, href)
                    if full_url not in urls:
                        urls.append(full_url)
        
        return urls[:40]
    
    def parse_event_page(self, soup, url: str) -> Optional[ScrapedEvent]:
        """Parse exhibition/event details."""
        try:
            # Title
            title_el = soup.select_one('h1, .exhibition-title, .event-title')
            title = title_el.get_text(strip=True) if title_el else None
            
            if not title:
                return None
            
            # Description
            desc_el = soup.select_one('.exhibition-description, .event-description, .introduction, article p')
            description = desc_el.get_text(strip=True)[:1500] if desc_el else ''
            
            # Dates
            date_start = None
            date_end = None
            
            date_el = soup.select_one('.dates, .exhibition-dates, .event-date')
            if date_el:
                date_text = date_el.get_text()
                dates = self._parse_date_range(date_text)
                if dates:
                    date_start, date_end = dates
            
            # Fallback
            if not date_start:
                text = soup.get_text()
                date_pattern = r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December|janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})'
                match = re.search(date_pattern, text, re.IGNORECASE)
                if match:
                    date_start = self._parse_date(match.group(0))
            
            # Location
            location_name = "Musée du Louvre"
            address = "Rue de Rivoli, 75001 Paris"
            
            # Price
            price_from = None
            is_free = False
            
            price_el = soup.select_one('.price, .tarif, .ticket-price')
            if price_el:
                price_text = price_el.get_text().lower()
                if 'free' in price_text or 'gratuit' in price_text:
                    is_free = True
                    price_from = 0
                else:
                    prices = re.findall(r'(\d+(?:[.,]\d{2})?)\s*€', price_text)
                    if prices:
                        price_from = min(float(p.replace(',', '.')) for p in prices)
            
            # Default Louvre entry price
            if price_from is None:
                price_from = 17.0  # Standard Louvre ticket price
            
            # Image
            img_el = soup.select_one('.exhibition-image img, .hero-image img, figure img')
            image_url = None
            if img_el:
                image_url = img_el.get('src') or img_el.get('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(url, image_url)
            
            # Ticket URL
            ticket_url = "https://www.louvre.fr/en/visit/hours-admission"
            has_ticket = True
            
            for link in soup.select('a[href*="ticket"], a[href*="billet"], a[href*="visit"]'):
                href = link.get('href', '')
                if href:
                    ticket_url = urljoin(url, href)
                    break
            
            # Determine type
            raw_category = 'exposition'
            text_lower = (title + ' ' + description).lower()
            
            if any(w in text_lower for w in ['concert', 'musique', 'music']):
                raw_category = 'concert'
            elif any(w in text_lower for w in ['visite', 'visit', 'tour', 'guided']):
                raw_category = 'visite_guidee'
            elif any(w in text_lower for w in ['atelier', 'workshop']):
                raw_category = 'atelier'
            
            return ScrapedEvent(
                title=title,
                description=description,
                source_name='louvre',
                source_event_url=url,
                date_start=date_start or datetime.now().strftime('%Y-%m-%d'),
                date_end=date_end,
                location_name=location_name,
                address=address,
                price_from=price_from,
                is_free=is_free,
                image_url=image_url,
                ticket_url=ticket_url,
                has_direct_ticket_button=has_ticket,
                raw_category=raw_category,
                raw_tags=['musee', 'louvre', 'exposition', 'art'],
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to parse {url}: {e}")
            return None
    
    def _parse_date_range(self, text: str) -> Optional[tuple]:
        """Parse a date range like 'January 15 - March 20, 2025'."""
        # Try to find two dates
        months_en = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
        }
        months_fr = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12,
        }
        months = {**months_en, **months_fr}
        
        pattern = r'(\d{1,2})\s+(' + '|'.join(months.keys()) + r')\s*(\d{4})?'
        matches = re.findall(pattern, text.lower())
        
        if len(matches) >= 2:
            # Extract year from text if not in match
            year_match = re.search(r'\b(20\d{2})\b', text)
            year = int(year_match.group(1)) if year_match else datetime.now().year
            
            day1, month1, year1 = matches[0]
            day2, month2, year2 = matches[1]
            
            year1 = int(year1) if year1 else year
            year2 = int(year2) if year2 else year
            
            date1 = f"{year1}-{months[month1]:02d}-{int(day1):02d}"
            date2 = f"{year2}-{months[month2]:02d}-{int(day2):02d}"
            
            return date1, date2
        elif len(matches) == 1:
            year_match = re.search(r'\b(20\d{2})\b', text)
            year = int(year_match.group(1)) if year_match else datetime.now().year
            
            day, month, year_m = matches[0]
            year_val = int(year_m) if year_m else year
            date = f"{year_val}-{months[month]:02d}-{int(day):02d}"
            return date, None
        
        return None
    
    def _parse_date(self, text: str) -> Optional[str]:
        """Parse a single date."""
        result = self._parse_date_range(text)
        if result:
            return result[0]
        return None


def scrape_louvre(max_events: int = 100) -> List:
    """Scrape Louvre events."""
    with LouvreScraper(max_events=max_events) as scraper:
        return scraper.scrape_all()

