"""
🎭 Artify - Ticket URL Extractor
Extracts real ticket purchase URLs from event pages
"""

import re
from typing import Optional, Tuple, List
from urllib.parse import urljoin, urlparse
import time

# Try to import playwright, but allow fallback to requests
try:
    from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# Patterns for ticket/booking buttons and links
TICKET_BUTTON_PATTERNS = [
    # French
    r'acheter.*billet',
    r'achat.*billet',
    r'billets?',
    r'billetterie',
    r'réserver',
    r'reserver',
    r'réservation',
    r'reservation',
    r'je réserve',
    r"s'inscrire",
    r'inscription',
    r'prendre.*place',
    # English
    r'buy.*ticket',
    r'get.*ticket',
    r'book.*now',
    r'book.*ticket',
    r'purchase.*ticket',
    r'reserve.*now',
    r'register',
    r'sign.*up',
    # General
    r'ticket',
    r'booking',
]

# URL patterns that indicate a ticket/booking page
TICKET_URL_PATTERNS = [
    r'/billet',
    r'/ticket',
    r'/resa',
    r'/reserv',
    r'/book',
    r'/achat',
    r'/checkout',
    r'/paiement',
    r'/payment',
    r'/inscription',
    r'/register',
    r'billetweb',
    r'fnacspectacles',
    r'ticketmaster',
    r'eventbrite',
    r'weezevent',
    r'seetickets',
    r'digitick',
    r'francebillet',
]

# URL patterns to AVOID (generic/organizer pages)
AVOID_URL_PATTERNS = [
    r'^https?://[^/]+/?$',  # Root domain
    r'/concerts?/?$',
    r'/events?/?$',
    r'/agenda/?$',
    r'/spectacles?/?$',
    r'/programme/?$',
    r'/saison/?$',
    r'/category/',
    r'/categories/',
    r'/artiste/',
    r'/artist/',
    r'/venue/',
    r'/lieu/',
    r'/about',
    r'/contact',
    r'/faq',
]


