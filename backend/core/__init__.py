"""
🎭 Artify Core Modules
"""

from .models import UnifiedEvent, ScrapedEvent
from .db import EventsDB
from .categorizer import EventCategorizer
from .deduplicate import EventDeduplicator
from .ticket_extractor import TicketExtractor
from .normalization import normalize_event, normalize_address, extract_arrondissement

__all__ = [
    'UnifiedEvent', 
    'ScrapedEvent',
    'EventsDB',
    'EventCategorizer',
    'EventDeduplicator',
    'TicketExtractor',
    'normalize_event',
    'normalize_address',
    'extract_arrondissement',
]

