# 🎨 Artify - Extracteur de Liens Élégant

Interface web minimaliste et moderne pour extraire des liens de n'importe quelle page web.

## ✨ Caractéristiques

- 🎯 **Design minimaliste** inspiré de Notion, Apple et Spotify
- 🌐 **Extraction rapide** de tous les liens d'une page
- 🔍 **Filtrage intelligent** par mots-clés
- 📋 **Copie en un clic** de tous les résultats
- 🎨 **Interface responsive** et animations fluides
- ⚡ **Performance optimale** avec Flask

## 🚀 Installation

```bash
# Installer les dépendances
pip3 install -r requirements.txt

# Lancer l'application
python3 app.py
```

## 💻 Utilisation

1. Ouvrez votre navigateur à l'adresse : **http://127.0.0.1:5000**
2. Entrez une URL (exemple : https://www.sortiraparis.com/)
3. Ajoutez un filtre optionnel (exemple : "actualites")
4. Cliquez sur "Extraire les liens"
5. Copiez les résultats en un clic !

## 📁 Structure du projet

```
Artify/
├── app.py                 # Application Flask
├── extract_links.py       # Extraction des liens
├── filter_links.py        # Filtrage des liens
├── templates/
│   └── index.html        # Interface HTML
├── static/
│   ├── style.css         # Design minimaliste
│   └── script.js         # Interactions
├── test_extraction.py    # Tests
├── example_usage.py      # Exemple d'utilisation
└── requirements.txt      # Dépendances
```

## 🎨 Design

L'interface utilise une palette de couleurs claires et apaisantes :
- Fond principal : `#fafafa`
- Accents : Dégradé violet-bleu `#667eea` → `#764ba2`
- Typographie : Inter (police moderne de Apple)
- Animations douces et transitions fluides
- Shadows subtiles pour la profondeur
- Border radius arrondis pour la douceur

## 🛠 Technologies

- **Backend** : Flask (Python)
- **Frontend** : HTML5, CSS3, JavaScript
- **Parsing** : BeautifulSoup4
- **HTTP** : Requests

## 📝 License

Développé avec 💜 par Artify
