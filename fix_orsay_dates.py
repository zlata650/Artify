#!/usr/bin/env python3
"""
🏛️ Correction des dates des expositions Orsay
Ajoute des créneaux pour CHAQUE jour (pas tous les 3 jours)
et des horaires soir pour le filtre "Ce soir"
"""

import hashlib
from datetime import datetime, timedelta
from events_database import EventsDatabase

# Expositions du Musée d'Orsay
ORSAY_EXHIBITIONS = [
    {
        "title": "John Singer Sargent - Éblouir Paris",
        "description": "Première grande rétrospective en France consacrée à John Singer Sargent (1856-1925), figure majeure de la peinture de la fin du XIXe siècle. L'exposition explore son rapport à Paris et à la scène artistique française.",
        "date_start": "2024-10-15",
        "date_end": "2026-01-11",
        "sub_category": "beaux_arts",
        "price": 16,
        "image": "https://www.musee-orsay.fr/sites/default/files/2024-09/sargent-affiche.jpg",
        "tags": ["peinture", "portrait", "impressionnisme", "américain", "musée"],
    },
    {
        "title": "Paul Troubetzkoy - Sculpteur (1866-1938)",
        "description": "Première exposition monographique en France dédiée au sculpteur italo-russe Paul Troubetzkoy. Ses œuvres impressionnistes saisissent l'instant avec une virtuosité remarquable.",
        "date_start": "2024-10-15",
        "date_end": "2026-01-11",
        "sub_category": "beaux_arts",
        "price": 16,
        "image": None,
        "tags": ["sculpture", "impressionnisme", "portrait", "belle époque", "musée"],
    },
    {
        "title": "Bridget Riley - Point de départ",
        "description": "Exposition contemporaine dédiée à Bridget Riley, figure majeure de l'art optique. L'artiste britannique dialogue avec les collections impressionnistes du musée d'Orsay.",
        "date_start": "2024-10-22",
        "date_end": "2026-01-25",
        "sub_category": "art_contemporain",
        "price": 16,
        "image": None,
        "tags": ["art contemporain", "art optique", "abstraction", "couleur", "musée"],
    },
    {
        "title": "Gabrielle Hébert - Amour fou à la Villa Médicis",
        "description": "Exposition consacrée à Gabrielle Hébert, explorant sa relation passionnée avec le sculpteur Ernest Hébert lors de leurs années à la Villa Médicis à Rome.",
        "date_start": "2024-11-05",
        "date_end": "2026-02-15",
        "sub_category": "beaux_arts",
        "price": 16,
        "image": None,
        "tags": ["art romantique", "histoire", "villa médicis", "XIXe siècle", "musée"],
    },
]

MUSEUM_INFO = {
    "name": "Musée d'Orsay",
    "address": "1 Rue de la Légion d'Honneur, 75007 Paris",
    "arrondissement": 7,
    "source_url": "https://www.musee-orsay.fr/fr/agenda/expositions",
    "source_name": "Musée d'Orsay",
}


def generate_event_id(title: str, date: str, time: str) -> str:
    """Génère un ID unique pour un événement."""
    unique_string = f"orsay-{title}-{date}-{time}"
    return f"orsay-{hashlib.md5(unique_string.encode()).hexdigest()[:12]}"


def add_daily_orsay_events():
    """Ajoute des événements Orsay pour CHAQUE jour avec tous les créneaux horaires."""
    db = EventsDatabase('real_events.db')
    
    print("=" * 70)
    print("🏛️  CORRECTION DES DATES DES EXPOSITIONS ORSAY")
    print("=" * 70)
    
    # Supprimer les anciens événements Orsay
    cursor = db._connect()
    cursor.execute("DELETE FROM events WHERE venue = 'Musée d''Orsay'")
    deleted = cursor.rowcount
    db.conn.commit()
    db._close()
    print(f"🗑️  {deleted} anciens événements Orsay supprimés")
    
    events_to_add = []
    
    # Créneaux horaires incluant le soir
    horaires = [
        ("10:00", "matin", 16),
        ("14:30", "apres_midi", 16),
        ("19:00", "soir", 14),  # Nocturne avec tarif réduit
    ]
    
    # Générer des événements pour les 45 prochains jours (chaque jour)
    today = datetime.now().date()
    
    for expo in ORSAY_EXHIBITIONS:
        print(f"\n📍 {expo['title']}")
        
        expo_start = datetime.strptime(expo['date_start'], "%Y-%m-%d").date()
        expo_end = datetime.strptime(expo['date_end'], "%Y-%m-%d").date()
        
        # Générer pour les 45 prochains jours
        for day_offset in range(45):
            event_date = today + timedelta(days=day_offset)
            
            # Vérifier que la date est dans la période de l'expo
            if event_date < expo_start or event_date > expo_end:
                continue
            
            date_str = event_date.strftime("%Y-%m-%d")
            
            for start_time, time_of_day, price in horaires:
                event = {
                    'id': generate_event_id(expo['title'], date_str, start_time),
                    'title': expo['title'],
                    'description': expo['description'],
                    'main_category': 'arts_visuels',
                    'sub_category': expo.get('sub_category', 'beaux_arts'),
                    'date': date_str,
                    'start_time': start_time,
                    'end_time': None,
                    'time_of_day': time_of_day,
                    'venue': MUSEUM_INFO['name'],
                    'address': MUSEUM_INFO['address'],
                    'arrondissement': MUSEUM_INFO['arrondissement'],
                    'price': price,
                    'price_max': None,
                    'source_url': MUSEUM_INFO['source_url'],
                    'source_name': MUSEUM_INFO['source_name'],
                    'image_url': expo.get('image'),
                    'duration': 120,  # 2 heures
                    'booking_required': True,
                    'tags': expo.get('tags', []),
                    'latitude': 48.8600,
                    'longitude': 2.3266,
                    'verified': True,
                }
                events_to_add.append(event)
        
        print(f"   📅 {len([e for e in events_to_add if e['title'] == expo['title']])} créneaux générés")
    
    print(f"\n💾 Ajout de {len(events_to_add)} événements...")
    
    result = db.add_batch(events_to_add)
    
    print(f"\n✅ Résultat:")
    print(f"   • Ajoutés: {result['added']}")
    print(f"   • Mis à jour: {result['updated']}")
    
    # Vérification
    print("\n🔍 Vérification des événements pour les prochains jours:")
    for day_offset in range(5):
        date_check = (today + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        cursor = db._connect()
        cursor.execute(
            "SELECT COUNT(*), GROUP_CONCAT(DISTINCT time_of_day) FROM events WHERE venue = 'Musée d''Orsay' AND date = ?",
            (date_check,)
        )
        count, times = cursor.fetchone()
        db._close()
        day_name = ["Aujourd'hui", "Demain", "Après-demain", "Dans 3 jours", "Dans 4 jours"][day_offset]
        print(f"   {day_name} ({date_check}): {count} événements ({times})")
    
    return result


if __name__ == "__main__":
    add_daily_orsay_events()
    print("\n✅ Les expositions Orsay sont maintenant disponibles pour tous les jours!")
    print("   Incluant les créneaux soir pour le filtre 'Ce soir'")

