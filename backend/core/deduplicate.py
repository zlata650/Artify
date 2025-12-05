"""
🎭 Artify - Event Deduplication
Detects and merges duplicate events using fuzzy matching
"""

import re
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
import unicodedata

# Try to import rapidfuzz, fall back to basic matching
try:
    from rapidfuzz import fuzz, process
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False


@dataclass
class DuplicateMatch:
    """Represents a detected duplicate pair."""
    canonical_id: str
    duplicate_id: str
    similarity_score: float
    match_reason: str


class EventDeduplicator:
    """
    Detects and handles duplicate events.
    
    Two events are considered duplicates if:
    - Titles are similar (fuzzy match > threshold)
    - Date is the same
    - Location is similar
    """
    
    def __init__(
        self, 
        title_threshold: float = 85.0,
        location_threshold: float = 75.0
    ):
        """
        Initialize the deduplicator.
        
        Args:
            title_threshold: Minimum similarity score for titles (0-100)
            location_threshold: Minimum similarity score for locations (0-100)
        """
        self.title_threshold = title_threshold
        self.location_threshold = location_threshold
    
    def normalize_for_comparison(self, text: str) -> str:
        """Normalize text for comparison."""
        if not text:
            return ""
        
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        # Remove accents
        text = ''.join(c for c in text if not unicodedata.combining(c))
        
        # Lowercase
        text = text.lower()
        
        # Remove common words that don't help differentiate
        stopwords = [
            'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'the', 'a', 'an',
            'et', 'and', 'à', 'au', 'aux', 'en', 'dans', 'sur', 'par', 'pour',
            'concert', 'spectacle', 'exposition', 'atelier', 'soirée', 'soiree',
            'paris', 'france',
        ]
        
        words = text.split()
        words = [w for w in words if w not in stopwords]
        text = ' '.join(words)
        
        # Remove special characters
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two strings."""
        norm1 = self.normalize_for_comparison(text1)
        norm2 = self.normalize_for_comparison(text2)
        
        if not norm1 or not norm2:
            return 0.0
        
        if HAS_RAPIDFUZZ:
            # Use multiple fuzzy matching strategies
            ratio = fuzz.ratio(norm1, norm2)
            partial = fuzz.partial_ratio(norm1, norm2)
            token_sort = fuzz.token_sort_ratio(norm1, norm2)
            token_set = fuzz.token_set_ratio(norm1, norm2)
            
            # Weighted average
            return (ratio * 0.2 + partial * 0.3 + token_sort * 0.2 + token_set * 0.3)
        else:
            # Basic similarity using set intersection
            words1 = set(norm1.split())
            words2 = set(norm2.split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1 & words2
            union = words1 | words2
            
            return (len(intersection) / len(union)) * 100
    
    def are_duplicates(self, event1: Dict, event2: Dict) -> Tuple[bool, float, str]:
        """
        Check if two events are duplicates.
        
        Args:
            event1, event2: Event dictionaries with title, date_start, location_name
            
        Returns:
            Tuple of (is_duplicate, similarity_score, reason)
        """
        # Must have same date
        date1 = event1.get('date_start') or event1.get('date')
        date2 = event2.get('date_start') or event2.get('date')
        
        if date1 != date2:
            return False, 0.0, ""
        
        # Check title similarity
        title1 = event1.get('title', '')
        title2 = event2.get('title', '')
        title_similarity = self.calculate_similarity(title1, title2)
        
        if title_similarity < self.title_threshold:
            return False, title_similarity, ""
        
        # Check location similarity
        loc1 = event1.get('location_name') or event1.get('venue', '')
        loc2 = event2.get('location_name') or event2.get('venue', '')
        
        # If both have locations, check similarity
        if loc1 and loc2:
            loc_similarity = self.calculate_similarity(loc1, loc2)
            if loc_similarity < self.location_threshold:
                return False, title_similarity, ""
        
        # Check address as additional signal
        addr1 = event1.get('address', '')
        addr2 = event2.get('address', '')
        
        if addr1 and addr2:
            addr_similarity = self.calculate_similarity(addr1, addr2)
            # High address similarity is a strong signal
            if addr_similarity > 80:
                return True, max(title_similarity, addr_similarity), f"title:{title_similarity:.0f}%, address:{addr_similarity:.0f}%"
        
        return True, title_similarity, f"title:{title_similarity:.0f}%"
    
    def find_duplicates(self, events: List[Dict]) -> List[DuplicateMatch]:
        """
        Find all duplicates in a list of events.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            List of DuplicateMatch objects
        """
        duplicates = []
        seen_pairs: Set[Tuple[str, str]] = set()
        
        # Group events by date for efficiency
        by_date: Dict[str, List[Dict]] = {}
        for event in events:
            date = event.get('date_start') or event.get('date', '')
            if date:
                if date not in by_date:
                    by_date[date] = []
                by_date[date].append(event)
        
        # Compare within each date group
        for date, date_events in by_date.items():
            for i, event1 in enumerate(date_events):
                for event2 in date_events[i+1:]:
                    id1 = event1.get('id', str(i))
                    id2 = event2.get('id', str(i + 1))
                    
                    # Skip if already compared
                    pair = tuple(sorted([id1, id2]))
                    if pair in seen_pairs:
                        continue
                    seen_pairs.add(pair)
                    
                    is_dup, score, reason = self.are_duplicates(event1, event2)
                    
                    if is_dup:
                        # Determine canonical (prefer one with more data)
                        canonical, duplicate = self._choose_canonical(event1, event2)
                        
                        duplicates.append(DuplicateMatch(
                            canonical_id=canonical.get('id', ''),
                            duplicate_id=duplicate.get('id', ''),
                            similarity_score=score,
                            match_reason=reason
                        ))
        
        return duplicates
    
    def _choose_canonical(self, event1: Dict, event2: Dict) -> Tuple[Dict, Dict]:
        """
        Choose which event should be canonical and which is duplicate.
        Prefers event with more complete data.
        """
        def score_completeness(event: Dict) -> int:
            score = 0
            # Prefer events with ticket URLs
            if event.get('ticket_url') and event.get('has_direct_ticket_button'):
                score += 10
            elif event.get('ticket_url'):
                score += 5
            
            # Prefer events with images
            if event.get('image_url'):
                score += 3
            
            # Prefer events with longer descriptions
            desc = event.get('description', '')
            if len(desc) > 200:
                score += 3
            elif len(desc) > 50:
                score += 1
            
            # Prefer events with price info
            if event.get('price_from') or event.get('price'):
                score += 2
            
            # Prefer events from certain sources
            trusted_sources = ['philharmonie', 'opera', 'louvre', 'orsay', 'pompidou']
            source = event.get('source_name', '').lower()
            if any(s in source for s in trusted_sources):
                score += 5
            
            return score
        
        score1 = score_completeness(event1)
        score2 = score_completeness(event2)
        
        if score1 >= score2:
            return event1, event2
        else:
            return event2, event1
    
    def merge_events(self, canonical: Dict, duplicate: Dict) -> Dict:
        """
        Merge two events, keeping best data from each.
        
        Args:
            canonical: The primary event to keep
            duplicate: The event to merge from
            
        Returns:
            Merged event dictionary
        """
        merged = canonical.copy()
        
        # Fill in missing fields from duplicate
        fields_to_merge = [
            'description', 'image_url', 'ticket_url', 'address',
            'arrondissement', 'latitude', 'longitude', 'price_from',
            'price_to', 'time_start', 'time_end', 'organizer_name'
        ]
        
        for field in fields_to_merge:
            if not merged.get(field) and duplicate.get(field):
                merged[field] = duplicate[field]
        
        # Prefer ticket_url with direct button
        if duplicate.get('has_direct_ticket_button') and duplicate.get('ticket_url'):
            if not merged.get('has_direct_ticket_button'):
                merged['ticket_url'] = duplicate['ticket_url']
                merged['has_direct_ticket_button'] = True
        
        # Merge tags
        merged_tags = set(merged.get('tags', []) or [])
        dup_tags = set(duplicate.get('tags', []) or [])
        merged['tags'] = list(merged_tags | dup_tags)
        
        # Use longer description
        if len(duplicate.get('description', '')) > len(merged.get('description', '')):
            merged['description'] = duplicate['description']
        
        return merged
    
    def deduplicate_events(self, events: List[Dict]) -> Tuple[List[Dict], List[DuplicateMatch]]:
        """
        Remove duplicates from a list of events.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Tuple of (deduplicated_events, detected_duplicates)
        """
        # Find all duplicates
        duplicates = self.find_duplicates(events)
        
        # Build mapping of duplicate IDs to canonical IDs
        duplicate_ids: Set[str] = set()
        merge_map: Dict[str, str] = {}  # duplicate_id -> canonical_id
        
        for match in duplicates:
            duplicate_ids.add(match.duplicate_id)
            merge_map[match.duplicate_id] = match.canonical_id
        
        # Build id -> event mapping
        events_by_id = {e.get('id', str(i)): e for i, e in enumerate(events)}
        
        # Merge and filter
        result = []
        merged_canonical: Set[str] = set()
        
        for event in events:
            event_id = event.get('id', '')
            
            # Skip duplicates
            if event_id in duplicate_ids:
                continue
            
            # If this is a canonical event, merge with its duplicates
            if event_id not in merged_canonical:
                merged_event = event.copy()
                
                # Find all duplicates of this event and merge
                for match in duplicates:
                    if match.canonical_id == event_id:
                        dup = events_by_id.get(match.duplicate_id)
                        if dup:
                            merged_event = self.merge_events(merged_event, dup)
                
                result.append(merged_event)
                merged_canonical.add(event_id)
        
        return result, duplicates


# Quick helper function
def deduplicate_events(events: List[Dict]) -> List[Dict]:
    """Quick deduplication returning just the deduplicated list."""
    deduplicator = EventDeduplicator()
    result, _ = deduplicator.deduplicate_events(events)
    return result

