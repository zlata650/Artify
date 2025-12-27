# CLAUDE.md - AI Assistant Guide for Artify

## Project Overview

**Artify** is a Paris cultural events aggregation and recommendation platform that scrapes, normalizes, and presents events from various cultural venues across Paris including museums, concert halls, galleries, and more.

### Core Purpose
- Aggregate cultural events from diverse Paris venues
- Normalize and categorize event data using AI
- Provide personalized event recommendations
- Maintain up-to-date event database through automated daily scraping

### Tech Stack
- **Backend**: Python 3.11, Flask, Playwright, OpenAI API
- **Frontend**: Next.js, TypeScript, React
- **Database**: SQLite (with optional Supabase sync)
- **Infrastructure**: GitHub Actions, MCP server integration
- **Timezone**: Europe/Paris (all dates/times)

---

## Repository Structure

### Current State
The repository was recently cleaned up (commit `77c851b`). The main branch contains only configuration and infrastructure files. The actual codebase was removed in preparation for restructuring.

```
Artify/
├── .cursor/
│   ├── mcp.json              # MCP server configuration (currently empty)
│   └── mvp_1                 # MVP planning file (empty)
├── .github/
│   └── workflows/
│       └── daily_scrape.yml  # Automated daily event scraping workflow
├── .gitignore                # Comprehensive ignore patterns
└── CLAUDE.md                 # This file
```

### Previous Architecture (for reference)

The codebase previously contained:

#### Backend Structure (`backend/`)
```
backend/
├── __init__.py
├── api.py                    # Flask API endpoints
├── ingest.py                 # Main ingestion pipeline orchestrator
├── mcp_server.py            # MCP server integration
├── requirements.txt         # Python dependencies
├── core/
│   ├── categorizer.py       # AI-powered event categorization
│   ├── db.py               # Database operations and EventsDB class
│   ├── deduplicate.py      # Event deduplication logic
│   ├── models.py           # Data models
│   ├── normalization.py    # Data normalization utilities
│   └── ticket_extractor.py # Extract ticket URLs from events
└── scrapers/
    ├── base.py             # Base scraper class
    ├── aggregators/
    │   ├── eventbrite.py   # Eventbrite scraper
    │   └── sortiraparis.py # Sortiraparis scraper
    ├── museums/
    │   ├── louvre.py       # Louvre Museum scraper
    │   ├── orsay.py        # Musée d'Orsay scraper
    │   └── pompidou.py     # Centre Pompidou scraper
    ├── venues/
    │   ├── opera_paris.py  # Opéra de Paris scraper
    │   └── philharmonie.py # Philharmonie de Paris scraper
    ├── galleries/
    │   └── generic_gallery.py
    └── workshops/
        └── generic_workshop.py
```

#### Frontend Structure (`web/`)
```
web/
├── package.json
├── next.config.js
├── tsconfig.json
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx           # Homepage
│   ├── globals.css        # Global styles
│   ├── events/[id]/
│   │   └── page.tsx       # Event detail page
│   ├── results/
│   │   └── page.tsx       # Search results
│   ├── musees/
│   │   ├── page.tsx       # Museums listing
│   │   └── orsay/page.tsx # Orsay-specific page
│   ├── admin/
│   │   └── page.tsx       # Admin dashboard
│   └── api/
│       ├── recommendations/route.ts
│       ├── museums/orsay/route.ts
│       └── admin/
│           ├── history/route.ts
│           ├── parse/route.ts
│           ├── scheduler/route.ts
│           ├── sources/route.ts
│           └── stats/route.ts
├── components/
│   ├── Onboarding.tsx     # User onboarding flow
│   └── RecommendationSection.tsx
├── hooks/
│   └── useRecommendations.ts
└── lib/
    └── recommendations/
        ├── engine.ts      # Recommendation algorithm
        ├── types.ts
        └── userProfile.ts
```

