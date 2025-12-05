#!/usr/bin/env python3
"""
Script de scraping des événements cinéma actuels à Paris.
Récupère les films à l'affiche depuis plusieurs sources.
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime, timedelta
import time
import re
import json
import warnings

warnings.filterwarnings('ignore')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
}


class EventDatabase:
    """Gère la base de données des événements cinéma."""
    
    def __init__(self, db_path='concerts.db'):
        self.db_path = db_path
        self.conn = None
        self.create_tables()
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        return self.conn.cursor()
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        cursor = self.connect()
        
        # Table des événements cinéma détaillés
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cinema_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titre TEXT NOT NULL,
                cinema TEXT,
                adresse TEXT,
                date_seance TEXT,
                horaire TEXT,
                genre TEXT,
                duree TEXT,
                realisateur TEXT,
                description TEXT,
                url TEXT UNIQUE,
                image_url TEXT,
                prix TEXT,
                source TEXT,
                date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        self.close()
    
    def add_event(self, event):
        cursor = self.connect()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO cinema_events 
                (titre, cinema, adresse, date_seance, horaire, genre, duree, 
                 realisateur, description, url, image_url, prix, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.get('titre'),
                event.get('cinema'),
                event.get('adresse'),
                event.get('date_seance'),
                event.get('horaire'),
                event.get('genre'),
                event.get('duree'),
                event.get('realisateur'),
                event.get('description'),
                event.get('url'),
                event.get('image_url'),
                event.get('prix'),
                event.get('source')
            ))
            self.conn.commit()
            self.close()
            return True
        except Exception as e:
            self.close()
            return False
    
    def add_events_batch(self, events):
        cursor = self.connect()
        added = 0
        for event in events:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO cinema_events 
                    (titre, cinema, adresse, date_seance, horaire, genre, duree, 
                     realisateur, description, url, image_url, prix, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.get('titre'),
                    event.get('cinema'),
                    event.get('adresse'),
                    event.get('date_seance'),
                    event.get('horaire'),
                    event.get('genre'),
                    event.get('duree'),
                    event.get('realisateur'),
                    event.get('description'),
                    event.get('url'),
                    event.get('image_url'),
                    event.get('prix'),
                    event.get('source')
                ))
                added += 1
            except:
                continue
        self.conn.commit()
        self.close()
        return added
    
    def count_events(self):
        cursor = self.connect()
        cursor.execute('SELECT COUNT(*) FROM cinema_events')
        count = cursor.fetchone()[0]
        self.close()
        return count
    
    def get_events_by_date(self, date):
        cursor = self.connect()
        cursor.execute('SELECT * FROM cinema_events WHERE date_seance LIKE ? ORDER BY titre', (f'%{date}%',))
        events = cursor.fetchall()
        self.close()
        return events
    
    def get_all_events(self):
        cursor = self.connect()
        cursor.execute('SELECT * FROM cinema_events ORDER BY date_ajout DESC')
        events = cursor.fetchall()
        self.close()
        return events


def clean_text(text):
    """Nettoie le texte."""
    if not text:
        return None
    text = ' '.join(text.split())
    text = text.strip()
    return text if text else None


def scrape_allocine_films():
    """Scrape les films à l'affiche depuis AlloCiné."""
    print("\n📌 Scraping AlloCiné - Films à l'affiche...")
    events = []
    base_url = "https://www.allocine.fr"
    
    try:
        # Page des films à l'affiche
        url = f"{base_url}/film/aucinema/"
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code != 200:
            print(f"   ❌ Erreur HTTP {response.status_code}")
            return events
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trouver les cartes de films
        film_cards = soup.find_all('div', class_=lambda x: x and 'card' in str(x).lower())
        
        for card in film_cards[:50]:  # Limiter à 50 films
            try:
                # Titre
                title_elem = card.find(['h2', 'h3', 'a'], class_=lambda x: x and 'title' in str(x).lower())
                if not title_elem:
                    title_elem = card.find('a')
                
                titre = clean_text(title_elem.get_text()) if title_elem else None
                
                if not titre or len(titre) < 2:
                    continue
                
                # URL
                link = card.find('a', href=True)
                url = base_url + link['href'] if link and link['href'].startswith('/') else None
                
                # Image
                img = card.find('img')
                image_url = img.get('src') or img.get('data-src') if img else None
                
                # Genre/Info
                meta = card.find('div', class_=lambda x: x and 'meta' in str(x).lower())
                genre = clean_text(meta.get_text()) if meta else None
                
                if titre and url:
                    events.append({
                        'titre': titre,
                        'cinema': 'Paris - Tous cinémas',
                        'adresse': 'Paris',
                        'date_seance': 'Décembre 2025',
                        'horaire': 'Voir horaires',
                        'genre': genre,
                        'duree': None,
                        'realisateur': None,
                        'description': None,
                        'url': url,
                        'image_url': image_url,
                        'prix': None,
                        'source': 'allocine'
                    })
            except:
                continue
        
        print(f"   ✅ {len(events)} films trouvés")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    return events


