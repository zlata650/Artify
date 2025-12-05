import { NextRequest, NextResponse } from 'next/server';
import { MainCategory, Budget, TimeOfDay, Event } from '@/data/categories';
import { 
  ArtifyRecommendationEngine,
  createDefaultProfile,
  UserProfile,
  RecommendationResult,
  EventWithScore,
} from '@/lib/recommendations';

// URL de l'API des événements réels
const EVENTS_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

// Instance du moteur de recommandations (sera chargé avec les vrais événements)
const engine = new ArtifyRecommendationEngine();

// Flag pour savoir si les événements ont été chargés
let eventsLoaded = false;
let lastLoadTime = 0;
const RELOAD_INTERVAL = 10000; // Recharger toutes les 10 secondes pour avoir les dernières données

/**
 * Charge les événements réels depuis l'API Python
 */
async function loadRealEvents(): Promise<void> {
  const now = Date.now();
  // Recharger si pas encore chargé ou si le délai est dépassé
  console.log(`🔄 loadRealEvents: eventsLoaded=${eventsLoaded}, timeDiff=${now - lastLoadTime}ms`);
  if (eventsLoaded && (now - lastLoadTime) < RELOAD_INTERVAL) {
    console.log('⏩ Utilisation du cache');
    return;
  }
  
  try {
    // Charger les événements à partir d'aujourd'hui pour avoir les plus pertinents
    const today = new Date().toISOString().split('T')[0];
    const response = await fetch(`${EVENTS_API_URL}/api/events?limit=500&date_from=${today}`, {
      cache: 'no-store', // Pas de cache pour avoir les données à jour
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.success && data.events) {
        // Convertir vers le format Event
        const events: Event[] = data.events.map((e: any) => ({
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
          budget: e.price === 0 ? 'gratuit' : e.price <= 20 ? '0-20' : e.price <= 50 ? '20-50' : '50-100',
          sourceUrl: e.source_url,
          image: e.image_url,
          ambiance: e.tags || [],
          duration: e.duration,
          bookingRequired: e.booking_required,
          verified: e.verified,
        }));
        
        engine.setEvents(events);
        eventsLoaded = true;
        lastLoadTime = Date.now();
        console.log(`✅ Recommandations: ${events.length} événements réels chargés`);
      }
    }
  } catch (error) {
    console.warn('⚠️ API des événements non disponible:', error);
  }
}

// Mapping des anciennes catégories vers les nouvelles
const categoryMapping: { [key: string]: string } = {
  musique: 'musique',
  expositions: 'arts_visuels',
  soirees: 'nightlife',
  gastro: 'gastronomie',
  theatre: 'spectacles',
  lectures: 'culture',
};

// Mapping des anciens budgets vers les nouveaux
const budgetMapping: { [key: string]: string[] } = {
  '0-20': ['gratuit', '0-20'],
  '20-50': ['20-50'],
  '50-80': ['50-100'],
  '50-100': ['50-100'],
  '100+': ['100+'],
  'gratuit': ['gratuit'],
};

// Mapping des anciens temps vers les nouveaux
const timeMapping: { [key: string]: string[] } = {
  jour: ['matin', 'apres_midi'],
  soir: ['soir'],
  nuit: ['nuit'],
  matin: ['matin'],
  apres_midi: ['apres_midi'],
};

function normalizeCategories(categories: string[]): MainCategory[] {
  return categories.flatMap(cat => {
    const mapped = categoryMapping[cat];
    return mapped ? [mapped as MainCategory] : [cat as MainCategory];
  });
}

function normalizeBudgets(budgets: string[]): Budget[] {
  return budgets.flatMap(budget => {
    const mapped = budgetMapping[budget];
    return mapped ? mapped as Budget[] : [budget as Budget];
  });
}

function normalizeTimes(times: string[]): TimeOfDay[] {
  return times.flatMap(time => {
    const mapped = timeMapping[time];
    return mapped ? mapped as TimeOfDay[] : [time as TimeOfDay];
  });
}

