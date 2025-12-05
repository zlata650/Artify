# 🎭 Artify Backend - Paris Events Data System

## Overview

This backend system scrapes, normalizes, and serves real events happening in Paris from multiple sources:

- **Aggregators**: Eventbrite, Sortir à Paris
- **Venues**: Philharmonie de Paris, Opéra de Paris (Garnier & Bastille)
- **Museums**: Louvre, Musée d'Orsay, Centre Pompidou
- **Galleries**: Perrotin, Thaddaeus Ropac, Fondation Cartier, Palais de Tokyo
- **Workshops**: WeCandoo, Superprof, and other creative ateliers

## Architecture

```
backend/
├── core/               # Core modules
│   ├── models.py       # Unified event schema
│   ├── db.py           # Database operations
│   ├── normalization.py # Data normalization
│   ├── categorizer.py  # AI categorization
│   ├── deduplicate.py  # Deduplication logic
│   └── ticket_extractor.py # Ticket URL extraction
├── scrapers/           # Source-specific scrapers
│   ├── aggregators/    # Eventbrite, Sortir à Paris, etc.
│   ├── venues/         # Concert halls, theatres
│   ├── museums/        # Louvre, Orsay, Pompidou
│   ├── galleries/      # Art galleries
│   └── workshops/      # Creative ateliers
├── api.py              # Flask API server
├── ingest.py           # Main ingestion pipeline
├── mcp_server.py       # MCP server for AI tools
└── requirements.txt    # Python dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r backend/requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Set Up Environment

Create a `.env` file:

```env
# Optional: For AI categorization
OPENAI_API_KEY=your_key_here

# Database path (default: real_events.db)
EVENTS_DB_PATH=real_events.db
```

### 3. Run the Scraping Pipeline

```bash
# Scrape all sources
python -m backend.ingest

# Scrape specific sources
python -m backend.ingest --source eventbrite philharmonie

# Scrape a group of sources
python -m backend.ingest --group museums

# Dry run (no database changes)
python -m backend.ingest --dry-run
```

### 4. Start the API Server

```bash
python -m backend.api
# or
python backend/api.py
```

The API will be available at `http://localhost:5001`

## API Endpoints

### Events

- `GET /api/events` - List events with filters
  - `categories`: comma-separated (musique, spectacles, arts_visuels, ateliers, sport, gastronomie, culture, nightlife, rencontres)
  - `date_from`, `date_to`: YYYY-MM-DD format
  - `arrondissements`: comma-separated (1-20)
  - `price_max`: maximum price in euros
  - `time_of_day`: jour, soir, nuit
  - `search`: text search
  - `limit`, `offset`: pagination

- `GET /api/events/<id>` - Get single event

- `GET /api/events/upcoming` - Get upcoming events
  - `days`: number of days ahead (default 30)

- `GET /api/events/search?q=<query>` - Text search

- `GET /api/events/stats` - Database statistics

- `GET /api/events/categories` - Available categories

- `GET /api/health` - Health check

## Unified Event Schema

```json
{
  "id": "abc123def456",
  "title": "Concert Name",
  "description": "Event description...",
  "category": "musique",
  "sub_category": "classique",
  "tags": ["concert", "philharmonie"],
  
  "date_start": "2025-01-15",
  "date_end": null,
  "time_start": "20:00",
  "time_end": "22:00",
  "time_of_day": "soir",
  
  "location_name": "Philharmonie de Paris",
  "address": "221 avenue Jean-Jaurès, 75019 Paris",
  "arrondissement": 19,
  "latitude": 48.8895,
  "longitude": 2.3938,
  
  "price_from": 25.0,
  "price_to": 85.0,
  "is_free": false,
  "currency": "EUR",
  
  "image_url": "https://...",
  "source_name": "philharmonie",
  "source_event_url": "https://...",
  "ticket_url": "https://...",
  "has_direct_ticket_button": true,
  
  "created_at": "2025-01-01T10:00:00",
  "updated_at": "2025-01-01T10:00:00",
  "verified": true
}
```

## Adding New Sources

### 1. Create a Scraper

