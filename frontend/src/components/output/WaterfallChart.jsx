import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts'

export default function WaterfallChart({ summary, currency = 'INR' }) {
  if (!summary) return null

  const COLORS = {
    Material: '#475569',   // Slate
    Conversion: '#2563eb', // Blue
    Labor: '#0284c7',      // Sky
    Overhead: '#059669',   // Emerald
    Tooling: '#8b5cf6',    // Violet
    SGA: '#d97706',        // Amber
    Profit: '#0f766e',     // Teal
    Logistics: '#be123c',  // Rose
  }

  const data = [
    { name: 'Material', value: summary.total_material_net, fill: COLORS.Material },
    { name: 'Conversion', value: summary.total_conversion, fill: COLORS.Conversion },
    { name: 'Labor', value: summary.total_labor, fill: COLORS.Labor },
    { name: 'Overhead', value: summary.total_overhead, fill: COLORS.Overhead },
    { name: 'Tooling', value: summary.total_tooling_nre, fill: COLORS.Tooling },
    { name: 'SGA', value: summary.total_sga, fill: COLORS.SGA },
    { name: 'Profit', value: summary.total_profit, fill: COLORS.Profit },
    { name: 'Logistics', value: summary.total_logistics, fill: COLORS.Logistics },
  ].filter(d => d.value > 0)

  // Build waterfall data using array [bottom, top]
  let running = 0
  const waterfallData = data.map(d => {
    const item = { name: d.name, val: [running, running + d.value], value: d.value, fill: d.fill }
    running += d.value
    return item
  })
  // Add total bar
  waterfallData.push({ name: 'Should Cost', val: [0, summary.should_cost], value: summary.should_cost, fill: '#334155' })

  // If there's a quoted price, add it
  if (summary.current_price > 0) {
    waterfallData.push({ name: 'Quoted', val: [0, summary.current_price], value: summary.current_price, fill: '#94a3b8' })
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
        <CartesianGrid strokeDasharray="3 3" stroke="#f5f5f4" vertical={false} />
        <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748b' }} axisLine={{ stroke: '#cbd5e1' }} tickLine={false} />
        <YAxis tick={{ fontSize: 10, fill: '#64748b' }} axisLine={{ stroke: '#cbd5e1' }} tickLine={false} tickFormatter={v => `₹${v}`} />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: '#f8fafc' }} />
        <Bar dataKey="val" radius={[2, 2, 2, 2]} isAnimationActive={false}>
          {waterfallData.map((entry, i) => (
            <Cell key={i} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
