/**
 * Search functionality for events
 */

import { Event, fetchEvents } from './api'

export interface SearchResult {
  events: Event[]
  total: number
  query: string
}

export async function searchEvents(
  query: string,
  filters?: {
    category?: string
    venue?: string
    is_free?: boolean
    date_from?: string
    date_to?: string
  }
): Promise<SearchResult> {
  if (!query.trim()) {
    // If no query, return all events with filters
    const result = await fetchEvents({
      ...filters,
      limit: 100,
    })
    return {
      events: result.events,
      total: result.count,
      query: '',
    }
  }

  // Fetch all events and filter by search query
  const result = await fetchEvents({
    ...filters,
    limit: 500, // Get more results for search
  })

  const searchLower = query.toLowerCase()
  const filtered = result.events.filter((event) => {
    const titleMatch = event.title.toLowerCase().includes(searchLower)
    const descMatch = event.description?.toLowerCase().includes(searchLower)
    const locationMatch = event.location.toLowerCase().includes(searchLower)
    const categoryMatch = event.category?.toLowerCase().includes(searchLower)

    return titleMatch || descMatch || locationMatch || categoryMatch
  })

  return {
    events: filtered,
    total: filtered.length,
    query,
  }
}

