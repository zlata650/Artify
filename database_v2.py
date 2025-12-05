"""
🎭 Artify - Base de données enrichie v2
Gestion des événements avec catégories complètes
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
import json


class ArtifyDatabase:
    """
    Base de données enrichie pour Artify.
    Gère les événements, lieux et catégories.
    """
    
    def __init__(self, db_path: str = 'artify.db'):
        """Initialise la connexion à la base de données."""
        self.db_path = db_path
        self.conn = None
        self._create_tables()
    
    def _connect(self) -> sqlite3.Cursor:
        """Établit la connexion et retourne un curseur."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn.cursor()
    
    def _close(self):
        """Ferme la connexion."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def _create_tables(self):
        """Crée les tables si elles n'existent pas."""
        cursor = self._connect()
        
        # Table des lieux
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS venues (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                address TEXT NOT NULL,
                arrondissement INTEGER CHECK(arrondissement BETWEEN 1 AND 20),
                lat REAL,
                lng REAL,
                metro TEXT,  -- JSON array
                website TEXT,
                phone TEXT,
                categories TEXT,  -- JSON array
                description TEXT,
                image TEXT,
                capacity INTEGER,
                rating REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des événements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                slug TEXT NOT NULL,
                
                -- Classification
                main_category TEXT NOT NULL,
                sub_category TEXT NOT NULL,
                tags TEXT,  -- JSON array
                
                -- Timing
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                time_of_day TEXT NOT NULL,
                duration INTEGER,
                
                -- Location
                venue_id TEXT,
                venue_name TEXT NOT NULL,
                address TEXT NOT NULL,
                arrondissement INTEGER CHECK(arrondissement BETWEEN 1 AND 20),
                lat REAL,
                lng REAL,
                metro TEXT,  -- JSON array
                
                -- Pricing
                price REAL DEFAULT 0,
                price_max REAL,
                budget TEXT NOT NULL,
                booking_required INTEGER DEFAULT 1,
                booking_url TEXT,
                
                -- Details
                description TEXT NOT NULL,
                short_description TEXT,
                ambiance TEXT,  -- JSON array
                
                -- Media
                image TEXT,
                images TEXT,  -- JSON array
                
                -- Source
                source_url TEXT NOT NULL,
                source_name TEXT DEFAULT 'Artify',
                
                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                featured INTEGER DEFAULT 0,
                verified INTEGER DEFAULT 0,
                
                FOREIGN KEY (venue_id) REFERENCES venues(id)
            )
        ''')
        
        # Index pour les recherches fréquentes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_date ON events(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_category ON events(main_category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_arrondissement ON events(arrondissement)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_budget ON events(budget)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_time ON events(time_of_day)')
        
        # Table pour les sources de scraping
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                category TEXT NOT NULL,
                scraper_type TEXT NOT NULL,
                frequency TEXT DEFAULT 'daily',
                last_scraped TIMESTAMP,
                events_count INTEGER DEFAULT 0,
                active INTEGER DEFAULT 1,
                config TEXT  -- JSON config
            )
        ''')
        
        # Table pour les statistiques
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                event_count INTEGER,
                avg_price REAL,
                free_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        self._close()
    
    # =========================================================================
    # ÉVÉNEMENTS
    # =========================================================================
    
    def add_event(self, event: Dict[str, Any]) -> bool:
        """
        Ajoute un événement à la base de données.
        
        Args:
            event: Dictionnaire contenant les données de l'événement
            
        Returns:
            True si ajouté, False si déjà existant
        """
        cursor = self._connect()
        
        # Sérialiser les listes en JSON
        tags = json.dumps(event.get('tags', []))
        metro = json.dumps(event.get('metro', []))
        ambiance = json.dumps(event.get('ambiance', []))
        images = json.dumps(event.get('images', []))
        
        try:
            cursor.execute('''
                INSERT INTO events (
                    id, title, slug, main_category, sub_category, tags,
                    date, start_time, end_time, time_of_day, duration,
                    venue_id, venue_name, address, arrondissement, lat, lng, metro,
                    price, price_max, budget, booking_required, booking_url,
                    description, short_description, ambiance,
                    image, images, source_url, source_name,
                    featured, verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event['id'],
                event['title'],
                event.get('slug', self._generate_slug(event['title'])),
                event['main_category'],
                event['sub_category'],
                tags,
                event['date'],
                event['start_time'],
                event.get('end_time'),
                event.get('time_of_day', 'soir'),
                event.get('duration'),
                event.get('venue_id'),
                event['venue'],
                event['address'],
                event.get('arrondissement', 1),
                event.get('lat'),
                event.get('lng'),
                metro,
                event.get('price', 0),
                event.get('price_max'),
                event.get('budget', self._price_to_budget(event.get('price', 0))),
                1 if event.get('booking_required', True) else 0,
                event.get('booking_url'),
                event['description'],
                event.get('short_description', event['description'][:100] + '...' if len(event['description']) > 100 else event['description']),
                ambiance,
                event.get('image'),
                images,
                event['source_url'],
                event.get('source_name', 'Artify'),
                1 if event.get('featured', False) else 0,
                1 if event.get('verified', False) else 0,
            ))
            self.conn.commit()
            self._close()
            return True
        except sqlite3.IntegrityError:
            self._close()
            return False
    
    def add_events_batch(self, events: List[Dict[str, Any]]) -> int:
        """
        Ajoute plusieurs événements en une seule transaction.
        
        Returns:
            Nombre d'événements ajoutés
        """
        added = 0
        for event in events:
            if self.add_event(event):
                added += 1
        return added
    
    def get_events(
        self,
        categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None,
        budgets: Optional[List[str]] = None,
        times: Optional[List[str]] = None,
        arrondissements: Optional[List[int]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        search: Optional[str] = None,
        free_only: bool = False,
        featured_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Récupère des événements avec filtres.
        """
        cursor = self._connect()
        
        query = "SELECT * FROM events WHERE 1=1"
        params = []
        
        if categories:
            placeholders = ','.join(['?' for _ in categories])
            query += f" AND main_category IN ({placeholders})"
            params.extend(categories)
        
        if sub_categories:
            placeholders = ','.join(['?' for _ in sub_categories])
            query += f" AND sub_category IN ({placeholders})"
            params.extend(sub_categories)
        
        if budgets:
            placeholders = ','.join(['?' for _ in budgets])
            query += f" AND budget IN ({placeholders})"
            params.extend(budgets)
        
        if times:
            placeholders = ','.join(['?' for _ in times])
            query += f" AND time_of_day IN ({placeholders})"
            params.extend(times)
        
        if arrondissements:
            placeholders = ','.join(['?' for _ in arrondissements])
            query += f" AND arrondissement IN ({placeholders})"
            params.extend(arrondissements)
        
        if date_from:
            query += " AND date >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND date <= ?"
            params.append(date_to)
        
        if search:
            query += " AND (title LIKE ? OR description LIKE ? OR venue_name LIKE ?)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        if free_only:
            query += " AND price = 0"
        
        if featured_only:
            query += " AND featured = 1"
        
        query += " ORDER BY date ASC, start_time ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        self._close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un événement par son ID."""
        cursor = self._connect()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        self._close()
        return self._row_to_dict(row) if row else None
    
    def search_events(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Recherche textuelle dans les événements."""
        return self.get_events(search=query, limit=limit)
    
    def get_upcoming_events(self, days: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
        """Récupère les événements des X prochains jours."""
        from datetime import timedelta
        today = datetime.now().strftime('%Y-%m-%d')
        future = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        return self.get_events(date_from=today, date_to=future, limit=limit)
    
    def get_events_by_category(self, category: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Récupère les événements d'une catégorie."""
        return self.get_events(categories=[category], limit=limit)
    
    def count_events(self, **filters) -> int:
        """Compte les événements avec les mêmes filtres que get_events."""
        events = self.get_events(limit=10000, **filters)
        return len(events)
    
    # =========================================================================
    # LIEUX
    # =========================================================================
    
    def add_venue(self, venue: Dict[str, Any]) -> bool:
        """Ajoute un lieu."""
        cursor = self._connect()
        
        metro = json.dumps(venue.get('metro', []))
        categories = json.dumps(venue.get('categories', []))
        
        try:
            cursor.execute('''
                INSERT INTO venues (
                    id, name, slug, address, arrondissement,
                    lat, lng, metro, website, phone,
                    categories, description, image, capacity, rating
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                venue['id'],
                venue['name'],
                venue.get('slug', self._generate_slug(venue['name'])),
                venue['address'],
                venue.get('arrondissement', 1),
                venue.get('lat'),
                venue.get('lng'),
                metro,
                venue.get('website'),
                venue.get('phone'),
                categories,
                venue.get('description'),
                venue.get('image'),
                venue.get('capacity'),
                venue.get('rating'),
            ))
            self.conn.commit()
            self._close()
            return True
        except sqlite3.IntegrityError:
            self._close()
            return False
    
    def get_venues(self, category: Optional[str] = None, arrondissement: Optional[int] = None) -> List[Dict[str, Any]]:
        """Récupère les lieux avec filtres optionnels."""
        cursor = self._connect()
        
        query = "SELECT * FROM venues WHERE 1=1"
        params = []
        
        if category:
            query += " AND categories LIKE ?"
            params.append(f'%"{category}"%')
        
        if arrondissement:
            query += " AND arrondissement = ?"
            params.append(arrondissement)
        
        query += " ORDER BY name ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        self._close()
        
        return [self._row_to_dict(row) for row in rows]
    
    # =========================================================================
    # STATISTIQUES
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques globales."""
        cursor = self._connect()
        
        stats = {}
        
        # Nombre total d'événements
        cursor.execute("SELECT COUNT(*) FROM events")
        stats['total_events'] = cursor.fetchone()[0]
        
        # Par catégorie
        cursor.execute("""
            SELECT main_category, COUNT(*) as count 
            FROM events 
            GROUP BY main_category 
            ORDER BY count DESC
        """)
        stats['by_category'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Événements gratuits
        cursor.execute("SELECT COUNT(*) FROM events WHERE price = 0")
        stats['free_events'] = cursor.fetchone()[0]
        
        # Prix moyen
        cursor.execute("SELECT AVG(price) FROM events WHERE price > 0")
        avg = cursor.fetchone()[0]
        stats['avg_price'] = round(avg, 2) if avg else 0
        
        # Par arrondissement
        cursor.execute("""
            SELECT arrondissement, COUNT(*) as count 
            FROM events 
            GROUP BY arrondissement 
            ORDER BY arrondissement
        """)
        stats['by_arrondissement'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Par moment de la journée
        cursor.execute("""
            SELECT time_of_day, COUNT(*) as count 
            FROM events 
            GROUP BY time_of_day
        """)
        stats['by_time'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Nombre de lieux
        cursor.execute("SELECT COUNT(*) FROM venues")
        stats['total_venues'] = cursor.fetchone()[0]
        
        self._close()
        return stats
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convertit une row SQLite en dictionnaire."""
        d = dict(row)
        # Désérialiser les champs JSON
        for field in ['tags', 'metro', 'ambiance', 'images', 'categories']:
            if field in d and d[field]:
                try:
                    d[field] = json.loads(d[field])
                except json.JSONDecodeError:
                    d[field] = []
        return d
    
    def _generate_slug(self, title: str) -> str:
        """Génère un slug à partir d'un titre."""
        import re
        slug = title.lower()
        replacements = {
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'â': 'a', 'ä': 'a',
            'ù': 'u', 'û': 'u', 'ü': 'u',
            'î': 'i', 'ï': 'i',
            'ô': 'o', 'ö': 'o',
            'ç': 'c', 'ñ': 'n',
        }
        for old, new in replacements.items():
            slug = slug.replace(old, new)
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug.strip('-')
    
    def _price_to_budget(self, price: float) -> str:
        """Convertit un prix en catégorie de budget."""
        if price == 0:
            return 'gratuit'
        elif price <= 20:
            return '0-20'
        elif price <= 50:
            return '20-50'
        elif price <= 100:
            return '50-100'
        else:
            return '100+'
    
    def clear_all(self):
        """Supprime toutes les données (attention!)."""
        cursor = self._connect()
        cursor.execute("DELETE FROM events")
        cursor.execute("DELETE FROM venues")
        cursor.execute("DELETE FROM sources")
        cursor.execute("DELETE FROM stats")
        self.conn.commit()
        self._close()


