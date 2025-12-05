'use client';

import React from 'react';
import Link from 'next/link';

interface Event {
  id: string;
  title: string;
  date: string;
  startTime?: string;
  price: number;
  mainCategory: string;
  venue?: string;
  address: string;
  timeOfDay: string;
  arrondissement?: number;
  _score?: number;
  _reason?: {
    type: string;
    text: string;
    emoji: string;
  };
}

interface RecommendationSectionProps {
  title: string;
  subtitle?: string;
  emoji?: string;
  events: Event[];
  onEventClick?: (eventId: string) => void;
  onFavorite?: (eventId: string) => boolean;
  isFavorite?: (eventId: string) => boolean;
  showScore?: boolean;
}

const categoryConfig: Record<string, { emoji: string; color: string }> = {
  spectacles: { emoji: '🎭', color: '#F43F5E' },
  musique: { emoji: '🎵', color: '#A855F7' },
  arts_visuels: { emoji: '🎨', color: '#F97316' },
  ateliers: { emoji: '🖌️', color: '#22C55E' },
  sport: { emoji: '🏃', color: '#06B6D4' },
  rencontres: { emoji: '👥', color: '#8B5CF6' },
  gastronomie: { emoji: '🍷', color: '#EC4899' },
  culture: { emoji: '📚', color: '#3B82F6' },
  nightlife: { emoji: '🌙', color: '#6366F1' },
};

export function RecommendationSection({
  title,
  subtitle,
  emoji,
  events,
  onEventClick,
  onFavorite,
  isFavorite,
  showScore = false,
}: RecommendationSectionProps) {
  if (events.length === 0) return null;

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
    });
  };

  const formatPrice = (price: number) => {
    if (price === 0) return 'Gratuit';
    return `${price}€`;
  };

  return (
    <section style={styles.section}>
      <div style={styles.header}>
        <div style={styles.titleRow}>
          {emoji && <span style={styles.emoji}>{emoji}</span>}
          <h2 style={styles.title}>{title}</h2>
        </div>
        {subtitle && <p style={styles.subtitle}>{subtitle}</p>}
      </div>

      <div style={styles.scrollContainer}>
        <div style={styles.eventsRow}>
          {events.map((event, index) => {
            const config = categoryConfig[event.mainCategory] || { emoji: '📌', color: '#6366F1' };
            const isFav = isFavorite?.(event.id) || false;

            return (
              <Link
                key={event.id}
                href={`/events/${event.id}`}
                style={{ textDecoration: 'none' }}
                onClick={() => onEventClick?.(event.id)}
              >
                <article
                  style={{
                    ...styles.eventCard,
                    borderColor: `${config.color}30`,
                    animationDelay: `${index * 0.05}s`,
                  }}
                >
                  {/* Gradient top accent */}
                  <div style={{
                    ...styles.cardAccent,
                    background: `linear-gradient(90deg, ${config.color}, transparent)`,
                  }} />

                  {/* Reason badge */}
                  {event._reason && (
                    <div style={styles.reasonBadge}>
                      <span>{event._reason.emoji}</span>
                      <span style={styles.reasonText}>{event._reason.text}</span>
                    </div>
                  )}

                  {/* Category badge */}
                  <div style={{
                    ...styles.categoryBadge,
                    backgroundColor: `${config.color}20`,
                    color: config.color,
                  }}>
                    {config.emoji}
                  </div>

                  {/* Favorite button */}
                  {onFavorite && (
                    <button
                      style={{
                        ...styles.favoriteButton,
                        color: isFav ? '#EC4899' : '#71717A',
                      }}
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        onFavorite(event.id);
                      }}
                    >
                      {isFav ? '❤️' : '🤍'}
                    </button>
                  )}

                  {/* Title */}
                  <h3 style={styles.eventTitle}>{event.title}</h3>

                  {/* Meta info */}
                  <div style={styles.eventMeta}>
                    <span style={styles.metaItem}>
                      📅 {formatDate(event.date)}
                      {event.startTime && <span style={styles.time}> {event.startTime}</span>}
                    </span>
                    <span style={styles.metaItem}>
                      📍 {event.venue || event.address.split(',')[0]}
                    </span>
                  </div>

                  {/* Footer */}
                  <div style={styles.eventFooter}>
                    <span style={{
                      ...styles.price,
                      color: event.price === 0 ? '#22C55E' : '#fff',
                    }}>
                      {formatPrice(event.price)}
                    </span>
                    {showScore && event._score && (
                      <span style={styles.score}>
                        ⭐ {Math.round(event._score)}%
                      </span>
                    )}
                  </div>
                </article>
              </Link>
            );
          })}
        </div>
      </div>
    </section>
  );
}

