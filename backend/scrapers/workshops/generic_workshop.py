"""
🎭 Artify - Generic Workshop Scraper Template
Extensible template for scraping creative workshops in Paris
"""

import re
from typing import Generator, Optional, List, Dict
from urllib.parse import urljoin
from datetime import datetime

from backend.core.models import ScrapedEvent
from backend.scrapers.base import HTMLScraper, ScraperConfig


# Known Paris workshop/atelier providers
PARIS_WORKSHOPS = [
    {
        'name': 'wecandoo',
        'base_url': 'https://wecandoo.fr',
        'agenda_url': 'https://wecandoo.fr/ateliers/paris',
        'selectors': {
            'event_links': '.workshop-card a, a[href*="/atelier/"]',
            'title': 'h1',
            'description': '.workshop-description, .description',
            'dates': '.dates, .availability',
            'price': '.price, .tarif',
            'image': '.workshop-image img, .hero img',
        },
        'workshop_types': ['ceramique', 'poterie', 'bijoux', 'couture', 'cuisine'],
    },
    {
        'name': 'superprof_ateliers',
        'base_url': 'https://www.superprof.fr',
        'agenda_url': 'https://www.superprof.fr/cours/dessin-peinture/paris/',
        'selectors': {
            'event_links': '.course-card a, a[href*="/cours/"]',
            'title': 'h1',
            'description': '.course-description',
            'price': '.price',
            'image': '.profile-img',
        },
        'workshop_types': ['dessin', 'peinture', 'sculpture'],
    },
    {
        'name': 'latourdargile',
        'base_url': 'https://www.latourdargile.com',
        'agenda_url': 'https://www.latourdargile.com/cours-stages/',
        'selectors': {
            'event_links': 'a[href*="/cours"], a[href*="/stage"]',
            'title': 'h1',
            'description': '.course-content',
            'price': '.price',
            'image': '.course-image img',
        },
        'address': 'Paris',
        'workshop_types': ['ceramique', 'poterie'],
    },
    {
        'name': 'ateliers_de_paris',
        'base_url': 'https://www.ateliersdeparis.com',
        'agenda_url': 'https://www.ateliersdeparis.com/cours',
        'selectors': {
            'event_links': '.course-link, a[href*="/cours/"]',
            'title': 'h1',
            'description': '.intro',
            'price': '.tarif',
            'image': '.visual img',
        },
        'workshop_types': ['dessin', 'peinture', 'sculpture', 'ceramique'],
    },
]


