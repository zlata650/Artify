"""
🎭 Artify - Configuration des sources de données
Sources de scraping pour les événements parisiens
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class ScraperType(str, Enum):
    """Types de scrapers disponibles"""
    API = "api"              # API REST
    RSS = "rss"              # Flux RSS
    HTML = "html"            # Parsing HTML
    JSON_LD = "json_ld"      # Données structurées JSON-LD
    SITEMAP = "sitemap"      # Parsing de sitemap


class Frequency(str, Enum):
    """Fréquence de mise à jour"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class DataSource:
    """Configuration d'une source de données"""
    id: str
    name: str
    url: str
    category: str
    scraper_type: ScraperType
    frequency: Frequency = Frequency.DAILY
    active: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""


# ============================================================================
# 🎭 SOURCES - SPECTACLES
# ============================================================================

SPECTACLES_SOURCES: List[DataSource] = [
    # Théâtre
    DataSource(
        id="billetreduc-theatre",
        name="BilletReduc - Théâtre",
        url="https://www.billetreduc.com/theatre.htm",
        category="spectacles",
        scraper_type=ScraperType.HTML,
        config={"selectors": {"event": ".event-card", "title": ".event-title", "date": ".event-date"}},
        notes="Billets à prix réduits pour le théâtre",
    ),
    DataSource(
        id="theatreonline",
        name="Théâtre Online",
        url="https://www.theatreonline.com/",
        category="spectacles",
        scraper_type=ScraperType.HTML,
        notes="Billetterie théâtre parisien",
    ),
    DataSource(
        id="officiel-spectacles-theatre",
        name="L'Officiel des Spectacles - Théâtre",
        url="https://www.offi.fr/theatre-paris.html",
        category="spectacles",
        scraper_type=ScraperType.HTML,
        notes="Référence historique des spectacles parisiens",
    ),
    
    # Opéra & Ballet
    DataSource(
        id="opera-paris",
        name="Opéra National de Paris",
        url="https://www.operadeparis.fr/saison-24-25",
        category="spectacles",
        scraper_type=ScraperType.HTML,
        frequency=Frequency.WEEKLY,
        notes="Opéra Bastille et Palais Garnier",
    ),
    DataSource(
        id="opera-comique",
        name="Opéra Comique",
        url="https://www.opera-comique.com/fr/saison",
        category="spectacles",
        scraper_type=ScraperType.HTML,
        frequency=Frequency.WEEKLY,
    ),
    DataSource(
        id="chaillot",
        name="Théâtre de Chaillot",
        url="https://theatre-chaillot.fr/fr/saison",
        category="spectacles",
        scraper_type=ScraperType.HTML,
        notes="Danse contemporaine",
    ),
    
    # Humour & Stand-up
    DataSource(
        id="comedyclub",
        name="Comedy Club Paris",
        url="https://www.comedyclub.fr/programmation",
        category="spectacles",
        scraper_type=ScraperType.HTML,
        notes="Stand-up et humour",
    ),
    DataSource(
        id="point-virgule",
        name="Le Point Virgule",
        url="https://www.lepointvirgule.com/",
        category="spectacles",
        scraper_type=ScraperType.HTML,
        notes="Café-théâtre et one-man show",
    ),
    DataSource(
        id="jamel-comedy",
        name="Jamel Comedy Club",
        url="https://www.jamelcomedyclub.com/",
        category="spectacles",
        scraper_type=ScraperType.HTML,
    ),
    
    # Cirque
    DataSource(
        id="cirque-hiver",
        name="Cirque d'Hiver Bouglione",
        url="https://www.cirquedhiver.com/",
        category="spectacles",
        scraper_type=ScraperType.HTML,
        frequency=Frequency.WEEKLY,
    ),
]

# ============================================================================
# 🎵 SOURCES - MUSIQUE
# ============================================================================

