"""
🎭 Artify - Modèles de données pour les événements
Schéma Python pour la base de données des activités à Paris
"""

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Optional, List, Literal
from enum import Enum


# ============================================================================
# ÉNUMÉRATIONS
# ============================================================================

class MainCategory(str, Enum):
    """Catégories principales d'événements"""
    SPECTACLES = "spectacles"
    MUSIQUE = "musique"
    ARTS_VISUELS = "arts_visuels"
    ATELIERS = "ateliers"
    SPORT = "sport"
    RENCONTRES = "rencontres"
    GASTRONOMIE = "gastronomie"
    CULTURE = "culture"
    NIGHTLIFE = "nightlife"


class SubCategorySpectacles(str, Enum):
    """Sous-catégories pour Spectacles"""
    THEATRE_CLASSIQUE = "theatre_classique"
    THEATRE_CONTEMPORAIN = "theatre_contemporain"
    THEATRE_BOULEVARD = "theatre_boulevard"
    CAFE_THEATRE = "cafe_theatre"
    OPERA = "opera"
    BALLET = "ballet"
    DANSE_CONTEMPORAINE = "danse_contemporaine"
    ONE_MAN_SHOW = "one_man_show"
    STAND_UP = "stand_up"
    IMPRO = "impro"
    CIRQUE = "cirque"
    MAGIE = "magie"


class SubCategoryMusique(str, Enum):
    """Sous-catégories pour Musique"""
    CLASSIQUE = "classique"
    SYMPHONIQUE = "symphonique"
    MUSIQUE_CHAMBRE = "musique_chambre"
    JAZZ = "jazz"
    BLUES = "blues"
    POP = "pop"
    ROCK = "rock"
    ROCK_INDIE = "rock_indie"
    CHANSON_FRANCAISE = "chanson_francaise"
    FOLK = "folk"
    TECHNO = "techno"
    HOUSE = "house"
    ELECTRO = "electro"
    RAP = "rap"
    HIP_HOP = "hip_hop"
    AFROBEAT = "afrobeat"
    LATINO = "latino"
    WORLD_MUSIC = "world_music"


class SubCategoryArtsVisuels(str, Enum):
    """Sous-catégories pour Arts Visuels"""
    BEAUX_ARTS = "beaux_arts"
    ART_MODERNE = "art_moderne"
    ART_CONTEMPORAIN = "art_contemporain"
    PHOTOGRAPHIE = "photographie"
    DESIGN = "design"
    ARCHITECTURE = "architecture"
    VERNISSAGE = "vernissage"
    GALERIE = "galerie"
    ART_NUMERIQUE = "art_numerique"
    STREET_ART = "street_art"


class SubCategoryAteliers(str, Enum):
    """Sous-catégories pour Ateliers Créatifs"""
    DESSIN = "dessin"
    PEINTURE = "peinture"
    SCULPTURE = "sculpture"
    CERAMIQUE = "ceramique"
    POTERIE = "poterie"
    BIJOUX = "bijoux"
    COUTURE = "couture"
    PHOTO_WORKSHOP = "photo_workshop"
    ECRITURE = "ecriture"
    CALLIGRAPHIE = "calligraphie"


class SubCategorySport(str, Enum):
    """Sous-catégories pour Sport & Bien-être"""
    FOOTBALL = "football"
    BASKETBALL = "basketball"
    RUNNING = "running"
    BOXE = "boxe"
    ARTS_MARTIAUX = "arts_martiaux"
    YOGA = "yoga"
    PILATES = "pilates"
    FITNESS = "fitness"
    DANSE = "danse"
    ESCALADE = "escalade"
    PATINAGE = "patinage"
    ESCAPE_GAME = "escape_game"


class SubCategoryRencontres(str, Enum):
    """Sous-catégories pour Rencontres & Meetups"""
    CLUB_LECTURE = "club_lecture"
    CLUB_LANGUES = "club_langues"
    CLUB_JEUX = "club_jeux"
    AFTERWORK = "afterwork"
    SPEED_DATING = "speed_dating"
    NETWORKING = "networking"
    BALADE_URBAINE = "balade_urbaine"
    RANDONNEE = "randonnee"


class SubCategoryGastronomie(str, Enum):
    """Sous-catégories pour Gastronomie"""
    COURS_CUISINE = "cours_cuisine"
    PATISSERIE = "patisserie"
    DEGUSTATION_VIN = "degustation_vin"
    DEGUSTATION_FROMAGE = "degustation_fromage"
    DEGUSTATION_CHOCOLAT = "degustation_chocolat"
    FOOD_MARKET = "food_market"
    BRUNCH = "brunch"
    DINER_INSOLITE = "diner_insolite"


class SubCategoryCulture(str, Enum):
    """Sous-catégories pour Culture & Savoir"""
    CONFERENCE = "conference"
    VISITE_GUIDEE = "visite_guidee"
    VISITE_INSOLITE = "visite_insolite"
    CINEMA_ART_ESSAI = "cinema_art_essai"
    CINECLUB = "cineclub"
    MASTERCLASS = "masterclass"


