import sqlite3
from extract_links import extract_links_from_url
from filter_links import filter_links_by_substring
from fetch_html import fetch_html


def init_database(db_path='concerts.db'):
    """
    Initialise la base de données avec la table appropriée.
    
    Args:
        db_path: Chemin vers la base de données SQLite
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Créer la table si elle n'existe pas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS concert_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            content TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


def url_exists_in_database(url, db_path='concerts.db'):
    """
    Vérifie si une URL existe déjà dans la base de données.
    
    Args:
        url: L'URL à vérifier
        db_path: Chemin vers la base de données SQLite
        
    Returns:
        True si l'URL existe, False sinon
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM concert_pages WHERE url = ?', (url,))
    count = cursor.fetchone()[0]
    
    conn.close()
    return count > 0


def save_concert_to_database(url, text_content, db_path='concerts.db'):
    """
    Sauvegarde une URL et son contenu textuel dans la base de données.
    
    Args:
        url: L'URL de la page
        text_content: Le contenu textuel extrait
        db_path: Chemin vers la base de données SQLite
        
    Returns:
        True si sauvegardé avec succès, False sinon
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO concert_pages (url, content) VALUES (?, ?)',
            (url, text_content)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # L'URL existe déjà
        conn.close()
        return False


def process_concert_links(base_url='https://www.sortiraparis.com/scenes/concert-musique', db_path='concerts.db'):
    """
    Fonction principale qui :
    1. Extrait tous les liens depuis l'URL de base
    2. Filtre les liens contenant '/concert-musique/'
    3. Vérifie si chaque lien existe dans la base de données
    4. Si le lien n'existe pas, récupère son contenu textuel et le sauvegarde
    
    Args:
        base_url: L'URL de base à analyser (par défaut: https://www.sortiraparis.com/scenes/concert-musique)
        db_path: Chemin vers la base de données SQLite
        
    Returns:
        Dict contenant les statistiques du traitement
    """
    # Initialiser la base de données
    print("Initialisation de la base de données...")
    init_database(db_path)
    
    # Étape 1: Extraire tous les liens
    print(f"Extraction des liens depuis {base_url}...")
    try:
        all_links = extract_links_from_url(base_url)
        print(f"✓ {len(all_links)} liens extraits")
    except Exception as e:
        print(f"✗ Erreur lors de l'extraction des liens : {e}")
        return {'error': str(e)}
    
    # Étape 2: Filtrer les liens contenant '/concert-musique/'
    print("Filtrage des liens contenant '/concert-musique/'...")
    concert_links = filter_links_by_substring(all_links, '/concert-musique/')
    print(f"✓ {len(concert_links)} liens de concerts trouvés")
    
    # Normaliser les liens relatifs en URLs absolues
    normalized_links = []
    for link in concert_links:
        if link.startswith('/'):
            # Ajouter le domaine pour les liens relatifs
            full_link = base_url.rstrip('/') + link
        elif link.startswith('http'):
            full_link = link
        else:
            # Ignorer les autres types de liens
            continue
        normalized_links.append(full_link)
    
    print(f"✓ {len(normalized_links)} liens normalisés")
    
    # Statistiques
    stats = {
        'total_links_found': len(all_links),
        'concert_links_found': len(concert_links),
        'normalized_links': len(normalized_links),
        'already_in_db': 0,
        'newly_added': 0,
        'failed': 0
    }
    
    # Étape 3 et 4: Vérifier et sauvegarder les nouveaux liens
    print("\nTraitement des liens...")
    for i, url in enumerate(normalized_links, 1):
        print(f"\n[{i}/{len(normalized_links)}] {url}")
        
        # Vérifier si l'URL existe déjà
        if url_exists_in_database(url, db_path):
            print("  → Déjà dans la base de données, ignoré")
            stats['already_in_db'] += 1
            continue
        
        # Récupérer le contenu textuel
        print("  → Récupération du contenu...")
        text_content = fetch_html(url, text_only=True)
        
        if text_content:
            # Sauvegarder dans la base de données
            if save_concert_to_database(url, text_content, db_path):
                print(f"  ✓ Sauvegardé ({len(text_content)} caractères)")
                stats['newly_added'] += 1
            else:
                print("  ✗ Échec de la sauvegarde")
                stats['failed'] += 1
        else:
            print("  ✗ Échec de la récupération du contenu")
            stats['failed'] += 1
    
    # Afficher le résumé
    print("\n" + "="*60)
    print("RÉSUMÉ")
    print("="*60)
    print(f"Total de liens extraits        : {stats['total_links_found']}")
    print(f"Liens de concerts trouvés      : {stats['concert_links_found']}")
    print(f"Liens normalisés               : {stats['normalized_links']}")
    print(f"Déjà dans la base de données   : {stats['already_in_db']}")
    print(f"Nouveaux liens ajoutés         : {stats['newly_added']}")
    print(f"Échecs                         : {stats['failed']}")
    print("="*60)
    
    return stats


# Exemple d'utilisation
if __name__ == "__main__":
    # Exécuter le processus complet
    results = process_concert_links()
    
    # Afficher les résultats
    print("\nTraitement terminé !")
    
    # Afficher quelques exemples de la base de données
    print("\nVérification de la base de données...")
    conn = sqlite3.connect('concerts.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM concert_pages')
    total = cursor.fetchone()[0]
    print(f"Total d'entrées dans la base : {total}")
    
    if total > 0:
        print("\nDernières entrées ajoutées :")
        cursor.execute('SELECT url, LENGTH(content), fetched_at FROM concert_pages ORDER BY fetched_at DESC LIMIT 5')
        for row in cursor.fetchall():
            print(f"  - {row[0]}")
            print(f"    Taille: {row[1]} caractères, Ajouté: {row[2]}")
    
    conn.close()

from extract_links import extract_links_from_url
from filter_links import filter_links_by_substring

START_URL = "https://www.sortiraparis.com/"
CONCERT_KEYWORDS = ["concert", "musique", "classique"]

def filter_by_keywords(links, keywords):
    """Return only links that contain at least one of the given keywords."""
    return [
        link for link in links
        if any(keyword.lower() in link.lower() for keyword in keywords)
    ]

def main():
    print(f"Fetching links from: {START_URL}")
    links = extract_links_from_url(START_URL)
    print(f"{len(links)} total links found.")

    concert_links = filter_by_keywords(links, CONCERT_KEYWORDS)
    print(f"{len(concert_links)} concert-related links found:\n")

    for link in concert_links:
        print(link)

if __name__ == "__main__":
    main()


