/**
 * 🎭 Artify - Structure des catégories d'activités à Paris
 * Catégories principales et sous-catégories pour la découverte culturelle
 */

// ============================================================================
// TYPES PRINCIPAUX
// ============================================================================

export type MainCategory =
  | 'spectacles'
  | 'musique'
  | 'arts_visuels'
  | 'ateliers'
  | 'sport'
  | 'rencontres'
  | 'gastronomie'
  | 'culture'
  | 'nightlife';

export type SubCategory =
  // Spectacles
  | 'theatre_classique'
  | 'theatre_contemporain'
  | 'theatre_boulevard'
  | 'cafe_theatre'
  | 'opera'
  | 'ballet'
  | 'danse_contemporaine'
  | 'one_man_show'
  | 'stand_up'
  | 'impro'
  | 'cirque'
  | 'magie'
  // Musique
  | 'classique'
  | 'symphonique'
  | 'musique_chambre'
  | 'jazz'
  | 'blues'
  | 'pop'
  | 'rock'
  | 'rock_indie'
  | 'chanson_francaise'
  | 'folk'
  | 'techno'
  | 'house'
  | 'electro'
  | 'rap'
  | 'hip_hop'
  | 'afrobeat'
  | 'latino'
  | 'world_music'
  // Arts visuels
  | 'beaux_arts'
  | 'art_moderne'
  | 'art_contemporain'
  | 'photographie'
  | 'design'
  | 'architecture'
  | 'vernissage'
  | 'galerie'
  | 'art_numerique'
  | 'street_art'
  // Ateliers
  | 'dessin'
  | 'peinture'
  | 'sculpture'
  | 'ceramique'
  | 'poterie'
  | 'bijoux'
  | 'couture'
  | 'photo_workshop'
  | 'ecriture'
  | 'calligraphie'
  // Sport
  | 'football'
  | 'basketball'
  | 'running'
  | 'boxe'
  | 'arts_martiaux'
  | 'yoga'
  | 'pilates'
  | 'fitness'
  | 'danse'
  | 'escalade'
  | 'patinage'
  | 'escape_game'
  // Rencontres
  | 'club_lecture'
  | 'club_langues'
  | 'club_jeux'
  | 'afterwork'
  | 'speed_dating'
  | 'networking'
  | 'balade_urbaine'
  | 'randonnee'
  // Gastronomie
  | 'cours_cuisine'
  | 'patisserie'
  | 'degustation_vin'
  | 'degustation_fromage'
  | 'degustation_chocolat'
  | 'food_market'
  | 'brunch'
  | 'diner_insolite'
  // Culture
  | 'conference'
  | 'visite_guidee'
  | 'visite_insolite'
  | 'cinema_art_essai'
  | 'cineclub'
  | 'masterclass'
  // Nightlife
  | 'bar_cocktails'
  | 'speakeasy'
  | 'rooftop'
  | 'bar_vin'
  | 'club_techno'
  | 'club_mainstream'
  | 'club_latino';

export type Budget = 'gratuit' | '0-20' | '20-50' | '50-100' | '100+';
export type TimeOfDay = 'matin' | 'apres_midi' | 'soir' | 'nuit';
export type Ambiance = 'intime' | 'festif' | 'culturel' | 'sportif' | 'social' | 'creatif' | 'gastronomique';
export type Arrondissement = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20;

// ============================================================================
// INTERFACES
// ============================================================================

export interface CategoryInfo {
  id: MainCategory;
  label: string;
  emoji: string;
  color: string;
  description: string;
  subCategories: SubCategoryInfo[];
}

export interface SubCategoryInfo {
  id: SubCategory;
  label: string;
  emoji?: string;
  parentCategory: MainCategory;
}

export interface Event {
  id: string;
  title: string;
  slug: string;
  
  // Classification
  mainCategory: MainCategory;
  subCategory: SubCategory;
  tags: string[];
  
  // Timing
  date: string; // ISO date
  startTime: string; // HH:mm
  endTime?: string;
  timeOfDay: TimeOfDay;
  duration?: number; // en minutes
  
  // Location
  venue: string;
  address: string;
  arrondissement: Arrondissement;
  coordinates?: {
    lat: number;
    lng: number;
  };
  metro?: string[];
  
  // Pricing
  price: number;
  priceMax?: number;
  budget: Budget;
  bookingRequired: boolean;
  bookingUrl?: string;
  
  // Details
  description: string;
  shortDescription: string;
  ambiance: Ambiance[];
  
  // Media
  image?: string;
  images?: string[];
  
