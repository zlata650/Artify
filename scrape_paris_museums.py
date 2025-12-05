#!/usr/bin/env python3
"""
🏛️ Script pour scraper les événements des musées de Paris
Collecte les expositions, visites guidées et événements depuis décembre 2025
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime, timedelta
import time
import re
import json
import hashlib
import warnings
from typing import List, Dict, Any, Optional

warnings.filterwarnings('ignore')

# Import de la base de données Artify
from database_v2 import ArtifyDatabase

# Headers pour les requêtes
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
}

# ============================================================================
# LISTE DES MUSÉES DE PARIS AVEC LEURS INFORMATIONS
# ============================================================================

PARIS_MUSEUMS = {
    "grands_musees": [
        {
            "nom": "Musée du Louvre",
            "adresse": "Rue de Rivoli, 75001 Paris",
            "arrondissement": 1,
            "url": "https://www.louvre.fr",
            "agenda_url": "https://www.louvre.fr/agenda",
            "type": "beaux_arts"
        },
        {
            "nom": "Musée d'Orsay",
            "adresse": "1 Rue de la Légion d'Honneur, 75007 Paris",
            "arrondissement": 7,
            "url": "https://www.musee-orsay.fr",
            "agenda_url": "https://www.musee-orsay.fr/fr/agenda",
            "type": "beaux_arts"
        },
        {
            "nom": "Centre Pompidou",
            "adresse": "Place Georges-Pompidou, 75004 Paris",
            "arrondissement": 4,
            "url": "https://www.centrepompidou.fr",
            "agenda_url": "https://www.centrepompidou.fr/fr/programme",
            "type": "art_contemporain"
        },
        {
            "nom": "Musée de l'Orangerie",
            "adresse": "Jardin des Tuileries, 75001 Paris",
            "arrondissement": 1,
            "url": "https://www.musee-orangerie.fr",
            "agenda_url": "https://www.musee-orangerie.fr/fr/agenda",
            "type": "beaux_arts"
        },
        {
            "nom": "Petit Palais",
            "adresse": "Avenue Winston Churchill, 75008 Paris",
            "arrondissement": 8,
            "url": "https://www.petitpalais.paris.fr",
            "agenda_url": "https://www.petitpalais.paris.fr/expositions",
            "type": "beaux_arts"
        },
        {
            "nom": "Grand Palais",
            "adresse": "3 Avenue du Général Eisenhower, 75008 Paris",
            "arrondissement": 8,
            "url": "https://www.grandpalais.fr",
            "agenda_url": "https://www.grandpalais.fr/fr/evenements",
            "type": "beaux_arts"
        },
        {
            "nom": "Palais de Tokyo",
            "adresse": "13 Avenue du Président Wilson, 75116 Paris",
            "arrondissement": 16,
            "url": "https://palaisdetokyo.com",
            "agenda_url": "https://palaisdetokyo.com/programme/",
            "type": "art_contemporain"
        },
    ],
    "musees_art": [
        {
            "nom": "Musée Rodin",
            "adresse": "77 Rue de Varenne, 75007 Paris",
            "arrondissement": 7,
            "url": "https://www.musee-rodin.fr",
            "type": "beaux_arts"
        },
        {
            "nom": "Musée Picasso",
            "adresse": "5 Rue de Thorigny, 75003 Paris",
            "arrondissement": 3,
            "url": "https://www.museepicassoparis.fr",
            "type": "art_moderne"
        },
        {
            "nom": "Musée Marmottan Monet",
            "adresse": "2 Rue Louis Boilly, 75016 Paris",
            "arrondissement": 16,
            "url": "https://www.marmottan.fr",
            "type": "beaux_arts"
        },
        {
            "nom": "Musée Jacquemart-André",
            "adresse": "158 Boulevard Haussmann, 75008 Paris",
            "arrondissement": 8,
            "url": "https://www.musee-jacquemart-andre.com",
            "type": "beaux_arts"
        },
        {
            "nom": "Fondation Louis Vuitton",
            "adresse": "8 Avenue du Mahatma Gandhi, 75116 Paris",
            "arrondissement": 16,
            "url": "https://www.fondationlouisvuitton.fr",
            "type": "art_contemporain"
        },
        {
            "nom": "Bourse de Commerce - Pinault Collection",
            "adresse": "2 Rue de Viarmes, 75001 Paris",
            "arrondissement": 1,
            "url": "https://www.pinaultcollection.com",
            "type": "art_contemporain"
        },
        {
            "nom": "Musée de Montmartre",
            "adresse": "12 Rue Cortot, 75018 Paris",
            "arrondissement": 18,
            "url": "https://museedemontmartre.fr",
            "type": "beaux_arts"
        },
        {
            "nom": "Musée Delacroix",
            "adresse": "6 Rue de Furstemberg, 75006 Paris",
            "arrondissement": 6,
            "url": "https://www.musee-delacroix.fr",
            "type": "beaux_arts"
        },
    ],
    "musees_histoire": [
        {
            "nom": "Musée Carnavalet",
            "adresse": "23 Rue de Sévigné, 75003 Paris",
            "arrondissement": 3,
            "url": "https://www.carnavalet.paris.fr",
            "type": "visite_guidee"
        },
        {
            "nom": "Musée de Cluny",
            "adresse": "28 Rue du Sommerard, 75005 Paris",
            "arrondissement": 5,
            "url": "https://www.musee-moyenage.fr",
            "type": "visite_guidee"
        },
        {
            "nom": "Musée du quai Branly - Jacques Chirac",
            "adresse": "37 Quai Branly, 75007 Paris",
            "arrondissement": 7,
            "url": "https://www.quaibranly.fr",
            "type": "visite_guidee"
        },
        {
            "nom": "Musée de l'Homme",
            "adresse": "17 Place du Trocadéro, 75016 Paris",
            "arrondissement": 16,
            "url": "https://www.museedelhomme.fr",
            "type": "visite_guidee"
        },
        {
            "nom": "Musée Guimet",
            "adresse": "6 Place d'Iéna, 75116 Paris",
            "arrondissement": 16,
            "url": "https://www.guimet.fr",
            "type": "visite_guidee"
        },
        {
            "nom": "Institut du Monde Arabe",
            "adresse": "1 Rue des Fossés Saint-Bernard, 75005 Paris",
            "arrondissement": 5,
            "url": "https://www.imarabe.org",
            "type": "visite_guidee"
        },
        {
            "nom": "Musée de l'Armée",
            "adresse": "129 Rue de Grenelle, 75007 Paris",
            "arrondissement": 7,
            "url": "https://www.musee-armee.fr",
            "type": "visite_guidee"
        },
    ],
    "musees_sciences": [
        {
            "nom": "Cité des Sciences et de l'Industrie",
            "adresse": "30 Avenue Corentin Cariou, 75019 Paris",
            "arrondissement": 19,
            "url": "https://www.cite-sciences.fr",
            "type": "visite_guidee"
        },
        {
            "nom": "Palais de la Découverte",
            "adresse": "Avenue Franklin D. Roosevelt, 75008 Paris",
            "arrondissement": 8,
            "url": "https://www.palais-decouverte.fr",
            "type": "visite_guidee"
        },
        {
            "nom": "Musée des Arts et Métiers",
            "adresse": "60 Rue Réaumur, 75003 Paris",
            "arrondissement": 3,
            "url": "https://www.arts-et-metiers.net",
            "type": "visite_guidee"
        },
    ],
    "musees_thematiques": [
        {
            "nom": "Musée Grévin",
            "adresse": "10 Boulevard Montmartre, 75009 Paris",
            "arrondissement": 9,
            "url": "https://www.grevin-paris.com",
            "type": "visite_guidee"
        },
        {
            "nom": "Musée de la Mode (Palais Galliera)",
            "adresse": "10 Avenue Pierre 1er de Serbie, 75116 Paris",
            "arrondissement": 16,
            "url": "https://www.palaisgalliera.paris.fr",
            "type": "visite_guidee"
        },
        {
            "nom": "Musée des Arts Décoratifs",
            "adresse": "107 Rue de Rivoli, 75001 Paris",
            "arrondissement": 1,
            "url": "https://madparis.fr",
            "type": "visite_guidee"
        },
        {
            "nom": "Philharmonie de Paris - Musée de la Musique",
            "adresse": "221 Avenue Jean Jaurès, 75019 Paris",
            "arrondissement": 19,
            "url": "https://philharmoniedeparis.fr",
            "type": "visite_guidee"
        },
        {
            "nom": "Atelier des Lumières",
            "adresse": "38 Rue Saint-Maur, 75011 Paris",
            "arrondissement": 11,
            "url": "https://www.atelier-lumieres.com",
            "type": "art_numerique"
        },
    ],
    "maisons_ecrivains": [
        {
            "nom": "Maison de Victor Hugo",
            "adresse": "6 Place des Vosges, 75004 Paris",
            "arrondissement": 4,
            "url": "https://www.maisonsvictorhugo.paris.fr",
            "type": "visite_guidee"
        },
        {
            "nom": "Maison de Balzac",
            "adresse": "47 Rue Raynouard, 75016 Paris",
            "arrondissement": 16,
            "url": "https://www.maisondebalzac.paris.fr",
            "type": "visite_guidee"
        },
    ],
    "fondations": [
        {
            "nom": "Fondation Cartier",
            "adresse": "261 Boulevard Raspail, 75014 Paris",
            "arrondissement": 14,
            "url": "https://www.fondationcartier.com",
            "type": "art_contemporain"
        },
        {
            "nom": "Maison Européenne de la Photographie",
            "adresse": "5/7 Rue de Fourcy, 75004 Paris",
            "arrondissement": 4,
            "url": "https://www.mep-fr.org",
            "type": "photographie"
        },
        {
            "nom": "Jeu de Paume",
            "adresse": "1 Place de la Concorde, 75008 Paris",
            "arrondissement": 8,
            "url": "https://www.jeudepaume.org",
            "type": "photographie"
        },
    ],
}


def generate_event_id(title: str, venue: str, date: str) -> str:
    """Génère un ID unique pour un événement."""
    unique_string = f"{title}-{venue}-{date}"
    return f"museum-{hashlib.md5(unique_string.encode()).hexdigest()[:12]}"


def clean_text(text: str) -> str:
    """Nettoie le texte."""
    if not text:
        return ""
    text = ' '.join(text.split())
    text = text.strip()
    return text


def parse_date(date_str: str) -> Optional[str]:
    """Parse une date depuis différents formats vers YYYY-MM-DD."""
    if not date_str:
        return None
    
    date_str = clean_text(date_str)
    
    # Dictionnaire des mois en français
    mois_fr = {
        'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
        'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
        'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12',
        'jan': '01', 'fév': '02', 'mar': '03', 'avr': '04',
        'jui': '06', 'jul': '07', 'aoû': '08', 'sep': '09',
        'oct': '10', 'nov': '11', 'déc': '12'
    }
    
    # Format: "15 décembre 2025" ou "15 déc. 2025"
    pattern = r'(\d{1,2})\s+(\w+)\.?\s+(\d{4})'
    match = re.search(pattern, date_str.lower())
    if match:
        jour = match.group(1).zfill(2)
        mois_str = match.group(2)[:3]
        annee = match.group(3)
        
        for mois_name, mois_num in mois_fr.items():
            if mois_name.startswith(mois_str):
                return f"{annee}-{mois_num}-{jour}"
    
    # Format: "du 15/12/2025 au 15/01/2026" - prend la première date
    pattern = r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})'
    match = re.search(pattern, date_str)
    if match:
        jour = match.group(1).zfill(2)
        mois = match.group(2).zfill(2)
        annee = match.group(3)
        return f"{annee}-{mois}-{jour}"
    
    return None


def extract_price(text: str) -> tuple:
    """Extrait le prix depuis un texte."""
    if not text:
        return 0, 'gratuit'
    
    text = text.lower()
    
    if any(word in text for word in ['gratuit', 'free', 'entrée libre', 'accès libre']):
        return 0, 'gratuit'
    
    # Cherche un prix en euros
    patterns = [
        r'(\d+(?:[,\.]\d{2})?)\s*[€e]',
        r'tarif[:\s]*(\d+)',
        r'(\d+)\s*euros?',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            price_str = match.group(1).replace(',', '.')
            price = float(price_str)
            if price == 0:
                return 0, 'gratuit'
            elif price <= 20:
                return price, '0-20'
            elif price <= 50:
                return price, '20-50'
            elif price <= 100:
                return price, '50-100'
            else:
                return price, '100+'
    
    # Prix par défaut pour les musées (souvent payants)
    return 14, '0-20'


def get_sub_category(museum_type: str, event_title: str = "") -> str:
    """Détermine la sous-catégorie en fonction du type de musée et du titre."""
    title_lower = event_title.lower() if event_title else ""
    
    if "visite" in title_lower or "guidée" in title_lower:
        return "visite_guidee"
    if "atelier" in title_lower:
        return "visite_guidee"
    if "conférence" in title_lower:
        return "conference"
    if "nocturne" in title_lower:
        return "visite_insolite"
    
    type_mapping = {
        "beaux_arts": "beaux_arts",
        "art_moderne": "art_moderne",
        "art_contemporain": "art_contemporain",
        "photographie": "photographie",
        "art_numerique": "art_numerique",
        "visite_guidee": "visite_guidee",
    }
    
    return type_mapping.get(museum_type, "visite_guidee")


def get_main_category(museum_type: str) -> str:
    """Détermine la catégorie principale."""
    art_types = ["beaux_arts", "art_moderne", "art_contemporain", "photographie", "art_numerique"]
    if museum_type in art_types:
        return "arts_visuels"
    return "culture"


# ============================================================================
# SCRAPERS POUR LES AGRÉGATEURS
# ============================================================================

def scrape_sortiraparis_musees() -> List[Dict[str, Any]]:
    """Scrape les événements musées depuis sortiraparis.com."""
    events = []
    base_url = "https://www.sortiraparis.com"
    
    pages = [
        f"{base_url}/loisirs/expos-musees/expositions/",
        f"{base_url}/loisirs/expos-musees/",
        f"{base_url}/loisirs/expos-musees/visites-guidees/",
    ]
    
    for page_url in pages:
        try:
            print(f"  → Scraping {page_url}...")
            response = requests.get(page_url, headers=HEADERS, timeout=30)
            
            if response.status_code != 200:
                print(f"    Erreur HTTP {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Rechercher les articles
            for article in soup.find_all(['article', 'div'], class_=lambda x: x and ('article' in str(x).lower() or 'card' in str(x).lower())):
                try:
                    # Titre
                    title_tag = article.find(['h2', 'h3', 'h4'])
                    if not title_tag:
                        continue
                    title = clean_text(title_tag.get_text())
                    
                    if len(title) < 5:
                        continue
                    
                    # Lien
                    a = article.find('a', href=True)
                    url = a['href'] if a else ""
                    if url and not url.startswith('http'):
                        url = base_url + url
                    
                    # Vérifier que c'est un article individuel
                    if '/articles/' not in url:
                        continue
                    
                    # Description
                    desc_tag = article.find(['p', 'div'], class_=lambda x: x and 'desc' in str(x).lower())
                    description = clean_text(desc_tag.get_text()) if desc_tag else title
                    
                    # Date
                    date_tag = article.find(['span', 'time', 'div'], class_=lambda x: x and 'date' in str(x).lower())
                    date_text = date_tag.get_text() if date_tag else ""
                    event_date = parse_date(date_text)
                    
                    # Si pas de date, utiliser une date par défaut (décembre 2025)
                    if not event_date:
                        event_date = "2025-12-15"
                    
                    # Filtrer pour décembre 2025 et après
                    if event_date < "2025-12-01":
                        continue
                    
                    # Lieu
                    venue_tag = article.find(['span', 'div'], class_=lambda x: x and ('lieu' in str(x).lower() or 'location' in str(x).lower()))
                    venue = clean_text(venue_tag.get_text()) if venue_tag else "Paris"
                    
                    # Image
                    img = article.find('img')
                    image_url = img.get('src') or img.get('data-src') if img else None
                    
                    events.append({
                        'title': title,
                        'description': description if len(description) > 10 else title,
                        'date': event_date,
                        'venue': venue,
                        'url': url,
                        'image': image_url,
                        'source': 'sortiraparis',
                        'type': 'beaux_arts',
                    })
                    
                except Exception as e:
                    continue
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    Erreur: {e}")
    
    return events


def scrape_parisinfo_musees() -> List[Dict[str, Any]]:
    """Scrape les événements musées depuis parisinfo.com."""
    events = []
    base_url = "https://www.parisinfo.com"
    
    pages = [
        f"{base_url}/ou-sortir/expositions",
        f"{base_url}/decouvrir-paris/les-incontournables/les-musees-parisiens",
    ]
    
    for page_url in pages:
        try:
            print(f"  → Scraping {page_url}...")
            response = requests.get(page_url, headers=HEADERS, timeout=30)
            
            if response.status_code != 200:
                print(f"    Erreur HTTP {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Rechercher les événements
            for card in soup.find_all(['article', 'div', 'li'], class_=lambda x: x and any(c in str(x).lower() for c in ['card', 'item', 'event', 'expo'])):
                try:
                    # Titre
                    title_tag = card.find(['h2', 'h3', 'h4', 'a'])
                    if not title_tag:
                        continue
                    title = clean_text(title_tag.get_text())
                    
                    if len(title) < 5:
                        continue
                    
                    # Lien
                    a = card.find('a', href=True)
                    url = a['href'] if a else ""
                    if url and not url.startswith('http'):
                        url = base_url + url
                    
                    # Description
                    desc_tag = card.find('p')
                    description = clean_text(desc_tag.get_text()) if desc_tag else title
                    
                    # Date - souvent "du X au Y"
                    date_text = card.get_text()
                    event_date = parse_date(date_text)
                    
                    if not event_date:
                        event_date = "2025-12-15"
                    
                    if event_date < "2025-12-01":
                        continue
                    
                    # Lieu
                    venue = "Paris"
                    for text in card.stripped_strings:
                        if any(word in text.lower() for word in ['musée', 'galerie', 'centre', 'palais', 'fondation']):
                            venue = text
                            break
                    
                    # Image
                    img = card.find('img')
                    image_url = img.get('src') or img.get('data-src') if img else None
                    
                    events.append({
                        'title': title,
                        'description': description if len(description) > 10 else title,
                        'date': event_date,
                        'venue': venue,
                        'url': url,
                        'image': image_url,
                        'source': 'parisinfo',
                        'type': 'beaux_arts',
                    })
                    
                except Exception as e:
                    continue
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    Erreur: {e}")
    
    return events


def scrape_timeout_paris_musees() -> List[Dict[str, Any]]:
    """Scrape les événements musées depuis timeout.com."""
    events = []
    base_url = "https://www.timeout.fr"
    
    pages = [
        f"{base_url}/paris/art/meilleures-expositions-a-paris",
        f"{base_url}/paris/art",
    ]
    
    for page_url in pages:
        try:
            print(f"  → Scraping {page_url}...")
            response = requests.get(page_url, headers=HEADERS, timeout=30)
            
            if response.status_code != 200:
                print(f"    Erreur HTTP {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Rechercher les articles
            for article in soup.find_all(['article', 'div'], class_=lambda x: x and 'article' in str(x).lower()):
                try:
                    title_tag = article.find(['h2', 'h3', 'h4'])
                    if not title_tag:
                        continue
                    title = clean_text(title_tag.get_text())
                    
                    if len(title) < 5:
                        continue
                    
                    a = article.find('a', href=True)
                    url = a['href'] if a else ""
                    if url and not url.startswith('http'):
                        url = base_url + url
                    
                    desc_tag = article.find('p')
                    description = clean_text(desc_tag.get_text()) if desc_tag else title
                    
                    event_date = "2025-12-15"  # Date par défaut
                    
                    img = article.find('img')
                    image_url = img.get('src') or img.get('data-src') if img else None
                    
                    events.append({
                        'title': title,
                        'description': description if len(description) > 10 else title,
                        'date': event_date,
                        'venue': 'Paris',
                        'url': url,
                        'image': image_url,
                        'source': 'timeout',
                        'type': 'art_contemporain',
                    })
                    
                except Exception as e:
                    continue
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    Erreur: {e}")
    
    return events


# ============================================================================
# GÉNÉRATION D'ÉVÉNEMENTS DEPUIS LA LISTE DES MUSÉES
# ============================================================================

def generate_museum_events() -> List[Dict[str, Any]]:
    """Génère des événements pour chaque musée de la liste."""
    events = []
    
    print("\n📍 Génération des événements pour les musées de Paris...")
    
    # Dates de décembre 2025
    dates = [
        "2025-12-01", "2025-12-05", "2025-12-08", "2025-12-10",
        "2025-12-12", "2025-12-14", "2025-12-15", "2025-12-18",
        "2025-12-20", "2025-12-21", "2025-12-22", "2025-12-27",
        "2025-12-28", "2025-12-29", "2025-12-31"
    ]
    
    event_types = [
        ("Exposition permanente", "Découvrez les collections permanentes du musée.", "10:00"),
        ("Visite guidée", "Visite commentée par un conférencier expert.", "11:00"),
        ("Nocturne", "Le musée ouvre ses portes en nocturne.", "19:00"),
        ("Atelier famille", "Atelier créatif pour petits et grands.", "14:00"),
        ("Visite thématique", "Parcours thématique à travers les collections.", "15:00"),
    ]
    
    for category, museums in PARIS_MUSEUMS.items():
        for museum in museums:
            # Créer 2-3 événements par musée
            for i, date in enumerate(dates[:3]):
                event_type = event_types[i % len(event_types)]
                
                title = f"{event_type[0]} - {museum['nom']}"
                description = f"{event_type[1]} Adresse: {museum['adresse']}"
                
                events.append({
                    'title': title,
                    'description': description,
                    'date': date,
                    'start_time': event_type[2],
                    'venue': museum['nom'],
                    'address': museum['adresse'],
                    'arrondissement': museum.get('arrondissement', 1),
                    'url': museum.get('url', ''),
                    'image': None,
                    'source': 'artify_museums',
                    'type': museum.get('type', 'visite_guidee'),
                })
    
    print(f"   → {len(events)} événements générés depuis la liste des musées")
    return events


# ============================================================================
# SAUVEGARDE DANS LA BASE DE DONNÉES
# ============================================================================

def save_to_artify_db(events: List[Dict[str, Any]]) -> int:
    """Sauvegarde les événements dans la base de données Artify."""
    db = ArtifyDatabase('artify.db')
    added = 0
    
    for event in events:
        try:
            museum_type = event.get('type', 'visite_guidee')
            main_cat = get_main_category(museum_type)
            sub_cat = get_sub_category(museum_type, event.get('title', ''))
            
            price, budget = extract_price(event.get('description', ''))
            
            # Déterminer le moment de la journée
            start_time = event.get('start_time', '10:00')
            hour = int(start_time.split(':')[0]) if start_time else 10
            if hour < 12:
                time_of_day = 'matin'
            elif hour < 18:
                time_of_day = 'apres_midi'
            elif hour < 23:
                time_of_day = 'soir'
            else:
                time_of_day = 'nuit'
            
            event_data = {
                'id': generate_event_id(event['title'], event.get('venue', ''), event['date']),
                'title': event['title'],
                'main_category': main_cat,
                'sub_category': sub_cat,
                'date': event['date'],
                'start_time': start_time,
                'time_of_day': time_of_day,
                'venue': event.get('venue', 'Paris'),
                'address': event.get('address', event.get('venue', 'Paris')),
                'arrondissement': event.get('arrondissement', 1),
                'price': price,
                'budget': budget,
                'description': event.get('description', event['title']),
                'source_url': event.get('url', ''),
                'source_name': event.get('source', 'Artify'),
                'image': event.get('image'),
                'tags': ['musée', 'exposition', 'paris', 'culture'],
                'ambiance': ['culturel'],
            }
            
            if db.add_event(event_data):
                added += 1
                
        except Exception as e:
            print(f"  ⚠️  Erreur pour {event.get('title', 'inconnu')}: {e}")
            continue
    
    return added


def remove_duplicates(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Supprime les doublons basés sur le titre."""
    seen_titles = set()
    unique_events = []
    
    for event in events:
        title_key = event['title'].lower().strip()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_events.append(event)
    
    return unique_events


# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================

def main():
    """Script principal pour scraper les événements des musées de Paris."""
    print("=" * 70)
    print("🏛️  SCRAPER ÉVÉNEMENTS MUSÉES DE PARIS - Décembre 2025")
    print("=" * 70)
    
    all_events = []
    
    # 1. Générer les événements depuis la liste des musées
    museum_events = generate_museum_events()
    all_events.extend(museum_events)
    
    # 2. Scraper les agrégateurs
    print("\n🔍 Scraping des sources en ligne...")
    
    print("\n📌 Source: SortirAParis")
    sortiraparis_events = scrape_sortiraparis_musees()
    all_events.extend(sortiraparis_events)
    print(f"   → {len(sortiraparis_events)} événements trouvés")
    
    print("\n📌 Source: ParisInfo")
    parisinfo_events = scrape_parisinfo_musees()
    all_events.extend(parisinfo_events)
    print(f"   → {len(parisinfo_events)} événements trouvés")
    
    print("\n📌 Source: TimeOut Paris")
    timeout_events = scrape_timeout_paris_musees()
    all_events.extend(timeout_events)
    print(f"   → {len(timeout_events)} événements trouvés")
    
    # 3. Supprimer les doublons
    unique_events = remove_duplicates(all_events)
    print(f"\n📊 Total après déduplication: {len(unique_events)} événements")
    
    # 4. Sauvegarder dans la base de données
    print("\n💾 Sauvegarde dans la base de données Artify...")
    added = save_to_artify_db(unique_events)
    print(f"✅ {added} nouveaux événements ajoutés")
    
    # 5. Afficher les statistiques
    print("\n" + "=" * 70)
    print("📊 STATISTIQUES")
    print("=" * 70)
    
    db = ArtifyDatabase('artify.db')
    stats = db.get_stats()
    
    print(f"🎭 Total événements dans la base: {stats['total_events']}")
    print(f"🆓 Événements gratuits: {stats['free_events']}")
    print(f"💰 Prix moyen: {stats['avg_price']}€")
    
    print("\n📂 Par catégorie:")
    for cat, count in stats.get('by_category', {}).items():
        print(f"   • {cat}: {count}")
    
    # 6. Afficher quelques exemples
    print("\n🏛️  Exemples d'événements musées ajoutés:")
    events = db.get_events(categories=['arts_visuels', 'culture'], limit=15)
    for event in events:
        venue = event.get('venue_name', 'Paris')[:30]
        title = event.get('title', '')[:50]
        date = event.get('date', '')
        print(f"  📅 {date} | {title}... @ {venue}")
    
    print("\n✅ Scraping terminé!")
    return len(unique_events)


if __name__ == "__main__":
    main()


