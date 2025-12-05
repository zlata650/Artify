"""
🎭 Artify - Events API
Flask API serving real Paris events from the database.

This API is compatible with the existing frontend expectations.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, date, timedelta
import json

from backend.core.db import EventsDB

app = Flask(__name__)
CORS(app, origins=[
    'http://localhost:3000',
    'http://localhost:3001', 
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001'
])

# Database instance
db = EventsDB('real_events.db')


def format_event_for_frontend(event: dict) -> dict:
    """
    Format an event for the frontend API response.
    Maps database schema to frontend expected format.
    """
    # Map time_of_day to frontend format
    time_of_day_map = {
        'matin': 'jour',
        'apres_midi': 'jour',
        'soir': 'soir',
        'nuit': 'nuit',
    }
    
    return {
        'id': event.get('id'),
        'title': event.get('title'),
        'description': event.get('description', ''),
        'main_category': event.get('category'),
        'sub_category': event.get('sub_category'),
        'date': event.get('date_start'),
        'start_time': event.get('time_start'),
        'end_time': event.get('time_end'),
        'time_of_day': time_of_day_map.get(event.get('time_of_day', 'soir'), 'jour'),
        'venue': event.get('location_name', ''),
        'address': event.get('address', ''),
        'arrondissement': event.get('arrondissement'),
        'price': event.get('price_from', 0),
        'price_max': event.get('price_to'),
        'source_url': event.get('ticket_url') or event.get('source_event_url'),
        'source_name': event.get('source_name', ''),
        'image_url': event.get('image_url'),
        'duration': None,
        'booking_required': event.get('has_direct_ticket_button', False),
        'tags': event.get('tags', []),
        'latitude': event.get('latitude'),
        'longitude': event.get('longitude'),
        'verified': event.get('verified', False),
    }


def deduplicate_events(events: list) -> list:
    """
    Deduplicate events by title, keeping the one with earliest upcoming date.
    """
    now = datetime.now()
    unique_events = {}
    
    for event in events:
        title = event.get('title', '')
        event_date_str = event.get('date') or event.get('date_start', '')
        event_time = event.get('start_time') or event.get('time_start', '00:00')
        
        try:
            event_datetime = datetime.strptime(f"{event_date_str} {event_time}", '%Y-%m-%d %H:%M')
        except:
            event_datetime = datetime.max
        
        # Calculate distance (past events are far away)
        if event_datetime < now:
            time_distance = float('inf')
        else:
            time_distance = (event_datetime - now).total_seconds()
        
        if title not in unique_events:
            unique_events[title] = (event, time_distance)
        else:
            if time_distance < unique_events[title][1]:
                unique_events[title] = (event, time_distance)
    
    result = [e[0] for e in unique_events.values()]
    result.sort(key=lambda x: f"{x.get('date', '')} {x.get('start_time', '')}")
    return result


@app.route('/api/events', methods=['GET'])
def get_events():
    """
    Get events with optional filters.
    
    Query params:
        - categories: comma-separated list of categories
        - date_from: start date (YYYY-MM-DD)
        - date_to: end date (YYYY-MM-DD)
        - arrondissements: comma-separated list of arrondissements
        - price_max: maximum price
        - time_of_day: comma-separated (jour, soir, nuit)
        - limit: max results (default 100)
        - offset: pagination offset
        - verified_only: true/false
        - unique: true/false - deduplicate by title (default true)
        - search: text search query
    """
    try:
        # Parse parameters
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
        
        search_query = request.args.get('search')
        
        limit = int(request.args.get('limit', 500))
        offset = int(request.args.get('offset', 0))
        verified_only = request.args.get('verified_only', 'false').lower() == 'true'
        unique = request.args.get('unique', 'true').lower() == 'true'
        
        # Query database
        events = db.get_events(
            categories=categories,
            date_from=date_from,
            date_to=date_to,
            arrondissements=arrondissements,
            price_max=price_max,
            time_of_day=time_of_day,
            search_query=search_query,
            verified_only=verified_only,
            limit=limit,
            offset=offset
        )
        
        # Format for frontend
        events = [format_event_for_frontend(e) for e in events]
        
        # Deduplicate if requested
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
    """Get a single event by ID."""
    try:
        event = db.get_event(event_id)
        
        if event:
            return jsonify({
                'success': True,
                'event': format_event_for_frontend(event)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/events/upcoming', methods=['GET'])
def get_upcoming_events():
    """Get upcoming events."""
    try:
        days = int(request.args.get('days', 30))
        limit = int(request.args.get('limit', 50))
        
        today = date.today().isoformat()
        end_date = (date.today() + timedelta(days=days)).isoformat()
        
        events = db.get_events(
            date_from=today,
            date_to=end_date,
            limit=limit
        )
        
        events = [format_event_for_frontend(e) for e in events]
        
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
    """Search events by text."""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 50))
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter q is required'
            }), 400
        
        events = db.get_events(search_query=query, limit=limit)
        events = [format_event_for_frontend(e) for e in events]
        
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
    """Get database statistics."""
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
    """Get available categories."""
    categories = {
        'spectacles': {
            'label': 'Spectacles',
            'emoji': '🎭',
            'subCategories': ['theatre', 'opera', 'ballet', 'danse', 'humour', 'cirque', 'cabaret']
        },
        'musique': {
            'label': 'Musique',
            'emoji': '🎵',
            'subCategories': ['classique', 'jazz', 'rock', 'pop', 'electro', 'rap', 'world']
        },
        'arts_visuels': {
            'label': 'Arts Visuels',
            'emoji': '🎨',
            'subCategories': ['exposition', 'musee', 'galerie', 'photographie', 'street_art']
        },
        'ateliers': {
            'label': 'Ateliers',
            'emoji': '🖌️',
            'subCategories': ['ceramique', 'peinture', 'dessin', 'sculpture', 'couture', 'cuisine']
        },
        'sport': {
            'label': 'Sport',
            'emoji': '🏃',
            'subCategories': ['yoga', 'fitness', 'running', 'escalade', 'velo']
        },
        'gastronomie': {
            'label': 'Gastronomie',
            'emoji': '🍷',
            'subCategories': ['degustation', 'brunch', 'cours_cuisine', 'food_market']
        },
        'culture': {
            'label': 'Culture',
            'emoji': '📚',
            'subCategories': ['cinema', 'conference', 'visite_guidee', 'lecture']
        },
        'nightlife': {
            'label': 'Vie Nocturne',
            'emoji': '🌙',
            'subCategories': ['club', 'bar', 'rooftop', 'speakeasy']
        },
        'rencontres': {
            'label': 'Rencontres',
            'emoji': '👥',
            'subCategories': ['meetup', 'networking', 'afterwork', 'speed_dating']
        }
    }
    
    return jsonify({
        'success': True,
        'categories': categories
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'database': 'real_events.db',
        'events_count': db.count_events()
    })


if __name__ == '__main__':
    print("🎭 Artify Events API")
    print(f"📊 {db.count_events()} events in database")
    print("🚀 Starting on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)

