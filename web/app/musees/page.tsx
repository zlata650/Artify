'use client';

import Link from 'next/link';

const MUSEUMS = [
  {
    id: 'orsay',
    name: 'Musée d\'Orsay',
    description: 'La plus importante collection d\'art impressionniste au monde',
    emoji: '🎨',
    color: '#F97316',
    exhibitionCount: 4,
    upcomingCount: 2,
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Mus%C3%A9e_d%27Orsay%2C_Paris_7e%2C_France.jpg/400px-Mus%C3%A9e_d%27Orsay%2C_Paris_7e%2C_France.jpg',
    featured: true,
  },
  {
    id: 'louvre',
    name: 'Musée du Louvre',
    description: 'Le plus grand musée d\'art au monde',
    emoji: '🏛️',
    color: '#A855F7',
    exhibitionCount: 0,
    upcomingCount: 0,
    image: null,
    featured: false,
    comingSoon: true,
  },
  {
    id: 'pompidou',
    name: 'Centre Pompidou',
    description: 'Art moderne et contemporain',
    emoji: '🔴',
    color: '#3B82F6',
    exhibitionCount: 0,
    upcomingCount: 0,
    image: null,
    featured: false,
    comingSoon: true,
  },
  {
    id: 'orangerie',
    name: 'Musée de l\'Orangerie',
    description: 'Les Nymphéas de Monet',
    emoji: '🌸',
    color: '#EC4899',
    exhibitionCount: 0,
    upcomingCount: 0,
    image: null,
    featured: false,
    comingSoon: true,
  },
];

