import sqlite3
from datetime import datetime


class ConcertDatabase:
    """Gère la base de données des concerts."""
    
    def __init__(self, db_path='concerts.db'):
        """Initialise la connexion à la base de données."""
        self.db_path = db_path
        self.conn = None
        self.create_table()
    
    def connect(self):
        """Établit la connexion à la base de données."""
        self.conn = sqlite3.connect(self.db_path)
        return self.conn.cursor()
    
    def close(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()
    
    def create_table(self):
        """Crée la table des concerts si elle n'existe pas."""
        cursor = self.connect()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS concerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                nom TEXT NOT NULL,
                date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        self.close()
    
    def add_concert(self, url, nom):
        """
        Ajoute un concert à la base de données.
        
        Args:
            url: L'URL du concert
            nom: Le nom/titre du concert
            
        Returns:
            True si ajouté avec succès, False si déjà existant
        """
        cursor = self.connect()
        try:
            cursor.execute(
                'INSERT INTO concerts (url, nom) VALUES (?, ?)',
                (url, nom)
            )
            self.conn.commit()
            self.close()
            return True
        except sqlite3.IntegrityError:
            # Le concert existe déjà (URL dupliquée)
            self.close()
            return False
    
    def add_concerts_batch(self, concerts):
        """
        Ajoute plusieurs concerts en une seule transaction.
        
        Args:
            concerts: Liste de tuples (url, nom)
            
        Returns:
            Nombre de concerts ajoutés
        """
        cursor = self.connect()
        added = 0
        for url, nom in concerts:
            try:
                cursor.execute(
                    'INSERT INTO concerts (url, nom) VALUES (?, ?)',
                    (url, nom)
                )
                added += 1
            except sqlite3.IntegrityError:
                # Concert déjà existant
                continue
        self.conn.commit()
        self.close()
        return added
    
    def get_all_concerts(self):
        """
        Récupère tous les concerts de la base de données.
        
        Returns:
            Liste de tuples (id, url, nom, date_ajout)
        """
        cursor = self.connect()
        cursor.execute('SELECT * FROM concerts ORDER BY date_ajout DESC')
        concerts = cursor.fetchall()
        self.close()
        return concerts
    
    def search_concerts(self, search_term):
        """
        Recherche des concerts par nom ou URL.
        
        Args:
            search_term: Terme à rechercher
            
        Returns:
            Liste de tuples (id, url, nom, date_ajout)
        """
        cursor = self.connect()
        cursor.execute(
            'SELECT * FROM concerts WHERE nom LIKE ? OR url LIKE ? ORDER BY date_ajout DESC',
            (f'%{search_term}%', f'%{search_term}%')
        )
        concerts = cursor.fetchall()
        self.close()
        return concerts
    
    def clear_all(self):
        """Supprime tous les concerts de la base de données."""
        cursor = self.connect()
        cursor.execute('DELETE FROM concerts')
        self.conn.commit()
        self.close()
    
    def count_concerts(self):
        """Retourne le nombre total de concerts dans la base."""
        cursor = self.connect()
        cursor.execute('SELECT COUNT(*) FROM concerts')
        count = cursor.fetchone()[0]
        self.close()
        return count


# Exemple d'utilisation
if __name__ == "__main__":
    db = ConcertDatabase()
    
    # Ajouter des concerts de test
    concerts_test = [
        ("https://example.com/concert1", "Vald à la Defense Arena"),
        ("https://example.com/concert2", "Chris Isaak à la Seine Musicale"),
        ("https://example.com/concert3", "Whitney Houston Tribute")
    ]
    
    added = db.add_concerts_batch(concerts_test)
    print(f"{added} concerts ajoutés")
    
    # Afficher tous les concerts
    print("\nTous les concerts :")
    for concert in db.get_all_concerts():
        print(f"  {concert[0]}. {concert[2]} - {concert[1]}")
    
    print(f"\nTotal : {db.count_concerts()} concerts")





