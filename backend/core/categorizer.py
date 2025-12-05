"""
🎭 Artify - AI Event Categorizer
Uses OpenAI to classify events into categories
"""

import os
import json
from typing import Optional, List, Dict
import re

# Try to import openai, but allow fallback
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


# Valid categories matching frontend
VALID_CATEGORIES = [
    "spectacles",       # Theatre, opera, dance, comedy, circus
    "musique",          # Concerts, live music
    "arts_visuels",     # Exhibitions, museums, galleries
    "ateliers",         # Workshops: ceramics, painting, drawing
    "sport",            # Sports, fitness, yoga
    "gastronomie",      # Food, wine, cooking classes
    "culture",          # Cinema, conferences, guided tours
    "nightlife",        # Clubs, bars, parties
    "rencontres",       # Meetups, networking, social events
]

# Sub-category mapping
SUB_CATEGORIES = {
    "spectacles": ["theatre", "opera", "ballet", "danse", "humour", "stand_up", "cirque", "magie", "cabaret"],
    "musique": ["classique", "jazz", "rock", "pop", "electro", "rap", "world", "chanson_francaise", "symphonique"],
    "arts_visuels": ["exposition", "musee", "galerie", "photographie", "street_art", "art_contemporain", "vernissage"],
    "ateliers": ["ceramique", "poterie", "peinture", "dessin", "sculpture", "couture", "bijoux", "ecriture"],
    "sport": ["yoga", "fitness", "running", "escalade", "danse", "arts_martiaux", "velo"],
    "gastronomie": ["degustation_vin", "cours_cuisine", "patisserie", "brunch", "food_market"],
    "culture": ["cinema", "conference", "visite_guidee", "lecture", "masterclass"],
    "nightlife": ["club", "bar", "rooftop", "speakeasy", "soiree"],
    "rencontres": ["meetup", "networking", "afterwork", "speed_dating"],
}

# Keywords for rule-based fallback
CATEGORY_KEYWORDS = {
    "spectacles": [
        "théâtre", "theatre", "opéra", "opera", "ballet", "danse", "dance",
        "comédie", "comedie", "comedy", "humour", "stand-up", "standup", "one man show",
        "cirque", "circus", "magie", "magic", "cabaret", "spectacle", "pièce",
        "marionnettes", "improvisation", "impro"
    ],
    "musique": [
        "concert", "musique", "music", "live", "jazz", "rock", "pop", "electro",
        "electronic", "classique", "classical", "symphonie", "symphony", "orchestre",
        "orchestra", "rap", "hip-hop", "hip hop", "chanson", "folk", "blues",
        "récital", "recital", "philharmonie", "chamber music", "quartet", "trio"
    ],
    "arts_visuels": [
        "exposition", "exhibition", "expo", "musée", "museum", "galerie", "gallery",
        "art", "vernissage", "photographie", "photography", "photo", "peinture",
        "painting", "sculpture", "installation", "beaux-arts", "contemporain"
    ],
    "ateliers": [
        "atelier", "workshop", "cours", "class", "stage", "céramique", "ceramics",
        "poterie", "pottery", "peinture", "painting", "dessin", "drawing",
        "sculpture", "couture", "sewing", "bijoux", "jewelry", "créatif", "creative",
        "diy", "fabrication", "initiation", "masterclass créative"
    ],
    "sport": [
        "sport", "fitness", "yoga", "pilates", "running", "course", "vélo", "cycling",
        "escalade", "climbing", "natation", "swimming", "musculation", "gym",
        "boxe", "boxing", "arts martiaux", "martial arts", "match", "compétition"
    ],
    "gastronomie": [
        "dégustation", "tasting", "vin", "wine", "cuisine", "cooking", "chef",
        "gastronomie", "gastronomy", "pâtisserie", "pastry", "chocolat", "chocolate",
        "fromage", "cheese", "brunch", "food", "restaurant", "repas", "dîner", "dinner"
    ],
    "culture": [
        "cinéma", "cinema", "film", "movie", "conférence", "conference", "talk",
        "lecture", "visite", "visit", "guidée", "guided", "patrimoine", "heritage",
        "histoire", "history", "littérature", "literature", "livre", "book", "débat"
    ],
    "nightlife": [
        "club", "soirée", "party", "nuit", "night", "dj", "danse", "dancing",
        "bar", "cocktail", "rooftop", "speakeasy", "lounge", "afterparty"
    ],
    "rencontres": [
        "meetup", "networking", "afterwork", "rencontre", "meeting", "social",
        "speed dating", "apéro", "drinks", "échange", "exchange", "conversation",
        "communauté", "community"
    ],
}


