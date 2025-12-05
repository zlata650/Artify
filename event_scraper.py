"""
🎭 Artify - Scraper d'événements réels
Récupère des événements depuis OpenAgenda, Que Faire à Paris, et autres sources
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import json
import re
import hashlib
import time
from dataclasses import dataclass

from events_database import EventsDatabase


# Configuration
OPENAGENDA_API_KEY = None  # À configurer dans .env ou directement ici
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def generate_event_id(source: str, title: str, date: str, venue: str) -> str:
    """Génère un ID unique pour un événement."""
    raw = f"{source}:{title}:{date}:{venue}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def determine_time_of_day(time_str: Optional[str]) -> str:
    """Détermine le moment de la journée basé sur l'heure."""
    if not time_str:
        return "jour"
    
    try:
        hour = int(time_str.split(':')[0])
        if hour < 12:
            return "jour"
        elif hour < 18:
            return "jour"
        elif hour < 22:
            return "soir"
        else:
            return "nuit"
    except:
        return "jour"


def extract_arrondissement(address: str) -> Optional[int]:
    """Extrait le numéro d'arrondissement depuis une adresse."""
    # Patterns: "75001", "75019", "Paris 1er", "Paris 20e", "1er arr", etc.
    patterns = [
        r'750(\d{2})',  # Code postal 75001-75020
        r'Paris\s*(\d{1,2})(?:e|er|ème)?',  # Paris 1er, Paris 20e
        r'(\d{1,2})(?:e|er|ème)\s*arr',  # 1er arr, 20ème arr
    ]
    
    for pattern in patterns:
        match = re.search(pattern, address, re.IGNORECASE)
        if match:
            arr = int(match.group(1))
            if 1 <= arr <= 20:
                return arr
    
    return None


def parse_price(price_str: str) -> tuple[float, Optional[float]]:
    """Parse une chaîne de prix et retourne (min, max)."""
    if not price_str:
        return 0, None
    
    price_str = price_str.lower().strip()
    
    # Gratuit
    if any(word in price_str for word in ['gratuit', 'free', 'entrée libre', '0€']):
        return 0, None
    
    # Extraire les nombres
    prices = re.findall(r'(\d+(?:[,\.]\d+)?)', price_str)
    
    if not prices:
        return 0, None
    
    prices = [float(p.replace(',', '.')) for p in prices]
    
    if len(prices) == 1:
        return prices[0], None
    else:
        return min(prices), max(prices)


