import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts'

export default function WaterfallChart({ summary, currency = 'INR' }) {
  if (!summary) return null

  const data = [
    { name: 'Material', value: summary.total_material_net, fill: '#f59e0b' },
    { name: 'Conversion', value: summary.total_conversion, fill: '#3b82f6' },
    { name: 'Labor', value: summary.total_labor, fill: '#6366f1' },
    { name: 'Overhead', value: summary.total_overhead, fill: '#8b5cf6' },
    { name: 'Tooling', value: summary.total_tooling_nre, fill: '#ec4899' },
    { name: 'SGA', value: summary.total_sga, fill: '#14b8a6' },
    { name: 'Profit', value: summary.total_profit, fill: '#f97316' },
    { name: 'Logistics', value: summary.total_logistics, fill: '#64748b' },
  ].filter(d => d.value > 0)

  // Build waterfall data with invisible base bars
  let running = 0
  const waterfallData = data.map(d => {
    const item = { name: d.name, base: running, value: d.value, fill: d.fill }
    running += d.value
    return item
  })
  // Add total bar
  waterfallData.push({ name: 'Should Cost', base: 0, value: summary.should_cost, fill: '#059669' })

  // If there's a quoted price, add it
  if (summary.current_price > 0) {
    waterfallData.push({ name: 'Quoted', base: 0, value: summary.current_price, fill: '#dc2626' })
  }

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null
    const d = payload[0].payload
    return (
      <div className="rounded-lg border border-surface-200 bg-white px-3 py-2 shadow-lg text-xs">
        <div className="font-semibold text-surface-700">{d.name}</div>
        <div className="font-mono text-surface-600">₹{d.value?.toFixed(2)}</div>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={waterfallData} margin={{ top: 10, right: 10, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
        <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#78716c' }} />
        <YAxis tick={{ fontSize: 11, fill: '#78716c' }} tickFormatter={v => `₹${v}`} />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="base" stackId="a" fill="transparent" />
        <Bar dataKey="value" stackId="a" radius={[4, 4, 0, 0]}>
          {waterfallData.map((entry, i) => (
            <Cell key={i} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
