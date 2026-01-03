/**
 * PriceDisplay Component
 * Displays event pricing information with proper formatting
 */

interface PriceDisplayProps {
  isFree: boolean
  price?: number | null
  priceMin?: number | null
  priceMax?: number | null
  currency?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function PriceDisplay({
  isFree,
  price,
  priceMin,
  priceMax,
  currency = 'EUR',
  size = 'md',
  className = '',
}: PriceDisplayProps) {
  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
  }[size]

  const formatPrice = (amount: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(amount)
  }

  if (isFree) {
    return (
      <span className={`font-semibold text-green-600 ${sizeClasses} ${className}`}>
        Gratuit
      </span>
    )
  }

  if (price !== null && price !== undefined) {
    return (
      <span className={`font-semibold text-gray-900 ${sizeClasses} ${className}`}>
        {formatPrice(price)}
      </span>
    )
  }

  if (priceMin !== null && priceMin !== undefined) {
    if (priceMax !== null && priceMax !== undefined && priceMax !== priceMin) {
      return (
        <span className={`font-semibold text-gray-900 ${sizeClasses} ${className}`}>
          {formatPrice(priceMin)} - {formatPrice(priceMax)}
        </span>
      )
    }
    return (
      <span className={`font-semibold text-gray-900 ${sizeClasses} ${className}`}>
        À partir de {formatPrice(priceMin)}
      </span>
    )
  }

  return (
    <span className={`text-gray-500 ${sizeClasses} ${className}`}>
      Prix non disponible
    </span>
  )
}

