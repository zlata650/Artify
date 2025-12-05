"""
🎭 Script pour ajouter les théâtres et salles de concert classique à Paris
Ajoute les opéras, théâtres et salles de musique classique à la base de données Artify
"""

from database_v2 import ArtifyDatabase
import uuid


def generate_venue_id(name: str) -> str:
    """Génère un ID unique pour un lieu."""
    slug = name.lower().replace(" ", "-").replace("'", "").replace("é", "e").replace("è", "e")
    slug = slug.replace("â", "a").replace("ô", "o").replace("î", "i").replace("ç", "c")
    return f"venue-{slug[:30]}"


# Liste des théâtres et salles de concert classique/opéra à Paris
CLASSICAL_VENUES = [
    # ====== OPÉRAS ======
    {
        "name": "Palais Garnier - Opéra National de Paris",
        "address": "Place de l'Opéra, 75009 Paris",
        "arrondissement": 9,
        "lat": 48.8719,
        "lng": 2.3316,
        "metro": ["Opéra (3, 7, 8)"],
        "website": "https://www.operadeparis.fr",
        "phone": "+33 1 71 25 24 23",
        "categories": ["opera", "ballet", "classique"],
        "description": "Chef-d'œuvre architectural de Charles Garnier, inauguré en 1875. L'un des plus célèbres opéras du monde, avec son plafond peint par Chagall et son légendaire lustre de cristal. Accueille opéras, ballets et concerts de musique classique.",
        "capacity": 1979,
        "rating": 4.7,
    },
    {
        "name": "Opéra Bastille",
        "address": "Place de la Bastille, 75012 Paris",
        "arrondissement": 12,
        "lat": 48.8533,
        "lng": 2.3696,
        "metro": ["Bastille (1, 5, 8)"],
        "website": "https://www.operadeparis.fr",
        "phone": "+33 1 71 25 24 23",
        "categories": ["opera", "ballet", "classique"],
        "description": "Opéra moderne inauguré en 1989 pour le bicentenaire de la Révolution française. Scène principale de l'Opéra National de Paris avec une acoustique exceptionnelle et une programmation d'opéras et de ballets contemporains.",
        "capacity": 2745,
        "rating": 4.6,
    },
    {
        "name": "Opéra Comique - Salle Favart",
        "address": "1 Place Boieldieu, 75002 Paris",
        "arrondissement": 2,
        "lat": 48.8709,
        "lng": 2.3388,
        "metro": ["Richelieu-Drouot (8, 9)", "Quatre-Septembre (3)"],
        "website": "https://www.opera-comique.com",
        "phone": "+33 1 70 23 01 31",
        "categories": ["opera", "opera-comique", "classique"],
        "description": "Fondé en 1715, l'Opéra Comique est l'un des plus anciens théâtres lyriques de Paris. Lieu de création de Carmen de Bizet, Pelléas et Mélisande de Debussy, et de nombreux chefs-d'œuvre de l'opéra français.",
        "capacity": 1248,
        "rating": 4.5,
    },
    
    # ====== SALLES DE CONCERT CLASSIQUE ======
    {
        "name": "Philharmonie de Paris",
        "address": "221 Avenue Jean Jaurès, 75019 Paris",
        "arrondissement": 19,
        "lat": 48.8897,
        "lng": 2.3936,
        "metro": ["Porte de Pantin (5)"],
        "website": "https://philharmoniedeparis.fr",
        "phone": "+33 1 44 84 44 84",
        "categories": ["classique", "symphonique", "musique-contemporaine"],
        "description": "Grande salle de concert inaugurée en 2015, chef-d'œuvre de l'architecte Jean Nouvel. Résidence de l'Orchestre de Paris, elle offre une acoustique de classe mondiale et une programmation variée de musique classique et contemporaine.",
        "capacity": 2400,
        "rating": 4.7,
    },
    {
        "name": "Cité de la Musique",
        "address": "221 Avenue Jean Jaurès, 75019 Paris",
        "arrondissement": 19,
        "lat": 48.8891,
        "lng": 2.3933,
        "metro": ["Porte de Pantin (5)"],
        "website": "https://philharmoniedeparis.fr",
        "phone": "+33 1 44 84 44 84",
        "categories": ["classique", "musique-du-monde", "musee"],
        "description": "Complexe musical conçu par Christian de Portzamparc, ouvert en 1995. Abrite le Musée de la Musique, une médiathèque et plusieurs salles de concert. Programmation éclectique de musique classique et du monde.",
        "capacity": 900,
        "rating": 4.6,
    },
    {
        "name": "Salle Pleyel",
        "address": "252 Rue du Faubourg Saint-Honoré, 75008 Paris",
        "arrondissement": 8,
        "lat": 48.8794,
        "lng": 2.2987,
        "metro": ["Ternes (2)", "Charles de Gaulle - Étoile (1, 2, 6)"],
        "website": "https://www.sallepleyel.com",
        "phone": "+33 1 42 56 13 13",
        "categories": ["classique", "symphonique", "recitals"],
        "description": "Salle de concert mythique inaugurée en 1927, restaurée en 2006. Ancienne résidence de l'Orchestre de Paris, elle continue d'accueillir des concerts de musique classique et des récitals de grands solistes internationaux.",
        "capacity": 1913,
        "rating": 4.5,
    },
    {
        "name": "Théâtre des Champs-Élysées",
        "address": "15 Avenue Montaigne, 75008 Paris",
        "arrondissement": 8,
        "lat": 48.8658,
        "lng": 2.3055,
        "metro": ["Alma-Marceau (9)", "Franklin D. Roosevelt (1, 9)"],
        "website": "https://www.theatrechampselysees.fr",
        "phone": "+33 1 49 52 50 50",
        "categories": ["opera", "ballet", "classique", "symphonique"],
        "description": "Chef-d'œuvre Art Déco inauguré en 1913, célèbre pour la création scandaleuse du Sacre du Printemps de Stravinsky. Trois salles accueillent opéras, ballets, concerts symphoniques et récitals de musique de chambre.",
        "capacity": 1905,
        "rating": 4.5,
    },
    {
        "name": "Théâtre du Châtelet",
        "address": "1 Place du Châtelet, 75001 Paris",
        "arrondissement": 1,
        "lat": 48.8583,
        "lng": 2.3472,
        "metro": ["Châtelet (1, 4, 7, 11, 14)"],
        "website": "https://www.chatelet.com",
        "phone": "+33 1 40 28 28 40",
        "categories": ["opera", "ballet", "musical", "classique"],
        "description": "Plus grand théâtre de Paris avec 2500 places, inauguré en 1862. Temple de l'opéra, du ballet et des comédies musicales. Accueille également des concerts symphoniques et des productions lyriques internationales.",
        "capacity": 2500,
        "rating": 4.5,
    },
    
    # ====== THÉÂTRES CLASSIQUES ======
    {
        "name": "Comédie-Française - Salle Richelieu",
        "address": "1 Place Colette, 75001 Paris",
        "arrondissement": 1,
        "lat": 48.8632,
        "lng": 2.3366,
        "metro": ["Palais Royal - Musée du Louvre (1, 7)"],
        "website": "https://www.comedie-francaise.fr",
        "phone": "+33 1 44 58 15 15",
        "categories": ["theatre", "theatre-classique", "repertoire"],
        "description": "La 'Maison de Molière', fondée en 1680, est le plus ancien théâtre national du monde. Répertoire du théâtre classique français (Molière, Racine, Corneille) et créations contemporaines par la troupe permanente.",
        "capacity": 862,
        "rating": 4.7,
    },
    {
        "name": "Théâtre de l'Odéon - Théâtre de l'Europe",
        "address": "Place de l'Odéon, 75006 Paris",
        "arrondissement": 6,
        "lat": 48.8496,
        "lng": 2.3388,
        "metro": ["Odéon (4, 10)"],
        "website": "https://www.theatre-odeon.eu",
        "phone": "+33 1 44 85 40 40",
        "categories": ["theatre", "theatre-europeen", "creation"],
        "description": "Théâtre national inauguré en 1782, dédié au théâtre européen. Architecture néoclassique remarquable. Programmation de créations contemporaines et de grands textes du répertoire européen.",
        "capacity": 782,
        "rating": 4.5,
    },
    {
        "name": "Théâtre de la Ville - Sarah Bernhardt",
        "address": "2 Place du Châtelet, 75004 Paris",
        "arrondissement": 4,
        "lat": 48.8581,
        "lng": 2.3476,
        "metro": ["Châtelet (1, 4, 7, 11, 14)"],
        "website": "https://www.theatredelaville-paris.com",
        "phone": "+33 1 42 74 22 77",
        "categories": ["theatre", "danse", "musique-contemporaine"],
        "description": "Anciennement Théâtre Sarah Bernhardt, ce lieu mythique face au Châtelet est dédié à la création contemporaine : théâtre, danse et musique. Programmation audacieuse et artistes internationaux.",
        "capacity": 1000,
        "rating": 4.4,
    },
    {
        "name": "Théâtre National de Chaillot",
        "address": "1 Place du Trocadéro, 75016 Paris",
        "arrondissement": 16,
        "lat": 48.8625,
        "lng": 2.2877,
        "metro": ["Trocadéro (6, 9)"],
        "website": "https://theatre-chaillot.fr",
        "phone": "+33 1 53 65 30 00",
        "categories": ["theatre", "danse", "creation"],
        "description": "Théâtre national dédié à la danse et aux arts du mouvement, installé dans le Palais de Chaillot face à la Tour Eiffel. Programmation internationale de danse contemporaine et de créations théâtrales.",
        "capacity": 1250,
        "rating": 4.4,
    },
    {
        "name": "Théâtre Mogador",
        "address": "25 Rue de Mogador, 75009 Paris",
        "arrondissement": 9,
        "lat": 48.8762,
        "lng": 2.3287,
        "metro": ["Trinité - d'Estienne d'Orves (12)"],
        "website": "https://www.stage-entertainment.fr",
        "phone": "+33 1 53 32 32 00",
        "categories": ["musical", "comedie-musicale", "spectacle"],
        "description": "Théâtre inauguré en 1919, temple parisien de la comédie musicale. Accueille les plus grandes productions de Broadway et du West End adaptées en français.",
        "capacity": 1600,
        "rating": 4.5,
    },
    {
        "name": "Théâtre Marigny",
        "address": "Carré Marigny, 75008 Paris",
        "arrondissement": 8,
        "lat": 48.8689,
        "lng": 2.3138,
        "metro": ["Champs-Élysées - Clemenceau (1, 13)"],
        "website": "https://www.theatremarigny.fr",
        "phone": "+33 1 76 49 47 12",
        "categories": ["theatre", "boulevard", "classique"],
        "description": "Élégant théâtre à l'italienne situé dans les jardins des Champs-Élysées. Programmation de théâtre classique et contemporain, pièces de boulevard et créations.",
        "capacity": 1024,
        "rating": 4.5,
    },
    
    # ====== AUTRES SALLES DE MUSIQUE CLASSIQUE ======
    {
        "name": "Auditorium du Louvre",
        "address": "Musée du Louvre, 75001 Paris",
        "arrondissement": 1,
        "lat": 48.8606,
        "lng": 2.3376,
        "metro": ["Palais Royal - Musée du Louvre (1, 7)"],
        "website": "https://www.louvre.fr/auditorium",
        "phone": "+33 1 40 20 55 55",
        "categories": ["classique", "musique-de-chambre", "conference"],
        "description": "Auditorium de 420 places au cœur du Musée du Louvre. Concerts de musique de chambre, récitals et conférences en lien avec les collections du musée.",
        "capacity": 420,
        "rating": 4.5,
    },
    {
        "name": "Salle Gaveau",
        "address": "45 Rue La Boétie, 75008 Paris",
        "arrondissement": 8,
        "lat": 48.8742,
        "lng": 2.3107,
        "metro": ["Miromesnil (9, 13)", "Saint-Augustin (9)"],
        "website": "https://www.sallegaveau.com",
        "phone": "+33 1 49 53 05 07",
        "categories": ["classique", "recitals", "musique-de-chambre"],
        "description": "Salle de concert inaugurée en 1907, célèbre pour son acoustique parfaite. Lieu privilégié des récitals de piano et des concerts de musique de chambre.",
        "capacity": 1020,
        "rating": 4.6,
    },
    {
        "name": "Salle Cortot",
        "address": "78 Rue Cardinet, 75017 Paris",
        "arrondissement": 17,
        "lat": 48.8831,
        "lng": 2.3098,
        "metro": ["Malesherbes (3)", "Wagram (3)"],
        "website": "https://www.ecolenormalecortot.com",
        "phone": "+33 1 47 63 47 48",
        "categories": ["classique", "recitals", "musique-de-chambre"],
        "description": "Salle Art Déco de l'École Normale de Musique de Paris, fondée par Alfred Cortot. Acoustique remarquable pour les récitals et concerts de musique de chambre.",
        "capacity": 400,
        "rating": 4.5,
    },
    {
        "name": "Église de la Madeleine",
        "address": "Place de la Madeleine, 75008 Paris",
        "arrondissement": 8,
        "lat": 48.8701,
        "lng": 2.3249,
        "metro": ["Madeleine (8, 12, 14)"],
        "website": "https://www.eglise-lamadeleine.com",
        "phone": "+33 1 44 51 69 00",
        "categories": ["classique", "musique-sacree", "orgue"],
        "description": "Église néoclassique monumentale, haut lieu de la musique sacrée à Paris. Concerts d'orgue, messes en musique et grands oratorios dans un cadre architectural exceptionnel.",
        "capacity": 750,
        "rating": 4.6,
    },
    {
        "name": "Sainte-Chapelle",
        "address": "8 Boulevard du Palais, 75001 Paris",
        "arrondissement": 1,
        "lat": 48.8554,
        "lng": 2.3450,
        "metro": ["Cité (4)", "Saint-Michel (4)"],
        "website": "https://www.sainte-chapelle.fr",
        "phone": "+33 1 53 40 60 80",
        "categories": ["classique", "musique-baroque", "musique-de-chambre"],
        "description": "Chef-d'œuvre du gothique rayonnant, la Sainte-Chapelle offre un cadre unique pour les concerts de musique baroque et classique. Vitraux du XIIIe siècle et acoustique exceptionnelle.",
        "capacity": 300,
        "rating": 4.8,
    },
    {
        "name": "Église Saint-Eustache",
        "address": "146 Rue Rambuteau, 75001 Paris",
        "arrondissement": 1,
        "lat": 48.8634,
        "lng": 2.3456,
        "metro": ["Les Halles (4)", "Châtelet-Les Halles (A, B, D)"],
        "website": "https://www.saint-eustache.org",
        "phone": "+33 1 42 36 31 05",
        "categories": ["classique", "orgue", "musique-sacree"],
        "description": "Église monumentale des Halles, célèbre pour son grand orgue de 8000 tuyaux. Concerts d'orgue gratuits le dimanche et programmation de musique sacrée tout au long de l'année.",
        "capacity": 800,
        "rating": 4.5,
    },
    {
        "name": "Conservatoire National Supérieur de Musique et de Danse de Paris",
        "address": "209 Avenue Jean Jaurès, 75019 Paris",
        "arrondissement": 19,
        "lat": 48.8888,
        "lng": 2.3927,
        "metro": ["Porte de Pantin (5)"],
        "website": "https://www.conservatoiredeparis.fr",
        "phone": "+33 1 40 40 45 45",
        "categories": ["classique", "formation", "concerts-etudiants"],
        "description": "Le plus prestigieux conservatoire de musique de France. Nombreux concerts gratuits des élèves et masterclasses de grands artistes internationaux.",
        "capacity": 500,
        "rating": 4.5,
    },
    {
        "name": "Maison de la Radio et de la Musique",
        "address": "116 Avenue du Président Kennedy, 75016 Paris",
        "arrondissement": 16,
        "lat": 48.8521,
        "lng": 2.2697,
        "metro": ["Passy (6)", "Ranelagh (9)"],
        "website": "https://www.maisondelaradioetdelamusique.fr",
        "phone": "+33 1 56 40 15 16",
        "categories": ["classique", "symphonique", "jazz"],
        "description": "Siège de Radio France, abrite l'Auditorium et le Studio 104. Résidence des orchestres de Radio France. Programmation de concerts symphoniques, jazz et musiques du monde.",
        "capacity": 1461,
        "rating": 4.5,
    },
    {
        "name": "Théâtre des Bouffes du Nord",
        "address": "37 bis Boulevard de la Chapelle, 75010 Paris",
        "arrondissement": 10,
        "lat": 48.8823,
        "lng": 2.3582,
        "metro": ["La Chapelle (2)"],
        "website": "https://www.bouffesdunord.com",
        "phone": "+33 1 46 07 34 50",
        "categories": ["theatre", "musique", "creation"],
        "description": "Théâtre mythique dirigé pendant 35 ans par Peter Brook. Architecture unique avec ses murs patinés. Programmation de théâtre, musique et créations internationales.",
        "capacity": 500,
        "rating": 4.6,
    },
    {
        "name": "Théâtre de l'Athénée - Louis-Jouvet",
        "address": "7 Rue Boudreau, 75009 Paris",
        "arrondissement": 9,
        "lat": 48.8726,
        "lng": 2.3299,
        "metro": ["Opéra (3, 7, 8)", "Havre-Caumartin (3, 9)"],
        "website": "https://www.athenee-theatre.com",
        "phone": "+33 1 53 05 19 19",
        "categories": ["theatre", "opera", "musique-de-chambre"],
        "description": "Théâtre à l'italienne de 600 places, ancienne scène de Louis Jouvet. Programmation d'opéra de chambre, théâtre musical et pièces du répertoire.",
        "capacity": 600,
        "rating": 4.5,
    },
]


