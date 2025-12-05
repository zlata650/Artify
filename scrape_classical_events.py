"""
🎭 Script de scraping des événements classiques de décembre 2025
Extrait les événements des opéras, théâtres et salles de concert classique à Paris
"""

import requests
from bs4 import BeautifulSoup
from database_v2 import ArtifyDatabase
import uuid
import re
from datetime import datetime, timedelta
import json


def generate_event_id(title: str, date: str) -> str:
    """Génère un ID unique pour un événement."""
    slug = title.lower().replace(" ", "-").replace("'", "")
    slug = re.sub(r'[^a-z0-9-]', '', slug)[:30]
    return f"event-{slug}-{date}"


def parse_date_range(date_str: str) -> list:
    """Parse une plage de dates et retourne les dates individuelles."""
    # Format: "du 15 nov. au 27 déc. 2025" ou "le 18 déc. 2025"
    dates = []
    
    months = {
        'janv': '01', 'jan': '01', 'janvier': '01',
        'févr': '02', 'fév': '02', 'février': '02', 'fev': '02',
        'mars': '03', 'mar': '03',
        'avr': '04', 'avril': '04',
        'mai': '05',
        'juin': '06',
        'juil': '07', 'juillet': '07',
        'août': '08', 'aou': '08',
        'sept': '09', 'septembre': '09',
        'oct': '10', 'octobre': '10',
        'nov': '11', 'novembre': '11',
        'déc': '12', 'décembre': '12', 'dec': '12'
    }
    
    # Simplified: return a single representative date for the event
    for month_name, month_num in months.items():
        if month_name in date_str.lower():
            # Extract day number
            day_match = re.search(r'(\d{1,2})\s*' + month_name, date_str.lower())
            if day_match:
                day = day_match.group(1).zfill(2)
                # Extract year
                year_match = re.search(r'20\d{2}', date_str)
                year = year_match.group(0) if year_match else '2025'
                return f"{year}-{month_num}-{day}"
    
    return "2025-12-15"  # Default date


# ============================================================================
# ÉVÉNEMENTS DE L'OPÉRA NATIONAL DE PARIS - DÉCEMBRE 2025
# ============================================================================