class SubCategoryNightlife(str, Enum):
    """Sous-catégories pour Vie Nocturne"""
    BAR_COCKTAILS = "bar_cocktails"
    SPEAKEASY = "speakeasy"
    ROOFTOP = "rooftop"
    BAR_VIN = "bar_vin"
    CLUB_TECHNO = "club_techno"
    CLUB_MAINSTREAM = "club_mainstream"
    CLUB_LATINO = "club_latino"


class Budget(str, Enum):
    """Tranches de budget"""
    GRATUIT = "gratuit"
    ECONOMIQUE = "0-20"      # 0-20€
    MODERE = "20-50"         # 20-50€
    PREMIUM = "50-100"       # 50-100€
    LUXE = "100+"            # 100€+


class TimeOfDay(str, Enum):
    """Moment de la journée"""
    MATIN = "matin"           # 8h-12h
    APRES_MIDI = "apres_midi" # 12h-18h
    SOIR = "soir"             # 18h-23h
    NUIT = "nuit"             # 23h+


class Ambiance(str, Enum):
    """Types d'ambiance"""
    INTIME = "intime"
    FESTIF = "festif"
    CULTUREL = "culturel"
    SPORTIF = "sportif"
    SOCIAL = "social"
    CREATIF = "creatif"
    GASTRONOMIQUE = "gastronomique"


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class Coordinates:
    """Coordonnées GPS"""
    lat: float
    lng: float


@dataclass
class Venue:
    """Lieu d'un événement"""
    id: str
    name: str
    slug: str
    address: str
    arrondissement: int  # 1-20
    coordinates: Optional[Coordinates] = None
    metro: List[str] = field(default_factory=list)
    website: Optional[str] = None
    phone: Optional[str] = None
    categories: List[MainCategory] = field(default_factory=list)
    description: Optional[str] = None
    image: Optional[str] = None
    capacity: Optional[int] = None
    rating: Optional[float] = None


@dataclass
class Event:
    """Événement/Activité à Paris"""
    # Identifiants
    id: str
    title: str
    slug: str
    
    # Classification
    main_category: MainCategory
    sub_category: str  # Une des SubCategory* enum
    tags: List[str] = field(default_factory=list)
    
    # Timing
    date: str  # Format ISO: YYYY-MM-DD
    start_time: str  # Format: HH:MM
    end_time: Optional[str] = None
    time_of_day: TimeOfDay = TimeOfDay.SOIR
    duration: Optional[int] = None  # En minutes
    
    # Location
    venue: str
    address: str
    arrondissement: int = 1
    coordinates: Optional[Coordinates] = None
    metro: List[str] = field(default_factory=list)
    
    # Pricing
    price: float = 0.0
    price_max: Optional[float] = None
    budget: Budget = Budget.GRATUIT
    booking_required: bool = True
    booking_url: Optional[str] = None
    
    # Details
    description: str = ""
    short_description: str = ""
    ambiance: List[Ambiance] = field(default_factory=list)
    
    # Media
    image: Optional[str] = None
    images: List[str] = field(default_factory=list)
    
    # Source
    source_url: str = ""
    source_name: str = "Artify"
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    featured: bool = False
    verified: bool = False
    
    def __post_init__(self):
        """Calcule automatiquement le budget et la description courte"""
        # Calcul du budget
        if self.price == 0:
            self.budget = Budget.GRATUIT
        elif self.price <= 20:
            self.budget = Budget.ECONOMIQUE
        elif self.price <= 50:
            self.budget = Budget.MODERE
        elif self.price <= 100:
            self.budget = Budget.PREMIUM
        else:
            self.budget = Budget.LUXE
        
        # Description courte
        if not self.short_description and self.description:
            self.short_description = self.description[:100] + "..." if len(self.description) > 100 else self.description


@dataclass
class EventFilter:
    """Filtres de recherche d'événements"""
    categories: List[MainCategory] = field(default_factory=list)
    sub_categories: List[str] = field(default_factory=list)
    budgets: List[Budget] = field(default_factory=list)
    times: List[TimeOfDay] = field(default_factory=list)
    ambiances: List[Ambiance] = field(default_factory=list)
    arrondissements: List[int] = field(default_factory=list)
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    search_query: Optional[str] = None
    free_only: bool = False


# ============================================================================
# CONSTANTES
# ============================================================================