class TicketExtractor:
    """
    Extracts real ticket purchase URLs from event pages.
    Uses Playwright for dynamic pages, falls back to requests/BeautifulSoup.
    """
    
    def __init__(self, use_playwright: bool = True, headless: bool = True):
        """
        Initialize the extractor.
        
        Args:
            use_playwright: Whether to use Playwright for dynamic pages
            headless: Whether to run browser in headless mode
        """
        self.use_playwright = use_playwright and HAS_PLAYWRIGHT
        self.headless = headless
        self._browser: Optional[Browser] = None
        self._playwright = None
    
    def __enter__(self):
        if self.use_playwright:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=self.headless)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
    
    def extract_ticket_url(self, source_url: str) -> Tuple[Optional[str], bool]:
        """
        Extract the ticket/booking URL from an event page.
        
        Args:
            source_url: The event page URL to analyze
            
        Returns:
            Tuple of (ticket_url, has_direct_button)
            - ticket_url: The resolved ticket purchase URL, or source_url if none found
            - has_direct_button: True if a dedicated ticket button was found
        """
        if not source_url:
            return None, False
        
        # Try Playwright first for dynamic pages
        if self.use_playwright and self._browser:
            result = self._extract_with_playwright(source_url)
            if result[1]:  # If found a direct button
                return result
        
        # Fall back to requests/BeautifulSoup
        if HAS_REQUESTS:
            result = self._extract_with_requests(source_url)
            if result[1]:
                return result
        
        # No ticket URL found, return source URL
        return source_url, False
    
    def _extract_with_playwright(self, url: str) -> Tuple[Optional[str], bool]:
        """Extract ticket URL using Playwright."""
        try:
            page = self._browser.new_page()
            page.set_default_timeout(15000)
            
            # Navigate to page
            page.goto(url, wait_until='domcontentloaded')
            time.sleep(2)  # Wait for dynamic content
            
            # Find ticket buttons/links
            ticket_url, found = self._find_ticket_link(page)
            
            page.close()
            
            if ticket_url and found:
                return ticket_url, True
            return url, False
            
        except Exception as e:
            print(f"⚠️ Playwright error for {url}: {e}")
            return url, False
    
    def _find_ticket_link(self, page: Page) -> Tuple[Optional[str], bool]:
        """Find ticket link on a Playwright page."""
        
        # CSS selectors for common ticket buttons
        selectors = [
            'a[href*="ticket"]',
            'a[href*="billet"]',
            'a[href*="reserv"]',
            'a[href*="book"]',
            'a[href*="achat"]',
            'button:has-text("Réserver")',
            'button:has-text("Billets")',
            'button:has-text("Acheter")',
            'a:has-text("Réserver")',
            'a:has-text("Billets")',
            'a:has-text("Acheter")',
            'a:has-text("Book")',
            'a:has-text("Tickets")',
            '.ticket-button a',
            '.booking-button a',
            '[data-booking] a',
            '[class*="ticket"] a',
            '[class*="booking"] a',
            '[class*="reserve"] a',
        ]
        
        for selector in selectors:
            try:
                elements = page.query_selector_all(selector)
                for element in elements:
                    href = element.get_attribute('href')
                    if href and self._is_valid_ticket_url(href, page.url):
                        # Resolve relative URLs
                        full_url = urljoin(page.url, href)
                        
                        # Try to follow the link and get final URL
                        final_url = self._follow_redirect(full_url)
                        return final_url, True
            except:
                continue
        
        # Check by text content
        try:
            for pattern in TICKET_BUTTON_PATTERNS[:10]:  # Check top patterns
                elements = page.query_selector_all(f'a, button')
                for element in elements:
                    text = element.inner_text().lower() if element else ''
                    if re.search(pattern, text, re.IGNORECASE):
                        href = element.get_attribute('href')
                        if href and self._is_valid_ticket_url(href, page.url):
                            full_url = urljoin(page.url, href)
                            final_url = self._follow_redirect(full_url)
                            return final_url, True
        except:
            pass
        
        return None, False
    
    def _extract_with_requests(self, url: str) -> Tuple[Optional[str], bool]:
        """Extract ticket URL using requests/BeautifulSoup."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text().lower()
                aria = link.get('aria-label', '').lower()
                title = link.get('title', '').lower()
                
                # Check if text matches ticket patterns
                combined_text = f"{text} {aria} {title}"
                
                for pattern in TICKET_BUTTON_PATTERNS:
                    if re.search(pattern, combined_text, re.IGNORECASE):
                        if self._is_valid_ticket_url(href, url):
                            full_url = urljoin(url, href)
                            final_url = self._follow_redirect(full_url)
                            return final_url, True
            
            # Check href patterns directly
            for link in links:
                href = link.get('href', '')
                for pattern in TICKET_URL_PATTERNS:
                    if re.search(pattern, href, re.IGNORECASE):
                        if self._is_valid_ticket_url(href, url):
                            full_url = urljoin(url, href)
                            final_url = self._follow_redirect(full_url)
                            return final_url, True
            
            return url, False
            
        except Exception as e:
            print(f"⚠️ Requests error for {url}: {e}")
            return url, False
    
    def _is_valid_ticket_url(self, url: str, base_url: str) -> bool:
        """Check if a URL is a valid ticket URL."""
        if not url:
            return False
        
        # Skip javascript and mailto links
        if url.startswith(('javascript:', 'mailto:', 'tel:', '#')):
            return False
        
        # Check against avoid patterns
        for pattern in AVOID_URL_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        # Check if it has positive indicators
        for pattern in TICKET_URL_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return True  # Allow by default if not explicitly avoided
    
    def _follow_redirect(self, url: str) -> str:
        """Follow redirects to get final URL."""
        if not HAS_REQUESTS:
            return url
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
            return response.url
        except:
            return url
    
    def extract_batch(self, urls: List[str]) -> List[Tuple[str, Optional[str], bool]]:
        """
        Extract ticket URLs for multiple event pages.
        
        Args:
            urls: List of event page URLs
            
        Returns:
            List of tuples (source_url, ticket_url, has_direct_button)
        """
        results = []
        
        for url in urls:
            ticket_url, has_direct = self.extract_ticket_url(url)
            results.append((url, ticket_url, has_direct))
            time.sleep(0.5)  # Rate limiting
        
        return results


# Helper function for quick extraction
def extract_ticket_url(source_url: str) -> Tuple[Optional[str], bool]:
    """Quick ticket URL extraction."""
    with TicketExtractor() as extractor:
        return extractor.extract_ticket_url(source_url)

