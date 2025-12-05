"""
🎭 Artify - Base de données des événements réels
Database SQLite pour stocker les événements parisiens
"""

import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json


class MainCategory(str, Enum):
    """Catégories principales d'événements"""
    SPECTACLES = "spectacles"
    MUSIQUE = "musique"
    ARTS_VISUELS = "arts_visuels"
    ATELIERS = "ateliers"
    SPORT = "sport"
    GASTRONOMIE = "gastronomie"
    CULTURE = "culture"
    NIGHTLIFE = "nightlife"
    RENCONTRES = "rencontres"


class TimeOfDay(str, Enum):
    """Moment de la journée"""
    JOUR = "jour"
    SOIR = "soir"
    NUIT = "nuit"


@dataclass
class Event:
    """Structure d'un événement"""
    id: str
    title: str
    description: str
    main_category: str
    sub_category: Optional[str]
    date: str  # Format: YYYY-MM-DD
    start_time: Optional[str]  # Format: HH:MM
    end_time: Optional[str]
    time_of_day: str
    venue: str
    address: str
    arrondissement: Optional[int]
    price: float
    price_max: Optional[float]
    source_url: str
    source_name: str
    image_url: Optional[str]
    duration: Optional[int]  # En minutes
    booking_required: bool
    tags: List[str]
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: str
    updated_at: str
    verified: bool


