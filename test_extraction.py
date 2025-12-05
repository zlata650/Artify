

from extract_links import extract_links_from_url
from filter_links import filter_links_by_substring

# Extraire tous les liens
liens = extract_links_from_url('https://www.sortiraparis.com/')
print(f'✅ {len(liens)} liens trouvés !\n')

# Filtrer par catégorie
evenements = filter_links_by_substring(liens, '/evenement')
actualites = filter_links_by_substring(liens, '/actualites')
restaurants = filter_links_by_substring(liens, '/restaurant')

print(f'📅 Événements : {len(evenements)} liens')
print(f'📰 Actualités : {len(actualites)} liens')
print(f'🍽️  Restaurants : {len(restaurants)} liens')

# Afficher quelques exemples
if actualites:
    print(f'\n📋 Exemples d\'actualités :')
    for link in actualites[:3]:
        print(f'  • {link}')

