import Link from 'next/link'
import { fetchEvents } from '@/lib/api'

async function getStats() {
  const allEvents = await fetchEvents({ limit: 1000 })
  const freeEvents = await fetchEvents({ is_free: true, limit: 1000 })
  
  const byCategory: Record<string, number> = {}
  const byVenue: Record<string, number> = {}
  
  allEvents.events.forEach((event) => {
    if (event.category) {
      byCategory[event.category] = (byCategory[event.category] || 0) + 1
    }
    if (event.location) {
      byVenue[event.location] = (byVenue[event.location] || 0) + 1
    }
  })
  
  return {
    total: allEvents.count,
    free: freeEvents.count,
    byCategory,
    byVenue,
  }
}

export default async function StatsPage() {
  const stats = await getStats()
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="text-2xl font-bold text-primary-600">
              Artify
            </Link>
            <nav className="flex gap-6">
              <Link href="/" className="text-gray-700 hover:text-primary-600">
                Événements
              </Link>
              <Link href="/stats" className="text-primary-600 font-medium">
                Statistiques
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Statistiques
          </h1>
          <p className="text-gray-600">
            Vue d'ensemble des événements culturels à Paris
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Total d'événements
            </h2>
            <p className="text-4xl font-bold text-primary-600">{stats.total}</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Événements gratuits
            </h2>
            <p className="text-4xl font-bold text-green-600">{stats.free}</p>
            <p className="text-sm text-gray-500 mt-2">
              {stats.total > 0
                ? `${Math.round((stats.free / stats.total) * 100)}% du total`
                : '0%'}
            </p>
          </div>
        </div>

        {/* By Category */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Par catégorie
          </h2>
          <div className="space-y-3">
            {Object.entries(stats.byCategory)
              .sort((a, b) => b[1] - a[1])
              .map(([category, count]) => (
                <div key={category} className="flex items-center justify-between">
                  <span className="text-gray-700 capitalize">{category}</span>
                  <div className="flex items-center gap-4">
                    <div className="w-48 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full"
                        style={{
                          width: `${
                            (count / stats.total) * 100
                          }%`,
                        }}
                      />
                    </div>
                    <span className="text-gray-900 font-semibold w-12 text-right">
                      {count}
                    </span>
                  </div>
                </div>
              ))}
          </div>
        </div>

        {/* By Venue */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Par lieu
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(stats.byVenue)
              .sort((a, b) => b[1] - a[1])
              .slice(0, 10)
              .map(([venue, count]) => (
                <div
                  key={venue}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <span className="text-gray-700">{venue}</span>
                  <span className="text-primary-600 font-semibold">
                    {count}
                  </span>
                </div>
              ))}
          </div>
        </div>
      </main>
    </div>
  )
}

