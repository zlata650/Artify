import Link from 'next/link'
import { EventBadge } from './EventBadge'
import { PriceDisplay } from './PriceDisplay'
import type { Event } from '@/lib/api'

interface EventCardProps {
  event: Event
}

export function EventCard({ event }: EventCardProps) {
  const startDate = new Date(event.start_date)

  return (
    <Link
      href={`/events/${event.id}`}
      className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-200"
    >
      {/* Image */}
      {event.image_url ? (
        <div className="relative h-48 w-full">
          <img
            src={event.image_url}
            alt={event.title}
            className="w-full h-full object-cover"
          />
          <div className="absolute top-2 right-2">
            <EventBadge
              variant={event.is_free ? 'free' : 'paid'}
              size="sm"
            />
          </div>
        </div>
      ) : (
        <div className="relative h-48 w-full bg-gray-200 flex items-center justify-center">
          <div className="absolute top-2 right-2">
            <EventBadge
              variant={event.is_free ? 'free' : 'paid'}
              size="sm"
            />
          </div>
          <svg
            className="w-16 h-16 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>
      )}

      {/* Content */}
      <div className="p-4">
        {event.category && (
          <span className="inline-block px-2 py-1 bg-primary-100 text-primary-700 rounded text-xs font-medium mb-2">
            {event.category}
          </span>
        )}
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
          {event.title}
        </h3>
        <div className="flex items-center text-sm text-gray-600 mb-2">
          <svg
            className="w-4 h-4 mr-1"
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
              day: 'numeric',
              month: 'short',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>
        <div className="flex items-center text-sm text-gray-600 mb-3">
          <svg
            className="w-4 h-4 mr-1"
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
          <span className="truncate">{event.location}</span>
        </div>
        <div className="mt-3">
          <PriceDisplay
            isFree={event.is_free}
            price={event.price}
            priceMin={event.price_min}
            priceMax={event.price_max}
            currency={event.currency}
            size="sm"
          />
        </div>
      </div>
    </Link>
  )
}

