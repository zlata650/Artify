import Link from 'next/link'
import { EventCard } from './EventCard'
import { fetchEvents } from '@/lib/api'

export async function FreeEventsSection() {
  const { events } = await fetchEvents({
    is_free: true,
    limit: 6,
  })

  if (events.length === 0) {
    return null
  }

  return (
    <section className="mb-12">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Événements Gratuits
          </h2>
          <p className="text-gray-600">
            Découvrez les meilleurs événements culturels gratuits à Paris
          </p>
        </div>
        <Link
          href="/?is_free=true"
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          Voir tous →
        </Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {events.slice(0, 3).map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>
    </section>
  )
}

