import Link from 'next/link'
import { EventCard } from '@/components/EventCard'
import { EventFilters } from '@/components/EventFilters'
import { SearchBar } from '@/components/SearchBar'
import { FreeEventsSection } from '@/components/FreeEventsSection'
import { fetchEvents } from '@/lib/api'
import { searchEvents } from '@/lib/search'

export default async function HomePage({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  const dateFrom = searchParams.date_from as string | undefined
  const dateTo = searchParams.date_to as string | undefined
  const category = searchParams.category as string | undefined
  const venue = searchParams.venue as string | undefined
  const isFree = searchParams.is_free === 'true' ? true : undefined
  const searchQuery = searchParams.search as string | undefined

  // Use search if query exists, otherwise use regular fetch
  let events, total
  if (searchQuery) {
    const searchResult = await searchEvents(searchQuery, {
      category,
      venue,
      is_free: isFree,
      date_from: dateFrom,
      date_to: dateTo,
    })
    events = searchResult.events
    total = searchResult.total
  } else {
    const result = await fetchEvents({
      date_from: dateFrom,
      date_to: dateTo,
      category,
      venue,
      is_free: isFree,
      limit: 50,
    })
    events = result.events
    total = result.count
  }

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
              <Link href="/stats" className="text-gray-700 hover:text-primary-600">
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
            Événements Culturels à Paris
          </h1>
          <p className="text-gray-600 mb-6">
            Découvrez les meilleurs événements culturels de la capitale
          </p>
          
          {/* Search Bar */}
          <div className="mb-6">
            <SearchBar />
          </div>
        </div>

        {/* Free Events Section - only show if no filters active */}
        {!searchQuery && !category && !venue && !isFree && !dateFrom && (
          <FreeEventsSection />
        )}

        {/* Filters */}
        <EventFilters />
        
        {/* Results count */}
        {events.length > 0 && (
          <div className="mb-4 flex items-center justify-between">
            <div className="text-sm text-gray-600">
              <span className="font-semibold text-gray-900">{total}</span> événement{total > 1 ? 's' : ''} trouvé{total > 1 ? 's' : ''}
              {searchQuery && (
                <span className="ml-2">
                  pour <span className="font-medium">"{searchQuery}"</span>
                </span>
              )}
            </div>
            {isFree && (
              <div className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                Événements gratuits uniquement
              </div>
            )}
          </div>
        )}

        {/* Events Grid */}
        {events.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
            {events.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">
              Aucun événement trouvé. Essayez de modifier vos filtres.
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Artify
              </h3>
              <p className="text-gray-600 text-sm">
                Votre guide des événements culturels à Paris. Découvrez les meilleurs expositions, concerts, spectacles et plus encore.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Navigation
              </h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href="/" className="text-gray-600 hover:text-primary-600">
                    Événements
                  </Link>
                </li>
                <li>
                  <Link href="/stats" className="text-gray-600 hover:text-primary-600">
                    Statistiques
                  </Link>
                </li>
                <li>
                  <Link href="/?is_free=true" className="text-gray-600 hover:text-primary-600">
                    Événements gratuits
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Informations
              </h3>
              <p className="text-gray-600 text-sm">
                Tous les événements sont collectés depuis les sites officiels des institutions culturelles parisiennes.
              </p>
            </div>
          </div>
          <div className="border-t pt-8">
            <p className="text-center text-gray-500 text-sm">
              © 2025 Artify - Tous droits réservés | Plateforme d'agrégation d'événements culturels à Paris
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

