'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { DayPicker, DateRange } from 'react-day-picker';
import { format, addDays } from 'date-fns';
import { fr } from 'date-fns/locale';
import 'react-day-picker/style.css';
import Onboarding from '@/components/Onboarding';
import { getUserProfileManager } from '@/lib/recommendations';

// Types
type MainCategory = 
  | 'spectacles'
  | 'musique'
  | 'arts_visuels'
  | 'ateliers'
  | 'sport'
  | 'rencontres'
  | 'gastronomie'
  | 'culture'
  | 'nightlife';

type QuickPick = 'ce_soir' | 'demain' | 'ce_weekend' | 'cette_semaine' | 'surprends_moi';

// Configuration des catégories
const categories: { id: MainCategory; label: string; emoji: string; color: string }[] = [
  { id: 'spectacles', label: 'Spectacles', emoji: '🎭', color: '#F43F5E' },
  { id: 'musique', label: 'Musique', emoji: '🎵', color: '#A855F7' },
  { id: 'arts_visuels', label: 'Expos', emoji: '🎨', color: '#F97316' },
  { id: 'ateliers', label: 'Ateliers', emoji: '🖌️', color: '#22C55E' },
  { id: 'sport', label: 'Sport', emoji: '🏃', color: '#06B6D4' },
  { id: 'rencontres', label: 'Social', emoji: '👥', color: '#8B5CF6' },
  { id: 'gastronomie', label: 'Food', emoji: '🍷', color: '#EC4899' },
  { id: 'culture', label: 'Culture', emoji: '📚', color: '#3B82F6' },
  { id: 'nightlife', label: 'Nightlife', emoji: '🌙', color: '#6366F1' },
];

// Quick picks avec couleurs
const quickPicks: { id: QuickPick; label: string; emoji: string; color: string; gradient: string }[] = [
  { id: 'ce_soir', label: 'Ce soir', emoji: '🌆', color: '#6366F1', gradient: 'linear-gradient(135deg, #6366F1, #8B5CF6)' },
  { id: 'demain', label: 'Demain', emoji: '☀️', color: '#F59E0B', gradient: 'linear-gradient(135deg, #F59E0B, #F97316)' },
  { id: 'ce_weekend', label: 'Ce weekend', emoji: '🎉', color: '#EC4899', gradient: 'linear-gradient(135deg, #EC4899, #F43F5E)' },
  { id: 'cette_semaine', label: '7 jours', emoji: '📅', color: '#22C55E', gradient: 'linear-gradient(135deg, #22C55E, #10B981)' },
  { id: 'surprends_moi', label: 'Pour moi', emoji: '✨', color: '#A855F7', gradient: 'linear-gradient(135deg, #A855F7, #EC4899)' },
];

