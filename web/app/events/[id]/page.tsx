'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { RecommendationSection } from '@/components/RecommendationSection';
import { useRecommendations } from '@/hooks/useRecommendations';

// URL de l'API des événements réels
const EVENTS_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

interface EventData {
  id: string;
  title: string;
  date: string;
  startTime?: string;
  endTime?: string;
  price: number;
  mainCategory?: string;
  category?: string;
  subCategory?: string;
  venue?: string;
  address: string;
  description: string;
  link?: string;
  sourceUrl?: string;
  timeOfDay: string;
  arrondissement?: number;
  metro?: string[];
  ambiance?: string[];
  duration?: number;
  bookingRequired?: boolean;
}

// Configuration des catégories
const categoryConfig: { [key: string]: { emoji: string; label: string; color: string } } = {
  spectacles: { emoji: '🎭', label: 'Spectacles', color: '#F43F5E' },
  musique: { emoji: '🎵', label: 'Musique', color: '#A855F7' },
  arts_visuels: { emoji: '🎨', label: 'Arts visuels', color: '#F97316' },
  ateliers: { emoji: '🖌️', label: 'Ateliers', color: '#22C55E' },
  sport: { emoji: '🏃', label: 'Sport', color: '#06B6D4' },
  rencontres: { emoji: '👥', label: 'Rencontres', color: '#8B5CF6' },
  gastronomie: { emoji: '🍷', label: 'Gastronomie', color: '#EC4899' },
  culture: { emoji: '📚', label: 'Culture', color: '#3B82F6' },
  nightlife: { emoji: '🌙', label: 'Nightlife', color: '#6366F1' },
  // Legacy
  expositions: { emoji: '🎨', label: 'Exposition', color: '#F97316' },
  soirees: { emoji: '🎉', label: 'Soirée', color: '#6366F1' },
  gastro: { emoji: '🍷', label: 'Gastronomie', color: '#EC4899' },
  theatre: { emoji: '🎭', label: 'Théâtre', color: '#F43F5E' },
  lectures: { emoji: '📚', label: 'Culture', color: '#3B82F6' },
};

const timeConfig: { [key: string]: { emoji: string; label: string } } = {
  matin: { emoji: '🌅', label: 'Matin (8h-12h)' },
  apres_midi: { emoji: '☀️', label: 'Après-midi (12h-18h)' },
  soir: { emoji: '🌆', label: 'Soirée (18h-23h)' },
  nuit: { emoji: '🌙', label: 'Nuit (23h+)' },
  jour: { emoji: '☀️', label: 'Journée' },
};

const ambianceLabels: { [key: string]: { emoji: string; label: string } } = {
  intime: { emoji: '🕯️', label: 'Intimiste' },
  festif: { emoji: '🎉', label: 'Festif' },
  culturel: { emoji: '🎭', label: 'Culturel' },
  sportif: { emoji: '💪', label: 'Sportif' },
  social: { emoji: '👥', label: 'Social' },
  creatif: { emoji: '✨', label: 'Créatif' },
  gastronomique: { emoji: '🍽️', label: 'Gastronomique' },
};

