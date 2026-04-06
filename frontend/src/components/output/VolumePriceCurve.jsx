import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'

export default function VolumePriceCurve({ volumeAnalysis, baseCost }) {
  if (!volumeAnalysis?.length) return null

  const data = volumeAnalysis.map(v => ({
    volume: v.annual_volume,
    cost: v.should_cost_per_unit,
    label: v.annual_volume >= 1000 ? `${(v.annual_volume / 1000).toFixed(0)}K` : String(v.annual_volume),
  }))

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null
    const d = payload[0].payload
    return (
      <div className="rounded-lg border border-surface-200 bg-white px-3 py-2 shadow-lg text-xs">
        <div className="font-semibold text-surface-700">Volume: {d.volume.toLocaleString()}</div>
        <div className="font-mono text-brand-600">₹{d.cost?.toFixed(2)}/unit</div>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
        <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#78716c' }} />
        <YAxis tick={{ fontSize: 11, fill: '#78716c' }} tickFormatter={v => `₹${v}`} />
        <Tooltip content={<CustomTooltip />} />
        {baseCost > 0 && <ReferenceLine y={baseCost} stroke="#f59e0b" strokeDasharray="5 5" label={{ value: 'Base', fill: '#f59e0b', fontSize: 10 }} />}
        <Line type="monotone" dataKey="cost" stroke="#3b82f6" strokeWidth={2.5} dot={{ fill: '#3b82f6', r: 4 }} activeDot={{ r: 6 }} />
      </LineChart>
    </ResponsiveContainer>
  )
}
