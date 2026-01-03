"""
Database module for Artify - SQLite database with event schema
"""
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import json


class EventsDB:
    """Database class for managing events, venues, and scrape statistics"""
    
    def __init__(self, db_path: str = "real_events.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                start_date TEXT NOT NULL,
                end_date TEXT,
                location TEXT NOT NULL,
                address TEXT,
                category TEXT,
                image_url TEXT,
                source_url TEXT UNIQUE,
                source_name TEXT,
                is_free INTEGER NOT NULL DEFAULT 0,
                price REAL,
                price_min REAL,
                price_max REAL,
                currency TEXT DEFAULT 'EUR',
                ticket_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Venues table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS venues (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                address TEXT,
                latitude REAL,
                longitude REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Scrape statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scrape_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                scrape_date TEXT NOT NULL,
                events_found INTEGER DEFAULT 0,
                events_added INTEGER DEFAULT 0,
                events_updated INTEGER DEFAULT 0,
                errors TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_start_date ON events(start_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_category ON events(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_is_free ON events(is_free)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_location ON events(location)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_source_url ON events(source_url)")
        
        conn.commit()
        conn.close()
    
    def add_event(self, event_data: Dict[str, Any]) -> bool:
        """Add or update an event. Returns True if added, False if updated"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if event exists by source_url
        existing = None
        if event_data.get('source_url'):
            cursor.execute("SELECT id FROM events WHERE source_url = ?", (event_data['source_url'],))
            existing = cursor.fetchone()
        
        event_id = event_data.get('id') or (existing[0] if existing else f"evt_{datetime.now().timestamp()}")
        
        # Prepare data
        now = datetime.now().isoformat()
        is_new = existing is None
        
        if is_new:
            cursor.execute("""
                INSERT INTO events (
                    id, title, description, start_date, end_date, location, address,
                    category, image_url, source_url, source_name,
                    is_free, price, price_min, price_max, currency, ticket_url,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                event_data.get('title'),
                event_data.get('description'),
                event_data.get('start_date'),
                event_data.get('end_date'),
                event_data.get('location'),
                event_data.get('address'),
                event_data.get('category'),
                event_data.get('image_url'),
                event_data.get('source_url'),
                event_data.get('source_name'),
                1 if event_data.get('is_free') else 0,
                event_data.get('price'),
                event_data.get('price_min'),
                event_data.get('price_max'),
                event_data.get('currency', 'EUR'),
                event_data.get('ticket_url'),
                now,
                now
            ))
        else:
            cursor.execute("""
                UPDATE events SET
                    title = ?, description = ?, start_date = ?, end_date = ?,
                    location = ?, address = ?, category = ?, image_url = ?,
                    is_free = ?, price = ?, price_min = ?, price_max = ?,
                    currency = ?, ticket_url = ?, updated_at = ?
                WHERE id = ?
            """, (
                event_data.get('title'),
                event_data.get('description'),
                event_data.get('start_date'),
                event_data.get('end_date'),
                event_data.get('location'),
                event_data.get('address'),
                event_data.get('category'),
                event_data.get('image_url'),
                1 if event_data.get('is_free') else 0,
                event_data.get('price'),
                event_data.get('price_min'),
                event_data.get('price_max'),
                event_data.get('currency', 'EUR'),
                event_data.get('ticket_url'),
                now,
                event_id
            ))
        
        conn.commit()
        conn.close()
        return is_new
    
    def get_events(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        category: Optional[str] = None,
        venue: Optional[str] = None,
        is_free: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get events with filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM events WHERE 1=1"
        params = []
        
        if date_from:
            query += " AND start_date >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND start_date <= ?"
            params.append(date_to)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if venue:
            query += " AND location LIKE ?"
            params.append(f"%{venue}%")
        
        if is_free is not None:
            query += " AND is_free = ?"
            params.append(1 if is_free else 0)
        
        query += " ORDER BY start_date ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        events = []
        for row in rows:
            event = dict(row)
            event['is_free'] = bool(event['is_free'])
            events.append(event)
        
        conn.close()
        return events
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a single event by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        
        if row:
            event = dict(row)
            event['is_free'] = bool(event['is_free'])
            conn.close()
            return event
        
        conn.close()
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total events
        cursor.execute("SELECT COUNT(*) FROM events")
        total_events = cursor.fetchone()[0]
        
        # Free events
        cursor.execute("SELECT COUNT(*) FROM events WHERE is_free = 1")
        free_events = cursor.fetchone()[0]
        
        # Events with ticket URL
        cursor.execute("SELECT COUNT(*) FROM events WHERE ticket_url IS NOT NULL AND ticket_url != ''")
        with_ticket_url = cursor.fetchone()[0]
        
        # Upcoming events (next 30 days)
        from datetime import datetime, timedelta
        future_date = (datetime.now() + timedelta(days=30)).isoformat()
        cursor.execute("SELECT COUNT(*) FROM events WHERE start_date >= datetime('now') AND start_date <= ?", (future_date,))
        upcoming_30_days = cursor.fetchone()[0]
        
        # By category
        cursor.execute("SELECT category, COUNT(*) FROM events WHERE category IS NOT NULL GROUP BY category")
        by_category = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total_events": total_events,
            "free_events": free_events,
            "with_ticket_url": with_ticket_url,
            "upcoming_30_days": upcoming_30_days,
            "by_category": by_category
        }
    
    def get_categories(self) -> List[str]:
        """Get list of all categories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT category FROM events WHERE category IS NOT NULL ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return categories
    
    def get_venues(self) -> List[str]:
        """Get list of all venues"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT location FROM events WHERE location IS NOT NULL ORDER BY location")
        venues = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return venues

