/**
 * 🎵 Artify User Profile Manager
 * Gestion des profils utilisateurs et leurs préférences
 */

import { MainCategory, SubCategory, Budget, TimeOfDay, Ambiance, Arrondissement } from '@/data/categories';
import { UserProfile, UserInteraction, UserPreferences } from './types';

// ============================================================================
// DEFAULT PROFILE
// ============================================================================

export function createDefaultProfile(userId?: string): UserProfile {
  const now = Date.now();
  
  return {
    id: userId || `user_${now}_${Math.random().toString(36).substr(2, 9)}`,
    createdAt: now,
    updatedAt: now,
    
    preferences: {
      explicit: {
        categories: [],
        subCategories: [],
        budgets: [],
        times: [],
        ambiances: [],
        arrondissements: [],
      },
      implicit: {
        categoryScores: {} as Record<MainCategory, number>,
        subCategoryScores: {} as Record<SubCategory, number>,
        budgetScores: {} as Record<Budget, number>,
        timeScores: {} as Record<TimeOfDay, number>,
        ambianceScores: {} as Record<Ambiance, number>,
        venueScores: {},
        priceRange: { min: 0, max: 100, avg: 30 },
      },
    },
    
    interactions: [],
    totalViews: 0,
    totalFavorites: 0,
    totalAttended: 0,
    
    tasteProfile: {
      adventurousness: 0.5,
      socialLevel: 0.5,
      budgetSensitivity: 0.5,
      timeConsistency: 0.5,
      categoryDiversity: 0.5,
    },
    
    lastDiscoverWeekly: 0,
    discoverWeeklyEventIds: [],
  };
}

// ============================================================================
// USER PROFILE MANAGER
// ============================================================================

export class UserProfileManager {
  private profile: UserProfile;
  private storageKey = 'artify_user_profile';
  
  constructor() {
    this.profile = this.loadProfile();
  }
  
