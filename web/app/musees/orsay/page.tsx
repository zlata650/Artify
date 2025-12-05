'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Exhibition {
  id: string;
  title: string;
  slug: string;
  description: string;
  shortDescription: string;
  dateStart: string;
  dateEnd: string;
  status: 'current' | 'upcoming' | 'past';
  price: number;
  priceReduced: number;
  image: string | null;
  bookingUrl: string;
  featured: boolean;
  tags: string[];
}

interface Museum {
  name: string;
  address: string;
  arrondissement: number;
  website: string;
  bookingUrl: string;
  phone: string;
  metro: string[];
  hours: {
    regular: string;
    thursday: string;
    closed: string;
  };
  prices: {
    full: number;
    reduced: number;
    free: string;
    firstSunday: string;
  };
  description: string;
  image: string;
}

export default function OrsayPage() {
  const [museum, setMuseum] = useState<Museum | null>(null);
  const [exhibitions, setExhibitions] = useState<Exhibition[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'current' | 'upcoming'>('current');

  useEffect(() => {
    const loadData = async () => {
      try {
        const response = await fetch('/api/museums/orsay');
        const data = await response.json();
        
        if (data.success) {
          setMuseum(data.museum);
          setExhibitions(data.exhibitions);
        }
      } catch (error) {
        console.error('Error loading Orsay data:', error);
      }
      setIsLoading(false);
    };
    
    loadData();
  }, []);

  const formatDateRange = (start: string, end: string) => {
    const startDate = new Date(start);
    const endDate = new Date(end);
    
    const formatOptions: Intl.DateTimeFormatOptions = { 
      day: 'numeric', 
      month: 'long', 
      year: 'numeric' 
    };
    
    return `Du ${startDate.toLocaleDateString('fr-FR', formatOptions)} au ${endDate.toLocaleDateString('fr-FR', formatOptions)}`;
  };

  const getDaysRemaining = (endDate: string) => {
    const end = new Date(endDate);
    const today = new Date();
    const diffTime = end.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const currentExhibitions = exhibitions.filter(e => e.status === 'current');
  const upcomingExhibitions = exhibitions.filter(e => e.status === 'upcoming');

  if (isLoading) {
    return (
      <main style={styles.main}>
        <div style={styles.loadingContainer}>
          <div style={styles.spinner}></div>
          <p style={styles.loadingText}>Chargement des expositions...</p>
        </div>
      </main>
    );
  }

  return (
    <main style={styles.main}>
      {/* Background orbs */}
      <div style={styles.bgOrb1} />
      <div style={styles.bgOrb2} />
      
      <div style={styles.container}>
        {/* Back link */}
        <Link href="/" style={styles.backLink}>
          ← Retour à l'accueil
        </Link>

        {/* Museum Header */}
        <header style={styles.header}>
          <div style={styles.headerBadge}>🏛️ Musée</div>
          <h1 style={styles.title}>{museum?.name}</h1>
          <p style={styles.subtitle}>{museum?.description}</p>
          
          {/* Quick Info */}
          <div style={styles.quickInfo}>
            <div style={styles.infoItem}>
              <span style={styles.infoIcon}>📍</span>
              <span>{museum?.address}</span>
            </div>
            <div style={styles.infoItem}>
              <span style={styles.infoIcon}>🚇</span>
              <span>{museum?.metro.join(' • ')}</span>
            </div>
            <div style={styles.infoItem}>
              <span style={styles.infoIcon}>🕐</span>
              <span>{museum?.hours.regular} | {museum?.hours.thursday}</span>
            </div>
          </div>
        </header>

        {/* Tabs */}
        <div style={styles.tabs}>
          <button
            onClick={() => setActiveTab('current')}
            style={{
              ...styles.tab,
              backgroundColor: activeTab === 'current' ? 'rgba(249, 115, 22, 0.2)' : 'transparent',
              borderColor: activeTab === 'current' ? '#F97316' : 'rgba(255,255,255,0.1)',
              color: activeTab === 'current' ? '#F97316' : '#A1A1AA',
            }}
          >
            🎨 En cours ({currentExhibitions.length})
          </button>
          <button
            onClick={() => setActiveTab('upcoming')}
            style={{
              ...styles.tab,
              backgroundColor: activeTab === 'upcoming' ? 'rgba(59, 130, 246, 0.2)' : 'transparent',
              borderColor: activeTab === 'upcoming' ? '#3B82F6' : 'rgba(255,255,255,0.1)',
              color: activeTab === 'upcoming' ? '#3B82F6' : '#A1A1AA',
            }}
          >
            📅 À venir ({upcomingExhibitions.length})
          </button>
        </div>

        {/* Exhibitions Grid */}
        <div style={styles.exhibitionsGrid}>
          {(activeTab === 'current' ? currentExhibitions : upcomingExhibitions).map((expo) => {
            const daysRemaining = getDaysRemaining(expo.dateEnd);
            const isEnding = daysRemaining <= 30 && expo.status === 'current';
            
            return (
              <article key={expo.id} style={styles.exhibitionCard}>
                {/* Featured badge */}
                {expo.featured && (
                  <div style={styles.featuredBadge}>⭐ Exposition phare</div>
                )}
                
                {/* Urgency badge */}
                {isEnding && (
                  <div style={styles.urgencyBadge}>
                    ⏰ Plus que {daysRemaining} jours !
                  </div>
                )}

                {/* Image placeholder */}
                <div style={styles.imageContainer}>
                  {expo.image ? (
                    <img src={expo.image} alt={expo.title} style={styles.image} />
                  ) : (
                    <div style={styles.imagePlaceholder}>
                      <span style={styles.placeholderEmoji}>🖼️</span>
                    </div>
                  )}
                  
                  {/* Status overlay */}
                  <div style={{
                    ...styles.statusOverlay,
                    backgroundColor: expo.status === 'current' 
                      ? 'rgba(34, 197, 94, 0.9)' 
                      : 'rgba(59, 130, 246, 0.9)',
                  }}>
                    {expo.status === 'current' ? '🟢 En cours' : '🔵 À venir'}
                  </div>
                </div>

                {/* Content */}
                <div style={styles.cardContent}>
                  <h2 style={styles.expoTitle}>{expo.title}</h2>
                  
                  <p style={styles.expoDescription}>{expo.shortDescription}</p>
                  
                  {/* Date range */}
                  <div style={styles.dateRange}>
                    <span style={styles.dateIcon}>📅</span>
                    <span>{formatDateRange(expo.dateStart, expo.dateEnd)}</span>
                  </div>

                  {/* Tags */}
                  <div style={styles.tags}>
                    {expo.tags.slice(0, 4).map((tag) => (
                      <span key={tag} style={styles.tag}>#{tag}</span>
                    ))}
                  </div>

                  {/* Price & CTA */}
                  <div style={styles.cardFooter}>
                    <div style={styles.priceInfo}>
                      <span style={styles.price}>{expo.price}€</span>
                      <span style={styles.priceReduced}>TR: {expo.priceReduced}€</span>
                    </div>
                    
                    <a
                      href={expo.bookingUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={styles.bookButton}
                    >
                      🎟️ Réserver
                    </a>
                  </div>
                </div>
              </article>
            );
          })}
        </div>

        {/* Museum Info Panel */}
        <section style={styles.infoPanel}>
          <h2 style={styles.infoPanelTitle}>📋 Informations pratiques</h2>
          
          <div style={styles.infoPanelGrid}>
            <div style={styles.infoPanelCard}>
              <h3 style={styles.infoPanelCardTitle}>🎫 Tarifs</h3>
              <ul style={styles.infoList}>
                <li>Plein tarif : <strong>{museum?.prices.full}€</strong></li>
                <li>Tarif réduit : <strong>{museum?.prices.reduced}€</strong></li>
                <li>{museum?.prices.free}</li>
                <li>{museum?.prices.firstSunday}</li>
              </ul>
            </div>
            
            <div style={styles.infoPanelCard}>
              <h3 style={styles.infoPanelCardTitle}>🕐 Horaires</h3>
              <ul style={styles.infoList}>
                <li>{museum?.hours.regular}</li>
                <li>Jeudi : {museum?.hours.thursday}</li>
                <li style={{ color: '#EF4444' }}>{museum?.hours.closed}</li>
              </ul>
            </div>
            
            <div style={styles.infoPanelCard}>
              <h3 style={styles.infoPanelCardTitle}>📍 Accès</h3>
              <ul style={styles.infoList}>
                <li><strong>Adresse :</strong> {museum?.address}</li>
                <li><strong>Métro :</strong> {museum?.metro.join(', ')}</li>
              </ul>
            </div>
          </div>

          {/* Main CTA */}
          <div style={styles.mainCta}>
            <a
              href={museum?.bookingUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={styles.mainCtaButton}
            >
              🎟️ Réserver mes billets sur le site officiel
            </a>
            <a
              href={museum?.website}
              target="_blank"
              rel="noopener noreferrer"
              style={styles.secondaryCta}
            >
              🌐 Visiter le site du musée
            </a>
          </div>
        </section>
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
    top: '0',
    right: '-20%',
    width: '600px',
    height: '600px',
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(249, 115, 22, 0.15) 0%, transparent 70%)',
    filter: 'blur(60px)',
    pointerEvents: 'none',
  },
  bgOrb2: {
    position: 'fixed',
    bottom: '-20%',
    left: '-10%',
    width: '500px',
    height: '500px',
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%)',
    filter: 'blur(60px)',
    pointerEvents: 'none',
  },
  container: {
    maxWidth: '1100px',
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
  header: {
    marginBottom: '40px',
    textAlign: 'center',
  },
  headerBadge: {
    display: 'inline-block',
    padding: '8px 16px',
    backgroundColor: 'rgba(249, 115, 22, 0.15)',
    color: '#F97316',
    borderRadius: '20px',
    fontSize: '13px',
    fontWeight: 600,
    marginBottom: '16px',
  },
  title: {
    fontSize: '48px',
    fontWeight: 800,
    letterSpacing: '-2px',
    background: 'linear-gradient(135deg, #fff 0%, #F97316 50%, #3B82F6 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    marginBottom: '16px',
  },
  subtitle: {
    fontSize: '16px',
    color: '#A1A1AA',
    maxWidth: '700px',
    margin: '0 auto 24px',
    lineHeight: 1.7,
  },
  quickInfo: {
    display: 'flex',
    justifyContent: 'center',
    flexWrap: 'wrap',
    gap: '20px',
  },
  infoItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '14px',
    color: '#71717A',
  },
  infoIcon: {
    fontSize: '16px',
  },
  tabs: {
    display: 'flex',
    gap: '12px',
    marginBottom: '32px',
    justifyContent: 'center',
  },
  tab: {
    padding: '14px 24px',
    border: '2px solid',
    borderRadius: '16px',
    fontSize: '15px',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  exhibitionsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
    gap: '24px',
    marginBottom: '48px',
  },
  exhibitionCard: {
    backgroundColor: 'rgba(24, 24, 31, 0.8)',
    backdropFilter: 'blur(20px)',
    borderRadius: '24px',
    overflow: 'hidden',
    border: '1px solid rgba(255,255,255,0.08)',
    position: 'relative',
    transition: 'all 0.3s ease',
  },
  featuredBadge: {
    position: 'absolute',
    top: '16px',
    left: '16px',
    zIndex: 10,
    padding: '8px 12px',
    backgroundColor: 'rgba(234, 179, 8, 0.9)',
    color: '#000',
    borderRadius: '10px',
    fontSize: '12px',
    fontWeight: 600,
  },
  urgencyBadge: {
    position: 'absolute',
    top: '16px',
    right: '16px',
    zIndex: 10,
    padding: '8px 12px',
    backgroundColor: 'rgba(239, 68, 68, 0.9)',
    color: '#fff',
    borderRadius: '10px',
    fontSize: '12px',
    fontWeight: 600,
    animation: 'pulse 2s ease-in-out infinite',
  },
  imageContainer: {
    position: 'relative',
    height: '200px',
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  },
  imagePlaceholder: {
    width: '100%',
    height: '100%',
    background: 'linear-gradient(135deg, rgba(249, 115, 22, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  placeholderEmoji: {
    fontSize: '64px',
    opacity: 0.5,
  },
  statusOverlay: {
    position: 'absolute',
    bottom: '12px',
    right: '12px',
    padding: '6px 12px',
    borderRadius: '8px',
    fontSize: '12px',
    fontWeight: 600,
    color: '#fff',
  },
  cardContent: {
    padding: '24px',
  },
  expoTitle: {
    fontSize: '22px',
    fontWeight: 700,
    color: '#fff',
    marginBottom: '12px',
    lineHeight: 1.3,
  },
  expoDescription: {
    fontSize: '14px',
    color: '#A1A1AA',
    lineHeight: 1.6,
    marginBottom: '16px',
  },
  dateRange: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '13px',
    color: '#71717A',
    marginBottom: '16px',
    padding: '12px',
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: '10px',
  },
  dateIcon: {
    fontSize: '14px',
  },
  tags: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    marginBottom: '20px',
  },
  tag: {
    fontSize: '11px',
    color: '#F97316',
    backgroundColor: 'rgba(249, 115, 22, 0.1)',
    padding: '4px 10px',
    borderRadius: '12px',
  },
  cardFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: '16px',
    borderTop: '1px solid rgba(255,255,255,0.05)',
  },
  priceInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  price: {
    fontSize: '24px',
    fontWeight: 700,
    color: '#fff',
  },
  priceReduced: {
    fontSize: '12px',
    color: '#71717A',
  },
  bookButton: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '14px 24px',
    background: 'linear-gradient(135deg, #F97316 0%, #EA580C 100%)',
    color: '#fff',
    borderRadius: '14px',
    fontSize: '15px',
    fontWeight: 600,
    textDecoration: 'none',
    boxShadow: '0 8px 24px rgba(249, 115, 22, 0.4)',
    transition: 'all 0.2s ease',
  },
  infoPanel: {
    backgroundColor: 'rgba(24, 24, 31, 0.7)',
    backdropFilter: 'blur(20px)',
    borderRadius: '24px',
    padding: '32px',
    border: '1px solid rgba(255,255,255,0.08)',
  },
  infoPanelTitle: {
    fontSize: '22px',
    fontWeight: 700,
    color: '#fff',
    marginBottom: '24px',
    textAlign: 'center',
  },
  infoPanelGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
    marginBottom: '32px',
  },
  infoPanelCard: {
    padding: '20px',
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: '16px',
    border: '1px solid rgba(255,255,255,0.05)',
  },
  infoPanelCardTitle: {
    fontSize: '16px',
    fontWeight: 600,
    color: '#fff',
    marginBottom: '16px',
  },
  infoList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
    fontSize: '14px',
    color: '#A1A1AA',
    lineHeight: 1.8,
  },
  mainCta: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '16px',
  },
  mainCtaButton: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '10px',
    padding: '20px 40px',
    background: 'linear-gradient(135deg, #F97316 0%, #3B82F6 100%)',
    color: '#fff',
    borderRadius: '16px',
    fontSize: '17px',
    fontWeight: 600,
    textDecoration: 'none',
    boxShadow: '0 8px 32px rgba(249, 115, 22, 0.3)',
    transition: 'all 0.3s ease',
  },
  secondaryCta: {
    fontSize: '14px',
    color: '#71717A',
    textDecoration: 'none',
    transition: 'color 0.2s ease',
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
    border: '3px solid rgba(249, 115, 22, 0.2)',
    borderTopColor: '#F97316',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  loadingText: {
    fontSize: '15px',
    color: '#71717A',
  },
};