class QueFaireParissScraper:
    """Scraper pour quefaire.paris.fr - l'agenda officiel de la ville de Paris."""
    
    BASE_URL = "https://quefaire.paris.fr"
    SOURCE_NAME = "Que Faire à Paris"
    
    CATEGORY_MAPPING = {
        'concerts': 'musique',
        'spectacles': 'spectacles',
        'expositions': 'arts_visuels',
        'cinema': 'culture',
        'festivals': 'musique',
        'conferences': 'culture',
        'ateliers': 'ateliers',
        'sports': 'sport',
        'enfants': 'ateliers',
        'balades': 'sport',
        'gastronomie': 'gastronomie',
        'soirees': 'nightlife',
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'fr-FR,fr;q=0.9',
        })
    
    def scrape_category(self, category: str, max_pages: int = 3) -> List[Dict[str, Any]]:
        """Scrape une catégorie d'événements."""
        events = []
        
        for page in range(1, max_pages + 1):
            url = f"{self.BASE_URL}/{category}?page={page}"
            print(f"  📄 Scraping {url}")
            
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Trouver les cartes d'événements
                event_cards = soup.select('.event-card, .card-event, article.event')
                
                if not event_cards:
                    # Essayer d'autres sélecteurs
                    event_cards = soup.select('[data-event], .liste-events li, .results-item')
                
                for card in event_cards:
                    event = self._parse_event_card(card, category)
                    if event:
                        events.append(event)
                
                # Pause entre les pages
                time.sleep(1)
                
            except Exception as e:
                print(f"  ❌ Erreur page {page}: {e}")
                continue
        
        return events
    
    def _parse_event_card(self, card, category: str) -> Optional[Dict[str, Any]]:
        """Parse une carte d'événement."""
        try:
            # Titre
            title_elem = card.select_one('h2, h3, .title, .event-title, a[title]')
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)
            if not title:
                return None
            
            # Lien
            link_elem = card.select_one('a[href]')
            link = link_elem['href'] if link_elem else ""
            if link and not link.startswith('http'):
                link = self.BASE_URL + link
            
            # Date
            date_elem = card.select_one('.date, .event-date, time')
            date_str = date_elem.get_text(strip=True) if date_elem else ""
            event_date = self._parse_date(date_str)
            
            # Lieu
            venue_elem = card.select_one('.lieu, .venue, .location, address')
            venue = venue_elem.get_text(strip=True) if venue_elem else "Paris"
            
            # Description
            desc_elem = card.select_one('.description, .summary, p')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Image
            img_elem = card.select_one('img')
            image_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else None
            
            # Prix
            price_elem = card.select_one('.price, .tarif, .prix')
            price_text = price_elem.get_text(strip=True) if price_elem else "Gratuit"
            price, price_max = parse_price(price_text)
            
            # Heure
            time_elem = card.select_one('.time, .horaire, .hour')
            start_time = None
            if time_elem:
                time_text = time_elem.get_text(strip=True)
                time_match = re.search(r'(\d{1,2})[hH:](\d{2})?', time_text)
                if time_match:
                    hour = time_match.group(1).zfill(2)
                    minute = time_match.group(2) or "00"
                    start_time = f"{hour}:{minute}"
            
            main_cat = self.CATEGORY_MAPPING.get(category, 'culture')
            
            event = {
                'id': generate_event_id('qfp', title, event_date, venue),
                'title': title,
                'description': description[:500] if description else "",
                'main_category': main_cat,
                'sub_category': category,
                'date': event_date,
                'start_time': start_time,
                'end_time': None,
                'time_of_day': determine_time_of_day(start_time),
                'venue': venue.split(',')[0] if ',' in venue else venue,
                'address': venue,
                'arrondissement': extract_arrondissement(venue),
                'price': price,
                'price_max': price_max,
                'source_url': link,
                'source_name': self.SOURCE_NAME,
                'image_url': image_url,
                'duration': None,
                'booking_required': False,
                'tags': [category, main_cat],
                'latitude': None,
                'longitude': None,
                'verified': True,
            }
            
            return event
            
        except Exception as e:
            print(f"  ⚠️ Erreur parsing: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> str:
        """Parse une date en format YYYY-MM-DD."""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        # Nettoyer
        date_str = date_str.lower().strip()
        
        # Patterns français
        months = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12,
            'janv': 1, 'févr': 2, 'avr': 4, 'juil': 7, 'sept': 9,
            'oct': 10, 'nov': 11, 'déc': 12
        }
        
        # "15 décembre 2025"
        for month_name, month_num in months.items():
            if month_name in date_str:
                match = re.search(r'(\d{1,2})\s*' + month_name + r'\s*(\d{4})?', date_str)
                if match:
                    day = int(match.group(1))
                    year = int(match.group(2)) if match.group(2) else datetime.now().year
                    return f"{year}-{month_num:02d}-{day:02d}"
        
        # Format DD/MM/YYYY ou DD-MM-YYYY
        match = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})', date_str)
        if match:
            day, month, year = match.groups()
            if len(year) == 2:
                year = '20' + year
            return f"{year}-{int(month):02d}-{int(day):02d}"
        
        # Par défaut: aujourd'hui
        return datetime.now().strftime('%Y-%m-%d')
    
    def scrape_all(self) -> List[Dict[str, Any]]:
        """Scrape toutes les catégories."""
        all_events = []
        categories = ['concerts', 'spectacles', 'expositions', 'ateliers', 'conferences']
        
        for cat in categories:
            print(f"\n🔍 Catégorie: {cat}")
            events = self.scrape_category(cat, max_pages=2)
            all_events.extend(events)
            print(f"  ✅ {len(events)} événements trouvés")
        
        return all_events


