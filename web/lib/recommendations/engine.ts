/**
 * 🎵 Artify AI Recommendation Engine
 * Système de recommandations inspiré de Spotify
 * Maintenant alimenté par des événements RÉELS
 */

import { Event, MainCategory, SubCategory, Budget, TimeOfDay, Ambiance } from '@/data/categories';
import {
  UserProfile,
  UserInteraction,
  EventScore,
  RecommendationReason,
  RecommendationResult,
  RecommendationSection,
  EventWithScore,
  RecommendationConfig,
  DEFAULT_CONFIG,
} from './types';

// URL de l'API des événements réels
const EVENTS_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

// Cache des événements pour éviter trop de requêtes
let eventsCache: Event[] = [];
let cacheTimestamp = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

/**
 * Récupère les événements réels depuis l'API
 */
async function fetchRealEvents(): Promise<Event[]> {
  // Vérifier le cache
  if (eventsCache.length > 0 && Date.now() - cacheTimestamp < CACHE_TTL) {
    return eventsCache;
  }
  
  try {
    const response = await fetch(`${EVENTS_API_URL}/api/events?limit=200`);
    if (!response.ok) {
      console.warn('API not available, using cached events');
      return eventsCache;
    }
    
    const data = await response.json();
    if (data.success && data.events) {
      // Convertir les événements API vers le format Event
      eventsCache = data.events.map((e: any) => ({
        id: e.id,
        title: e.title,
        description: e.description,
        mainCategory: e.main_category as MainCategory,
        subCategory: e.sub_category,
        date: e.date,
        startTime: e.start_time,
        endTime: e.end_time,
        timeOfDay: e.time_of_day as TimeOfDay,
        venue: e.venue,
        address: e.address,
        arrondissement: e.arrondissement,
        price: e.price,
        budget: e.price === 0 ? 'gratuit' : e.price <= 20 ? 'petit' : e.price <= 50 ? 'moyen' : 'premium',
        sourceUrl: e.source_url,
        image: e.image_url,
        ambiance: e.tags || [],
        duration: e.duration,
        bookingRequired: e.booking_required,
        verified: e.verified,
      }));
      cacheTimestamp = Date.now();
      console.log(`✅ ${eventsCache.length} événements réels chargés`);
    }
  } catch (error) {
    console.warn('Error fetching real events:', error);
  }
  
  return eventsCache;
}

// ============================================================================
// RECOMMENDATION ENGINE
// ============================================================================

export class ArtifyRecommendationEngine {
  private config: RecommendationConfig;
  private events: Event[];
  
  constructor(config: RecommendationConfig = DEFAULT_CONFIG, initialEvents: Event[] = []) {
    this.config = config;
    this.events = initialEvents;
  }
  
  /**
   * Met à jour les événements (appelé après récupération API)
   */
  public setEvents(events: Event[]): void {
    this.events = events;
  }
  
  /**
   * Charge les événements depuis l'API
   */
  public async loadEvents(): Promise<void> {
    this.events = await fetchRealEvents();
  }
  
  /**
   * Génère des recommandations personnalisées pour un utilisateur
   */
  public generateRecommendations(
    userProfile: UserProfile,
    filters?: {
      categories?: MainCategory[];
      budgets?: Budget[];
      times?: TimeOfDay[];
      limit?: number;
    }
  ): RecommendationResult {
    const limit = filters?.limit || 50;
    
    // Filtrer les événements de base
    let candidateEvents = this.filterEvents(this.events, filters);
    
    // Calculer les scores pour chaque événement
    const scoredEvents = candidateEvents.map(event => 
      this.scoreEvent(event, userProfile)
    );
    
    // Trier par score
    scoredEvents.sort((a, b) => b.score.totalScore - a.score.totalScore);
    
    // Appliquer la diversification
    const diversifiedEvents = this.diversifyResults(scoredEvents, userProfile);
    
    // Créer les sections thématiques
    const sections = this.createSections(diversifiedEvents, userProfile);
    
    return {
      events: diversifiedEvents.slice(0, limit),
      sections,
      generatedAt: Date.now(),
      userProfileSnapshot: {
        id: userProfile.id,
        tasteProfile: userProfile.tasteProfile,
      },
    };
  }
  
