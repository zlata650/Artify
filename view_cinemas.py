#!/usr/bin/env python3
"""
Script pour afficher les cinémas et films de la base de données.
"""

from scrape_paris_cinemas import CinemaDatabase
from database import ConcertDatabase
import argparse


def main():
    parser = argparse.ArgumentParser(description='Affiche les cinémas et films de Paris')
    parser.add_argument('--cinemas', action='store_true', help='Afficher les cinémas')
    parser.add_argument('--films', action='store_true', help='Afficher les films')
    parser.add_argument('--stats', action='store_true', help='Afficher les statistiques')
    parser.add_argument('--type', type=str, help='Filtrer par type de cinéma (reseau, art_essai, independant, etc.)')
    parser.add_argument('--limit', type=int, default=20, help='Nombre max de résultats')
    args = parser.parse_args()
    
    db = CinemaDatabase('concerts.db')
    concert_db = ConcertDatabase('concerts.db')
    
    # Par défaut, afficher les stats
    if not args.cinemas and not args.films:
        args.stats = True
    
    if args.stats:
        print("=" * 60)
        print("📊 STATISTIQUES ARTIFY - CINÉMAS DE PARIS")
        print("=" * 60)
        print(f"\n🎬 Cinémas enregistrés: {db.count_cinemas()}")
        print(f"🎞️  Films dans la base: {db.count_films()}")
        print(f"🎵 Total événements: {concert_db.count_concerts()}")
        
        # Stats par type
        cinemas = db.get_all_cinemas()
        types_count = {}
        for cinema in cinemas:
            t = cinema[3] if len(cinema) > 3 else "autre"
            types_count[t] = types_count.get(t, 0) + 1
        
        print("\n📊 Répartition par type:")
        for t, count in sorted(types_count.items(), key=lambda x: -x[1]):
            emoji = {
                'art_essai': '🎭',
                'reseau': '🏢',
                'independant': '🎪',
                'cinematheque': '📚',
                'imax': '🖥️'
            }.get(t, '🎬')
            print(f"  {emoji} {t}: {count}")
    
    if args.cinemas:
        print("\n" + "=" * 60)
        print("🏛️  LISTE DES CINÉMAS DE PARIS")
        print("=" * 60)
        
        cinemas = db.get_all_cinemas()
        
        if args.type:
            cinemas = [c for c in cinemas if c[3] == args.type]
        
        for cinema in sorted(cinemas, key=lambda x: x[1])[:args.limit]:
            emoji = {
                'art_essai': '🎭',
                'reseau': '🏢',
                'independant': '🎪',
                'cinematheque': '📚',
                'imax': '🖥️'
            }.get(cinema[3], '🎬')
            print(f"\n{emoji} {cinema[1]} ({cinema[3]})")
            print(f"   📍 {cinema[2]}")
            if cinema[4]:
                print(f"   🔗 {cinema[4]}")
    
    if args.films:
        print("\n" + "=" * 60)
        print("🎬 FILMS ET ÉVÉNEMENTS CINÉMA")
        print("=" * 60)
        
        films = db.get_all_films()
        for film in films[:args.limit]:
            title = film[2][:60] + '...' if len(film[2]) > 60 else film[2]
            source = film[6] if len(film) > 6 else "?"
            print(f"\n• [{source}] {title}")
            print(f"  🔗 {film[1][:70]}...")


if __name__ == "__main__":
    main()


