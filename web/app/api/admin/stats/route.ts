import { NextResponse } from 'next/server'

const ADMIN_API_URL = process.env.ADMIN_API_URL || 'http://localhost:5001'

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const period = searchParams.get('period') || 'day'
    
    const response = await fetch(`${ADMIN_API_URL}/api/admin/stats?period=${period}`, {
      cache: 'no-store'
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch stats')
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching stats:', error)
    // Retourner des données mock si l'API n'est pas disponible
    return NextResponse.json({
      stats: {
        period: 'day',
        total_concerts: 0,
        new_concerts: 0,
        sources_parsed: 0,
        parsing_errors: 0
      },
      today: {
        period: 'day',
        total_concerts: 0,
        new_concerts: 0,
        sources_parsed: 0,
        parsing_errors: 0
      },
      week: {
        period: 'week',
        total_concerts: 0,
        new_concerts: 0,
        sources_parsed: 0,
        parsing_errors: 0
      },
      month: {
        period: 'month',
        total_concerts: 0,
        new_concerts: 0,
        sources_parsed: 0,
        parsing_errors: 0
      }
    })
  }
}