  /**
   * Charge le profil depuis le localStorage
   */
  private loadProfile(): UserProfile {
    if (typeof window === 'undefined') {
      return createDefaultProfile();
    }
    
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        const parsed = JSON.parse(stored);
        return { ...createDefaultProfile(), ...parsed };
      }
    } catch (e) {
      console.error('Error loading user profile:', e);
    }
    
    return createDefaultProfile();
  }
  
  /**
   * Sauvegarde le profil
   */
  private saveProfile(): void {
    if (typeof window === 'undefined') return;
    
    try {
      this.profile.updatedAt = Date.now();
      localStorage.setItem(this.storageKey, JSON.stringify(this.profile));
    } catch (e) {
      console.error('Error saving user profile:', e);
    }
  }
  
  /**
   * Obtient le profil actuel
   */
  public getProfile(): UserProfile {
    return this.profile;
  }
  
  /**
   * Met à jour les préférences explicites
   */
  public setExplicitPreferences(prefs: Partial<UserPreferences['explicit']>): void {
    this.profile.preferences.explicit = {
      ...this.profile.preferences.explicit,
      ...prefs,
    };
    this.updateTasteProfile();
    this.saveProfile();
  }
  
  /**
   * Enregistre une interaction utilisateur
   */
  public recordInteraction(interaction: Omit<UserInteraction, 'timestamp'>): void {
    const fullInteraction: UserInteraction = {
      ...interaction,
      timestamp: Date.now(),
    };
    
    this.profile.interactions.push(fullInteraction);
    
    // Limiter l'historique à 1000 interactions
    if (this.profile.interactions.length > 1000) {
      this.profile.interactions = this.profile.interactions.slice(-1000);
    }
    
    // Mettre à jour les compteurs
    switch (interaction.type) {
      case 'view':
        this.profile.totalViews++;
        break;
      case 'favorite':
        this.profile.totalFavorites++;
        break;
      case 'attend':
        this.profile.totalAttended++;
        break;
    }
    
    // Mettre à jour les préférences implicites
    this.updateImplicitPreferences(fullInteraction);
    this.updateTasteProfile();
    this.saveProfile();
  }
  
  /**
   * Met à jour les préférences implicites basées sur une interaction
   */
  private updateImplicitPreferences(interaction: UserInteraction): void {
    // Trouver l'événement correspondant
    const event = this.getEventById(interaction.eventId);
    if (!event) return;
    
    const weight = this.getInteractionWeight(interaction.type);
    
    // Mettre à jour les scores de catégorie
    const catScores = this.profile.preferences.implicit.categoryScores;
    catScores[event.mainCategory as MainCategory] = 
      (catScores[event.mainCategory as MainCategory] || 0) + weight;
    
    // Mettre à jour les scores de sous-catégorie
    const subCatScores = this.profile.preferences.implicit.subCategoryScores;
    subCatScores[event.subCategory as SubCategory] = 
      (subCatScores[event.subCategory as SubCategory] || 0) + weight;
    
    // Mettre à jour les scores de budget
    const budgetScores = this.profile.preferences.implicit.budgetScores;
    budgetScores[event.budget as Budget] = 
      (budgetScores[event.budget as Budget] || 0) + weight;
    
    // Mettre à jour les scores de temps
    const timeScores = this.profile.preferences.implicit.timeScores;
    timeScores[event.timeOfDay as TimeOfDay] = 
      (timeScores[event.timeOfDay as TimeOfDay] || 0) + weight;
    
    // Mettre à jour les scores d'ambiance
    const ambianceScores = this.profile.preferences.implicit.ambianceScores;
    if (event.ambiance) {
      for (const ambiance of event.ambiance) {
        ambianceScores[ambiance as Ambiance] = 
          (ambianceScores[ambiance as Ambiance] || 0) + weight;
      }
    }
    
    // Mettre à jour les scores de lieu
    const venueScores = this.profile.preferences.implicit.venueScores;
    if (event.venue) {
      venueScores[event.venue] = (venueScores[event.venue] || 0) + weight;
    }
    
    // Mettre à jour la gamme de prix moyenne
    const priceRange = this.profile.preferences.implicit.priceRange;
    const prices = this.profile.interactions
      .filter(i => ['favorite', 'attend'].includes(i.type))
      .map(i => {
        const e = this.getEventById(i.eventId);
        return e?.price || 0;
      });
    
    if (prices.length > 0) {
      priceRange.min = Math.min(...prices);
      priceRange.max = Math.max(...prices);
      priceRange.avg = prices.reduce((a, b) => a + b, 0) / prices.length;
    }
  }
  
  /**
   * Obtient le poids d'une interaction
   */
  private getInteractionWeight(type: UserInteraction['type']): number {
    const weights: Record<UserInteraction['type'], number> = {
      view: 0.1,
      click: 0.2,
      favorite: 1.0,
      attend: 1.5,
      share: 0.8,
      skip: -0.3,
    };
    return weights[type] || 0;
  }
  
  /**
   * Met à jour le profil de goût (taste profile)
   */
  private updateTasteProfile(): void {
    const interactions = this.profile.interactions;
    const explicit = this.profile.preferences.explicit;
    const implicit = this.profile.preferences.implicit;
    
    // Adventurousness: diversité des catégories explorées
    const uniqueCategories = new Set(
      interactions
        .map(i => this.getEventById(i.eventId)?.mainCategory)
        .filter(Boolean)
    );
    this.profile.tasteProfile.adventurousness = 
      Math.min(1, uniqueCategories.size / 6);
    
    // Social level: proportion d'événements sociaux
    const socialEvents = interactions.filter(i => {
      const event = this.getEventById(i.eventId);
      return event?.ambiance?.includes('social');
    });
    this.profile.tasteProfile.socialLevel = 
      interactions.length > 0 
        ? socialEvents.length / interactions.length 
        : 0.5;
    
    // Budget sensitivity: basée sur le budget moyen
    const avgPrice = implicit.priceRange.avg;
    this.profile.tasteProfile.budgetSensitivity = 
      avgPrice <= 20 ? 0.8 : avgPrice <= 50 ? 0.5 : 0.2;
    
    // Time consistency: régularité dans les horaires
    const timePrefs = Object.values(implicit.timeScores);
    if (timePrefs.length > 0) {
      const maxTime = Math.max(...timePrefs);
      const totalTime = timePrefs.reduce((a, b) => a + b, 0);
      this.profile.tasteProfile.timeConsistency = 
        totalTime > 0 ? maxTime / totalTime : 0.5;
    }
    
    // Category diversity: spread across categories
    const catScores = Object.values(implicit.categoryScores);
    if (catScores.length > 1) {
      const maxCat = Math.max(...catScores);
      const totalCat = catScores.reduce((a, b) => a + b, 0);
      this.profile.tasteProfile.categoryDiversity = 
        totalCat > 0 ? 1 - (maxCat / totalCat) : 0.5;
    }
  }
  
  /**
   * Réinitialise le profil
   */
  public resetProfile(): void {
    this.profile = createDefaultProfile();
    this.saveProfile();
  }
  
  /**
   * Helper: obtient un événement par ID
   * Note: Les événements sont maintenant chargés depuis l'API réelle
   */
  private getEventById(eventId: string): any | null {
    // Les événements sont maintenant gérés par le moteur de recommandations
    // qui les charge depuis l'API. Cette méthode n'est plus utilisée directement.
    return null;
  }
  
  /**
   * Obtient les événements favoris
   */
  public getFavorites(): string[] {
    return this.profile.interactions
      .filter(i => i.type === 'favorite')
      .map(i => i.eventId);
  }
  
  /**
   * Vérifie si un événement est en favori
   */
  public isFavorite(eventId: string): boolean {
    return this.getFavorites().includes(eventId);
  }
  
  /**
   * Toggle favori
   */
  public toggleFavorite(eventId: string): boolean {
    if (this.isFavorite(eventId)) {
      // Retirer des favoris (ajouter un skip)
      this.recordInteraction({ eventId, type: 'skip' });
      return false;
    } else {
      this.recordInteraction({ eventId, type: 'favorite' });
      return true;
    }
  }
  
  /**
   * Obtient les statistiques du profil
   */
  public getStats(): {
    totalEvents: number;
    topCategories: { category: string; count: number }[];
    avgBudget: string;
    preferredTime: string;
    memberSince: string;
  } {
    const implicit = this.profile.preferences.implicit;
    
    // Top catégories
    const topCategories = Object.entries(implicit.categoryScores)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([category, count]) => ({ category, count }));
    
    // Budget moyen
    const avgPrice = implicit.priceRange.avg;
    let avgBudget = 'Moyen';
    if (avgPrice === 0) avgBudget = 'Gratuit';
    else if (avgPrice <= 20) avgBudget = 'Économique';
    else if (avgPrice <= 50) avgBudget = 'Moyen';
    else avgBudget = 'Premium';
    
    // Horaire préféré
    const topTime = Object.entries(implicit.timeScores)
      .sort(([, a], [, b]) => b - a)[0];
    const timeLabels: Record<string, string> = {
      matin: 'Matin',
      apres_midi: 'Après-midi',
      soir: 'Soirée',
      nuit: 'Nuit',
    };
    const preferredTime = topTime ? timeLabels[topTime[0]] || 'Varié' : 'Varié';
    
    // Membre depuis
    const memberSince = new Date(this.profile.createdAt).toLocaleDateString('fr-FR', {
      month: 'long',
      year: 'numeric',
    });
    
    return {
      totalEvents: this.profile.totalViews,
      topCategories,
      avgBudget,
      preferredTime,
      memberSince,
    };
  }
}

// Singleton pour utilisation côté client
let profileManagerInstance: UserProfileManager | null = null;

export function getUserProfileManager(): UserProfileManager {
  if (typeof window === 'undefined') {
    // Côté serveur, créer une nouvelle instance
    return new UserProfileManager();
  }
  
  if (!profileManagerInstance) {
    profileManagerInstance = new UserProfileManager();
  }
  
  return profileManagerInstance;
}