def scrape_ugc():
    """Scrape les films depuis UGC."""
    print("\n📌 Scraping UGC...")
    events = []
    
    try:
        url = "https://www.ugc.fr/films.html"
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.find_all(['article', 'div'], class_=lambda x: x and ('film' in str(x).lower() or 'movie' in str(x).lower())):
                try:
                    title = item.find(['h2', 'h3', 'a'])
                    titre = clean_text(title.get_text()) if title else None
                    
                    link = item.find('a', href=True)
                    film_url = link['href'] if link else None
                    if film_url and not film_url.startswith('http'):
                        film_url = "https://www.ugc.fr" + film_url
                    
                    img = item.find('img')
                    image_url = img.get('src') or img.get('data-src') if img else None
                    
                    if titre and len(titre) > 2:
                        events.append({
                            'titre': titre,
                            'cinema': 'UGC Paris',
                            'adresse': 'Paris',
                            'date_seance': 'Décembre 2025',
                            'horaire': 'Voir horaires sur ugc.fr',
                            'genre': 'Cinéma',
                            'duree': None,
                            'realisateur': None,
                            'description': None,
                            'url': film_url,
                            'image_url': image_url,
                            'prix': '10-15€',
                            'source': 'ugc'
                        })
                except:
                    continue
        
        print(f"   ✅ {len(events)} films trouvés")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    return events


def scrape_pathe():
    """Scrape les films depuis Pathé."""
    print("\n📌 Scraping Pathé...")
    events = []
    
    try:
        url = "https://www.pathe.fr/films"
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.find_all(['article', 'div', 'li'], class_=lambda x: x and ('film' in str(x).lower() or 'card' in str(x).lower() or 'movie' in str(x).lower())):
                try:
                    title = item.find(['h2', 'h3', 'h4', 'a'])
                    titre = clean_text(title.get_text()) if title else None
                    
                    link = item.find('a', href=True)
                    film_url = link['href'] if link else None
                    if film_url and not film_url.startswith('http'):
                        film_url = "https://www.pathe.fr" + film_url
                    
                    img = item.find('img')
                    image_url = img.get('src') or img.get('data-src') if img else None
                    
                    if titre and len(titre) > 2:
                        events.append({
                            'titre': titre,
                            'cinema': 'Pathé Paris',
                            'adresse': 'Paris',
                            'date_seance': 'Décembre 2025',
                            'horaire': 'Voir horaires sur pathe.fr',
                            'genre': 'Cinéma',
                            'duree': None,
                            'realisateur': None,
                            'description': None,
                            'url': film_url,
                            'image_url': image_url,
                            'prix': '10-15€',
                            'source': 'pathe'
                        })
                except:
                    continue
        
        print(f"   ✅ {len(events)} films trouvés")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    return events


def scrape_mk2():
    """Scrape les films depuis MK2."""
    print("\n📌 Scraping MK2...")
    events = []
    
    try:
        url = "https://www.mk2.com/films"
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # MK2 utilise souvent des structures modernes
            for item in soup.find_all(['article', 'div', 'a'], class_=lambda x: x and ('film' in str(x).lower() or 'card' in str(x).lower() or 'movie' in str(x).lower())):
                try:
                    title = item.find(['h2', 'h3', 'h4', 'span'])
                    titre = clean_text(title.get_text()) if title else None
                    
                    if item.name == 'a':
                        film_url = item.get('href')
                    else:
                        link = item.find('a', href=True)
                        film_url = link['href'] if link else None
                    
                    if film_url and not film_url.startswith('http'):
                        film_url = "https://www.mk2.com" + film_url
                    
                    img = item.find('img')
                    image_url = img.get('src') or img.get('data-src') if img else None
                    
                    if titre and len(titre) > 2:
                        events.append({
                            'titre': titre,
                            'cinema': 'MK2 Paris',
                            'adresse': 'Paris',
                            'date_seance': 'Décembre 2025',
                            'horaire': 'Voir horaires sur mk2.com',
                            'genre': 'Cinéma Art et Essai',
                            'duree': None,
                            'realisateur': None,
                            'description': None,
                            'url': film_url,
                            'image_url': image_url,
                            'prix': '8-14€',
                            'source': 'mk2'
                        })
                except:
                    continue
        
        print(f"   ✅ {len(events)} films trouvés")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    return events


