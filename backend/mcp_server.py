#!/usr/bin/env python3
"""
🎭 Artify - MCP Server for Paris Events
Model Context Protocol server providing tools for event management.

Tools:
- scrape_all_events: Run the full ingestion pipeline
- get_events: Query events from database
- refresh_event_ticket_url: Update ticket URL for a specific event
"""

import json
import sys
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime

# MCP imports - using simple JSON-RPC protocol
# For a full MCP implementation, you'd use the official mcp SDK

from backend.core.db import EventsDB
from backend.core.ticket_extractor import TicketExtractor
from backend.ingest import IngestionPipeline


class MCPServer:
    """
    MCP Server for Paris Events.
    
    Provides tools for managing and querying Paris events.
    """
    
    def __init__(self):
        self.db = EventsDB()
        self.tools = {
            'scrape_all_events': self.scrape_all_events,
            'get_events': self.get_events,
            'refresh_event_ticket_url': self.refresh_event_ticket_url,
            'get_event_stats': self.get_event_stats,
            'search_events': self.search_events,
        }
    
    def get_tool_definitions(self) -> List[Dict]:
        """Return tool definitions for MCP."""
        return [
            {
                "name": "scrape_all_events",
                "description": "Run the full event scraping pipeline to collect Paris events from all sources",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sources": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of sources to scrape (e.g., 'eventbrite', 'philharmonie')"
                        },
                        "dry_run": {
                            "type": "boolean",
                            "description": "If true, don't save to database",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "get_events",
                "description": "Query Paris events from the database with optional filters",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Filter by category (musique, spectacles, arts_visuels, etc.)"
                        },
                        "date_from": {
                            "type": "string",
                            "description": "Start date filter (YYYY-MM-DD)"
                        },
                        "date_to": {
                            "type": "string",
                            "description": "End date filter (YYYY-MM-DD)"
                        },
                        "search": {
                            "type": "string",
                            "description": "Text search query"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 20
                        }
                    }
                }
            },
            {
                "name": "refresh_event_ticket_url",
                "description": "Re-extract the ticket URL for a specific event",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": "The event ID to refresh"
                        }
                    },
                    "required": ["event_id"]
                }
            },
            {
                "name": "get_event_stats",
                "description": "Get statistics about events in the database",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "search_events",
                "description": "Search events by text query",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    
    async def scrape_all_events(
        self, 
        sources: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Run the ingestion pipeline."""
        pipeline = IngestionPipeline(
            extract_tickets=True,
            deduplicate=True,
            dry_run=dry_run
        )
        
        stats = pipeline.run(sources)
        
        return {
            "success": True,
            "message": f"Scraped {stats['events_scraped']} events",
            "stats": stats
        }
    
    async def get_events(
        self,
        category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Query events from database."""
        categories = [category] if category else None
        
        events = self.db.get_events(
            categories=categories,
            date_from=date_from,
            date_to=date_to,
            search_query=search,
            limit=limit
        )
        
        return {
            "success": True,
            "count": len(events),
            "events": events
        }
    
    async def refresh_event_ticket_url(self, event_id: str) -> Dict[str, Any]:
        """Refresh ticket URL for an event."""
        event = self.db.get_event(event_id)
        
        if not event:
            return {
                "success": False,
                "error": f"Event {event_id} not found"
            }
        
        source_url = event.get('source_event_url')
        if not source_url:
            return {
                "success": False,
                "error": "Event has no source URL"
            }
        
        try:
            with TicketExtractor() as extractor:
                ticket_url, has_direct = extractor.extract_ticket_url(source_url)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to extract ticket URL: {e}"
            }
        
        # Update in database
        self.db.upsert_event({
            **event,
            'ticket_url': ticket_url,
            'has_direct_ticket_button': has_direct,
            'updated_at': datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "event_id": event_id,
            "ticket_url": ticket_url,
            "has_direct_button": has_direct
        }
    
    async def get_event_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = self.db.get_statistics()
        
        return {
            "success": True,
            "stats": stats
        }
    
    async def search_events(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search events."""
        events = self.db.get_events(search_query=query, limit=limit)
        
        return {
            "success": True,
            "query": query,
            "count": len(events),
            "events": events
        }
    
    async def handle_request(self, request: Dict) -> Dict:
        """Handle an MCP request."""
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')
        
        if method == 'tools/list':
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": self.get_tool_definitions()
                }
            }
        
        elif method == 'tools/call':
            tool_name = params.get('name')
            tool_args = params.get('arguments', {})
            
            if tool_name not in self.tools:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool not found: {tool_name}"
                    }
                }
            
            try:
                result = await self.tools[tool_name](**tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2, default=str)
                            }
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32000,
                        "message": str(e)
                    }
                }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }
    
    async def run_stdio(self):
        """Run the server using stdio transport."""
        print("🎭 Artify MCP Server started", file=sys.stderr)
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                response = await self.handle_request(request)
                
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)


def main():
    """Main entry point."""
    server = MCPServer()
    asyncio.run(server.run_stdio())


if __name__ == '__main__':
    main()