  /**
   * Génère "Discover Weekly" - événements hors de la zone de confort
   */
  public generateDiscoverWeekly(userProfile: UserProfile): EventWithScore[] {
    const userTopCategories = this.getTopCategories(userProfile, 3);
    
    // Trouver des événements dans des catégories moins explorées
    const unexploredEvents = this.events.filter(event => 
      !userTopCategories.includes(event.mainCategory)
    );
    
    // Scorer mais avec bonus pour la nouveauté
    const scored = unexploredEvents.map(event => {
      const baseScore = this.scoreEvent(event, userProfile);
      // Ajouter un bonus "découverte"
      baseScore.score.breakdown.diversityBonus += 30;
      baseScore.score.totalScore = this.calculateTotalScore(baseScore.score.breakdown);
      baseScore.primaryReason = {
        type: 'discover_new',
        text: 'Sortez de votre zone de confort',
        emoji: '✨',
      };
      return baseScore;
    });
    
    scored.sort((a, b) => b.score.totalScore - a.score.totalScore);
    
    return scored.slice(0, this.config.thresholds.discoverWeeklySize);
  }
  
  /**
   * "Car vous avez aimé X" - événements similaires
   */
  public findSimilarEvents(eventId: string, userProfile: UserProfile): EventWithScore[] {
    const sourceEvent = this.events.find(e => e.id === eventId);
    if (!sourceEvent) return [];
    
    const similar = this.events
      .filter(e => e.id !== eventId)
      .map(event => ({
        event,
        similarity: this.calculateEventSimilarity(sourceEvent, event),
      }))
      .filter(e => e.similarity > 0.3)
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, 10);
    