/**
 * POST - Obtenir des recommandations personnalisées
 */
export async function POST(request: NextRequest) {
  try {
    // Charger les événements réels si pas encore fait
    await loadRealEvents();
    
    const body = await request.json();
    
    const { 
      categories = [], 
      budgets = [], 
      times = [],
      dateFrom,
      dateTo,
      userProfile: clientProfile,
      mode = 'personalized', // 'personalized' | 'discover' | 'trending' | 'similar'
      eventId, // Pour le mode 'similar'
    } = body as {
      categories: string[];
      budgets: string[];
      times: string[];
      dateFrom?: string;
      dateTo?: string;
      userProfile?: Partial<UserProfile>;
      mode?: 'personalized' | 'discover' | 'trending' | 'similar';
      eventId?: string;
    };

    // Créer ou utiliser le profil utilisateur
    const profile = clientProfile 
      ? { ...createDefaultProfile(), ...clientProfile }
      : createDefaultProfile();
    
    // Mettre à jour les préférences explicites
    profile.preferences.explicit = {
      ...profile.preferences.explicit,
      categories: normalizeCategories(categories),
      budgets: normalizeBudgets(budgets),
      times: normalizeTimes(times),
    };

    let result: { events: EventWithScore[]; sections?: any[] };
    
    switch (mode) {
      case 'discover':
        // Mode découverte - hors zone de confort
        result = {
          events: engine.generateDiscoverWeekly(profile),
        };
        break;
        
      case 'trending':
        // Mode tendances
        result = {
          events: engine.getTrendingEvents(20),
        };
        break;
        
      case 'similar':
        // Événements similaires
        if (!eventId) {
          return NextResponse.json(
            { success: false, error: 'eventId required for similar mode' },
            { status: 400 }
          );
        }
        result = {
          events: engine.findSimilarEvents(eventId, profile),
        };
        break;
        
      default:
        // Mode personnalisé par défaut
        const fullResult = engine.generateRecommendations(profile, {
          categories: normalizeCategories(categories),
          budgets: normalizeBudgets(budgets),
          times: normalizeTimes(times),
          limit: 50,
        });
        result = {
          events: fullResult.events,
          sections: fullResult.sections,
        };
    }
    
    // Convertir EventWithScore en format attendu par le frontend
    let events = result.events.map(ews => ({
      ...ews.event,
      _score: ews.score.totalScore,
      _reason: ews.primaryReason,
      _breakdown: ews.score.breakdown,
    }));
    
    // Filtrer par dates si spécifiées
    if (dateFrom || dateTo) {
      // D'abord filtrer les événements recommandés
      events = events.filter(event => {
        const eventDate = event.date;
        if (dateFrom && eventDate < dateFrom) return false;
        if (dateTo && eventDate > dateTo) return false;
        return true;
      });
      
      // Ensuite, charger directement les événements depuis l'API Python pour les dates spécifiées
      // pour s'assurer qu'on a tous les événements, même ceux avec un score faible
      try {
        const dateParams = new URLSearchParams();
        if (dateFrom) dateParams.append('date_from', dateFrom);
        if (dateTo) dateParams.append('date_to', dateTo);
        dateParams.append('limit', '100');
        
        const directResponse = await fetch(`${EVENTS_API_URL}/api/events?${dateParams.toString()}`, {
          cache: 'no-store',
        });
        
        if (directResponse.ok) {
          const directData = await directResponse.json();
          if (directData.success && directData.events) {
            // Convertir vers le format Event
            const directEvents: Event[] = directData.events.map((e: any) => ({
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
              budget: e.price === 0 ? 'gratuit' : e.price <= 20 ? '0-20' : e.price <= 50 ? '20-50' : '50-100',
              sourceUrl: e.source_url,
              image: e.image_url,
              ambiance: e.tags || [],
              duration: e.duration,
              bookingRequired: e.booking_required,
              verified: e.verified,
            }));
            
            // Fusionner avec les événements recommandés (éviter les doublons)
            const existingIds = new Set(events.map(e => e.id));
            const newEvents = directEvents
              .filter(e => !existingIds.has(e.id))
              .map(e => ({
                ...e,
                _score: 15, // Score minimum pour qu'ils apparaissent
                _reason: 'Disponible à cette date',
                _breakdown: {},
              }));
            
            events = [...events, ...newEvents];
            // Trier par date puis par score
            events.sort((a, b) => {
              if (a.date !== b.date) return a.date.localeCompare(b.date);
              return (b._score || 0) - (a._score || 0);
            });
          }
        }
      } catch (error) {
        console.warn('Erreur lors du chargement direct des événements:', error);
      }
    }
    
    // Filtrer par moment de la journée si spécifié
    if (times && times.length > 0) {
      const normalizedTimes = normalizeTimes(times);
      events = events.filter(event => {
        const eventTime = event.timeOfDay;
        return normalizedTimes.includes(eventTime);
      });
    }
    
    return NextResponse.json({
      success: true,
      count: events.length,
      events,
      sections: result.sections || [],
      filters: {
        categories,
        budgets,
        times,
        dateFrom,
        dateTo,
      },
      mode,
    });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { success: false, error: 'Invalid request' },
      { status: 400 }
    );
  }
}

