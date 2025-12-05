import { NextResponse } from 'next/server'

const ADMIN_API_URL = process.env.ADMIN_API_URL || 'http://localhost:5001'

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}))
    
    const response = await fetch(`${ADMIN_API_URL}/api/admin/parse`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })
    
    if (!response.ok) {
      throw new Error('Failed to trigger parsing')
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error triggering parsing:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to trigger parsing. Make sure the admin API is running.' },
      { status: 500 }
    )
  }
}



