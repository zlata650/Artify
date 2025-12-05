'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { RecommendationSection, DiscoverWeekly } from '@/components/RecommendationSection';
import { useRecommendations } from '@/hooks/useRecommendations';

// Types
interface Event {
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
  link?: string;
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

interface Section {
  id: string;
  title: string;
  subtitle: string;
  emoji: string;
  type: string;
  eventIds: string[];
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
};

const timeConfig: { [key: string]: { emoji: string; label: string } } = {
  matin: { emoji: '🌅', label: 'Matin' },
  apres_midi: { emoji: '☀️', label: 'Après-midi' },
  soir: { emoji: '🌆', label: 'Soirée' },
  nuit: { emoji: '🌙', label: 'Nuit' },
};

export default function ResultsPage() {
  const router = useRouter();
  const { 
    isLoading, 
    error, 
    events: allEvents, 
    sections,
    fetchRecommendations,
    recordView,
    recordFavorite,
    isFavorite,
    getStats,
    userProfile,
  } = useRecommendations();
  
  const [viewMode, setViewMode] = useState<'sections' | 'grid'>('sections');
  const [activeFilter, setActiveFilter] = useState<string | null>(null);
  const [showStats, setShowStats] = useState(false);

  // Charger les recommandations au démarrage
  useEffect(() => {
    const loadRecommendations = async () => {
      try {
        const filtersStr = sessionStorage.getItem('artify_filters');
        const filters = filtersStr ? JSON.parse(filtersStr) : {
          categories: [],
          budgets: [],
          times: [],
        };
        
        await fetchRecommendations({
          categories: filters.categories,
          budgets: filters.budgets,
          times: filters.times,
          dateFrom: filters.dateFrom,
          dateTo: filters.dateTo,
          mode: 'personalized',
        });
      } catch (err) {
        console.error('Error loading recommendations:', err);
      }
    };
    
    loadRecommendations();
  }, [fetchRecommendations]);

  // Handlers
  const handleEventClick = useCallback((eventId: string) => {
    recordView(eventId);
  }, [recordView]);

  const handleFavorite = useCallback((eventId: string): boolean => {
    return recordFavorite(eventId);
  }, [recordFavorite]);

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

  const getCategory = (event: Event) => {
    const cat = event.mainCategory;
    return categoryConfig[cat] || { emoji: '📌', label: cat, color: '#6366F1' };
  };

  const getTime = (timeOfDay: string) => {
    return timeConfig[timeOfDay] || { emoji: '🕐', label: timeOfDay };
  };

  const filteredEvents = activeFilter 
    ? allEvents.filter(e => e.mainCategory === activeFilter)
    : allEvents;

  // Get unique categories from events
  const uniqueCategories = [...new Set(allEvents.map(e => e.mainCategory))];

  // Get events for a section
  const getEventsForSection = (section: Section): Event[] => {
    return section.eventIds
      .map(id => allEvents.find(e => e.id === id))
      .filter((e): e is Event => e !== undefined);
  };

  // Stats
  const stats = getStats();

  if (isLoading) {
    return (
      <main style={styles.main}>
        <div style={styles.loadingContainer}>
          <div style={styles.loadingContent}>
            <div style={styles.pulseContainer}>
              <div style={styles.pulse1} />
              <div style={styles.pulse2} />
              <div style={styles.pulse3} />
            </div>
            <h2 style={styles.loadingTitle}>Analyse de vos goûts...</h2>
            <p style={styles.loadingText}>Notre IA prépare vos recommandations personnalisées</p>
            <div style={styles.loadingSteps}>
              <div style={styles.loadingStep}>✓ Analyse des préférences</div>
              <div style={styles.loadingStep}>✓ Recherche d'événements similaires</div>
              <div style={{...styles.loadingStep, opacity: 0.5}}>⋯ Personnalisation des résultats</div>
            </div>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main style={styles.main}>
        <div style={styles.errorContainer}>
          <span style={styles.errorIcon}>😕</span>
          <h2 style={styles.errorTitle}>Oops !</h2>
          <p style={styles.errorText}>{error}</p>
          <button onClick={() => router.push('/')} style={styles.errorButton}>
            ← Retour à l'accueil
          </button>
        </div>
      </main>
    );
  }

  return (
    <main style={styles.main}>
      {/* Background */}
      <div style={styles.bgOrb1} />
      <div style={styles.bgOrb2} />
      <div style={styles.bgOrb3} />

      <div style={styles.container}>
        {/* Header */}
        <header style={styles.header}>
          <button onClick={() => router.push('/')} style={styles.backButton}>
            <span>←</span> Modifier mes préférences
          </button>
          
          <div style={styles.headerContent}>
            <div style={styles.headerLeft}>
              <h1 style={styles.title}>
                <span style={styles.titleIcon}>✨</span>
                Vos recommandations
              </h1>
              <p style={styles.subtitle}>
                <span style={styles.countBadge}>{allEvents.length}</span>
                événements sélectionnés pour vous
              </p>
            </div>
            
            <div style={styles.headerRight}>
              {/* View mode toggle */}
              <div style={styles.viewToggle}>
                <button
                  onClick={() => setViewMode('sections')}
                  style={{
                    ...styles.viewButton,
                    backgroundColor: viewMode === 'sections' ? 'rgba(139, 92, 246, 0.2)' : 'transparent',
                    color: viewMode === 'sections' ? '#A855F7' : '#71717A',
                  }}
                >
                  🎵 Sections
                </button>
                <button
                  onClick={() => setViewMode('grid')}
                  style={{
                    ...styles.viewButton,
                    backgroundColor: viewMode === 'grid' ? 'rgba(139, 92, 246, 0.2)' : 'transparent',
                    color: viewMode === 'grid' ? '#A855F7' : '#71717A',
                  }}
                >
                  📋 Liste
                </button>
              </div>
              
              {/* Stats button */}
              <button
                onClick={() => setShowStats(!showStats)}
                style={styles.statsButton}
              >
                📊 Mon profil
              </button>
            </div>
          </div>
        </header>

        {/* User Stats Panel */}
        {showStats && (
          <div style={styles.statsPanel}>
            <div style={styles.statsPanelHeader}>
              <h3 style={styles.statsPanelTitle}>🎯 Votre profil musical</h3>
              <p style={styles.statsPanelSubtitle}>
                Membre depuis {stats.memberSince}
              </p>
            </div>
            <div style={styles.statsGrid}>
              <div style={styles.statBox}>
                <span style={styles.statValue}>{stats.totalEvents}</span>
                <span style={styles.statLabel}>événements vus</span>
              </div>
              <div style={styles.statBox}>
                <span style={styles.statValue}>{stats.avgBudget}</span>
                <span style={styles.statLabel}>budget moyen</span>
              </div>
              <div style={styles.statBox}>
                <span style={styles.statValue}>{stats.preferredTime}</span>
                <span style={styles.statLabel}>horaire préféré</span>
              </div>
            </div>
            {stats.topCategories.length > 0 && (
              <div style={styles.topCategories}>
                <span style={styles.topCategoriesLabel}>Vos catégories favorites:</span>
                <div style={styles.topCategoriesList}>
                  {stats.topCategories.map((cat, i) => (
                    <span key={i} style={styles.topCategoryBadge}>
                      {categoryConfig[cat.category]?.emoji} {categoryConfig[cat.category]?.label || cat.category}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Sections View */}
        {viewMode === 'sections' && sections.length > 0 && (
          <div style={styles.sectionsContainer}>
            {sections.map((section) => {
              const sectionEvents = getEventsForSection(section);
              
              if (section.type === 'for_you' && sectionEvents.length > 0) {
                return (
                  <div key={section.id} style={styles.forYouSection}>
                    <div style={styles.forYouHeader}>
                      <div style={styles.forYouIcon}>✨</div>
                      <div>
                        <h2 style={styles.forYouTitle}>Pour vous</h2>
                        <p style={styles.forYouSubtitle}>
                          Sélection basée sur vos goûts
                        </p>
                      </div>
                    </div>
                    <RecommendationSection
                      title=""
                      events={sectionEvents}
                      onEventClick={handleEventClick}
                      onFavorite={handleFavorite}
                      isFavorite={isFavorite}
                      showScore
                    />
                  </div>
                );
              }
              
              return (
                <RecommendationSection
                  key={section.id}
                  title={section.title}
                  subtitle={section.subtitle}
                  emoji={section.emoji}
                  events={sectionEvents}
                  onEventClick={handleEventClick}
                  onFavorite={handleFavorite}
                  isFavorite={isFavorite}
                />
              );
            })}
          </div>
        )}

        {/* Grid View */}
        {viewMode === 'grid' && (
          <>
            {/* Category filters */}
            {uniqueCategories.length > 1 && (
              <div style={styles.filterBar}>
                <button
                  onClick={() => setActiveFilter(null)}
                  style={{
                    ...styles.filterChip,
                    backgroundColor: activeFilter === null ? 'rgba(139, 92, 246, 0.2)' : 'transparent',
                    borderColor: activeFilter === null ? '#8B5CF6' : 'rgba(255,255,255,0.1)',
                  }}
                >
                  Tous ({allEvents.length})
                </button>
                {uniqueCategories.map(cat => {
                  const config = categoryConfig[cat] || { emoji: '📌', label: cat, color: '#6366F1' };
                  const count = allEvents.filter(e => e.mainCategory === cat).length;
                  return (
                    <button
                      key={cat}
                      onClick={() => setActiveFilter(cat)}
                      style={{
                        ...styles.filterChip,
                        backgroundColor: activeFilter === cat ? `${config.color}20` : 'transparent',
                        borderColor: activeFilter === cat ? config.color : 'rgba(255,255,255,0.1)',
                      }}
                    >
                      {config.emoji} {config.label} ({count})
                    </button>
                  );
                })}
              </div>
            )}

            {/* Events Grid */}
            {filteredEvents.length === 0 ? (
              <div style={styles.emptyState}>
                <span style={styles.emptyIcon}>🔍</span>
                <h2 style={styles.emptyTitle}>Aucun événement trouvé</h2>
                <p style={styles.emptyText}>Essayez de modifier vos critères de recherche</p>
                <button onClick={() => router.push('/')} style={styles.emptyButton}>
                  Modifier mes préférences
                </button>
              </div>
            ) : (
              <div style={styles.eventsGrid}>
                {filteredEvents.map((event, index) => {
                  const category = getCategory(event);
                  const time = getTime(event.timeOfDay);
                  const isFav = isFavorite(event.id);
                  
                  return (
                    <Link
                      key={event.id}
                      href={`/events/${event.id}`}
                      style={{ textDecoration: 'none', color: 'inherit' }}
                      onClick={() => handleEventClick(event.id)}
                    >
                      <article
                        style={{
                          ...styles.eventCard,
                          animationDelay: `${index * 0.05}s`,
                          borderColor: `${category.color}30`,
                        }}
                        className="animate-slide-up"
                      >
                        {/* Category accent line */}
                        <div style={{
                          ...styles.cardAccent,
                          background: `linear-gradient(90deg, ${category.color}, transparent)`,
                        }} />

                        {/* Reason badge */}
                        {event._reason && (
                          <div style={styles.reasonBadge}>
                            <span>{event._reason.emoji}</span>
                            <span style={styles.reasonText}>{event._reason.text}</span>
                          </div>
                        )}

                        {/* Card Header */}
                        <div style={styles.cardHeader}>
                          <span style={{
                            ...styles.categoryBadge,
                            backgroundColor: `${category.color}20`,
                            color: category.color,
                          }}>
                            {category.emoji} {category.label}
                          </span>
                          <div style={styles.cardHeaderRight}>
                            <span style={styles.timeBadge}>
                              {time.emoji} {time.label}
                            </span>
                            <button
                              style={{
                                ...styles.favoriteBtn,
                                color: isFav ? '#EC4899' : '#71717A',
                              }}
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                handleFavorite(event.id);
                              }}
                            >
                              {isFav ? '❤️' : '🤍'}
                            </button>
                          </div>
                        </div>

                        {/* Title */}
                        <h2 style={styles.eventTitle}>{event.title}</h2>

                        {/* Description */}
                        <p style={styles.eventDescription}>
                          {event.shortDescription || event.description}
                        </p>

                        {/* Meta Info */}
                        <div style={styles.eventMeta}>
                          <div style={styles.metaItem}>
                            <span style={styles.metaIcon}>📅</span>
                            <span>{formatDate(event.date)}</span>
                            {event.startTime && <span style={styles.metaTime}>{event.startTime}</span>}
                          </div>
                          <div style={styles.metaItem}>
                            <span style={styles.metaIcon}>📍</span>
                            <span style={styles.address}>
                              {event.venue || event.address.split(',')[0]}
                              {event.arrondissement && <span style={styles.arrondissement}> ({event.arrondissement}e)</span>}
                            </span>
                          </div>
                        </div>

                        {/* Footer */}
                        <div style={styles.cardFooter}>
                          <span style={{
                            ...styles.price,
                            color: event.price === 0 ? '#22C55E' : '#fff',
                            backgroundColor: event.price === 0 ? 'rgba(34, 197, 94, 0.15)' : 'rgba(255,255,255,0.1)',
                          }}>
                            {formatPrice(event.price)}
                          </span>
                          <div style={styles.footerRight}>
                            {event._score && (
                              <span style={styles.matchScore}>
                                ⭐ {Math.round(event._score)}% match
                              </span>
                            )}
                            <span style={styles.linkButton}>
                              Voir détails
                              <span style={styles.linkArrow}>→</span>
                            </span>
                          </div>
                        </div>
                      </article>
                    </Link>
                  );
                })}
              </div>
            )}
          </>
        )}

        {/* Empty sections state */}
        {viewMode === 'sections' && sections.length === 0 && allEvents.length > 0 && (
          <RecommendationSection
            title="Tous les événements"
            subtitle="Recommandés pour vous"
            emoji="✨"
            events={allEvents}
            onEventClick={handleEventClick}
            onFavorite={handleFavorite}
            isFavorite={isFavorite}
          />
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
    overflow: 'hidden',
  },
  bgOrb1: {
    position: 'fixed',
    top: '10%',
    right: '-10%',
    width: '500px',
    height: '500px',
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(139, 92, 246, 0.12) 0%, transparent 70%)',
    filter: 'blur(60px)',
    pointerEvents: 'none',
  },
  bgOrb2: {
    position: 'fixed',
    bottom: '10%',
    left: '-10%',
    width: '400px',
    height: '400px',
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(236, 72, 153, 0.12) 0%, transparent 70%)',
    filter: 'blur(60px)',
    pointerEvents: 'none',
  },
  bgOrb3: {
    position: 'fixed',
    top: '50%',
    left: '30%',
    width: '600px',
    height: '600px',
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%)',
    filter: 'blur(80px)',
    pointerEvents: 'none',
  },
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    position: 'relative',
    zIndex: 1,
  },
  header: {
    marginBottom: '32px',
  },
  backButton: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    background: 'none',
    border: 'none',
    fontSize: '14px',
    color: '#71717A',
    marginBottom: '24px',
    padding: '8px 0',
    cursor: 'pointer',
    transition: 'color 0.2s ease',
  },
  headerContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    flexWrap: 'wrap',
    gap: '20px',
  },
  headerLeft: {},
  headerRight: {
    display: 'flex',
    gap: '12px',
    alignItems: 'center',
  },
  title: {
    fontSize: '36px',
    fontWeight: 700,
    letterSpacing: '-1px',
    background: 'linear-gradient(135deg, #fff 0%, #A855F7 50%, #EC4899 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '8px',
  },
  titleIcon: {
    WebkitTextFillColor: 'initial',
    fontSize: '32px',
  },
  subtitle: {
    fontSize: '15px',
    color: '#71717A',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  countBadge: {
    background: 'linear-gradient(135deg, #A855F7 0%, #EC4899 100%)',
    color: '#fff',
    padding: '4px 12px',
    borderRadius: '20px',
    fontSize: '14px',
    fontWeight: 600,
  },
  viewToggle: {
    display: 'flex',
    gap: '4px',
    padding: '4px',
    backgroundColor: 'rgba(24, 24, 31, 0.6)',
    borderRadius: '12px',
    border: '1px solid rgba(255,255,255,0.05)',
  },
  viewButton: {
    padding: '8px 14px',
    border: 'none',
    borderRadius: '8px',
    fontSize: '13px',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  statsButton: {
    padding: '10px 16px',
    backgroundColor: 'rgba(24, 24, 31, 0.6)',
    border: '1px solid rgba(255,255,255,0.05)',
    borderRadius: '12px',
    fontSize: '13px',
    fontWeight: 500,
    color: '#A1A1AA',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  statsPanel: {
    marginBottom: '32px',
    padding: '24px',
    background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%)',
    borderRadius: '20px',
    border: '1px solid rgba(139, 92, 246, 0.2)',
  },
  statsPanelHeader: {
    marginBottom: '20px',
  },
  statsPanelTitle: {
    fontSize: '18px',
    fontWeight: 600,
    color: '#fff',
    marginBottom: '4px',
  },
  statsPanelSubtitle: {
    fontSize: '13px',
    color: '#71717A',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '16px',
    marginBottom: '20px',
  },
  statBox: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '16px',
    backgroundColor: 'rgba(24, 24, 31, 0.5)',
    borderRadius: '12px',
  },
  statValue: {
    fontSize: '24px',
    fontWeight: 700,
    color: '#A855F7',
    marginBottom: '4px',
  },
  statLabel: {
    fontSize: '12px',
    color: '#71717A',
  },
  topCategories: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  topCategoriesLabel: {
    fontSize: '13px',
    color: '#71717A',
  },
  topCategoriesList: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap',
  },
  topCategoryBadge: {
    padding: '6px 12px',
    backgroundColor: 'rgba(139, 92, 246, 0.2)',
    borderRadius: '20px',
    fontSize: '13px',
    color: '#A855F7',
  },
  sectionsContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  forYouSection: {
    background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(236, 72, 153, 0.1) 100%)',
    borderRadius: '24px',
    padding: '24px',
    marginBottom: '20px',
    border: '1px solid rgba(139, 92, 246, 0.2)',
  },
  forYouHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    marginBottom: '20px',
  },
  forYouIcon: {
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
  forYouTitle: {
    fontSize: '22px',
    fontWeight: 700,
    color: '#fff',
    marginBottom: '4px',
  },
  forYouSubtitle: {
    fontSize: '14px',
    color: '#A1A1AA',
  },
  filterBar: {
    display: 'flex',
    gap: '10px',
    marginBottom: '24px',
    flexWrap: 'wrap',
    padding: '16px',
    background: 'rgba(24, 24, 31, 0.5)',
    backdropFilter: 'blur(10px)',
    borderRadius: '16px',
    border: '1px solid rgba(255,255,255,0.05)',
  },
  filterChip: {
    padding: '8px 16px',
    borderRadius: '20px',
    border: '1px solid rgba(255,255,255,0.1)',
    background: 'transparent',
    color: '#A1A1AA',
    fontSize: '13px',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  loadingContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '70vh',
  },
  loadingContent: {
    textAlign: 'center',
    maxWidth: '400px',
  },
  pulseContainer: {
    display: 'flex',
    justifyContent: 'center',
    gap: '8px',
    marginBottom: '32px',
  },
  pulse1: {
    width: '16px',
    height: '16px',
    borderRadius: '50%',
    background: '#A855F7',
    animation: 'pulse 1.2s ease-in-out infinite',
  },
  pulse2: {
    width: '16px',
    height: '16px',
    borderRadius: '50%',
    background: '#EC4899',
    animation: 'pulse 1.2s ease-in-out 0.2s infinite',
  },
  pulse3: {
    width: '16px',
    height: '16px',
    borderRadius: '50%',
    background: '#6366F1',
    animation: 'pulse 1.2s ease-in-out 0.4s infinite',
  },
  loadingTitle: {
    fontSize: '24px',
    fontWeight: 600,
    color: '#fff',
    marginBottom: '8px',
  },
  loadingText: {
    fontSize: '15px',
    color: '#71717A',
    marginBottom: '24px',
  },
  loadingSteps: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    textAlign: 'left',
    padding: '20px',
    backgroundColor: 'rgba(24, 24, 31, 0.5)',
    borderRadius: '12px',
  },
  loadingStep: {
    fontSize: '13px',
    color: '#A1A1AA',
  },
  errorContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '70vh',
    textAlign: 'center',
  },
  errorIcon: {
    fontSize: '64px',
    marginBottom: '16px',
  },
  errorTitle: {
    fontSize: '24px',
    fontWeight: 600,
    color: '#fff',
    marginBottom: '8px',
  },
  errorText: {
    fontSize: '15px',
    color: '#71717A',
    marginBottom: '24px',
  },
  errorButton: {
    padding: '14px 28px',
    background: 'linear-gradient(135deg, #6366F1 0%, #A855F7 100%)',
    color: '#fff',
    border: 'none',
    borderRadius: '12px',
    fontSize: '15px',
    fontWeight: 500,
    cursor: 'pointer',
  },
  emptyState: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '80px 20px',
    textAlign: 'center',
  },
  emptyIcon: {
    fontSize: '64px',
    marginBottom: '16px',
  },
  emptyTitle: {
    fontSize: '24px',
    fontWeight: 600,
    color: '#fff',
    marginBottom: '8px',
  },
  emptyText: {
    fontSize: '15px',
    color: '#71717A',
    marginBottom: '24px',
  },
  emptyButton: {
    padding: '14px 28px',
    background: 'linear-gradient(135deg, #6366F1 0%, #A855F7 100%)',
    color: '#fff',
    border: 'none',
    borderRadius: '12px',
    fontSize: '15px',
    fontWeight: 500,
    cursor: 'pointer',
  },
  eventsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
    gap: '20px',
  },
  eventCard: {
    backgroundColor: 'rgba(24, 24, 31, 0.7)',
    backdropFilter: 'blur(20px)',
    borderRadius: '20px',
    padding: '24px',
    border: '1px solid rgba(255,255,255,0.08)',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    position: 'relative',
    overflow: 'hidden',
  },
  cardAccent: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '3px',
  },
  reasonBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    marginBottom: '12px',
    padding: '6px 10px',
    backgroundColor: 'rgba(139, 92, 246, 0.15)',
    borderRadius: '8px',
  },
  reasonText: {
    fontSize: '11px',
    color: '#A855F7',
    fontWeight: 500,
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
  },
  cardHeaderRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  categoryBadge: {
    fontSize: '12px',
    fontWeight: 600,
    padding: '6px 12px',
    borderRadius: '20px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  timeBadge: {
    fontSize: '12px',
    fontWeight: 500,
    color: '#A1A1AA',
    backgroundColor: 'rgba(255,255,255,0.05)',
    padding: '6px 12px',
    borderRadius: '20px',
  },
  favoriteBtn: {
    width: '32px',
    height: '32px',
    background: 'rgba(255,255,255,0.05)',
    border: 'none',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '14px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  eventTitle: {
    fontSize: '20px',
    fontWeight: 600,
    letterSpacing: '-0.3px',
    marginBottom: '12px',
    lineHeight: 1.3,
    color: '#fff',
  },
  eventDescription: {
    fontSize: '14px',
    color: '#A1A1AA',
    lineHeight: 1.6,
    marginBottom: '20px',
    display: '-webkit-box',
    WebkitLineClamp: 2,
    WebkitBoxOrient: 'vertical',
    overflow: 'hidden',
  },
  eventMeta: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    marginBottom: '20px',
    paddingTop: '16px',
    borderTop: '1px solid rgba(255,255,255,0.05)',
  },
  metaItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '13px',
    color: '#71717A',
  },
  metaIcon: {
    fontSize: '14px',
  },
  metaTime: {
    marginLeft: '4px',
    color: '#A855F7',
  },
  address: {
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  arrondissement: {
    color: '#52525B',
  },
  cardFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  footerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  price: {
    fontSize: '16px',
    fontWeight: 600,
    padding: '8px 14px',
    borderRadius: '10px',
  },
  matchScore: {
    fontSize: '12px',
    color: '#A855F7',
    backgroundColor: 'rgba(139, 92, 246, 0.1)',
    padding: '6px 10px',
    borderRadius: '8px',
  },
  linkButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '14px',
    fontWeight: 500,
    color: '#A1A1AA',
    padding: '10px 16px',
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: '10px',
    transition: 'all 0.2s ease',
  },
  linkArrow: {
    fontSize: '16px',
    transition: 'transform 0.2s ease',
  },
};