export default function EventPage() {
  const params = useParams();
  const router = useRouter();
  const [event, setEvent] = useState<EventData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [similarEvents, setSimilarEvents] = useState<any[]>([]);
  const { recordView, recordFavorite, isFavorite, fetchRecommendations } = useRecommendations();

  useEffect(() => {
    const id = params.id as string;
    
    const loadEvent = async () => {
      setIsLoading(true);
      
      // Charger depuis l'API des événements réels
      try {
        const response = await fetch(`${EVENTS_API_URL}/api/events/${id}`);
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.event) {
            // Convertir vers le format EventData
            const realEvent = data.event;
            const convertedEvent: EventData = {
              id: realEvent.id,
              title: realEvent.title,
              date: realEvent.date,
              startTime: realEvent.start_time,
              endTime: realEvent.end_time,
              price: realEvent.price,
              mainCategory: realEvent.main_category,
              subCategory: realEvent.sub_category,
              venue: realEvent.venue,
              address: realEvent.address,
              description: realEvent.description,
              sourceUrl: realEvent.source_url,
              timeOfDay: realEvent.time_of_day,
              arrondissement: realEvent.arrondissement,
              ambiance: realEvent.tags || [],
              duration: realEvent.duration,
              bookingRequired: realEvent.booking_required,
            };
            setEvent(convertedEvent);
            recordView(id);
          } else {
            setEvent(null);
          }
        } else {
          setEvent(null);
        }
      } catch (error) {
        console.error('Erreur lors du chargement de l\'événement:', error);
        setEvent(null);
      }
      
      setIsLoading(false);
    };
    
    loadEvent();
    
    // Charger les événements similaires
    fetch('/api/recommendations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mode: 'similar',
        eventId: id,
      }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.success && data.events) {
          setSimilarEvents(data.events.slice(0, 6));
        }
      })
      .catch(console.error);
  }, [params.id, recordView]);

  const handleFavorite = useCallback(() => {
    if (event) {
      recordFavorite(event.id);
    }
  }, [event, recordFavorite]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  };

  const formatPrice = (price: number) => {
    if (price === 0) return 'Gratuit';
    return `${price}€`;
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 60) return `${minutes} min`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h${mins}` : `${hours}h`;
  };

  const getCategory = (event: EventData) => {
    const cat = event.mainCategory || event.category || 'culture';
    return categoryConfig[cat] || { emoji: '📌', label: cat, color: '#6366F1' };
  };

  const getTime = (timeOfDay: string) => {
    return timeConfig[timeOfDay] || { emoji: '🕐', label: timeOfDay };
  };

  if (isLoading) {
    return (
      <main style={styles.main}>
        <div style={styles.loadingContainer}>
          <div style={styles.spinner}></div>
          <p style={styles.loadingText}>Chargement...</p>
        </div>
      </main>
    );
  }

  if (!event) {
    return (
      <main style={styles.main}>
        <div style={styles.errorContainer}>
          <span style={styles.errorEmoji}>😕</span>
          <h1 style={styles.errorTitle}>Événement non trouvé</h1>
          <p style={styles.errorText}>Cet événement n'existe pas ou a été supprimé.</p>
          <Link href="/results" style={styles.backButton}>
            ← Retour à la sélection
          </Link>
        </div>
      </main>
    );
  }

  const category = getCategory(event);
  const time = getTime(event.timeOfDay);
  const eventLink = event.sourceUrl || event.link || '#';
  const isFav = isFavorite(event.id);

  return (
    <main style={styles.main}>
      {/* Background */}
      <div style={{
        ...styles.bgGradient,
        background: `linear-gradient(180deg, ${category.color}15 0%, transparent 50%)`,
      }} />

      <div style={styles.container}>
        {/* Back Link */}
        <Link href="/results" style={styles.backLink}>
          <span>←</span> Retour à la sélection
        </Link>

        {/* Category & Time */}
        <div style={styles.badges}>
          <span style={{
            ...styles.categoryBadge,
            backgroundColor: `${category.color}20`,
            color: category.color,
            borderColor: `${category.color}40`,
          }}>
            {category.emoji} {category.label}
          </span>
          <span style={styles.timeBadge}>
            {time.emoji} {time.label}
          </span>
          {/* Favorite button */}
          <button
            onClick={handleFavorite}
            style={{
              ...styles.favoriteButton,
              backgroundColor: isFav ? 'rgba(236, 72, 153, 0.2)' : 'rgba(255,255,255,0.05)',
              borderColor: isFav ? '#EC4899' : 'transparent',
            }}
          >
            {isFav ? '❤️ Favori' : '🤍 Ajouter aux favoris'}
          </button>
        </div>

        {/* Title */}
        <h1 style={styles.title}>{event.title}</h1>

        {/* Match score if available */}
        {(event as any)._score && (
          <div style={styles.matchBadge}>
            <span style={styles.matchIcon}>✨</span>
            <span style={styles.matchText}>
              {Math.round((event as any)._score)}% de compatibilité avec vos goûts
            </span>
          </div>
        )}

        {/* Price */}
        <div style={styles.priceContainer}>
          <span style={{
            ...styles.price,
            color: event.price === 0 ? '#22C55E' : '#fff',
            backgroundColor: event.price === 0 ? 'rgba(34, 197, 94, 0.15)' : 'rgba(255,255,255,0.1)',
          }}>
            {formatPrice(event.price)}
          </span>
          {event.bookingRequired && (
            <span style={styles.bookingBadge}>🎟️ Réservation requise</span>
          )}
        </div>

        {/* Ambiance tags */}
        {event.ambiance && event.ambiance.length > 0 && (
          <div style={styles.ambianceTags}>
            {event.ambiance.map(amb => {
              const ambInfo = ambianceLabels[amb] || { emoji: '✨', label: amb };
              return (
                <span key={amb} style={styles.ambianceTag}>
                  {ambInfo.emoji} {ambInfo.label}
                </span>
              );
            })}
          </div>
        )}

        {/* Description */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>À propos</h2>
          <p style={styles.description}>{event.description}</p>
        </div>

        {/* Details */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>Informations pratiques</h2>
          <div style={styles.detailsGrid}>
            <div style={styles.detailItem}>
              <span style={styles.detailIcon}>📅</span>
              <div>
                <p style={styles.detailLabel}>Date</p>
                <p style={styles.detailValue}>{formatDate(event.date)}</p>
              </div>
            </div>
            
            {event.startTime && (
              <div style={styles.detailItem}>
                <span style={styles.detailIcon}>🕐</span>
                <div>
                  <p style={styles.detailLabel}>Horaire</p>
                  <p style={styles.detailValue}>
                    {event.startTime}
                    {event.endTime && ` - ${event.endTime}`}
                    {event.duration && ` (${formatDuration(event.duration)})`}
                  </p>
                </div>
              </div>
            )}
            
            <div style={styles.detailItem}>
              <span style={styles.detailIcon}>📍</span>
              <div>
                <p style={styles.detailLabel}>Lieu</p>
                <p style={styles.detailValue}>
                  {event.venue && <strong>{event.venue}</strong>}
                  {event.venue && <br />}
                  {event.address}
                  {event.arrondissement && (
                    <span style={styles.arrondissement}> ({event.arrondissement}e arr.)</span>
                  )}
                </p>
              </div>
            </div>

            {event.metro && event.metro.length > 0 && (
              <div style={styles.detailItem}>
                <span style={styles.detailIcon}>🚇</span>
                <div>
                  <p style={styles.detailLabel}>Métro</p>
                  <p style={styles.detailValue}>{event.metro.join(', ')}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* CTA Buttons */}
        <div style={styles.ctaContainer}>
          <a
            href={eventLink}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              ...styles.primaryButton,
              background: `linear-gradient(135deg, ${category.color} 0%, #6366F1 100%)`,
            }}
          >
            Réserver / En savoir plus →
          </a>
          <a
            href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(event.address)}`}
            target="_blank"
            rel="noopener noreferrer"
            style={styles.secondaryButton}
          >
            📍 Voir sur Google Maps
          </a>
        </div>

        {/* Similar Events */}
        {similarEvents.length > 0 && (
          <div style={styles.similarSection}>
            <RecommendationSection
              title={`Car vous aimez cet événement`}
              subtitle="Événements similaires qui pourraient vous plaire"
              emoji="💫"
              events={similarEvents}
              onFavorite={recordFavorite}
              isFavorite={isFavorite}
            />
          </div>
        )}
      </div>
    </main>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  main: {
    minHeight: '100vh',
    padding: '24px 20px 80px',
    position: 'relative',
  },
  bgGradient: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    height: '50vh',
    pointerEvents: 'none',
  },
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    position: 'relative',
    zIndex: 1,
  },
  backLink: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '14px',
    color: '#71717A',
    textDecoration: 'none',
    marginBottom: '32px',
    padding: '8px 0',
    transition: 'color 0.2s ease',
  },
  badges: {
    display: 'flex',
    gap: '12px',
    marginBottom: '20px',
    flexWrap: 'wrap',
    alignItems: 'center',
  },
  categoryBadge: {
    fontSize: '13px',
    fontWeight: 600,
    padding: '8px 16px',
    borderRadius: '20px',
    border: '1px solid',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  timeBadge: {
    fontSize: '13px',
    fontWeight: 500,
    color: '#A1A1AA',
    backgroundColor: 'rgba(255,255,255,0.05)',
    padding: '8px 16px',
    borderRadius: '20px',
  },
  favoriteButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '13px',
    fontWeight: 500,
    padding: '8px 16px',
    borderRadius: '20px',
    border: '1px solid transparent',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    marginLeft: 'auto',
  },
  title: {
    fontSize: '36px',
    fontWeight: 700,
    letterSpacing: '-1px',
    lineHeight: 1.2,
    marginBottom: '16px',
    color: '#fff',
  },
  matchBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '10px 16px',
    background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(236, 72, 153, 0.2) 100%)',
    borderRadius: '12px',
    marginBottom: '20px',
    border: '1px solid rgba(139, 92, 246, 0.3)',
  },
  matchIcon: {
    fontSize: '16px',
  },
  matchText: {
    fontSize: '14px',
    color: '#A855F7',
    fontWeight: 500,
  },
  priceContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    marginBottom: '20px',
    flexWrap: 'wrap',
  },
  price: {
    fontSize: '20px',
    fontWeight: 600,
    padding: '10px 20px',
    borderRadius: '12px',
  },
  bookingBadge: {
    fontSize: '13px',
    color: '#A1A1AA',
  },
  ambianceTags: {
    display: 'flex',
    gap: '8px',
    marginBottom: '32px',
    flexWrap: 'wrap',
  },
  ambianceTag: {
    fontSize: '12px',
    color: '#A1A1AA',
    backgroundColor: 'rgba(255,255,255,0.05)',
    padding: '6px 12px',
    borderRadius: '16px',
  },
  section: {
    backgroundColor: 'rgba(24, 24, 31, 0.7)',
    backdropFilter: 'blur(20px)',
    borderRadius: '20px',
    padding: '28px',
    marginBottom: '16px',
    border: '1px solid rgba(255,255,255,0.08)',
  },
  sectionTitle: {
    fontSize: '12px',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '1px',
    color: '#71717A',
    marginBottom: '16px',
  },
  description: {
    fontSize: '16px',
    lineHeight: 1.8,
    color: '#D4D4D8',
  },
  detailsGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },
  detailItem: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '16px',
  },
  detailIcon: {
    fontSize: '20px',
    marginTop: '4px',
    width: '24px',
    textAlign: 'center',
  },
  detailLabel: {
    fontSize: '12px',
    color: '#71717A',
    marginBottom: '4px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  detailValue: {
    fontSize: '15px',
    color: '#E4E4E7',
    fontWeight: 400,
    lineHeight: 1.5,
  },
  arrondissement: {
    color: '#71717A',
  },
  ctaContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    marginTop: '32px',
  },
  primaryButton: {
    display: 'block',
    textAlign: 'center',
    padding: '20px 28px',
    color: '#FFFFFF',
    fontSize: '16px',
    fontWeight: 600,
    borderRadius: '16px',
    textDecoration: 'none',
    boxShadow: '0 8px 32px rgba(99, 102, 241, 0.3)',
    transition: 'all 0.3s ease',
  },
  secondaryButton: {
    display: 'block',
    textAlign: 'center',
    padding: '18px 28px',
    backgroundColor: 'rgba(255,255,255,0.05)',
    color: '#E4E4E7',
    fontSize: '15px',
    fontWeight: 500,
    borderRadius: '16px',
    border: '1px solid rgba(255,255,255,0.1)',
    textDecoration: 'none',
    transition: 'all 0.2s ease',
  },
  similarSection: {
    marginTop: '48px',
    paddingTop: '32px',
    borderTop: '1px solid rgba(255,255,255,0.1)',
  },
  loadingContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '70vh',
    gap: '20px',
  },
  spinner: {
    width: '48px',
    height: '48px',
    border: '3px solid rgba(139, 92, 246, 0.2)',
    borderTopColor: '#A855F7',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  loadingText: {
    fontSize: '15px',
    color: '#71717A',
  },
  errorContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '70vh',
    textAlign: 'center',
    gap: '12px',
  },
  errorEmoji: {
    fontSize: '64px',
    marginBottom: '8px',
  },
  errorTitle: {
    fontSize: '28px',
    fontWeight: 600,
    color: '#fff',
  },
  errorText: {
    fontSize: '15px',
    color: '#71717A',
    marginBottom: '24px',
  },
  backButton: {
    display: 'inline-block',
    padding: '16px 32px',
    background: 'linear-gradient(135deg, #6366F1 0%, #A855F7 100%)',
    color: '#FFFFFF',
    fontSize: '15px',
    fontWeight: 500,
    borderRadius: '14px',
    textDecoration: 'none',
  },
};
