/**
 * 🎵 Artify Recommendation Engine - Types
 * Système de recommandations inspiré de Spotify
 */

import { MainCategory, SubCategory, Budget, TimeOfDay, Ambiance, Arrondissement } from '@/data/categories';

// ============================================================================
// USER PROFILE TYPES
// ============================================================================

export interface UserInteraction {
  eventId: string;
  type: 'view' | 'click' | 'favorite' | 'attend' | 'share' | 'skip';
  timestamp: number;
  duration?: number; // temps passé sur la page (ms)
}

export interface UserPreferences {
  // Préférences explicites (choisies par l'utilisateur)
  explicit: {
    categories: MainCategory[];
    subCategories: SubCategory[];
    budgets: Budget[];
    times: TimeOfDay[];
    ambiances: Ambiance[];
    arrondissements: Arrondissement[];
  };
  
  // Préférences implicites (déduites du comportement)
  implicit: {
    categoryScores: Record<MainCategory, number>;
    subCategoryScores: Record<SubCategory, number>;
    budgetScores: Record<Budget, number>;
    timeScores: Record<TimeOfDay, number>;
    ambianceScores: Record<Ambiance, number>;
    venueScores: Record<string, number>;
    priceRange: { min: number; max: number; avg: number };
  };
}

export interface UserProfile {
  id: string;
  createdAt: number;
  updatedAt: number;
  
  preferences: UserPreferences;
  interactions: UserInteraction[];
  
  // Stats
  totalViews: number;
  totalFavorites: number;
  totalAttended: number;
  
  // Taste profile (comme Spotify)
  tasteProfile: {
    adventurousness: number; // 0-1, propension à découvrir de nouvelles choses
    socialLevel: number; // 0-1, préférence pour événements sociaux
    budgetSensitivity: number; // 0-1, sensibilité au prix
    timeConsistency: number; // 0-1, régularité dans les horaires
    categoryDiversity: number; // 0-1, diversité des intérêts
  };
  
  // Discover Weekly state
  lastDiscoverWeekly: number;
  discoverWeeklyEventIds: string[];
}

// ============================================================================
// RECOMMENDATION TYPES
// ============================================================================

export interface EventScore {
  eventId: string;
  totalScore: number;
  breakdown: {
    categoryMatch: number;      // 0-100 - match avec catégories préférées
    contentSimilarity: number;  // 0-100 - similarité avec événements aimés
    collaborativeScore: number; // 0-100 - "les utilisateurs similaires aiment aussi"
    trendingBonus: number;      // 0-100 - événements populaires
    diversityBonus: number;     // 0-100 - bonus pour diversité
    recencyBonus: number;       // 0-100 - événements récents/à venir
    personalizedBonus: number;  // 0-100 - facteurs personnalisés
  };
  reasons: RecommendationReason[];
}

export interface RecommendationReason {
  type: 
    | 'category_match' 
    | 'similar_event' 
    | 'popular_nearby' 
    | 'trending' 
    | 'discover_new'
    | 'friends_like'
    | 'because_you_liked'
    | 'perfect_timing'
    | 'budget_friendly'
    | 'hidden_gem';
  text: string;
  emoji: string;
  relatedEventId?: string;
}

export interface RecommendationResult {
  events: EventWithScore[];
  sections: RecommendationSection[];
  generatedAt: number;
  userProfileSnapshot: Partial<UserProfile>;
}

export interface EventWithScore {
  event: any; // Event type from categories.ts
  score: EventScore;
  primaryReason: RecommendationReason;
}

export interface RecommendationSection {
  id: string;
  title: string;
  subtitle: string;
  emoji: string;
  type: 
    | 'for_you'           // Personnalisé global
    | 'discover_weekly'   // Découvertes de la semaine
    | 'trending'          // Tendances
    | 'because_you_liked' // Car vous avez aimé X
    | 'category_mix'      // Mix d'une catégorie
    | 'hidden_gems'       // Pépites cachées
    | 'this_weekend'      // Ce week-end
    | 'near_you'          // Près de chez vous
    | 'budget_friendly';  // Petit budget
  eventIds: string[];
  reason?: string;
}

// ============================================================================
// ALGORITHM CONFIG
// ============================================================================

export interface RecommendationConfig {
  weights: {
    categoryMatch: number;
    contentSimilarity: number;
    collaborativeFiltering: number;
    trendingBonus: number;
    diversityBonus: number;
    recencyBonus: number;
    personalizedBonus: number;
  };
  
  // Facteurs de décroissance
  decay: {
    interactionAge: number; // Plus anciennes interactions comptent moins
    viewWithoutAction: number; // Vue sans action = moins important
  };
  
  // Seuils
  thresholds: {
    minScoreForRecommendation: number;
    maxSimilarEvents: number;
    discoverWeeklySize: number;
  };
}

export const DEFAULT_CONFIG: RecommendationConfig = {
  weights: {
    categoryMatch: 0.25,
    contentSimilarity: 0.20,
    collaborativeFiltering: 0.20,
    trendingBonus: 0.10,
    diversityBonus: 0.10,
    recencyBonus: 0.10,
    personalizedBonus: 0.05,
  },
  decay: {
    interactionAge: 0.95, // perte de 5% par semaine
    viewWithoutAction: 0.3,
  },
  thresholds: {
    minScoreForRecommendation: 20,
    maxSimilarEvents: 10,
    discoverWeeklySize: 20,
  },
};


