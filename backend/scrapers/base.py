"""
Base scraper class for Playwright-based web scraping
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
import time
import logging

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base scraper class with common functionality"""
    
    def __init__(
        self,
        source_name: str,
        base_url: str,
        rate_limit_delay: float = 2.0,
        max_retries: int = 3,
        timeout: int = 30000
    ):
        self.source_name = source_name
        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.timeout = timeout
        self.browser: Optional[Browser] = None
    
    def __enter__(self):
        """Context manager entry"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def navigate(self, page: Page, url: str, wait_until: str = "networkidle") -> bool:
        """
        Navigate to URL with error handling and retry logic
        
        Args:
            page: Playwright page object
            url: URL to navigate to
            wait_until: Wait condition ('load', 'domcontentloaded', 'networkidle')
        
        Returns:
            True if navigation successful, False otherwise
        """
        for attempt in range(self.max_retries):
            try:
                page.goto(url, wait_until=wait_until, timeout=self.timeout)
                logger.info(f"Successfully navigated to {url}")
                return True
            except PlaywrightTimeoutError:
                logger.warning(f"Navigation timeout (attempt {attempt + 1}/{self.max_retries}) for {url}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.rate_limit_delay)
                else:
                    logger.error(f"Failed to navigate to {url} after {self.max_retries} attempts")
                    return False
            except Exception as e:
                logger.error(f"Error navigating to {url}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.rate_limit_delay)
                else:
                    return False
        return False
    
    def wait_for_selector(
        self,
        page: Page,
        selector: str,
        timeout: Optional[int] = None
    ) -> bool:
        """Wait for selector to appear"""
        try:
            page.wait_for_selector(selector, timeout=timeout or self.timeout)
            return True
        except PlaywrightTimeoutError:
            logger.warning(f"Selector not found: {selector}")
            return False
        except Exception as e:
            logger.error(f"Error waiting for selector {selector}: {e}")
            return False
    
    def extract_text(self, page: Page, selector: str, default: str = "") -> str:
        """Extract text from selector with error handling"""
        try:
            element = page.query_selector(selector)
            return element.inner_text() if element else default
        except Exception as e:
            logger.warning(f"Error extracting text from {selector}: {e}")
            return default
    
    def extract_events(self) -> List[Dict[str, Any]]:
        """
        Main scraping method - must be implemented by subclasses
        
        Returns:
            List of event dictionaries matching the database schema
        """
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use context manager.")
        
        page = self.browser.new_page()
        page.set_default_timeout(self.timeout)
        
        try:
            events = self.scrape(page)
            logger.info(f"Scraped {len(events)} events from {self.source_name}")
            return events
        except Exception as e:
            logger.error(f"Error during scraping from {self.source_name}: {e}")
            return []
        finally:
            page.close()
            time.sleep(self.rate_limit_delay)  # Rate limiting
    
    @abstractmethod
    def scrape(self, page: Page) -> List[Dict[str, Any]]:
        """
        Scrape events from the page
        
        Args:
            page: Playwright page object
        
        Returns:
            List of event dictionaries with keys:
            - title, description, start_date, end_date, location, address
            - category, image_url, source_url, source_name
            - is_free, price, price_min, price_max, currency, ticket_url
        """
        pass
    
    def normalize_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize event data to match database schema
        
        Args:
            event_data: Raw event data from scraper
        
        Returns:
            Normalized event data
        """
        normalized = {
            "title": event_data.get("title", "").strip(),
            "description": event_data.get("description", "").strip(),
            "start_date": event_data.get("start_date", ""),
            "end_date": event_data.get("end_date"),
            "location": event_data.get("location", "").strip(),
            "address": event_data.get("address", "").strip(),
            "category": event_data.get("category"),
            "image_url": event_data.get("image_url"),
            "source_url": event_data.get("source_url"),
            "source_name": self.source_name,
            "is_free": event_data.get("is_free", False),
            "price": event_data.get("price"),
            "price_min": event_data.get("price_min"),
            "price_max": event_data.get("price_max"),
            "currency": event_data.get("currency", "EUR"),
            "ticket_url": event_data.get("ticket_url"),
        }
        
        # Generate ID if not provided
        if "id" not in event_data:
            import hashlib
            source = normalized.get("source_url") or normalized.get("title", "")
            normalized["id"] = f"evt_{hashlib.md5(source.encode()).hexdigest()[:12]}"
        else:
            normalized["id"] = event_data["id"]
        
        return normalized

