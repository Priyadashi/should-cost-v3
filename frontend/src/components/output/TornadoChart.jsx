import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts'

export default function TornadoChart({ sensitivity, baseCost }) {
  if (!sensitivity?.length) return null

  // Group by driver (pair +/- for each driver)
  const drivers = {}
  sensitivity.forEach(s => {
    const baseName = s.driver.replace(/\s*[+-]20%$/, '').trim()
    if (!drivers[baseName]) drivers[baseName] = { name: baseName }
    if (s.driver.includes('+20%')) drivers[baseName].high = s.impact
    if (s.driver.includes('-20%')) drivers[baseName].low = s.impact
  })

  const data = Object.values(drivers)
    .map(d => ({
      ...d,
      low: d.low || 0,
      high: d.high || 0,
      range: Math.abs((d.high || 0) - (d.low || 0)),
    }))
    .sort((a, b) => b.range - a.range)
    .slice(0, 8) // Top 8 drivers

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null
    const d = payload[0].payload
    return (
      <div className="rounded-lg border border-surface-200 bg-white px-3 py-2 shadow-lg text-xs">
        <div className="font-semibold text-surface-700">{d.name}</div>
        <div className="text-red-500 font-mono">-20%: ₹{d.low?.toFixed(2)}</div>
        <div className="text-emerald-600 font-mono">+20%: ₹{d.high?.toFixed(2)}</div>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(200, data.length * 40 + 40)}>
      <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 100, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" horizontal={false} />
        <XAxis type="number" tick={{ fontSize: 11, fill: '#78716c' }} tickFormatter={v => `₹${v}`} />
        <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: '#78716c' }} width={90} />
        <Tooltip content={<CustomTooltip />} />
        <ReferenceLine x={0} stroke="#a8a29e" />
        <Bar dataKey="low" fill="#ef4444" radius={[4, 0, 0, 4]} barSize={16} />
        <Bar dataKey="high" fill="#22c55e" radius={[0, 4, 4, 0]} barSize={16} />
      </BarChart>
    </ResponsiveContainer>
  )
}