def add_venues_to_database():
    """Ajoute tous les lieux à la base de données."""
    db = ArtifyDatabase()
    
    added_count = 0
    existing_count = 0
    
    print("🎭 Ajout des théâtres et salles de concert classique à Paris\n")
    print("=" * 60)
    
    for venue_data in CLASSICAL_VENUES:
        venue = {
            "id": generate_venue_id(venue_data["name"]),
            "name": venue_data["name"],
            "address": venue_data["address"],
            "arrondissement": venue_data.get("arrondissement"),
            "lat": venue_data.get("lat"),
            "lng": venue_data.get("lng"),
            "metro": venue_data.get("metro", []),
            "website": venue_data.get("website"),
            "phone": venue_data.get("phone"),
            "categories": venue_data.get("categories", []),
            "description": venue_data.get("description"),
            "capacity": venue_data.get("capacity"),
            "rating": venue_data.get("rating"),
        }
        
        if db.add_venue(venue):
            print(f"✅ Ajouté: {venue_data['name']}")
            added_count += 1
        else:
            print(f"⏭️  Existe déjà: {venue_data['name']}")
            existing_count += 1
    
    print("\n" + "=" * 60)
    print(f"\n📊 Résumé:")
    print(f"   ✅ {added_count} lieux ajoutés")
    print(f"   ⏭️  {existing_count} lieux existants")
    print(f"   📍 Total traité: {len(CLASSICAL_VENUES)} lieux")
    
    # Afficher les statistiques
    stats = db.get_stats()
    print(f"\n📈 Statistiques de la base de données:")
    print(f"   Total lieux: {stats['total_venues']}")
    print(f"   Total événements: {stats['total_events']}")


def list_venues():
    """Liste tous les lieux de la base de données."""
    db = ArtifyDatabase()
    venues = db.get_venues()
    
    print(f"\n🎭 Liste des lieux ({len(venues)} au total):\n")
    for venue in venues:
        print(f"  • {venue['name']}")
        print(f"    📍 {venue['address']}")
        if venue.get('categories'):
            print(f"    🏷️  {', '.join(venue['categories'])}")
        print()


if __name__ == "__main__":
    add_venues_to_database()
    print("\n" + "=" * 60)
    list_venues()


