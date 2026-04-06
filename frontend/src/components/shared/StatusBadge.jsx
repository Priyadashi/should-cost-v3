import clsx from 'clsx'
import { STATUS_COLORS, CONFIDENCE_COLORS } from '../../utils/constants'

export function StatusBadge({ status }) {
  const colors = STATUS_COLORS[status] || STATUS_COLORS.draft
  return (
    <span className={clsx('inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-semibold capitalize', colors.bg, colors.text)}>
      {status}
    </span>
  )
}

export function ConfidenceTag({ level }) {
  const colors = CONFIDENCE_COLORS[level?.toLowerCase()] || CONFIDENCE_COLORS.medium
  return (
    <span className={clsx('inline-flex items-center rounded-md border px-1.5 py-0.5 text-[10px] font-semibold uppercase', colors.bg, colors.text, colors.border)}>
      {level}
    </span>
  )
}

export function CurrencyDisplay({ value, currency = 'INR', className }) {
  if (value == null || isNaN(value)) return <span className="text-surface-400">—</span>
  const formatted = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  }).format(value)
  return <span className={clsx('font-mono', className)}>{formatted}</span>
}
