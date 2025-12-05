"""
Exemples d'utilisation du module d'authentification Supabase
"""

from auth import SupabaseAuth


def exemple_inscription():
    """Exemple d'inscription d'un nouvel utilisateur"""
    print("\n" + "="*60)
    print("EXEMPLE 1 : INSCRIPTION D'UN NOUVEL UTILISATEUR")
    print("="*60)
    
    auth = SupabaseAuth()
    
    # Inscription avec email et mot de passe
    result = auth.sign_up(
        email="test@example.com",
        password="MonMotDePasseSecurise123!",
        user_data={
            "nom": "Dupont",
            "prenom": "Jean"
        }
    )
    
    print(f"\n✓ Résultat : {result['message']}")
    if result['success']:
        print(f"  User ID: {result['user'].id if result['user'] else 'N/A'}")
        print(f"  Email: {result['user'].email if result['user'] else 'N/A'}")


def exemple_connexion():
    """Exemple de connexion d'un utilisateur existant"""
    print("\n" + "="*60)
    print("EXEMPLE 2 : CONNEXION D'UN UTILISATEUR")
    print("="*60)
    
    auth = SupabaseAuth()
    
    # Connexion
    result = auth.sign_in(
        email="test@example.com",
        password="MonMotDePasseSecurise123!"
    )
    
    print(f"\n✓ Résultat : {result['message']}")
    if result['success']:
        print(f"  User ID: {result['user'].id if result['user'] else 'N/A'}")
        print(f"  Email: {result['user'].email if result['user'] else 'N/A'}")
        print(f"  Session active: {'Oui' if result['session'] else 'Non'}")
    
    return auth


def exemple_get_utilisateur(auth):
    """Exemple de récupération de l'utilisateur connecté"""
    print("\n" + "="*60)
    print("EXEMPLE 3 : RÉCUPÉRATION DE L'UTILISATEUR ACTUEL")
    print("="*60)
    
    result = auth.get_user()
    
    print(f"\n✓ Résultat : {result['message']}")
    if result['success'] and result['user']:
        user = result['user']
        print(f"  User ID: {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Créé le: {user.created_at}")
        print(f"  Dernière connexion: {user.last_sign_in_at}")


def exemple_get_session(auth):
    """Exemple de récupération de la session"""
    print("\n" + "="*60)
    print("EXEMPLE 4 : RÉCUPÉRATION DE LA SESSION")
    print("="*60)
    
    result = auth.get_session()
    
    print(f"\n✓ Résultat : {result['message']}")
    if result['success'] and result['session']:
        print(f"  Session active: Oui")
        print(f"  Access token disponible: Oui")


def exemple_update_utilisateur(auth):
    """Exemple de mise à jour des données utilisateur"""
    print("\n" + "="*60)
    print("EXEMPLE 5 : MISE À JOUR DES DONNÉES UTILISATEUR")
    print("="*60)
    
    result = auth.update_user({
        'data': {
            'ville': 'Paris',
            'preferences': {
                'genre_favori': 'rock',
                'notifications': True
            }
        }
    })
    
    print(f"\n✓ Résultat : {result['message']}")
    if result['success']:
        print("  Données mises à jour avec succès")


def exemple_reset_password():
    """Exemple de réinitialisation de mot de passe"""
    print("\n" + "="*60)
    print("EXEMPLE 6 : RÉINITIALISATION DE MOT DE PASSE")
    print("="*60)
    
    auth = SupabaseAuth()
    
    result = auth.reset_password("test@example.com")
    
    print(f"\n✓ Résultat : {result['message']}")


def exemple_deconnexion(auth):
    """Exemple de déconnexion"""
    print("\n" + "="*60)
    print("EXEMPLE 7 : DÉCONNEXION")
    print("="*60)
    
    result = auth.sign_out()
    
    print(f"\n✓ Résultat : {result['message']}")


def main():
    """Fonction principale pour tester tous les exemples"""
    print("\n" + "="*60)
    print("EXEMPLES D'AUTHENTIFICATION AVEC SUPABASE")
    print("="*60)
    print("\n⚠️  Note: Ces exemples ne fonctionneront que si vous avez")
    print("   configuré votre fichier .env avec vos clés Supabase.")
    print("   Voir SUPABASE_CONFIG.md pour plus d'informations.")
    
    try:
        # Décommentez les exemples que vous voulez tester
        
        # INSCRIPTION (à utiliser une seule fois avec un email unique)
        # exemple_inscription()
        
        # CONNEXION
        # auth = exemple_connexion()
        
        # RÉCUPÉRATION DE L'UTILISATEUR (nécessite d'être connecté)
        # exemple_get_utilisateur(auth)
        
        # RÉCUPÉRATION DE LA SESSION (nécessite d'être connecté)
        # exemple_get_session(auth)
        
        # MISE À JOUR DE L'UTILISATEUR (nécessite d'être connecté)
        # exemple_update_utilisateur(auth)
        
        # RÉINITIALISATION DE MOT DE PASSE
        # exemple_reset_password()
        
        # DÉCONNEXION (nécessite d'être connecté)
        # exemple_deconnexion(auth)
        
        print("\n" + "="*60)
        print("TOUS LES EXEMPLES ONT ÉTÉ EXÉCUTÉS")
        print("="*60)
        
    except ValueError as e:
        print(f"\n❌ ERREUR DE CONFIGURATION:")
        print(f"   {str(e)}")
        print(f"\n   Veuillez créer un fichier .env avec vos clés Supabase.")
        print(f"   Voir SUPABASE_CONFIG.md pour plus d'informations.")
    except Exception as e:
        print(f"\n❌ ERREUR:")
        print(f"   {str(e)}")


if __name__ == "__main__":
    # Exemple simple : Workflow complet d'authentification
    print("\n" + "="*60)
    print("WORKFLOW COMPLET D'AUTHENTIFICATION")
    print("="*60)
    print("\nCe script montre comment utiliser le module auth.py")
    print("Décommentez les exemples dans la fonction main() pour les tester.")
    
    main()


