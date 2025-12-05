"""
🎭 Artify - Eventbrite Scraper
Scrapes events from Eventbrite Paris
"""

import re
import json
from typing import Generator, Optional, Dict, List
from urllib.parse import urljoin, quote
from datetime import datetime

from backend.core.models import ScrapedEvent
from backend.scrapers.base import BaseScraper, ScraperConfig, HTMLScraper


class EventbriteScraper(HTMLScraper):
    """
    Scraper for Eventbrite Paris events.
    
    Eventbrite uses JavaScript-heavy pages, so we parse the JSON-LD data
    embedded in the HTML.
    """
    
    def __init__(self, max_events: int = 100):
        config = ScraperConfig(
            name="eventbrite",
            source_url="https://www.eventbrite.fr/d/france--paris/all-events/",
            source_type="aggregator",
            requires_playwright=True,  # Better for dynamic content
            rate_limit_seconds=1.5,
            max_events=max_events,
        )
        super().__init__(config)
    
    def get_listing_url(self, page: int = 1) -> str:
        """Get listing URL with pagination."""
        base = self.config.source_url
        if page > 1:
            return f"{base}?page={page}"
        return base
    
    def get_event_urls(self, soup) -> List[str]:
        """Extract event URLs from listing page."""
        urls = []
        
        # Eventbrite event links
        selectors = [
            'a[href*="/e/"]',
            '.event-card-link',
            '[data-event-id] a',
            '.search-event-card-wrapper a',
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                if '/e/' in href and href not in urls:
                    # Ensure full URL
                    if not href.startswith('http'):
                        href = urljoin('https://www.eventbrite.fr', href)
                    urls.append(href)
        
        return urls[:50]  # Limit per page
    
    def parse_event_page(self, soup, url: str) -> Optional[ScrapedEvent]:
        """Parse event details from event page."""
        try:
            # Try to find JSON-LD data
            json_ld = self._extract_json_ld(soup)
            if json_ld:
                return self._parse_json_ld(json_ld, url)
            
            # Fallback to HTML parsing
            return self._parse_html(soup, url)
            
        except Exception as e:
            self.logger.warning(f"Failed to parse {url}: {e}")
            return None
    
    def _extract_json_ld(self, soup) -> Optional[Dict]:
        """Extract JSON-LD structured data."""
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') == 'Event':
                            return item
                elif data.get('@type') == 'Event':
                    return data
            except:
                continue
        
        return None
    
    def _parse_json_ld(self, data: Dict, url: str) -> ScrapedEvent:
        """Parse event from JSON-LD data."""
        # Extract dates
        start_date = data.get('startDate', '')
        end_date = data.get('endDate', '')
        
        # Parse datetime
        date_start = None
        time_start = None
        if start_date:
            try:
                dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                date_start = dt.strftime('%Y-%m-%d')
                time_start = dt.strftime('%H:%M')
            except:
                date_start = start_date[:10] if len(start_date) >= 10 else start_date
        
        # Location
        location = data.get('location', {})
        if isinstance(location, dict):
            venue_name = location.get('name', '')
            address_obj = location.get('address', {})
            if isinstance(address_obj, dict):
                address = address_obj.get('streetAddress', '')
                if address_obj.get('addressLocality'):
                    address += f", {address_obj['addressLocality']}"
                if address_obj.get('postalCode'):
                    address += f" {address_obj['postalCode']}"
            else:
                address = str(address_obj)
        else:
            venue_name = str(location)
            address = ''
        
        # Price
        offers = data.get('offers', {})
        price_from = None
        is_free = False
        
        if isinstance(offers, dict):
            price = offers.get('price', offers.get('lowPrice'))
            if price is not None:
                try:
                    price_from = float(price)
                    is_free = price_from == 0
                except:
                    pass
        elif isinstance(offers, list) and offers:
            prices = []
            for offer in offers:
                if isinstance(offer, dict):
                    p = offer.get('price', offer.get('lowPrice'))
                    if p is not None:
                        try:
                            prices.append(float(p))
                        except:
                            pass
            if prices:
                price_from = min(prices)
                is_free = price_from == 0
        
        # Image
        image = data.get('image', [])
        if isinstance(image, list) and image:
            image_url = image[0]
        elif isinstance(image, str):
            image_url = image
        else:
            image_url = None
        
        # Organizer
        organizer = data.get('organizer', {})
        organizer_name = organizer.get('name', '') if isinstance(organizer, dict) else str(organizer)
        
        # Ticket URL - Eventbrite uses the event page itself
        ticket_url = url
        
        return ScrapedEvent(
            title=data.get('name', 'Untitled Event'),
            description=data.get('description', ''),
            source_name='eventbrite',
            source_event_url=url,
            date_start=date_start,
            date_end=end_date[:10] if end_date and len(end_date) >= 10 else None,
            time_start=time_start,
            location_name=venue_name,
            address=address,
            price_from=price_from,
            is_free=is_free,
            image_url=image_url,
            organizer_name=organizer_name,
            ticket_url=ticket_url,
            has_direct_ticket_button=True,  # Eventbrite always has ticket button
            raw_category=data.get('eventAttendanceMode', ''),
        )
    
    def _parse_html(self, soup, url: str) -> Optional[ScrapedEvent]:
        """Fallback HTML parsing."""
        # Title
        title_el = soup.select_one('h1, .event-title, [data-testid="event-title"]')
        title = title_el.get_text(strip=True) if title_el else None
        
        if not title:
            return None
        
        # Description
        desc_el = soup.select_one('.event-description, [data-testid="event-description"], .eds-text--left')
        description = desc_el.get_text(strip=True)[:1000] if desc_el else ''
        
        # Date
        date_el = soup.select_one('[data-testid="event-date"], .event-date, time')
        date_start = None
        if date_el:
            datetime_attr = date_el.get('datetime', '')
            if datetime_attr:
                date_start = datetime_attr[:10]
        
        # Venue
        venue_el = soup.select_one('[data-testid="venue-name"], .event-venue')
        venue_name = venue_el.get_text(strip=True) if venue_el else 'Paris'
        
        # Image
        img_el = soup.select_one('.event-header img, [data-testid="event-image"] img, .listing-hero img')
        image_url = img_el.get('src') if img_el else None
        
        return ScrapedEvent(
            title=title,
            description=description,
            source_name='eventbrite',
            source_event_url=url,
            date_start=date_start,
            location_name=venue_name,
            image_url=image_url,
            ticket_url=url,
            has_direct_ticket_button=True,
        )


# Convenience function
def scrape_eventbrite(max_events: int = 100) -> List:
    """Scrape Eventbrite Paris events."""
    with EventbriteScraper(max_events=max_events) as scraper:
        return scraper.scrape_all()

