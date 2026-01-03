import { notFound } from 'next/navigation'
import Link from 'next/link'
import { fetchEvent } from '@/lib/api'
import { EventBadge } from '@/components/EventBadge'
import { PriceDisplay } from '@/components/PriceDisplay'

export default async function EventDetailPage({
  params,
}: {
  params: { id: string }
}) {
  const event = await fetchEvent(params.id)

  if (!event) {
    notFound()
  }

  const startDate = new Date(event.start_date)
  const endDate = event.end_date ? new Date(event.end_date) : null

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="text-2xl font-bold text-primary-600">
              Artify
            </Link>
            <Link
              href="/"
              className="text-gray-700 hover:text-primary-600"
            >
              ← Retour aux événements
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <article className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Event Image */}
          {event.image_url && (
            <div className="relative h-96 w-full">
              <img
                src={event.image_url}
                alt={event.title}
                className="w-full h-full object-cover"
              />
              <div className="absolute top-4 right-4">
                <EventBadge
                  variant={event.is_free ? 'free' : 'paid'}
                  size="lg"
                />
              </div>
            </div>
          )}

          <div className="p-8">
            {/* Title and Category */}
            <div className="mb-4">
              {event.category && (
                <span className="inline-block px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium mb-2">
                  {event.category}
                </span>
              )}
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                {event.title}
              </h1>
            </div>

            {/* Date and Location */}
            <div className="mb-6 space-y-2">
              <div className="flex items-center text-gray-600">
                <svg
                  className="w-5 h-5 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <span>
                  {startDate.toLocaleDateString('fr-FR', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                  {endDate &&
                    ` - ${endDate.toLocaleDateString('fr-FR', {
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}`}
                </span>
              </div>
              <div className="flex items-center text-gray-600">
                <svg
                  className="w-5 h-5 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
                <span>{event.location}</span>
                {event.address && <span className="ml-2 text-gray-500">- {event.address}</span>}
              </div>
            </div>

            {/* Price */}
            <div className="mb-6">
              <PriceDisplay
                isFree={event.is_free}
                price={event.price}
                priceMin={event.price_min}
                priceMax={event.price_max}
                currency={event.currency}
              />
            </div>

            {/* Description */}
            {event.description && (
              <div className="mb-6">
                <h2 className="text-2xl font-semibold text-gray-900 mb-3">
                  Description
                </h2>
                <p className="text-gray-700 whitespace-pre-line">
                  {event.description}
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-4">
              {event.ticket_url && (
                <a
                  href={event.ticket_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
                >
                  Acheter des billets
                </a>
              )}
              {event.source_url && (
                <a
                  href={event.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                >
                  Voir sur le site source
                </a>
              )}
            </div>
          </div>
        </article>
      </main>
    </div>
  )
}