class GenericWorkshopScraper(HTMLScraper):
    """
    Generic scraper for Paris creative workshops.
    
    Handles ceramics, pottery, painting, drawing, and other creative classes.
    """
    
    def __init__(
        self, 
        workshop_config: Dict = None,
        workshop_name: str = None,
        max_events: int = 50
    ):
        """
        Initialize with a specific workshop config.
        
        Args:
            workshop_config: Custom workshop configuration
            workshop_name: Name of known workshop provider
            max_events: Maximum events to scrape
        """
        if workshop_name:
            workshop_config = next(
                (w for w in PARIS_WORKSHOPS if w['name'] == workshop_name),
                None
            )
        
        if not workshop_config:
            workshop_config = PARIS_WORKSHOPS[0]
        
        self.workshop_config = workshop_config
        self.selectors = workshop_config.get('selectors', {})
        
        config = ScraperConfig(
            name=workshop_config['name'],
            source_url=workshop_config.get('agenda_url', workshop_config['base_url']),
            source_type="workshop",
            category_hint="ateliers",  # Always ateliers category
            requires_playwright=True,
            rate_limit_seconds=2.0,
            max_events=max_events,
        )
        super().__init__(config)
    
    def get_event_urls(self, soup) -> List[str]:
        """Extract workshop URLs."""
        urls = []
        
        selector = self.selectors.get('event_links', 'a[href*="/atelier"], a[href*="/cours"]')
        
        for link in soup.select(selector):
            href = link.get('href', '')
            if href:
                full_url = urljoin(self.workshop_config['base_url'], href)
                if full_url not in urls:
                    urls.append(full_url)
        
        return urls[:30]
    
    def parse_event_page(self, soup, url: str) -> Optional[ScrapedEvent]:
        """Parse workshop details."""
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
            
            # Dates - workshops often have multiple sessions
            date_start = None
            time_start = None
            
            dates_selector = self.selectors.get('dates', '.dates')
            dates_el = soup.select_one(dates_selector)
            if dates_el:
                date_text = dates_el.get_text()
                date_start = self._extract_next_date(date_text)
                time_start = self._extract_time(date_text)
            
            if not date_start:
                # Many workshops are available on demand
                date_start = datetime.now().strftime('%Y-%m-%d')
            
            # Location
            location_name = self.workshop_config['name'].replace('_', ' ').title()
            address = self.workshop_config.get('address', 'Paris')
            
            # Try to extract address from page
            addr_el = soup.select_one('.address, .location, .lieu')
            if addr_el:
                address = addr_el.get_text(strip=True)
            
            # Price
            price_from = None
            is_free = False
            
            price_selector = self.selectors.get('price', '.price, .tarif')
            price_el = soup.select_one(price_selector)
            if price_el:
                price_text = price_el.get_text()
                prices = re.findall(r'(\d+(?:[.,]\d{2})?)\s*€', price_text)
                if prices:
                    price_from = min(float(p.replace(',', '.')) for p in prices)
            
            # Image
            img_selector = self.selectors.get('image', 'figure img')
            img_el = soup.select_one(img_selector)
            image_url = None
            if img_el:
                image_url = img_el.get('src') or img_el.get('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(url, image_url)
            
            # Determine workshop sub-category
            sub_category = self._detect_workshop_type(title, description)
            
            # Ticket URL - usually booking on same page
            ticket_url = url
            has_ticket = False
            
            for link in soup.select('a[href*="reserv"], a[href*="book"], button.reserve'):
                href = link.get('href', '')
                if href:
                    ticket_url = urljoin(url, href)
                    has_ticket = True
                    break
            
            return ScrapedEvent(
                title=title,
                description=description,
                source_name=self.workshop_config['name'],
                source_event_url=url,
                date_start=date_start,
                time_start=time_start,
                location_name=location_name,
                address=address,
                price_from=price_from,
                is_free=is_free or (price_from == 0),
                image_url=image_url,
                ticket_url=ticket_url,
                has_direct_ticket_button=has_ticket,
                raw_category=sub_category,
                raw_tags=['atelier', 'workshop', 'cours', sub_category],
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to parse {url}: {e}")
            return None
    
    def _detect_workshop_type(self, title: str, description: str) -> str:
        """Detect the type of workshop from content."""
        text = (title + ' ' + description).lower()
        
        type_keywords = {
            'ceramique': ['céramique', 'ceramique', 'ceramic'],
            'poterie': ['poterie', 'pottery', 'tournage', 'tour'],
            'peinture': ['peinture', 'painting', 'aquarelle', 'huile', 'acrylique'],
            'dessin': ['dessin', 'drawing', 'croquis', 'sketch'],
            'sculpture': ['sculpture', 'sculpt', 'modelage'],
            'bijoux': ['bijou', 'jewelry', 'joaillerie'],
            'couture': ['couture', 'sewing', 'broderie', 'tricot'],
            'calligraphie': ['calligraphie', 'calligraphy', 'lettrage'],
            'photo_workshop': ['photo', 'photographie'],
        }
        
        for workshop_type, keywords in type_keywords.items():
            if any(kw in text for kw in keywords):
                return workshop_type
        
        return 'atelier'  # Default
    
    def _extract_next_date(self, text: str) -> Optional[str]:
        """Extract the next available date."""
        months = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12,
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
        }
        
        pattern = r'(\d{1,2})[/\.\s]+(' + '|'.join(months.keys()) + r')[/\.\s]*(\d{4})?'
        match = re.search(pattern, text.lower())
        
        if match:
            day = int(match.group(1))
            month = months[match.group(2)]
            year = int(match.group(3)) if match.group(3) else datetime.now().year
            return f"{year}-{month:02d}-{day:02d}"
        
        # Try simple date format
        simple_pattern = r'(\d{1,2})/(\d{1,2})/(\d{2,4})'
        match = re.search(simple_pattern, text)
        if match:
            day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if year < 100:
                year += 2000
            return f"{year}-{month:02d}-{day:02d}"
        
        return None
    
    def _extract_time(self, text: str) -> Optional[str]:
        """Extract time from text."""
        time_pattern = r'(\d{1,2})[h:](\d{2})?'
        match = re.search(time_pattern, text)
        if match:
            hour = int(match.group(1))
            minute = match.group(2) or '00'
            return f"{hour:02d}:{minute}"
        return None


def scrape_all_workshops(max_events_per_source: int = 30) -> List:
    """Scrape all known Paris workshop providers."""
    all_events = []
    
    for workshop in PARIS_WORKSHOPS:
        try:
            with GenericWorkshopScraper(workshop_config=workshop, max_events=max_events_per_source) as scraper:
                events = scraper.scrape_all()
                all_events.extend(events)
        except Exception as e:
            print(f"⚠️ Failed to scrape {workshop['name']}: {e}")
    
    return all_events