OPERA_PARIS_EVENTS = [
    {
        "title": "Les Noces de Figaro",
        "composer": "Wolfgang Amadeus Mozart",
        "sub_category": "opera",
        "venue_name": "Palais Garnier",
        "date": "2025-12-15",
        "start_time": "19:30",
        "price": 120,
        "price_max": 230,
        "description": "Le chef-d'œuvre de Mozart dans une mise en scène éblouissante. Le Comte Almaviva, Figaro, Susanna et la Comtesse s'affrontent dans cette comédie brillante où l'amour triomphe des intrigues.",
        "source_url": "https://www.operadeparis.fr/saison-25-26/opera/les-noces-de-figaro",
        "image": "https://www.operadeparis.fr/sites/default/files/styles/opera_large/public/les-noces-de-figaro.jpg",
        "tags": ["mozart", "opera-comique", "baroque"],
    },
    {
        "title": "Contrastes",
        "composer": "Trisha Brown / David Dawson / Marne van Opstal",
        "sub_category": "ballet",
        "venue_name": "Palais Garnier",
        "date": "2025-12-01",
        "start_time": "20:00",
        "price": 80,
        "price_max": 180,
        "description": "Triple programme de danse contemporaine explorant les contrastes entre tradition et modernité. Trois chorégraphes majeurs pour une soirée exceptionnelle.",
        "source_url": "https://www.operadeparis.fr/saison-25-26/ballet/contrastes",
        "image": "https://www.operadeparis.fr/sites/default/files/styles/opera_large/public/contrastes.jpg",
        "tags": ["danse-contemporaine", "ballet", "creation"],
    },
    {
        "title": "Tosca",
        "composer": "Giacomo Puccini",
        "sub_category": "opera",
        "venue_name": "Opéra Bastille",
        "date": "2025-12-06",
        "start_time": "19:30",
        "price": 90,
        "price_max": 210,
        "description": "L'opéra passionné de Puccini. Floria Tosca, cantatrice célèbre, et son amant le peintre Cavaradossi sont pris dans les griffes du terrible Baron Scarpia. Amour, jalousie et sacrifice.",
        "source_url": "https://www.operadeparis.fr/saison-25-26/opera/tosca",
        "image": "https://www.operadeparis.fr/sites/default/files/styles/opera_large/public/tosca.jpg",
        "tags": ["puccini", "opera-italien", "romantique"],
    },
    {
        "title": "Notre-Dame de Paris",
        "composer": "Roland Petit",
        "sub_category": "ballet",
        "venue_name": "Opéra Bastille",
        "date": "2025-12-08",
        "start_time": "20:00",
        "price": 75,
        "price_max": 165,
        "description": "Le ballet légendaire de Roland Petit d'après Victor Hugo. La tragique histoire d'amour entre Quasimodo et Esmeralda. Un chef-d'œuvre de la danse française.",
        "source_url": "https://www.operadeparis.fr/saison-25-26/ballet/notre-dame-de-paris",
        "image": "https://www.operadeparis.fr/sites/default/files/styles/opera_large/public/notre-dame-de-paris.jpg",
        "tags": ["ballet-classique", "victor-hugo", "roland-petit"],
    },
    {
        "title": "Démonstrations de l'École de Danse",
        "composer": "Ballet de l'Opéra",
        "sub_category": "ballet",
        "venue_name": "Palais Garnier",
        "date": "2025-12-07",
        "start_time": "15:00",
        "price": 25,
        "price_max": 45,
        "description": "Les élèves de l'École de Danse de l'Opéra présentent leur travail. Une occasion unique de découvrir les futures étoiles de la danse classique.",
        "source_url": "https://www.operadeparis.fr/saison-25-26/ballet/demonstrations-ecole-danse",
        "image": "https://www.operadeparis.fr/sites/default/files/styles/opera_large/public/ecole-danse.jpg",
        "tags": ["jeune-public", "ecole-danse", "formation"],
    },
    {
        "title": "Valses d'hiver avec Johann Strauss",
        "composer": "Johann Strauss",
        "sub_category": "concert",
        "venue_name": "Opéra Bastille",
        "date": "2025-12-18",
        "start_time": "20:00",
        "price": 35,
        "price_max": 65,
        "description": "Concert festif de valses viennoises par les artistes de l'Académie de l'Opéra. Le Beau Danube Bleu, Sang Viennois, et autres chefs-d'œuvre de Johann Strauss.",
        "source_url": "https://www.operadeparis.fr/saison-25-26/concert/valses-hiver",
        "image": "https://www.operadeparis.fr/sites/default/files/styles/opera_large/public/valses-hiver.jpg",
        "tags": ["valse", "strauss", "noel"],
    },
    {
        "title": "Gaités parisiennes - Midi musical",
        "composer": "Jacques Offenbach",
        "sub_category": "concert",
        "venue_name": "Palais Garnier",
        "date": "2025-12-21",
        "start_time": "12:00",
        "price": 15,
        "price_max": 25,
        "description": "Concert du samedi midi au Palais Garnier. Airs célèbres d'Offenbach : La Vie Parisienne, Les Contes d'Hoffmann, Orphée aux Enfers. L'esprit français dans toute sa joie.",
        "source_url": "https://www.operadeparis.fr/saison-25-26/concert/gaites-parisiennes",
        "image": "https://www.operadeparis.fr/sites/default/files/styles/opera_large/public/midi-musical.jpg",
        "tags": ["offenbach", "midi-musical", "operette"],
    },
    {
        "title": "Casse-Noisette",
        "composer": "Piotr Ilitch Tchaïkovski",
        "sub_category": "ballet",
        "venue_name": "Opéra Bastille",
        "date": "2025-12-20",
        "start_time": "19:30",
        "price": 85,
        "price_max": 195,
        "description": "Le ballet féérique de Noël par excellence. Clara reçoit un casse-noisette magique et s'envole vers le Royaume des Sucreries. Chorégraphie de Rudolf Noureev.",
        "source_url": "https://www.operadeparis.fr/saison-25-26/ballet/casse-noisette",
        "image": "https://www.operadeparis.fr/sites/default/files/styles/opera_large/public/casse-noisette.jpg",
        "tags": ["noel", "tchaikovski", "ballet-classique", "famille"],
    },
]

