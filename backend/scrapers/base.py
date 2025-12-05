"""
🎭 Artify - Base Scraper Class
Abstract base class for all event scrapers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Generator
from datetime import datetime
import time
import logging

from backend.core.models import ScrapedEvent, UnifiedEvent
from backend.core.normalization import normalize_event
from backend.core.categorizer import EventCategorizer

# Try imports
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    from playwright.sync_api import sync_playwright, Browser, Page
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScraperConfig:
    """Configuration for a scraper."""
    name: str
    source_url: str
    source_type: str  # 'aggregator', 'venue', 'museum', 'gallery', 'workshop'
    category_hint: Optional[str] = None  # Default category if known
    requires_playwright: bool = False
    rate_limit_seconds: float = 1.0
    max_events: int = 100
    headers: Dict[str, str] = field(default_factory=lambda: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
    })
    extra_config: Dict[str, Any] = field(default_factory=dict)


class BaseScraper(ABC):
    """
    Abstract base class for all event scrapers.
    
    Subclasses must implement:
    - scrape(): Generator that yields ScrapedEvent objects
    """
    
    def __init__(self, config: ScraperConfig):
        """Initialize the scraper with configuration."""
        self.config = config
        self.session: Optional[requests.Session] = None
        self.browser: Optional[Browser] = None
        self._playwright = None
        self.categorizer = EventCategorizer()
        self.logger = logging.getLogger(f"scraper.{config.name}")
    
    def __enter__(self):
        """Set up resources."""
        if HAS_REQUESTS:
            self.session = requests.Session()
            self.session.headers.update(self.config.headers)
        
        if self.config.requires_playwright and HAS_PLAYWRIGHT:
            self._playwright = sync_playwright().start()
            self.browser = self._playwright.chromium.launch(headless=True)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources."""
        if self.session:
            self.session.close()
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()
    
    @abstractmethod
    def scrape(self) -> Generator[ScrapedEvent, None, None]:
        """
        Scrape events from the source.
        
        Yields:
            ScrapedEvent objects for each found event
        """
        pass
    
    def scrape_all(self) -> List[UnifiedEvent]:
        """
        Scrape and normalize all events.
        
        Returns:
            List of UnifiedEvent objects ready for database
        """
        events = []
        count = 0
        
        self.logger.info(f"🔍 Starting scrape from {self.config.name}")
        start_time = time.time()
        
        try:
            for scraped in self.scrape():
                if count >= self.config.max_events:
                    self.logger.info(f"Reached max events limit ({self.config.max_events})")
                    break
                
                # Normalize the event
                unified = normalize_event(scraped, self.config.category_hint)
                
                # Categorize if no category hint
                if not self.config.category_hint:
                    cat_result = self.categorizer.categorize(
                        title=unified.title,
                        description=unified.description,
                        source_name=self.config.name,
                        venue_name=unified.location_name
                    )
                    unified.category = cat_result['category']
                    if cat_result['sub_category']:
                        unified.sub_category = cat_result['sub_category']
                
                events.append(unified)
                count += 1
                
                # Rate limiting
                time.sleep(self.config.rate_limit_seconds)
                
        except Exception as e:
            self.logger.error(f"❌ Scraping error: {e}")
            raise
        
        elapsed = time.time() - start_time
        self.logger.info(f"✅ Scraped {len(events)} events in {elapsed:.1f}s")
        
        return events
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a page's HTML content.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content or None on error
        """
        if self.config.requires_playwright and self.browser:
            return self._fetch_with_playwright(url)
        elif self.session:
            return self._fetch_with_requests(url)
        return None
    
    def _fetch_with_requests(self, url: str) -> Optional[str]:
        """Fetch page with requests."""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.warning(f"Failed to fetch {url}: {e}")
            return None
    
    def _fetch_with_playwright(self, url: str) -> Optional[str]:
        """Fetch page with Playwright."""
        try:
            page = self.browser.new_page()
            page.goto(url, wait_until='networkidle', timeout=30000)
            content = page.content()
            page.close()
            return content
        except Exception as e:
            self.logger.warning(f"Playwright failed for {url}: {e}")
            return None
    
    def parse_html(self, html: str) -> Optional[BeautifulSoup]:
        """Parse HTML content."""
        if not HAS_BS4 or not html:
            return None
        return BeautifulSoup(html, 'html.parser')
    
    def get_page(self) -> Optional[Page]:
        """Get a Playwright page for advanced interactions."""
        if self.browser:
            return self.browser.new_page()
        return None
    
    def fetch_json(self, url: str) -> Optional[Dict]:
        """Fetch and parse JSON from URL."""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.warning(f"Failed to fetch JSON from {url}: {e}")
            return None


class JSONAPIScraper(BaseScraper):
    """
    Base scraper for sites with JSON APIs.
    """
    
    @abstractmethod
    def get_api_url(self, page: int = 1) -> str:
        """Get the API URL for a specific page."""
        pass
    
    @abstractmethod
    def parse_event(self, data: Dict) -> Optional[ScrapedEvent]:
        """Parse a single event from API response."""
        pass
    
    def get_events_from_response(self, data: Dict) -> List[Dict]:
        """Extract events list from API response. Override if needed."""
        if isinstance(data, list):
            return data
        return data.get('events', data.get('results', data.get('data', [])))
    
    def has_more_pages(self, data: Dict, current_page: int) -> bool:
        """Check if there are more pages. Override if needed."""
        events = self.get_events_from_response(data)
        return len(events) > 0 and current_page < 10  # Max 10 pages by default
    
    def scrape(self) -> Generator[ScrapedEvent, None, None]:
        """Scrape events from JSON API."""
        page = 1
        
        while True:
            url = self.get_api_url(page)
            self.logger.debug(f"Fetching page {page}: {url}")
            
            data = self.fetch_json(url)
            if not data:
                break
            
            events = self.get_events_from_response(data)
            if not events:
                break
            
            for event_data in events:
                event = self.parse_event(event_data)
                if event:
                    yield event
            
            if not self.has_more_pages(data, page):
                break
            
            page += 1
            time.sleep(self.config.rate_limit_seconds)


class HTMLScraper(BaseScraper):
    """
    Base scraper for sites requiring HTML parsing.
    """
    
    @abstractmethod
    def get_event_urls(self, soup: BeautifulSoup) -> List[str]:
        """Extract event URLs from listing page."""
        pass
    
    @abstractmethod
    def parse_event_page(self, soup: BeautifulSoup, url: str) -> Optional[ScrapedEvent]:
        """Parse a single event from its detail page."""
        pass
    
    def get_listing_url(self, page: int = 1) -> str:
        """Get the listing page URL. Override if paginated."""
        return self.config.source_url
    
    def scrape(self) -> Generator[ScrapedEvent, None, None]:
        """Scrape events from HTML pages."""
        page = 1
        seen_urls = set()
        
        while True:
            listing_url = self.get_listing_url(page)
            html = self.fetch_page(listing_url)
            
            if not html:
                break
            
            soup = self.parse_html(html)
            if not soup:
                break
            
            event_urls = self.get_event_urls(soup)
            new_urls = [u for u in event_urls if u not in seen_urls]
            
            if not new_urls:
                break
            
            for url in new_urls:
                seen_urls.add(url)
                
                event_html = self.fetch_page(url)
                if not event_html:
                    continue
                
                event_soup = self.parse_html(event_html)
                if not event_soup:
                    continue
                
                event = self.parse_event_page(event_soup, url)
                if event:
                    yield event
                
                time.sleep(self.config.rate_limit_seconds)
            
            page += 1
            
            # Safety limit
            if page > 20:
                break