CATEGORY_INFO = {
    MainCategory.SPECTACLES: {
        "label": "Spectacles",
        "emoji": "🎭",
        "color": "#E53935",
        "description": "Théâtre, opéra, danse, humour et cirque",
    },
    MainCategory.MUSIQUE: {
        "label": "Musique",
        "emoji": "🎵",
        "color": "#8E24AA",
        "description": "Concerts, festivals et performances live",
    },
    MainCategory.ARTS_VISUELS: {
        "label": "Arts visuels",
        "emoji": "🎨",
        "color": "#FB8C00",
        "description": "Expositions, galeries et vernissages",
    },
    MainCategory.ATELIERS: {
        "label": "Ateliers créatifs",
        "emoji": "🖌️",
        "color": "#43A047",
        "description": "Cours et ateliers artistiques",
    },
    MainCategory.SPORT: {
        "label": "Sport & Bien-être",
        "emoji": "🏃",
        "color": "#00ACC1",
        "description": "Activités sportives et wellness",
    },
    MainCategory.RENCONTRES: {
        "label": "Rencontres",
        "emoji": "👥",
        "color": "#5E35B1",
        "description": "Meetups, clubs et événements sociaux",
    },
    MainCategory.GASTRONOMIE: {
        "label": "Gastronomie",
        "emoji": "🍷",
        "color": "#D81B60",
        "description": "Cours de cuisine, dégustations et expériences culinaires",
    },
    MainCategory.CULTURE: {
        "label": "Culture & Savoir",
        "emoji": "📚",
        "color": "#1E88E5",
        "description": "Conférences, visites guidées et cinéma",
    },
    MainCategory.NIGHTLIFE: {
        "label": "Vie nocturne",
        "emoji": "🌙",
        "color": "#3949AB",
        "description": "Bars, clubs et soirées",
    },
}

ARRONDISSEMENTS = {
    1: {"name": "1er - Louvre", "character": "Monumental et touristique"},
    2: {"name": "2ème - Bourse", "character": "Passages couverts et vie nocturne"},
    3: {"name": "3ème - Temple", "character": "Marais historique et galeries"},
    4: {"name": "4ème - Hôtel-de-Ville", "character": "Notre-Dame et le Marais"},
    5: {"name": "5ème - Panthéon", "character": "Quartier Latin et universités"},
    6: {"name": "6ème - Luxembourg", "character": "Saint-Germain et librairies"},
    7: {"name": "7ème - Palais-Bourbon", "character": "Tour Eiffel et musées"},
    8: {"name": "8ème - Élysée", "character": "Champs-Élysées et luxe"},
    9: {"name": "9ème - Opéra", "character": "Grands magasins et opéra"},
    10: {"name": "10ème - Entrepôt", "character": "Canal Saint-Martin et hipster"},
    11: {"name": "11ème - Popincourt", "character": "Vie nocturne et Bastille"},
    12: {"name": "12ème - Reuilly", "character": "Bercy et promenades"},
    13: {"name": "13ème - Gobelins", "character": "Chinatown et street art"},
    14: {"name": "14ème - Observatoire", "character": "Montparnasse artistique"},
    15: {"name": "15ème - Vaugirard", "character": "Résidentiel et familial"},
    16: {"name": "16ème - Passy", "character": "Bourgeois et musées"},
    17: {"name": "17ème - Batignolles", "character": "Village et tendance"},
    18: {"name": "18ème - Butte-Montmartre", "character": "Sacré-Cœur et artistes"},
    19: {"name": "19ème - Buttes-Chaumont", "character": "La Villette et culture"},
    20: {"name": "20ème - Ménilmontant", "character": "Populaire et multiculturel"},
}


# ============================================================================
# HELPERS
# ============================================================================

def price_to_budget(price: float) -> Budget:
    """Convertit un prix en catégorie de budget"""
    if price == 0:
        return Budget.GRATUIT
    elif price <= 20:
        return Budget.ECONOMIQUE
    elif price <= 50:
        return Budget.MODERE
    elif price <= 100:
        return Budget.PREMIUM
    else:
        return Budget.LUXE


def get_category_info(category: MainCategory) -> dict:
    """Retourne les informations d'une catégorie"""
    return CATEGORY_INFO.get(category, {})


def get_arrondissement_info(arr: int) -> dict:
    """Retourne les informations d'un arrondissement"""
    return ARRONDISSEMENTS.get(arr, {})


def generate_slug(title: str) -> str:
    """Génère un slug à partir d'un titre"""
    import re
    slug = title.lower()
    # Remplace les caractères accentués
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'î': 'i', 'ï': 'i',
        'ô': 'o', 'ö': 'o',
        'ç': 'c',
        'ñ': 'n',
    }
    for old, new in replacements.items():
        slug = slug.replace(old, new)
    # Garde seulement les caractères alphanumériques et tirets
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


if __name__ == "__main__":
    # Exemple d'utilisation
    event = Event(
        id="ev-001",
        title="Concert Jazz au Sunset",
        slug="concert-jazz-sunset",
        main_category=MainCategory.MUSIQUE,
        sub_category=SubCategoryMusique.JAZZ.value,
        date="2024-12-15",
        start_time="21:00",
        venue="Sunset-Sunside",
        address="60 Rue des Lombards",
        arrondissement=1,
        price=28,
        description="Soirée jazz intimiste avec le quartet de Thomas Dutronc.",
        source_url="https://sunset-sunside.com",
        ambiance=[Ambiance.INTIME, Ambiance.CULTUREL],
    )
    
    print(f"🎵 {event.title}")
    print(f"   📍 {event.venue} ({event.arrondissement}e)")
    print(f"   💰 {event.price}€ ({event.budget.value})")
    print(f"   📅 {event.date} à {event.start_time}")