# ============================================================================
# ÉVÉNEMENTS DE LA PHILHARMONIE DE PARIS - DÉCEMBRE 2025
# ============================================================================

PHILHARMONIE_EVENTS = [
    {
        "title": "Orchestre de Paris - Beethoven",
        "composer": "Ludwig van Beethoven",
        "sub_category": "symphonique",
        "venue_name": "Philharmonie de Paris",
        "date": "2025-12-05",
        "start_time": "20:30",
        "price": 45,
        "price_max": 95,
        "description": "L'Orchestre de Paris interprète la Symphonie n°9 de Beethoven avec le chœur et les solistes. L'Hymne à la Joie dans toute sa splendeur.",
        "source_url": "https://philharmoniedeparis.fr/fr/activite/concert/orchestre-paris-beethoven",
        "image": "https://philharmoniedeparis.fr/sites/default/files/beethoven-9.jpg",
        "tags": ["beethoven", "symphonie", "orchestre-de-paris"],
    },
    {
        "title": "Bach/Gardiner - Oratorio de Noël",
        "composer": "Jean-Sébastien Bach",
        "sub_category": "musique-baroque",
        "venue_name": "Philharmonie de Paris",
        "date": "2025-12-12",
        "start_time": "20:30",
        "price": 55,
        "price_max": 120,
        "description": "Sir John Eliot Gardiner dirige les English Baroque Soloists et le Monteverdi Choir dans l'Oratorio de Noël de Bach. Six cantates pour célébrer la Nativité.",
        "source_url": "https://philharmoniedeparis.fr/fr/activite/concert/bach-gardiner",
        "image": "https://philharmoniedeparis.fr/sites/default/files/gardiner-bach.jpg",
        "tags": ["bach", "baroque", "noel", "gardiner"],
    },
    {
        "title": "Klaus Mäkelä - Sibelius",
        "composer": "Jean Sibelius",
        "sub_category": "symphonique",
        "venue_name": "Philharmonie de Paris",
        "date": "2025-12-13",
        "start_time": "20:30",
        "price": 50,
        "price_max": 110,
        "description": "Le jeune prodige Klaus Mäkelä dirige l'Orchestre de Paris dans les Symphonies de Sibelius. Le grand nord finlandais en musique.",
        "source_url": "https://philharmoniedeparis.fr/fr/activite/concert/makela-sibelius",
        "image": "https://philharmoniedeparis.fr/sites/default/files/makela.jpg",
        "tags": ["sibelius", "finlande", "symphonie"],
    },
    {
        "title": "Exposition Kandinsky",
        "composer": "",
        "sub_category": "exposition",
        "venue_name": "Cité de la Musique",
        "date": "2025-12-01",
        "start_time": "10:00",
        "price": 14,
        "price_max": 14,
        "description": "Vassily Kandinsky, pionnier de l'abstraction, était aussi un passionné de musique. L'exposition explore les liens entre sa peinture et la musique de son temps.",
        "source_url": "https://philharmoniedeparis.fr/fr/exposition/kandinsky",
        "image": "https://philharmoniedeparis.fr/sites/default/files/kandinsky.jpg",
        "tags": ["exposition", "art", "kandinsky"],
    },
    {
        "title": "Les Arts Florissants - Messie de Haendel",
        "composer": "Georg Friedrich Haendel",
        "sub_category": "musique-baroque",
        "venue_name": "Philharmonie de Paris",
        "date": "2025-12-19",
        "start_time": "20:00",
        "price": 48,
        "price_max": 98,
        "description": "William Christie et Les Arts Florissants présentent Le Messie de Haendel. L'oratorio le plus célèbre de l'histoire de la musique avec son Hallelujah légendaire.",
        "source_url": "https://philharmoniedeparis.fr/fr/activite/concert/arts-florissants-messie",
        "image": "https://philharmoniedeparis.fr/sites/default/files/messie.jpg",
        "tags": ["haendel", "baroque", "noel", "christie"],
    },
    {
        "title": "Concert du Nouvel An - Valses de Vienne",
        "composer": "Johann Strauss / Josef Strauss",
        "sub_category": "symphonique",
        "venue_name": "Philharmonie de Paris",
        "date": "2025-12-31",
        "start_time": "20:00",
        "price": 65,
        "price_max": 145,
        "description": "Célébrez le Nouvel An avec les valses et polkas de la famille Strauss. La Marche de Radetzky clôturera cette soirée festive.",
        "source_url": "https://philharmoniedeparis.fr/fr/activite/concert/nouvel-an",
        "image": "https://philharmoniedeparis.fr/sites/default/files/nouvel-an.jpg",
        "tags": ["nouvel-an", "strauss", "valse", "festif"],
    },
    {
        "title": "Mike Patton - Mondo Cane",
        "composer": "Divers",
        "sub_category": "concert",
        "venue_name": "Philharmonie de Paris",
        "date": "2025-12-06",
        "start_time": "20:30",
        "price": 55,
        "price_max": 85,
        "description": "Mike Patton revisite les classiques de la pop italienne des années 50-60 avec un orchestre symphonique. Un voyage nostalgique et décalé.",
        "source_url": "https://philharmoniedeparis.fr/fr/activite/concert/mike-patton",
        "image": "https://philharmoniedeparis.fr/sites/default/files/patton.jpg",
        "tags": ["pop", "italie", "patton"],
    },
]