  // Source
  sourceUrl: string;
  sourceName: string;
  
  // Metadata
  createdAt: string;
  updatedAt: string;
  featured?: boolean;
  verified?: boolean;
}

export interface Venue {
  id: string;
  name: string;
  slug: string;
  address: string;
  arrondissement: Arrondissement;
  coordinates: {
    lat: number;
    lng: number;
  };
  metro: string[];
  website?: string;
  phone?: string;
  categories: MainCategory[];
  description?: string;
  image?: string;
  capacity?: number;
  rating?: number;
}

// ============================================================================
// DONNÉES DES CATÉGORIES
// ============================================================================

export const mainCategories: CategoryInfo[] = [
  {
    id: 'spectacles',
    label: 'Spectacles',
    emoji: '🎭',
    color: '#E53935',
    description: 'Théâtre, opéra, danse, humour et cirque',
    subCategories: [
      { id: 'theatre_classique', label: 'Théâtre classique', parentCategory: 'spectacles' },
      { id: 'theatre_contemporain', label: 'Théâtre contemporain', parentCategory: 'spectacles' },
      { id: 'theatre_boulevard', label: 'Théâtre de boulevard', parentCategory: 'spectacles' },
      { id: 'cafe_theatre', label: 'Café-théâtre', parentCategory: 'spectacles' },
      { id: 'opera', label: 'Opéra', emoji: '🎤', parentCategory: 'spectacles' },
      { id: 'ballet', label: 'Ballet', emoji: '🩰', parentCategory: 'spectacles' },
      { id: 'danse_contemporaine', label: 'Danse contemporaine', parentCategory: 'spectacles' },
      { id: 'one_man_show', label: 'One man/woman show', emoji: '🎤', parentCategory: 'spectacles' },
      { id: 'stand_up', label: 'Stand-up', emoji: '😂', parentCategory: 'spectacles' },
      { id: 'impro', label: 'Improvisation', parentCategory: 'spectacles' },
      { id: 'cirque', label: 'Cirque', emoji: '🎪', parentCategory: 'spectacles' },
      { id: 'magie', label: 'Magie', emoji: '🪄', parentCategory: 'spectacles' },
    ],
  },
  {
    id: 'musique',
    label: 'Musique',
    emoji: '🎵',
    color: '#8E24AA',
    description: 'Concerts, festivals et performances live',
    subCategories: [
      { id: 'classique', label: 'Classique', emoji: '🎻', parentCategory: 'musique' },
      { id: 'symphonique', label: 'Symphonique', parentCategory: 'musique' },
      { id: 'musique_chambre', label: 'Musique de chambre', parentCategory: 'musique' },
      { id: 'jazz', label: 'Jazz', emoji: '🎷', parentCategory: 'musique' },
      { id: 'blues', label: 'Blues', parentCategory: 'musique' },
      { id: 'pop', label: 'Pop', emoji: '🎤', parentCategory: 'musique' },
      { id: 'rock', label: 'Rock', emoji: '🎸', parentCategory: 'musique' },
      { id: 'rock_indie', label: 'Rock indé', parentCategory: 'musique' },
      { id: 'chanson_francaise', label: 'Chanson française', parentCategory: 'musique' },
      { id: 'folk', label: 'Folk/Acoustique', parentCategory: 'musique' },
      { id: 'techno', label: 'Techno', emoji: '🎧', parentCategory: 'musique' },
      { id: 'house', label: 'House', parentCategory: 'musique' },
      { id: 'electro', label: 'Électro', parentCategory: 'musique' },
      { id: 'rap', label: 'Rap', emoji: '🎤', parentCategory: 'musique' },
      { id: 'hip_hop', label: 'Hip-hop', parentCategory: 'musique' },
      { id: 'afrobeat', label: 'Afrobeat', emoji: '🌍', parentCategory: 'musique' },
      { id: 'latino', label: 'Latino', emoji: '💃', parentCategory: 'musique' },
      { id: 'world_music', label: 'Musiques du monde', parentCategory: 'musique' },
    ],
  },
  {
    id: 'arts_visuels',
    label: 'Arts visuels',
    emoji: '🎨',
    color: '#FB8C00',
    description: 'Expositions, galeries et vernissages',
    subCategories: [
      { id: 'beaux_arts', label: 'Beaux-arts classiques', parentCategory: 'arts_visuels' },
      { id: 'art_moderne', label: 'Art moderne', parentCategory: 'arts_visuels' },
      { id: 'art_contemporain', label: 'Art contemporain', parentCategory: 'arts_visuels' },
      { id: 'photographie', label: 'Photographie', emoji: '📷', parentCategory: 'arts_visuels' },
      { id: 'design', label: 'Design', parentCategory: 'arts_visuels' },
      { id: 'architecture', label: 'Architecture', parentCategory: 'arts_visuels' },
      { id: 'vernissage', label: 'Vernissage', emoji: '🥂', parentCategory: 'arts_visuels' },
      { id: 'galerie', label: 'Galerie', parentCategory: 'arts_visuels' },
      { id: 'art_numerique', label: 'Art numérique/immersif', emoji: '✨', parentCategory: 'arts_visuels' },
      { id: 'street_art', label: 'Street art', emoji: '🖌️', parentCategory: 'arts_visuels' },
    ],
  },
  {
    id: 'ateliers',
    label: 'Ateliers créatifs',
    emoji: '🖌️',
    color: '#43A047',
    description: 'Cours et ateliers artistiques',
    subCategories: [
      { id: 'dessin', label: 'Dessin', emoji: '✏️', parentCategory: 'ateliers' },
      { id: 'peinture', label: 'Peinture', emoji: '🎨', parentCategory: 'ateliers' },
      { id: 'sculpture', label: 'Sculpture', parentCategory: 'ateliers' },
      { id: 'ceramique', label: 'Céramique', emoji: '🏺', parentCategory: 'ateliers' },
      { id: 'poterie', label: 'Poterie', parentCategory: 'ateliers' },
      { id: 'bijoux', label: 'Création de bijoux', emoji: '💍', parentCategory: 'ateliers' },
      { id: 'couture', label: 'Couture', emoji: '🧵', parentCategory: 'ateliers' },
      { id: 'photo_workshop', label: 'Atelier photo', emoji: '📸', parentCategory: 'ateliers' },
      { id: 'ecriture', label: 'Écriture créative', emoji: '📝', parentCategory: 'ateliers' },
      { id: 'calligraphie', label: 'Calligraphie', parentCategory: 'ateliers' },
    ],
  },
  {
    id: 'sport',
    label: 'Sport & Bien-être',
    emoji: '🏃',
    color: '#00ACC1',
    description: 'Activités sportives et wellness',
    subCategories: [
      { id: 'football', label: 'Football', emoji: '⚽', parentCategory: 'sport' },
      { id: 'basketball', label: 'Basketball', emoji: '🏀', parentCategory: 'sport' },
      { id: 'running', label: 'Running', emoji: '🏃', parentCategory: 'sport' },
      { id: 'boxe', label: 'Boxe', emoji: '🥊', parentCategory: 'sport' },
      { id: 'arts_martiaux', label: 'Arts martiaux', emoji: '🥋', parentCategory: 'sport' },
      { id: 'yoga', label: 'Yoga', emoji: '🧘', parentCategory: 'sport' },
      { id: 'pilates', label: 'Pilates', parentCategory: 'sport' },
      { id: 'fitness', label: 'Fitness', emoji: '💪', parentCategory: 'sport' },
      { id: 'danse', label: 'Danse', emoji: '💃', parentCategory: 'sport' },
      { id: 'escalade', label: 'Escalade', emoji: '🧗', parentCategory: 'sport' },
      { id: 'patinage', label: 'Patinage', emoji: '⛸️', parentCategory: 'sport' },
      { id: 'escape_game', label: 'Escape game', emoji: '🔐', parentCategory: 'sport' },
    ],
  },
  {
    id: 'rencontres',
    label: 'Rencontres',
    emoji: '👥',
    color: '#5E35B1',
    description: 'Meetups, clubs et événements sociaux',
    subCategories: [
      { id: 'club_lecture', label: 'Club de lecture', emoji: '📚', parentCategory: 'rencontres' },
      { id: 'club_langues', label: 'Échange linguistique', emoji: '🗣️', parentCategory: 'rencontres' },
      { id: 'club_jeux', label: 'Jeux de société', emoji: '🎲', parentCategory: 'rencontres' },
      { id: 'afterwork', label: 'Afterwork', emoji: '🍻', parentCategory: 'rencontres' },
      { id: 'speed_dating', label: 'Speed dating', emoji: '💕', parentCategory: 'rencontres' },
      { id: 'networking', label: 'Networking', emoji: '🤝', parentCategory: 'rencontres' },
      { id: 'balade_urbaine', label: 'Balade urbaine', emoji: '🚶', parentCategory: 'rencontres' },
      { id: 'randonnee', label: 'Randonnée', emoji: '🥾', parentCategory: 'rencontres' },
    ],
  },
  {
    id: 'gastronomie',
    label: 'Gastronomie',
    emoji: '🍷',
    color: '#D81B60',
    description: 'Cours de cuisine, dégustations et expériences culinaires',
    subCategories: [
      { id: 'cours_cuisine', label: 'Cours de cuisine', emoji: '👨‍🍳', parentCategory: 'gastronomie' },
      { id: 'patisserie', label: 'Pâtisserie', emoji: '🧁', parentCategory: 'gastronomie' },
      { id: 'degustation_vin', label: 'Dégustation de vin', emoji: '🍷', parentCategory: 'gastronomie' },
      { id: 'degustation_fromage', label: 'Dégustation de fromage', emoji: '🧀', parentCategory: 'gastronomie' },
      { id: 'degustation_chocolat', label: 'Dégustation de chocolat', emoji: '🍫', parentCategory: 'gastronomie' },
      { id: 'food_market', label: 'Food market', emoji: '🍔', parentCategory: 'gastronomie' },
      { id: 'brunch', label: 'Brunch', emoji: '🥐', parentCategory: 'gastronomie' },
      { id: 'diner_insolite', label: 'Dîner insolite', emoji: '✨', parentCategory: 'gastronomie' },
    ],
  },
  {
    id: 'culture',
    label: 'Culture & Savoir',
    emoji: '📚',
    color: '#1E88E5',
    description: 'Conférences, visites guidées et cinéma',
    subCategories: [
      { id: 'conference', label: 'Conférence', emoji: '🎓', parentCategory: 'culture' },
      { id: 'visite_guidee', label: 'Visite guidée', emoji: '🗺️', parentCategory: 'culture' },
      { id: 'visite_insolite', label: 'Visite insolite', emoji: '🔦', parentCategory: 'culture' },
      { id: 'cinema_art_essai', label: 'Cinéma art et essai', emoji: '🎬', parentCategory: 'culture' },
      { id: 'cineclub', label: 'Ciné-club', parentCategory: 'culture' },
      { id: 'masterclass', label: 'Masterclass', emoji: '🎯', parentCategory: 'culture' },
    ],
  },
  {
    id: 'nightlife',
    label: 'Vie nocturne',
    emoji: '🌙',
    color: '#3949AB',
    description: 'Bars, clubs et soirées',
    subCategories: [
      { id: 'bar_cocktails', label: 'Bar à cocktails', emoji: '🍸', parentCategory: 'nightlife' },
      { id: 'speakeasy', label: 'Speakeasy', emoji: '🚪', parentCategory: 'nightlife' },
      { id: 'rooftop', label: 'Rooftop', emoji: '🌆', parentCategory: 'nightlife' },
      { id: 'bar_vin', label: 'Bar à vin', emoji: '🍷', parentCategory: 'nightlife' },
      { id: 'club_techno', label: 'Club techno', emoji: '🎧', parentCategory: 'nightlife' },
      { id: 'club_mainstream', label: 'Club mainstream', emoji: '🎉', parentCategory: 'nightlife' },
      { id: 'club_latino', label: 'Club latino', emoji: '💃', parentCategory: 'nightlife' },
    ],
  },
];

