"""
🎭 Artify - Modèles de données
"""

from .event import (
    MainCategory,
    SubCategorySpectacles,
    SubCategoryMusique,
    SubCategoryArtsVisuels,
    SubCategoryAteliers,
    SubCategorySport,
    SubCategoryRencontres,
    SubCategoryGastronomie,
    SubCategoryCulture,
    SubCategoryNightlife,
    Budget,
    TimeOfDay,
    Ambiance,
    Coordinates,
    Venue,
    Event,
    EventFilter,
    CATEGORY_INFO,
    ARRONDISSEMENTS,
    price_to_budget,
    get_category_info,
    get_arrondissement_info,
    generate_slug,
)

__all__ = [
    # Enums
    'MainCategory',
    'SubCategorySpectacles',
    'SubCategoryMusique',
    'SubCategoryArtsVisuels',
    'SubCategoryAteliers',
    'SubCategorySport',
    'SubCategoryRencontres',
    'SubCategoryGastronomie',
    'SubCategoryCulture',
    'SubCategoryNightlife',
    'Budget',
    'TimeOfDay',
    'Ambiance',
    # Dataclasses
    'Coordinates',
    'Venue',
    'Event',
    'EventFilter',
    # Constants
    'CATEGORY_INFO',
    'ARRONDISSEMENTS',
    # Helpers
    'price_to_budget',
    'get_category_info',
    'get_arrondissement_info',
    'generate_slug',
]


