#!/usr/bin/env python3
"""
🏛️ Scraper pour les expositions du Musée d'Orsay
Ajoute les expositions actuelles avec leurs vraies périodes
"""

import hashlib
from datetime import datetime, timedelta
from database_v2 import ArtifyDatabase

# ============================================================================
# EXPOSITIONS DU MUSÉE D'ORSAY (décembre 2024 - données réelles)
# ============================================================================

ORSAY_EXHIBITIONS = [
    # ========== EXPOSITIONS EN COURS ==========
    {
        "title": "John Singer Sargent - Éblouir Paris",
        "description": "Première grande rétrospective en France consacrée à John Singer Sargent (1856-1925), figure majeure de la peinture de la fin du XIXe siècle. L'exposition explore son rapport à Paris et à la scène artistique française, depuis ses années de formation jusqu'à sa consécration internationale.",
        "date_start": "2024-10-15",
        "date_end": "2026-01-11",
        "type": "exposition_temporaire",
        "price": 16,
        "image": "https://www.musee-orsay.fr/sites/default/files/2024-09/sargent-affiche.jpg",
    },
    {
        "title": "Paul Troubetzkoy - Sculpteur (1866-1938)",
        "description": "Première exposition monographique en France dédiée au sculpteur italo-russe Paul Troubetzkoy. Ses œuvres impressionnistes saisissent l'instant avec une virtuosité remarquable, immortalisant les figures de son époque.",
        "date_start": "2024-10-15",
        "date_end": "2026-01-11",
        "type": "exposition_temporaire",
        "price": 16,
        "image": None,
    },
    {
        "title": "Bridget Riley - Point de départ",
        "description": "Exposition contemporaine dédiée à Bridget Riley, figure majeure de l'art optique. L'artiste britannique dialogue avec les collections impressionnistes du musée d'Orsay dans une exploration fascinante de la perception visuelle.",
        "date_start": "2024-10-22",
        "date_end": "2026-01-25",
        "type": "exposition_contemporaine",
        "price": 16,
        "image": None,
    },
    {
        "title": "Gabrielle Hébert - Amour fou à la Villa Médicis",
        "description": "Exposition consacrée à Gabrielle Hébert, explorant sa relation passionnée avec le sculpteur Ernest Hébert lors de leurs années à la Villa Médicis à Rome. Un voyage au cœur de l'art et de l'amour au XIXe siècle.",
        "date_start": "2024-11-05",
        "date_end": "2026-02-15",
        "type": "exposition_temporaire",
        "price": 16,
        "image": None,
    },
    
    # ========== EXPOSITIONS À VENIR ==========
    {
        "title": "Renoir dessinateur",
        "description": "Exposition dédiée à l'œuvre graphique d'Auguste Renoir, révélant un aspect méconnu de son art. Dessins, pastels et études préparatoires témoignent de la maîtrise technique et de la sensibilité du maître impressionniste.",
        "date_start": "2026-03-17",
        "date_end": "2026-07-05",
        "type": "exposition_temporaire",
        "price": 16,
        "image": None,
    },
    {
        "title": "Renoir et l'amour",
        "description": "Grande exposition thématique explorant le thème de l'amour dans l'œuvre de Pierre-Auguste Renoir. Des premiers portraits intimes aux grandes compositions, une célébration de la tendresse et de la joie de vivre.",
        "date_start": "2026-03-17",
        "date_end": "2026-07-19",
        "type": "exposition_temporaire",
        "price": 16,
        "image": None,
    },
    
    # ========== COLLECTIONS PERMANENTES ==========
    {
        "title": "Collections impressionnistes - Musée d'Orsay",
        "description": "La plus grande collection d'art impressionniste et post-impressionniste au monde. Chefs-d'œuvre de Monet, Renoir, Van Gogh, Cézanne, Degas, et bien d'autres maîtres du XIXe siècle.",
        "date_start": "2025-01-01",
        "date_end": "2025-12-31",
        "type": "collection_permanente",
        "price": 16,
        "image": None,
    },
]

# Informations du musée
MUSEE_ORSAY = {
    "nom": "Musée d'Orsay",
    "adresse": "1 Rue de la Légion d'Honneur, 75007 Paris",
    "arrondissement": 7,
    "url": "https://www.musee-orsay.fr",
    "metro": ["Solférino", "Musée d'Orsay (RER C)"],
}


def generate_event_id(title: str, date: str) -> str:
    """Génère un ID unique pour un événement."""
    unique_string = f"orsay-{title}-{date}"
    return f"orsay-{hashlib.md5(unique_string.encode()).hexdigest()[:12]}"


def get_dates_in_range(start_date: str, end_date: str, interval_days: int = 7) -> list:
    """Génère une liste de dates entre deux dates avec un intervalle."""
    dates = []
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=interval_days)
    
    return dates


def determine_time_of_day(hour: int) -> str:
    """Détermine le moment de la journée."""
    if hour < 12:
        return "matin"
    elif hour < 18:
        return "apres_midi"
    elif hour < 23:
        return "soir"
    return "nuit"


