from bs4 import BeautifulSoup
import requests


def extract_links(html_content):
    """
    Extrait tous les liens d'une page HTML.
    
    Args:
        html_content: Le contenu HTML sous forme de chaîne de caractères
        
    Returns:
        Liste des URLs trouvées dans les balises <a>
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    links = [a.get('href') for a in soup.find_all('a') if a.get('href')]
    return links


def extract_links_from_url(url):
    """
    Extrait tous les liens d'une URL.
    
    Args:
        url: L'URL de la page à analyser
        
    Returns:
        Liste des URLs trouvées dans les balises <a>
    """
    response = requests.get(url)
    return extract_links(response.text)


# Exemple d'utilisation
if __name__ == "__main__":
    from filter_links import filter_links_by_substring
    
    # Exemple avec du HTML brut
    html = """
    <html>
        <body>
            <a href="https://example.com">Exemple</a>
            <a href="https://www.sortiraparis.com/concerts">Concerts</a>
            <a href="https://google.com">Google</a>
            <a href="/evenement/theatre">Théâtre</a>
            <a href="/evenement/exposition">Exposition</a>
        </body>
    </html>
    """
    
    liens = extract_links(html)
    print(f"Liens extraits : {len(liens)}")
    for link in liens:
        print(f"  - {link}")
    
    # Filtrer les liens contenant "evenement"
    print("\nLiens filtrés (contenant 'evenement') :")
    liens_filtres = filter_links_by_substring(liens, "evenement")
    for link in liens_filtres:
        print(f"  - {link}")