MUSIQUE_SOURCES: List[DataSource] = [
    # Billetteries principales
    DataSource(
        id="fnac-spectacles",
        name="Fnac Spectacles",
        url="https://www.fnacspectacles.com/place-concert-musique/",
        category="musique",
        scraper_type=ScraperType.HTML,
        notes="Principale billetterie de concerts en France",
    ),
    DataSource(
        id="ticketmaster",
        name="Ticketmaster France",
        url="https://www.ticketmaster.fr/music",
        category="musique",
        scraper_type=ScraperType.HTML,
    ),
    DataSource(
        id="seetickets",
        name="See Tickets",
        url="https://www.seetickets.com/fr/concerts",
        category="musique",
        scraper_type=ScraperType.HTML,
    ),
    
    # APIs de concerts
    DataSource(
        id="bandsintown",
        name="Bandsintown",
        url="https://rest.bandsintown.com/artists/",
        category="musique",
        scraper_type=ScraperType.API,
        config={"location": "Paris, France", "radius": "50"},
        notes="API REST pour concerts",
    ),
    DataSource(
        id="songkick",
        name="Songkick",
        url="https://www.songkick.com/metro-areas/28909-france-paris",
        category="musique",
        scraper_type=ScraperType.HTML,
    ),
    
    # Salles de concert
    DataSource(
        id="philharmonie",
        name="Philharmonie de Paris",
        url="https://philharmoniedeparis.fr/fr/concerts",
        category="musique",
        scraper_type=ScraperType.HTML,
        frequency=Frequency.WEEKLY,
        notes="Classique et world music",
    ),
    DataSource(
        id="olympia",
        name="L'Olympia",
        url="https://www.lolympia.com/agenda",
        category="musique",
        scraper_type=ScraperType.HTML,
    ),
    DataSource(
        id="bataclan",
        name="Le Bataclan",
        url="https://www.bataclan.fr/agenda/",
        category="musique",
        scraper_type=ScraperType.HTML,
    ),
    DataSource(
        id="zenith",
        name="Zénith de Paris",
        url="https://www.zenith-paris.com/programmation",
        category="musique",
        scraper_type=ScraperType.HTML,
    ),
    DataSource(
        id="accor-arena",
        name="Accor Arena",
        url="https://www.accorarena.com/agenda",
        category="musique",
        scraper_type=ScraperType.HTML,
        notes="Grands concerts",
    ),
    
    # Jazz & Blues
    DataSource(
        id="sunset-sunside",
        name="Sunset-Sunside",
        url="https://www.sunset-sunside.com/programme",
        category="musique",
        scraper_type=ScraperType.HTML,
        notes="Jazz club historique",
    ),
    DataSource(
        id="duc-lombards",
        name="Duc des Lombards",
        url="https://www.ducdeslombards.com/programmation",
        category="musique",
        scraper_type=ScraperType.HTML,
    ),
    DataSource(
        id="new-morning",
        name="New Morning",
        url="https://www.newmorning.com/programme/",
        category="musique",
        scraper_type=ScraperType.HTML,
        notes="Jazz et world music",
    ),
    
    # Électro & Clubs
    DataSource(
        id="resident-advisor",
        name="Resident Advisor - Paris",
        url="https://ra.co/events/fr/paris",
        category="musique",
        scraper_type=ScraperType.HTML,
        notes="Référence pour la musique électronique",
    ),
    DataSource(
        id="shotgun",
        name="Shotgun",
        url="https://shotgun.live/fr/cities/paris",
        category="musique",
        scraper_type=ScraperType.HTML,
        notes="Billetterie électro et clubbing",
    ),
]

# ============================================================================
# 🎨 SOURCES - ARTS VISUELS
# ============================================================================

ARTS_VISUELS_SOURCES: List[DataSource] = [
    # Musées nationaux
    DataSource(
        id="louvre",
        name="Musée du Louvre",
        url="https://www.louvre.fr/expositions",
        category="arts_visuels",
        scraper_type=ScraperType.HTML,
        frequency=Frequency.WEEKLY,
    ),
    DataSource(
        id="orsay",
        name="Musée d'Orsay",
        url="https://www.musee-orsay.fr/fr/expositions",
        category="arts_visuels",
        scraper_type=ScraperType.HTML,
        frequency=Frequency.WEEKLY,
    ),
    DataSource(
        id="pompidou",
        name="Centre Pompidou",
        url="https://www.centrepompidou.fr/fr/programme",
        category="arts_visuels",
        scraper_type=ScraperType.HTML,
        frequency=Frequency.WEEKLY,
    ),
    DataSource(
        id="grand-palais",
        name="Grand Palais",
        url="https://www.grandpalais.fr/fr/les-expositions",
        category="arts_visuels",
        scraper_type=ScraperType.HTML,
        frequency=Frequency.WEEKLY,
    ),
    DataSource(
        id="palais-tokyo",
        name="Palais de Tokyo",
        url="https://palaisdetokyo.com/programme/",
        category="arts_visuels",
        scraper_type=ScraperType.HTML,
    ),
    
    # Fondations
    DataSource(
        id="fondation-lv",
        name="Fondation Louis Vuitton",
        url="https://www.fondationlouisvuitton.fr/fr/expositions",
        category="arts_visuels",
        scraper_type=ScraperType.HTML,
        frequency=Frequency.WEEKLY,
    ),
    DataSource(
        id="cartier",
        name="Fondation Cartier",
        url="https://www.fondationcartier.com/expositions",
        category="arts_visuels",
        scraper_type=ScraperType.HTML,
    ),
    
    # Photographie
    DataSource(
        id="mep",
        name="Maison Européenne de la Photographie",
        url="https://www.mep-fr.org/programmation/",
        category="arts_visuels",
        scraper_type=ScraperType.HTML,
    ),
    DataSource(
        id="jeu-paume",
        name="Jeu de Paume",
        url="https://jeudepaume.org/expositions/",
        category="arts_visuels",
        scraper_type=ScraperType.HTML,
    ),
    
    # Immersif
    DataSource(
        id="atelier-lumieres",
        name="Atelier des Lumières",
        url="https://www.atelier-lumieres.com/",
        category="arts_visuels",
        scraper_type=ScraperType.HTML,
        notes="Expositions numériques immersives",
    ),
    
    # Agrégateurs
    DataSource(
        id="paris-musees",
        name="Paris Musées",
        url="https://www.parismusees.paris.fr/fr/expositions",
        category="arts_visuels",
        scraper_type=ScraperType.HTML,
        notes="14 musées de la ville de Paris",
    ),
    DataSource(
        id="openagenda-expos",
        name="OpenAgenda - Expositions Paris",
        url="https://openagenda.com/expos-paris",
        category="arts_visuels",
        scraper_type=ScraperType.API,
        config={"api_key": "OPENAGENDA_KEY"},
    ),
]

