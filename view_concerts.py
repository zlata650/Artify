from database import ConcertDatabase
import sys


def view_all_concerts():
    """Affiche tous les concerts de la base de données."""
    db = ConcertDatabase('concerts.db')
    concerts = db.get_all_concerts()
    
    print(f"\n📊 Total : {len(concerts)} concerts dans la base\n")
    print("=" * 80)
    
    for concert in concerts:
        concert_id, url, nom, date_ajout = concert
        print(f"\n🎵 {concert_id}. {nom}")
        print(f"   🔗 URL: {url}")
        print(f"   📅 Ajouté le: {date_ajout}")
    
    print("\n" + "=" * 80)


def search_concerts(search_term):
    """Recherche des concerts dans la base de données."""
    db = ConcertDatabase('concerts.db')
    concerts = db.search_concerts(search_term)
    
    if not concerts:
        print(f"\n❌ Aucun concert trouvé pour '{search_term}'")
        return
    
    print(f"\n🔍 {len(concerts)} concert(s) trouvé(s) pour '{search_term}':\n")
    print("=" * 80)
    
    for concert in concerts:
        concert_id, url, nom, date_ajout = concert
        print(f"\n🎵 {concert_id}. {nom}")
        print(f"   🔗 URL: {url}")
        print(f"   📅 Ajouté le: {date_ajout}")
    
    print("\n" + "=" * 80)


def main():
    """Script principal."""
    if len(sys.argv) > 1:
        # Recherche avec un terme
        search_term = ' '.join(sys.argv[1:])
        search_concerts(search_term)
    else:
        # Afficher tous les concerts
        view_all_concerts()


if __name__ == "__main__":
    main()





