/**
 * 🎭 Artify - Événements réels
 * Ce fichier gère la récupération des événements depuis l'API backend
 */

// Types pour les événements réels
export interface RealEvent {
  id: string;
  title: string;
  description: string;
  main_category: string;
  sub_category: string | null;
  date: string;
  start_time: string | null;
  end_time: string | null;
  time_of_day: 'jour' | 'soir' | 'nuit';
  venue: string;
  address: string;
  arrondissement: number | null;
  price: number;
  price_max: number | null;
  source_url: string;
  source_name: string;
  image_url: string | null;
  duration: number | null;
  booking_required: boolean;
  tags: string[];
  latitude: number | null;
  longitude: number | null;
  verified: boolean;
}

// Configuration de l'API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

/**
 * Récupère tous les événements avec filtres optionnels
 */
export async function fetchEvents(filters?: {
  categories?: string[];
  date_from?: string;
  date_to?: string;
  arrondissements?: number[];
  price_max?: number;
  time_of_day?: string[];
  limit?: number;
  offset?: number;
  verified_only?: boolean;
}): Promise<{ events: RealEvent[]; count: number }> {
  try {
    const params = new URLSearchParams();
    
    if (filters?.categories?.length) {
      params.set('categories', filters.categories.join(','));
    }
    if (filters?.date_from) {
      params.set('date_from', filters.date_from);
    }
    if (filters?.date_to) {
      params.set('date_to', filters.date_to);
    }
    if (filters?.arrondissements?.length) {
      params.set('arrondissements', filters.arrondissements.join(','));
    }
    if (filters?.price_max !== undefined) {
      params.set('price_max', String(filters.price_max));
    }
    if (filters?.time_of_day?.length) {
      params.set('time_of_day', filters.time_of_day.join(','));
    }
    if (filters?.limit) {
      params.set('limit', String(filters.limit));
    }
    if (filters?.offset) {
      params.set('offset', String(filters.offset));
    }
    if (filters?.verified_only) {
      params.set('verified_only', 'true');
    }
    
    const response = await fetch(`${API_BASE_URL}/api/events?${params.toString()}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.success) {
      return {
        events: data.events,
        count: data.count,
      };
    } else {
      throw new Error(data.error || 'Unknown error');
    }
  } catch (error) {
    console.error('Error fetching events:', error);
    // Fallback vers les données locales si l'API n'est pas disponible
    return { events: [], count: 0 };
  }
}

/**
 * Récupère un événement par son ID
 */
export async function fetchEvent(eventId: string): Promise<RealEvent | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/events/${eventId}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        return null;
      }
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.success) {
      return data.event;
    }
    
    return null;
  } catch (error) {
    console.error('Error fetching event:', error);
    return null;
  }
}

/**
 * Récupère les événements à venir
 */
export async function fetchUpcomingEvents(days: number = 30, limit: number = 50): Promise<RealEvent[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/events/upcoming?days=${days}&limit=${limit}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.success) {
      return data.events;
    }
    
    return [];
  } catch (error) {
    console.error('Error fetching upcoming events:', error);
    return [];
  }
}

/**
 * Recherche d'événements
 */
export async function searchEvents(query: string, limit: number = 50): Promise<RealEvent[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/events/search?q=${encodeURIComponent(query)}&limit=${limit}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.success) {
      return data.events;
    }
    
    return [];
  } catch (error) {
    console.error('Error searching events:', error);
    return [];
  }
}

/**
 * Récupère les statistiques
 */
export async function fetchStats(): Promise<{
  total_events: number;
  by_category: Record<string, number>;
  free_events: number;
  average_price: number;
  verified_events: number;
} | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/events/stats`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.success) {
      return data.stats;
    }
    
    return null;
  } catch (error) {
    console.error('Error fetching stats:', error);
    return null;
  }
}

/**
 * Récupère les catégories disponibles
 */
export async function fetchCategories(): Promise<Record<string, {
  label: string;
  emoji: string;
  subCategories: string[];
}>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/events/categories`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.success) {
      return data.categories;
    }
    
    // Fallback
    return {};
  } catch (error) {
    console.error('Error fetching categories:', error);
    // Fallback vers les catégories par défaut
    return {
      spectacles: { label: 'Spectacles', emoji: '🎭', subCategories: [] },
      musique: { label: 'Musique', emoji: '🎵', subCategories: [] },
      arts_visuels: { label: 'Arts Visuels', emoji: '🎨', subCategories: [] },
      ateliers: { label: 'Ateliers', emoji: '🖌️', subCategories: [] },
      sport: { label: 'Sport', emoji: '🏃', subCategories: [] },
      gastronomie: { label: 'Gastronomie', emoji: '🍷', subCategories: [] },
      culture: { label: 'Culture', emoji: '📚', subCategories: [] },
      nightlife: { label: 'Vie Nocturne', emoji: '🌙', subCategories: [] },
      rencontres: { label: 'Rencontres', emoji: '👥', subCategories: [] },
    };
  }
}

/**
 * Vérifie si l'API est disponible
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Convertit un RealEvent vers le format Event utilisé par le frontend
 */
export function convertToFrontendEvent(event: RealEvent): {
  id: string;
  title: string;
  date: string;
  startTime: string | null;
  timeOfDay: 'jour' | 'soir' | 'nuit';
  venue: string;
  address: string;
  arrondissement: number | null;
  price: number;
  description: string;
  sourceUrl: string;
  mainCategory: string;
  subCategory: string | null;
  ambiance: string[];
  duration: number | null;
  image: string | null;
  bookingRequired: boolean;
  verified: boolean;
} {
  return {
    id: event.id,
    title: event.title,
    date: event.date,
    startTime: event.start_time,
    timeOfDay: event.time_of_day,
    venue: event.venue,
    address: event.address,
    arrondissement: event.arrondissement,
    price: event.price,
    description: event.description,
    sourceUrl: event.source_url,
    mainCategory: event.main_category,
    subCategory: event.sub_category,
    ambiance: event.tags || [],
    duration: event.duration,
    image: event.image_url,
    bookingRequired: event.booking_required,
    verified: event.verified,
  };
}


