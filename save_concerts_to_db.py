from extract_concerts import extract_concerts_from_url, remove_duplicates
from database import ConcertDatabase


def main():
    """Script principal pour extraire et sauvegarder les concerts."""
    
    # Créer/ouvrir la base de données
    db = ConcertDatabase('concerts.db')
    
    print("🎵 Extraction des concerts depuis sortiraparis.com...")
    
    # Extraire les concerts
    concerts = extract_concerts_from_url('https://www.sortiraparis.com/', filter_keyword="concert")
    
    # Supprimer les doublons
    concerts_uniques = remove_duplicates(concerts)
    
    print(f"✅ {len(concerts_uniques)} concerts uniques trouvés")
    
    # Sauvegarder dans la base de données
    print("\n💾 Sauvegarde dans la base de données...")
    added = db.add_concerts_batch(concerts_uniques)
    
    print(f"✅ {added} nouveaux concerts ajoutés à la base")
    print(f"📊 Total dans la base : {db.count_concerts()} concerts")
    
    # Afficher quelques exemples
    print("\n🎤 Exemples de concerts enregistrés :")
    concerts_db = db.get_all_concerts()
    for concert in concerts_db[:5]:
        concert_id, url, nom, date_ajout = concert
        print(f"\n{concert_id}. {nom}")
        print(f"   URL: {url}")
        print(f"   Ajouté le: {date_ajout}")


if __name__ == "__main__":
    main()





