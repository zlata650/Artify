#!/usr/bin/env python3
"""
Script pour scraper les affiches des cinémas de Paris.
Collecte les films à l'affiche depuis plusieurs sources.
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import time
import re
import warnings
from url_validator import clean_url, is_valid_event_url_pattern, is_allocine_event_url, validate_and_clean_events

warnings.filterwarnings('ignore')

# Liste complète des cinémas de Paris
PARIS_CINEMAS = {
    # Réseaux / Chaînes
    "reseaux": [
        # UGC
        {"nom": "UGC Ciné Cité Les Halles", "adresse": "7 place de la Rotonde, 75001 Paris", "type": "reseau"},
        {"nom": "UGC Ciné Cité Bercy", "adresse": "2 cour Saint-Émilion, 75012 Paris", "type": "reseau"},
        {"nom": "UGC Ciné Cité Paris 19", "adresse": "166 boulevard Macdonald, 75019 Paris", "type": "reseau"},
        {"nom": "UGC Danton", "adresse": "99 boulevard Saint-Germain, 75006 Paris", "type": "reseau"},
        {"nom": "UGC Gobelins", "adresse": "66 avenue des Gobelins, 75013 Paris", "type": "reseau"},
        {"nom": "UGC Odéon", "adresse": "124 boulevard Saint-Germain, 75006 Paris", "type": "reseau"},
        {"nom": "UGC Opéra", "adresse": "32 boulevard des Italiens, 75009 Paris", "type": "reseau"},
        {"nom": "UGC Normandie", "adresse": "116 avenue des Champs-Élysées, 75008 Paris", "type": "reseau"},
        {"nom": "UGC Rotonde", "adresse": "103 boulevard du Montparnasse, 75006 Paris", "type": "reseau"},
        {"nom": "UGC Montparnasse", "adresse": "83 boulevard du Montparnasse, 75006 Paris", "type": "reseau"},
        {"nom": "UGC Lyon Bastille", "adresse": "12 rue de Lyon, 75012 Paris", "type": "reseau"},
        {"nom": "UGC Maillot", "adresse": "15 avenue de la Grande Armée, 75016 Paris", "type": "reseau"},
        
        # Pathé / Gaumont
        {"nom": "Pathé Beaugrenelle", "adresse": "7 rue Linois, 75015 Paris", "type": "reseau"},
        {"nom": "Pathé Parnasse", "adresse": "67 boulevard du Montparnasse, 75006 Paris", "type": "reseau"},
        {"nom": "Pathé Wepler", "adresse": "140 boulevard de Clichy, 75018 Paris", "type": "reseau"},
        {"nom": "Pathé Convention", "adresse": "27 rue Alain Chartier, 75015 Paris", "type": "reseau"},
        {"nom": "Pathé Les Fauvettes", "adresse": "58 avenue des Gobelins, 75013 Paris", "type": "reseau"},
        {"nom": "Pathé Alésia", "adresse": "73 avenue du Général Leclerc, 75014 Paris", "type": "reseau"},
        {"nom": "Pathé La Villette", "adresse": "30 avenue Corentin Cariou, 75019 Paris", "type": "reseau"},
        {"nom": "Pathé Opéra Premier", "adresse": "2 rue Scribe, 75009 Paris", "type": "reseau"},
        {"nom": "Pathé Palace", "adresse": "2 rue Scribe, 75009 Paris", "type": "reseau"},
        {"nom": "Pathé Montparnos", "adresse": "31 rue du Départ, 75014 Paris", "type": "reseau"},
        {"nom": "Pathé Aquaboulevard", "adresse": "8 rue du Colonel Pierre Avia, 75015 Paris", "type": "reseau"},
        {"nom": "Pathé La Géode", "adresse": "26 avenue Corentin Cariou, 75019 Paris", "type": "reseau", "url": "https://www.pathe.fr/cinemas/cinema-la-geode"},
        
        # MK2
        {"nom": "MK2 Bibliothèque", "adresse": "128-162 avenue de France, 75013 Paris", "type": "reseau"},
        {"nom": "MK2 Bibliothèque x Centre Pompidou", "adresse": "128-162 avenue de France, 75013 Paris", "type": "reseau"},
        {"nom": "MK2 Beaubourg", "adresse": "50 rue Rambuteau, 75003 Paris", "type": "reseau"},
        {"nom": "MK2 Bastille (côté Beaumarchais)", "adresse": "4 boulevard Beaumarchais, 75011 Paris", "type": "reseau"},
        {"nom": "MK2 Bastille (côté Faubourg)", "adresse": "37 rue du Faubourg Saint-Antoine, 75011 Paris", "type": "reseau"},
        {"nom": "MK2 Nation", "adresse": "133 boulevard Diderot, 75012 Paris", "type": "reseau"},
        {"nom": "MK2 Parnasse", "adresse": "11 rue Jules Chaplain, 75006 Paris", "type": "reseau"},
        {"nom": "MK2 Gambetta", "adresse": "6 rue Belgrand, 75020 Paris", "type": "reseau"},
        {"nom": "MK2 Quai de Loire", "adresse": "7 quai de Loire, 75019 Paris", "type": "reseau"},
        {"nom": "MK2 Quai de Seine", "adresse": "14 quai de la Seine, 75019 Paris", "type": "reseau"},
        {"nom": "MK2 Odéon (côté Saint-Germain)", "adresse": "113 boulevard Saint-Germain, 75006 Paris", "type": "reseau"},
        {"nom": "MK2 Odéon (côté Saint-Michel)", "adresse": "7 rue Hautefeuille, 75006 Paris", "type": "reseau"},
        
        # CGR
        {"nom": "CGR Paris Lilas", "adresse": "71 rue de Paris, 93260 Les Lilas", "type": "reseau", "url": "https://www.cgrcinemas.fr"},
    ],
    
    # Cinémas indépendants et Art et Essai
    "independants": [
        # Grands indépendants
        {"nom": "Le Grand Rex", "adresse": "1 boulevard Poissonnière, 75002 Paris", "type": "independant", "url": "https://www.legrandrex.com"},
        {"nom": "Max Linder Panorama", "adresse": "24 boulevard Poissonnière, 75009 Paris", "type": "independant", "url": "https://www.maxlinder.com"},
        {"nom": "Le Publicis Cinémas", "adresse": "133 avenue des Champs-Élysées, 75008 Paris", "type": "independant"},
        
        # Centre / Historique
        {"nom": "Jeu de Paume", "adresse": "1 place de la Concorde, 75008 Paris", "type": "art_essai", "url": "https://www.jeudepaume.org"},
        {"nom": "Luminor Hôtel de Ville", "adresse": "20 rue du Temple, 75004 Paris", "type": "art_essai"},
        {"nom": "Le Latina", "adresse": "20 rue du Temple, 75004 Paris", "type": "art_essai"},
        
        # Quartier Latin (5e arrondissement)
        {"nom": "Le Champo", "adresse": "51 rue des Écoles, 75005 Paris", "type": "art_essai", "url": "https://www.lechampo.com"},
        {"nom": "Cinéma du Panthéon", "adresse": "13 rue Victor Cousin, 75005 Paris", "type": "art_essai"},
        {"nom": "Écoles Cinéma Club", "adresse": "23 rue des Écoles, 75005 Paris", "type": "art_essai"},
        {"nom": "Espace Saint-Michel", "adresse": "7 place Saint-Michel, 75005 Paris", "type": "art_essai"},
        {"nom": "Le Grand Action", "adresse": "5 rue des Écoles, 75005 Paris", "type": "art_essai"},
        {"nom": "La Filmothèque du Quartier Latin", "adresse": "9 rue Champollion, 75005 Paris", "type": "art_essai"},
        {"nom": "Le Desperado", "adresse": "23 rue des Écoles, 75005 Paris", "type": "art_essai"},
        {"nom": "L'Épée de Bois", "adresse": "100 rue Mouffetard, 75005 Paris", "type": "art_essai"},
        {"nom": "Le Reflet Médicis", "adresse": "3-5-7 rue Champollion, 75005 Paris", "type": "art_essai"},
        {"nom": "Studio des Ursulines", "adresse": "10 rue des Ursulines, 75005 Paris", "type": "art_essai"},
        {"nom": "Studio Galande", "adresse": "42 rue Galande, 75005 Paris", "type": "art_essai"},
        
        # 6e arrondissement
        {"nom": "Christine 21", "adresse": "4 rue Christine, 75006 Paris", "type": "art_essai"},
        {"nom": "Christine Cinéma Club", "adresse": "4 rue Christine, 75006 Paris", "type": "art_essai"},
        {"nom": "Action Christine", "adresse": "4 rue Christine, 75006 Paris", "type": "art_essai"},
        {"nom": "L'Arlequin", "adresse": "76 rue de Rennes, 75006 Paris", "type": "art_essai"},
        {"nom": "Les 3 Luxembourg", "adresse": "67 rue Monsieur-le-Prince, 75006 Paris", "type": "art_essai"},
        {"nom": "Le Lucernaire", "adresse": "53 rue Notre-Dame des Champs, 75006 Paris", "type": "art_essai"},
        {"nom": "Le Nouvel Odéon", "adresse": "6 rue de l'École de Médecine, 75006 Paris", "type": "art_essai"},
        {"nom": "Le Saint-André des Arts", "adresse": "30 rue Saint-André des Arts, 75006 Paris", "type": "art_essai"},
        {"nom": "Le Saint-Germain-des-Prés", "adresse": "22 rue Guillaume Apollinaire, 75006 Paris", "type": "art_essai"},
        {"nom": "Le Bretagne", "adresse": "73 boulevard du Montparnasse, 75006 Paris", "type": "art_essai"},
        
        # 8e-9e arrondissements
        {"nom": "Cinéma Katara", "adresse": "28 avenue des Champs-Élysées, 75008 Paris", "type": "art_essai"},
        {"nom": "Élysées Biarritz", "adresse": "22-24 rue Quentin Bauchart, 75008 Paris", "type": "art_essai"},
        {"nom": "Élysées Lincoln", "adresse": "27-29 rue Lincoln, 75008 Paris", "type": "art_essai"},
        {"nom": "Le Balzac", "adresse": "1 rue Balzac, 75008 Paris", "type": "art_essai"},
        {"nom": "Le Lincoln", "adresse": "2 rue Lincoln, 75008 Paris", "type": "art_essai"},
        {"nom": "Les 5 Caumartin", "adresse": "101 rue Saint-Lazare, 75009 Paris", "type": "art_essai"},
        
        # 10e-11e arrondissements
        {"nom": "Le Louxor - Palais du Cinéma", "adresse": "170 boulevard de Magenta, 75010 Paris", "type": "art_essai", "url": "https://www.cinemalouxor.fr"},
        {"nom": "L'Archipel", "adresse": "17 boulevard de Strasbourg, 75010 Paris", "type": "art_essai"},
        {"nom": "Le Brady", "adresse": "39 boulevard de Strasbourg, 75010 Paris", "type": "art_essai"},
        {"nom": "Le Majestic Bastille", "adresse": "2-4 boulevard Richard Lenoir, 75011 Paris", "type": "art_essai"},
        
        # 13e-15e arrondissements
        {"nom": "L'Escurial", "adresse": "11 boulevard de Port-Royal, 75013 Paris", "type": "art_essai"},
        {"nom": "Les 7 Parnassiens", "adresse": "98 boulevard du Montparnasse, 75014 Paris", "type": "art_essai"},
        {"nom": "Chaplin Denfert", "adresse": "24 place Denfert-Rochereau, 75014 Paris", "type": "art_essai"},
        {"nom": "L'Entrepôt", "adresse": "7-9 rue Francis de Pressensé, 75014 Paris", "type": "art_essai"},
        {"nom": "Chaplin Saint-Lambert", "adresse": "6 rue Péclet, 75015 Paris", "type": "art_essai"},
        
        # 16e-20e arrondissements
        {"nom": "Le Majestic Passy", "adresse": "18 rue de Passy, 75016 Paris", "type": "art_essai"},
        {"nom": "Le Mac Mahon", "adresse": "5 avenue Mac-Mahon, 75017 Paris", "type": "art_essai"},
        {"nom": "Les 7 Batignolles", "adresse": "12 rue des Batignolles, 75017 Paris", "type": "art_essai"},
        {"nom": "Cinéma des Cinéastes", "adresse": "7 avenue de Clichy, 75017 Paris", "type": "art_essai"},
        {"nom": "Club de l'Étoile", "adresse": "14 rue Troyon, 75017 Paris", "type": "art_essai"},
        {"nom": "Studio 28", "adresse": "10 rue Tholozé, 75018 Paris", "type": "art_essai"},
        {"nom": "L'Écran", "adresse": "14 passage de l'Atlas, 75019 Paris", "type": "art_essai"},
        
        # Cinémathèques et institutions
        {"nom": "La Géode", "adresse": "26 avenue Corentin Cariou, 75019 Paris", "type": "imax"},
        {"nom": "Forum des Images", "adresse": "2 rue du Cinéma, Forum des Halles, 75001 Paris", "type": "cinematheque"},
        {"nom": "Cinémathèque Française", "adresse": "51 rue de Bercy, 75012 Paris", "type": "cinematheque"},
        {"nom": "Fondation Jérôme Seydoux-Pathé", "adresse": "73 avenue des Gobelins, 75013 Paris", "type": "cinematheque"},
    ]
}

# Headers pour les requêtes
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
}


class CinemaDatabase:
    """Gère la base de données des films et séances de cinéma."""
    
    def __init__(self, db_path='concerts.db'):
        """Initialise la connexion à la base de données."""
        self.db_path = db_path
        self.conn = None
        self.create_tables()
    
    def connect(self):
        """Établit la connexion à la base de données."""
        self.conn = sqlite3.connect(self.db_path)
        return self.conn.cursor()
    
    def close(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Crée les tables pour les cinémas et films."""
        cursor = self.connect()
        
        # Table des cinémas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cinemas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                adresse TEXT,
                type TEXT,
                url TEXT,
                date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(nom, adresse)
            )
        ''')
        
        # Table des films à l'affiche
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS films (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                nom TEXT NOT NULL,
                cinema TEXT,
                date TEXT,
                horaire TEXT,
                source TEXT,
                date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        self.close()
    
    def add_cinema(self, nom, adresse, type_cinema, url=None):
        """Ajoute un cinéma à la base de données."""
        cursor = self.connect()
        try:
            cursor.execute(
                'INSERT OR IGNORE INTO cinemas (nom, adresse, type, url) VALUES (?, ?, ?, ?)',
                (nom, adresse, type_cinema, url)
            )
            self.conn.commit()
            self.close()
            return True
        except Exception as e:
            print(f"Erreur ajout cinéma: {e}")
            self.close()
            return False
    
    def add_film(self, url, nom, cinema=None, date=None, horaire=None, source=None):
        """Ajoute un film à la base de données."""
        cursor = self.connect()
        try:
            cursor.execute(
                'INSERT OR REPLACE INTO films (url, nom, cinema, date, horaire, source) VALUES (?, ?, ?, ?, ?, ?)',
                (url, nom, cinema, date, horaire, source)
            )
            self.conn.commit()
            self.close()
            return True
        except Exception as e:
            print(f"Erreur ajout film: {e}")
            self.close()
            return False
    
    def add_films_batch(self, films):
        """Ajoute plusieurs films en une seule transaction."""
        cursor = self.connect()
        added = 0
        for film in films:
            try:
                cursor.execute(
                    'INSERT OR REPLACE INTO films (url, nom, cinema, date, horaire, source) VALUES (?, ?, ?, ?, ?, ?)',
                    (film.get('url'), film.get('nom'), film.get('cinema'), 
                     film.get('date'), film.get('horaire'), film.get('source'))
                )
                added += 1
            except Exception as e:
                continue
        self.conn.commit()
        self.close()
        return added
    
    def get_all_cinemas(self):
        """Récupère tous les cinémas."""
        cursor = self.connect()
        cursor.execute('SELECT * FROM cinemas ORDER BY type, nom')
        cinemas = cursor.fetchall()
        self.close()
        return cinemas
    
    def get_all_films(self):
        """Récupère tous les films."""
        cursor = self.connect()
        cursor.execute('SELECT * FROM films ORDER BY date_ajout DESC')
        films = cursor.fetchall()
        self.close()
        return films
    
    def count_films(self):
        """Retourne le nombre total de films."""
        cursor = self.connect()
        cursor.execute('SELECT COUNT(*) FROM films')
        count = cursor.fetchone()[0]
        self.close()
        return count
    
    def count_cinemas(self):
        """Retourne le nombre total de cinémas."""
        cursor = self.connect()
        cursor.execute('SELECT COUNT(*) FROM cinemas')
        count = cursor.fetchone()[0]
        self.close()
        return count


def is_valid_film_title(text):
    """Vérifie si le texte ressemble à un titre de film valide."""
    if not text or len(text) < 3:
        return False
    
    # Exclure les textes qui ne sont clairement pas des titres de films
    exclude_patterns = [
        r'^©',  # Copyright
        r'^Campagne',
        r'^\d+x\d+',  # Dimensions
        r'^http',
        r'\.jpg$',
        r'\.png$',
        r'^Menu$',
        r'^Accueil$',
        r'^Voir plus$',
        r'^Lire la suite$',
        r'^En savoir plus$',
        r'^Fermer$',
        r'^Newsletter$',
        r'^Facebook$',
        r'^Twitter$',
        r'^Instagram$',
        r'^Partager$',
        r'^Connexion$',
        r'^S\'inscrire$',
        r'^Rechercher$',
        r'^Suivant$',
        r'^Précédent$',
    ]
    
    for pattern in exclude_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    
    # Le texte doit avoir au moins un mot d'une certaine longueur
    if not any(len(word) >= 3 for word in text.split()):
        return False
    
    return True


def clean_film_title(title):
    """Nettoie un titre de film."""
    if not title:
        return None
    
    # Supprimer les espaces multiples
    title = ' '.join(title.split())
    
    # Supprimer les caractères de début/fin
    title = title.strip('•·-–— ')
    
    # Limiter la longueur
    if len(title) > 150:
        title = title[:147] + "..."
    
    return title if title else None


def scrape_sortiraparis_cinema():
    """Scrape les événements cinéma depuis sortiraparis.com."""
    films = []
    base_url = "https://www.sortiraparis.com"
    
    # Pages spécifiques au cinéma
    cinema_urls = [
        f"{base_url}/loisirs/cinema/a-l-affiche.html",
        f"{base_url}/loisirs/cinema/",
        f"{base_url}/loisirs/cinema/les-films-de-la-semaine.html",
    ]
    
    for page_url in cinema_urls:
        try:
            print(f"  Scraping {page_url}...")
            response = requests.get(page_url, headers=HEADERS, timeout=30)
            
            if response.status_code != 200:
                print(f"    Erreur HTTP {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Rechercher les articles/liens de films
            # Rechercher dans les balises article, h2, h3
            for article in soup.find_all(['article', 'div'], class_=lambda x: x and ('article' in str(x).lower() or 'card' in str(x).lower() or 'item' in str(x).lower())):
                # Trouver le lien principal
                a = article.find('a', href=True)
                if a:
                    href = a.get('href', '')
                    
                    # Trouver le titre
                    title_tag = article.find(['h2', 'h3', 'h4']) or a
                    nom = title_tag.get_text(strip=True) if title_tag else None
                    
                    if not nom:
                        img = a.find('img')
                        if img:
                            nom = img.get('alt', '') or img.get('title', '')
                    
                    nom = clean_film_title(nom)
                    
                    if nom and is_valid_film_title(nom):
                        # Nettoyer et valider l'URL
                        cleaned_url = clean_url(href, base_url)
                        
                        if not cleaned_url:
                            continue
                        
                        # Vérifier que c'est une page d'événement (article individuel)
                        if not is_valid_event_url_pattern(cleaned_url):
                            continue
                        
                        # Doit contenir /articles/ avec un ID pour SortirAParis
                        if 'sortiraparis.com' in cleaned_url and '/articles/' not in cleaned_url:
                            continue
                        
                        films.append({
                            'url': cleaned_url,
                            'nom': nom,
                            'source': 'sortiraparis',
                            'cinema': None,
                            'date': None,
                            'horaire': None
                        })
            
            # Aussi rechercher les liens directs avec "film" ou "cinema" dans l'URL
            for a in soup.find_all('a', href=True):
                href = a.get('href', '')
                
                if any(kw in href.lower() for kw in ['/film/', '/cinema/', '/projection/']):
                    nom = a.get_text(strip=True)
                    nom = clean_film_title(nom)
                    
                    if nom and is_valid_film_title(nom) and len(nom) > 5:
                        # Nettoyer et valider l'URL
                        cleaned_url = clean_url(href, base_url)
                        
                        if not cleaned_url:
                            continue
                        
                        # Vérifier que c'est une page d'événement individuel
                        if not is_valid_event_url_pattern(cleaned_url):
                            continue
                        
                        # Doit contenir /articles/ avec un ID pour SortirAParis
                        if 'sortiraparis.com' in cleaned_url and '/articles/' not in cleaned_url:
                            continue
                        
                        films.append({
                            'url': cleaned_url,
                            'nom': nom,
                            'source': 'sortiraparis',
                            'cinema': None,
                            'date': None,
                            'horaire': None
                        })
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    Erreur: {e}")
    
    # Valider et nettoyer tous les événements
    films = validate_and_clean_events(films, base_url, verbose=False)
    
    return films


def scrape_allocine_films():
    """Scrape les films depuis allocine.fr."""
    films = []
    base_url = "https://www.allocine.fr"
    
    urls = [
        f"{base_url}/film/aucinema/",
    ]
    
    for page_url in urls:
        try:
            print(f"  Scraping {page_url}...")
            response = requests.get(page_url, headers=HEADERS, timeout=30)
            
            if response.status_code != 200:
                print(f"    Erreur HTTP {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Rechercher les liens de films (fiches individuelles)
            for a in soup.find_all('a', href=True):
                href = a.get('href', '')
                
                # Valider que c'est bien une fiche film individuelle
                if '/film/fichefilm_gen_cfilm=' in href:
                    nom = a.get_text(strip=True)
                    nom = clean_film_title(nom)
                    
                    if nom and is_valid_film_title(nom):
                        # Nettoyer et valider l'URL
                        cleaned_url = clean_url(href, base_url)
                        
                        if not cleaned_url:
                            continue
                        
                        # Vérifier que c'est une vraie fiche film AlloCiné
                        if not is_allocine_event_url(cleaned_url):
                            continue
                        
                        films.append({
                            'url': cleaned_url,
                            'nom': nom,
                            'source': 'allocine',
                            'cinema': None,
                            'date': None,
                            'horaire': None
                        })
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    Erreur: {e}")
    
    # Valider et nettoyer tous les événements
    films = validate_and_clean_events(films, base_url, verbose=False)
    
    return films


def scrape_premiere_films():
    """Scrape les films depuis premiere.fr."""
    films = []
    base_url = "https://www.premiere.fr"
    
    urls = [
        f"{base_url}/film/films-en-salles/",
        f"{base_url}/film/",
    ]
    
    for page_url in urls:
        try:
            print(f"  Scraping {page_url}...")
            response = requests.get(page_url, headers=HEADERS, timeout=30)
            
            if response.status_code != 200:
                print(f"    Erreur HTTP {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Rechercher les liens de films
            for a in soup.find_all('a', href=True):
                href = a.get('href', '')
                
                # Vérifier que c'est une fiche film (pas une catégorie)
                if '/film/' in href and href.count('/') >= 3:
                    nom = a.get_text(strip=True)
                    nom = clean_film_title(nom)
                    
                    if nom and is_valid_film_title(nom) and len(nom) > 3:
                        # Nettoyer et valider l'URL
                        cleaned_url = clean_url(href, base_url)
                        
                        if not cleaned_url:
                            continue
                        
                        # Vérifier que c'est une page d'événement individuel
                        if not is_valid_event_url_pattern(cleaned_url):
                            continue
                        
                        # Doit avoir un slug de film (pas juste /film/ ou /films/)
                        path_parts = cleaned_url.split('/')
                        film_idx = next((i for i, p in enumerate(path_parts) if 'film' in p.lower()), -1)
                        if film_idx == -1 or film_idx >= len(path_parts) - 1:
                            continue
                        
                        # Le slug après /film/ doit être substantiel
                        film_slug = path_parts[film_idx + 1] if film_idx + 1 < len(path_parts) else ''
                        if not film_slug or len(film_slug) < 3 or film_slug in ['films-en-salles', 'a-venir', 'tous']:
                            continue
                        
                        films.append({
                            'url': cleaned_url,
                            'nom': nom,
                            'source': 'premiere',
                            'cinema': None,
                            'date': None,
                            'horaire': None
                        })
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    Erreur: {e}")
    
    # Valider et nettoyer tous les événements
    films = validate_and_clean_events(films, base_url, verbose=False)
    
    return films


def scrape_telerama_films():
    """Scrape les films depuis telerama.fr."""
    films = []
    base_url = "https://www.telerama.fr"
    
    urls = [
        f"{base_url}/cinema/films-a-l-affiche",
    ]
    
    for page_url in urls:
        try:
            print(f"  Scraping {page_url}...")
            response = requests.get(page_url, headers=HEADERS, timeout=30)
            
            if response.status_code != 200:
                print(f"    Erreur HTTP {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Rechercher les liens de films (fiches individuelles)
            for a in soup.find_all('a', href=True):
                href = a.get('href', '')
                
                # Les fiches films de Telerama ont le format /cinema/films/slug-film
                if '/cinema/' in href and '/films/' in href:
                    nom = a.get_text(strip=True)
                    nom = clean_film_title(nom)
                    
                    if nom and is_valid_film_title(nom):
                        # Nettoyer et valider l'URL
                        cleaned_url = clean_url(href, base_url)
                        
                        if not cleaned_url:
                            continue
                        
                        # Vérifier que c'est une page d'événement individuel
                        if not is_valid_event_url_pattern(cleaned_url):
                            continue
                        
                        # Doit avoir un slug de film après /films/
                        if '/films/' in cleaned_url:
                            parts = cleaned_url.split('/films/')
                            if len(parts) < 2 or not parts[1] or parts[1] in ['', 'a-l-affiche', 'prochainement']:
                                continue
                        
                        films.append({
                            'url': cleaned_url,
                            'nom': nom,
                            'source': 'telerama',
                            'cinema': None,
                            'date': None,
                            'horaire': None
                        })
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    Erreur: {e}")
    
    # Valider et nettoyer tous les événements
    films = validate_and_clean_events(films, base_url, verbose=False)
    
    return films


def scrape_cinema_websites():
    """Scrape les affiches directement depuis les sites des cinémas."""
    films = []
    
    cinema_urls = [
        ("https://www.legrandrex.com/films", "Le Grand Rex"),
        ("https://www.cinemalouxor.fr/films/a-l-affiche/", "Le Louxor"),
        ("https://www.mk2.com/films", "MK2"),
    ]
    
    for base_url, cinema_name in cinema_urls:
        try:
            print(f"  Scraping {base_url}...")
            response = requests.get(base_url, headers=HEADERS, timeout=30)
            
            if response.status_code != 200:
                print(f"    Erreur HTTP {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Rechercher les liens vers les fiches films individuelles
            for elem in soup.find_all('a', href=True):
                href = elem.get('href', '')
                nom = elem.get_text(strip=True)
                
                # Si pas de texte, chercher un titre ou h2/h3 à l'intérieur
                if not nom:
                    title_elem = elem.find(['h2', 'h3', 'h4', 'span'])
                    if title_elem:
                        nom = title_elem.get_text(strip=True)
                
                nom = clean_film_title(nom)
                
                if nom and is_valid_film_title(nom) and len(nom) > 3:
                    # Nettoyer et valider l'URL
                    cleaned_url = clean_url(href, base_url)
                    
                    if not cleaned_url:
                        continue
                    
                    # Vérifier que c'est une page de film individuel
                    # (doit avoir un slug après /films/ ou /film/)
                    if '/films/' in cleaned_url or '/film/' in cleaned_url:
                        path = cleaned_url.split('/film')[-1]
                        # Doit avoir plus qu'un simple / ou /a-l-affiche
                        if path in ['/', '/s/', '/s', ''] or 'a-l-affiche' in path:
                            continue
                        
                        # Le slug doit être substantiel
                        slug = path.strip('/').split('/')[0] if path else ''
                        if not slug or len(slug) < 3:
                            continue
                    else:
                        # Pas un lien vers un film
                        continue
                    
                    films.append({
                        'url': cleaned_url,
                        'nom': nom,
                        'source': cinema_name.lower().replace(' ', '_'),
                        'cinema': cinema_name,
                        'date': None,
                        'horaire': None
                    })
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    Erreur: {e}")
    
    return films


def remove_duplicates(films):
    """Supprime les doublons basés sur l'URL et le nom."""
    seen_urls = set()
    seen_names = set()
    unique_films = []
    
    for film in films:
        url = film.get('url', '')
        nom = film.get('nom', '').lower().strip()
        
        # Nettoyer l'URL pour une meilleure déduplication
        cleaned_url = clean_url(url) if url else ''
        
        if not cleaned_url:
            continue
        
        # Vérifier les doublons par URL et par nom similaire
        if cleaned_url not in seen_urls and nom not in seen_names:
            seen_urls.add(cleaned_url)
            seen_names.add(nom)
            film['url'] = cleaned_url  # Mettre à jour avec l'URL nettoyée
            unique_films.append(film)
    
    return unique_films


def save_cinemas_to_db(db):
    """Enregistre tous les cinémas parisiens dans la base de données."""
    print("\n📽️  Enregistrement des cinémas de Paris...")
    
    count = 0
    for cinema in PARIS_CINEMAS["reseaux"]:
        if db.add_cinema(cinema["nom"], cinema["adresse"], cinema.get("type", "reseau"), cinema.get("url")):
            count += 1
    
    for cinema in PARIS_CINEMAS["independants"]:
        if db.add_cinema(cinema["nom"], cinema["adresse"], cinema.get("type", "independant"), cinema.get("url")):
            count += 1
    
    print(f"✅ {db.count_cinemas()} cinémas enregistrés")
    return count


def main():
    """Script principal pour scraper les affiches des cinémas de Paris."""
    print("=" * 60)
    print("🎬 SCRAPER CINÉMAS DE PARIS")
    print("=" * 60)
    
    # Initialiser la base de données
    db = CinemaDatabase('concerts.db')
    
    # 1. Enregistrer les cinémas
    save_cinemas_to_db(db)
    
    # 2. Scraper les films depuis différentes sources
    print("\n🔍 Recherche des films à l'affiche...")
    
    all_films = []
    
    # SortiraParis
    print("\n📌 Source: SortiraParis")
    films_sortiraparis = scrape_sortiraparis_cinema()
    all_films.extend(films_sortiraparis)
    print(f"   → {len(films_sortiraparis)} liens trouvés")
    
    # AlloCiné
    print("\n📌 Source: AlloCiné")
    films_allocine = scrape_allocine_films()
    all_films.extend(films_allocine)
    print(f"   → {len(films_allocine)} liens trouvés")
    
    # Première
    print("\n📌 Source: Première")
    films_premiere = scrape_premiere_films()
    all_films.extend(films_premiere)
    print(f"   → {len(films_premiere)} liens trouvés")
    
    # Télérama
    print("\n📌 Source: Télérama")
    films_telerama = scrape_telerama_films()
    all_films.extend(films_telerama)
    print(f"   → {len(films_telerama)} liens trouvés")
    
    # Sites de cinémas
    print("\n📌 Source: Sites de cinémas")
    films_cinemas = scrape_cinema_websites()
    all_films.extend(films_cinemas)
    print(f"   → {len(films_cinemas)} liens trouvés")
    
    # Supprimer les doublons
    unique_films = remove_duplicates(all_films)
    print(f"\n📊 Total unique: {len(unique_films)} événements cinéma")
    
    # Sauvegarder dans la base de données
    print("\n💾 Sauvegarde dans la base de données...")
    added = db.add_films_batch(unique_films)
    print(f"✅ {added} nouveaux films ajoutés à la table films")
    
    # Ajouter aussi à la table concerts pour compatibilité avec l'application existante
    from database import ConcertDatabase
    concert_db = ConcertDatabase('concerts.db')
    
    concerts_to_add = [(f['url'], f['nom']) for f in unique_films if f['url'] and f['nom']]
    concerts_added = concert_db.add_concerts_batch(concerts_to_add)
    print(f"✅ {concerts_added} événements ajoutés à la table concerts")
    
    # Afficher les statistiques
    print("\n" + "=" * 60)
    print("📊 STATISTIQUES FINALES")
    print("=" * 60)
    print(f"🎬 Cinémas de Paris: {db.count_cinemas()}")
    print(f"🎞️  Films dans la base: {db.count_films()}")
    print(f"🎵 Total concerts/événements: {concert_db.count_concerts()}")
    
    # Afficher quelques exemples
    print("\n🎬 Exemples d'événements cinéma enregistrés:")
    films = db.get_all_films()
    for film in films[:15]:
        title = film[2]
        source = film[6] if len(film) > 6 else "?"
        display = f"{title[:55]}..." if len(title) > 55 else title
        print(f"  • [{source}] {display}")
    
    # Afficher les cinémas par type
    print("\n🏛️  Cinémas par type:")
    cinemas = db.get_all_cinemas()
    types_count = {}
    for cinema in cinemas:
        t = cinema[3] if len(cinema) > 3 else "autre"
        types_count[t] = types_count.get(t, 0) + 1
    
    for t, count in sorted(types_count.items()):
        print(f"  • {t}: {count}")
    
    print("\n✅ Scraping terminé!")
    return len(unique_films)


if __name__ == "__main__":
    main()