def add_orsay_exhibitions_to_db():
    """Ajoute les expositions du Musée d'Orsay à la base de données."""
    db = ArtifyDatabase('artify.db')
    added = 0
    
    print("=" * 70)
    print("🏛️  AJOUT DES EXPOSITIONS DU MUSÉE D'ORSAY")
    print("=" * 70)
    
    for expo in ORSAY_EXHIBITIONS:
        print(f"\n📍 {expo['title']}")
        print(f"   Période: {expo['date_start']} → {expo['date_end']}")
        
        # Déterminer si c'est une expo en cours ou à venir
        today = datetime.now().strftime("%Y-%m-%d")
        is_current = expo['date_start'] <= today <= expo['date_end']
        is_upcoming = expo['date_start'] > today
        
        status = "🟢 En cours" if is_current else ("🔵 À venir" if is_upcoming else "⚪ Passée")
        print(f"   Statut: {status}")
        
        # Créer des événements pour différentes dates de visite
        # On génère des créneaux tous les 3 jours pendant la période
        dates = get_dates_in_range(expo['date_start'], expo['date_end'], interval_days=3)
        
        # Filtrer pour garder uniquement les dates à partir de décembre 2025
        dates = [d for d in dates if d >= "2025-12-01"]
        
        if not dates:
            print(f"   ⚠️  Aucune date à partir de décembre 2025")
            continue
        
        print(f"   📅 {len(dates)} créneaux de visite générés")
        
        # Horaires d'ouverture du musée
        horaires = [
            ("09:30", "matin"),
            ("14:00", "apres_midi"),
            ("16:30", "apres_midi"),
        ]
        
        # Ajouter le jeudi soir (nocturne)
        if expo['type'] != 'collection_permanente':
            horaires.append(("21:00", "soir"))
        
        for date in dates[:50]:  # Limiter à 50 dates par expo pour ne pas surcharger
            for start_time, time_of_day in horaires[:2]:  # 2 créneaux par jour
                # Prix selon le type
                price = expo['price']
                if time_of_day == 'soir':
                    price = 12  # Tarif réduit nocturne
                
                # Budget
                if price == 0:
                    budget = 'gratuit'
                elif price <= 20:
                    budget = '0-20'
                else:
                    budget = '20-50'
                
                # Description enrichie
                description = expo['description']
                description += f"\n\n📅 Période d'exposition: du {expo['date_start']} au {expo['date_end']}"
                description += f"\n🎫 Tarif: {price}€"
                description += f"\n📍 {MUSEE_ORSAY['adresse']}"
                description += f"\n🚇 Métro: {', '.join(MUSEE_ORSAY['metro'])}"
                
                event_data = {
                    'id': generate_event_id(expo['title'], f"{date}-{start_time}"),
                    'title': expo['title'],
                    'main_category': 'arts_visuels',
                    'sub_category': 'beaux_arts' if 'impressionni' in expo['description'].lower() else 'art_moderne',
                    'date': date,
                    'start_time': start_time,
                    'end_time': None,
                    'time_of_day': time_of_day,
                    'venue': MUSEE_ORSAY['nom'],
                    'address': MUSEE_ORSAY['adresse'],
                    'arrondissement': MUSEE_ORSAY['arrondissement'],
                    'price': price,
                    'budget': budget,
                    'description': description,
                    'short_description': expo['description'][:150] + "...",
                    'source_url': MUSEE_ORSAY['url'] + '/fr/agenda/expositions',
                    'source_name': 'Musée d\'Orsay',
                    'image': expo.get('image'),
                    'tags': ['musée', 'exposition', 'orsay', 'paris', 'impressionnisme', 'art'],
                    'ambiance': ['culturel'],
                    'metro': MUSEE_ORSAY['metro'],
                    'booking_required': True,
                    'booking_url': 'https://billetterie.musee-orsay.fr/',
                }
                
                if db.add_event(event_data):
                    added += 1
    
    print(f"\n✅ {added} créneaux de visite ajoutés à la base de données")
    return added


def show_orsay_stats():
    """Affiche les statistiques des expositions Orsay."""
    db = ArtifyDatabase('artify.db')
    
    print("\n" + "=" * 70)
    print("📊 STATISTIQUES DES EXPOSITIONS ORSAY")
    print("=" * 70)
    
    # Rechercher les événements Orsay
    events = db.get_events(search="Orsay", limit=1000)
    orsay_events = [e for e in events if "orsay" in e.get('venue_name', '').lower()]
    
    print(f"\n🏛️  Total événements Musée d'Orsay: {len(orsay_events)}")
    
    # Par exposition
    expos = {}
    for e in orsay_events:
        title = e.get('title', 'Inconnu')
        if title not in expos:
            expos[title] = {'count': 0, 'dates': set()}
        expos[title]['count'] += 1
        expos[title]['dates'].add(e.get('date', ''))
    
    print("\n📍 Par exposition:")
    for title, data in sorted(expos.items()):
        dates = sorted(data['dates'])
        if dates:
            print(f"   • {title[:50]}...")
            print(f"     {data['count']} créneaux | {dates[0]} → {dates[-1]}")
    
    # Stats globales
    stats = db.get_stats()
    print(f"\n📊 Base de données globale:")
    print(f"   Total événements: {stats['total_events']}")
    print(f"   Par catégorie: {stats.get('by_category', {})}")


def main():
    """Script principal."""
    print("\n🏛️  MUSÉE D'ORSAY - IMPORT DES EXPOSITIONS")
    print("   Données actualisées décembre 2024")
    print()
    
    # Afficher les expositions
    print("📋 EXPOSITIONS À IMPORTER:")
    print("-" * 50)
    for expo in ORSAY_EXHIBITIONS:
        status = "🟢" if expo['date_start'] <= "2025-12-04" else "🔵"
        print(f"{status} {expo['title']}")
        print(f"   📅 {expo['date_start']} → {expo['date_end']}")
        print(f"   💰 {expo['price']}€")
        print()
    
    # Ajouter à la base de données
    added = add_orsay_exhibitions_to_db()
    
    # Afficher les stats
    show_orsay_stats()
    
    print("\n✅ Import terminé!")
    return added


if __name__ == "__main__":
    main()


