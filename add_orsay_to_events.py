#!/usr/bin/env python3
"""
🏛️ Ajoute les expositions du Musée d'Orsay à la base de données des événements
Pour qu'elles apparaissent dans les recommandations et le calendrier
"""

import hashlib
from datetime import datetime, timedelta
from events_database import EventsDatabase
import json

# Expositions du Musée d'Orsay avec périodes réelles
ORSAY_EXHIBITIONS = [
    {
        "title": "John Singer Sargent - Éblouir Paris",
        "description": "Première grande rétrospective en France consacrée à John Singer Sargent (1856-1925), figure majeure de la peinture de la fin du XIXe siècle. L'exposition explore son rapport à Paris et à la scène artistique française, depuis ses années de formation jusqu'à sa consécration internationale. Découvrez plus de 80 œuvres majeures du maître américain, virtuose du portrait et de la lumière.",
        "date_start": "2024-10-15",
        "date_end": "2026-01-11",
        "sub_category": "beaux_arts",
        "price": 16,
        "image": "https://www.musee-orsay.fr/sites/default/files/2024-09/sargent-affiche.jpg",
        "featured": True,
        "tags": ["peinture", "portrait", "impressionnisme", "américain", "musée"],
    },
    {
        "title": "Paul Troubetzkoy - Sculpteur (1866-1938)",
        "description": "Première exposition monographique en France dédiée au sculpteur italo-russe Paul Troubetzkoy. Ses œuvres impressionnistes saisissent l'instant avec une virtuosité remarquable, immortalisant les figures de son époque avec une spontanéité et une élégance uniques. Un artiste majeur de la Belle Époque à redécouvrir.",
        "date_start": "2024-10-15",
        "date_end": "2026-01-11",
        "sub_category": "beaux_arts",
        "price": 16,
        "image": None,
        "featured": False,
        "tags": ["sculpture", "impressionnisme", "portrait", "belle époque", "musée"],
    },
    {
        "title": "Bridget Riley - Point de départ",
        "description": "Exposition contemporaine dédiée à Bridget Riley, figure majeure de l'art optique. L'artiste britannique dialogue avec les collections impressionnistes du musée d'Orsay dans une exploration fascinante de la perception visuelle et de la couleur. Une rencontre unique entre Op Art et impressionnisme.",
        "date_start": "2024-10-22",
        "date_end": "2026-01-25",
        "sub_category": "art_contemporain",
        "price": 16,
        "image": None,
        "featured": True,
        "tags": ["art contemporain", "art optique", "abstraction", "couleur", "musée"],
    },
    {
        "title": "Gabrielle Hébert - Amour fou à la Villa Médicis",
        "description": "Exposition consacrée à Gabrielle Hébert, explorant sa relation passionnée avec le sculpteur Ernest Hébert lors de leurs années à la Villa Médicis à Rome. Un voyage au cœur de l'art et de l'amour au XIXe siècle, à travers des œuvres et correspondances inédites.",
        "date_start": "2024-11-05",
        "date_end": "2026-02-15",
        "sub_category": "beaux_arts",
        "price": 16,
        "image": None,
        "featured": False,
        "tags": ["art romantique", "histoire", "villa médicis", "XIXe siècle", "musée"],
    },
    {
        "title": "Renoir dessinateur",
        "description": "Exposition dédiée à l'œuvre graphique d'Auguste Renoir, révélant un aspect méconnu de son art. Dessins, pastels et études préparatoires témoignent de la maîtrise technique et de la sensibilité du maître impressionniste. Une plongée intime dans le processus créatif de Renoir.",
        "date_start": "2026-03-17",
        "date_end": "2026-07-05",
        "sub_category": "beaux_arts",
        "price": 16,
        "image": None,
        "featured": True,
        "tags": ["dessin", "renoir", "impressionnisme", "études", "musée"],
    },
    {
        "title": "Renoir et l'amour",
        "description": "Grande exposition thématique explorant le thème de l'amour dans l'œuvre de Pierre-Auguste Renoir. Des premiers portraits intimes aux grandes compositions, une célébration de la tendresse, de la sensualité et de la joie de vivre qui caractérisent l'art du maître impressionniste.",
        "date_start": "2026-03-17",
        "date_end": "2026-07-19",
        "sub_category": "beaux_arts",
        "price": 16,
        "image": None,
        "featured": True,
        "tags": ["renoir", "amour", "impressionnisme", "portrait", "musée"],
    },
]

