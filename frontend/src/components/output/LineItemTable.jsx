import { ConfidenceTag } from '../shared/StatusBadge'

export default function LineItemTable({ lineItems = [] }) {
  if (!lineItems.length) return <div className="text-sm text-surface-400 p-4">No line items</div>

  // Group by category
  const groups = {}
  lineItems.forEach(item => {
    if (!groups[item.category]) groups[item.category] = []
    groups[item.category].push(item)
  })

  const total = lineItems.reduce((s, i) => s + i.value, 0)

  return (
    <div className="rounded-xl border border-surface-200 bg-white shadow-subtle overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="bg-surface-50 border-b border-surface-100">
            {['Category', 'Item', 'Value (₹)', 'Detail', 'Source', 'Confidence'].map(h => (
              <th key={h} className="px-4 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wider text-surface-400">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Object.entries(groups).map(([category, items]) => (
            items.map((item, i) => (
              <tr key={`${category}-${i}`} className="border-b border-surface-100 last:border-0 hover:bg-surface-50/50">
                <td className="px-4 py-2.5 text-xs font-semibold text-surface-500">{i === 0 ? category : ''}</td>
                <td className="px-4 py-2.5 text-sm text-surface-700">{item.item}</td>
                <td className="px-4 py-2.5 text-sm font-mono font-semibold text-surface-700">
                  {item.value < 0 ? <span className="text-emerald-600">{item.value.toFixed(2)}</span> : item.value.toFixed(2)}
                </td>
                <td className="px-4 py-2.5 text-xs text-surface-500 max-w-xs truncate" title={item.detail}>{item.detail}</td>
                <td className="px-4 py-2.5 text-xs text-surface-400">{item.source}</td>
                <td className="px-4 py-2.5"><ConfidenceTag level={item.confidence} /></td>
              </tr>
            ))
          ))}
        </tbody>
        <tfoot>
          <tr className="bg-surface-50 border-t border-surface-200">
            <td colSpan={2} className="px-4 py-3 text-sm font-bold text-surface-700">TOTAL SHOULD COST</td>
            <td className="px-4 py-3 text-base font-bold font-mono text-brand-600">₹{total.toFixed(2)}</td>
            <td colSpan={3}></td>
          </tr>
        </tfoot>
      </table>
    </div>
  )
}
