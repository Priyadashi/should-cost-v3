export function formatCurrency(value, currency = 'INR') {
  if (value == null || isNaN(value)) return '—'
  const formatter = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
  return formatter.format(value)
}

export function formatNumber(value, decimals = 2) {
  if (value == null || isNaN(value)) return '—'
  return new Intl.NumberFormat('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

export function formatPercent(value, decimals = 1) {
  if (value == null || isNaN(value)) return '—'
  return `${value.toFixed(decimals)}%`
}