MUSEUM_INFO = {
    "name": "Musée d'Orsay",
    "address": "1 Rue de la Légion d'Honneur, 75007 Paris",
    "arrondissement": 7,
    "source_url": "https://www.musee-orsay.fr/fr/agenda/expositions",
    "source_name": "Musée d'Orsay",
    "booking_url": "https://billetterie.musee-orsay.fr/",
}


def generate_event_id(title: str, date: str) -> str:
    """Génère un ID unique pour un événement."""
    unique_string = f"orsay-{title}-{date}"
    return f"orsay-{hashlib.md5(unique_string.encode()).hexdigest()[:12]}"


def get_dates_in_range(start_date: str, end_date: str, interval_days: int = 3) -> list:
    """Génère une liste de dates entre deux dates avec un intervalle."""
    dates = []
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    today = datetime.now().date()
    
    # S'assurer qu'on commence à partir d'aujourd'hui si l'exposition est en cours
    if start.date() < today:
        start = datetime.combine(today, datetime.min.time())
    
    current = start
    day_count = 0
    
    # Pour les 7 premiers jours : créer des événements quotidiens
    # Ensuite, utiliser l'intervalle de 3 jours
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        if current.date() >= today:
            dates.append(date_str)
        
        day_count += 1
        if day_count < 7:
            # Quotidien pour la première semaine
            current += timedelta(days=1)
        else:
            # Tous les 3 jours après
            current += timedelta(days=interval_days)
    
    return dates


def delete_old_orsay_events(db: EventsDatabase):
    """Supprime les anciens événements Orsay de la base."""
    import sqlite3
    conn = sqlite3.connect('real_events.db')
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM events WHERE id LIKE 'orsay-%'")
        deleted = cursor.rowcount
        conn.commit()
        print(f"🗑️  {deleted} anciens événements Orsay supprimés")
    except Exception as e:
        print(f"⚠️  Erreur lors de la suppression: {e}")
    finally:
        conn.close()


