/**
 * EventBadge Component
 * Displays a visual badge for event pricing status
 */

export type BadgeVariant = 'free' | 'paid' | 'range'
export type BadgeSize = 'sm' | 'md' | 'lg'

interface EventBadgeProps {
  variant: BadgeVariant
  size?: BadgeSize
  className?: string
}

const BADGE_VARIANTS = {
  free: {
    text: 'GRATUIT',
    classes: 'bg-green-500 text-white font-bold shadow-sm ring-1 ring-green-600',
    ariaLabel: 'Événement gratuit',
  },
  paid: {
    text: 'PAYANT',
    classes: 'bg-slate-100 text-slate-700 font-medium ring-1 ring-slate-200',
    ariaLabel: 'Événement payant',
  },
  range: {
    text: 'À PARTIR DE',
    classes: 'bg-blue-100 text-blue-700 font-medium ring-1 ring-blue-200',
    ariaLabel: 'Gamme de prix disponible',
  },
}

const BADGE_SIZES = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base',
}

export function EventBadge({
  variant,
  size = 'md',
  className = '',
}: EventBadgeProps) {
  const variantConfig = BADGE_VARIANTS[variant]
  const sizeClasses = BADGE_SIZES[size]

  return (
    <span
      className={`
        inline-flex items-center justify-center
        rounded-full
        uppercase tracking-wide
        ${variantConfig.classes}
        ${sizeClasses}
        ${className}
      `.trim()}
      role="status"
      aria-label={variantConfig.ariaLabel}
    >
      {variantConfig.text}
    </span>
  )
}

