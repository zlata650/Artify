"""
🎭 Artify - Unified Event Models
Defines the schema for all events across sources
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List
from datetime import datetime
from enum import Enum
import hashlib
import json


class MainCategory(str, Enum):
    """Main event categories matching frontend expectations"""
    SPECTACLES = "spectacles"
    MUSIQUE = "musique"
    ARTS_VISUELS = "arts_visuels"
    ATELIERS = "ateliers"
    SPORT = "sport"
    GASTRONOMIE = "gastronomie"
    CULTURE = "culture"
    NIGHTLIFE = "nightlife"
    RENCONTRES = "rencontres"


class TimeOfDay(str, Enum):
    """Time of day for events"""
    MATIN = "matin"
    APRES_MIDI = "apres_midi"
    SOIR = "soir"
    NUIT = "nuit"


@dataclass
class ScrapedEvent:
    """
    Raw event data as scraped from a source.
    This is the intermediate format before normalization.
    """
    title: str
    description: str
    source_name: str
    source_event_url: str
    
    # Date and time (may be in various formats)
    date_start: Optional[str] = None
    date_end: Optional[str] = None
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    
    # Location
    location_name: Optional[str] = None
    address: Optional[str] = None
    
    # Pricing
    price_text: Optional[str] = None
    price_from: Optional[float] = None
    price_to: Optional[float] = None
    is_free: bool = False
    
    # Media
    image_url: Optional[str] = None
    
    # Ticket
    ticket_url: Optional[str] = None
    has_direct_ticket_button: bool = False
    
    # Additional metadata
    organizer_name: Optional[str] = None
    raw_category: Optional[str] = None
    raw_tags: List[str] = field(default_factory=list)
    raw_data: Optional[dict] = None  # Store original JSON/data if needed


@dataclass
class UnifiedEvent:
    """
    Unified event model stored in the database.
    This is the final normalized format.
    """
    # Required fields (no defaults) - must come first
    id: str
    title: str
    description: str
    category: str  # MainCategory value
    date_start: str  # ISO format YYYY-MM-DD
    
    # Optional classification
    sub_category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Date and time (optional)
    date_end: Optional[str] = None
    time_start: Optional[str] = None  # HH:MM format
    time_end: Optional[str] = None
    time_of_day: str = "soir"  # TimeOfDay value
    timezone: str = "Europe/Paris"
    
    # Location
    location_name: str = ""
    address: str = ""
    arrondissement: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Pricing
    price_from: float = 0.0
    price_to: Optional[float] = None
    currency: str = "EUR"
    is_free: bool = False
    
    # Media
    image_url: Optional[str] = None
    
    # Organizer and source
    organizer_name: Optional[str] = None
    source_name: str = ""
    source_event_url: str = ""
    
    # Ticket information (CRITICAL)
    ticket_url: Optional[str] = None
    has_direct_ticket_button: bool = False
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    verified: bool = False
    
    @classmethod
    def generate_id(cls, title: str, date: str, location: str, source: str) -> str:
        """Generate a unique ID for an event based on its key properties."""
        raw = f"{title.lower().strip()}|{date}|{location.lower().strip()}|{source}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        # Convert tags list to JSON string for SQLite
        if isinstance(data.get('tags'), list):
            data['tags'] = json.dumps(data['tags'])
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UnifiedEvent':
        """Create from dictionary (from database)."""
        if isinstance(data.get('tags'), str):
            data['tags'] = json.loads(data['tags'])
        return cls(**data)
    
    def to_api_format(self) -> dict:
        """Convert to the format expected by the frontend API."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'main_category': self.category,
            'sub_category': self.sub_category,
            'date': self.date_start,
            'start_time': self.time_start,
            'end_time': self.time_end,
            'time_of_day': self._map_time_of_day(),
            'venue': self.location_name,
            'address': self.address,
            'arrondissement': self.arrondissement,
            'price': self.price_from,
            'price_max': self.price_to,
            'source_url': self.ticket_url or self.source_event_url,
            'source_name': self.source_name,
            'image_url': self.image_url,
            'duration': None,  # Could be calculated from time_start/time_end
            'booking_required': self.has_direct_ticket_button,
            'tags': self.tags,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'verified': self.verified,
        }
    
    def _map_time_of_day(self) -> str:
        """Map time_of_day to frontend expected values."""
        mapping = {
            'matin': 'jour',
            'apres_midi': 'jour', 
            'soir': 'soir',
            'nuit': 'nuit',
        }
        return mapping.get(self.time_of_day, 'jour')


