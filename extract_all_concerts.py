from fetch_html import fetch_html
from extract_links import extract_links
from url_validator import clean_url, is_valid_event_url_pattern, is_sortiraparis_event_url
import os
import time


# URLs à explorer pour trouver des concerts
CONCERT_URLS = [
    "https://www.sortiraparis.com/scenes/concert-musique",
    "https://www.sortiraparis.com/scenes/concert-musique/guides/285571-musique-rock-prochains-concerts-paris-a-ne-pas-manquer",
    "https://www.sortiraparis.com/scenes/concert-musique/guides/309108-paris-concerts-artistes-internationaux-a-ne-pas-manquer",
    "https://www.sortiraparis.com/scenes/concert-musique/guides/309037-variete-francaise-prochains-concerts-a-ne-pas-manquer",
    "https://www.sortiraparis.com/scenes/concert-musique/guides/285538-artistes-francophones-les-prochains-concerts-a-paris-a-ne-pas-manquer",
    "https://www.sortiraparis.com/soiree",  # Soirées électro, clubs, etc.
]

# Définir les genres musicaux avec mots-clés
GENRES = {
    'classique': ['classique', 'symphonique', 'orchestre', 'opera', 'opéra', 'philharmonique', 'baroque', 'beethoven', 'mozart', 'bach', 'bocelli'],
    'jazz': ['jazz', 'blues', 'swing', 'bebop'],
    'dance': ['dance', 'edm', 'house', 'trance', 'drum-and-bass', 'hardstyle', 'skate', 'roller'],
    'pop': ['pop', 'k-pop', 'kpop', 'variete', 'variété', 'pink', 'louane', 'amir'],
    'techno': ['techno', 'electro', 'electronic', 'électro', 'rave', 'dub', 'dubstep', 'ambient', 'dj-set', 'guetta', 'daft', 'gesaffelstein', 'tiesto', 'calvin-harris', 'club', 'miamao', 'essaim'],
    'rock': ['rock', 'metal', 'punk', 'indie', 'grunge', 'alternative', 'hard-rock', 'metallica', 'guns', 'gojira', 'cure', 'indochine'],
    'rap': ['rap', 'hip-hop', 'hiphop', 'trap', 'gims', 'soprano', 'dinos', 'hamza'],
    'autre': []
}


def categorize_concert_by_keywords(url, title=""):
    """
    Catégorise un concert selon les mots-clés dans son URL ou titre
    """
    import re
    text = (url + " " + title).lower()
    
    # Attention : vérifier "pop-up" avant "pop" pour éviter les faux positifs
    if 'pop-up' in text or 'popup' in text:
        text = text.replace('pop-up', '').replace('popup', '')
    
    for genre, keywords in GENRES.items():
        if genre == 'autre':
            continue
        for keyword in keywords:
            # Utiliser des word boundaries pour éviter les faux positifs
            # Par exemple, "rap" ne doit pas matcher "paris"
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text):
                return genre
    
    return 'autre'


def extract_all_concerts():
    """
    Extrait tous les concerts de plusieurs pages et les catégorise
    """
    print("🎵 EXTRACTION COMPLÈTE DES CONCERTS 🎵")
    print("="*60)
    print()
    
    all_concert_urls = set()
    
    # Télécharger chaque page source
    for i, url in enumerate(CONCERT_URLS, 1):
        print(f"📥 [{i}/{len(CONCERT_URLS)}] Téléchargement de : {url}")
        
        # Utiliser text_only=False pour obtenir le HTML complet nécessaire à l'extraction des liens
        html_content = fetch_html(url, text_only=False)
        
        if not html_content:
            print(f"   ✗ Échec du téléchargement\n")
            continue
        
        # Extraire tous les liens
        all_links = extract_links(html_content)
        
        # Filtrer pour garder uniquement les articles de concerts et soirées
        concert_count = 0
        skipped_count = 0
        base_url = "https://www.sortiraparis.com"
        
        for link in all_links:
            if '/concert-musique/articles/' in link or '/scenes/concert' in link or '/soiree/articles/' in link:
                if link.startswith('/'):
                    full_url = f"{base_url}{link}"
                else:
                    full_url = link
                
                # Nettoyer l'URL
                cleaned_url = clean_url(full_url, base_url)
                
                if not cleaned_url:
                    skipped_count += 1
                    continue
                
                # Vérifier que c'est bien une page d'événement (article individuel)
                # Les articles ont le format: /xxx/articles/ID-titre
                if not is_sortiraparis_event_url(cleaned_url):
                    # Vérification alternative: doit contenir /articles/ avec un ID numérique
                    if '/articles/' not in cleaned_url:
                        skipped_count += 1
                        continue
                    
                    # Vérifier qu'il y a un ID numérique après /articles/
                    import re
                    if not re.search(r'/articles/\d+', cleaned_url):
                        skipped_count += 1
                        continue
                
                all_concert_urls.add(cleaned_url)
                concert_count += 1
        
        print(f"   ✓ {concert_count} liens de concerts validés")
        if skipped_count > 0:
            print(f"   ✗ {skipped_count} liens non-événements filtrés")
        print(f"   Total unique : {len(all_concert_urls)} concerts\n")
        
        # Petit délai pour ne pas surcharger le serveur
        time.sleep(1)
    
    print(f"✅ Total de {len(all_concert_urls)} concerts uniques trouvés\n")
    
    # Catégoriser les concerts
    concerts_by_genre = {genre: [] for genre in GENRES.keys()}
    
    print("🔍 Catégorisation des concerts...")
    for i, concert_url in enumerate(all_concert_urls, 1):
        genre = categorize_concert_by_keywords(concert_url)
        concerts_by_genre[genre].append(concert_url)
        
        if i % 50 == 0:
            print(f"   Traité : {i}/{len(all_concert_urls)} concerts")
    
    print(f"✓ Catégorisation terminée\n")
    
    # Sauvegarder dans des fichiers séparés
    output_dir = 'concerts_par_genre'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print("💾 Sauvegarde des résultats...")
    print("="*60)
    
    total_categorized = 0
    for genre, concerts in concerts_by_genre.items():
        if len(concerts) > 0:
            output_file = os.path.join(output_dir, f'{genre}.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                for concert in sorted(concerts):
                    f.write(f"{concert}\n")
            
            total_categorized += len(concerts)
            print(f"  {genre:15} : {len(concerts):3} concerts → {output_file}")
    
    print("="*60)
    print(f"✅ Terminé ! {total_categorized} concerts catégorisés")
    print(f"📁 Résultats dans : {output_dir}/")


if __name__ == "__main__":
    extract_all_concerts()