/**
 * GET - Informations sur l'API et événements par défaut
 */
export async function GET(request: NextRequest) {
  // Charger les événements réels si pas encore fait
  await loadRealEvents();
  
  const searchParams = request.nextUrl.searchParams;
  const mode = searchParams.get('mode') || 'featured';
  
  // Créer un profil par défaut pour les recommandations
  const defaultProfile = createDefaultProfile();
  
  let events: any[];
  let title = '';
  let subtitle = '';
  
  switch (mode) {
    case 'trending':
      events = engine.getTrendingEvents(12).map(ews => ({
        ...ews.event,
        _score: ews.score.totalScore,
        _reason: ews.primaryReason,
      }));
      title = 'Tendances 🔥';
      subtitle = 'Les événements les plus populaires';
      break;
      
    case 'discover':
      events = engine.generateDiscoverWeekly(defaultProfile).slice(0, 12).map(ews => ({
        ...ews.event,
        _score: ews.score.totalScore,
        _reason: ews.primaryReason,
      }));
      title = 'Découvertes ✨';
      subtitle = 'Sortez de votre zone de confort';
      break;
      
    default:
      // Featured - les meilleurs scores
      const result = engine.generateRecommendations(defaultProfile, { limit: 12 });
      events = result.events.map(ews => ({
        ...ews.event,
        _score: ews.score.totalScore,
        _reason: ews.primaryReason,
      }));
      title = 'Pour vous ⭐';
      subtitle = 'Sélection personnalisée';
  }
  
  return NextResponse.json({
    success: true,
    message: 'Artify AI Recommendations API',
    version: '2.0',
    title,
    subtitle,
    totalEvents: events.length,
    categories: [
      'spectacles', 'musique', 'arts_visuels', 'ateliers', 
      'sport', 'rencontres', 'gastronomie', 'culture', 'nightlife'
    ],
    budgets: ['gratuit', '0-20', '20-50', '50-100', '100+'],
    times: ['matin', 'apres_midi', 'soir', 'nuit'],
    modes: ['personalized', 'discover', 'trending', 'similar'],
    featured: events,
    example: {
      method: 'POST',
      body: {
        categories: ['musique', 'spectacles'],
        budgets: ['0-20', '20-50'],
        times: ['soir', 'nuit'],
        mode: 'personalized',
        userProfile: {
          preferences: {
            explicit: {
              categories: ['musique'],
            },
          },
          tasteProfile: {
            adventurousness: 0.7,
            socialLevel: 0.6,
          },
        },
      },
    },
  });
}