class EventCategorizer:
    """
    Categorizes events using AI with rule-based fallback.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the categorizer."""
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.client = None
        
        if HAS_OPENAI and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
    
    def categorize(
        self, 
        title: str, 
        description: str = "", 
        source_name: str = "",
        venue_name: str = ""
    ) -> Dict[str, Optional[str]]:
        """
        Categorize an event.
        
        Returns:
            Dict with 'category' and 'sub_category' keys
        """
        # First try AI if available
        if self.client:
            try:
                result = self._categorize_with_ai(title, description, source_name, venue_name)
                if result['category'] in VALID_CATEGORIES:
                    return result
            except Exception as e:
                print(f"⚠️ AI categorization failed: {e}")
        
        # Fallback to rules
        return self._categorize_with_rules(title, description, venue_name)
    
    def _categorize_with_ai(
        self, 
        title: str, 
        description: str,
        source_name: str,
        venue_name: str
    ) -> Dict[str, Optional[str]]:
        """Use OpenAI to categorize the event."""
        
        prompt = f"""Classify this Paris event into exactly ONE category.

Event:
- Title: {title}
- Description: {description[:500] if description else 'N/A'}
- Source: {source_name}
- Venue: {venue_name}

Categories (choose ONE):
- spectacles: Theatre, opera, ballet, dance, comedy, stand-up, circus, magic, cabaret
- musique: Concerts, live music (classical, jazz, rock, pop, electro, rap)
- arts_visuels: Exhibitions, museums, galleries, photography, vernissage
- ateliers: Creative workshops (ceramics, pottery, painting, drawing, crafts)
- sport: Sports events, fitness, yoga, running
- gastronomie: Wine tasting, cooking classes, food events, brunch
- culture: Cinema, conferences, guided tours, lectures
- nightlife: Clubs, bars, DJ parties, rooftop events
- rencontres: Meetups, networking, afterwork, social events

Respond with JSON only:
{{"category": "category_name", "sub_category": "optional_subcategory"}}"""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an event categorizer. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=100
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            # Handle potential markdown code blocks
            if '```' in content:
                content = re.search(r'\{.*\}', content, re.DOTALL).group()
            result = json.loads(content)
            return {
                'category': result.get('category', 'culture'),
                'sub_category': result.get('sub_category')
            }
        except:
            return {'category': 'culture', 'sub_category': None}
    
    def _categorize_with_rules(
        self, 
        title: str, 
        description: str,
        venue_name: str
    ) -> Dict[str, Optional[str]]:
        """Rule-based categorization fallback."""
        
        text = f"{title} {description} {venue_name}".lower()
        
        # Count keyword matches per category
        scores = {}
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text)
            if score > 0:
                scores[category] = score
        
        if not scores:
            return {'category': 'culture', 'sub_category': None}
        
        # Return highest scoring category
        best_category = max(scores, key=scores.get)
        
        # Try to find sub-category
        sub_category = self._find_sub_category(text, best_category)
        
        return {
            'category': best_category,
            'sub_category': sub_category
        }
    
    def _find_sub_category(self, text: str, category: str) -> Optional[str]:
        """Find the most likely sub-category."""
        sub_cats = SUB_CATEGORIES.get(category, [])
        
        for sub in sub_cats:
            # Check if sub-category name appears in text
            if sub.replace('_', ' ') in text or sub.replace('_', '-') in text:
                return sub
        
        return None
    
    def categorize_batch(self, events: List[Dict]) -> List[Dict]:
        """
        Categorize multiple events.
        
        Args:
            events: List of dicts with 'title', 'description', 'source_name', 'venue_name'
            
        Returns:
            List of dicts with 'category' and 'sub_category' added
        """
        results = []
        for event in events:
            cat_result = self.categorize(
                title=event.get('title', ''),
                description=event.get('description', ''),
                source_name=event.get('source_name', ''),
                venue_name=event.get('venue_name', event.get('location_name', ''))
            )
            event_copy = event.copy()
            event_copy.update(cat_result)
            results.append(event_copy)
        
        return results


# Quick helper function
def categorize_event(
    title: str, 
    description: str = "", 
    source_name: str = "",
    venue_name: str = ""
) -> str:
    """Quick categorization returning just the category."""
    categorizer = EventCategorizer()
    result = categorizer.categorize(title, description, source_name, venue_name)
    return result['category']

