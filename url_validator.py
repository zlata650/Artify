#!/usr/bin/env python3
"""
Module de validation et nettoyage des URLs pour le scraping d'événements.
Garantit que les liens mènent à des pages d'événements avec possibilité de réservation.
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time

# Headers pour les requêtes
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
}

# Patterns d'URL qui ne sont PAS des pages d'événements individuels
EXCLUDE_URL_PATTERNS = [
    # Pages de listes/catégories
    r'/guides?/',
    r'/categories?/',
    r'/rubrique/',
    r'/tag/',
    r'/tags/',
    r'/search',
    r'/recherche',
    r'\?page=\d+',
    r'/page/\d+',
    r'/p/\d+',
    r'/index\.html?$',
    r'/accueil',
    r'/home',
    
    # Pages d'aide/légales
    r'/mentions-legales',
    r'/cgu',
    r'/cgv',
    r'/politique-confidentialite',
    r'/privacy',
    r'/terms',
    r'/contact',
    r'/about',
    r'/a-propos',
    r'/faq',
    r'/aide',
    r'/help',
    
    # Pages compte utilisateur
    r'/login',
    r'/connexion',
    r'/inscription',
    r'/register',
    r'/signup',
    r'/mon-compte',
    r'/account',
    r'/profil',
    r'/panier',
    r'/cart',
    r'/checkout',
    
    # Réseaux sociaux
    r'facebook\.com',
    r'twitter\.com',
    r'instagram\.com',
    r'linkedin\.com',
    r'youtube\.com',
    r'tiktok\.com',
    
    # Pages d'organisateurs/lieux (pas d'événements spécifiques)
    r'/organizer',
    r'/organiser',
    r'/organisateur',
    r'/organisateurs',
    r'/profile/',
    r'/profil/',
    r'/venue/',
    r'/lieu/',
    r'/lieux/',
    r'/salle/',
    r'/salles/',
    r'/artiste/',
    r'/artist/',
    r'/artists/',
    r'/artistes/',
    r'/band/',
    r'/groupe/',
    
    # Autres
    r'/newsletter',
    r'/rss',
    r'/feed',
    r'/sitemap',
    r'/plan-du-site',
    r'\.pdf$',
    r'\.jpg$',
    r'\.png$',
    r'\.gif$',
    r'#',  # Ancres
]

# Patterns d'URL d'organisateurs à éviter (pages racine de sites)
ORGANIZER_URL_PATTERNS = [
    # Ces URLs sont des pages d'accueil de lieux/organisateurs, pas d'événements
    r'^https?://[^/]+/?$',  # Juste le domaine sans chemin
    r'^https?://[^/]+/fr/?$',  # Page d'accueil en français
    r'^https?://[^/]+/en/?$',  # Page d'accueil en anglais
    r'^https?://www\.[^/]+/?$',  # www.site.com/
]

# Patterns d'URL qui indiquent une page d'événement INDIVIDUEL
EVENT_URL_PATTERNS = {
    'sortiraparis.com': [
        r'/articles/\d+',  # Articles individuels
        r'/[^/]+/[^/]+/articles/\d+-',  # Ex: /scenes/concert-musique/articles/12345-nom
    ],
    'allocine.fr': [
        r'/film/fichefilm_gen_cfilm=\d+',  # Fiche film
        r'/seance/salle_gen_csalle=\d+',  # Séance
    ],
    'premiere.fr': [
        r'/film/[^/]+-\d+',  # Film avec ID
    ],
    'telerama.fr': [
        r'/cinema/films?/[^/]+',  # Film individuel
    ],
    'fnacspectacles.com': [
        r'/place-spectacle/manifestation/',  # Page événement
        r'/[^/]+-a\d+',  # Event avec ID
    ],
    'ticketmaster.fr': [
        r'/event/\d+',
        r'/artist/\d+',
        r'/manifestation/',
    ],
    'billetreduc.com': [
        r'/\d+/',  # ID numérique
    ],
    'legrandrex.com': [
        r'/films?/[^/]+$',  # Fiche film spécifique
    ],
    'cinemalouxor.fr': [
        r'/films?/[^/]+$',
    ],
    'mk2.com': [
        r'/films?/[^/]+$',
    ],
    'operadeparis.fr': [
        r'/saison-\d+/[^/]+$',  # Page spectacle spécifique
        r'/spectacles/[^/]+$',
    ],
    'philharmoniedeparis.fr': [
        r'/concert/\d+',  # Concert spécifique
        r'/activite/\d+',
    ],
    'theatredelaville-paris.com': [
        r'/spectacle/[^/]+$',
    ],
    'olympiahall.com': [
        r'/concert/[^/]+$',
        r'/spectacle/[^/]+$',
    ],
    'zenith-paris.com': [
        r'/programmation/[^/]+$',
    ],
}

# Mots-clés indiquant une possibilité de réservation/achat
BOOKING_KEYWORDS = [
    'réserver', 'reserver', 'reservation', 'réservation',
    'acheter', 'achat', 'acheter-billets', 'buy-tickets',
    'billets', 'billet', 'tickets', 'ticket',
    'places', 'place', 'entrées', 'entree', 'entrée',
    'tarif', 'tarifs', 'prix',
    'prochaines-dates', 'dates', 'séances', 'seances', 'horaires',
    'disponible', 'disponibles',
    'ajouter-au-panier', 'add-to-cart',
    'booking', 'book-now',
]

# Mots-clés qui indiquent que ce n'est PAS un événement
NON_EVENT_KEYWORDS = [
    'tous les concerts', 'tous les événements', 'toutes les dates',
    'voir tout', 'voir plus', 'afficher plus',
    'liste des', 'agenda', 'calendrier',
    'nos partenaires', 'nos sponsors',
    'à propos', 'qui sommes-nous',
    'conditions générales', 'mentions légales',
]


def is_organizer_url(url: str) -> bool:
    """
    Vérifie si l'URL est une page d'organisateur/lieu (pas un événement spécifique).
    
    Args:
        url: L'URL à vérifier
        
    Returns:
        True si c'est une page d'organisateur, False sinon
    """
    if not url:
        return True
    
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    
    # URL sans chemin = page d'accueil = page d'organisateur
    if not path or path in ['', 'fr', 'en', 'de', 'es', 'it']:
        return True
    
    # Vérifier les patterns d'organisateurs
    for pattern in ORGANIZER_URL_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    
    # Chemin très court sans ID = probablement page de liste
    path_parts = [p for p in path.split('/') if p]
    if len(path_parts) == 1:
        # Un seul segment comme /concerts, /events, /spectacles = page liste
        single_segment_lists = [
            'concerts', 'events', 'evenements', 'spectacles', 'programmation',
            'agenda', 'billetterie', 'tickets', 'programme', 'saison',
            'films', 'seances', 'cinema', 'expositions', 'exhibitions'
        ]
        if path_parts[0].lower() in single_segment_lists:
            return True
    
    return False


def is_valid_event_url_pattern(url: str) -> bool:
    """
    Vérifie si l'URL correspond au pattern d'une page d'événement individuel.
    
    Args:
        url: L'URL à vérifier
        
    Returns:
        True si l'URL semble être une page d'événement, False sinon
    """
    # D'abord vérifier si c'est une URL d'organisateur
    if is_organizer_url(url):
        return False
    
    # Ensuite, exclure les patterns non-événements
    for pattern in EXCLUDE_URL_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return False
    
    # Ensuite, vérifier si c'est un pattern d'événement connu
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    
    for site_domain, patterns in EVENT_URL_PATTERNS.items():
        if site_domain in domain:
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return True
            # Si c'est un domaine connu mais ne matche pas les patterns, c'est suspect
            return False
    
    # Pour les domaines inconnus, on vérifie quelques heuristiques
    path = parsed.path.lower()
    
    # Un article individuel a généralement un ID numérique ou un slug unique
    if re.search(r'/\d{4,}[-/]', url):  # ID numérique d'au moins 4 chiffres
        return True
    
    if re.search(r'/articles?/\d+', url):  # /article/123 ou /articles/123
        return True
    
    # URLs avec /event/ ou /spectacle/ + slug = événement individuel
    if re.search(r'/(event|events|spectacle|spectacles|concert|concerts|seance|film)/[^/]+', url, re.IGNORECASE):
        return True
        
    # Éviter les pages de liste courtes (/, /concerts, /events)
    path_parts = [p for p in path.split('/') if p]
    if len(path_parts) < 2:
        return False
    
    return True


def clean_url(url: str, base_url: str = None) -> str:
    """
    Nettoie et normalise une URL.
    
    Args:
        url: L'URL à nettoyer
        base_url: URL de base pour les liens relatifs
        
    Returns:
        URL nettoyée ou None si invalide
    """
    if not url or not isinstance(url, str):
        return None
    
    url = url.strip()
    
    # Ignorer les ancres, javascript, mailto
    if url.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
        return None
    
    # Convertir les liens relatifs en absolus
    if url.startswith('/'):
        if base_url:
            url = urljoin(base_url, url)
        else:
            return None  # Impossible de résoudre sans base_url
    
    # Vérifier que c'est une URL HTTP(S) valide
    if not url.startswith(('http://', 'https://')):
        if base_url:
            url = urljoin(base_url, url)
        else:
            return None
    
    # Supprimer les fragments d'ancre (#...)
    url = url.split('#')[0]
    
    # Supprimer les paramètres de tracking courants
    tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 
                       'fbclid', 'gclid', 'ref', 'source']
    parsed = urlparse(url)
    
    if parsed.query:
        params = parsed.query.split('&')
        clean_params = [p for p in params if not any(tp in p.lower() for tp in tracking_params)]
        if clean_params:
            url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{'&'.join(clean_params)}"
        else:
            url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    return url


def has_booking_indicators(html_content: str) -> bool:
    """
    Vérifie si la page contient des indicateurs de réservation/achat de billets.
    
    Args:
        html_content: Le contenu HTML de la page
        
    Returns:
        True si des indicateurs de réservation sont trouvés
    """
    if not html_content:
        return False
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Chercher dans les boutons et liens
    for elem in soup.find_all(['a', 'button', 'input']):
        text = elem.get_text(strip=True).lower()
        href = elem.get('href', '').lower()
        class_attr = ' '.join(elem.get('class', [])).lower()
        
        for keyword in BOOKING_KEYWORDS:
            if keyword in text or keyword in href or keyword in class_attr:
                return True
    
    # Chercher dans les textes en général
    page_text = soup.get_text(separator=' ').lower()
    
    # Vérifier les mots-clés de réservation
    booking_found = sum(1 for kw in BOOKING_KEYWORDS if kw in page_text) >= 2
    
    # Vérifier les indicateurs négatifs
    non_event_found = any(kw in page_text for kw in NON_EVENT_KEYWORDS)
    
    if non_event_found and not booking_found:
        return False
    
    return booking_found


def validate_event_url(url: str, verify_booking: bool = False, timeout: int = 10) -> dict:
    """
    Valide complètement une URL d'événement.
    
    Args:
        url: L'URL à valider
        verify_booking: Si True, vérifie que la page a des options de réservation
        timeout: Timeout pour les requêtes HTTP
        
    Returns:
        Dict avec les résultats de validation:
        {
            'valid': bool,
            'url': str (URL nettoyée),
            'reason': str (raison si invalide),
            'has_booking': bool (si verify_booking=True)
        }
    """
    result = {
        'valid': False,
        'url': url,
        'reason': None,
        'has_booking': None
    }
    
    # Nettoyer l'URL
    cleaned_url = clean_url(url)
    if not cleaned_url:
        result['reason'] = "URL invalide ou non nettoyable"
        return result
    
    result['url'] = cleaned_url
    
    # Vérifier le pattern de l'URL
    if not is_valid_event_url_pattern(cleaned_url):
        result['reason'] = "Pattern d'URL ne correspond pas à un événement"
        return result
    
    # Si on veut vérifier la capacité de réservation
    if verify_booking:
        try:
            response = requests.get(cleaned_url, headers=HEADERS, timeout=timeout)
            
            if response.status_code != 200:
                result['reason'] = f"Page inaccessible (HTTP {response.status_code})"
                return result
            
            has_booking = has_booking_indicators(response.text)
            result['has_booking'] = has_booking
            
            if not has_booking:
                result['reason'] = "Pas d'options de réservation détectées"
                return result
                
        except requests.RequestException as e:
            result['reason'] = f"Erreur de connexion: {str(e)}"
            return result
    
    result['valid'] = True
    return result


def filter_event_urls(urls: list, base_url: str = None, verify_booking: bool = False, 
                      max_verify: int = 50, verbose: bool = False) -> list:
    """
    Filtre une liste d'URLs pour ne garder que celles menant à des événements.
    
    Args:
        urls: Liste d'URLs à filtrer
        base_url: URL de base pour les liens relatifs
        verify_booking: Si True, vérifie les pages pour la réservation (plus lent)
        max_verify: Nombre maximum d'URLs à vérifier en détail
        verbose: Si True, affiche les détails du filtrage
        
    Returns:
        Liste d'URLs valides
    """
    valid_urls = []
    verified_count = 0
    
    for url in urls:
        # Nettoyer l'URL
        cleaned = clean_url(url, base_url)
        if not cleaned:
            if verbose:
                print(f"  ✗ URL invalide: {url[:50]}...")
            continue
        
        # Vérifier le pattern
        if not is_valid_event_url_pattern(cleaned):
            if verbose:
                print(f"  ✗ Pattern non-événement: {cleaned[:50]}...")
            continue
        
        # Vérification approfondie (optionnelle, limitée)
        if verify_booking and verified_count < max_verify:
            result = validate_event_url(cleaned, verify_booking=True)
            verified_count += 1
            
            if not result['valid']:
                if verbose:
                    print(f"  ✗ {result['reason']}: {cleaned[:50]}...")
                continue
            
            if verbose:
                print(f"  ✓ Événement validé: {cleaned[:50]}...")
            
            # Petit délai pour éviter de surcharger le serveur
            time.sleep(0.3)
        
        valid_urls.append(cleaned)
    
    return list(set(valid_urls))  # Supprimer les doublons


def validate_and_clean_events(events: list, base_url: str = None, 
                               url_key: str = 'url', verbose: bool = False) -> list:
    """
    Valide et nettoie une liste d'événements (dictionnaires).
    
    Args:
        events: Liste de dictionnaires d'événements
        base_url: URL de base pour les liens relatifs
        url_key: Clé du dictionnaire contenant l'URL
        verbose: Si True, affiche les détails
        
    Returns:
        Liste d'événements avec URLs validées
    """
    valid_events = []
    
    for event in events:
        url = event.get(url_key)
        
        if not url:
            continue
        
        # Nettoyer l'URL
        cleaned = clean_url(url, base_url)
        if not cleaned:
            if verbose:
                print(f"  ✗ URL invalide: {url[:50] if url else 'None'}...")
            continue
        
        # Vérifier le pattern
        if not is_valid_event_url_pattern(cleaned):
            if verbose:
                print(f"  ✗ Non-événement: {cleaned[:50]}...")
            continue
        
        # Mettre à jour l'URL nettoyée
        event[url_key] = cleaned
        valid_events.append(event)
    
    if verbose:
        print(f"\n  → {len(valid_events)}/{len(events)} événements validés")
    
    return valid_events


# Fonctions spécifiques par source
def is_sortiraparis_event_url(url: str) -> bool:
    """Vérifie si c'est une URL d'événement SortiraParis valide."""
    if 'sortiraparis.com' not in url:
        return False
    
    # Les articles d'événements ont le format /xxx/xxx/articles/ID-titre
    if '/articles/' in url and re.search(r'/articles/\d+-', url):
        return True
    
    return False


def is_allocine_event_url(url: str) -> bool:
    """Vérifie si c'est une URL de film AlloCiné valide."""
    if 'allocine.fr' not in url:
        return False
    
    # Les fiches films ont le format /film/fichefilm_gen_cfilm=ID.html
    if '/film/fichefilm_gen_cfilm=' in url:
        return True
    
    return False


