"""
Ingestion pipeline for scraping events from multiple sources
"""
import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from core.db import EventsDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Artify event ingestion pipeline")
    parser.add_argument(
        "--source",
        type=str,
        help="Specific source to scrape (comma-separated) or 'all' for all sources"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode - don't save to database"
    )
    
    args = parser.parse_args()
    
    db = EventsDB()
    
    logger.info("Starting Artify ingestion pipeline")
    logger.info(f"Dry run: {args.dry_run}")
    
    # TODO: Import and run scrapers
    # For now, this is a placeholder
    logger.info("No scrapers implemented yet. Add scrapers in scrapers/ directory.")
    
    if not args.dry_run:
        stats = db.get_statistics()
        logger.info(f"Database statistics: {stats}")
    
    logger.info("Ingestion pipeline completed")


if __name__ == "__main__":
    main()

