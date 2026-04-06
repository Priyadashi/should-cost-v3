import clsx from 'clsx'

export default function ComparisonTable({ sheets = [], deltas = [] }) {
  if (sheets.length < 2) return null

  const [a, b] = sheets
  const delta = deltas[0]?.deltas || {}

  const rows = [
    { label: 'Material Cost', key: 'total_material_net' },
    { label: 'Conversion Cost', key: 'total_conversion' },
    { label: 'Labor Cost', key: 'total_labor' },
    { label: 'Tooling/NRE', key: 'total_tooling_nre' },
    { label: 'Overhead', key: 'total_overhead' },
    { label: 'SGA', key: 'total_sga' },
    { label: 'Profit', key: 'total_profit' },
    { label: 'Logistics', key: 'total_logistics' },
    { label: 'Should Cost', key: 'should_cost', bold: true },
    { label: 'Gap %', key: 'gap_pct' },
    { label: 'Annual Opportunity', key: 'annual_opportunity' },
  ]

  return (
    <div className="rounded-xl border border-surface-200 bg-white shadow-subtle overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="bg-surface-50 border-b border-surface-100">
            <th className="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-surface-400">Cost Element</th>
            <th className="px-4 py-3 text-right text-[11px] font-semibold uppercase tracking-wider text-brand-600">{a.scenario_name}</th>
            <th className="px-4 py-3 text-right text-[11px] font-semibold uppercase tracking-wider text-blue-600">{b.scenario_name}</th>
            <th className="px-4 py-3 text-right text-[11px] font-semibold uppercase tracking-wider text-surface-400">Diff (₹)</th>
            <th className="px-4 py-3 text-right text-[11px] font-semibold uppercase tracking-wider text-surface-400">Diff (%)</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(({ label, key, bold }) => {
            const av = a.summary?.[key] ?? 0
            const bv = b.summary?.[key] ?? 0
            const d = bv - av
            const pct = av !== 0 ? (d / av * 100) : 0
            const diffColor = d < 0 ? 'text-emerald-600' : d > 0 ? 'text-red-500' : 'text-surface-400'

            return (
              <tr key={key} className={clsx('border-b border-surface-100 last:border-0', bold && 'bg-surface-50')}>
                <td className={clsx('px-4 py-2.5 text-sm', bold ? 'font-bold text-surface-800' : 'text-surface-600')}>{label}</td>
                <td className={clsx('px-4 py-2.5 text-right font-mono', bold ? 'text-base font-bold text-brand-700' : 'text-sm text-surface-700')}>
                  {key === 'gap_pct' ? `${av?.toFixed(1)}%` : `₹${av?.toFixed(2)}`}
                </td>
                <td className={clsx('px-4 py-2.5 text-right font-mono', bold ? 'text-base font-bold text-blue-700' : 'text-sm text-surface-700')}>
                  {key === 'gap_pct' ? `${bv?.toFixed(1)}%` : `₹${bv?.toFixed(2)}`}
                </td>
                <td className={clsx('px-4 py-2.5 text-right text-sm font-mono font-semibold', diffColor)}>
                  {d !== 0 ? `${d > 0 ? '+' : ''}₹${d.toFixed(2)}` : '—'}
                </td>
                <td className={clsx('px-4 py-2.5 text-right text-sm font-mono font-semibold', diffColor)}>
                  {pct !== 0 ? `${pct > 0 ? '+' : ''}${pct.toFixed(1)}%` : '—'}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
