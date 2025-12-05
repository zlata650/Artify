"""
🎭 Artify - Database Module
SQLite database management for events - compatible with existing schema
"""

import sqlite3
import json
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

from .models import UnifiedEvent


class EventsDB:
    """
    Database manager for events.
    Compatible with the existing real_events.db schema.
    """
    
    def __init__(self, db_path: str = None):
        """Initialize database connection."""
        self.db_path = db_path or os.environ.get('EVENTS_DB_PATH', 'real_events.db')
        self._ensure_tables()
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _ensure_tables(self):
        """Create tables if they don't exist (using existing schema)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if events table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
            if cursor.fetchone():
                # Table exists, just ensure indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_date ON events(date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_category ON events(main_category)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_source ON events(source_name)')
                return
            
            # Create events table with existing schema format
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
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_date ON events(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_category ON events(main_category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_arrondissement ON events(arrondissement)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_price ON events(price)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_time ON events(time_of_day)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_source ON events(source_name)')
            
            # Scrape logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scrape_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    events_found INTEGER DEFAULT 0,
                    events_added INTEGER DEFAULT 0,
                    events_updated INTEGER DEFAULT 0,
                    events_deduplicated INTEGER DEFAULT 0,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT,
                    duration_seconds REAL
                )
            ''')
    
    def _unified_to_db(self, event: UnifiedEvent) -> Dict:
        """Convert UnifiedEvent to database format (existing schema)."""
        tags = event.tags if isinstance(event.tags, list) else []
        
        return {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'main_category': event.category,
            'sub_category': event.sub_category,
            'date': event.date_start,
            'start_time': event.time_start,
            'end_time': event.time_end,
            'time_of_day': self._map_time_of_day(event.time_of_day),
            'venue': event.location_name,
            'address': event.address,
            'arrondissement': event.arrondissement,
            'price': event.price_from,
            'price_max': event.price_to,
            'source_url': event.ticket_url or event.source_event_url,
            'source_name': event.source_name,
            'image_url': event.image_url,
            'duration': None,
            'booking_required': event.has_direct_ticket_button,
            'tags': json.dumps(tags),
            'latitude': event.latitude,
            'longitude': event.longitude,
            'verified': event.verified,
        }
    
    def _map_time_of_day(self, time_of_day: str) -> str:
        """Map internal time_of_day to existing schema format."""
        mapping = {
            'matin': 'jour',
            'apres_midi': 'jour',
            'soir': 'soir',
            'nuit': 'nuit',
        }
        return mapping.get(time_of_day, 'jour')
    
    def upsert_event(self, event: UnifiedEvent) -> bool:
        """
        Insert or update an event.
        Returns True if inserted, False if updated.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute('SELECT id FROM events WHERE id = ?', (event.id,))
            exists = cursor.fetchone() is not None
            
            data = self._unified_to_db(event)
            
            if exists:
                # Update
                cursor.execute('''
                    UPDATE events SET
                        title = ?, description = ?, main_category = ?, sub_category = ?,
                        date = ?, start_time = ?, end_time = ?, time_of_day = ?,
                        venue = ?, address = ?, arrondissement = ?,
                        price = ?, price_max = ?, source_url = ?, source_name = ?,
                        image_url = ?, duration = ?, booking_required = ?, tags = ?,
                        latitude = ?, longitude = ?, updated_at = ?, verified = ?
                    WHERE id = ?
                ''', (
                    data['title'], data['description'], data['main_category'], data['sub_category'],
                    data['date'], data['start_time'], data['end_time'], data['time_of_day'],
                    data['venue'], data['address'], data['arrondissement'],
                    data['price'], data['price_max'], data['source_url'], data['source_name'],
                    data['image_url'], data['duration'], data['booking_required'], data['tags'],
                    data['latitude'], data['longitude'], datetime.now().isoformat(), data['verified'],
                    event.id
                ))
                return False
            else:
                # Insert
                cursor.execute('''
                    INSERT INTO events (
                        id, title, description, main_category, sub_category,
                        date, start_time, end_time, time_of_day,
                        venue, address, arrondissement,
                        price, price_max, source_url, source_name,
                        image_url, duration, booking_required, tags,
                        latitude, longitude, verified
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['id'], data['title'], data['description'], data['main_category'], data['sub_category'],
                    data['date'], data['start_time'], data['end_time'], data['time_of_day'],
                    data['venue'], data['address'], data['arrondissement'],
                    data['price'], data['price_max'], data['source_url'], data['source_name'],
                    data['image_url'], data['duration'], data['booking_required'], data['tags'],
                    data['latitude'], data['longitude'], data['verified']
                ))
                return True
    
    def upsert_batch(self, events: List[UnifiedEvent]) -> Dict[str, int]:
        """Insert or update multiple events."""
        added = 0
        updated = 0
        
        for event in events:
            if self.upsert_event(event):
                added += 1
            else:
                updated += 1
        
        return {'added': added, 'updated': updated}
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get an event by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM events WHERE id = ?', (event_id,))
            row = cursor.fetchone()
            
            if row:
                event = dict(row)
                if event.get('tags') and isinstance(event['tags'], str):
                    try:
                        event['tags'] = json.loads(event['tags'])
                    except:
                        event['tags'] = []
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
        source_name: Optional[str] = None,
        search_query: Optional[str] = None,
        has_ticket: Optional[bool] = None,
        verified_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get events with filters."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
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
                query += " AND (price <= ? OR price = 0)"
                params.append(price_max)
            
            if time_of_day:
                placeholders = ','.join('?' * len(time_of_day))
                query += f" AND time_of_day IN ({placeholders})"
                params.extend(time_of_day)
            
            if source_name:
                query += " AND source_name = ?"
                params.append(source_name)
            
            if search_query:
                query += " AND (title LIKE ? OR description LIKE ? OR venue LIKE ?)"
                search_pattern = f"%{search_query}%"
                params.extend([search_pattern, search_pattern, search_pattern])
            
            if has_ticket:
                query += " AND source_url IS NOT NULL AND source_url != ''"
            
            if verified_only:
                query += " AND verified = 1"
            
            query += " ORDER BY date ASC, start_time ASC"
            query += f" LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                event = dict(row)
                if event.get('tags') and isinstance(event['tags'], str):
                    try:
                        event['tags'] = json.loads(event['tags'])
                    except:
                        event['tags'] = []
                events.append(event)
            
            return events
    
    def count_events(self, category: Optional[str] = None) -> int:
        """Count events optionally filtered by category."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if category:
                cursor.execute('SELECT COUNT(*) FROM events WHERE main_category = ?', (category,))
            else:
                cursor.execute('SELECT COUNT(*) FROM events')
            
            return cursor.fetchone()[0]
    
    def delete_past_events(self, days_before_today: int = 0) -> int:
        """Delete events that have passed."""
        cutoff = (date.today() - timedelta(days=days_before_today)).isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM events WHERE date < ?', (cutoff,))
            return cursor.rowcount
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total events
            cursor.execute('SELECT COUNT(*) FROM events')
            total = cursor.fetchone()[0]
            
            # By category
            cursor.execute('''
                SELECT main_category, COUNT(*) as count 
                FROM events 
                GROUP BY main_category 
                ORDER BY count DESC
            ''')
            by_category = {row[0]: row[1] for row in cursor.fetchall()}
            
            # By source
            cursor.execute('''
                SELECT source_name, COUNT(*) as count 
                FROM events 
                GROUP BY source_name 
                ORDER BY count DESC
            ''')
            by_source = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Free vs paid
            cursor.execute('SELECT COUNT(*) FROM events WHERE price = 0')
            free_count = cursor.fetchone()[0]
            
            # Average price
            cursor.execute('SELECT AVG(price) FROM events WHERE price > 0')
            avg_price = cursor.fetchone()[0] or 0
            
            # With source URL
            cursor.execute("SELECT COUNT(*) FROM events WHERE source_url IS NOT NULL AND source_url != ''")
            with_ticket = cursor.fetchone()[0]
            
            # Upcoming events (next 30 days)
            future_date = (date.today() + timedelta(days=30)).isoformat()
            cursor.execute('SELECT COUNT(*) FROM events WHERE date >= ? AND date <= ?', 
                         (date.today().isoformat(), future_date))
            upcoming = cursor.fetchone()[0]
            
            return {
                'total_events': total,
                'by_category': by_category,
                'by_source': by_source,
                'free_events': free_count,
                'paid_events': total - free_count,
                'average_price': round(avg_price, 2),
                'with_ticket_url': with_ticket,
                'upcoming_30_days': upcoming,
            }
    
    def log_scrape(
        self,
        source_name: str,
        events_found: int,
        events_added: int,
        events_updated: int,
        events_deduplicated: int = 0,
        success: bool = True,
        error_message: Optional[str] = None,
        duration_seconds: Optional[float] = None
    ):
        """Log a scrape operation."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Ensure scrape_logs table exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scrape_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    events_found INTEGER DEFAULT 0,
                    events_added INTEGER DEFAULT 0,
                    events_updated INTEGER DEFAULT 0,
                    events_deduplicated INTEGER DEFAULT 0,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT,
                    duration_seconds REAL
                )
            ''')
            
            cursor.execute('''
                INSERT INTO scrape_logs (
                    source_name, events_found, events_added, 
                    events_updated, events_deduplicated, success, 
                    error_message, duration_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                source_name, events_found, events_added,
                events_updated, events_deduplicated, success,
                error_message, duration_seconds
            ))
    
    def get_scrape_logs(self, source_name: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get recent scrape logs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scrape_logs'")
            if not cursor.fetchone():
                return []
            
            if source_name:
                cursor.execute('''
                    SELECT * FROM scrape_logs 
                    WHERE source_name = ?
                    ORDER BY scraped_at DESC 
                    LIMIT ?
                ''', (source_name, limit))
            else:
                cursor.execute('''
                    SELECT * FROM scrape_logs 
                    ORDER BY scraped_at DESC 
                    LIMIT ?
                ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
            return cursor.rowcount > 0
