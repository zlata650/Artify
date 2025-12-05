#!/usr/bin/env python3
"""
🎭 Artify - Main Event Ingestion Pipeline
Scrapes events from all sources, normalizes, deduplicates, and saves to database.

Usage:
    python -m backend.ingest               # Run full ingestion
    python -m backend.ingest --source eventbrite  # Run specific source
    python -m backend.ingest --dry-run    # Test without saving
"""

import argparse
import sys
import time
import logging
from datetime import datetime
from typing import List, Optional, Dict

# Add parent directory to path for imports
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.db import EventsDB
from backend.core.models import UnifiedEvent
from backend.core.deduplicate import EventDeduplicator
from backend.core.categorizer import EventCategorizer
from backend.core.ticket_extractor import TicketExtractor

# Import scrapers
from backend.scrapers.aggregators.eventbrite import EventbriteScraper
from backend.scrapers.aggregators.sortiraparis import SortirAParisScraper
from backend.scrapers.venues.philharmonie import PhilharmonieScraper
from backend.scrapers.venues.opera_paris import OperaParisScraper
from backend.scrapers.museums.louvre import LouvreScraper
from backend.scrapers.museums.orsay import OrsayScraper
from backend.scrapers.museums.pompidou import PompidouScraper
from backend.scrapers.galleries.generic_gallery import GenericGalleryScraper, PARIS_GALLERIES
from backend.scrapers.workshops.generic_workshop import GenericWorkshopScraper, PARIS_WORKSHOPS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Scraper registry - maps source names to scraper classes
SCRAPERS = {
    # Aggregators
    'eventbrite': EventbriteScraper,
    'sortiraparis': SortirAParisScraper,
    
    # Venues
    'philharmonie': PhilharmonieScraper,
    'opera_paris': OperaParisScraper,
    
    # Museums
    'louvre': LouvreScraper,
    'orsay': OrsayScraper,
    'pompidou': PompidouScraper,
}

# Source groups for selective scraping
SOURCE_GROUPS = {
    'aggregators': ['eventbrite', 'sortiraparis'],
    'venues': ['philharmonie', 'opera_paris'],
    'museums': ['louvre', 'orsay', 'pompidou'],
    'galleries': 'galleries',  # Special handling
    'workshops': 'workshops',  # Special handling
    'all': None,  # Run everything
}


