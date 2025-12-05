"""
🎭 Artify - Generic Gallery Scraper Template
Extensible template for scraping art galleries in Paris
"""

import re
from typing import Generator, Optional, List, Dict
from urllib.parse import urljoin
from datetime import datetime

from backend.core.models import ScrapedEvent
from backend.scrapers.base import HTMLScraper, ScraperConfig


# Known Paris galleries and their configurations
PARIS_GALLERIES = [
    {
        'name': 'galerie_perrotin',
        'base_url': 'https://www.perrotin.com',
        'agenda_url': 'https://www.perrotin.com/exhibitions/current/paris',
        'selectors': {
            'event_links': 'a[href*="/exhibitions/"]',
            'title': 'h1',
            'description': '.exhibition-description',
            'dates': '.exhibition-dates',
            'image': '.exhibition-image img',
        },
        'address': '76 Rue de Turenne, 75003 Paris',
    },
    {
        'name': 'galerie_thaddaeus_ropac',
        'base_url': 'https://ropac.net',
        'agenda_url': 'https://ropac.net/exhibitions/paris-marais',
        'selectors': {
            'event_links': 'a[href*="/exhibitions/"]',
            'title': 'h1',
            'description': '.exhibition-text',
            'dates': '.dates',
            'image': '.hero-image img',
        },
        'address': '7 Rue Debelleyme, 75003 Paris',
    },
    {
        'name': 'fondation_cartier',
        'base_url': 'https://www.fondationcartier.com',
        'agenda_url': 'https://www.fondationcartier.com/expositions',
        'selectors': {
            'event_links': 'a[href*="/expositions/"]',
            'title': 'h1',
            'description': '.intro, .description',
            'dates': '.dates',
            'image': '.visual img',
        },
        'address': '261 Boulevard Raspail, 75014 Paris',
    },
    {
        'name': 'palais_tokyo',
        'base_url': 'https://palaisdetokyo.com',
        'agenda_url': 'https://palaisdetokyo.com/en/programme/',
        'selectors': {
            'event_links': 'a[href*="/exposition/"], a[href*="/event/"]',
            'title': 'h1',
            'description': '.intro',
            'dates': '.dates',
            'image': '.hero img',
        },
        'address': '13 Avenue du Président Wilson, 75116 Paris',
    },
]


class GenericGalleryScraper(HTMLScraper):
    """
    Generic scraper for Paris art galleries.
    
    Can be instantiated with different gallery configurations.
    """
    
    def __init__(
        self, 
        gallery_config: Dict = None,
        gallery_name: str = None,
        max_events: int = 50
    ):
        """
        Initialize with a specific gallery config or name.
        
        Args:
            gallery_config: Custom gallery configuration dict
            gallery_name: Name of a known gallery from PARIS_GALLERIES
            max_events: Maximum events to scrape
        """
        # Get config from name or use provided
        if gallery_name:
            gallery_config = next(
                (g for g in PARIS_GALLERIES if g['name'] == gallery_name),
                None
            )
        
        if not gallery_config:
            # Default to first gallery
            gallery_config = PARIS_GALLERIES[0]
        
        self.gallery_config = gallery_config
        self.selectors = gallery_config.get('selectors', {})
        
        config = ScraperConfig(
            name=gallery_config['name'],
            source_url=gallery_config.get('agenda_url', gallery_config['base_url']),
            source_type="gallery",
            category_hint="arts_visuels",
            requires_playwright=True,
            rate_limit_seconds=2.0,
            max_events=max_events,
        )
        super().__init__(config)
    
    def get_event_urls(self, soup) -> List[str]:
        """Extract event URLs based on gallery selectors."""
        urls = []
        
        selector = self.selectors.get('event_links', 'a[href*="/exhibition"]')
        
        for link in soup.select(selector):
            href = link.get('href', '')
            if href:
                full_url = urljoin(self.gallery_config['base_url'], href)
                if full_url not in urls:
                    urls.append(full_url)
        
        return urls[:30]
    
    def parse_event_page(self, soup, url: str) -> Optional[ScrapedEvent]:
        """Parse exhibition details."""
        try:
            # Title
            title_selector = self.selectors.get('title', 'h1')
            title_el = soup.select_one(title_selector)
            title = title_el.get_text(strip=True) if title_el else None
            
            if not title:
                return None
            
            # Description
            desc_selector = self.selectors.get('description', '.description')
            desc_el = soup.select_one(desc_selector)
            description = desc_el.get_text(strip=True)[:1500] if desc_el else ''
            
            # Dates
            date_start = None
            date_end = None
            
            dates_selector = self.selectors.get('dates', '.dates')
            dates_el = soup.select_one(dates_selector)
            if dates_el:
                dates = self._parse_date_range(dates_el.get_text())
                if dates:
                    date_start, date_end = dates
            
            if not date_start:
                date_start = datetime.now().strftime('%Y-%m-%d')
            
            # Location
            location_name = self.gallery_config['name'].replace('_', ' ').title()
            address = self.gallery_config.get('address', 'Paris')
            
            # Price - most galleries are free
            price_from = 0
            is_free = True
            
            price_el = soup.select_one('.price, .tarif')
            if price_el:
                price_text = price_el.get_text().lower()
                if 'gratuit' not in price_text and 'free' not in price_text:
                    prices = re.findall(r'(\d+(?:[.,]\d{2})?)\s*€', price_text)
                    if prices:
                        price_from = min(float(p.replace(',', '.')) for p in prices)
                        is_free = price_from == 0
            
            # Image
            img_selector = self.selectors.get('image', 'figure img')
            img_el = soup.select_one(img_selector)
            image_url = None
            if img_el:
                image_url = img_el.get('src') or img_el.get('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(url, image_url)
            
            return ScrapedEvent(
                title=title,
                description=description,
                source_name=self.gallery_config['name'],
                source_event_url=url,
                date_start=date_start,
                date_end=date_end,
                location_name=location_name,
                address=address,
                price_from=price_from,
                is_free=is_free,
                image_url=image_url,
                ticket_url=url,
                has_direct_ticket_button=False,
                raw_category='exposition',
                raw_tags=['galerie', 'art_contemporain', 'exposition', 'vernissage'],
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to parse {url}: {e}")
            return None
    
    def _parse_date_range(self, text: str) -> Optional[tuple]:
        """Parse date range from text."""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12,
        }
        
        pattern = r'(\d{1,2})[/\.\s]+(' + '|'.join(months.keys()) + r')[/\.\s]*(\d{4})?'
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


def scrape_all_galleries(max_events_per_gallery: int = 30) -> List:
    """Scrape all known Paris galleries."""
    all_events = []
    
    for gallery in PARIS_GALLERIES:
        try:
            with GenericGalleryScraper(gallery_config=gallery, max_events=max_events_per_gallery) as scraper:
                events = scraper.scrape_all()
                all_events.extend(events)
        except Exception as e:
            print(f"⚠️ Failed to scrape {gallery['name']}: {e}")
    
    return all_events

