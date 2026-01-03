/**
 * API client for fetching events from the backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface Event {
  id: string
  title: string
  description?: string
  start_date: string
  end_date?: string
  location: string
  address?: string
  category?: string
  image_url?: string
  source_url?: string
  source_name?: string
  is_free: boolean
  price?: number | null
  price_min?: number | null
  price_max?: number | null
  currency: string
  ticket_url?: string
  created_at?: string
  updated_at?: string
}

export interface EventsResponse {
  count: number
  limit: number
  offset: number
  events: Event[]
}

export interface FetchEventsParams {
  date_from?: string
  date_to?: string
  category?: string
  venue?: string
  is_free?: boolean
  limit?: number
  offset?: number
}

export async function fetchEvents(
  params: FetchEventsParams = {}
): Promise<EventsResponse> {
  const searchParams = new URLSearchParams()
  
  if (params.date_from) searchParams.append('date_from', params.date_from)
  if (params.date_to) searchParams.append('date_to', params.date_to)
  if (params.category) searchParams.append('category', params.category)
  if (params.venue) searchParams.append('venue', params.venue)
  if (params.is_free !== undefined) searchParams.append('is_free', String(params.is_free))
  if (params.limit) searchParams.append('limit', String(params.limit))
  if (params.offset) searchParams.append('offset', String(params.offset))

  const url = `${API_BASE_URL}/events${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
  
  const response = await fetch(url, {
    next: { revalidate: 60 }, // Revalidate every 60 seconds
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch events: ${response.statusText}`)
  }

  return response.json()
}

export async function fetchEvent(eventId: string): Promise<Event | null> {
  const response = await fetch(`${API_BASE_URL}/events/${eventId}`, {
    next: { revalidate: 60 },
  })

  if (response.status === 404) {
    return null
  }

  if (!response.ok) {
    throw new Error(`Failed to fetch event: ${response.statusText}`)
  }

  return response.json()
}

export async function fetchCategories(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/categories`, {
    next: { revalidate: 3600 }, // Revalidate every hour
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch categories: ${response.statusText}`)
  }

  const data = await response.json()
  return data.categories || []
}

export async function fetchVenues(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/venues`, {
    next: { revalidate: 3600 },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch venues: ${response.statusText}`)
  }

  const data = await response.json()
  return data.venues || []
}

