export const COMMODITY_TYPES = ['Forging', 'Casting', 'Fabrication']

export const COST_SHEET_STATUSES = {
  DRAFT: 'draft',
  CALCULATED: 'calculated',
  REVIEWED: 'reviewed',
  FINAL: 'final',
}

export const STATUS_COLORS = {
  draft: { bg: 'bg-surface-100', text: 'text-surface-600' },
  calculated: { bg: 'bg-blue-50', text: 'text-blue-700' },
  reviewed: { bg: 'bg-brand-50', text: 'text-brand-700' },
  final: { bg: 'bg-emerald-50', text: 'text-emerald-700' },
}

export const CONFIDENCE_COLORS = {
  high: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  medium: { bg: 'bg-brand-50', text: 'text-brand-700', border: 'border-brand-200' },
  low: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
}