#### Configuration & Scripts
```
config/
└── sources.py             # Source configuration

Root level:
├── app.py                 # Main Flask application
├── admin_api.py          # Admin API endpoints
├── auth.py               # Authentication
├── database.py           # Database utilities
├── requirements.txt      # Root Python dependencies
└── various scrapers and utilities
```

---

## Key Workflows

### 1. Daily Event Scraping (Automated)
**File**: `.github/workflows/daily_scrape.yml`

**Schedule**: Daily at 02:00 Paris time (01:00 UTC)

**Process**:
1. Checkout repository
2. Setup Python 3.11 environment
3. Install backend dependencies from `backend/requirements.txt`
4. Install Playwright with Chromium browser
5. Load OPENAI_API_KEY from GitHub secrets
6. Run ingestion pipeline: `python -m backend.ingest`
7. Upload database artifact (`real_events.db`)
8. Commit and push database updates (on main branch only)
9. Generate statistics report

**Manual Trigger**: Supports workflow_dispatch with options:
- `sources`: Comma-separated list or "all" (default: all)
- `dry_run`: Boolean to prevent database changes (default: false)

**Environment Variables**:
- `OPENAI_API_KEY`: Required for event categorization
- `TZ`: Europe/Paris
- `PYTHON_VERSION`: 3.11

### 2. Ingestion Pipeline
**Entry Point**: `backend/ingest.py`

**Expected Flow**:
1. Initialize scrapers from configuration
2. Scrape events from each source (museums, venues, aggregators)
3. Normalize event data (dates, locations, formatting)
4. Categorize events using OpenAI API
5. Extract ticket URLs where available
6. Deduplicate events (same event from multiple sources)
7. Store in SQLite database (`real_events.db`)

**Data Model** (from `backend/core/models.py`):
- Event fields: title, description, date, time, location, category, price, ticket_url, source
- Categories: Music (Classical, Jazz, Pop, Rock, Rap, Techno, Dance), Museums, Theater, Cinema, Workshops, Other

### 3. Scraper Development Pattern
**Base Class**: `backend/scrapers/base.py`

All scrapers should inherit from the base scraper class and implement:
- `scrape()`: Main scraping method
- `parse_event()`: Parse individual event data
- Error handling and logging
- Rate limiting and politeness delays
- Playwright browser automation when needed

### 4. Recommendation Engine
**Location**: `web/lib/recommendations/`

**Components**:
- User profile tracking (preferences, view history)
- Content-based filtering
- Collaborative filtering considerations
- Personalized event scoring

---

## Development Conventions

### Python Code Style
- **Version**: Python 3.11+
- **Style Guide**: PEP 8
- **Type Hints**: Use type hints for function signatures
- **Imports**: Absolute imports for backend modules (`from backend.core.db import EventsDB`)
- **Error Handling**: Comprehensive try-except blocks for external API calls and web scraping
- **Logging**: Use Python logging module, write to `scraping_log.txt` for scraper logs

### TypeScript/Next.js Conventions
- **Framework**: Next.js App Router (not Pages Router)
- **TypeScript**: Strict mode enabled
- **Components**: React Server Components by default, use 'use client' only when needed
- **API Routes**: In `app/api/` directory
- **Data Fetching**: Server-side where possible

### Database Conventions
- **Primary Database**: SQLite (`real_events.db`)
- **Schema Management**: Defined in `backend/core/db.py`
- **Timezone**: All dates stored in Paris timezone
- **Deduplication**: Events checked for duplicates before insertion
- **Statistics**: EventsDB class provides `get_statistics()` method for metrics

### Git Workflow
- **Main Branch**: Protected, only updated via automated workflow or approved PRs
- **Feature Branches**: Use descriptive names (e.g., `feature/add-cinema-scraper`)
- **Commits**: Descriptive messages, use conventional commits format
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation
  - `refactor:` for code refactoring
  - `test:` for tests
  - Automated commits: `📊 Daily events update - YYYY-MM-DD`

