"""
🎭 Artify - Event Normalization
Normalizes scraped data into unified format
"""

import re
from datetime import datetime, time
from typing import Optional, Tuple
import unicodedata

from .models import ScrapedEvent, UnifiedEvent, TimeOfDay, get_category_from_alias


def normalize_text(text: Optional[str]) -> str:
    """Normalize text: strip whitespace, normalize unicode."""
    if not text:
        return ""
    # Normalize unicode
    text = unicodedata.normalize('NFKC', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()


def normalize_date(date_str: Optional[str]) -> Optional[str]:
    """
    Normalize various date formats to ISO format (YYYY-MM-DD).
    """
    if not date_str:
        return None
    
    date_str = date_str.strip()
    
    # Common French date formats
    formats = [
        '%Y-%m-%d',           # ISO format
        '%d/%m/%Y',           # DD/MM/YYYY
        '%d-%m-%Y',           # DD-MM-YYYY
        '%d %B %Y',           # DD Month YYYY (French)
        '%d %b %Y',           # DD Mon YYYY
        '%d %B',              # DD Month (assume current year)
        '%A %d %B %Y',        # Day DD Month YYYY
        '%Y-%m-%dT%H:%M:%S',  # ISO with time
        '%Y-%m-%dT%H:%M:%S.%fZ',  # ISO with microseconds
        '%Y-%m-%dT%H:%M:%SZ', # ISO with Z
    ]
    
    # French month names mapping
    french_months = {
        'janvier': 'January', 'février': 'February', 'mars': 'March',
        'avril': 'April', 'mai': 'May', 'juin': 'June',
        'juillet': 'July', 'août': 'August', 'septembre': 'September',
        'octobre': 'October', 'novembre': 'November', 'décembre': 'December',
        'jan': 'Jan', 'fév': 'Feb', 'fev': 'Feb', 'mar': 'Mar',
        'avr': 'Apr', 'juil': 'Jul', 'aoû': 'Aug', 'aou': 'Aug',
        'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'déc': 'Dec', 'dec': 'Dec',
    }
    
    # French day names
    french_days = {
        'lundi': 'Monday', 'mardi': 'Tuesday', 'mercredi': 'Wednesday',
        'jeudi': 'Thursday', 'vendredi': 'Friday', 'samedi': 'Saturday',
        'dimanche': 'Sunday',
    }
    
    # Replace French with English
    normalized = date_str.lower()
    for fr, en in french_months.items():
        normalized = normalized.replace(fr, en.lower())
    for fr, en in french_days.items():
        normalized = normalized.replace(fr, en.lower())
    
    # Try parsing with different formats
    for fmt in formats:
        try:
            dt = datetime.strptime(normalized, fmt.lower())
            # If no year, assume current year
            if dt.year == 1900:
                dt = dt.replace(year=datetime.now().year)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # Try regex for common patterns
    patterns = [
        (r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', lambda m: f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"),
        (r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})', lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"),
    ]
    
    for pattern, formatter in patterns:
        match = re.search(pattern, date_str)
        if match:
            return formatter(match)
    
    return None


def normalize_time(time_str: Optional[str]) -> Optional[str]:
    """
    Normalize various time formats to HH:MM.
    """
    if not time_str:
        return None
    
    time_str = time_str.strip().lower()
    
    # Remove common prefixes
    time_str = re.sub(r'^(à|a|at|from|de|dès)\s*', '', time_str)
    
    # Try common formats
    patterns = [
        (r'^(\d{1,2})[h:](\d{2})$', lambda m: f"{m.group(1).zfill(2)}:{m.group(2)}"),
        (r'^(\d{1,2})h$', lambda m: f"{m.group(1).zfill(2)}:00"),
        (r'^(\d{1,2}):(\d{2})(?::\d{2})?$', lambda m: f"{m.group(1).zfill(2)}:{m.group(2)}"),
        (r'^(\d{1,2})\s*(am|pm)$', lambda m: _convert_12h(m.group(1), m.group(2))),
        (r'^(\d{1,2}):(\d{2})\s*(am|pm)$', lambda m: _convert_12h_full(m.group(1), m.group(2), m.group(3))),
    ]
    
    for pattern, formatter in patterns:
        match = re.match(pattern, time_str)
        if match:
            return formatter(match)
    
    return None


def _convert_12h(hour: str, ampm: str) -> str:
    """Convert 12-hour format to 24-hour."""
    h = int(hour)
    if ampm == 'pm' and h != 12:
        h += 12
    elif ampm == 'am' and h == 12:
        h = 0
    return f"{h:02d}:00"


def _convert_12h_full(hour: str, minute: str, ampm: str) -> str:
    """Convert 12-hour format with minutes to 24-hour."""
    h = int(hour)
    if ampm == 'pm' and h != 12:
        h += 12
    elif ampm == 'am' and h == 12:
        h = 0
    return f"{h:02d}:{minute}"


def get_time_of_day(time_str: Optional[str]) -> str:
    """
    Determine time of day from time string.
    """
    if not time_str:
        return TimeOfDay.SOIR.value
    
    normalized = normalize_time(time_str)
    if not normalized:
        return TimeOfDay.SOIR.value
    
    try:
        hour = int(normalized.split(':')[0])
        
        if 6 <= hour < 12:
            return TimeOfDay.MATIN.value
        elif 12 <= hour < 18:
            return TimeOfDay.APRES_MIDI.value
        elif 18 <= hour < 23:
            return TimeOfDay.SOIR.value
        else:
            return TimeOfDay.NUIT.value
    except:
        return TimeOfDay.SOIR.value


def extract_arrondissement(address: Optional[str]) -> Optional[int]:
    """
    Extract Paris arrondissement from address.
    """
    if not address:
        return None
    
    # Patterns for arrondissement
    patterns = [
        r'750(\d{2})',           # Postal code 75001-75020
        r'(\d{1,2})(?:e|ème|eme|er|è)\s*(?:arr|arrondissement)?',
        r'Paris\s*(\d{1,2})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, address, re.IGNORECASE)
        if match:
            arr = int(match.group(1))
            if 1 <= arr <= 20:
                return arr
    
    return None


def normalize_address(address: Optional[str]) -> str:
    """
    Normalize an address string.
    """
    if not address:
        return ""
    
    address = normalize_text(address)
    
    # Ensure Paris is mentioned if arrondissement found
    arr = extract_arrondissement(address)
    if arr and 'paris' not in address.lower():
        address = f"{address}, Paris"
    
    return address


def parse_price(price_text: Optional[str]) -> Tuple[float, Optional[float], bool]:
    """
    Parse price text and return (price_from, price_to, is_free).
    """
    if not price_text:
        return 0.0, None, False
    
    price_text = price_text.lower().strip()
    
    # Check for free
    free_patterns = ['gratuit', 'free', 'entrée libre', 'libre', '0€', '0 €']
    if any(p in price_text for p in free_patterns):
        return 0.0, None, True
    
    # Extract numeric prices
    prices = re.findall(r'(\d+(?:[.,]\d{2})?)\s*(?:€|eur|euros?)?', price_text)
    
    if not prices:
        return 0.0, None, False
    
    prices = [float(p.replace(',', '.')) for p in prices]
    prices.sort()
    
    if len(prices) == 1:
        return prices[0], None, prices[0] == 0
    else:
        return prices[0], prices[-1], prices[0] == 0


def normalize_event(scraped: ScrapedEvent, category_override: Optional[str] = None) -> UnifiedEvent:
    """
    Convert a ScrapedEvent to a UnifiedEvent with normalization.
    """
    # Normalize dates
    date_start = normalize_date(scraped.date_start) or datetime.now().strftime('%Y-%m-%d')
    date_end = normalize_date(scraped.date_end)
    
    # Normalize times
    time_start = normalize_time(scraped.time_start)
    time_end = normalize_time(scraped.time_end)
    
    # Determine time of day
    time_of_day = get_time_of_day(scraped.time_start)
    
    # Normalize location
    location_name = normalize_text(scraped.location_name) or "Paris"
    address = normalize_address(scraped.address)
    arrondissement = extract_arrondissement(address) or extract_arrondissement(location_name)
    
    # Parse price
    if scraped.price_from is not None:
        price_from = scraped.price_from
        price_to = scraped.price_to
        is_free = scraped.is_free or price_from == 0
    else:
        price_from, price_to, is_free = parse_price(scraped.price_text)
    
    # Determine category
    if category_override:
        category = category_override
    elif scraped.raw_category:
        category = get_category_from_alias(scraped.raw_category)
    else:
        category = 'culture'  # Default
    
    # Generate ID
    event_id = UnifiedEvent.generate_id(
        scraped.title,
        date_start,
        location_name,
        scraped.source_name
    )
    
    # Build tags
    tags = list(scraped.raw_tags) if scraped.raw_tags else []
    
    # Determine ticket URL
    ticket_url = scraped.ticket_url if scraped.ticket_url else scraped.source_event_url
    
    return UnifiedEvent(
        id=event_id,
        title=normalize_text(scraped.title),
        description=normalize_text(scraped.description),
        category=category,
        date_start=date_start,
        sub_category=None,
        tags=tags,
        date_end=date_end,
        time_start=time_start,
        time_end=time_end,
        time_of_day=time_of_day,
        location_name=location_name,
        address=address,
        arrondissement=arrondissement,
        price_from=price_from,
        price_to=price_to,
        is_free=is_free,
        image_url=scraped.image_url,
        organizer_name=scraped.organizer_name,
        source_name=scraped.source_name,
        source_event_url=scraped.source_event_url,
        ticket_url=ticket_url,
        has_direct_ticket_button=scraped.has_direct_ticket_button,
    )

