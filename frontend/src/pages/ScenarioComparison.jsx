import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCostSheets, useCompareCostSheets } from '../hooks/useApi'
import ComparisonTable from '../components/output/ComparisonTable'
import WaterfallChart from '../components/output/WaterfallChart'
import { ArrowLeft, GitCompare } from 'lucide-react'

export default function ScenarioComparison() {
  const navigate = useNavigate()
  const { data: sheets = [] } = useCostSheets({ status: 'calculated' })
  const compareMut = useCompareCostSheets()
  const [selectedIds, setSelectedIds] = useState([])
  const [comparisonData, setComparisonData] = useState(null)

  const calculatedSheets = sheets.filter(s => s.result_summary)

  const toggleSheet = (id) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : prev.length < 2 ? [...prev, id] : [prev[1], id]
    )
  }

  const handleCompare = async () => {
    if (selectedIds.length < 2) return
    try {
      const result = await compareMut.mutateAsync(selectedIds)
      setComparisonData(result)
    } catch (err) {
      console.error('Compare failed:', err)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="flex items-center gap-1 rounded-lg border border-surface-200 px-3 py-1.5 text-xs font-medium text-surface-500 hover:bg-surface-50">
          <ArrowLeft size={14} /> Back
        </button>
        <h2 className="text-lg font-semibold text-surface-800">Scenario Comparison</h2>
      </div>

      {/* Sheet selector */}
      <div className="rounded-xl border border-surface-200 bg-white p-5 shadow-subtle">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-surface-700">Select 2 cost sheets to compare</h3>
          <button
            onClick={handleCompare}
            disabled={selectedIds.length < 2 || compareMut.isPending}
            className="flex items-center gap-1.5 rounded-lg bg-brand-500 px-4 py-2 text-xs font-semibold text-white hover:bg-brand-600 disabled:opacity-50"
          >
            <GitCompare size={14} />
            {compareMut.isPending ? 'Comparing...' : 'Compare'}
          </button>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {calculatedSheets.map(sheet => (
            <button
              key={sheet.id}
              onClick={() => toggleSheet(sheet.id)}
              className={`rounded-lg border p-3 text-left transition-colors ${
                selectedIds.includes(sheet.id)
                  ? 'border-brand-400 bg-brand-50'
                  : 'border-surface-200 hover:border-surface-300'
              }`}
            >
              <div className="text-sm font-medium text-surface-700">{sheet.scenario_name}</div>
              <div className="text-xs text-surface-400">{sheet.part_name} ({sheet.part_no})</div>
              <div className="mt-1 text-sm font-mono font-semibold text-brand-600">
                ₹{sheet.result_summary?.should_cost?.toFixed(2)}
              </div>
            </button>
          ))}
        </div>
        {calculatedSheets.length === 0 && (
          <p className="text-sm text-surface-400 text-center py-4">No calculated cost sheets available. Calculate at least 2 to compare.</p>
        )}
      </div>

      {/* Comparison results */}
      {comparisonData && (
        <div className="space-y-6">
          <ComparisonTable sheets={comparisonData.sheets} deltas={comparisonData.deltas} />
        </div>
      )}
    </div>
  )
}