def verify_event_page_with_booking(url: str, timeout: int = 10) -> dict:
    """
    Vérifie si une URL mène à une page d'événement avec options de réservation.
    
    Args:
        url: L'URL à vérifier
        timeout: Timeout pour la requête HTTP
        
    Returns:
        Dict avec les résultats:
        {
            'is_event': bool,
            'has_booking': bool,
            'title': str or None,
            'error': str or None
        }
    """
    result = {
        'is_event': False,
        'has_booking': False,
        'title': None,
        'error': None
    }
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        
        if response.status_code != 200:
            result['error'] = f"HTTP {response.status_code}"
            return result
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraire le titre
        title_tag = soup.find('title') or soup.find('h1')
        if title_tag:
            result['title'] = title_tag.get_text(strip=True)[:100]
        
        # Vérifier si c'est une page d'événement (présence de date, lieu, etc.)
        page_text = soup.get_text(separator=' ').lower()
        
        event_indicators = ['date', 'lieu', 'horaire', 'heure', 'adresse', 
                           'séance', 'tarif', 'prix', 'salle', 'durée']
        event_count = sum(1 for ind in event_indicators if ind in page_text)
        result['is_event'] = event_count >= 3
        
        # Vérifier la capacité de réservation
        result['has_booking'] = has_booking_indicators(response.text)
        
    except requests.RequestException as e:
        result['error'] = str(e)
    
    return result