# ============================================================================
# 🖌️ SOURCES - ATELIERS CRÉATIFS
# ============================================================================

ATELIERS_SOURCES: List[DataSource] = [
    DataSource(
        id="wecandoo",
        name="Wecandoo",
        url="https://wecandoo.fr/paris/",
        category="ateliers",
        scraper_type=ScraperType.HTML,
        notes="Ateliers artisanaux",
    ),
    DataSource(
        id="funbooker",
        name="Funbooker",
        url="https://funbooker.com/fr/activites/paris",
        category="ateliers",
        scraper_type=ScraperType.HTML,
    ),
    DataSource(
        id="atelier-chefs",
        name="L'Atelier des Chefs",
        url="https://www.atelierdeschefs.fr/fr/cours-de-cuisine-paris.php",
        category="ateliers",
        scraper_type=ScraperType.HTML,
        notes="Cours de cuisine et pâtisserie",
    ),
]

# ============================================================================
# 🏃 SOURCES - SPORT
# ============================================================================

SPORT_SOURCES: List[DataSource] = [
    DataSource(
        id="meetup-sport",
        name="Meetup - Sport Paris",
        url="https://www.meetup.com/find/?categoryId=9&location=fr--Paris",
        category="sport",
        scraper_type=ScraperType.HTML,
        notes="Événements sportifs communautaires",
    ),
    DataSource(
        id="decathlon-activites",
        name="Decathlon Activités",
        url="https://activites.decathlon.fr/paris",
        category="sport",
        scraper_type=ScraperType.HTML,
    ),
    DataSource(
        id="arkose",
        name="Arkose",
        url="https://www.arkose.com/",
        category="sport",
        scraper_type=ScraperType.HTML,
        notes="Escalade et bloc",
    ),
]

# ============================================================================
# 👥 SOURCES - RENCONTRES
# ============================================================================

RENCONTRES_SOURCES: List[DataSource] = [
    DataSource(
        id="meetup",
        name="Meetup - Paris",
        url="https://www.meetup.com/find/?location=fr--Paris",
        category="rencontres",
        scraper_type=ScraperType.HTML,
        notes="Tous types de meetups",
    ),
    DataSource(
        id="eventbrite-paris",
        name="Eventbrite Paris",
        url="https://www.eventbrite.fr/d/france--paris/events/",
        category="rencontres",
        scraper_type=ScraperType.HTML,
    ),
    DataSource(
        id="onvasortir",
        name="OnVaSortir Paris",
        url="https://paris.onvasortir.com/",
        category="rencontres",
        scraper_type=ScraperType.HTML,
        notes="Sorties entre célibataires",
    ),
]

# ============================================================================
# 🍷 SOURCES - GASTRONOMIE
# ============================================================================

GASTRONOMIE_SOURCES: List[DataSource] = [
    DataSource(
        id="lafourchette",
        name="TheFork / La Fourchette",
        url="https://www.thefork.fr/restaurants/paris",
        category="gastronomie",
        scraper_type=ScraperType.HTML,
        notes="Restaurants et expériences",
    ),
    DataSource(
        id="o-chateau",
        name="O Château",
        url="https://www.o-chateau.com/wine-tastings/",
        category="gastronomie",
        scraper_type=ScraperType.HTML,
        notes="Dégustations de vin",
    ),
]

# ============================================================================
# 📚 SOURCES - CULTURE
# ============================================================================