### Environment Variables
**Required**:
- `OPENAI_API_KEY`: For event categorization

**Optional**:
- `SUPABASE_URL`: For Supabase sync
- `SUPABASE_KEY`: For Supabase authentication

**Storage**: Use `.env` file (gitignored) for local development

---

## AI Assistant Guidelines

### When Adding New Event Sources

1. **Research the Source**
   - Identify the website structure and event pages
   - Check robots.txt and terms of service
   - Determine if API exists or web scraping needed

2. **Create Scraper**
   - Place in appropriate `backend/scrapers/` subdirectory
   - Inherit from base scraper class
   - Implement required methods
   - Add comprehensive error handling
   - Include rate limiting (respect the source)

3. **Register Source**
   - Add to `config/sources.py`
   - Update documentation

4. **Test Thoroughly**
   - Run with `--dry-run` flag first
   - Verify data normalization
   - Check deduplication logic
   - Validate categorization results

### When Modifying the Database Schema

1. **Update Model**: Modify `backend/core/models.py`
2. **Update DB Class**: Modify `backend/core/db.py`
3. **Migration**: Create migration logic for existing data
4. **Update API**: Ensure API endpoints reflect schema changes
5. **Update Frontend**: Update TypeScript types and components
6. **Test**: Verify all CRUD operations work

### When Working with External APIs

1. **API Keys**: Always use environment variables, never hardcode
2. **Rate Limiting**: Implement exponential backoff and respect limits
3. **Error Handling**: Handle network errors, timeouts, rate limits gracefully
4. **Costs**: Be mindful of API usage costs (especially OpenAI)
5. **Fallbacks**: Consider fallback strategies for API failures

### When Debugging Scrapers

**Check**:
1. `scraping_log.txt` for detailed logs
2. Website HTML structure hasn't changed
3. Playwright browser automation is working
4. Network connectivity and DNS resolution
5. Rate limiting or IP blocking by source
6. Selector changes (CSS/XPath)

**Tools**:
- Run with `--dry-run` to avoid database changes
- Use `--source <name>` to test specific scraper
- Check GitHub Actions logs for automated runs

### Code Quality Standards

**Before Committing**:
1. **Test Locally**: Run affected components
2. **Check Dependencies**: Ensure `requirements.txt` / `package.json` updated
3. **Verify Imports**: No circular dependencies
4. **Review Logs**: Check for warnings or errors
5. **Clean Up**: Remove debug print statements, commented code
6. **Documentation**: Update relevant docs and comments

**Security Considerations**:
1. **Input Validation**: Validate all external data
2. **SQL Injection**: Use parameterized queries
3. **XSS Prevention**: Sanitize user inputs in frontend
4. **API Keys**: Never commit secrets
5. **Dependencies**: Keep dependencies updated for security patches

---

## Common Tasks

### Running the Ingestion Pipeline Locally

```bash
# Install dependencies
pip install -r backend/requirements.txt
playwright install chromium

# Set environment variable
export OPENAI_API_KEY="your-key-here"

# Run full ingestion
python -m backend.ingest

# Run specific source
python -m backend.ingest --source louvre

# Dry run (no database changes)
python -m backend.ingest --dry-run
```

### Running the Frontend Locally

```bash
cd web
npm install
npm run dev
# Access at http://localhost:3000
```

### Database Operations

```bash
# View statistics
python -c "from backend.core.db import EventsDB; db = EventsDB(); print(db.get_statistics())"

# Query events
sqlite3 real_events.db "SELECT * FROM events LIMIT 10;"

# Backup database
cp real_events.db real_events.db.backup
```

### Adding a New Museum Scraper

1. Create `backend/scrapers/museums/new_museum.py`
2. Implement scraper class inheriting from base
3. Add to `config/sources.py`
4. Test with `python -m backend.ingest --source new_museum --dry-run`
5. Verify data quality and categorization
6. Run full ingestion and check for duplicates

