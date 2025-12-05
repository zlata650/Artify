"""
🎭 Artify - API des événements réels
API Flask pour servir les événements depuis la base de données SQLite
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, date, timedelta
from events_database import EventsDatabase
import json

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001'])

# Instance de la base de données
db = EventsDatabase()


def deduplicate_events(events: list) -> list:
    """
    Déduplique les événements par titre, gardant le plus proche dans le temps.
    Pour les expositions avec plusieurs créneaux, on garde celui avec la date/heure la plus proche.
    """
    from datetime import datetime
    
    now = datetime.now()
    unique_events = {}
    
    for event in events:
        title = event.get('title', '')
        event_datetime_str = f"{event.get('date', '')} {event.get('start_time', '00:00')}"
        
        try:
            event_datetime = datetime.strptime(event_datetime_str, '%Y-%m-%d %H:%M')
        except:
            event_datetime = datetime.max
        
        # Calculer la distance temporelle (événements passés comptent comme très loin)
        if event_datetime < now:
            time_distance = float('inf')
        else:
            time_distance = (event_datetime - now).total_seconds()
        
        if title not in unique_events:
            unique_events[title] = (event, time_distance)
        else:
            # Garder celui le plus proche dans le futur
            existing_distance = unique_events[title][1]
            if time_distance < existing_distance:
                unique_events[title] = (event, time_distance)
    
    # Retourner les événements uniques, triés par date
    result = [e[0] for e in unique_events.values()]
    result.sort(key=lambda x: f"{x.get('date', '')} {x.get('start_time', '')}")
    return result


@app.route('/api/events', methods=['GET'])
def get_events():
    """
    Récupère les événements avec filtres optionnels.
    
    Query params:
        - categories: liste de catégories (comma-separated)
        - date_from: date minimum (YYYY-MM-DD)
        - date_to: date maximum (YYYY-MM-DD)
        - arrondissements: liste d'arrondissements (comma-separated)
        - price_max: prix maximum
        - time_of_day: jour, soir, nuit (comma-separated)
        - limit: nombre max de résultats (default 100)
        - offset: pagination offset
        - verified_only: true/false
        - unique: true/false - déduplique par titre (default true)
    """
    try:
        # Récupérer les paramètres
        categories = request.args.get('categories')
        if categories:
            categories = [c.strip() for c in categories.split(',')]
        
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        arrondissements = request.args.get('arrondissements')
        if arrondissements:
            arrondissements = [int(a.strip()) for a in arrondissements.split(',')]
        
        price_max = request.args.get('price_max')
        if price_max:
            price_max = float(price_max)
        
        time_of_day = request.args.get('time_of_day')
        if time_of_day:
            time_of_day = [t.strip() for t in time_of_day.split(',')]
        
        limit = int(request.args.get('limit', 500))  # Augmenté pour avoir plus de résultats avant déduplication
        offset = int(request.args.get('offset', 0))
        verified_only = request.args.get('verified_only', 'false').lower() == 'true'
        unique = request.args.get('unique', 'true').lower() == 'true'  # Par défaut: dédupliqué
        
        # Récupérer les événements
        events = db.get_events(
            categories=categories,
            date_from=date_from,
            date_to=date_to,
            arrondissements=arrondissements,
            price_max=price_max,
            time_of_day=time_of_day,
            limit=limit,
            offset=offset,
            verified_only=verified_only
        )
        
        # Dédupliquer si demandé
        if unique:
            events = deduplicate_events(events)
        
        return jsonify({
            'success': True,
            'count': len(events),
            'events': events,
            'filters': {
                'categories': categories,
                'date_from': date_from,
                'date_to': date_to,
                'arrondissements': arrondissements,
                'price_max': price_max,
                'time_of_day': time_of_day,
                'unique': unique,
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id: str):
    """Récupère un événement par son ID."""
    try:
        event = db.get_event(event_id)
        
        if event:
            return jsonify({
                'success': True,
                'event': event
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Événement non trouvé'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/events/upcoming', methods=['GET'])
def get_upcoming_events():
    """Récupère les événements à venir."""
    try:
        days = int(request.args.get('days', 30))
        limit = int(request.args.get('limit', 50))
        
        events = db.get_upcoming_events(days=days, limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(events),
            'events': events
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/events/search', methods=['GET'])
def search_events():
    """Recherche textuelle dans les événements."""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 50))
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Paramètre q requis'
            }), 400
        
        events = db.search_events(query, limit=limit)
        
        return jsonify({
            'success': True,
            'query': query,
            'count': len(events),
            'events': events
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/events/stats', methods=['GET'])
def get_stats():
    """Retourne les statistiques de la base de données."""
    try:
        stats = db.get_statistics()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/events/categories', methods=['GET'])
def get_categories():
    """Retourne la liste des catégories disponibles."""
    categories = {
        'spectacles': {
            'label': 'Spectacles',
            'emoji': '🎭',
            'subCategories': ['theatre', 'danse', 'opera', 'cirque', 'humour']
        },
        'musique': {
            'label': 'Musique',
            'emoji': '🎵',
            'subCategories': ['concert', 'jazz', 'classique', 'electro', 'rock', 'rap']
        },
        'arts_visuels': {
            'label': 'Arts Visuels',
            'emoji': '🎨',
            'subCategories': ['exposition', 'musee', 'galerie', 'photo', 'street_art']
        },
        'ateliers': {
            'label': 'Ateliers',
            'emoji': '🖌️',
            'subCategories': ['cuisine', 'art', 'artisanat', 'bien_etre']
        },
        'sport': {
            'label': 'Sport',
            'emoji': '🏃',
            'subCategories': ['running', 'yoga', 'escalade', 'velo', 'collectif']
        },
        'gastronomie': {
            'label': 'Gastronomie',
            'emoji': '🍷',
            'subCategories': ['degustation', 'brunch', 'cours_cuisine', 'food_market']
        },
        'culture': {
            'label': 'Culture',
            'emoji': '📚',
            'subCategories': ['cinema', 'conference', 'lecture', 'visite_guidee']
        },
        'nightlife': {
            'label': 'Vie Nocturne',
            'emoji': '🌙',
            'subCategories': ['club', 'bar', 'rooftop', 'speakeasy']
        },
        'rencontres': {
            'label': 'Rencontres',
            'emoji': '👥',
            'subCategories': ['meetup', 'networking', 'speed_dating', 'afterwork']
        }
    }
    
    return jsonify({
        'success': True,
        'categories': categories
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérifie que l'API fonctionne."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'database': 'real_events.db',
        'events_count': db.count_events()
    })


if __name__ == '__main__':
    print("🎭 Artify Events API")
    print(f"📊 {db.count_events()} événements en base")
    print("🚀 Démarrage sur http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)