# ============================================================================
# EXEMPLE D'UTILISATION
# ============================================================================

if __name__ == "__main__":
    db = ArtifyDatabase()
    
    # Ajouter des événements de test
    test_events = [
        {
            'id': 'test-001',
            'title': 'Concert Jazz au Sunset',
            'main_category': 'musique',
            'sub_category': 'jazz',
            'date': '2024-12-15',
            'start_time': '21:00',
            'venue': 'Sunset-Sunside',
            'address': '60 Rue des Lombards',
            'arrondissement': 1,
            'price': 28,
            'description': 'Soirée jazz intimiste avec le quartet de Thomas Dutronc.',
            'source_url': 'https://sunset-sunside.com',
            'ambiance': ['intime', 'culturel'],
        },
        {
            'id': 'test-002',
            'title': 'Atelier Céramique',
            'main_category': 'ateliers',
            'sub_category': 'ceramique',
            'date': '2024-12-16',
            'start_time': '14:00',
            'venue': 'Clementine Studio',
            'address': '15 Rue de la Fontaine au Roi',
            'arrondissement': 11,
            'price': 75,
            'description': 'Apprenez les bases du tournage. Repartez avec votre création.',
            'source_url': 'https://clementinestudio.com',
            'ambiance': ['creatif'],
        },
        {
            'id': 'test-003',
            'title': 'Stand-up Comedy Night',
            'main_category': 'spectacles',
            'sub_category': 'stand_up',
            'date': '2024-12-17',
            'start_time': '21:00',
            'venue': 'Comedy Club',
            'address': '42 Boulevard Bonne Nouvelle',
            'arrondissement': 10,
            'price': 18,
            'description': '5 humoristes, 15 minutes chacun. Les nouveaux talents de la scène.',
            'source_url': 'https://comedyclub.fr',
            'ambiance': ['festif'],
        },
    ]
    
    added = db.add_events_batch(test_events)
    print(f"✅ {added} événements ajoutés")
    
    # Statistiques
    stats = db.get_stats()
    print(f"\n📊 Statistiques:")
    print(f"   Total: {stats['total_events']} événements")
    print(f"   Gratuits: {stats['free_events']}")
    print(f"   Prix moyen: {stats['avg_price']}€")
    print(f"\n   Par catégorie:")
    for cat, count in stats['by_category'].items():
        print(f"      {cat}: {count}")
    
    # Recherche
    print(f"\n🔍 Recherche 'jazz':")
    results = db.search_events('jazz')
    for event in results:
        print(f"   - {event['title']} ({event['venue_name']})")