// ============================================================================
// HELPERS
// ============================================================================

export function getCategoryById(id: MainCategory): CategoryInfo | undefined {
  return mainCategories.find(cat => cat.id === id);
}

export function getSubCategoryById(id: SubCategory): SubCategoryInfo | undefined {
  for (const cat of mainCategories) {
    const sub = cat.subCategories.find(s => s.id === id);
    if (sub) return sub;
  }
  return undefined;
}

export function getBudgetLabel(budget: Budget): string {
  const labels: Record<Budget, string> = {
    gratuit: 'Gratuit',
    '0-20': '0-20€',
    '20-50': '20-50€',
    '50-100': '50-100€',
    '100+': '100€+',
  };
  return labels[budget];
}

export function getTimeOfDayLabel(time: TimeOfDay): string {
  const labels: Record<TimeOfDay, string> = {
    matin: 'Matin (8h-12h)',
    apres_midi: 'Après-midi (12h-18h)',
    soir: 'Soirée (18h-23h)',
    nuit: 'Nuit (23h+)',
  };
  return labels[time];
}

export function priceTobudget(price: number): Budget {
  if (price === 0) return 'gratuit';
  if (price <= 20) return '0-20';
  if (price <= 50) return '20-50';
  if (price <= 100) return '50-100';
  return '100+';
}

