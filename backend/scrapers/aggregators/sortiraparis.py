"""
🎭 Artify - Sortir à Paris Scraper
Scrapes events from sortiraparis.com
"""

import re
from typing import Generator, Optional, List
from urllib.parse import urljoin
from datetime import datetime

from backend.core.models import ScrapedEvent
from backend.scrapers.base import HTMLScraper, ScraperConfig


class SortirAParisScraper(HTMLScraper):
    """
    Scraper for Sortir à Paris events.
    
    Covers multiple categories: concerts, expositions, spectacles, etc.
    """
    
    CATEGORY_URLS = {
        'concerts': 'https://www.sortiraparis.com/scenes/concert',
        'expositions': 'https://www.sortiraparis.com/arts-culture/exposition',
        'spectacles': 'https://www.sortiraparis.com/scenes/spectacle',
        'theatre': 'https://www.sortiraparis.com/scenes/theatre',
        'ateliers': 'https://www.sortiraparis.com/loisirs/atelier-stage',
        'soirees': 'https://www.sortiraparis.com/soirees',
    }
    
    CATEGORY_MAPPING = {
        'concerts': 'musique',
        'expositions': 'arts_visuels',
        'spectacles': 'spectacles',
        'theatre': 'spectacles',
        'ateliers': 'ateliers',
        'soirees': 'nightlife',
    }
    
    def __init__(self, categories: List[str] = None, max_events: int = 100):
        config = ScraperConfig(
            name="sortiraparis",
            source_url="https://www.sortiraparis.com",
            source_type="aggregator",
            requires_playwright=False,
            rate_limit_seconds=1.0,
            max_events=max_events,
        )
        super().__init__(config)
        self.categories = categories or list(self.CATEGORY_URLS.keys())
        self.current_category = None
    
    def scrape(self) -> Generator[ScrapedEvent, None, None]:
        """Scrape events from multiple categories."""
        for category in self.categories:
            if category not in self.CATEGORY_URLS:
                continue
            
            self.current_category = category
            self.config.source_url = self.CATEGORY_URLS[category]
            self.config.category_hint = self.CATEGORY_MAPPING.get(category)
            
            self.logger.info(f"📂 Scraping category: {category}")
            
            # Get listing page
            html = self.fetch_page(self.config.source_url)
            if not html:
                continue
            
            soup = self.parse_html(html)
            if not soup:
                continue
            
            event_urls = self.get_event_urls(soup)
            
            for url in event_urls:
                event_html = self.fetch_page(url)
                if not event_html:
                    continue
                
                event_soup = self.parse_html(event_html)
                if not event_soup:
                    continue
                
                event = self.parse_event_page(event_soup, url)
                if event:
                    yield event
    
    def get_listing_url(self, page: int = 1) -> str:
        """Get listing URL."""
        return self.config.source_url
    
    def get_event_urls(self, soup) -> List[str]:
        """Extract event URLs from listing page."""
        urls = []
        
        # Sortir à Paris article links
        selectors = [
            'article a[href*="/"]',
            '.article-item a',
            '.card a[href]',
            '.listing-item a',
            'a.stretched-link',
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                # Filter for event pages
                if (href and '/guide/' not in href and '/videos/' not in href 
                    and href.startswith('/')):
                    full_url = urljoin(self.config.source_url, href)
                    if full_url not in urls:
                        urls.append(full_url)
        
        return urls[:30]  # Limit per category
    
    def parse_event_page(self, soup, url: str) -> Optional[ScrapedEvent]:
        """Parse event details from event page."""
        try:
            # Title
            title_el = soup.select_one('h1, .article-title')
            title = title_el.get_text(strip=True) if title_el else None
            
            if not title:
                return None
            
            # Description
            desc_el = soup.select_one('.article-content, .article-text, .chapeau')
            description = ''
            if desc_el:
                description = desc_el.get_text(strip=True)[:1500]
            
            # Date parsing
            date_start = None
            date_end = None
            time_start = None
            
            date_el = soup.select_one('.date, .event-date, [itemprop="startDate"]')
            if date_el:
                date_text = date_el.get_text(strip=True)
                date_start = self._parse_french_date(date_text)
            
            # Look for date in page text
            if not date_start:
                date_pattern = r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})'
                match = re.search(date_pattern, soup.get_text(), re.IGNORECASE)
                if match:
                    date_start = self._parse_french_date(match.group(0))
            
            # Time
            time_pattern = r'(\d{1,2})[h:](\d{2})'
            time_match = re.search(time_pattern, soup.get_text())
            if time_match:
                time_start = f"{time_match.group(1).zfill(2)}:{time_match.group(2)}"
            
            # Location
            location_el = soup.select_one('.lieu, .location, [itemprop="location"]')
            location_name = location_el.get_text(strip=True) if location_el else 'Paris'
            
            address_el = soup.select_one('.adresse, .address, [itemprop="address"]')
            address = address_el.get_text(strip=True) if address_el else ''
            
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
                    price_match = re.search(r'(\d+(?:[.,]\d{2})?)\s*€', price_text)
                    if price_match:
                        price_from = float(price_match.group(1).replace(',', '.'))
            
            # Image
            img_el = soup.select_one('.article-image img, .main-image img, [itemprop="image"]')
            image_url = None
            if img_el:
                image_url = img_el.get('src') or img_el.get('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(url, image_url)
            
            # Ticket URL - look for booking links
            ticket_url = url
            has_ticket = False
            
            ticket_patterns = ['billet', 'ticket', 'réserv', 'achat']
            for link in soup.select('a[href]'):
                href = link.get('href', '')
                text = link.get_text().lower()
                if any(p in text for p in ticket_patterns) or any(p in href.lower() for p in ticket_patterns):
                    ticket_url = urljoin(url, href) if not href.startswith('http') else href
                    has_ticket = True
                    break
            
            return ScrapedEvent(
                title=title,
                description=description,
                source_name='sortiraparis',
                source_event_url=url,
                date_start=date_start,
                date_end=date_end,
                time_start=time_start,
                location_name=location_name,
                address=address,
                price_from=price_from,
                is_free=is_free,
                image_url=image_url,
                ticket_url=ticket_url,
                has_direct_ticket_button=has_ticket,
                raw_category=self.current_category,
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
def scrape_sortiraparis(categories: List[str] = None, max_events: int = 100) -> List:
    """Scrape Sortir à Paris events."""
    with SortirAParisScraper(categories=categories, max_events=max_events) as scraper:
        return scraper.scrape_all()

