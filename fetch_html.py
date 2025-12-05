import requests
from typing import Optional
from bs4 import BeautifulSoup


def fetch_html(url: str, timeout: int = 10, text_only: bool = True) -> Optional[str]:
    """
    Télécharge le contenu d'une page web depuis une URL donnée.
    
    Args:
        url: L'URL de la page à télécharger
        timeout: Temps d'attente maximum en secondes (par défaut: 10)
        text_only: Si True, retourne uniquement le texte sans HTML/CSS/JS (par défaut: True)
        
    Returns:
        Le contenu textuel ou HTML de la page, ou None en cas d'erreur
        
    Raises:
        requests.exceptions.RequestException: En cas d'erreur lors de la requête
    """
    try:
        # Définir un User-Agent pour éviter d'être bloqué par certains sites
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Effectuer la requête GET
        response = requests.get(url, headers=headers, timeout=timeout)
        
        # Vérifier que la requête a réussi
        response.raise_for_status()
        
        # Si text_only est False, retourner le HTML brut
        if not text_only:
            return response.text
        
        # Parser le HTML avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Supprimer les balises script et style (JavaScript et CSS)
        for script in soup(['script', 'style', 'noscript']):
            script.decompose()
        
        # Extraire le texte et nettoyer les espaces
        text = soup.get_text(separator=' ', strip=True)
        
        # Nettoyer les espaces multiples et les sauts de ligne excessifs
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except requests.exceptions.Timeout:
        print(f"Erreur : Le délai d'attente a été dépassé pour l'URL {url}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"Erreur : Impossible de se connecter à {url}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Erreur HTTP {e.response.status_code} pour l'URL {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête : {e}")
        return None


# Exemple d'utilisation
if __name__ == "__main__":
    test_url = "https://www.example.com"
    
    print("="*60)
    print("MODE 1 : Extraction du texte uniquement (par défaut)")
    print("="*60)
    text_content = fetch_html(test_url, text_only=True)
    
    if text_content:
        print(f"✓ Texte extrait avec succès ({len(text_content)} caractères)")
        print("\nAperçu des 200 premiers caractères :")
        print(text_content[:200])
    else:
        print("✗ Échec de l'extraction")
    
    print("\n" + "="*60)
    print("MODE 2 : Récupération du HTML complet")
    print("="*60)
    html_content = fetch_html(test_url, text_only=False)
    
    if html_content:
        print(f"✓ HTML téléchargé avec succès ({len(html_content)} caractères)")
        print("\nAperçu des 200 premiers caractères :")
        print(html_content[:200])
    else:
        print("✗ Échec du téléchargement")