class EventsDatabase:
    """Gère la base de données des événements réels."""
    
    def __init__(self, db_path: str = 'real_events.db'):
        """Initialise la connexion à la base de données."""
        self.db_path = db_path
        self.conn = None
        self._create_tables()
    
    def _connect(self) -> sqlite3.Cursor:
        """Établit la connexion à la base de données."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn.cursor()
    
    def _close(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def _create_tables(self):
        """Crée les tables si elles n'existent pas."""
        cursor = self._connect()
        
        # Table principale des événements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                main_category TEXT NOT NULL,
                sub_category TEXT,
                date TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                time_of_day TEXT NOT NULL,
                venue TEXT NOT NULL,
                address TEXT NOT NULL,
                arrondissement INTEGER,
                price REAL DEFAULT 0,
                price_max REAL,
                source_url TEXT NOT NULL,
                source_name TEXT NOT NULL,
                image_url TEXT,
                duration INTEGER,
                booking_required BOOLEAN DEFAULT FALSE,
                tags TEXT,
                latitude REAL,
                longitude REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Index pour les recherches fréquentes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_date ON events(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_category ON events(main_category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_arrondissement ON events(arrondissement)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_price ON events(price)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_time ON events(time_of_day)')
        
        # Table des sources de données
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                category TEXT,
                last_scraped TIMESTAMP,
                events_count INTEGER DEFAULT 0,
                active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Table de logs de scraping
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scrape_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                events_found INTEGER,
                events_added INTEGER,
                events_updated INTEGER,
                success BOOLEAN,
                error_message TEXT,
                FOREIGN KEY (source_id) REFERENCES sources(id)
            )
        ''')
        
        self.conn.commit()
        self._close()
    
    def add_event(self, event: Dict[str, Any]) -> bool:
        """
        Ajoute un événement à la base de données.
        
        Args:
            event: Dictionnaire avec les données de l'événement
            
        Returns:
            True si ajouté avec succès, False si déjà existant
        """
        cursor = self._connect()
        
        # Convertir les tags en JSON si c'est une liste
        if 'tags' in event and isinstance(event['tags'], list):
            event['tags'] = json.dumps(event['tags'])
        
        try:
            cursor.execute('''
                INSERT INTO events (
                    id, title, description, main_category, sub_category,
                    date, start_time, end_time, time_of_day,
                    venue, address, arrondissement,
                    price, price_max, source_url, source_name,
                    image_url, duration, booking_required, tags,
                    latitude, longitude, verified
                ) VALUES (
                    :id, :title, :description, :main_category, :sub_category,
                    :date, :start_time, :end_time, :time_of_day,
                    :venue, :address, :arrondissement,
                    :price, :price_max, :source_url, :source_name,
                    :image_url, :duration, :booking_required, :tags,
                    :latitude, :longitude, :verified
                )
            ''', event)
            self.conn.commit()
            self._close()
            return True
        except sqlite3.IntegrityError:
            # L'événement existe déjà
            self._close()
            return False
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> bool:
        """Met à jour un événement existant."""
        cursor = self._connect()
        
        # Construire la requête de mise à jour dynamiquement
        set_clauses = []
        values = {}
        for key, value in updates.items():
            if key != 'id':
                set_clauses.append(f"{key} = :{key}")
                values[key] = value
        
        values['id'] = event_id
        values['updated_at'] = datetime.now().isoformat()
        set_clauses.append("updated_at = :updated_at")
        
        query = f"UPDATE events SET {', '.join(set_clauses)} WHERE id = :id"
        
        cursor.execute(query, values)
        rows_affected = cursor.rowcount
        self.conn.commit()
        self._close()
        
        return rows_affected > 0
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un événement par son ID."""
        cursor = self._connect()
        cursor.execute('SELECT * FROM events WHERE id = ?', (event_id,))
        row = cursor.fetchone()
        self._close()
        
        if row:
            event = dict(row)
            if event.get('tags'):
                event['tags'] = json.loads(event['tags'])
            return event
        return None
    
    def get_events(
        self,
        categories: Optional[List[str]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        arrondissements: Optional[List[int]] = None,
        price_max: Optional[float] = None,
        time_of_day: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
        verified_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Récupère les événements avec filtres optionnels.
        """
        cursor = self._connect()
        
        query = "SELECT * FROM events WHERE 1=1"
        params = []
        
        if categories:
            placeholders = ','.join('?' * len(categories))
            query += f" AND main_category IN ({placeholders})"
            params.extend(categories)
        
        if date_from:
            query += " AND date >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND date <= ?"
            params.append(date_to)
        
        if arrondissements:
            placeholders = ','.join('?' * len(arrondissements))
            query += f" AND arrondissement IN ({placeholders})"
            params.extend(arrondissements)
        
        if price_max is not None:
            query += " AND price <= ?"
            params.append(price_max)
        
        if time_of_day:
            placeholders = ','.join('?' * len(time_of_day))
            query += f" AND time_of_day IN ({placeholders})"
            params.extend(time_of_day)
        
        if verified_only:
            query += " AND verified = 1"
        
        query += " ORDER BY date ASC, start_time ASC"
        query += f" LIMIT {limit} OFFSET {offset}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        self._close()
        
        events = []
        for row in rows:
            event = dict(row)
            if event.get('tags'):
                event['tags'] = json.loads(event['tags'])
            events.append(event)
        
        return events
    
    def get_upcoming_events(self, days: int = 30, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère les événements à venir."""
        today = date.today().isoformat()
        end_date = date.today()
        from datetime import timedelta
        end_date = (date.today() + timedelta(days=days)).isoformat()
        
        return self.get_events(date_from=today, date_to=end_date, limit=limit)
    
    def search_events(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Recherche textuelle dans les événements."""
        cursor = self._connect()
        
        search_query = f"%{query}%"
        cursor.execute('''
            SELECT * FROM events 
            WHERE title LIKE ? OR description LIKE ? OR venue LIKE ?
            ORDER BY date ASC
            LIMIT ?
        ''', (search_query, search_query, search_query, limit))
        
        rows = cursor.fetchall()
        self._close()
        
        events = []
        for row in rows:
            event = dict(row)
            if event.get('tags'):
                event['tags'] = json.loads(event['tags'])
            events.append(event)
        
        return events
    
    def delete_event(self, event_id: str) -> bool:
        """Supprime un événement."""
        cursor = self._connect()
        cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
        rows_affected = cursor.rowcount
        self.conn.commit()
        self._close()
        return rows_affected > 0
    
    def delete_past_events(self) -> int:
        """Supprime les événements passés."""
        cursor = self._connect()
        today = date.today().isoformat()
        cursor.execute('DELETE FROM events WHERE date < ?', (today,))
        rows_deleted = cursor.rowcount
        self.conn.commit()
        self._close()
        return rows_deleted
    
    def count_events(self, category: Optional[str] = None) -> int:
        """Compte le nombre d'événements."""
        cursor = self._connect()
        
        if category:
            cursor.execute('SELECT COUNT(*) FROM events WHERE main_category = ?', (category,))
        else:
            cursor.execute('SELECT COUNT(*) FROM events')
        
        count = cursor.fetchone()[0]
        self._close()
        return count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne des statistiques sur la base de données."""
        cursor = self._connect()
        
        # Total événements
        cursor.execute('SELECT COUNT(*) FROM events')
        total = cursor.fetchone()[0]
        
        # Par catégorie
        cursor.execute('''
            SELECT main_category, COUNT(*) as count 
            FROM events 
            GROUP BY main_category 
            ORDER BY count DESC
        ''')
        by_category = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Par arrondissement
        cursor.execute('''
            SELECT arrondissement, COUNT(*) as count 
            FROM events 
            WHERE arrondissement IS NOT NULL
            GROUP BY arrondissement 
            ORDER BY arrondissement
        ''')
        by_arrondissement = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Événements gratuits vs payants
        cursor.execute('SELECT COUNT(*) FROM events WHERE price = 0')
        free_count = cursor.fetchone()[0]
        
        # Prix moyen
        cursor.execute('SELECT AVG(price) FROM events WHERE price > 0')
        avg_price = cursor.fetchone()[0] or 0
        
        # Par moment de la journée
        cursor.execute('''
            SELECT time_of_day, COUNT(*) as count 
            FROM events 
            GROUP BY time_of_day
        ''')
        by_time = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Événements vérifiés
        cursor.execute('SELECT COUNT(*) FROM events WHERE verified = 1')
        verified_count = cursor.fetchone()[0]
        
        self._close()
        
        return {
            'total_events': total,
            'by_category': by_category,
            'by_arrondissement': by_arrondissement,
            'free_events': free_count,
            'paid_events': total - free_count,
            'average_price': round(avg_price, 2),
            'by_time_of_day': by_time,
            'verified_events': verified_count,
        }
    
    def add_batch(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Ajoute plusieurs événements en une seule transaction."""
        cursor = self._connect()
        added = 0
        updated = 0
        
        for event in events:
            # Convertir les tags en JSON si c'est une liste
            if 'tags' in event and isinstance(event['tags'], list):
                event['tags'] = json.dumps(event['tags'])
            
            try:
                cursor.execute('''
                    INSERT INTO events (
                        id, title, description, main_category, sub_category,
                        date, start_time, end_time, time_of_day,
                        venue, address, arrondissement,
                        price, price_max, source_url, source_name,
                        image_url, duration, booking_required, tags,
                        latitude, longitude, verified
                    ) VALUES (
                        :id, :title, :description, :main_category, :sub_category,
                        :date, :start_time, :end_time, :time_of_day,
                        :venue, :address, :arrondissement,
                        :price, :price_max, :source_url, :source_name,
                        :image_url, :duration, :booking_required, :tags,
                        :latitude, :longitude, :verified
                    )
                ''', event)
                added += 1
            except sqlite3.IntegrityError:
                # Événement existe, on le met à jour
                self.update_event(event['id'], event)
                updated += 1
        
        self.conn.commit()
        self._close()
        
        return {'added': added, 'updated': updated}
    
    def log_scrape(
        self,
        source_id: str,
        events_found: int,
        events_added: int,
        events_updated: int,
        success: bool,
        error_message: Optional[str] = None
    ):
        """Enregistre un log de scraping."""
        cursor = self._connect()
        cursor.execute('''
            INSERT INTO scrape_logs (
                source_id, events_found, events_added, 
                events_updated, success, error_message
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (source_id, events_found, events_added, events_updated, success, error_message))
        self.conn.commit()
        self._close()


# Export pour TypeScript/Next.js
def export_to_json(db: EventsDatabase, output_path: str = 'web/data/realEvents.json'):
    """Exporte les événements au format JSON pour le frontend."""
    events = db.get_upcoming_events(days=60, limit=500)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'events': events,
            'exported_at': datetime.now().isoformat(),
            'count': len(events)
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(events)} événements exportés vers {output_path}")


if __name__ == "__main__":
    # Test de la base de données
    db = EventsDatabase()
    
    print("📊 Statistiques de la base de données:")
    stats = db.get_statistics()
    print(f"  Total événements: {stats['total_events']}")
    print(f"  Événements gratuits: {stats['free_events']}")
    print(f"  Prix moyen: {stats['average_price']}€")
    
    if stats['by_category']:
        print("\n  Par catégorie:")
        for cat, count in stats['by_category'].items():
            print(f"    {cat}: {count}")