export default function MuseumsPage() {
  return (
    <main style={styles.main}>
      {/* Background */}
      <div style={styles.bgOrb1} />
      <div style={styles.bgOrb2} />
      
      <div style={styles.container}>
        {/* Back link */}
        <Link href="/" style={styles.backLink}>
          ← Retour à l'accueil
        </Link>

        {/* Header */}
        <header style={styles.header}>
          <div style={styles.headerBadge}>🏛️ Musées de Paris</div>
          <h1 style={styles.title}>Expositions</h1>
          <p style={styles.subtitle}>
            Découvrez les expositions en cours et à venir dans les plus grands musées parisiens
          </p>
        </header>

        {/* Museums Grid */}
        <div style={styles.museumsGrid}>
          {MUSEUMS.map((museum) => (
            <Link
              key={museum.id}
              href={museum.comingSoon ? '#' : `/musees/${museum.id}`}
              style={{
                ...styles.museumCard,
                borderColor: museum.featured ? museum.color : 'rgba(255,255,255,0.08)',
                opacity: museum.comingSoon ? 0.6 : 1,
                cursor: museum.comingSoon ? 'not-allowed' : 'pointer',
              }}
            >
              {/* Featured badge */}
              {museum.featured && (
                <div style={{
                  ...styles.featuredBadge,
                  backgroundColor: museum.color,
                }}>
                  ⭐ Nouveau
                </div>
              )}
              
              {/* Coming soon badge */}
              {museum.comingSoon && (
                <div style={styles.comingSoonBadge}>
                  🔜 Bientôt disponible
                </div>
              )}

              {/* Image/Emoji */}
              <div style={{
                ...styles.museumImage,
                background: museum.image 
                  ? `url(${museum.image}) center/cover no-repeat` 
                  : `linear-gradient(135deg, ${museum.color}30 0%, ${museum.color}10 100%)`,
              }}>
                {!museum.image && (
                  <span style={styles.museumEmoji}>{museum.emoji}</span>
                )}
              </div>

              {/* Content */}
              <div style={styles.museumContent}>
                <h2 style={styles.museumName}>{museum.name}</h2>
                <p style={styles.museumDescription}>{museum.description}</p>
                
                {/* Stats */}
                {(museum.exhibitionCount > 0 || museum.upcomingCount > 0) && (
                  <div style={styles.museumStats}>
                    {museum.exhibitionCount > 0 && (
                      <span style={{
                        ...styles.statBadge,
                        backgroundColor: 'rgba(34, 197, 94, 0.15)',
                        color: '#22C55E',
                      }}>
                        🟢 {museum.exhibitionCount} en cours
                      </span>
                    )}
                    {museum.upcomingCount > 0 && (
                      <span style={{
                        ...styles.statBadge,
                        backgroundColor: 'rgba(59, 130, 246, 0.15)',
                        color: '#3B82F6',
                      }}>
                        🔵 {museum.upcomingCount} à venir
                      </span>
                    )}
                  </div>
                )}

                {/* CTA */}
                {!museum.comingSoon && (
                  <div style={styles.ctaContainer}>
                    <span style={{
                      ...styles.viewButton,
                      background: `linear-gradient(135deg, ${museum.color} 0%, ${museum.color}99 100%)`,
                    }}>
                      Voir les expositions →
                    </span>
                  </div>
                )}
              </div>
            </Link>
          ))}
        </div>

        {/* Info banner */}
        <div style={styles.infoBanner}>
          <span style={styles.infoIcon}>ℹ️</span>
          <p style={styles.infoText}>
            Nous ajoutons régulièrement de nouveaux musées et expositions. 
            Les informations sont mises à jour quotidiennement.
          </p>
        </div>
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
    top: '-10%',
    right: '-10%',
    width: '500px',
    height: '500px',
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(249, 115, 22, 0.12) 0%, transparent 70%)',
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
    background: 'radial-gradient(circle, rgba(168, 85, 247, 0.1) 0%, transparent 70%)',
    filter: 'blur(60px)',
    pointerEvents: 'none',
  },
  container: {
    maxWidth: '1000px',
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
  },
  header: {
    textAlign: 'center',
    marginBottom: '48px',
  },
  headerBadge: {
    display: 'inline-block',
    padding: '8px 16px',
    backgroundColor: 'rgba(168, 85, 247, 0.15)',
    color: '#A855F7',
    borderRadius: '20px',
    fontSize: '13px',
    fontWeight: 600,
    marginBottom: '16px',
  },
  title: {
    fontSize: '48px',
    fontWeight: 800,
    letterSpacing: '-2px',
    background: 'linear-gradient(135deg, #fff 0%, #F97316 50%, #A855F7 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    marginBottom: '12px',
  },
  subtitle: {
    fontSize: '16px',
    color: '#71717A',
    maxWidth: '500px',
    margin: '0 auto',
    lineHeight: 1.6,
  },
  museumsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '24px',
    marginBottom: '48px',
  },
  museumCard: {
    backgroundColor: 'rgba(24, 24, 31, 0.8)',
    backdropFilter: 'blur(20px)',
    borderRadius: '24px',
    overflow: 'hidden',
    border: '2px solid rgba(255,255,255,0.08)',
    textDecoration: 'none',
    color: 'inherit',
    transition: 'all 0.3s ease',
    position: 'relative',
  },
  featuredBadge: {
    position: 'absolute',
    top: '16px',
    left: '16px',
    zIndex: 10,
    padding: '6px 12px',
    color: '#fff',
    borderRadius: '10px',
    fontSize: '12px',
    fontWeight: 600,
  },
  comingSoonBadge: {
    position: 'absolute',
    top: '16px',
    right: '16px',
    zIndex: 10,
    padding: '6px 12px',
    backgroundColor: 'rgba(113, 113, 122, 0.9)',
    color: '#fff',
    borderRadius: '10px',
    fontSize: '12px',
    fontWeight: 600,
  },
  museumImage: {
    height: '160px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  museumEmoji: {
    fontSize: '64px',
  },
  museumContent: {
    padding: '24px',
  },
  museumName: {
    fontSize: '22px',
    fontWeight: 700,
    color: '#fff',
    marginBottom: '8px',
  },
  museumDescription: {
    fontSize: '14px',
    color: '#A1A1AA',
    lineHeight: 1.5,
    marginBottom: '16px',
  },
  museumStats: {
    display: 'flex',
    gap: '8px',
    marginBottom: '20px',
    flexWrap: 'wrap',
  },
  statBadge: {
    fontSize: '12px',
    fontWeight: 500,
    padding: '6px 12px',
    borderRadius: '10px',
  },
  ctaContainer: {
    paddingTop: '16px',
    borderTop: '1px solid rgba(255,255,255,0.05)',
  },
  viewButton: {
    display: 'inline-block',
    padding: '12px 20px',
    borderRadius: '12px',
    fontSize: '14px',
    fontWeight: 600,
    color: '#fff',
    transition: 'all 0.2s ease',
  },
  infoBanner: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    padding: '20px 24px',
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    borderRadius: '16px',
    border: '1px solid rgba(59, 130, 246, 0.2)',
  },
  infoIcon: {
    fontSize: '24px',
  },
  infoText: {
    fontSize: '14px',
    color: '#A1A1AA',
    margin: 0,
  },
};


