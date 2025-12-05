"""
API Admin pour le Dashboard de Parsing
Gère les scripts de parsing, les statistiques et la planification des tâches
"""

import sqlite3
import json
import subprocess
import threading
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
import schedule
import time
from extract_concerts import extract_concerts_from_url, remove_duplicates
from database import ConcertDatabase

app = Flask(__name__)
CORS(app)

# Base de données pour les logs et statistiques
ADMIN_DB = 'admin_stats.db'

# Sources de données configurées
DATA_SOURCES = [
    {
        "id": "sortiraparis",
        "name": "Sortir à Paris",
        "url": "https://www.sortiraparis.com/",
        "filter_keyword": "concert",
        "enabled": True
    },
    {
        "id": "fnac_spectacles",
        "name": "Fnac Spectacles",
        "url": "https://www.fnacspectacles.com/",
        "filter_keyword": "concert",
        "enabled": False
    },
    {
        "id": "ticketmaster",
        "name": "Ticketmaster",
        "url": "https://www.ticketmaster.fr/",
        "filter_keyword": "concert",
        "enabled": False
    }
]

# État du scheduler
scheduler_running = False
scheduler_thread = None


def init_admin_db():
    """Initialise la base de données admin pour les statistiques."""
    conn = sqlite3.connect(ADMIN_DB)
    cursor = conn.cursor()
    
    # Table des logs de parsing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parsing_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL,
            source_name TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            concerts_found INTEGER DEFAULT 0,
            concerts_added INTEGER DEFAULT 0,
            duration_seconds REAL DEFAULT 0,
            status TEXT DEFAULT 'success',
            error_message TEXT
        )
    ''')
    
    # Table des tâches planifiées
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL,
            schedule_type TEXT NOT NULL,
            schedule_time TEXT,
            enabled BOOLEAN DEFAULT 1,
            last_run DATETIME,
            next_run DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des statistiques quotidiennes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE UNIQUE NOT NULL,
            total_concerts INTEGER DEFAULT 0,
            new_concerts INTEGER DEFAULT 0,
            sources_parsed INTEGER DEFAULT 0,
            parsing_errors INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()


def run_parsing(source_id=None):
    """
    Exécute le parsing pour une source ou toutes les sources.
    
    Args:
        source_id: ID de la source à parser (None = toutes les sources)
    
    Returns:
        dict avec les résultats du parsing
    """
    results = []
    db = ConcertDatabase('concerts.db')
    
    sources_to_parse = DATA_SOURCES if source_id is None else [
        s for s in DATA_SOURCES if s['id'] == source_id
    ]
    
    for source in sources_to_parse:
        if not source['enabled'] and source_id is None:
            continue
            
        start_time = time.time()
        try:
            # Extraction des concerts
            concerts = extract_concerts_from_url(
                source['url'], 
                filter_keyword=source['filter_keyword']
            )
            concerts_uniques = remove_duplicates(concerts)
            
            # Sauvegarde dans la base
            added = db.add_concerts_batch(concerts_uniques)
            duration = time.time() - start_time
            
            # Log du résultat
            log_parsing_result(
                source_id=source['id'],
                source_name=source['name'],
                concerts_found=len(concerts_uniques),
                concerts_added=added,
                duration=duration,
                status='success'
            )
            
            results.append({
                'source_id': source['id'],
                'source_name': source['name'],
                'concerts_found': len(concerts_uniques),
                'concerts_added': added,
                'duration': round(duration, 2),
                'status': 'success'
            })
            
        except Exception as e:
            duration = time.time() - start_time
            log_parsing_result(
                source_id=source['id'],
                source_name=source['name'],
                concerts_found=0,
                concerts_added=0,
                duration=duration,
                status='error',
                error_message=str(e)
            )
            
            results.append({
                'source_id': source['id'],
                'source_name': source['name'],
                'concerts_found': 0,
                'concerts_added': 0,
                'duration': round(duration, 2),
                'status': 'error',
                'error': str(e)
            })
    
    # Mettre à jour les statistiques quotidiennes
    update_daily_stats()
    
    return results


def log_parsing_result(source_id, source_name, concerts_found, concerts_added, 
                       duration, status, error_message=None):
    """Enregistre les résultats d'un parsing dans les logs."""
    conn = sqlite3.connect(ADMIN_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO parsing_logs 
        (source_id, source_name, concerts_found, concerts_added, duration_seconds, status, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (source_id, source_name, concerts_found, concerts_added, duration, status, error_message))
    
    conn.commit()
    conn.close()


def update_daily_stats():
    """Met à jour les statistiques quotidiennes."""
    conn = sqlite3.connect(ADMIN_DB)
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Calculer les stats du jour
    cursor.execute('''
        SELECT 
            COALESCE(SUM(concerts_found), 0) as total_found,
            COALESCE(SUM(concerts_added), 0) as total_added,
            COUNT(DISTINCT source_id) as sources_count,
            SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors
        FROM parsing_logs 
        WHERE DATE(timestamp) = ?
    ''', (today,))
    
    stats = cursor.fetchone()
    
    # Obtenir le total des concerts
    db = ConcertDatabase('concerts.db')
    total_concerts = db.count_concerts()
    
    cursor.execute('''
        INSERT OR REPLACE INTO daily_stats 
        (date, total_concerts, new_concerts, sources_parsed, parsing_errors)
        VALUES (?, ?, ?, ?, ?)
    ''', (today, total_concerts, stats[1], stats[2], stats[3]))
    
    conn.commit()
    conn.close()


def get_stats_by_period(period='day'):
    """
    Récupère les statistiques par période.
    
    Args:
        period: 'day', 'week', 'month'
    
    Returns:
        dict avec les statistiques
    """
    conn = sqlite3.connect(ADMIN_DB)
    cursor = conn.cursor()
    
    if period == 'day':
        date_filter = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT * FROM daily_stats WHERE date = ?
        ''', (date_filter,))
    elif period == 'week':
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT 
                'week' as date,
                COALESCE(SUM(total_concerts), 0) / COUNT(*) as avg_total,
                COALESCE(SUM(new_concerts), 0) as new_concerts,
                COALESCE(SUM(sources_parsed), 0) as sources_parsed,
                COALESCE(SUM(parsing_errors), 0) as errors
            FROM daily_stats 
            WHERE date >= ?
        ''', (week_ago,))
    else:  # month
        month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT 
                'month' as date,
                COALESCE(SUM(total_concerts), 0) / COUNT(*) as avg_total,
                COALESCE(SUM(new_concerts), 0) as new_concerts,
                COALESCE(SUM(sources_parsed), 0) as sources_parsed,
                COALESCE(SUM(parsing_errors), 0) as errors
            FROM daily_stats 
            WHERE date >= ?
        ''', (month_ago,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'period': period,
            'total_concerts': result[1] if result[1] else 0,
            'new_concerts': result[2] if result[2] else 0,
            'sources_parsed': result[3] if result[3] else 0,
            'parsing_errors': result[4] if result[4] else 0
        }
    return None


