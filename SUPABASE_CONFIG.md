# Configuration de l'authentification Supabase

## Prérequis

1. Créez un compte sur [Supabase](https://supabase.com)
2. Créez un nouveau projet
3. Récupérez vos clés API

## Configuration

Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```bash
# URL de votre projet Supabase (trouvable dans Settings > API)
SUPABASE_URL=https://your-project-id.supabase.co

# Clé publique Supabase (anon/public key) (trouvable dans Settings > API)
SUPABASE_KEY=your-anon-key-here
```

### Comment trouver vos clés :

1. Allez dans votre projet Supabase
2. Cliquez sur **Settings** (⚙️) dans le menu de gauche
3. Cliquez sur **API**
4. Copiez :
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_KEY`

## Installation

Installez les dépendances nécessaires :

```bash
pip install -r requirements.txt
```

## Utilisation

Voir le fichier `auth_example.py` pour des exemples d'utilisation.