```python
# backend/scrapers/venues/my_venue.py
from backend.scrapers.base import HTMLScraper, ScraperConfig
from backend.core.models import ScrapedEvent

class MyVenueScraper(HTMLScraper):
    def __init__(self, max_events=100):
        config = ScraperConfig(
            name="my_venue",
            source_url="https://myvenue.com/agenda",
            source_type="venue",
            category_hint="musique",
            requires_playwright=True,
            max_events=max_events,
        )
        super().__init__(config)
    
    def get_event_urls(self, soup) -> List[str]:
        # Extract event URLs from listing page
        return [...]
    
    def parse_event_page(self, soup, url) -> ScrapedEvent:
        # Parse event details
        return ScrapedEvent(
            title=...,
            description=...,
            source_name='my_venue',
            source_event_url=url,
            ...
        )
```

### 2. Register in Ingest Pipeline

Add to `backend/ingest.py`:

```python
from backend.scrapers.venues.my_venue import MyVenueScraper

SCRAPERS['my_venue'] = MyVenueScraper
```

## Ticket URL Extraction

The system extracts real ticket purchase URLs by:

1. Analyzing event pages for ticket buttons/links
2. Looking for keywords: "Billets", "Réserver", "Acheter", "Book", "Tickets"
3. Following redirects to get final purchase URL
4. Avoiding generic pages (homepage, category pages)

Rules:
- Prefer URLs containing: `/billet`, `/ticket`, `/reserv`, `/book`, `/checkout`
- Avoid URLs that are: root domains, `/agenda`, `/concerts`, `/category`

## AI Categorization

Events are categorized using:

1. **OpenAI GPT-3.5** (if API key provided) - Analyzes title, description, venue
2. **Rule-based fallback** - Keyword matching

Categories:
- `spectacles`: Theatre, opera, ballet, comedy, circus
- `musique`: Concerts (classical, jazz, rock, pop, electro)
- `arts_visuels`: Exhibitions, galleries, photography
- `ateliers`: Creative workshops (ceramics, painting, drawing)
- `sport`: Fitness, yoga, sports events
- `gastronomie`: Wine tasting, cooking classes
- `culture`: Cinema, conferences, guided tours
- `nightlife`: Clubs, bars, parties
- `rencontres`: Meetups, networking

## Deduplication

Events are deduplicated using RapidFuzz fuzzy matching:

- Same date
- Similar title (>85% match)
- Similar location (>75% match)

The canonical event (kept) is chosen based on:
- Has direct ticket button
- Has image
- Longer description
- From trusted source (official venues preferred)

## GitHub Actions

The workflow `.github/workflows/daily_scrape.yml` runs daily at 02:00 Paris time:

1. Checks out repository
2. Installs Python and dependencies
3. Installs Playwright browsers
4. Runs full ingestion pipeline
5. Commits updated database

Manual trigger available with options for:
- Specific sources
- Dry run mode

## MCP Server

The MCP server (`backend/mcp_server.py`) provides tools for AI assistants:

- `scrape_all_events` - Run ingestion pipeline
- `get_events` - Query events with filters
- `refresh_event_ticket_url` - Update ticket URL for an event
- `get_event_stats` - Database statistics
- `search_events` - Text search

Start the MCP server:

```bash
python -m backend.mcp_server
```

## Database

SQLite database `real_events.db` with tables:

- `events` - Main events table
- `sources` - Scraper source tracking
- `scrape_logs` - Scraping history
- `duplicates` - Duplicate detection records

For production, consider migrating to PostgreSQL or Supabase.

## Troubleshooting

### Playwright Issues

```bash
# Install browsers
playwright install

# Install system dependencies (Linux)
playwright install-deps
```

### No Events Found

1. Check if source website structure changed
2. Run with verbose logging: `python -m backend.ingest -v`
3. Try dry run: `python -m backend.ingest --source eventbrite --dry-run`

### API Not Working

1. Check database exists: `ls real_events.db`
2. Check event count: `sqlite3 real_events.db "SELECT COUNT(*) FROM events;"`
3. Run API in debug mode: `FLASK_DEBUG=1 python -m backend.api`

## License

MIT License

