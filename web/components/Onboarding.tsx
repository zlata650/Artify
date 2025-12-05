'use client';

import { useState, useEffect } from 'react';
import { getUserProfileManager } from '@/lib/recommendations';

interface OnboardingProps {
  onComplete: () => void;
}

const categories = [
  { id: 'musique', emoji: '🎵', label: 'Musique & Concerts', color: '#A855F7' },
  { id: 'spectacles', emoji: '🎭', label: 'Spectacles & Théâtre', color: '#F43F5E' },
  { id: 'arts_visuels', emoji: '🎨', label: 'Expos & Musées', color: '#F97316' },
  { id: 'gastronomie', emoji: '🍷', label: 'Food & Vins', color: '#EC4899' },
  { id: 'nightlife', emoji: '🌙', label: 'Clubs & Soirées', color: '#6366F1' },
  { id: 'sport', emoji: '🏃', label: 'Sport & Bien-être', color: '#06B6D4' },
  { id: 'culture', emoji: '📚', label: 'Culture & Cinéma', color: '#3B82F6' },
  { id: 'ateliers', emoji: '🖌️', label: 'Ateliers créatifs', color: '#22C55E' },
  { id: 'rencontres', emoji: '👥', label: 'Meetups & Social', color: '#8B5CF6' },
];

const budgetOptions = [
  { id: 'gratuit', emoji: '🆓', label: 'Gratuit', desc: 'Événements gratuits' },
  { id: '0-20', emoji: '💚', label: 'Petit budget', desc: 'Moins de 20€' },
  { id: '20-50', emoji: '💛', label: 'Moyen', desc: '20-50€' },
  { id: '50-100', emoji: '🧡', label: 'Premium', desc: '50€+' },
];

const timeOptions = [
  { id: 'matin', emoji: '🌅', label: 'Matinées', time: 'Avant 12h' },
  { id: 'apres_midi', emoji: '☀️', label: 'Après-midi', time: '12h-18h' },
  { id: 'soir', emoji: '🌆', label: 'Soirées', time: '18h-23h' },
  { id: 'nuit', emoji: '🌙', label: 'Nuit', time: 'Après 23h' },
];

const vibeOptions = [
  { id: 'festif', emoji: '🎉', label: 'Festif' },
  { id: 'culturel', emoji: '🎭', label: 'Culturel' },
  { id: 'intime', emoji: '💕', label: 'Intime' },
  { id: 'social', emoji: '👥', label: 'Social' },
  { id: 'creatif', emoji: '✨', label: 'Créatif' },
  { id: 'sportif', emoji: '💪', label: 'Sportif' },
];

