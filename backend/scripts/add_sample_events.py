"""
Script to add sample events to the database for testing
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.db import EventsDB

def add_sample_events():
    """Add sample Paris cultural events to the database"""
    db = EventsDB()
    
    # Sample events
    events = [
        {
            "id": "evt_louvre_van_gogh",
            "title": "Van Gogh : Les Nuits Étoilées",
            "description": "Une exposition exceptionnelle présentant les plus belles œuvres de Vincent van Gogh, avec un focus sur ses célèbres nuits étoilées. Découvrez l'évolution de son style et son influence sur l'art moderne.",
            "start_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=95)).isoformat(),
            "location": "Musée du Louvre",
            "address": "Rue de Rivoli, 75001 Paris",
            "category": "art",
            "image_url": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800",
            "source_url": "https://www.louvre.fr/expositions/van-gogh-nuits-etoilees",
            "source_name": "louvre",
            "is_free": False,
            "price": 17.00,
            "currency": "EUR",
            "ticket_url": "https://www.louvre.fr/billetterie",
        },
        {
            "id": "evt_orsay_impressionnistes",
            "title": "Les Impressionnistes en Plein Air",
            "description": "Exposition temporaire sur les peintres impressionnistes et leur relation avec la nature. Plus de 80 œuvres de Monet, Renoir, Pissarro et bien d'autres.",
            "start_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "location": "Musée d'Orsay",
            "address": "1 Rue de la Légion d'Honneur, 75007 Paris",
            "category": "art",
            "image_url": "https://images.unsplash.com/photo-1578301978018-3005759f48f7?w=800",
            "source_url": "https://www.musee-orsay.fr/expositions/impressionnistes",
            "source_name": "orsay",
            "is_free": False,
            "price": 16.00,
            "currency": "EUR",
            "ticket_url": "https://www.musee-orsay.fr/billetterie",
        },
        {
            "id": "evt_pompidou_contemporain",
            "title": "Art Contemporain : Nouvelles Perspectives",
            "description": "Découvrez les dernières tendances de l'art contemporain avec des œuvres d'artistes émergents et établis. Installation interactive, vidéo-art et performances.",
            "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=45)).isoformat(),
            "location": "Centre Pompidou",
            "address": "Place Georges-Pompidou, 75004 Paris",
            "category": "art",
            "image_url": "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=800",
            "source_url": "https://www.centrepompidou.fr/expositions/contemporain",
            "source_name": "pompidou",
            "is_free": False,
            "price_min": 14.00,
            "price_max": 18.00,
            "currency": "EUR",
            "ticket_url": "https://www.centrepompidou.fr/billetterie",
        },
        {
            "id": "evt_philharmonie_jazz",
            "title": "Jazz Night : Herbie Hancock Tribute",
            "description": "Concert exceptionnel en hommage à Herbie Hancock avec des musiciens de renommée internationale. Une soirée inoubliable de jazz moderne.",
            "start_date": (datetime.now() + timedelta(days=7, hours=20)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=7, hours=23)).isoformat(),
            "location": "Philharmonie de Paris",
            "address": "221 Avenue Jean Jaurès, 75019 Paris",
            "category": "music",
            "image_url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800",
            "source_url": "https://www.philharmoniedeparis.fr/concerts/jazz-hancock",
            "source_name": "philharmonie",
            "is_free": False,
            "price_min": 35.00,
            "price_max": 85.00,
            "currency": "EUR",
            "ticket_url": "https://www.philharmoniedeparis.fr/billetterie",
        },
        {
            "id": "evt_opera_carmen",
            "title": "Carmen - Opéra de Bizet",
            "description": "Représentation de l'opéra emblématique de Georges Bizet dans une mise en scène moderne et audacieuse. Distribution internationale de premier plan.",
            "start_date": (datetime.now() + timedelta(days=10, hours=19)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=10, hours=22)).isoformat(),
            "location": "Opéra Bastille",
            "address": "Place de la Bastille, 75012 Paris",
            "category": "theater",
            "image_url": "https://images.unsplash.com/photo-1503095396549-807759245b35?w=800",
            "source_url": "https://www.operadeparis.fr/spectacles/carmen",
            "source_name": "opera",
            "is_free": False,
            "price_min": 25.00,
            "price_max": 150.00,
            "currency": "EUR",
            "ticket_url": "https://www.operadeparis.fr/billetterie",
        },
        {
            "id": "evt_grand_palais_photo",
            "title": "Photographie Contemporaine : Regards sur Paris",
            "description": "Exposition gratuite présentant les meilleurs photographes contemporains et leur vision de Paris. Entrée libre tous les premiers dimanches du mois.",
            "start_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "location": "Grand Palais",
            "address": "3 Avenue du Général Eisenhower, 75008 Paris",
            "category": "art",
            "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800",
            "source_url": "https://www.grandpalais.fr/expositions/photo-paris",
            "source_name": "grand_palais",
            "is_free": True,
            "price": None,
            "currency": "EUR",
            "ticket_url": None,
        },
        {
            "id": "evt_cite_musique_workshop",
            "title": "Atelier de Musique Électronique",
            "description": "Atelier interactif pour découvrir la création musicale électronique. Ouvert à tous les niveaux. Matériel fourni.",
            "start_date": (datetime.now() + timedelta(days=6, hours=14)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=6, hours=17)).isoformat(),
            "location": "Cité de la Musique",
            "address": "221 Avenue Jean Jaurès, 75019 Paris",
            "category": "music",
            "image_url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800",
            "source_url": "https://www.citedelamusique.fr/ateliers/electronique",
            "source_name": "cite_musique",
            "is_free": True,
            "price": None,
            "currency": "EUR",
            "ticket_url": None,
        },
        {
            "id": "evt_palais_tokyo_installation",
            "title": "Installation Interactive : Espace-Temps",
            "description": "Une installation artistique immersive qui explore les concepts d'espace et de temps à travers des technologies numériques et des expériences sensorielles.",
            "start_date": (datetime.now() + timedelta(days=4)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=50)).isoformat(),
            "location": "Palais de Tokyo",
            "address": "13 Avenue du Président Wilson, 75016 Paris",
            "category": "art",
            "image_url": "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=800",
            "source_url": "https://www.palaisdetokyo.com/expositions/espace-temps",
            "source_name": "palais_tokyo",
            "is_free": False,
            "price": 12.00,
            "currency": "EUR",
            "ticket_url": "https://www.palaisdetokyo.com/billetterie",
        },
        {
            "id": "evt_theatre_ville_dance",
            "title": "Spectacle de Danse Contemporaine",
            "description": "Compagnie de danse internationale présente une création originale mêlant danse contemporaine et musique live. Performance captivante et émotionnelle.",
            "start_date": (datetime.now() + timedelta(days=8, hours=20)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=8, hours=21, minutes=30)).isoformat(),
            "location": "Théâtre de la Ville",
            "address": "2 Place du Châtelet, 75001 Paris",
            "category": "dance",
            "image_url": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=800",
            "source_url": "https://www.theatredelaville-paris.com/spectacles/danse",
            "source_name": "theatre_ville",
            "is_free": False,
            "price_min": 20.00,
            "price_max": 45.00,
            "currency": "EUR",
            "ticket_url": "https://www.theatredelaville-paris.com/billetterie",
        },
        {
            "id": "evt_cinematheque_film",
            "title": "Rétrospective : Cinéma Français des Années 60",
            "description": "Cycle de projections de films français emblématiques des années 1960. Présentation et discussion avec des cinéastes et critiques.",
            "start_date": (datetime.now() + timedelta(days=12, hours=19)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=12, hours=21, minutes=30)).isoformat(),
            "location": "Cinémathèque Française",
            "address": "51 Rue de Bercy, 75012 Paris",
            "category": "film",
            "image_url": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800",
            "source_url": "https://www.cinematheque.fr/retrospectives/annees-60",
            "source_name": "cinematheque",
            "is_free": False,
            "price": 8.50,
            "currency": "EUR",
            "ticket_url": "https://www.cinematheque.fr/billetterie",
        },
    ]
    
    added_count = 0
    updated_count = 0
    
    for event in events:
        is_new = db.add_event(event)
        if is_new:
            added_count += 1
            print(f"✅ Ajouté: {event['title']}")
        else:
            updated_count += 1
            print(f"🔄 Mis à jour: {event['title']}")
    
    print(f"\n📊 Résumé: {added_count} événements ajoutés, {updated_count} mis à jour")
    
    # Afficher les statistiques
    stats = db.get_statistics()
    print(f"\n📈 Statistiques de la base de données:")
    print(f"   Total d'événements: {stats['total_events']}")
    print(f"   Événements gratuits: {stats['free_events']}")
    print(f"   Événements à venir (30 jours): {stats['upcoming_30_days']}")
    print(f"   Par catégorie: {stats['by_category']}")

if __name__ == "__main__":
    add_sample_events()