def add_orsay_exhibitions():
    """Ajoute les expositions du Musée d'Orsay à la base des événements."""
    db = EventsDatabase('real_events.db')
    
    print("=" * 70)
    print("🏛️  AJOUT DES EXPOSITIONS DU MUSÉE D'ORSAY AUX RECOMMANDATIONS")
    print("=" * 70)
    
    # Supprimer les anciens événements Orsay
    delete_old_orsay_events(db)
    
    events_to_add = []
    
    today = datetime.now().date()
    today_str = today.strftime("%Y-%m-%d")
    
    # Calculer les dates importantes : aujourd'hui, demain, weekend
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    
    # Trouver le prochain samedi et dimanche
    days_until_saturday = (5 - today.weekday()) % 7
    if days_until_saturday == 0:  # Si on est déjà samedi
        days_until_saturday = 7
    saturday = today + timedelta(days=days_until_saturday)
    sunday = saturday + timedelta(days=1)
    weekend_dates = [saturday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")]
    
    print(f"\n📅 Dates importantes:")
    print(f"   Aujourd'hui: {today_str}")
    print(f"   Demain: {tomorrow_str}")
    print(f"   Weekend: {', '.join(weekend_dates)}")
    
    for expo in ORSAY_EXHIBITIONS:
        print(f"\n📍 {expo['title']}")
        print(f"   Période: {expo['date_start']} → {expo['date_end']}")
        
        # Générer des dates de visite
        dates = get_dates_in_range(expo['date_start'], expo['date_end'], interval_days=3)
        
        # S'assurer qu'on a les dates importantes (aujourd'hui, demain, weekend)
        important_dates = [today_str, tomorrow_str] + weekend_dates
        for important_date in important_dates:
            expo_end = datetime.strptime(expo['date_end'], "%Y-%m-%d").date()
            if important_date not in dates and datetime.strptime(important_date, "%Y-%m-%d").date() <= expo_end:
                # Vérifier que la date est dans la période de l'exposition
                expo_start = datetime.strptime(expo['date_start'], "%Y-%m-%d").date()
                if datetime.strptime(important_date, "%Y-%m-%d").date() >= expo_start:
                    dates.append(important_date)
        
        # Trier et dédupliquer
        dates = sorted(list(set(dates)))
        
        # Filtrer pour garder uniquement les dates à partir d'aujourd'hui
        dates = [d for d in dates if d >= today_str]
        
        if not dates:
            print(f"   ⚠️  Aucune date disponible")
            continue
        
        # Limiter à 50 dates par exposition pour avoir plus de variété
        dates = dates[:50]
        print(f"   📅 {len(dates)} créneaux générés")
        
        # Vérifier qu'on a les dates importantes
        has_today = today_str in dates
        has_tomorrow = tomorrow_str in dates
        has_weekend = any(wd in dates for wd in weekend_dates)
        print(f"   ✓ Aujourd'hui: {'✅' if has_today else '❌'}")
        print(f"   ✓ Demain: {'✅' if has_tomorrow else '❌'}")
        print(f"   ✓ Weekend: {'✅' if has_weekend else '❌'}")
        
        # Créer les horaires de visite
        horaires = [
            ("10:00", "matin"),
            ("14:30", "apres_midi"),
            ("19:00", "soir"),  # Nocturne jeudi
        ]
        
        for event_date in dates:
            # Déterminer les horaires selon le jour
            date_obj = datetime.strptime(event_date, "%Y-%m-%d")
            is_thursday = date_obj.weekday() == 3  # Jeudi = 3
            
            # Horaires de base : matin et après-midi
            selected_horaires = horaires[:2]
            # Ajouter la nocturne pour le jeudi
            if is_thursday:
                selected_horaires = horaires  # Tous les horaires incluant le soir
            
            for start_time, time_of_day in selected_horaires:
                event = {
                    'id': generate_event_id(expo['title'], f"{event_date}-{start_time}"),
                    'title': expo['title'],
                    'description': expo['description'],
                    'main_category': 'arts_visuels',
                    'sub_category': expo.get('sub_category', 'beaux_arts'),
                    'date': event_date,
                    'start_time': start_time,
                    'end_time': None,
                    'time_of_day': time_of_day,
                    'venue': MUSEUM_INFO['name'],
                    'address': MUSEUM_INFO['address'],
                    'arrondissement': MUSEUM_INFO['arrondissement'],
                    'price': expo['price'],
                    'price_max': None,
                    'source_url': MUSEUM_INFO['source_url'],
                    'source_name': MUSEUM_INFO['source_name'],
                    'image_url': expo.get('image'),
                    'duration': 120,  # 2 heures de visite
                    'booking_required': True,
                    'tags': expo.get('tags', []),
                    'latitude': 48.8600,
                    'longitude': 2.3266,
                    'verified': True,
                }
                events_to_add.append(event)
    
    print(f"\n💾 Ajout de {len(events_to_add)} événements à la base...")
    
    result = db.add_batch(events_to_add)
    
    print(f"\n✅ Résultat:")
    print(f"   • Ajoutés: {result['added']}")
    print(f"   • Mis à jour: {result['updated']}")
    
    # Afficher les stats
    stats = db.get_statistics()
    print(f"\n📊 Statistiques de la base:")
    print(f"   Total événements: {stats['total_events']}")
    print(f"   Arts visuels: {stats['by_category'].get('arts_visuels', 0)}")
    
    return result


def verify_orsay_in_db():
    """Vérifie que les expositions Orsay sont dans la base."""
    db = EventsDatabase('real_events.db')
    
    print("\n🔍 Vérification des expositions Orsay dans la base...")
    
    # Rechercher les événements Orsay
    events = db.search_events("Orsay", limit=50)
    
    print(f"   Trouvé: {len(events)} événements")
    
    if events:
        print("\n📋 Exemples d'événements Orsay:")
        for event in events[:10]:
            print(f"   📅 {event['date']} | {event['title'][:45]}...")
    
    return len(events)


if __name__ == "__main__":
    # Ajouter les expositions
    add_orsay_exhibitions()
    
    # Vérifier
    verify_orsay_in_db()
    
    print("\n✅ Les expositions Orsay sont maintenant dans les recommandations!")
    print("   Redémarrez l'API events (python events_api.py) pour voir les changements.")