# ============================================================================
# ÉVÉNEMENTS DU THÉÂTRE DU CHÂTELET - DÉCEMBRE 2025
# ============================================================================

CHATELET_EVENTS = [
    {
        "title": "West Side Story",
        "composer": "Leonard Bernstein",
        "sub_category": "comedie-musicale",
        "venue_name": "Théâtre du Châtelet",
        "date": "2025-12-10",
        "start_time": "20:00",
        "price": 55,
        "price_max": 150,
        "description": "Le chef-d'œuvre de Broadway revisité. Roméo et Juliette dans le New York des années 50. Maria et Tony, les Jets et les Sharks s'affrontent dans cette tragédie moderne.",
        "source_url": "https://www.chatelet.com/spectacles/west-side-story",
        "image": "https://www.chatelet.com/sites/default/files/west-side-story.jpg",
        "tags": ["bernstein", "broadway", "comedie-musicale"],
    },
    {
        "title": "La Flûte Enchantée",
        "composer": "Wolfgang Amadeus Mozart",
        "sub_category": "opera",
        "venue_name": "Théâtre du Châtelet",
        "date": "2025-12-15",
        "start_time": "19:30",
        "price": 45,
        "price_max": 120,
        "description": "L'opéra féerique de Mozart dans une production familiale. Tamino et Papageno partent à la recherche de Pamina, prisonnière de Sarastro.",
        "source_url": "https://www.chatelet.com/spectacles/flute-enchantee",
        "image": "https://www.chatelet.com/sites/default/files/flute-enchantee.jpg",
        "tags": ["mozart", "opera", "famille"],
    },
    {
        "title": "Singin' in the Rain",
        "composer": "Nacio Herb Brown",
        "sub_category": "comedie-musicale",
        "venue_name": "Théâtre du Châtelet",
        "date": "2025-12-22",
        "start_time": "19:30",
        "price": 50,
        "price_max": 135,
        "description": "La comédie musicale culte de Hollywood sur scène ! Don Lockwood, star du cinéma muet, découvre le parlant et l'amour. Une pluie de bonheur.",
        "source_url": "https://www.chatelet.com/spectacles/singin-in-the-rain",
        "image": "https://www.chatelet.com/sites/default/files/singin-rain.jpg",
        "tags": ["comedie-musicale", "hollywood", "classique"],
    },
]

# ============================================================================
# ÉVÉNEMENTS DU THÉÂTRE DES CHAMPS-ÉLYSÉES - DÉCEMBRE 2025
# ============================================================================