def batch_validate_urls(urls: list, verify_booking: bool = False, 
                        max_concurrent: int = 5, verbose: bool = True) -> list:
    """
    Valide un lot d'URLs et retourne uniquement les valides.
    
    Args:
        urls: Liste d'URLs à valider
        verify_booking: Si True, vérifie la présence d'options de réservation
        max_concurrent: Nombre max d'URLs à vérifier en détail
        verbose: Si True, affiche les statistiques
        
    Returns:
        Liste d'URLs validées
    """
    valid_urls = []
    stats = {
        'total': len(urls),
        'valid_pattern': 0,
        'invalid_pattern': 0,
        'has_booking': 0,
        'no_booking': 0,
        'errors': 0
    }
    
    for i, url in enumerate(urls):
        # Vérification du pattern
        cleaned = clean_url(url)
        if not cleaned or not is_valid_event_url_pattern(cleaned):
            stats['invalid_pattern'] += 1
            continue
        
        stats['valid_pattern'] += 1
        
        # Vérification approfondie optionnelle
        if verify_booking and i < max_concurrent:
            result = verify_event_page_with_booking(cleaned)
            
            if result['error']:
                stats['errors'] += 1
                continue
            
            if result['has_booking']:
                stats['has_booking'] += 1
                valid_urls.append(cleaned)
            else:
                stats['no_booking'] += 1
            
            time.sleep(0.3)
        else:
            valid_urls.append(cleaned)
    
    if verbose:
        print(f"\n📊 Statistiques de validation:")
        print(f"   Total: {stats['total']} URLs")
        print(f"   ✓ Pattern valide: {stats['valid_pattern']}")
        print(f"   ✗ Pattern invalide: {stats['invalid_pattern']}")
        if verify_booking:
            print(f"   ✓ Avec réservation: {stats['has_booking']}")
            print(f"   ✗ Sans réservation: {stats['no_booking']}")
            print(f"   ⚠ Erreurs: {stats['errors']}")
        print(f"   → URLs retenues: {len(valid_urls)}")
    
    return valid_urls