# Mapping for category aliases used by different sources
CATEGORY_ALIASES = {
    # Music
    'concert': 'musique',
    'concerts': 'musique',
    'music': 'musique',
    'live music': 'musique',
    'classical': 'musique',
    'classique': 'musique',
    'jazz': 'musique',
    'rock': 'musique',
    'pop': 'musique',
    'electro': 'musique',
    'electronic': 'musique',
    'opera': 'spectacles',
    'opéra': 'spectacles',
    
    # Theater & Shows
    'theater': 'spectacles',
    'theatre': 'spectacles',
    'théâtre': 'spectacles',
    'comedy': 'spectacles',
    'comédie': 'spectacles',
    'stand-up': 'spectacles',
    'standup': 'spectacles',
    'humour': 'spectacles',
    'circus': 'spectacles',
    'cirque': 'spectacles',
    'danse': 'spectacles',
    'dance': 'spectacles',
    'ballet': 'spectacles',
    'cabaret': 'spectacles',
    
    # Visual Arts
    'exhibition': 'arts_visuels',
    'exposition': 'arts_visuels',
    'expo': 'arts_visuels',
    'museum': 'arts_visuels',
    'musée': 'arts_visuels',
    'gallery': 'arts_visuels',
    'galerie': 'arts_visuels',
    'art': 'arts_visuels',
    'photography': 'arts_visuels',
    'photographie': 'arts_visuels',
    'vernissage': 'arts_visuels',
    
    # Workshops
    'workshop': 'ateliers',
    'atelier': 'ateliers',
    'class': 'ateliers',
    'cours': 'ateliers',
    'ceramics': 'ateliers',
    'céramique': 'ateliers',
    'pottery': 'ateliers',
    'poterie': 'ateliers',
    'painting': 'ateliers',
    'peinture': 'ateliers',
    'drawing': 'ateliers',
    'dessin': 'ateliers',
    'craft': 'ateliers',
    'artisanat': 'ateliers',
    
    # Sport
    'sport': 'sport',
    'fitness': 'sport',
    'yoga': 'sport',
    'running': 'sport',
    'cycling': 'sport',
    'vélo': 'sport',
    
    # Food & Drink
    'food': 'gastronomie',
    'wine': 'gastronomie',
    'vin': 'gastronomie',
    'cooking': 'gastronomie',
    'cuisine': 'gastronomie',
    'gastronomie': 'gastronomie',
    'dégustation': 'gastronomie',
    'tasting': 'gastronomie',
    'brunch': 'gastronomie',
    
    # Culture
    'conference': 'culture',
    'conférence': 'culture',
    'talk': 'culture',
    'lecture': 'culture',
    'film': 'culture',
    'cinema': 'culture',
    'cinéma': 'culture',
    'movie': 'culture',
    'visite': 'culture',
    'visit': 'culture',
    'guided tour': 'culture',
    'visite guidée': 'culture',
    
    # Nightlife
    'party': 'nightlife',
    'soirée': 'nightlife',
    'club': 'nightlife',
    'dj': 'nightlife',
    'bar': 'nightlife',
    'nightlife': 'nightlife',
    
    # Social
    'meetup': 'rencontres',
    'networking': 'rencontres',
    'afterwork': 'rencontres',
    'speed dating': 'rencontres',
    'social': 'rencontres',
}


def get_category_from_alias(alias: str) -> str:
    """Get the main category from an alias."""
    return CATEGORY_ALIASES.get(alias.lower().strip(), 'culture')

