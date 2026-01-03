'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { useState } from 'react'

export function DateFilter() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [selectedPreset, setSelectedPreset] = useState<string>('')

  const presets = [
    { label: "Aujourd'hui", value: 'today' },
    { label: 'Ce week-end', value: 'weekend' },
    { label: 'Cette semaine', value: 'week' },
    { label: 'Ce mois', value: 'month' },
  ]

  const getDateRange = (preset: string) => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    switch (preset) {
      case 'today':
        return {
          from: today.toISOString().split('T')[0],
          to: today.toISOString().split('T')[0],
        }
      case 'weekend': {
        const day = today.getDay()
        const saturday = new Date(today)
        saturday.setDate(today.getDate() + (6 - day))
        const sunday = new Date(saturday)
        sunday.setDate(saturday.getDate() + 1)
        return {
          from: saturday.toISOString().split('T')[0],
          to: sunday.toISOString().split('T')[0],
        }
      }
      case 'week': {
        const weekEnd = new Date(today)
        weekEnd.setDate(today.getDate() + 7)
        return {
          from: today.toISOString().split('T')[0],
          to: weekEnd.toISOString().split('T')[0],
        }
      }
      case 'month': {
        const monthEnd = new Date(today.getFullYear(), today.getMonth() + 1, 0)
        return {
          from: today.toISOString().split('T')[0],
          to: monthEnd.toISOString().split('T')[0],
        }
      }
      default:
        return null
    }
  }

  const handlePreset = (preset: string) => {
    const range = getDateRange(preset)
    if (!range) return

    const params = new URLSearchParams(searchParams.toString())
    params.set('date_from', range.from)
    params.set('date_to', range.to)
    setSelectedPreset(preset)
    router.push(`/?${params.toString()}`)
  }

  const clearDates = () => {
    const params = new URLSearchParams(searchParams.toString())
    params.delete('date_from')
    params.delete('date_to')
    setSelectedPreset('')
    router.push(`/?${params.toString()}`)
  }

  return (
    <div className="flex flex-wrap gap-2">
      {presets.map((preset) => (
        <button
          key={preset.value}
          onClick={() => handlePreset(preset.value)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            selectedPreset === preset.value
              ? 'bg-primary-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          {preset.label}
        </button>
      ))}
      {(searchParams.get('date_from') || searchParams.get('date_to')) && (
        <button
          onClick={clearDates}
          className="px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-gray-800"
        >
          Effacer les dates
        </button>
      )}
    </div>
  )
}