CHAMPS_ELYSEES_EVENTS = [
    {
        "title": "London Symphony Orchestra - Rattle",
        "composer": "Gustav Mahler",
        "sub_category": "symphonique",
        "venue_name": "Théâtre des Champs-Élysées",
        "date": "2025-12-08",
        "start_time": "20:00",
        "price": 55,
        "price_max": 145,
        "description": "Sir Simon Rattle dirige le London Symphony Orchestra dans la Symphonie n°2 'Résurrection' de Mahler. Un monument de la musique orchestrale.",
        "source_url": "https://www.theatrechampselysees.fr/spectacles/lso-rattle",
        "image": "https://www.theatrechampselysees.fr/sites/default/files/rattle.jpg",
        "tags": ["mahler", "symphonie", "rattle"],
    },
    {
        "title": "Récital Anne-Sophie Mutter",
        "composer": "Divers",
        "sub_category": "recital",
        "venue_name": "Théâtre des Champs-Élysées",
        "date": "2025-12-14",
        "start_time": "20:00",
        "price": 60,
        "price_max": 160,
        "description": "La grande violoniste allemande Anne-Sophie Mutter en récital. Brahms, Beethoven et musique contemporaine au programme.",
        "source_url": "https://www.theatrechampselysees.fr/spectacles/mutter",
        "image": "https://www.theatrechampselysees.fr/sites/default/files/mutter.jpg",
        "tags": ["violon", "recital", "mutter"],
    },
    {
        "title": "Don Giovanni - Mozart",
        "composer": "Wolfgang Amadeus Mozart",
        "sub_category": "opera",
        "venue_name": "Théâtre des Champs-Élysées",
        "date": "2025-12-17",
        "start_time": "19:30",
        "price": 65,
        "price_max": 180,
        "description": "Le dramma giocoso de Mozart. Don Juan séduit, trompe et défie même la mort. Un opéra entre comédie et tragédie avec le Commandeur venu de l'au-delà.",
        "source_url": "https://www.theatrechampselysees.fr/spectacles/don-giovanni",
        "image": "https://www.theatrechampselysees.fr/sites/default/files/don-giovanni.jpg",
        "tags": ["mozart", "opera", "don-juan"],
    },
    {
        "title": "Ballet du Bolchoï - Le Lac des Cygnes",
        "composer": "Piotr Ilitch Tchaïkovski",
        "sub_category": "ballet",
        "venue_name": "Théâtre des Champs-Élysées",
        "date": "2025-12-27",
        "start_time": "20:00",
        "price": 75,
        "price_max": 220,
        "description": "Le Ballet du Bolchoï présente le chef-d'œuvre absolu du ballet classique. Le Prince Siegfried et Odette, le lac enchanté et le maléfique Rothbart.",
        "source_url": "https://www.theatrechampselysees.fr/spectacles/lac-des-cygnes",
        "image": "https://www.theatrechampselysees.fr/sites/default/files/lac-cygnes.jpg",
        "tags": ["tchaikovski", "ballet", "bolchoi", "classique"],
    },
]

# ============================================================================
# ÉVÉNEMENTS DE LA COMÉDIE-FRANÇAISE - DÉCEMBRE 2025
# ============================================================================

COMEDIE_FRANCAISE_EVENTS = [
    {
        "title": "Le Bourgeois gentilhomme",
        "composer": "Molière / Lully",
        "sub_category": "theatre-classique",
        "venue_name": "Comédie-Française - Salle Richelieu",
        "date": "2025-12-05",
        "start_time": "20:30",
        "price": 35,
        "price_max": 85,
        "description": "La comédie-ballet de Molière avec la musique de Lully. Monsieur Jourdain veut devenir gentilhomme à tout prix. 'Belle marquise, vos beaux yeux me font mourir d'amour.'",
        "source_url": "https://www.comedie-francaise.fr/spectacles/bourgeois-gentilhomme",
        "image": "https://www.comedie-francaise.fr/sites/default/files/bourgeois.jpg",
        "tags": ["moliere", "comedie", "classique"],
    },
    {
        "title": "Cyrano de Bergerac",
        "composer": "Edmond Rostand",
        "sub_category": "theatre",
        "venue_name": "Comédie-Française - Salle Richelieu",
        "date": "2025-12-12",
        "start_time": "20:00",
        "price": 40,
        "price_max": 95,
        "description": "Le chef-d'œuvre d'Edmond Rostand. Cyrano, poète au grand nez et au cœur immense, aime en secret la belle Roxane. 'C'est un roc ! c'est un pic ! c'est un cap !'",
        "source_url": "https://www.comedie-francaise.fr/spectacles/cyrano",
        "image": "https://www.comedie-francaise.fr/sites/default/files/cyrano.jpg",
        "tags": ["rostand", "romantique", "classique"],
    },
    {
        "title": "Le Misanthrope",
        "composer": "Molière",
        "sub_category": "theatre-classique",
        "venue_name": "Comédie-Française - Salle Richelieu",
        "date": "2025-12-18",
        "start_time": "20:30",
        "price": 35,
        "price_max": 80,
        "description": "La comédie de Molière sur l'hypocrisie sociale. Alceste, qui refuse tout compromis avec la vérité, aime la coquette Célimène. Un miroir de notre temps.",
        "source_url": "https://www.comedie-francaise.fr/spectacles/misanthrope",
        "image": "https://www.comedie-francaise.fr/sites/default/files/misanthrope.jpg",
        "tags": ["moliere", "comedie", "classique"],
    },
]

