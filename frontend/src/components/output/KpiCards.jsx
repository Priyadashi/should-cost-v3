import clsx from 'clsx'

export default function KpiCards({ summary, supplierName, currency = 'INR' }) {
  if (!summary) return null

  const cards = [
    { label: 'Should Cost', value: `₹${summary.should_cost?.toFixed(2)}`, sub: 'Per unit', color: 'brand' },
    { label: 'Quoted Price', value: `₹${summary.current_price?.toFixed(2)}`, sub: supplierName || 'Supplier quote', color: 'surface' },
    {
      label: 'Gap',
      value: `${summary.gap > 0 ? '+' : ''}₹${summary.gap?.toFixed(2)}`,
      sub: `${summary.gap_pct?.toFixed(1)}% ${summary.gap > 0 ? 'savings potential' : 'underpriced'}`,
      color: summary.gap > 0 ? 'emerald' : 'red',
    },
    {
      label: 'Annual Opportunity',
      value: `₹${(summary.annual_opportunity || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`,
      sub: `${summary.annual_volume?.toLocaleString()} units/year`,
      color: 'blue',
    },
  ]

  const colorMap = {
    brand: 'border-brand-200 bg-brand-50',
    surface: 'border-surface-200 bg-white',
    emerald: 'border-emerald-200 bg-emerald-50',
    red: 'border-red-200 bg-red-50',
    blue: 'border-blue-200 bg-blue-50',
  }
  const textMap = {
    brand: 'text-brand-700',
    surface: 'text-surface-700',
    emerald: 'text-emerald-700',
    red: 'text-red-700',
    blue: 'text-blue-700',
  }

  return (
    <div className="grid grid-cols-4 gap-4">
      {cards.map(card => (
        <div key={card.label} className={clsx('rounded-xl border p-4', colorMap[card.color])}>
          <div className="text-[10px] font-semibold uppercase tracking-wider text-surface-400 mb-1">{card.label}</div>
          <div className={clsx('text-xl font-bold font-mono', textMap[card.color])}>{card.value}</div>
          <div className="text-[11px] text-surface-500 mt-0.5">{card.sub}</div>
        </div>
      ))}
    </div>
  )
}