export default function Home() {
  const router = useRouter();
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [isFirstLoad, setIsFirstLoad] = useState(true);
  const [selectedQuickPick, setSelectedQuickPick] = useState<QuickPick | null>(null);
  const [selectedCategories, setSelectedCategories] = useState<MainCategory[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showCalendar, setShowCalendar] = useState(false);
  const [dateRange, setDateRange] = useState<DateRange | undefined>();
  const [singleDate, setSingleDate] = useState<Date | undefined>();
  const [isRangeMode, setIsRangeMode] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [greeting, setGreeting] = useState('');
  const [userStats, setUserStats] = useState<{topCategories: {category: string}[]} | null>(null);
  const [hasProfile, setHasProfile] = useState(false);

  const today = new Date();

  // Vérifier si l'onboarding a été fait
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const onboardingComplete = localStorage.getItem('artify_onboarding_complete');
      const profileManager = getUserProfileManager();
      const profile = profileManager.getProfile();
      
      // Vérifier si l'utilisateur a des préférences
      const hasPreferences = profile.preferences.explicit.categories.length > 0;
      setHasProfile(hasPreferences);
      
      if (!onboardingComplete && !hasPreferences) {
        setShowOnboarding(true);
      }
      
      // Charger les stats
      if (hasPreferences) {
        setUserStats(profileManager.getStats());
      }
      
      setIsFirstLoad(false);
    }
  }, []);

  // Définir le message de bienvenue selon l'heure
  useEffect(() => {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) {
      setGreeting('Bonjour ! ☀️');
    } else if (hour >= 12 && hour < 18) {
      setGreeting('Bon après-midi !');
    } else if (hour >= 18 && hour < 22) {
      setGreeting('Bonsoir ! 🌆');
    } else {
      setGreeting('Bonne nuit ! 🌙');
    }
  }, []);

  const toggleCategory = (category: MainCategory) => {
    setSelectedCategories(prev =>
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const handleQuickPick = (pick: QuickPick) => {
    if (selectedQuickPick === pick) {
      setSelectedQuickPick(null);
    } else {
      setSelectedQuickPick(pick);
      setShowCalendar(false);
      setDateRange(undefined);
      setSingleDate(undefined);
    }
  };

  const handleDateSelect = (date: Date | undefined) => {
    setSingleDate(date);
    setSelectedQuickPick(null);
  };

  const handleRangeSelect = (range: DateRange | undefined) => {
    setDateRange(range);
    setSelectedQuickPick(null);
  };

  const getDateFilters = () => {
    if (selectedQuickPick) {
      switch (selectedQuickPick) {
        case 'ce_soir':
          return { dateFrom: format(today, 'yyyy-MM-dd'), dateTo: format(today, 'yyyy-MM-dd'), timeOfDay: ['soir', 'nuit'] };
        case 'demain':
          const tomorrow = addDays(today, 1);
          return { dateFrom: format(tomorrow, 'yyyy-MM-dd'), dateTo: format(tomorrow, 'yyyy-MM-dd') };
        case 'ce_weekend':
          const weekendStart = addDays(today, (6 - today.getDay()) % 7 || 7);
          const weekendEnd = addDays(weekendStart, 1);
          return { dateFrom: format(weekendStart, 'yyyy-MM-dd'), dateTo: format(weekendEnd, 'yyyy-MM-dd') };
        case 'cette_semaine':
          return { dateFrom: format(today, 'yyyy-MM-dd'), dateTo: format(addDays(today, 7), 'yyyy-MM-dd') };
        case 'surprends_moi':
          return { mode: 'personalized' };
      }
    }
    
    if (isRangeMode && dateRange?.from) {
      return {
        dateFrom: format(dateRange.from, 'yyyy-MM-dd'),
        dateTo: dateRange.to ? format(dateRange.to, 'yyyy-MM-dd') : format(dateRange.from, 'yyyy-MM-dd'),
      };
    }
    
    if (singleDate) {
      return { dateFrom: format(singleDate, 'yyyy-MM-dd'), dateTo: format(singleDate, 'yyyy-MM-dd') };
    }
    
    return {};
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    
    const filters = {
      categories: selectedCategories,
      ...getDateFilters(),
    };
    
    sessionStorage.setItem('artify_filters', JSON.stringify(filters));
    router.push('/results');
  };

  const getButtonText = () => {
    if (selectedQuickPick === 'surprends_moi') return 'Mes recommandations ✨';
    if (selectedQuickPick) {
      const pick = quickPicks.find(p => p.id === selectedQuickPick);
      return `Voir ${pick?.label.toLowerCase()} →`;
    }
    return 'Explorer Paris →';
  };

  const hasSelection = selectedQuickPick || singleDate || dateRange?.from || selectedCategories.length > 0;

  // Afficher l'onboarding si nécessaire
  if (showOnboarding && !isFirstLoad) {
    return <Onboarding onComplete={() => {
      setShowOnboarding(false);
      setHasProfile(true);
      const profileManager = getUserProfileManager();
      setUserStats(profileManager.getStats());
    }} />;
  }

  return (
    <main style={styles.main}>
      {/* Background decorations */}
      <div style={styles.bgOrb1} />
      <div style={styles.bgOrb2} />
      
      <div style={styles.container}>
        {/* Header simplifié */}
        <header style={styles.header}>
          <p style={styles.greeting}>{greeting}</p>
          <h1 style={styles.title}>Que faire à Paris ?</h1>
          {hasProfile && userStats?.topCategories && userStats.topCategories.length > 0 ? (
            <p style={styles.subtitle}>
              <span style={styles.aiTag}>✨ IA</span>
              Recommandations personnalisées pour vous
            </p>
          ) : (
            <p style={styles.subtitle}>Choisis ton moment préféré</p>
          )}
        </header>

        {/* Quick Picks - Section principale */}
        <section style={styles.quickPicksSection}>
          <div style={styles.quickPicksRow}>
            {quickPicks.map((pick) => {
              const isSelected = selectedQuickPick === pick.id;
              const isAI = pick.id === 'surprends_moi' && hasProfile;
              return (
                <button
                  key={pick.id}
                  onClick={() => handleQuickPick(pick.id)}
                  style={{
                    ...styles.quickPickButton,
                    background: isSelected ? pick.gradient : 'rgba(24, 24, 31, 0.8)',
                    borderColor: isSelected ? pick.color : 'rgba(255,255,255,0.08)',
                    transform: isSelected ? 'scale(1.02)' : 'scale(1)',
                    boxShadow: isSelected ? `0 8px 24px ${pick.color}40` : 'none',
                  }}
                >
                  <span style={styles.quickPickEmoji}>{pick.emoji}</span>
                  <span style={{
                    ...styles.quickPickLabel,
                    color: isSelected ? '#fff' : '#E4E4E7',
                  }}>
                    {pick.label}
                  </span>
                  {isAI && (
                    <span style={styles.aiIndicator}>IA</span>
                  )}
                </button>
              );
            })}
          </div>
        </section>

        {/* AI Recommendation Card - si profil existe */}
        {hasProfile && selectedQuickPick === 'surprends_moi' && (
          <div style={styles.aiCard}>
            <div style={styles.aiCardHeader}>
              <span style={styles.aiCardIcon}>🤖</span>
              <div>
                <span style={styles.aiCardTitle}>Recommandations IA</span>
                <span style={styles.aiCardSubtitle}>
                  Basées sur vos {userStats?.topCategories?.length || 0} catégories préférées
                </span>
              </div>
            </div>
            <div style={styles.aiCardTags}>
              {userStats?.topCategories?.slice(0, 3).map((cat, i) => (
                <span key={i} style={styles.aiCardTag}>
                  {categories.find(c => c.id === cat.category)?.emoji || '📌'} {cat.category}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Bouton principal CTA */}
        <button
          onClick={handleSubmit}
          disabled={isLoading}
          style={{
            ...styles.mainButton,
            opacity: isLoading ? 0.7 : 1,
          }}
        >
          {isLoading ? (
            <span style={styles.buttonContent}>
              <span style={styles.spinner} />
              Recherche...
            </span>
          ) : (
            <span style={styles.buttonContent}>
              {getButtonText()}
            </span>
          )}
        </button>

        {/* Séparateur avec options avancées */}
        <div style={styles.advancedSection}>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            style={styles.advancedToggle}
          >
            <span style={styles.advancedToggleText}>
              {showAdvanced ? '✕ Masquer les options' : '⚙️ Plus d\'options'}
            </span>
          </button>

          {showAdvanced && (
            <div style={styles.advancedContent}>
              {/* Calendrier */}
              <div style={styles.advancedCard}>
                <button
                  onClick={() => setShowCalendar(!showCalendar)}
                  style={styles.advancedCardHeader}
                >
                  <span style={styles.advancedCardIcon}>📅</span>
                  <span style={styles.advancedCardTitle}>Date précise</span>
                  <span style={{
                    ...styles.chevron,
                    transform: showCalendar ? 'rotate(180deg)' : 'rotate(0deg)',
                  }}>
                    ▼
                  </span>
                </button>

                {showCalendar && (
                  <div style={styles.calendarPanel}>
                    <div style={styles.modeToggle}>
                      <button
                        onClick={() => { setIsRangeMode(false); setDateRange(undefined); }}
                        style={{
                          ...styles.modeButton,
                          backgroundColor: !isRangeMode ? 'rgba(168, 85, 247, 0.2)' : 'transparent',
                          color: !isRangeMode ? '#fff' : '#71717A',
                        }}
                      >
                        Une date
                      </button>
                      <button
                        onClick={() => { setIsRangeMode(true); setSingleDate(undefined); }}
                        style={{
                          ...styles.modeButton,
                          backgroundColor: isRangeMode ? 'rgba(168, 85, 247, 0.2)' : 'transparent',
                          color: isRangeMode ? '#fff' : '#71717A',
                        }}
                      >
                        Période
                      </button>
                    </div>

                    <div style={styles.calendarWrapper}>
                      {isRangeMode ? (
                        <DayPicker
                          mode="range"
                          selected={dateRange}
                          onSelect={handleRangeSelect}
                          locale={fr}
                          disabled={{ before: today }}
                          numberOfMonths={1}
                          showOutsideDays
                          classNames={{
                            root: 'artify-calendar',
                          }}
                        />
                      ) : (
                        <DayPicker
                          mode="single"
                          selected={singleDate}
                          onSelect={handleDateSelect}
                          locale={fr}
                          disabled={{ before: today }}
                          numberOfMonths={1}
                          showOutsideDays
                          classNames={{
                            root: 'artify-calendar',
                          }}
                        />
                      )}
                    </div>
                    
                    {(singleDate || dateRange?.from) && (
                      <div style={styles.dateSelected}>
                        ✓ {singleDate 
                          ? format(singleDate, 'EEEE d MMMM', { locale: fr })
                          : dateRange?.from && dateRange?.to
                            ? `${format(dateRange.from, 'd MMM', { locale: fr })} → ${format(dateRange.to, 'd MMM', { locale: fr })}`
                            : dateRange?.from && format(dateRange.from, 'd MMM', { locale: fr })
                        }
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Catégories */}
              <div style={styles.advancedCard}>
                <div style={styles.advancedCardHeader}>
                  <span style={styles.advancedCardIcon}>🎯</span>
                  <span style={styles.advancedCardTitle}>Filtrer par type</span>
                </div>
                <div style={styles.categoriesGrid}>
                  {categories.map((category) => {
                    const isSelected = selectedCategories.includes(category.id);
                    return (
                      <button
                        key={category.id}
                        onClick={() => toggleCategory(category.id)}
                        style={{
                          ...styles.categoryChip,
                          borderColor: isSelected ? category.color : 'rgba(255,255,255,0.1)',
                          backgroundColor: isSelected ? `${category.color}25` : 'transparent',
                        }}
                      >
                        <span>{category.emoji}</span>
                        <span style={{
                          color: isSelected ? '#fff' : '#A1A1AA',
                          fontWeight: isSelected ? 500 : 400,
                        }}>
                          {category.label}
                        </span>
                      </button>
                    );
                  })}
                </div>
                {selectedCategories.length > 0 && (
                  <button
                    onClick={() => setSelectedCategories([])}
                    style={styles.clearFilters}
                  >
                    Effacer les filtres
                  </button>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Résumé de sélection */}
        {hasSelection && (
          <div style={styles.selectionBadge}>
            <span style={styles.selectionDot} />
            <span style={styles.selectionText}>
              {selectedQuickPick && quickPicks.find(p => p.id === selectedQuickPick)?.label}
              {singleDate && format(singleDate, 'd MMM', { locale: fr })}
              {dateRange?.from && !selectedQuickPick && `${format(dateRange.from, 'd MMM', { locale: fr })}${dateRange.to ? ` → ${format(dateRange.to, 'd MMM', { locale: fr })}` : ''}`}
              {selectedCategories.length > 0 && ` • ${selectedCategories.length} filtre${selectedCategories.length > 1 ? 's' : ''}`}
            </span>
          </div>
        )}

        {/* Profil utilisateur */}
        {hasProfile && (
          <button
            onClick={() => {
              localStorage.removeItem('artify_onboarding_complete');
              localStorage.removeItem('artify_user_profile');
              setHasProfile(false);
              setShowOnboarding(true);
            }}
            style={styles.profileButton}
          >
            <span>👤</span>
            <span>Modifier mes préférences</span>
          </button>
        )}

        {/* Footer */}
        <footer style={styles.footer}>
          <span style={styles.footerText}>
            {hasProfile ? '🤖 Recommandations IA personnalisées' : '✨ Plus de 500 événements à Paris'}
          </span>
        </footer>
      </div>

      {/* Calendar Styles */}
      <style jsx global>{`
        .artify-calendar {
          --rdp-cell-size: 42px;
          --rdp-accent-color: #A855F7;
          --rdp-background-color: rgba(168, 85, 247, 0.15);
          font-family: 'Outfit', sans-serif;
          margin: 0 auto;
        }
        
        .artify-calendar .rdp-caption_label {
          color: #fff;
          font-size: 15px;
          font-weight: 600;
          text-transform: capitalize;
        }
        
        .artify-calendar .rdp-nav button {
          color: #A1A1AA;
          width: 28px;
          height: 28px;
          background: rgba(255,255,255,0.05);
          border-radius: 8px;
        }
        
        .artify-calendar .rdp-nav button:hover {
          background: rgba(255,255,255,0.1);
          color: #fff;
        }
        
        .artify-calendar .rdp-head_cell {
          color: #71717A;
          font-size: 11px;
          font-weight: 500;
          text-transform: uppercase;
        }
        
        .artify-calendar .rdp-day {
          color: #A1A1AA;
          border-radius: 8px;
          font-weight: 400;
          font-size: 14px;
        }
        
        .artify-calendar .rdp-day:hover:not(.rdp-day_selected):not(.rdp-day_disabled) {
          background: rgba(255,255,255,0.1);
          color: #fff;
        }
        
        .artify-calendar .rdp-day_today {
          color: #A855F7;
          font-weight: 600;
          background: rgba(168, 85, 247, 0.1);
        }
        
        .artify-calendar .rdp-day_selected,
        .artify-calendar .rdp-day_range_start,
        .artify-calendar .rdp-day_range_end {
          background: linear-gradient(135deg, #A855F7, #EC4899) !important;
          color: #fff !important;
          font-weight: 600;
        }
        
        .artify-calendar .rdp-day_range_middle {
          background: rgba(168, 85, 247, 0.2) !important;
          color: #fff !important;
        }
        
        .artify-calendar .rdp-day_disabled {
          color: #3F3F46;
        }
        
        .artify-calendar .rdp-day_outside {
          color: #27272A;
        }
      `}</style>
    </main>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  main: {
    minHeight: '100vh',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'flex-start',
    padding: '32px 20px 60px',
    position: 'relative',
    overflow: 'hidden',
  },
  bgOrb1: {
    position: 'fixed',
    top: '-30%',
    left: '-20%',
    width: '600px',
    height: '600px',
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, transparent 60%)',
    filter: 'blur(80px)',
    pointerEvents: 'none',
  },
  bgOrb2: {
    position: 'fixed',
    bottom: '-30%',
    right: '-20%',
    width: '700px',
    height: '700px',
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(236, 72, 153, 0.12) 0%, transparent 60%)',
    filter: 'blur(80px)',
    pointerEvents: 'none',
  },
  container: {
    width: '100%',
    maxWidth: '440px',
    position: 'relative',
    zIndex: 1,
  },
  header: {
    textAlign: 'center',
    marginBottom: '36px',
  },
  greeting: {
    fontSize: '15px',
    color: '#A1A1AA',
    marginBottom: '8px',
  },
  title: {
    fontSize: '32px',
    fontWeight: 700,
    letterSpacing: '-1px',
    color: '#fff',
    marginBottom: '8px',
  },
  subtitle: {
    fontSize: '16px',
    color: '#71717A',
    fontWeight: 400,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
  },
  aiTag: {
    fontSize: '11px',
    fontWeight: 600,
    padding: '3px 8px',
    background: 'linear-gradient(135deg, #A855F7, #EC4899)',
    borderRadius: '10px',
    color: '#fff',
  },
  quickPicksSection: {
    marginBottom: '24px',
  },
  quickPicksRow: {
    display: 'grid',
    gridTemplateColumns: 'repeat(5, 1fr)',
    gap: '10px',
  },
  quickPickButton: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '16px 8px',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '16px',
    transition: 'all 0.25s ease',
    backdropFilter: 'blur(10px)',
    cursor: 'pointer',
    gap: '6px',
    position: 'relative',
  },
  quickPickEmoji: {
    fontSize: '24px',
  },
  quickPickLabel: {
    fontSize: '11px',
    fontWeight: 500,
    textAlign: 'center',
  },
  aiIndicator: {
    position: 'absolute',
    top: '6px',
    right: '6px',
    fontSize: '8px',
    fontWeight: 700,
    padding: '2px 5px',
    background: 'linear-gradient(135deg, #A855F7, #EC4899)',
    borderRadius: '6px',
    color: '#fff',
  },
  aiCard: {
    background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(236, 72, 153, 0.1))',
    border: '1px solid rgba(168, 85, 247, 0.3)',
    borderRadius: '16px',
    padding: '16px',
    marginBottom: '20px',
  },
  aiCardHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '12px',
  },
  aiCardIcon: {
    fontSize: '28px',
  },
  aiCardTitle: {
    display: 'block',
    fontSize: '15px',
    fontWeight: 600,
    color: '#fff',
  },
  aiCardSubtitle: {
    display: 'block',
    fontSize: '12px',
    color: '#A1A1AA',
  },
  aiCardTags: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap',
  },
  aiCardTag: {
    fontSize: '11px',
    padding: '4px 10px',
    background: 'rgba(255,255,255,0.1)',
    borderRadius: '12px',
    color: '#E4E4E7',
  },
  mainButton: {
    width: '100%',
    padding: '18px 28px',
    background: 'linear-gradient(135deg, #A855F7 0%, #EC4899 100%)',
    color: '#FFFFFF',
    border: 'none',
    borderRadius: '16px',
    fontSize: '17px',
    fontWeight: 600,
    transition: 'all 0.3s ease',
    boxShadow: '0 8px 32px rgba(168, 85, 247, 0.4)',
    cursor: 'pointer',
    marginBottom: '20px',
  },
  buttonContent: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '10px',
  },
  spinner: {
    width: '18px',
    height: '18px',
    border: '2px solid rgba(255,255,255,0.3)',
    borderTopColor: '#fff',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  advancedSection: {
    marginBottom: '20px',
  },
  advancedToggle: {
    width: '100%',
    padding: '12px',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    justifyContent: 'center',
  },
  advancedToggleText: {
    fontSize: '13px',
    color: '#71717A',
    fontWeight: 500,
    transition: 'color 0.2s ease',
  },
  advancedContent: {
    marginTop: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  advancedCard: {
    background: 'rgba(24, 24, 31, 0.6)',
    backdropFilter: 'blur(20px)',
    borderRadius: '16px',
    border: '1px solid rgba(255,255,255,0.06)',
    overflow: 'hidden',
  },
  advancedCardHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '16px',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    width: '100%',
    textAlign: 'left',
  },
  advancedCardIcon: {
    fontSize: '20px',
  },
  advancedCardTitle: {
    flex: 1,
    fontSize: '14px',
    fontWeight: 500,
    color: '#E4E4E7',
  },
  chevron: {
    fontSize: '10px',
    color: '#71717A',
    transition: 'transform 0.3s ease',
  },
  calendarPanel: {
    padding: '0 16px 16px',
  },
  modeToggle: {
    display: 'flex',
    gap: '8px',
    marginBottom: '16px',
    padding: '4px',
    background: 'rgba(255,255,255,0.04)',
    borderRadius: '10px',
  },
  modeButton: {
    flex: 1,
    padding: '8px 12px',
    border: 'none',
    borderRadius: '8px',
    fontSize: '12px',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  calendarWrapper: {
    display: 'flex',
    justifyContent: 'center',
  },
  dateSelected: {
    marginTop: '12px',
    padding: '10px 14px',
    background: 'rgba(168, 85, 247, 0.15)',
    borderRadius: '10px',
    fontSize: '13px',
    color: '#A855F7',
    fontWeight: 500,
    textAlign: 'center',
    textTransform: 'capitalize',
  },
  categoriesGrid: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    padding: '0 16px 16px',
  },
  categoryChip: {
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
    padding: '8px 12px',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '20px',
    fontSize: '12px',
    transition: 'all 0.2s ease',
    cursor: 'pointer',
    background: 'transparent',
  },
  clearFilters: {
    display: 'block',
    margin: '0 16px 16px',
    padding: '8px',
    background: 'none',
    border: 'none',
    fontSize: '12px',
    color: '#71717A',
    cursor: 'pointer',
    textAlign: 'center',
  },
  selectionBadge: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    padding: '10px 16px',
    background: 'rgba(168, 85, 247, 0.1)',
    borderRadius: '20px',
    marginBottom: '24px',
  },
  selectionDot: {
    width: '6px',
    height: '6px',
    borderRadius: '50%',
    background: '#A855F7',
  },
  selectionText: {
    fontSize: '13px',
    color: '#A855F7',
    fontWeight: 500,
  },
  profileButton: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    width: '100%',
    padding: '12px',
    background: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '12px',
    color: '#A1A1AA',
    fontSize: '13px',
    cursor: 'pointer',
    marginBottom: '20px',
  },
  footer: {
    textAlign: 'center',
    paddingTop: '24px',
  },
  footerText: {
    fontSize: '13px',
    color: '#52525B',
  },
};
