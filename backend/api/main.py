"""
FastAPI main application for Artify events API
"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.db import EventsDB

app = FastAPI(
    title="Artify API",
    description="API for Paris cultural events aggregator",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = EventsDB()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Artify API - Paris Cultural Events",
        "version": "1.0.0",
        "endpoints": {
            "events": "/events",
            "event_detail": "/events/{id}",
            "categories": "/categories",
            "venues": "/venues",
            "statistics": "/statistics"
        }
    }


@app.get("/events")
async def get_events(
    date_from: Optional[str] = Query(None, description="Start date filter (ISO 8601)"),
    date_to: Optional[str] = Query(None, description="End date filter (ISO 8601)"),
    category: Optional[str] = Query(None, description="Category filter"),
    venue: Optional[str] = Query(None, description="Venue/location filter"),
    is_free: Optional[bool] = Query(None, description="Filter free events"),
    search: Optional[str] = Query(None, description="Search query (title, description, location)"),
    limit: int = Query(100, ge=1, le=500, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """Get events with optional filters and search"""
    try:
        events = db.get_events(
            date_from=date_from,
            date_to=date_to,
            category=category,
            venue=venue,
            is_free=is_free,
            limit=limit * 2 if search else limit,  # Get more for filtering
            offset=offset
        )
        
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            events = [
                e for e in events
                if (search_lower in e.get('title', '').lower() or
                    search_lower in e.get('description', '').lower() or
                    search_lower in e.get('location', '').lower() or
                    search_lower in e.get('category', '').lower())
            ]
            # Limit after filtering
            events = events[:limit]
        
        return {
            "count": len(events),
            "limit": limit,
            "offset": offset,
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events/{event_id}")
async def get_event(event_id: str):
    """Get a single event by ID"""
    event = db.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.get("/categories")
async def get_categories():
    """Get list of all event categories"""
    categories = db.get_categories()
    return {"categories": categories}


@app.get("/venues")
async def get_venues():
    """Get list of all venues"""
    venues = db.get_venues()
    return {"venues": venues}


@app.get("/statistics")
async def get_statistics():
    """Get database statistics"""
    stats = db.get_statistics()
    return stats


if __name__ == "__main__":
    import uvicorn
    import os
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)

