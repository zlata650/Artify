"""
Module d'authentification avec Supabase
Fournit les fonctions de base pour l'inscription, la connexion et la gestion des utilisateurs
"""

import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class SupabaseAuth:
    """Classe pour gérer l'authentification avec Supabase"""
    
    def __init__(self):
        """Initialise le client Supabase"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "Les variables d'environnement SUPABASE_URL et SUPABASE_KEY "
                "doivent être définies. Créez un fichier .env avec ces valeurs."
            )
        
        self.client: Client = create_client(supabase_url, supabase_key)
    
    def sign_up(self, email: str, password: str, user_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Inscrit un nouvel utilisateur avec email et mot de passe
        
        Args:
            email: L'adresse email de l'utilisateur
            password: Le mot de passe de l'utilisateur
            user_data: Données supplémentaires de l'utilisateur (optionnel)
            
        Returns:
            Dict contenant les données de l'utilisateur et de la session
            
        Raises:
            Exception: Si l'inscription échoue
        """
        try:
            options = {}
            if user_data:
                options['data'] = user_data
            
            response = self.client.auth.sign_up({
                'email': email,
                'password': password,
                'options': options
            })
            
            return {
                'success': True,
                'user': response.user,
                'session': response.session,
                'message': 'Inscription réussie ! Vérifiez votre email pour confirmer votre compte.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Erreur lors de l\'inscription : {str(e)}'
            }
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Connecte un utilisateur avec email et mot de passe
        
        Args:
            email: L'adresse email de l'utilisateur
            password: Le mot de passe de l'utilisateur
            
        Returns:
            Dict contenant les données de l'utilisateur et de la session
            
        Raises:
            Exception: Si la connexion échoue
        """
        try:
            response = self.client.auth.sign_in_with_password({
                'email': email,
                'password': password
            })
            
            return {
                'success': True,
                'user': response.user,
                'session': response.session,
                'message': 'Connexion réussie !'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Erreur lors de la connexion : {str(e)}'
            }
    
    def sign_out(self) -> Dict[str, Any]:
        """
        Déconnecte l'utilisateur actuel
        
        Returns:
            Dict indiquant le succès ou l'échec de la déconnexion
        """
        try:
            self.client.auth.sign_out()
            return {
                'success': True,
                'message': 'Déconnexion réussie !'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Erreur lors de la déconnexion : {str(e)}'
            }
    
    def get_user(self) -> Dict[str, Any]:
        """
        Récupère les informations de l'utilisateur actuellement connecté
        
        Returns:
            Dict contenant les données de l'utilisateur ou None si non connecté
        """
        try:
            response = self.client.auth.get_user()
            
            if response and response.user:
                return {
                    'success': True,
                    'user': response.user,
                    'message': 'Utilisateur récupéré avec succès'
                }
            else:
                return {
                    'success': False,
                    'user': None,
                    'message': 'Aucun utilisateur connecté'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Erreur lors de la récupération de l\'utilisateur : {str(e)}'
            }
    
    def get_session(self) -> Dict[str, Any]:
        """
        Récupère la session actuelle de l'utilisateur
        
        Returns:
            Dict contenant les données de la session
        """
        try:
            response = self.client.auth.get_session()
            
            if response:
                return {
                    'success': True,
                    'session': response,
                    'message': 'Session récupérée avec succès'
                }
            else:
                return {
                    'success': False,
                    'session': None,
                    'message': 'Aucune session active'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Erreur lors de la récupération de la session : {str(e)}'
            }
    
    def reset_password(self, email: str) -> Dict[str, Any]:
        """
        Envoie un email de réinitialisation de mot de passe
        
        Args:
            email: L'adresse email de l'utilisateur
            
        Returns:
            Dict indiquant le succès ou l'échec de l'envoi
        """
        try:
            self.client.auth.reset_password_email(email)
            return {
                'success': True,
                'message': f'Email de réinitialisation envoyé à {email}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Erreur lors de l\'envoi de l\'email : {str(e)}'
            }
    
    def update_user(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Met à jour les attributs de l'utilisateur connecté
        
        Args:
            attributes: Dict contenant les attributs à mettre à jour (email, password, data, etc.)
            
        Returns:
            Dict contenant les données mises à jour de l'utilisateur
        """
        try:
            response = self.client.auth.update_user(attributes)
            return {
                'success': True,
                'user': response.user,
                'message': 'Utilisateur mis à jour avec succès'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Erreur lors de la mise à jour : {str(e)}'
            }


# Créer une instance globale (optionnel)
def get_auth_client() -> SupabaseAuth:
    """
    Retourne une instance du client d'authentification
    Utile pour éviter de créer plusieurs instances
    """
    return SupabaseAuth()