class SortirAParisScraper:
    """Scraper pour sortiraparis.com"""
    
    BASE_URL = "https://www.sortiraparis.com"
    SOURCE_NAME = "Sortir à Paris"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml',
        })
    
    def scrape_agenda(self, max_pages: int = 3) -> List[Dict[str, Any]]:
        """Scrape l'agenda principal."""
        events = []
        
        for page in range(1, max_pages + 1):
            url = f"{self.BASE_URL}/loisirs/agenda-culturel-de-paris/page/{page}"
            print(f"  📄 Scraping {url}")
            
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Articles d'événements
                articles = soup.select('article, .article-item, .event-item')
                
                for article in articles:
                    event = self._parse_article(article)
                    if event:
                        events.append(event)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"  ❌ Erreur: {e}")
                continue
        
        return events
    
    def _parse_article(self, article) -> Optional[Dict[str, Any]]:
        """Parse un article d'événement."""
        try:
            title_elem = article.select_one('h2, h3, .title a')
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            if not title or len(title) < 5:
                return None
            
            link = article.select_one('a[href]')
            source_url = link['href'] if link else ""
            if source_url and not source_url.startswith('http'):
                source_url = self.BASE_URL + source_url
            
            # Déterminer la catégorie depuis le titre ou les tags
            main_category = self._guess_category(title)
            
            event = {
                'id': generate_event_id('sap', title, datetime.now().strftime('%Y-%m-%d'), 'Paris'),
                'title': title[:200],
                'description': "",
                'main_category': main_category,
                'sub_category': None,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'start_time': None,
                'end_time': None,
                'time_of_day': 'soir',
                'venue': 'Paris',
                'address': 'Paris',
                'arrondissement': None,
                'price': 0,
                'price_max': None,
                'source_url': source_url,
                'source_name': self.SOURCE_NAME,
                'image_url': None,
                'duration': None,
                'booking_required': False,
                'tags': [main_category],
                'latitude': None,
                'longitude': None,
                'verified': False,  # Besoin de vérification manuelle
            }
            
            return event
            
        except Exception:
            return None
    
    def _guess_category(self, title: str) -> str:
        """Devine la catégorie depuis le titre."""
        title_lower = title.lower()
        
        if any(w in title_lower for w in ['concert', 'musique', 'jazz', 'rock', 'electro', 'rap']):
            return 'musique'
        elif any(w in title_lower for w in ['expo', 'exposition', 'musée', 'galerie', 'art']):
            return 'arts_visuels'
        elif any(w in title_lower for w in ['théâtre', 'spectacle', 'comédie', 'opéra', 'ballet']):
            return 'spectacles'
        elif any(w in title_lower for w in ['atelier', 'cours', 'workshop']):
            return 'ateliers'
        elif any(w in title_lower for w in ['restaurant', 'gastronomie', 'dégustation', 'brunch']):
            return 'gastronomie'
        elif any(w in title_lower for w in ['club', 'soirée', 'night', 'disco']):
            return 'nightlife'
        elif any(w in title_lower for w in ['sport', 'running', 'vélo', 'yoga']):
            return 'sport'
        else:
            return 'culture'


