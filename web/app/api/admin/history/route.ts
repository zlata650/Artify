import { NextResponse } from 'next/server'

const ADMIN_API_URL = process.env.ADMIN_API_URL || 'http://localhost:5001'

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const limit = searchParams.get('limit') || '50'
    
    const response = await fetch(`${ADMIN_API_URL}/api/admin/history?limit=${limit}`, {
      cache: 'no-store'
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch history')
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching history:', error)
    return NextResponse.json({
      history: []
    })
  }
}



