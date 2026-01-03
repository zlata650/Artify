# Artify - Paris Cultural Events Aggregator

A comprehensive Paris cultural events aggregator that scrapes and organizes events from museums, venues, and cultural sites into one searchable platform.

## Project Structure

```
Artify/
├── backend/          # Python FastAPI backend
│   ├── api/         # FastAPI application
│   ├── core/        # Database and core utilities
│   ├── scrapers/    # Web scraping modules
│   └── requirements.txt
├── web/             # Next.js frontend
│   ├── app/         # Next.js App Router pages
│   ├── components/  # React components
│   └── lib/         # Utilities and API client
└── .github/         # GitHub Actions workflows
```

## Features

### Phase 1 (MVP) - Current
- ✅ SQLite database with event schema
- ✅ FastAPI REST API
- ✅ Next.js 14 frontend with App Router
- ✅ Playwright scraper framework
- ✅ Event listing and detail pages
- ✅ Filters (free, category, venue)
- ✅ Free event badges and price display

### Phase 2 (Planned)
- Museum scrapers (Louvre, Orsay, Pompidou)
- AI-powered event categorization
- Advanced search
- Map view

### Phase 3 (Planned)
- English language support
- User accounts
- Mobile optimization
- Supabase migration

## Getting Started

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# Run API server
python -m api.main
# or
uvicorn api.main:app --reload
```

API will be available at http://localhost:8000

### Frontend Setup

```bash
cd web
npm install
npm run dev
```

Frontend will be available at http://localhost:3000

### Database

The SQLite database (`real_events.db`) is created automatically on first run.

## Development

### Running Scrapers

```bash
cd backend
python -m ingest --source all
```

### API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## License

MIT