// Composant pour afficher "Discover Weekly"
export function DiscoverWeekly({
  events,
  onEventClick,
  onFavorite,
  isFavorite,
}: {
  events: Event[];
  onEventClick?: (eventId: string) => void;
  onFavorite?: (eventId: string) => boolean;
  isFavorite?: (eventId: string) => boolean;
}) {
  return (
    <div style={styles.discoverContainer}>
      <div style={styles.discoverHeader}>
        <div style={styles.discoverIcon}>✨</div>
        <div>
          <h2 style={styles.discoverTitle}>Découvertes de la semaine</h2>
          <p style={styles.discoverSubtitle}>
            Événements sélectionnés pour élargir vos horizons
          </p>
        </div>
      </div>
      <RecommendationSection
        title=""
        events={events}
        onEventClick={onEventClick}
        onFavorite={onFavorite}
        isFavorite={isFavorite}
      />
    </div>
  );
}

// Composant "Because you liked X"
export function BecauseYouLiked({
  sourceEvent,
  events,
  onEventClick,
}: {
  sourceEvent: { id: string; title: string };
  events: Event[];
  onEventClick?: (eventId: string) => void;
}) {
  return (
    <RecommendationSection
      title={`Car vous avez aimé "${sourceEvent.title}"`}
      emoji="💫"
      events={events}
      onEventClick={onEventClick}
    />
  );
}

const styles: Record<string, React.CSSProperties> = {
  section: {
    marginBottom: '40px',
  },
  header: {
    marginBottom: '20px',
    paddingLeft: '4px',
  },
  titleRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '4px',
  },
  emoji: {
    fontSize: '24px',
  },
  title: {
    fontSize: '22px',
    fontWeight: 700,
    color: '#fff',
    letterSpacing: '-0.5px',
  },
  subtitle: {
    fontSize: '14px',
    color: '#71717A',
  },
  scrollContainer: {
    overflowX: 'auto',
    overflowY: 'hidden',
    paddingBottom: '12px',
    margin: '0 -20px',
    padding: '0 20px 12px',
    scrollbarWidth: 'none',
  },
  eventsRow: {
    display: 'flex',
    gap: '16px',
    paddingRight: '20px',
  },
  eventCard: {
    flex: '0 0 280px',
    width: '280px',
    backgroundColor: 'rgba(24, 24, 31, 0.8)',
    backdropFilter: 'blur(20px)',
    borderRadius: '16px',
    padding: '20px',
    border: '1px solid rgba(255,255,255,0.08)',
    position: 'relative',
    overflow: 'hidden',
    transition: 'all 0.3s ease',
    cursor: 'pointer',
  },
  cardAccent: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '3px',
  },
  reasonBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    marginBottom: '12px',
    padding: '6px 10px',
    backgroundColor: 'rgba(139, 92, 246, 0.15)',
    borderRadius: '8px',
    width: 'fit-content',
  },
  reasonText: {
    fontSize: '11px',
    color: '#A855F7',
    fontWeight: 500,
  },
  categoryBadge: {
    position: 'absolute',
    top: '16px',
    right: '16px',
    width: '32px',
    height: '32px',
    borderRadius: '10px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '16px',
  },
  favoriteButton: {
    position: 'absolute',
    top: '52px',
    right: '16px',
    width: '32px',
    height: '32px',
    background: 'rgba(255,255,255,0.05)',
    border: 'none',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '16px',
    cursor: 'pointer',
    transition: 'transform 0.2s ease',
  },
  eventTitle: {
    fontSize: '16px',
    fontWeight: 600,
    color: '#fff',
    marginBottom: '12px',
    lineHeight: 1.3,
    paddingRight: '50px',
    display: '-webkit-box',
    WebkitLineClamp: 2,
    WebkitBoxOrient: 'vertical',
    overflow: 'hidden',
  },
  eventMeta: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
    marginBottom: '16px',
  },
  metaItem: {
    fontSize: '12px',
    color: '#71717A',
  },
  time: {
    color: '#A855F7',
  },
  eventFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: '12px',
    borderTop: '1px solid rgba(255,255,255,0.05)',
  },
  price: {
    fontSize: '15px',
    fontWeight: 600,
  },
  score: {
    fontSize: '12px',
    color: '#71717A',
    backgroundColor: 'rgba(255,255,255,0.05)',
    padding: '4px 8px',
    borderRadius: '6px',
  },
  discoverContainer: {
    background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(236, 72, 153, 0.15) 100%)',
    borderRadius: '24px',
    padding: '24px',
    marginBottom: '40px',
    border: '1px solid rgba(139, 92, 246, 0.2)',
  },
  discoverHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    marginBottom: '20px',
  },
  discoverIcon: {
    width: '56px',
    height: '56px',
    background: 'linear-gradient(135deg, #A855F7 0%, #EC4899 100%)',
    borderRadius: '16px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '28px',
    boxShadow: '0 8px 32px rgba(139, 92, 246, 0.4)',
  },
  discoverTitle: {
    fontSize: '20px',
    fontWeight: 700,
    color: '#fff',
    marginBottom: '4px',
  },
  discoverSubtitle: {
    fontSize: '14px',
    color: '#A1A1AA',
  },
};