def scrape_grand_rex():
    """Scrape les événements depuis Le Grand Rex."""
    print("\n📌 Scraping Le Grand Rex...")
    events = []
    
    try:
        url = "https://www.legrandrex.com/films"
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.find_all(['article', 'div', 'li']):
                try:
                    title = item.find(['h2', 'h3', 'h4', 'a'])
                    titre = clean_text(title.get_text()) if title else None
                    
                    link = item.find('a', href=True)
                    film_url = link['href'] if link else None
                    if film_url and not film_url.startswith('http'):
                        film_url = "https://www.legrandrex.com" + film_url
                    
                    if titre and len(titre) > 3 and 'rex' not in titre.lower():
                        events.append({
                            'titre': titre,
                            'cinema': 'Le Grand Rex',
                            'adresse': '1 boulevard Poissonnière, 75002 Paris',
                            'date_seance': 'Décembre 2025',
                            'horaire': 'Voir horaires',
                            'genre': 'Événement cinéma',
                            'duree': None,
                            'realisateur': None,
                            'description': None,
                            'url': film_url,
                            'image_url': None,
                            'prix': '10-20€',
                            'source': 'grandrex'
                        })
                except:
                    continue
        
        print(f"   ✅ {len(events)} événements trouvés")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    return events


def scrape_cinematheque():
    """Scrape les événements depuis la Cinémathèque Française."""
    print("\n📌 Scraping Cinémathèque Française...")
    events = []
    
    try:
        url = "https://www.cinematheque.fr/cycle/seances-du-jour.html"
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.find_all(['article', 'div', 'li'], class_=lambda x: x and ('seance' in str(x).lower() or 'film' in str(x).lower() or 'event' in str(x).lower())):
                try:
                    title = item.find(['h2', 'h3', 'h4', 'a'])
                    titre = clean_text(title.get_text()) if title else None
                    
                    link = item.find('a', href=True)
                    film_url = link['href'] if link else None
                    if film_url and not film_url.startswith('http'):
                        film_url = "https://www.cinematheque.fr" + film_url
                    
                    time_elem = item.find(class_=lambda x: x and 'time' in str(x).lower())
                    horaire = clean_text(time_elem.get_text()) if time_elem else None
                    
                    if titre and len(titre) > 2:
                        events.append({
                            'titre': titre,
                            'cinema': 'Cinémathèque Française',
                            'adresse': '51 rue de Bercy, 75012 Paris',
                            'date_seance': 'Décembre 2025',
                            'horaire': horaire or 'Voir programme',
                            'genre': 'Cinémathèque',
                            'duree': None,
                            'realisateur': None,
                            'description': None,
                            'url': film_url,
                            'image_url': None,
                            'prix': '7-10€',
                            'source': 'cinematheque'
                        })
                except:
                    continue
        
        print(f"   ✅ {len(events)} événements trouvés")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    return events


def scrape_louxor():
    """Scrape les films depuis Le Louxor."""
    print("\n📌 Scraping Le Louxor...")
    events = []
    
    try:
        url = "https://www.cinemalouxor.fr/films/a-l-affiche/"
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for item in soup.find_all(['article', 'div', 'li']):
                try:
                    title = item.find(['h2', 'h3', 'h4', 'a'])
                    titre = clean_text(title.get_text()) if title else None
                    
                    link = item.find('a', href=True)
                    film_url = link['href'] if link else None
                    if film_url and not film_url.startswith('http'):
                        film_url = "https://www.cinemalouxor.fr" + film_url
                    
                    img = item.find('img')
                    image_url = img.get('src') if img else None
                    
                    if titre and len(titre) > 2:
                        events.append({
                            'titre': titre,
                            'cinema': 'Le Louxor',
                            'adresse': '170 boulevard de Magenta, 75010 Paris',
                            'date_seance': 'Décembre 2025',
                            'horaire': 'Voir horaires',
                            'genre': 'Art et Essai',
                            'duree': None,
                            'realisateur': None,
                            'description': None,
                            'url': film_url,
                            'image_url': image_url,
                            'prix': '6-10€',
                            'source': 'louxor'
                        })
                except:
                    continue
        
        print(f"   ✅ {len(events)} films trouvés")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    return events