export default function Onboarding({ onComplete }: OnboardingProps) {
  const [step, setStep] = useState(0);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedBudgets, setSelectedBudgets] = useState<string[]>([]);
  const [selectedTimes, setSelectedTimes] = useState<string[]>([]);
  const [selectedVibes, setSelectedVibes] = useState<string[]>([]);
  const [isComplete, setIsComplete] = useState(false);

  const toggleItem = (item: string, list: string[], setList: (items: string[]) => void) => {
    if (list.includes(item)) {
      setList(list.filter(i => i !== item));
    } else {
      setList([...list, item]);
    }
  };

  const handleComplete = () => {
    // Sauvegarder les préférences
    const profileManager = getUserProfileManager();
    profileManager.setExplicitPreferences({
      categories: selectedCategories as any[],
      budgets: selectedBudgets as any[],
      times: selectedTimes as any[],
      ambiances: selectedVibes as any[],
    });
    
    // Marquer comme complété
    localStorage.setItem('artify_onboarding_complete', 'true');
    setIsComplete(true);
    
    setTimeout(() => {
      onComplete();
    }, 1500);
  };

  const canProceed = () => {
    switch (step) {
      case 0: return selectedCategories.length >= 2;
      case 1: return selectedBudgets.length >= 1;
      case 2: return selectedTimes.length >= 1;
      case 3: return selectedVibes.length >= 1;
      default: return true;
    }
  };

  const steps = [
    {
      title: "Qu'est-ce qui vous passionne ?",
      subtitle: "Choisissez au moins 2 catégories",
      content: (
        <div style={styles.grid}>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => toggleItem(cat.id, selectedCategories, setSelectedCategories)}
              style={{
                ...styles.card,
                borderColor: selectedCategories.includes(cat.id) ? cat.color : 'rgba(255,255,255,0.1)',
                backgroundColor: selectedCategories.includes(cat.id) ? `${cat.color}20` : 'rgba(24, 24, 31, 0.6)',
                boxShadow: selectedCategories.includes(cat.id) ? `0 0 20px ${cat.color}30` : 'none',
              }}
            >
              <span style={styles.cardEmoji}>{cat.emoji}</span>
              <span style={{
                ...styles.cardLabel,
                color: selectedCategories.includes(cat.id) ? '#fff' : '#A1A1AA',
              }}>{cat.label}</span>
              {selectedCategories.includes(cat.id) && (
                <span style={{...styles.checkmark, backgroundColor: cat.color}}>✓</span>
              )}
            </button>
          ))}
        </div>
      ),
    },
    {
      title: "Quel est votre budget ?",
      subtitle: "Vous pouvez en sélectionner plusieurs",
      content: (
        <div style={styles.optionsColumn}>
          {budgetOptions.map((opt) => (
            <button
              key={opt.id}
              onClick={() => toggleItem(opt.id, selectedBudgets, setSelectedBudgets)}
              style={{
                ...styles.optionRow,
                borderColor: selectedBudgets.includes(opt.id) ? '#A855F7' : 'rgba(255,255,255,0.1)',
                backgroundColor: selectedBudgets.includes(opt.id) ? 'rgba(168, 85, 247, 0.15)' : 'rgba(24, 24, 31, 0.6)',
              }}
            >
              <span style={styles.optionEmoji}>{opt.emoji}</span>
              <div style={styles.optionText}>
                <span style={{
                  ...styles.optionLabel,
                  color: selectedBudgets.includes(opt.id) ? '#fff' : '#E4E4E7',
                }}>{opt.label}</span>
                <span style={styles.optionDesc}>{opt.desc}</span>
              </div>
              {selectedBudgets.includes(opt.id) && (
                <span style={styles.optionCheck}>✓</span>
              )}
            </button>
          ))}
        </div>
      ),
    },
    {
      title: "Quand sortez-vous ?",
      subtitle: "Vos moments préférés",
      content: (
        <div style={styles.timeGrid}>
          {timeOptions.map((opt) => (
            <button
              key={opt.id}
              onClick={() => toggleItem(opt.id, selectedTimes, setSelectedTimes)}
              style={{
                ...styles.timeCard,
                borderColor: selectedTimes.includes(opt.id) ? '#6366F1' : 'rgba(255,255,255,0.1)',
                backgroundColor: selectedTimes.includes(opt.id) ? 'rgba(99, 102, 241, 0.15)' : 'rgba(24, 24, 31, 0.6)',
              }}
            >
              <span style={styles.timeEmoji}>{opt.emoji}</span>
              <span style={{
                ...styles.timeLabel,
                color: selectedTimes.includes(opt.id) ? '#fff' : '#E4E4E7',
              }}>{opt.label}</span>
              <span style={styles.timeDesc}>{opt.time}</span>
            </button>
          ))}
        </div>
      ),
    },
    {
      title: "Quelle ambiance ?",
      subtitle: "Le style qui vous correspond",
      content: (
        <div style={styles.vibeGrid}>
          {vibeOptions.map((opt) => (
            <button
              key={opt.id}
              onClick={() => toggleItem(opt.id, selectedVibes, setSelectedVibes)}
              style={{
                ...styles.vibeChip,
                borderColor: selectedVibes.includes(opt.id) ? '#EC4899' : 'rgba(255,255,255,0.1)',
                backgroundColor: selectedVibes.includes(opt.id) ? 'rgba(236, 72, 153, 0.15)' : 'rgba(24, 24, 31, 0.6)',
              }}
            >
              <span>{opt.emoji}</span>
              <span style={{
                color: selectedVibes.includes(opt.id) ? '#fff' : '#A1A1AA',
              }}>{opt.label}</span>
            </button>
          ))}
        </div>
      ),
    },
  ];

  if (isComplete) {
    return (
      <div style={styles.container}>
        <div style={styles.completeScreen}>
          <span style={styles.completeEmoji}>✨</span>
          <h2 style={styles.completeTitle}>Parfait !</h2>
          <p style={styles.completeText}>Vos recommandations sont prêtes</p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Progress bar */}
      <div style={styles.progressContainer}>
        {steps.map((_, i) => (
          <div
            key={i}
            style={{
              ...styles.progressDot,
              backgroundColor: i <= step ? '#A855F7' : 'rgba(255,255,255,0.2)',
            }}
          />
        ))}
      </div>

      {/* Content */}
      <div style={styles.content}>
        <h2 style={styles.title}>{steps[step].title}</h2>
        <p style={styles.subtitle}>{steps[step].subtitle}</p>
        
        <div style={styles.stepContent}>
          {steps[step].content}
        </div>
      </div>

      {/* Navigation */}
      <div style={styles.navigation}>
        {step > 0 && (
          <button onClick={() => setStep(step - 1)} style={styles.backButton}>
            ← Retour
          </button>
        )}
        
        <button
          onClick={() => step < steps.length - 1 ? setStep(step + 1) : handleComplete()}
          disabled={!canProceed()}
          style={{
            ...styles.nextButton,
            opacity: canProceed() ? 1 : 0.5,
          }}
        >
          {step < steps.length - 1 ? 'Continuer →' : 'C\'est parti ! 🚀'}
        </button>
      </div>

      {/* Skip */}
      <button
        onClick={() => {
          localStorage.setItem('artify_onboarding_complete', 'true');
          onComplete();
        }}
        style={styles.skipButton}
      >
        Passer pour l'instant
      </button>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px 20px',
    background: 'linear-gradient(180deg, #0A0A0F 0%, #12121A 100%)',
  },
  progressContainer: {
    display: 'flex',
    gap: '8px',
    marginBottom: '40px',
  },
  progressDot: {
    width: '40px',
    height: '4px',
    borderRadius: '2px',
    transition: 'background-color 0.3s ease',
  },
  content: {
    width: '100%',
    maxWidth: '480px',
    textAlign: 'center',
  },
  title: {
    fontSize: '28px',
    fontWeight: 700,
    color: '#fff',
    marginBottom: '8px',
  },
  subtitle: {
    fontSize: '15px',
    color: '#71717A',
    marginBottom: '32px',
  },
  stepContent: {
    marginBottom: '40px',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '12px',
  },
  card: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px 12px',
    border: '1px solid',
    borderRadius: '16px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    position: 'relative',
    backdropFilter: 'blur(10px)',
    gap: '8px',
  },
  cardEmoji: {
    fontSize: '28px',
  },
  cardLabel: {
    fontSize: '12px',
    fontWeight: 500,
    textAlign: 'center',
  },
  checkmark: {
    position: 'absolute',
    top: '8px',
    right: '8px',
    width: '18px',
    height: '18px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '10px',
    color: '#fff',
    fontWeight: 600,
  },
  optionsColumn: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  optionRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    padding: '18px 20px',
    border: '1px solid',
    borderRadius: '16px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    backdropFilter: 'blur(10px)',
    textAlign: 'left',
  },
  optionEmoji: {
    fontSize: '28px',
  },
  optionText: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  optionLabel: {
    fontSize: '16px',
    fontWeight: 500,
  },
  optionDesc: {
    fontSize: '13px',
    color: '#71717A',
  },
  optionCheck: {
    width: '24px',
    height: '24px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #A855F7, #EC4899)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '12px',
    color: '#fff',
    fontWeight: 600,
  },
  timeGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '12px',
  },
  timeCard: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '24px 16px',
    border: '1px solid',
    borderRadius: '16px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    backdropFilter: 'blur(10px)',
    gap: '8px',
  },
  timeEmoji: {
    fontSize: '32px',
  },
  timeLabel: {
    fontSize: '16px',
    fontWeight: 500,
  },
  timeDesc: {
    fontSize: '12px',
    color: '#71717A',
  },
  vibeGrid: {
    display: 'flex',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: '12px',
  },
  vibeChip: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '14px 20px',
    border: '1px solid',
    borderRadius: '30px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    backdropFilter: 'blur(10px)',
    fontSize: '15px',
  },
  navigation: {
    display: 'flex',
    gap: '12px',
    width: '100%',
    maxWidth: '480px',
    marginBottom: '20px',
  },
  backButton: {
    padding: '16px 24px',
    background: 'rgba(255,255,255,0.05)',
    color: '#A1A1AA',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '14px',
    fontSize: '15px',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  nextButton: {
    flex: 1,
    padding: '18px 28px',
    background: 'linear-gradient(135deg, #A855F7 0%, #EC4899 100%)',
    color: '#fff',
    border: 'none',
    borderRadius: '14px',
    fontSize: '16px',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    boxShadow: '0 8px 24px rgba(168, 85, 247, 0.4)',
  },
  skipButton: {
    padding: '12px',
    background: 'none',
    border: 'none',
    color: '#52525B',
    fontSize: '13px',
    cursor: 'pointer',
  },
  completeScreen: {
    textAlign: 'center',
  },
  completeEmoji: {
    fontSize: '64px',
    display: 'block',
    marginBottom: '16px',
    animation: 'pulse 1s ease-in-out infinite',
  },
  completeTitle: {
    fontSize: '32px',
    fontWeight: 700,
    color: '#fff',
    marginBottom: '8px',
  },
  completeText: {
    fontSize: '16px',
    color: '#A1A1AA',
  },
};


