import { NextResponse } from 'next/server'

const ADMIN_API_URL = process.env.ADMIN_API_URL || 'http://localhost:5001'

export async function GET() {
  try {
    const response = await fetch(`${ADMIN_API_URL}/api/admin/scheduler/status`, {
      cache: 'no-store'
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch scheduler status')
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching scheduler status:', error)
    return NextResponse.json({
      running: false,
      jobs: []
    })
  }
}

export async function POST(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const action = searchParams.get('action') || 'start'
    
    const response = await fetch(`${ADMIN_API_URL}/api/admin/scheduler/${action}`, {
      method: 'POST'
    })
    
    if (!response.ok) {
      throw new Error(`Failed to ${action} scheduler`)
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error with scheduler:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to control scheduler' },
      { status: 500 }
    )
  }
}