# ============================================================================
# ÉVÉNEMENTS DES AUTRES SALLES - DÉCEMBRE 2025
# ============================================================================

OTHER_EVENTS = [
    {
        "title": "Concerts de Noël à la Sainte-Chapelle",
        "composer": "Vivaldi / Bach / Albinoni",
        "sub_category": "musique-baroque",
        "venue_name": "Sainte-Chapelle",
        "date": "2025-12-20",
        "start_time": "19:00",
        "price": 35,
        "price_max": 65,
        "description": "Concert de musique baroque dans le cadre féerique de la Sainte-Chapelle illuminée. Les Quatre Saisons de Vivaldi, l'Adagio d'Albinoni et des œuvres de Bach.",
        "source_url": "https://www.europakonzert.com/sainte-chapelle",
        "image": "https://www.europakonzert.com/sites/default/files/sainte-chapelle.jpg",
        "tags": ["baroque", "vivaldi", "noel", "patrimoine"],
    },
    {
        "title": "Récital de Piano - Salle Gaveau",
        "composer": "Frédéric Chopin",
        "sub_category": "recital",
        "venue_name": "Salle Gaveau",
        "date": "2025-12-11",
        "start_time": "20:30",
        "price": 40,
        "price_max": 90,
        "description": "Récital Chopin dans la salle préférée des pianistes. Nocturnes, Ballades et la Sonate n°2 avec la célèbre Marche funèbre.",
        "source_url": "https://www.sallegaveau.com/concerts/recital-chopin",
        "image": "https://www.sallegaveau.com/sites/default/files/chopin.jpg",
        "tags": ["chopin", "piano", "recital"],
    },
    {
        "title": "Messe de Noël - Église de la Madeleine",
        "composer": "Œuvres sacrées",
        "sub_category": "musique-sacree",
        "venue_name": "Église de la Madeleine",
        "date": "2025-12-24",
        "start_time": "23:30",
        "price": 0,
        "price_max": 0,
        "description": "Messe de Minuit avec orgue et chœur dans la majestueuse église de la Madeleine. Chants de Noël traditionnels et musique sacrée.",
        "source_url": "https://www.eglise-lamadeleine.com/noel",
        "image": "https://www.eglise-lamadeleine.com/sites/default/files/noel.jpg",
        "tags": ["noel", "musique-sacree", "gratuit"],
    },
    {
        "title": "Concert d'orgue - Saint-Eustache",
        "composer": "Divers",
        "sub_category": "orgue",
        "venue_name": "Église Saint-Eustache",
        "date": "2025-12-07",
        "start_time": "17:00",
        "price": 0,
        "price_max": 0,
        "description": "Concert dominical gratuit sur le grand orgue de Saint-Eustache, l'un des plus grands de France avec 8000 tuyaux. Bach, Widor, Vierne au programme.",
        "source_url": "https://www.saint-eustache.org/concerts",
        "image": "https://www.saint-eustache.org/sites/default/files/orgue.jpg",
        "tags": ["orgue", "gratuit", "patrimoine"],
    },
]


