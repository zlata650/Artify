from bs4 import BeautifulSoup
import requests
from url_validator import clean_url, is_valid_event_url_pattern, is_sortiraparis_event_url
import re


def extract_concerts_with_names(html_content, filter_keyword="concert", base_url="https://www.sortiraparis.com"):
    """
    Extrait les liens et noms des concerts d'une page HTML.
    Nettoie et valide les URLs pour s'assurer qu'elles mènent à des pages d'événements.
    
    Args:
        html_content: Le contenu HTML sous forme de chaîne de caractères
        filter_keyword: Mot-clé pour filtrer les liens (défaut: "concert")
        base_url: URL de base pour les liens relatifs
        
    Returns:
        Liste de tuples (url, nom) des concerts trouvés
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    concerts = []
    
    # Trouver tous les liens
    for a in soup.find_all('a'):
        href = a.get('href')
        if not href:
            continue
        
        # Filtrer par mot-clé
        if filter_keyword.lower() not in href.lower():
            continue
        
        # Nettoyer et valider l'URL
        cleaned_url = clean_url(href, base_url)
        
        if not cleaned_url:
            continue
        
        # Vérifier que c'est une page d'événement individuel
        if not is_valid_event_url_pattern(cleaned_url):
            continue
        
        # Pour SortirAParis, doit contenir /articles/ avec un ID numérique
        if 'sortiraparis.com' in cleaned_url:
            if not is_sortiraparis_event_url(cleaned_url):
                # Vérification alternative
                if '/articles/' not in cleaned_url:
                    continue
                if not re.search(r'/articles/\d+', cleaned_url):
                    continue
        
        # Extraire le texte du lien (nom du concert)
        nom = a.get_text(strip=True)
        
        # Si pas de texte, essayer de récupérer le title ou alt d'une image
        if not nom:
            img = a.find('img')
            if img:
                nom = img.get('alt', '') or img.get('title', '')
        
        # Si toujours pas de nom, extraire de l'URL
        if not nom:
            nom = href.split('/')[-1].replace('-', ' ').title()
        
        # Vérifier que le nom est valide
        if nom and len(nom) > 3:
            concerts.append((cleaned_url, nom))
    
    return concerts


def extract_concerts_from_url(url, filter_keyword="concert"):
    """
    Extrait les concerts d'une URL.
    Nettoie et valide les URLs pour s'assurer qu'elles mènent à des pages d'événements.
    
    Args:
        url: L'URL de la page à analyser
        filter_keyword: Mot-clé pour filtrer les liens (défaut: "concert")
        
    Returns:
        Liste de tuples (url, nom) des concerts trouvés
    """
    response = requests.get(url)
    
    # Extraire l'URL de base pour les liens relatifs
    from urllib.parse import urlparse
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    return extract_concerts_with_names(response.text, filter_keyword, base_url)


def remove_duplicates(concerts):
    """
    Supprime les doublons basés sur l'URL.
    
    Args:
        concerts: Liste de tuples (url, nom)
        
    Returns:
        Liste de tuples (url, nom) sans doublons
    """
    seen_urls = set()
    unique_concerts = []
    
    for url, nom in concerts:
        if url not in seen_urls:
            seen_urls.add(url)
            unique_concerts.append((url, nom))
    
    return unique_concerts


# Exemple d'utilisation
if __name__ == "__main__":
    print("Extraction des concerts depuis sortiraparis.com...")
    concerts = extract_concerts_from_url('https://www.sortiraparis.com/')
    
    # Supprimer les doublons
    concerts_uniques = remove_duplicates(concerts)
    
    print(f"{len(concerts_uniques)} concerts uniques trouvés :\n")
    
    for i, (url, nom) in enumerate(concerts_uniques[:10], 1):
        print(f"{i}. {nom}")
        print(f"   URL: {url}\n")




