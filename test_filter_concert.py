from extract_links import extract_links_from_url
from filter_links import filter_links_by_substring

# Extraire tous les liens
print("Extraction des liens depuis sortiraparis.com...")
liens = extract_links_from_url('https://www.sortiraparis.com/')
print(f'{len(liens)} liens trouvés au total\n')

# Filtrer par "concert"
liens_concerts = filter_links_by_substring(liens, "concert")
print(f'{len(liens_concerts)} liens contenant "concert" :\n')

# Afficher les liens trouvés
for i, link in enumerate(liens_concerts, 1):
    print(f"{i}. {link}")