CULTURE_SOURCES: List[DataSource] = [
    DataSource(
        id="cinematheque",
        name="Cinémathèque Française",
        url="https://www.cinematheque.fr/cycle.html",
        category="culture",
        scraper_type=ScraperType.HTML,
        notes="Rétrospectives et ciné-clubs",
    ),
    DataSource(
        id="forum-images",
        name="Forum des Images",
        url="https://www.forumdesimages.fr/le-programme",
        category="culture",
        scraper_type=ScraperType.HTML,
    ),
    DataSource(
        id="cite-sciences",
        name="Cité des Sciences",
        url="https://www.cite-sciences.fr/fr/au-programme",
        category="culture",
        scraper_type=ScraperType.HTML,
    ),
]

# ============================================================================
# 🌙 SOURCES - NIGHTLIFE
# ============================================================================

NIGHTLIFE_SOURCES: List[DataSource] = [
    DataSource(
        id="ra-paris",
        name="Resident Advisor - Clubs Paris",
        url="https://ra.co/clubs/fr/paris",
        category="nightlife",
        scraper_type=ScraperType.HTML,
        notes="Clubs et soirées électro",
    ),
    DataSource(
        id="timeout-bars",
        name="Time Out - Bars Paris",
        url="https://www.timeout.fr/paris/bars",
        category="nightlife",
        scraper_type=ScraperType.HTML,
    ),
]

# ============================================================================
# 🌐 SOURCES GÉNÉRALES (AGRÉGATEURS)
# ============================================================================

GENERAL_SOURCES: List[DataSource] = [
    DataSource(
        id="paris-fr",
        name="Que Faire à Paris",
        url="https://quefaire.paris.fr/",
        category="general",
        scraper_type=ScraperType.HTML,
        notes="Agenda officiel de la ville de Paris",
    ),
    DataSource(
        id="officiel-spectacles",
        name="L'Officiel des Spectacles",
        url="https://www.offi.fr/",
        category="general",
        scraper_type=ScraperType.HTML,
        notes="Référence depuis 1946",
    ),
    DataSource(
        id="sortiraparis",
        name="Sortir à Paris",
        url="https://www.sortiraparis.com/",
        category="general",
        scraper_type=ScraperType.HTML,
        notes="Actualités sorties parisiennes",
    ),
    DataSource(
        id="timeout-paris",
        name="Time Out Paris",
        url="https://www.timeout.fr/paris",
        category="general",
        scraper_type=ScraperType.HTML,
        notes="Guide international",
    ),
    DataSource(
        id="parisinfo",
        name="Paris Info (Office de Tourisme)",
        url="https://www.parisinfo.com/decouvrir-paris/grandes-expositions",
        category="general",
        scraper_type=ScraperType.HTML,
        notes="Office de tourisme officiel",
    ),
]


# ============================================================================
# AGRÉGATION DE TOUTES LES SOURCES
# ============================================================================

ALL_SOURCES: List[DataSource] = (
    SPECTACLES_SOURCES +
    MUSIQUE_SOURCES +
    ARTS_VISUELS_SOURCES +
    ATELIERS_SOURCES +
    SPORT_SOURCES +
    RENCONTRES_SOURCES +
    GASTRONOMIE_SOURCES +
    CULTURE_SOURCES +
    NIGHTLIFE_SOURCES +
    GENERAL_SOURCES
)


def get_sources_by_category(category: str) -> List[DataSource]:
    """Retourne les sources pour une catégorie donnée."""
    return [s for s in ALL_SOURCES if s.category == category]


def get_active_sources() -> List[DataSource]:
    """Retourne uniquement les sources actives."""
    return [s for s in ALL_SOURCES if s.active]


def get_sources_by_type(scraper_type: ScraperType) -> List[DataSource]:
    """Retourne les sources par type de scraper."""
    return [s for s in ALL_SOURCES if s.scraper_type == scraper_type]


# ============================================================================
# STATISTIQUES DES SOURCES
# ============================================================================

def print_sources_stats():
    """Affiche les statistiques des sources."""
    print("📊 Statistiques des sources Artify\n")
    print(f"Total: {len(ALL_SOURCES)} sources\n")
    
    # Par catégorie
    categories = {}
    for source in ALL_SOURCES:
        categories[source.category] = categories.get(source.category, 0) + 1
    
    print("Par catégorie:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    
    # Par type de scraper
    print("\nPar type de scraper:")
    types = {}
    for source in ALL_SOURCES:
        types[source.scraper_type.value] = types.get(source.scraper_type.value, 0) + 1
    for t, count in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  {t}: {count}")
    
    # Sources actives
    active = len([s for s in ALL_SOURCES if s.active])
    print(f"\nSources actives: {active}/{len(ALL_SOURCES)}")


if __name__ == "__main__":
    print_sources_stats()