def log_url_validation(url: str, result: bool, reason: str = None):
    """
    Affiche le résultat de la validation d'une URL.
    """
    status = "✓" if result else "✗"
    print(f"{status} {url[:70]}{'...' if len(url) > 70 else ''}")
    if reason:
        print(f"  → {reason}")


def test_event_urls_from_list(urls: list, description: str = "Test URLs"):
    """
    Teste une liste d'URLs et affiche les statistiques.
    """
    print(f"\n{'='*60}")
    print(f"📋 {description}")
    print(f"{'='*60}\n")
    
    valid_count = 0
    organizer_count = 0
    invalid_count = 0
    
    for url in urls:
        cleaned = clean_url(url)
        
        if not cleaned:
            log_url_validation(url, False, "URL invalide ou non nettoyable")
            invalid_count += 1
            continue
        
        if is_organizer_url(cleaned):
            log_url_validation(url, False, "Page d'organisateur/lieu (pas un événement)")
            organizer_count += 1
            continue
        
        if is_valid_event_url_pattern(cleaned):
            log_url_validation(url, True, "URL d'événement valide")
            valid_count += 1
        else:
            log_url_validation(url, False, "Pattern non reconnu comme événement")
            invalid_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Résultats:")
    print(f"   ✓ Événements valides: {valid_count}")
    print(f"   ⚠ Pages organisateurs: {organizer_count}")
    print(f"   ✗ URLs invalides: {invalid_count}")
    print(f"   Total: {len(urls)} URLs")
    print(f"{'='*60}\n")
    
    return valid_count, organizer_count, invalid_count