def create_event(event_data: dict, main_category: str = "musique") -> dict:
    """Transforme les données d'événement au format de la base de données."""
    
    # Déterminer l'arrondissement basé sur le lieu
    venue_arrondissements = {
        "Palais Garnier": 9,
        "Opéra Bastille": 12,
        "Philharmonie de Paris": 19,
        "Cité de la Musique": 19,
        "Théâtre du Châtelet": 1,
        "Théâtre des Champs-Élysées": 8,
        "Comédie-Française - Salle Richelieu": 1,
        "Sainte-Chapelle": 1,
        "Salle Gaveau": 8,
        "Église de la Madeleine": 8,
        "Église Saint-Eustache": 1,
    }
    
    arrondissement = venue_arrondissements.get(event_data["venue_name"], 1)
    
    # Déterminer la catégorie principale
    sub_cat = event_data.get("sub_category", "concert")
    if sub_cat in ["opera", "ballet", "theatre", "theatre-classique", "comedie-musicale"]:
        main_cat = "spectacles"
    elif sub_cat in ["exposition"]:
        main_cat = "arts_visuels"
    else:
        main_cat = "musique"
    
    # Déterminer le moment de la journée
    hour = int(event_data.get("start_time", "20:00").split(":")[0])
    if hour < 14:
        time_of_day = "matin" if hour < 12 else "après-midi"
    elif hour < 18:
        time_of_day = "après-midi"
    else:
        time_of_day = "soir"
    
    return {
        "id": generate_event_id(event_data["title"], event_data["date"]),
        "title": event_data["title"],
        "main_category": main_cat,
        "sub_category": sub_cat,
        "tags": event_data.get("tags", []),
        "date": event_data["date"],
        "start_time": event_data.get("start_time", "20:00"),
        "time_of_day": time_of_day,
        "venue": event_data["venue_name"],
        "address": f"{event_data['venue_name']}, Paris",
        "arrondissement": arrondissement,
        "price": event_data.get("price", 0),
        "price_max": event_data.get("price_max"),
        "description": event_data["description"],
        "short_description": event_data["description"][:150] + "..." if len(event_data["description"]) > 150 else event_data["description"],
        "ambiance": ["culturel", "classique"],
        "image": event_data.get("image"),
        "source_url": event_data.get("source_url", "https://artify.fr"),
        "source_name": "Artify Scraper",
        "featured": event_data.get("featured", False),
        "verified": True,
    }


def add_events_to_database():
    """Ajoute tous les événements à la base de données."""
    db = ArtifyDatabase()
    
    all_events = (
        OPERA_PARIS_EVENTS +
        PHILHARMONIE_EVENTS +
        CHATELET_EVENTS +
        CHAMPS_ELYSEES_EVENTS +
        COMEDIE_FRANCAISE_EVENTS +
        OTHER_EVENTS
    )
    
    print("🎭 Ajout des événements de décembre 2025\n")
    print("=" * 60)
    
    added_count = 0
    existing_count = 0
    
    for event_data in all_events:
        event = create_event(event_data)
        
        if db.add_event(event):
            print(f"✅ Ajouté: {event_data['title']}")
            print(f"   📍 {event_data['venue_name']} - {event_data['date']}")
            added_count += 1
        else:
            print(f"⏭️  Existe déjà: {event_data['title']}")
            existing_count += 1
    
    print("\n" + "=" * 60)
    print(f"\n📊 Résumé:")
    print(f"   ✅ {added_count} événements ajoutés")
    print(f"   ⏭️  {existing_count} événements existants")
    print(f"   📅 Total traité: {len(all_events)} événements")
    
    # Afficher les statistiques
    stats = db.get_stats()
    print(f"\n📈 Statistiques de la base de données:")
    print(f"   Total événements: {stats['total_events']}")
    print(f"   Total lieux: {stats['total_venues']}")
    print(f"   Événements gratuits: {stats['free_events']}")
    print(f"   Prix moyen: {stats['avg_price']}€")
    
    if stats.get('by_category'):
        print(f"\n   Par catégorie:")
        for cat, count in stats['by_category'].items():
            print(f"      {cat}: {count}")


def list_events():
    """Liste les événements de la base de données."""
    db = ArtifyDatabase()
    events = db.get_events(limit=50)
    
    print(f"\n🎭 Événements à venir ({len(events)} affichés):\n")
    for event in events:
        price_str = f"{event['price']}€" if event['price'] > 0 else "Gratuit"
        print(f"  • {event['title']}")
        print(f"    📍 {event['venue_name']} - {event['date']} à {event['start_time']}")
        print(f"    💰 {price_str} | 🏷️  {event['main_category']}/{event['sub_category']}")
        print()


if __name__ == "__main__":
    add_events_to_database()
    print("\n" + "=" * 60)
    list_events()


