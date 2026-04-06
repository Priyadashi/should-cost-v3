import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'

const COLORS = ['#f59e0b', '#3b82f6', '#6366f1', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#64748b']

export default function CostSplitDonut({ summary }) {
  if (!summary) return null

  const data = [
    { name: 'Material', value: summary.total_material_net },
    { name: 'Conversion', value: summary.total_conversion },
    { name: 'Labor', value: summary.total_labor },
    { name: 'Overhead', value: summary.total_overhead },
    { name: 'Tooling', value: summary.total_tooling_nre },
    { name: 'SGA', value: summary.total_sga },
    { name: 'Profit', value: summary.total_profit },
    { name: 'Logistics', value: summary.total_logistics },
  ].filter(d => d.value > 0)

  const total = data.reduce((s, d) => s + d.value, 0)

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null
    const d = payload[0]
    return (
      <div className="rounded-lg border border-surface-200 bg-white px-3 py-2 shadow-lg text-xs">
        <div className="font-semibold text-surface-700">{d.name}</div>
        <div className="font-mono text-surface-600">₹{d.value?.toFixed(2)} ({(d.value / total * 100).toFixed(1)}%)</div>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-6">
      <ResponsiveContainer width={200} height={200}>
        <PieChart>
          <Pie data={data} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={2} dataKey="value">
            {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>
      <div className="space-y-1.5">
        {data.map((d, i) => (
          <div key={d.name} className="flex items-center gap-2 text-xs">
            <div className="h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
            <span className="text-surface-500 w-20">{d.name}</span>
            <span className="font-mono font-semibold text-surface-700">₹{d.value.toFixed(0)}</span>
            <span className="font-mono text-surface-400">({(d.value / total * 100).toFixed(0)}%)</span>
          </div>
        ))}
      </div>
    </div>
  )
}
