'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { fetchCategories, fetchVenues } from '@/lib/api'
import { DateFilter } from './DateFilter'

export function EventFilters() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [categories, setCategories] = useState<string[]>([])
  const [venues, setVenues] = useState<string[]>([])
  const [isFree, setIsFree] = useState(searchParams.get('is_free') === 'true')
  const [selectedCategory, setSelectedCategory] = useState(
    searchParams.get('category') || ''
  )
  const [selectedVenue, setSelectedVenue] = useState(
    searchParams.get('venue') || ''
  )

  useEffect(() => {
    fetchCategories().then(setCategories).catch(console.error)
    fetchVenues().then(setVenues).catch(console.error)
  }, [])

  const updateFilters = () => {
    const params = new URLSearchParams()
    
    if (isFree) params.set('is_free', 'true')
    if (selectedCategory) params.set('category', selectedCategory)
    if (selectedVenue) params.set('venue', selectedVenue)

    router.push(`/?${params.toString()}`)
  }

  const clearFilters = () => {
    setIsFree(false)
    setSelectedCategory('')
    setSelectedVenue('')
    router.push('/')
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Filtres</h2>
        <button
          onClick={clearFilters}
          className="text-sm text-primary-600 hover:text-primary-700"
        >
          Réinitialiser
        </button>
      </div>

      {/* Date Presets */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Période
        </label>
        <DateFilter />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Free Events Filter */}
        <div>
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={isFree}
              onChange={(e) => {
                setIsFree(e.target.checked)
                setTimeout(updateFilters, 100)
              }}
              className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
            />
            <span className="ml-2 text-gray-700 font-medium">
              Événements gratuits uniquement
            </span>
          </label>
        </div>

        {/* Category Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Catégorie
          </label>
          <select
            value={selectedCategory}
            onChange={(e) => {
              setSelectedCategory(e.target.value)
              setTimeout(updateFilters, 100)
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">Toutes les catégories</option>
            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>

        {/* Venue Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Lieu
          </label>
          <select
            value={selectedVenue}
            onChange={(e) => {
              setSelectedVenue(e.target.value)
              setTimeout(updateFilters, 100)
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">Tous les lieux</option>
            {venues.map((venue) => (
              <option key={venue} value={venue}>
                {venue}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  )
}