    return similar.map(({ event, similarity }) => {
      const scored = this.scoreEvent(event, userProfile);
      scored.primaryReason = {
        type: 'because_you_liked',
        text: `Car vous avez aimé "${sourceEvent.title}"`,
        emoji: '💫',
        relatedEventId: sourceEvent.id,
      };
      return scored;
    });
  }
  
  /**
   * Événements tendance / populaires
   */
  public getTrendingEvents(limit: number = 10): EventWithScore[] {
    // Simuler des scores de popularité (en production, basé sur vraies données)
    const trending = this.events
      .map(event => {
        const trendScore = this.calculateTrendScore(event);
        return {
          event,
          score: {
            eventId: event.id,
            totalScore: trendScore,
            breakdown: {
              categoryMatch: 0,
              contentSimilarity: 0,
              collaborativeScore: 0,
              trendingBonus: trendScore,
              diversityBonus: 0,
              recencyBonus: 0,
              personalizedBonus: 0,
            },
            reasons: [{
              type: 'trending' as const,
              text: 'Très populaire en ce moment',
              emoji: '🔥',
            }],
          },
          primaryReason: {
            type: 'trending' as const,
            text: 'Très populaire en ce moment',
            emoji: '🔥',
          },
        } as EventWithScore;
      })
      .sort((a, b) => b.score.totalScore - a.score.totalScore)
      .slice(0, limit);
    
    return trending;
  }
  
  // ============================================================================
  // SCORING METHODS
  // ============================================================================
  
  private scoreEvent(event: Event, userProfile: UserProfile): EventWithScore {
    const breakdown = {
      categoryMatch: this.scoreCategoryMatch(event, userProfile),
      contentSimilarity: this.scoreContentSimilarity(event, userProfile),
      collaborativeScore: this.scoreCollaborative(event, userProfile),
      trendingBonus: this.calculateTrendScore(event) * 0.3,
      diversityBonus: this.scoreDiversity(event, userProfile),
      recencyBonus: this.scoreRecency(event),
      personalizedBonus: this.scorePersonalized(event, userProfile),
    };
    
    const totalScore = this.calculateTotalScore(breakdown);
    const reasons = this.generateReasons(event, breakdown, userProfile);
    
    return {
      event,
      score: {
        eventId: event.id,
        totalScore,
        breakdown,
        reasons,
      },
      primaryReason: reasons[0] || {
        type: 'category_match',
        text: 'Recommandé pour vous',
        emoji: '⭐',
      },
    };
  }
  
  private scoreCategoryMatch(event: Event, userProfile: UserProfile): number {
    let score = 0;
    
    // Match avec catégories explicites
    if (userProfile.preferences.explicit.categories.includes(event.mainCategory)) {
      score += 50;
    }
    
    // Match avec sous-catégories
    if (userProfile.preferences.explicit.subCategories.includes(event.subCategory)) {
      score += 30;
    }
    
    // Scores implicites
    const implicitScore = userProfile.preferences.implicit.categoryScores[event.mainCategory] || 0;
    score += implicitScore * 20;
    
    return Math.min(100, score);
  }
  
  private scoreContentSimilarity(event: Event, userProfile: UserProfile): number {
    // Trouver les événements les plus aimés par l'utilisateur
    const likedEventIds = userProfile.interactions
      .filter(i => i.type === 'favorite' || i.type === 'attend')
      .map(i => i.eventId);
    
    if (likedEventIds.length === 0) return 30; // Score par défaut
    
    const likedEvents = this.events.filter(e => likedEventIds.includes(e.id));
    
    // Calculer la similarité moyenne avec les événements aimés
    const similarities = likedEvents.map(liked => 
      this.calculateEventSimilarity(liked, event)
    );
    
    const avgSimilarity = similarities.length > 0 
      ? similarities.reduce((a, b) => a + b, 0) / similarities.length 
      : 0;
    
    return avgSimilarity * 100;
  }
  
  private scoreCollaborative(event: Event, userProfile: UserProfile): number {
    // Simuler le filtrage collaboratif
    // En production, basé sur les comportements d'utilisateurs similaires
    const tasteMatch = userProfile.tasteProfile.adventurousness * 0.3 +
      (1 - userProfile.tasteProfile.budgetSensitivity) * 0.3 +
      userProfile.tasteProfile.socialLevel * 0.4;
    
    // Bonus pour événements sociaux si l'utilisateur est social
    if (event.ambiance.includes('social') && userProfile.tasteProfile.socialLevel > 0.6) {
      return 70;
    }
    
    return 50 * tasteMatch;
  }
  
  private calculateTrendScore(event: Event): number {
    // Simuler la popularité basée sur les caractéristiques de l'événement
    let score = 50;
    
    // Événements gratuits sont populaires
    if (event.price === 0) score += 20;
    
    // Événements de nuit sont tendance
    if (event.timeOfDay === 'nuit') score += 15;
    
    // Certaines catégories sont plus tendance
    const trendyCategories: MainCategory[] = ['nightlife', 'musique', 'gastronomie'];
    if (trendyCategories.includes(event.mainCategory)) score += 15;
    
    return Math.min(100, score);
  }
  
  private scoreDiversity(event: Event, userProfile: UserProfile): number {
    // Bonus pour des catégories moins explorées
    const categoryCount = userProfile.preferences.implicit.categoryScores[event.mainCategory] || 0;
    
    if (categoryCount < 2) {
      return 40 * userProfile.tasteProfile.adventurousness;
    }
    
    return 10;
  }
  
  private scoreRecency(event: Event): number {
    const eventDate = new Date(event.date);
    const now = new Date();
    const daysUntil = (eventDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);
    
    // Événements cette semaine = bonus max
    if (daysUntil >= 0 && daysUntil <= 7) return 80;
    if (daysUntil > 7 && daysUntil <= 14) return 60;
    if (daysUntil > 14 && daysUntil <= 30) return 40;
    
    return 20;
  }
  
  private scorePersonalized(event: Event, userProfile: UserProfile): number {
    let score = 0;
    
    // Budget match
    if (userProfile.preferences.explicit.budgets.includes(event.budget)) {
      score += 30;
    }
    
    // Horaire match
    if (userProfile.preferences.explicit.times.includes(event.timeOfDay)) {
      score += 30;
    }
    
    // Ambiance match
    const ambianceMatch = event.ambiance.some(a => 
      userProfile.preferences.explicit.ambiances.includes(a)
    );
    if (ambianceMatch) score += 20;
    
    // Arrondissement match
    if (userProfile.preferences.explicit.arrondissements.includes(event.arrondissement)) {
      score += 20;
    }
    
    return Math.min(100, score);
  }
  
  private calculateTotalScore(breakdown: EventScore['breakdown']): number {
    const { weights } = this.config;
    
    return (
      breakdown.categoryMatch * weights.categoryMatch +
      breakdown.contentSimilarity * weights.contentSimilarity +
      breakdown.collaborativeScore * weights.collaborativeFiltering +
      breakdown.trendingBonus * weights.trendingBonus +
      breakdown.diversityBonus * weights.diversityBonus +
      breakdown.recencyBonus * weights.recencyBonus +
      breakdown.personalizedBonus * weights.personalizedBonus
    );
  }
  
  // ============================================================================
  // SIMILARITY CALCULATION
  // ============================================================================
  
  private calculateEventSimilarity(eventA: Event, eventB: Event): number {
    let similarity = 0;
    let factors = 0;
    
    // Catégorie principale
    if (eventA.mainCategory === eventB.mainCategory) {
      similarity += 0.4;
    }
    factors += 0.4;
    
    // Sous-catégorie
    if (eventA.subCategory === eventB.subCategory) {
      similarity += 0.3;
    }
    factors += 0.3;
    
    // Budget similaire
    if (eventA.budget === eventB.budget) {
      similarity += 0.1;
    }
    factors += 0.1;
    
    // Horaire similaire
    if (eventA.timeOfDay === eventB.timeOfDay) {
      similarity += 0.1;
    }
    factors += 0.1;
    
    // Ambiance commune
    const commonAmbiance = eventA.ambiance.filter(a => eventB.ambiance.includes(a));
    similarity += (commonAmbiance.length / Math.max(eventA.ambiance.length, 1)) * 0.1;
    factors += 0.1;
    
    return similarity / factors;
  }
  
  // ============================================================================
  // REASON GENERATION
  // ============================================================================
  
  private generateReasons(
    event: Event,
    breakdown: EventScore['breakdown'],
    userProfile: UserProfile
  ): RecommendationReason[] {
    const reasons: RecommendationReason[] = [];
    
    if (breakdown.categoryMatch >= 50) {
      reasons.push({
        type: 'category_match',
        text: `Dans vos catégories favorites`,
        emoji: '🎯',
      });
    }
    
    if (breakdown.contentSimilarity >= 60) {
      reasons.push({
        type: 'similar_event',
        text: 'Similaire aux événements que vous aimez',
        emoji: '💫',
      });
    }
    
    if (breakdown.trendingBonus >= 70) {
      reasons.push({
        type: 'trending',
        text: 'Très populaire en ce moment',
        emoji: '🔥',
      });
    }
    
    if (breakdown.diversityBonus >= 30) {
      reasons.push({
        type: 'discover_new',
        text: 'Pour élargir vos horizons',
        emoji: '✨',
      });
    }
    
    if (event.price === 0) {
      reasons.push({
        type: 'budget_friendly',
        text: 'Gratuit !',
        emoji: '🆓',
      });
    }
    
    if (breakdown.recencyBonus >= 70) {
      reasons.push({
        type: 'perfect_timing',
        text: 'Cette semaine',
        emoji: '📅',
      });
    }
    
    // Fallback
    if (reasons.length === 0) {
      reasons.push({
        type: 'category_match',
        text: 'Recommandé pour vous',
        emoji: '⭐',
      });
    }
    
    return reasons;
  }
  
  // ============================================================================
  // HELPER METHODS
  // ============================================================================
  
  private filterEvents(events: Event[], filters?: {
    categories?: MainCategory[];
    budgets?: Budget[];
    times?: TimeOfDay[];
  }): Event[] {
    if (!filters) return events;
    
    return events.filter(event => {
      const categoryMatch = !filters.categories?.length || 
        filters.categories.includes(event.mainCategory);
      const budgetMatch = !filters.budgets?.length || 
        filters.budgets.includes(event.budget);
      const timeMatch = !filters.times?.length || 
        filters.times.includes(event.timeOfDay);
      
      return categoryMatch && budgetMatch && timeMatch;
    });
  }
  
  private getTopCategories(userProfile: UserProfile, count: number): MainCategory[] {
    const scores = userProfile.preferences.implicit.categoryScores;
    return Object.entries(scores)
      .sort(([, a], [, b]) => b - a)
      .slice(0, count)
      .map(([category]) => category as MainCategory);
  }
  
  private diversifyResults(events: EventWithScore[], userProfile: UserProfile): EventWithScore[] {
    // Éviter trop d'événements de la même catégorie consécutifs
    const diversified: EventWithScore[] = [];
    const categoryCount: Record<string, number> = {};
    const maxPerCategory = 3;
    
    for (const event of events) {
      const cat = event.event.mainCategory;
      if (!categoryCount[cat]) categoryCount[cat] = 0;
      
      if (categoryCount[cat] < maxPerCategory) {
        diversified.push(event);
        categoryCount[cat]++;
      }
    }
    
    // Ajouter les événements restants à la fin
    for (const event of events) {
      if (!diversified.includes(event)) {
        diversified.push(event);
      }
    }
    
    return diversified;
  }
  
  private createSections(
    events: EventWithScore[], 
    userProfile: UserProfile
  ): RecommendationSection[] {
    const sections: RecommendationSection[] = [];
    
    // Section "Pour vous"
    sections.push({
      id: 'for-you',
      title: 'Pour vous',
      subtitle: 'Sélection personnalisée',
      emoji: '✨',
      type: 'for_you',
      eventIds: events.slice(0, 8).map(e => e.event.id),
    });
    
    // Section "Tendances"
    const trending = events
      .filter(e => e.score.breakdown.trendingBonus >= 60)
      .slice(0, 6);
    if (trending.length > 0) {
      sections.push({
        id: 'trending',
        title: 'Tendances',
        subtitle: 'Les plus populaires',
        emoji: '🔥',
        type: 'trending',
        eventIds: trending.map(e => e.event.id),
      });
    }
    
    // Section "Ce week-end"
    const weekend = events.filter(e => {
      const date = new Date(e.event.date);
      const today = new Date();
      const daysUntil = (date.getTime() - today.getTime()) / (1000 * 60 * 60 * 24);
      return daysUntil >= 0 && daysUntil <= 3;
    }).slice(0, 6);
    
    if (weekend.length > 0) {
      sections.push({
        id: 'this-weekend',
        title: 'Ce week-end',
        subtitle: 'Ne ratez pas ces événements',
        emoji: '📅',
        type: 'this_weekend',
        eventIds: weekend.map(e => e.event.id),
      });
    }
    
    // Section "Petit budget"
    const budgetFriendly = events
      .filter(e => e.event.price <= 20)
      .slice(0, 6);
    if (budgetFriendly.length > 0) {
      sections.push({
        id: 'budget-friendly',
        title: 'Petit budget',
        subtitle: 'Événements gratuits ou pas chers',
        emoji: '💸',
        type: 'budget_friendly',
        eventIds: budgetFriendly.map(e => e.event.id),
      });
    }
    
    // Section par catégorie favorite
    const topCategory = this.getTopCategories(userProfile, 1)[0];
    if (topCategory) {
      const categoryEvents = events
        .filter(e => e.event.mainCategory === topCategory)
        .slice(0, 6);
      if (categoryEvents.length > 0) {
        sections.push({
          id: `category-${topCategory}`,
          title: `Mix ${this.getCategoryLabel(topCategory)}`,
          subtitle: 'Votre catégorie préférée',
          emoji: this.getCategoryEmoji(topCategory),
          type: 'category_mix',
          eventIds: categoryEvents.map(e => e.event.id),
        });
      }
    }
    
    // Section "Pépites cachées" (événements moins populaires mais bien notés)
    const hiddenGems = events
      .filter(e => e.score.breakdown.trendingBonus < 50 && e.score.totalScore > 50)
      .slice(0, 6);
    if (hiddenGems.length > 0) {
      sections.push({
        id: 'hidden-gems',
        title: 'Pépites cachées',
        subtitle: 'Des trésors à découvrir',
        emoji: '💎',
        type: 'hidden_gems',
        eventIds: hiddenGems.map(e => e.event.id),
      });
    }
    
    return sections;
  }
  
  private getCategoryLabel(category: MainCategory): string {
    const labels: Record<MainCategory, string> = {
      spectacles: 'Spectacles',
      musique: 'Musique',
      arts_visuels: 'Arts visuels',
      ateliers: 'Ateliers',
      sport: 'Sport',
      rencontres: 'Rencontres',
      gastronomie: 'Gastronomie',
      culture: 'Culture',
      nightlife: 'Nightlife',
    };
    return labels[category] || category;
  }
  
  private getCategoryEmoji(category: MainCategory): string {
    const emojis: Record<MainCategory, string> = {
      spectacles: '🎭',
      musique: '🎵',
      arts_visuels: '🎨',
      ateliers: '🖌️',
      sport: '🏃',
      rencontres: '👥',
      gastronomie: '🍷',
      culture: '📚',
      nightlife: '🌙',
    };
    return emojis[category] || '📌';
  }
}

// Singleton instance
export const recommendationEngine = new ArtifyRecommendationEngine();