class IngestionPipeline:
    """
    Main ingestion pipeline that coordinates scraping, processing, and storage.
    """
    
    def __init__(
        self,
        db_path: str = 'real_events.db',
        extract_tickets: bool = True,
        deduplicate: bool = True,
        dry_run: bool = False
    ):
        """
        Initialize the pipeline.
        
        Args:
            db_path: Path to SQLite database
            extract_tickets: Whether to extract ticket URLs
            deduplicate: Whether to run deduplication
            dry_run: If True, don't save to database
        """
        self.db = EventsDB(db_path)
        self.deduplicator = EventDeduplicator()
        self.categorizer = EventCategorizer()
        self.extract_tickets = extract_tickets
        self.deduplicate = deduplicate
        self.dry_run = dry_run
        
        # Statistics
        self.stats = {
            'sources_processed': 0,
            'events_scraped': 0,
            'events_added': 0,
            'events_updated': 0,
            'events_deduplicated': 0,
            'errors': [],
        }
    
    def run(self, sources: Optional[List[str]] = None):
        """
        Run the ingestion pipeline.
        
        Args:
            sources: List of source names to process, or None for all
        """
        start_time = time.time()
        logger.info("🚀 Starting ingestion pipeline")
        
        all_events = []
        
        # Determine which sources to scrape
        if sources:
            source_list = []
            for s in sources:
                if s in SOURCE_GROUPS:
                    group = SOURCE_GROUPS[s]
                    if group is None:  # 'all'
                        source_list = list(SCRAPERS.keys()) + ['galleries', 'workshops']
                        break
                    elif isinstance(group, list):
                        source_list.extend(group)
                    else:
                        source_list.append(group)
                else:
                    source_list.append(s)
        else:
            source_list = list(SCRAPERS.keys()) + ['galleries', 'workshops']
        
        # Scrape each source
        for source in source_list:
            try:
                events = self._scrape_source(source)
                all_events.extend(events)
                self.stats['sources_processed'] += 1
            except Exception as e:
                logger.error(f"❌ Failed to scrape {source}: {e}")
                self.stats['errors'].append({'source': source, 'error': str(e)})
        
        self.stats['events_scraped'] = len(all_events)
        logger.info(f"📊 Scraped {len(all_events)} events from {self.stats['sources_processed']} sources")
        
        # Extract ticket URLs if enabled
        if self.extract_tickets and all_events:
            all_events = self._extract_ticket_urls(all_events)
        
        # Deduplicate if enabled
        if self.deduplicate and all_events:
            all_events, duplicates = self.deduplicator.deduplicate_events(
                [e.to_dict() for e in all_events]
            )
            self.stats['events_deduplicated'] = len(duplicates)
            logger.info(f"🔄 Deduplicated: {len(duplicates)} duplicates removed")
            
            # Convert back to UnifiedEvent objects
            all_events = [UnifiedEvent.from_dict(e) for e in all_events]
        
        # Save to database
        if not self.dry_run and all_events:
            result = self.db.upsert_batch(all_events)
            self.stats['events_added'] = result['added']
            self.stats['events_updated'] = result['updated']
            logger.info(f"💾 Saved: {result['added']} added, {result['updated']} updated")
        elif self.dry_run:
            logger.info(f"🔍 Dry run: would save {len(all_events)} events")
        
        # Clean up old events
        if not self.dry_run:
            deleted = self.db.delete_past_events(days_before_today=1)
            if deleted > 0:
                logger.info(f"🗑️ Cleaned up {deleted} past events")
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Pipeline completed in {elapsed:.1f}s")
        
        # Log stats to database
        self._log_run()
        
        return self.stats
    
    def _scrape_source(self, source: str) -> List[UnifiedEvent]:
        """Scrape a single source."""
        logger.info(f"🔍 Scraping {source}...")
        
        if source == 'galleries':
            return self._scrape_galleries()
        elif source == 'workshops':
            return self._scrape_workshops()
        elif source in SCRAPERS:
            scraper_class = SCRAPERS[source]
            with scraper_class(max_events=100) as scraper:
                return scraper.scrape_all()
        else:
            logger.warning(f"Unknown source: {source}")
            return []
    
    def _scrape_galleries(self) -> List[UnifiedEvent]:
        """Scrape all galleries."""
        all_events = []
        
        for gallery in PARIS_GALLERIES:
            try:
                with GenericGalleryScraper(gallery_config=gallery, max_events=30) as scraper:
                    events = scraper.scrape_all()
                    all_events.extend(events)
            except Exception as e:
                logger.warning(f"Failed to scrape gallery {gallery['name']}: {e}")
        
        return all_events
    
    def _scrape_workshops(self) -> List[UnifiedEvent]:
        """Scrape all workshops."""
        all_events = []
        
        for workshop in PARIS_WORKSHOPS:
            try:
                with GenericWorkshopScraper(workshop_config=workshop, max_events=30) as scraper:
                    events = scraper.scrape_all()
                    all_events.extend(events)
            except Exception as e:
                logger.warning(f"Failed to scrape workshop {workshop['name']}: {e}")
        
        return all_events
    
    def _extract_ticket_urls(self, events: List[UnifiedEvent]) -> List[UnifiedEvent]:
        """Extract ticket URLs for events that don't have them."""
        logger.info("🎫 Extracting ticket URLs...")
        
        try:
            with TicketExtractor(use_playwright=True) as extractor:
                for event in events:
                    # Skip if already has a valid ticket URL different from source
                    if event.has_direct_ticket_button and event.ticket_url != event.source_event_url:
                        continue
                    
                    try:
                        ticket_url, has_direct = extractor.extract_ticket_url(event.source_event_url)
                        if ticket_url:
                            event.ticket_url = ticket_url
                            event.has_direct_ticket_button = has_direct
                    except Exception as e:
                        logger.debug(f"Could not extract ticket for {event.title}: {e}")
        except Exception as e:
            logger.warning(f"Ticket extraction failed: {e}")
        
        return events
    
    def _log_run(self):
        """Log the run statistics to database."""
        for source in self.stats.get('sources', []):
            self.db.log_scrape(
                source_name=source,
                events_found=self.stats['events_scraped'],
                events_added=self.stats['events_added'],
                events_updated=self.stats['events_updated'],
                events_deduplicated=self.stats['events_deduplicated'],
                success=len(self.stats['errors']) == 0,
            )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Artify Event Ingestion Pipeline')
    parser.add_argument(
        '--source', '-s',
        type=str,
        nargs='+',
        help='Specific sources to scrape (eventbrite, philharmonie, louvre, etc.)'
    )
    parser.add_argument(
        '--group', '-g',
        type=str,
        choices=list(SOURCE_GROUPS.keys()),
        help='Source group to scrape (aggregators, venues, museums, galleries, workshops, all)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test run without saving to database'
    )
    parser.add_argument(
        '--no-tickets',
        action='store_true',
        help='Skip ticket URL extraction'
    )
    parser.add_argument(
        '--no-dedupe',
        action='store_true',
        help='Skip deduplication'
    )
    parser.add_argument(
        '--db',
        type=str,
        default='real_events.db',
        help='Path to database file'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine sources
    sources = args.source
    if args.group:
        sources = [args.group]
    
    # Run pipeline
    pipeline = IngestionPipeline(
        db_path=args.db,
        extract_tickets=not args.no_tickets,
        deduplicate=not args.no_dedupe,
        dry_run=args.dry_run,
    )
    
    stats = pipeline.run(sources)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 INGESTION SUMMARY")
    print("=" * 50)
    print(f"Sources processed: {stats['sources_processed']}")
    print(f"Events scraped: {stats['events_scraped']}")
    print(f"Events added: {stats['events_added']}")
    print(f"Events updated: {stats['events_updated']}")
    print(f"Duplicates removed: {stats['events_deduplicated']}")
    
    if stats['errors']:
        print(f"\n⚠️ Errors ({len(stats['errors'])}):")
        for error in stats['errors']:
            print(f"  - {error['source']}: {error['error']}")
    
    return 0 if not stats['errors'] else 1


if __name__ == '__main__':
    sys.exit(main())