// ============================================================================
// LIEUX EMBLÉMATIQUES
// ============================================================================

export const parisVenues: Record<MainCategory, string[]> = {
  spectacles: [
    'Opéra Bastille',
    'Palais Garnier',
    'Comédie-Française',
    'Théâtre de la Ville',
    'Théâtre du Châtelet',
    'Théâtre de Chaillot',
    'Odéon-Théâtre de l\'Europe',
    'Point Virgule',
    'Comedy Club',
    'Cirque d\'Hiver',
    'Théâtre Mogador',
  ],
  musique: [
    'Philharmonie de Paris',
    'Accor Arena',
    'Stade de France',
    'Olympia',
    'Bataclan',
    'Zénith',
    'Sunset-Sunside',
    'New Morning',
    'Rex Club',
    'Trabendo',
    'La Cigale',
    'Café de la Danse',
  ],
  arts_visuels: [
    'Musée du Louvre',
    'Musée d\'Orsay',
    'Centre Pompidou',
    'Fondation Louis Vuitton',
    'Palais de Tokyo',
    'Grand Palais',
    'Musée Rodin',
    'Maison Européenne de la Photographie',
    'Atelier des Lumières',
    'Jeu de Paume',
  ],
  ateliers: [
    'Beaux-Arts de Paris',
    'Ateliers de Montmartre',
    'Artmandu',
    'Clementine Studio',
    'L\'Atelier du Bracelet Parisien',
    'Make My Lemonade',
  ],
  sport: [
    'Parc des Princes',
    'Stade de France',
    'Arkose',
    'Climb Up',
    'Forest Hill',
    'CMG Sports Club',
  ],
  rencontres: [
    'Shakespeare & Company',
    'Ground Control',
    'Station F',
    'La Felicità',
    'Café des Psys',
  ],
  gastronomie: [
    'Atelier des Chefs',
    'Ferrandi',
    'Le Cordon Bleu',
    'Ladurée',
    'O Château',
    'Laurent Dubois',
  ],
  culture: [
    'Cinémathèque Française',
    'Forum des Images',
    'Cité des Sciences',
    'Palais de la Découverte',
    'BnF François Mitterrand',
    'Institut du Monde Arabe',
  ],
  nightlife: [
    'Rex Club',
    'Concrete',
    'Badaboum',
    'Silencio',
    'Queen',
    'Le Perchoir',
    'Experimental Cocktail Club',
    'Little Red Door',
  ],
};