class OpenAgendaScraper:
    """Scraper utilisant l'API OpenAgenda."""
    
    API_URL = "https://api.openagenda.com/v2"
    SOURCE_NAME = "OpenAgenda"
    
    # IDs des agendas parisiens populaires sur OpenAgenda
    PARIS_AGENDAS = [
        # Ces IDs doivent être récupérés depuis OpenAgenda
        # Vous pouvez les trouver en visitant openagenda.com et en cherchant des agendas parisiens
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or OPENAGENDA_API_KEY
        self.session = requests.Session()
    
    def search_paris_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Recherche des événements à Paris via l'API."""
        if not self.api_key:
            print("⚠️ Clé API OpenAgenda non configurée")
            return []
        
        events = []
        
        try:
            # Recherche par localisation
            params = {
                'key': self.api_key,
                'geo': {
                    'latitude': 48.8566,
                    'longitude': 2.3522,
                    'radius': 15000  # 15km autour de Paris
                },
                'timings[gte]': datetime.now().strftime('%Y-%m-%d'),
                'size': min(limit, 100),
                'sort': 'timings.asc',
            }
            
            response = self.session.get(
                f"{self.API_URL}/events",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('events', []):
                    event = self._parse_api_event(item)
                    if event:
                        events.append(event)
            else:
                print(f"❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur API: {e}")
        
        return events
    
    def _parse_api_event(self, item: Dict) -> Optional[Dict[str, Any]]:
        """Parse un événement depuis l'API OpenAgenda."""
        try:
            title = item.get('title', {}).get('fr') or item.get('title', {}).get('en', '')
            if not title:
                return None
            
            description = item.get('description', {}).get('fr', '')
            
            # Dates
            timings = item.get('timings', [])
            if timings:
                first_timing = timings[0]
                event_date = first_timing.get('start', '')[:10]
                start_time = first_timing.get('start', '')[11:16] if 'T' in first_timing.get('start', '') else None
            else:
                event_date = datetime.now().strftime('%Y-%m-%d')
                start_time = None
            
            # Lieu
            location = item.get('location', {})
            venue = location.get('name', 'Paris')
            address = location.get('address', 'Paris')
            lat = location.get('latitude')
            lon = location.get('longitude')
            
            # Prix
            price_info = item.get('registration', {})
            price = 0
            if price_info.get('type') == 'paid':
                price = price_info.get('price', 0)
            
            # Catégorie
            keywords = item.get('keywords', {}).get('fr', [])
            main_category = self._determine_category(keywords, title)
            
            event = {
                'id': generate_event_id('oa', title, event_date, venue),
                'title': title[:200],
                'description': description[:500],
                'main_category': main_category,
                'sub_category': None,
                'date': event_date,
                'start_time': start_time,
                'end_time': None,
                'time_of_day': determine_time_of_day(start_time),
                'venue': venue,
                'address': address,
                'arrondissement': extract_arrondissement(address),
                'price': float(price),
                'price_max': None,
                'source_url': item.get('canonicalUrl', ''),
                'source_name': self.SOURCE_NAME,
                'image_url': item.get('image', {}).get('base') if item.get('image') else None,
                'duration': None,
                'booking_required': item.get('registration', {}).get('type') == 'required',
                'tags': keywords[:5] if keywords else [],
                'latitude': lat,
                'longitude': lon,
                'verified': True,
            }
            
            return event
            
        except Exception as e:
            print(f"⚠️ Erreur parsing OpenAgenda: {e}")
            return None
    
    def _determine_category(self, keywords: List[str], title: str) -> str:
        """Détermine la catégorie principale."""
        keywords_lower = [k.lower() for k in keywords]
        title_lower = title.lower()
        
        music_words = ['concert', 'musique', 'jazz', 'rock', 'classique', 'electro']
        if any(w in keywords_lower or w in title_lower for w in music_words):
            return 'musique'
        
        art_words = ['exposition', 'art', 'musée', 'galerie', 'photo']
        if any(w in keywords_lower or w in title_lower for w in art_words):
            return 'arts_visuels'
        
        show_words = ['théâtre', 'spectacle', 'danse', 'cirque', 'opéra']
        if any(w in keywords_lower or w in title_lower for w in show_words):
            return 'spectacles'
        
        return 'culture'


def run_scraping(save_to_db: bool = True) -> Dict[str, Any]:
    """Exécute le scraping de toutes les sources."""
    print("🎭 Artify - Scraping des événements réels\n")
    print("=" * 50)
    
    all_events = []
    stats = {}
    
    # 1. Que Faire à Paris
    print("\n📍 Source: Que Faire à Paris")
    try:
        qfp_scraper = QueFaireParissScraper()
        qfp_events = qfp_scraper.scrape_all()
        all_events.extend(qfp_events)
        stats['que_faire_paris'] = len(qfp_events)
        print(f"✅ Total: {len(qfp_events)} événements")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        stats['que_faire_paris'] = 0
    
    # 2. Sortir à Paris
    print("\n📍 Source: Sortir à Paris")
    try:
        sap_scraper = SortirAParisScraper()
        sap_events = sap_scraper.scrape_agenda(max_pages=2)
        all_events.extend(sap_events)
        stats['sortir_a_paris'] = len(sap_events)
        print(f"✅ Total: {len(sap_events)} événements")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        stats['sortir_a_paris'] = 0
    
    # 3. OpenAgenda (si clé API disponible)
    if OPENAGENDA_API_KEY:
        print("\n📍 Source: OpenAgenda API")
        try:
            oa_scraper = OpenAgendaScraper()
            oa_events = oa_scraper.search_paris_events(limit=100)
            all_events.extend(oa_events)
            stats['openagenda'] = len(oa_events)
            print(f"✅ Total: {len(oa_events)} événements")
        except Exception as e:
            print(f"❌ Erreur: {e}")
            stats['openagenda'] = 0
    else:
        print("\n⚠️ OpenAgenda: Clé API non configurée (optionnel)")
        stats['openagenda'] = 0
    
    print("\n" + "=" * 50)
    print(f"📊 TOTAL: {len(all_events)} événements récupérés")
    
    # Sauvegarder en base de données
    if save_to_db and all_events:
        print("\n💾 Sauvegarde en base de données...")
        db = EventsDatabase()
        result = db.add_batch(all_events)
        print(f"  ✅ Ajoutés: {result['added']}")
        print(f"  🔄 Mis à jour: {result['updated']}")
        
        # Log
        db.log_scrape(
            source_id='all',
            events_found=len(all_events),
            events_added=result['added'],
            events_updated=result['updated'],
            success=True
        )
    
    return {
        'total': len(all_events),
        'stats': stats,
        'events': all_events
    }


if __name__ == "__main__":
    result = run_scraping(save_to_db=True)
    
    print("\n📊 Statistiques finales:")
    for source, count in result['stats'].items():
        print(f"  {source}: {count} événements")


