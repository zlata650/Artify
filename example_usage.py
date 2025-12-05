from extract_links import extract_links_from_url
from filter_links import filter_links_by_substring

url = "https://www.sortiraparis.com/"

links = extract_links_from_url(url)
print(f"{len(links)} liens trouvés !")

# Afficher les liens 50-80 pour voir la structure des vraies pages
print("\n=== Liens 50-80 ===")
for i, link in enumerate(links[50:80], 51):
    print(f"{i}. {link}")
    
# Chercher des liens qui pourraient être des événements/concerts
print("\n=== Liens contenant 'concert' ou 'spectacle' ===")
concert_links = [link for link in links if 'concert' in link.lower() or 'spectacle' in link.lower()]
for i, link in enumerate(concert_links[:10], 1):
    print(f"{i}. {link}")

# Example: filter only event pages
filtered = filter_links_by_substring(links, "/evenement")
print(f"\n{len(filtered)} liens filtrés contenant '/evenement'")