// ============================================================================
// ARRONDISSEMENTS
// ============================================================================

export const arrondissements: { id: Arrondissement; name: string; character: string }[] = [
  { id: 1, name: '1er - Louvre', character: 'Monumental et touristique' },
  { id: 2, name: '2ème - Bourse', character: 'Passages couverts et vie nocturne' },
  { id: 3, name: '3ème - Temple', character: 'Marais historique et galeries' },
  { id: 4, name: '4ème - Hôtel-de-Ville', character: 'Notre-Dame et le Marais' },
  { id: 5, name: '5ème - Panthéon', character: 'Quartier Latin et universités' },
  { id: 6, name: '6ème - Luxembourg', character: 'Saint-Germain et librairies' },
  { id: 7, name: '7ème - Palais-Bourbon', character: 'Tour Eiffel et musées' },
  { id: 8, name: '8ème - Élysée', character: 'Champs-Élysées et luxe' },
  { id: 9, name: '9ème - Opéra', character: 'Grands magasins et opéra' },
  { id: 10, name: '10ème - Entrepôt', character: 'Canal Saint-Martin et hipster' },
  { id: 11, name: '11ème - Popincourt', character: 'Vie nocturne et Bastille' },
  { id: 12, name: '12ème - Reuilly', character: 'Bercy et promenades' },
  { id: 13, name: '13ème - Gobelins', character: 'Chinatown et street art' },
  { id: 14, name: '14ème - Observatoire', character: 'Montparnasse artistique' },
  { id: 15, name: '15ème - Vaugirard', character: 'Résidentiel et familial' },
  { id: 16, name: '16ème - Passy', character: 'Bourgeois et musées' },
  { id: 17, name: '17ème - Batignolles', character: 'Village et tendance' },
  { id: 18, name: '18ème - Butte-Montmartre', character: 'Sacré-Cœur et artistes' },
  { id: 19, name: '19ème - Buttes-Chaumont', character: 'La Villette et culture' },
  { id: 20, name: '20ème - Ménilmontant', character: 'Populaire et multiculturel' },
];


