import { NextResponse } from 'next/server'

const ADMIN_API_URL = process.env.ADMIN_API_URL || 'http://localhost:5001'

export async function GET() {
  try {
    const response = await fetch(`${ADMIN_API_URL}/api/admin/sources`, {
      cache: 'no-store'
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch sources')
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching sources:', error)
    // Retourner des données mock
    return NextResponse.json({
      sources: [
        {
          id: 'sortiraparis',
          name: 'Sortir à Paris',
          url: 'https://www.sortiraparis.com/',
          filter_keyword: 'concert',
          enabled: true
        },
        {
          id: 'fnac_spectacles',
          name: 'Fnac Spectacles',
          url: 'https://www.fnacspectacles.com/',
          filter_keyword: 'concert',
          enabled: false
        },
        {
          id: 'ticketmaster',
          name: 'Ticketmaster',
          url: 'https://www.ticketmaster.fr/',
          filter_keyword: 'concert',
          enabled: false
        }
      ]
    })
  }
}



