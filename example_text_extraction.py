"""
Exemple d'utilisation de fetch_html pour extraire le texte pur d'une page
sans les balises HTML, CSS et JavaScript.
"""

from fetch_html import fetch_html


def compare_extraction_modes(url):
    """
    Compare les deux modes d'extraction : texte seul vs HTML complet
    """
    print("="*70)
    print(f"📄 Extraction depuis : {url}")
    print("="*70)
    
    # Mode 1 : Texte seul (par défaut)
    print("\n🔹 MODE 1 : TEXTE SEUL (text_only=True)")
    print("-"*70)
    text_content = fetch_html(url, text_only=True)
    
    if text_content:
        print(f"✓ Longueur : {len(text_content)} caractères")
        print(f"\nAperçu (300 premiers caractères) :")
        print(text_content[:300])
        print("...")
    else:
        print("✗ Échec de l'extraction")
    
    # Mode 2 : HTML complet
    print("\n🔹 MODE 2 : HTML COMPLET (text_only=False)")
    print("-"*70)
    html_content = fetch_html(url, text_only=False)
    
    if html_content:
        print(f"✓ Longueur : {len(html_content)} caractères")
        print(f"\nAperçu (300 premiers caractères) :")
        print(html_content[:300])
        print("...")
    else:
        print("✗ Échec de l'extraction")
    
    # Comparaison
    if text_content and html_content:
        reduction = 100 - (len(text_content) / len(html_content) * 100)
        print("\n📊 COMPARAISON")
        print("-"*70)
        print(f"Taille HTML : {len(html_content):,} caractères")
        print(f"Taille texte : {len(text_content):,} caractères")
        print(f"Réduction : {reduction:.1f}% (plus compact)")


if __name__ == "__main__":
    # Test avec un article de concert
    test_url = "https://www.sortiraparis.com/scenes/concert-musique/articles/337169-guns-n-roses-concert-paris-accor-arena"
    
    compare_extraction_modes(test_url)
    
    print("\n" + "="*70)
    print("✅ Démonstration terminée !")
    print("="*70)
    print("\n💡 UTILISATIONS :")
    print("   - text_only=True  : Pour l'analyse de contenu, recherche de mots-clés")
    print("   - text_only=False : Pour l'extraction de liens, parsing HTML")