def get_parsing_history(limit=50):
    """Récupère l'historique des parsings."""
    conn = sqlite3.connect(ADMIN_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, source_id, source_name, timestamp, concerts_found, 
               concerts_added, duration_seconds, status, error_message
        FROM parsing_logs 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        'id': row[0],
        'source_id': row[1],
        'source_name': row[2],
        'timestamp': row[3],
        'concerts_found': row[4],
        'concerts_added': row[5],
        'duration': row[6],
        'status': row[7],
        'error': row[8]
    } for row in rows]


def get_chart_data(days=7):
    """Récupère les données pour les graphiques."""
    conn = sqlite3.connect(ADMIN_DB)
    cursor = conn.cursor()
    
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    cursor.execute('''
        SELECT date, new_concerts, parsing_errors
        FROM daily_stats 
        WHERE date >= ?
        ORDER BY date ASC
    ''', (start_date,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        'date': row[0],
        'new_concerts': row[1],
        'errors': row[2]
    } for row in rows]


# ========== ROUTES API ==========

@app.route('/api/admin/status', methods=['GET'])
def get_status():
    """Retourne le statut général du système."""
    db = ConcertDatabase('concerts.db')
    
    return jsonify({
        'status': 'online',
        'total_concerts': db.count_concerts(),
        'sources': DATA_SOURCES,
        'scheduler_running': scheduler_running,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/admin/parse', methods=['POST'])
def trigger_parsing():
    """Déclenche le parsing manuellement."""
    data = request.get_json() or {}
    source_id = data.get('source_id')  # None = toutes les sources
    
    results = run_parsing(source_id)
    
    return jsonify({
        'success': True,
        'results': results,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/admin/sources', methods=['GET'])
def get_sources():
    """Retourne la liste des sources de données."""
    return jsonify({
        'sources': DATA_SOURCES
    })


@app.route('/api/admin/sources/<source_id>/toggle', methods=['POST'])
def toggle_source(source_id):
    """Active/désactive une source."""
    for source in DATA_SOURCES:
        if source['id'] == source_id:
            source['enabled'] = not source['enabled']
            return jsonify({
                'success': True,
                'source': source
            })
    
    return jsonify({'success': False, 'error': 'Source not found'}), 404


@app.route('/api/admin/stats', methods=['GET'])
def get_all_stats():
    """Retourne toutes les statistiques."""
    period = request.args.get('period', 'day')
    
    return jsonify({
        'stats': get_stats_by_period(period),
        'today': get_stats_by_period('day'),
        'week': get_stats_by_period('week'),
        'month': get_stats_by_period('month')
    })


@app.route('/api/admin/history', methods=['GET'])
def get_history():
    """Retourne l'historique des parsings."""
    limit = request.args.get('limit', 50, type=int)
    
    return jsonify({
        'history': get_parsing_history(limit)
    })


@app.route('/api/admin/charts', methods=['GET'])
def get_charts():
    """Retourne les données pour les graphiques."""
    days = request.args.get('days', 7, type=int)
    
    return jsonify({
        'chart_data': get_chart_data(days)
    })


@app.route('/api/admin/concerts', methods=['GET'])
def get_concerts():
    """Retourne la liste des concerts."""
    db = ConcertDatabase('concerts.db')
    search = request.args.get('search', '')
    
    if search:
        concerts = db.search_concerts(search)
    else:
        concerts = db.get_all_concerts()
    
    return jsonify({
        'concerts': [{
            'id': c[0],
            'url': c[1],
            'name': c[2],
            'date_added': c[3]
        } for c in concerts[:100]],  # Limiter à 100
        'total': len(concerts)
    })


# ========== SCHEDULER ==========

def run_scheduler():
    """Boucle du scheduler."""
    global scheduler_running
    while scheduler_running:
        schedule.run_pending()
        time.sleep(60)  # Vérifier toutes les minutes


def start_scheduler():
    """Démarre le scheduler."""
    global scheduler_running, scheduler_thread
    
    if scheduler_running:
        return False
    
    scheduler_running = True
    
    # Programmer les tâches quotidiennes (à 6h du matin)
    schedule.every().day.at("06:00").do(lambda: run_parsing())
    
    # Programmer les tâches hebdomadaires (dimanche à minuit)
    schedule.every().sunday.at("00:00").do(lambda: run_parsing())
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    return True


def stop_scheduler():
    """Arrête le scheduler."""
    global scheduler_running
    scheduler_running = False
    schedule.clear()
    return True


@app.route('/api/admin/scheduler/start', methods=['POST'])
def api_start_scheduler():
    """Démarre le scheduler via l'API."""
    if start_scheduler():
        return jsonify({'success': True, 'message': 'Scheduler started'})
    return jsonify({'success': False, 'message': 'Scheduler already running'})


@app.route('/api/admin/scheduler/stop', methods=['POST'])
def api_stop_scheduler():
    """Arrête le scheduler via l'API."""
    if stop_scheduler():
        return jsonify({'success': True, 'message': 'Scheduler stopped'})
    return jsonify({'success': False, 'message': 'Scheduler not running'})


@app.route('/api/admin/scheduler/status', methods=['GET'])
def api_scheduler_status():
    """Retourne le statut du scheduler."""
    return jsonify({
        'running': scheduler_running,
        'jobs': [str(job) for job in schedule.get_jobs()]
    })


# Initialisation
init_admin_db()

if __name__ == '__main__':
    print("🚀 Admin API démarrée sur http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)