def scrape_sortiraparis():
    """Scrape les événements cinéma depuis SortiraParis."""
    print("\n📌 Scraping SortiraParis - Événements cinéma...")
    events = []
    base_url = "https://www.sortiraparis.com"
    
    try:
        url = f"{base_url}/loisirs/cinema/"
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Chercher les articles
            for article in soup.find_all(['article', 'div'], class_=lambda x: x and ('article' in str(x).lower() or 'card' in str(x).lower())):
                try:
                    title = article.find(['h2', 'h3', 'h4'])
                    titre = clean_text(title.get_text()) if title else None
                    
                    link = article.find('a', href=True)
                    article_url = link['href'] if link else None
                    if article_url and article_url.startswith('/'):
                        article_url = base_url + article_url
                    
                    img = article.find('img')
                    image_url = img.get('src') or img.get('data-src') if img else None
                    
                    # Extraire la date si présente
                    date_elem = article.find(class_=lambda x: x and 'date' in str(x).lower())
                    date_seance = clean_text(date_elem.get_text()) if date_elem else 'Décembre 2025'
                    
                    if titre and len(titre) > 5:
                        events.append({
                            'titre': titre,
                            'cinema': 'Paris',
                            'adresse': 'Paris',
                            'date_seance': date_seance,
                            'horaire': 'Voir détails',
                            'genre': 'Événement cinéma',
                            'duree': None,
                            'realisateur': None,
                            'description': None,
                            'url': article_url,
                            'image_url': image_url,
                            'prix': None,
                            'source': 'sortiraparis'
                        })
                except:
                    continue
        
        print(f"   ✅ {len(events)} événements trouvés")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    return events


def remove_duplicates(events):
    """Supprime les doublons par titre."""
    seen = set()
    unique = []
    for event in events:
        titre = event.get('titre', '').lower().strip()
        if titre and titre not in seen:
            seen.add(titre)
            unique.append(event)
    return unique


def add_to_concerts_db(events):
    """Ajoute les événements à la table concerts existante pour compatibilité."""
    from database import ConcertDatabase
    db = ConcertDatabase('concerts.db')
    
    concerts = [(e.get('url', ''), e.get('titre', '')) for e in events if e.get('url') and e.get('titre')]
    return db.add_concerts_batch(concerts)


def main():
    print("=" * 70)
    print("🎬 SCRAPING DES ÉVÉNEMENTS CINÉMA - PARIS - DÉCEMBRE 2025")
    print("=" * 70)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    db = EventDatabase('concerts.db')
    all_events = []
    
    # Scraper toutes les sources
    all_events.extend(scrape_allocine_films())
    time.sleep(1)
    
    all_events.extend(scrape_ugc())
    time.sleep(1)
    
    all_events.extend(scrape_pathe())
    time.sleep(1)
    
    all_events.extend(scrape_mk2())
    time.sleep(1)
    
    all_events.extend(scrape_grand_rex())
    time.sleep(1)
    
    all_events.extend(scrape_cinematheque())
    time.sleep(1)
    
    all_events.extend(scrape_louxor())
    time.sleep(1)
    
    all_events.extend(scrape_sortiraparis())
    
    # Supprimer les doublons
    unique_events = remove_duplicates(all_events)
    
    print("\n" + "=" * 70)
    print(f"📊 Total brut: {len(all_events)} événements")
    print(f"📊 Total unique: {len(unique_events)} événements")
    
    # Sauvegarder dans la base
    print("\n💾 Sauvegarde dans la base de données...")
    added = db.add_events_batch(unique_events)
    print(f"✅ {added} événements ajoutés à cinema_events")
    
    # Ajouter aussi à concerts pour compatibilité
    concerts_added = add_to_concerts_db(unique_events)
    print(f"✅ {concerts_added} événements ajoutés à concerts")
    
    # Stats finales
    print("\n" + "=" * 70)
    print("📊 STATISTIQUES FINALES")
    print("=" * 70)
    print(f"🎬 Événements cinéma: {db.count_events()}")
    
    # Afficher par source
    events = db.get_all_events()
    sources = {}
    for e in events:
        src = e[13] if len(e) > 13 else 'autre'
        sources[src] = sources.get(src, 0) + 1
    
    print("\n📌 Par source:")
    for src, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"   • {src}: {count}")
    
    # Exemples
    print("\n🎬 Exemples d'événements:")
    for e in events[:15]:
        titre = e[1][:50] + '...' if len(e[1]) > 50 else e[1]
        cinema = e[2] or 'Paris'
        print(f"   • [{cinema}] {titre}")
    
    print("\n✅ Scraping terminé!")
    return len(unique_events)


if __name__ == "__main__":
    main()


