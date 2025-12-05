'use client';

import { useState, useEffect, useCallback } from 'react';
import { getUserProfileManager, UserProfile, RecommendationSection } from '@/lib/recommendations';

interface RecommendedEvent {
  id: string;
  title: string;
  date: string;
  startTime?: string;
  price: number;
  mainCategory: string;
  subCategory?: string;
  venue?: string;
  address: string;
  description: string;
  shortDescription?: string;
  sourceUrl?: string;
  timeOfDay: string;
  image?: string;
  arrondissement?: number;
  budget?: string;
  ambiance?: string[];
  _score?: number;
  _reason?: {
    type: string;
    text: string;
    emoji: string;
  };
}

interface UseRecommendationsResult {
  // État
  isLoading: boolean;
  error: string | null;
  events: RecommendedEvent[];
  sections: RecommendationSection[];
  
  // Actions
  fetchRecommendations: (filters?: {
    categories?: string[];
    budgets?: string[];
    times?: string[];
    dateFrom?: string;
    dateTo?: string;
    mode?: 'personalized' | 'discover' | 'trending' | 'similar';
    eventId?: string;
  }) => Promise<void>;
  
  // User profile
  userProfile: UserProfile | null;
  recordView: (eventId: string) => void;
  recordFavorite: (eventId: string) => boolean;
  isFavorite: (eventId: string) => boolean;
  getStats: () => ReturnType<typeof getUserProfileManager>['getStats'] extends () => infer R ? R : never;
}

export function useRecommendations(): UseRecommendationsResult {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [events, setEvents] = useState<RecommendedEvent[]>([]);
  const [sections, setSections] = useState<RecommendationSection[]>([]);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [profileManager, setProfileManager] = useState<ReturnType<typeof getUserProfileManager> | null>(null);

  // Initialiser le profile manager côté client
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const manager = getUserProfileManager();
      setProfileManager(manager);
      setUserProfile(manager.getProfile());
    }
  }, []);

  const fetchRecommendations = useCallback(async (filters?: {
    categories?: string[];
    budgets?: string[];
    times?: string[];
    dateFrom?: string;
    dateTo?: string;
    mode?: 'personalized' | 'discover' | 'trending' | 'similar';
    eventId?: string;
  }) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          categories: filters?.categories || [],
          budgets: filters?.budgets || [],
          times: filters?.times || [],
          dateFrom: filters?.dateFrom,
          dateTo: filters?.dateTo,
          mode: filters?.mode || 'personalized',
          eventId: filters?.eventId,
          userProfile: userProfile ? {
            id: userProfile.id,
            preferences: userProfile.preferences,
            tasteProfile: userProfile.tasteProfile,
            interactions: userProfile.interactions.slice(-50), // Limiter
          } : undefined,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setEvents(data.events);
        setSections(data.sections || []);
      } else {
        setError(data.error || 'Erreur lors du chargement');
      }
    } catch (err) {
      setError('Erreur de connexion');
    } finally {
      setIsLoading(false);
    }
  }, [userProfile]);

  const recordView = useCallback((eventId: string) => {
    if (profileManager) {
      profileManager.recordInteraction({ eventId, type: 'view' });
      setUserProfile(profileManager.getProfile());
    }
  }, [profileManager]);

  const recordFavorite = useCallback((eventId: string): boolean => {
    if (profileManager) {
      const isFav = profileManager.toggleFavorite(eventId);
      setUserProfile(profileManager.getProfile());
      return isFav;
    }
    return false;
  }, [profileManager]);

  const isFavorite = useCallback((eventId: string): boolean => {
    return profileManager?.isFavorite(eventId) || false;
  }, [profileManager]);

  const getStats = useCallback(() => {
    if (profileManager) {
      return profileManager.getStats();
    }
    return {
      totalEvents: 0,
      topCategories: [],
      avgBudget: 'N/A',
      preferredTime: 'N/A',
      memberSince: 'N/A',
    };
  }, [profileManager]);

  return {
    isLoading,
    error,
    events,
    sections,
    fetchRecommendations,
    userProfile,
    recordView,
    recordFavorite,
    isFavorite,
    getStats,
  };
}

// Hook pour obtenir les événements tendance
export function useTrendingEvents() {
  const [events, setEvents] = useState<RecommendedEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch('/api/recommendations?mode=trending')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setEvents(data.featured);
        }
      })
      .finally(() => setIsLoading(false));
  }, []);

  return { events, isLoading };
}

// Hook pour les découvertes
export function useDiscoverEvents() {
  const [events, setEvents] = useState<RecommendedEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch('/api/recommendations?mode=discover')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setEvents(data.featured);
        }
      })
      .finally(() => setIsLoading(false));
  }, []);

  return { events, isLoading };
}