if __name__ == "__main__":
    # Tests
    print("🔍 Test du validateur d'URLs\n")
    
    # Test 1: URLs d'événements valides
    valid_event_urls = [
        "https://www.sortiraparis.com/scenes/concert-musique/articles/123456-concert-test",
        "https://www.allocine.fr/film/fichefilm_gen_cfilm=123456.html",
        "https://www.sortiraparis.com/soiree/articles/98765-soiree-techno",
        "https://www.fnacspectacles.com/place-spectacle/manifestation/Concert-ORELSAN-ORE24.htm",
        "https://www.ticketmaster.fr/event/12345-concert-metallica",
    ]
    
    # Test 2: URLs de pages d'organisateurs (doivent être rejetées)
    organizer_urls = [
        "https://www.sunset-sunside.com/",
        "https://philharmoniedeparis.fr/fr",
        "https://www.operadeparis.fr/",
        "https://comedie-francaise.fr",
        "https://olympiahall.com",
        "https://rexclub.com",
        "https://www.fondationlouisvuitton.fr/",
        "https://www.louvre.fr/",
        "https://le-zenith.com/",
    ]
    
    # Test 3: URLs invalides (pages de liste, contact, etc.)
    invalid_urls = [
        "https://www.sortiraparis.com/scenes/concert-musique",  # Page liste
        "https://www.sortiraparis.com/guides/concerts",  # Guide
        "https://www.sortiraparis.com/",  # Page d'accueil
        "https://facebook.com/events/123",  # Réseau social
        "/contact",  # Page contact
        "#anchor",  # Ancre
        "javascript:void(0)",  # JavaScript
        "https://venue.com/organizer/123",  # Page organisateur
    ]
    
    # Exécuter les tests
    test_event_urls_from_list(valid_event_urls, "URLs d'ÉVÉNEMENTS valides (doivent passer)")
    test_event_urls_from_list(organizer_urls, "URLs d'ORGANISATEURS (doivent être rejetées)")
    test_event_urls_from_list(invalid_urls, "URLs INVALIDES (doivent être rejetées)")