---

## Project Status & Next Steps

### Current Status (as of commit 77c851b)
- Repository cleaned and prepared for restructuring
- Infrastructure (GitHub Actions, .gitignore) maintained
- All implementation files removed
- Ready for new architecture implementation

### When Rebuilding the Codebase

**Priorities**:
1. **Core Database Layer**: Recreate `backend/core/db.py` with EventsDB class
2. **Data Models**: Define clear Pydantic or dataclass models in `backend/core/models.py`
3. **Base Scraper**: Implement robust base scraper class
4. **Initial Scrapers**: Start with 2-3 reliable sources (e.g., major museums)
5. **Ingestion Pipeline**: Build modular, testable pipeline
6. **API Layer**: Create RESTful API with clear endpoints
7. **Frontend**: Implement with modern React best practices

**Architecture Considerations**:
- Use dependency injection for testability
- Separate concerns (scraping, normalization, storage)
- Make scrapers pluggable and configurable
- Consider async/await for concurrent scraping
- Implement comprehensive logging from the start
- Design for horizontal scalability

---

## Resources & References

### Documentation to Create
- `README.md`: User-facing project description
- `BACKEND_README.md`: Backend development guide
- `SUPABASE_CONFIG.md`: Supabase integration guide
- `docs/CATEGORIES_ANALYSIS.md`: Event categorization guidelines
- API documentation (OpenAPI/Swagger)

### External Resources
- [Playwright Documentation](https://playwright.dev/python/)
- [Next.js App Router](https://nextjs.org/docs/app)
- [OpenAI API](https://platform.openai.com/docs)
- [GitHub Actions](https://docs.github.com/en/actions)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

### Event Sources (Previous Implementation)
- Louvre Museum
- Musée d'Orsay
- Centre Pompidou
- Opéra de Paris
- Philharmonie de Paris
- Eventbrite
- Sortiraparis.com
- Various galleries and workshops

---

## Troubleshooting

### Common Issues

**GitHub Actions Workflow Fails**:
- Check OPENAI_API_KEY secret is set in repository settings
- Verify backend/requirements.txt exists and is valid
- Check Playwright browser installation
- Review workflow logs for specific errors

**Scraper Returns No Data**:
- Website structure may have changed (inspect HTML)
- Check for rate limiting or blocking
- Verify network connectivity
- Review scraper selectors and logic

**OpenAI API Errors**:
- Verify API key is valid and has credits
- Check rate limits (requests per minute)
- Review prompt structure in categorizer
- Consider implementing retry logic

**Database Issues**:
- Check file permissions on `real_events.db`
- Verify schema matches model definitions
- Look for constraint violations in logs
- Check disk space availability

---

## Notes for AI Assistants

### Communication Style
- Be concise and technical
- Reference specific files and line numbers when discussing code
- Explain architectural decisions and trade-offs
- Highlight potential issues or edge cases
- Suggest testing strategies

### When Uncertain
- State assumptions clearly
- Propose multiple approaches with pros/cons
- Ask for clarification on requirements
- Reference similar patterns in the codebase
- Suggest research or prototyping steps

### Best Practices
- **Read First**: Always read existing code before suggesting changes
- **Test Locally**: Verify changes work before committing
- **Document**: Update relevant documentation with code changes
- **Security**: Consider security implications of all changes
- **Performance**: Be mindful of API costs and scraping frequency
- **Maintainability**: Write clear, self-documenting code
- **Error Handling**: Plan for failures and edge cases

### Prefer Existing Patterns
- Follow established naming conventions
- Use existing utilities and helpers
- Match code style of surrounding code
- Leverage existing abstractions
- Don't reinvent solved problems

---

**Last Updated**: 2025-12-27
**Current Branch**: claude/add-claude-documentation-jdeO4
**Project Status**: Post-cleanup, ready for restructuring
