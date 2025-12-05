#!/usr/bin/env python3
"""
Script pour extraire les liens d'événements spécifiques depuis les sites organisateurs.
Aide à trouver les bonnes URLs pour les cartes d'événements.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from url_validator import (
    is_valid_event_url_pattern, 
    is_organizer_url, 
    clean_url,
    HEADERS
)


def extract_event_links_from_organizer(organizer_url: str, max_links: int = 20) -> list:
    """
    Extrait les liens d'événements spécifiques depuis une page d'organisateur.
    
    Args:
        organizer_url: URL de la page d'organisateur/lieu
        max_links: Nombre maximum de liens à retourner
        
    Returns:
        Liste de dicts avec {url, text, confidence}
    """
    print(f"\n🔍 Analyse de: {organizer_url}")
    
    try:
        response = requests.get(organizer_url, headers=HEADERS, timeout=15)
        
        if response.status_code != 200:
            print(f"  ✗ Erreur HTTP {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Patterns de liens qui indiquent des événements
        event_link_patterns = [
            r'/(event|events|spectacle|spectacles|concert|concerts)/',
            r'/(seance|seances|film|films)/',
            r'/(billetterie|tickets|reservation)/',
            r'/(programmation|agenda|saison)/',
            r'/manifestation/',
            r'/spectacle-',
            r'/concert-',
            r'/event-',
            r'/\d{4,}',  # ID numérique
        ]
        
        # Chercher les liens
        found_links = []
        
        for a in soup.find_all('a', href=True):
            href = a.get('href', '')
            text = a.get_text(strip=True)
            
            # Ignorer les liens vides ou trop courts
            if not href or len(href) < 5:
                continue
            
            # Construire l'URL complète
            full_url = urljoin(organizer_url, href)
            cleaned = clean_url(full_url, organizer_url)
            
            if not cleaned:
                continue
            
            # Vérifier si c'est un lien d'événement
            confidence = 0
            
            # Bonus si le lien contient un pattern d'événement
            for pattern in event_link_patterns:
                if re.search(pattern, cleaned, re.IGNORECASE):
                    confidence += 30
                    break
            
            # Bonus si le texte indique un événement
            event_text_keywords = [
                'réserver', 'billets', 'tickets', 'spectacle', 'concert',
                'seance', 'séance', 'horaires', 'dates'
            ]
            for kw in event_text_keywords:
                if kw in text.lower():
                    confidence += 15
                    break
            
            # Bonus si c'est un titre de spectacle/film (texte plus long)
            if len(text) > 10 and not any(x in text.lower() for x in ['accueil', 'contact', 'menu', 'connexion']):
                confidence += 20
            
            # Malus si c'est encore une page d'organisateur
            if is_organizer_url(cleaned):
                confidence -= 50
            
            # Vérifier avec notre validateur
            if is_valid_event_url_pattern(cleaned):
                confidence += 40
            
            # Garder les liens avec une confiance positive
            if confidence > 0:
                found_links.append({
                    'url': cleaned,
                    'text': text[:100] if text else '(sans texte)',
                    'confidence': confidence
                })
        
        # Trier par confiance et dédupliquer
        seen_urls = set()
        unique_links = []
        for link in sorted(found_links, key=lambda x: -x['confidence']):
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)
                if len(unique_links) >= max_links:
                    break
        
        return unique_links
        
    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        return []


def find_best_event_url(organizer_url: str, event_name: str = None) -> str:
    """
    Trouve la meilleure URL d'événement sur un site organisateur.
    
    Args:
        organizer_url: URL du site organisateur
        event_name: Nom optionnel de l'événement recherché
        
    Returns:
        URL de l'événement ou None
    """
    links = extract_event_links_from_organizer(organizer_url, max_links=50)
    
    if not links:
        return None
    
    # Si on a un nom d'événement, chercher une correspondance
    if event_name:
        event_name_lower = event_name.lower()
        for link in links:
            if event_name_lower in link['text'].lower():
                return link['url']
    
    # Sinon, retourner le lien avec la plus haute confiance
    return links[0]['url'] if links else None


def test_organizer_pages():
    """
    Teste l'extraction de liens sur plusieurs sites organisateurs.
    """
    organizers = [
        "https://www.operadeparis.fr/",
        "https://philharmoniedeparis.fr/fr",
        "https://www.sunset-sunside.com/",
        "https://www.comedie-francaise.fr/",
    ]
    
    for url in organizers:
        links = extract_event_links_from_organizer(url, max_links=5)
        
        if links:
            print(f"\n  📌 Liens d'événements trouvés:")
            for i, link in enumerate(links, 1):
                print(f"     {i}. [{link['confidence']}%] {link['text'][:50]}...")
                print(f"        → {link['url'][:70]}...")
        else:
            print(f"  ⚠ Aucun lien d'événement trouvé")


if __name__ == "__main__":
    print("🎭 Extracteur de liens d'événements")
    print("="*60)
    
    # Tester sur quelques pages d'organisateurs
    test_organizer_pages()
    
    print("\n" + "="*60)
    print("✅ Test terminé")


