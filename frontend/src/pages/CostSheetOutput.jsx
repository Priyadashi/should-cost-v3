import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useCostSheet } from '../hooks/useApi'
import KpiCards from '../components/output/KpiCards'
import WaterfallChart from '../components/output/WaterfallChart'
import CostSplitDonut from '../components/output/CostSplitDonut'
import LineItemTable from '../components/output/LineItemTable'
import TornadoChart from '../components/output/TornadoChart'
import VolumePriceCurve from '../components/output/VolumePriceCurve'
import RecommendationsPanel from '../components/output/RecommendationsPanel'
import { ArrowLeft, Download, RefreshCw, GitCompare, Sparkles } from 'lucide-react'
import clsx from 'clsx'

const TABS = [
  { id: 'summary', label: 'Summary' },
  { id: 'detail', label: 'Detail' },
  { id: 'sensitivity', label: 'Sensitivity' },
  { id: 'recommendations', label: 'Recommendations' },
]

export default function CostSheetOutput() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { data: sheet, isLoading } = useCostSheet(id)
  const [activeTab, setActiveTab] = useState('summary')

  if (isLoading) {
    return <div className="flex items-center justify-center h-64 text-sm text-surface-400">Loading cost sheet...</div>
  }

  if (!sheet) {
    return <div className="flex items-center justify-center h-64 text-sm text-surface-400">Cost sheet not found</div>
  }

  const summary = sheet.result_summary
  const lineItems = sheet.result_line_items || []
  const sensitivity = sheet.sensitivity || []
  const volumeAnalysis = sheet.volume_analysis || []
  const recommendations = sheet.recommendations || []

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/cost-sheets')} className="flex items-center gap-1 rounded-lg border border-surface-200 px-3 py-1.5 text-xs font-medium text-surface-500 hover:bg-surface-50">
            <ArrowLeft size={14} /> Back
          </button>
          <div>
            <h2 className="text-lg font-semibold text-surface-800">{sheet.scenario_name}</h2>
            <p className="text-xs text-surface-400">{sheet.part_name} ({sheet.part_no})</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1.5 rounded-lg border border-surface-200 px-3 py-1.5 text-xs font-medium text-surface-500 hover:bg-surface-50">
            <Download size={14} /> Export Excel
          </button>
          <button onClick={() => navigate(`/cost-sheets/${id}/edit`)} className="flex items-center gap-1.5 rounded-lg border border-surface-200 px-3 py-1.5 text-xs font-medium text-surface-500 hover:bg-surface-50">
            <RefreshCw size={14} /> Edit & Recalculate
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <KpiCards summary={summary} />

      {/* Tabs */}
      <div className="flex border-b border-surface-200">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={clsx(
              'px-4 py-2.5 text-xs font-semibold uppercase tracking-wider border-b-2 transition-colors',
              activeTab === tab.id
                ? 'border-brand-500 text-brand-600'
                : 'border-transparent text-surface-400 hover:text-surface-600'
            )}
          >
            {tab.label}
            {tab.id === 'recommendations' && recommendations.length > 0 && (
              <span className="ml-1.5 inline-flex h-4 w-4 items-center justify-center rounded-full bg-brand-100 text-[10px] font-bold text-brand-700">
                {recommendations.length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'summary' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <div className="rounded-xl border border-surface-200 bg-white p-5 shadow-subtle">
              <h3 className="mb-4 text-sm font-semibold text-surface-700">Cost Waterfall</h3>
              <WaterfallChart summary={summary} />
            </div>
            <div className="rounded-xl border border-surface-200 bg-white p-5 shadow-subtle">
              <h3 className="mb-4 text-sm font-semibold text-surface-700">Cost Split</h3>
              <CostSplitDonut summary={summary} />
            </div>
          </div>
        </div>
      )}

      {activeTab === 'detail' && (
        <LineItemTable lineItems={lineItems} />
      )}

      {activeTab === 'sensitivity' && (
        <div className="space-y-6">
          <div className="rounded-xl border border-surface-200 bg-white p-5 shadow-subtle">
            <h3 className="mb-4 text-sm font-semibold text-surface-700">Sensitivity Analysis (±20%)</h3>
            <TornadoChart sensitivity={sensitivity} baseCost={summary?.should_cost} />
          </div>
          <div className="rounded-xl border border-surface-200 bg-white p-5 shadow-subtle">
            <h3 className="mb-4 text-sm font-semibold text-surface-700">Volume-Price Curve</h3>
            <VolumePriceCurve volumeAnalysis={volumeAnalysis} baseCost={summary?.should_cost} />
          </div>
          {/* Volume analysis table */}
          <div className="rounded-xl border border-surface-200 bg-white shadow-subtle overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="bg-surface-50 border-b border-surface-100">
                  {['Volume', 'Batch Size', 'Cost/Unit', 'Delta', 'Delta %'].map(h => (
                    <th key={h} className="px-4 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wider text-surface-400">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {volumeAnalysis.map((va, i) => (
                  <tr key={i} className="border-b border-surface-100 last:border-0">
                    <td className="px-4 py-2.5 text-sm font-mono">{va.annual_volume?.toLocaleString()}</td>
                    <td className="px-4 py-2.5 text-sm font-mono">{va.batch_size}</td>
                    <td className="px-4 py-2.5 text-sm font-mono font-semibold">₹{va.should_cost_per_unit?.toFixed(2)}</td>
                    <td className={clsx('px-4 py-2.5 text-sm font-mono font-semibold', va.delta_vs_base < 0 ? 'text-emerald-600' : va.delta_vs_base > 0 ? 'text-red-500' : '')}>
                      {va.delta_vs_base !== 0 ? `${va.delta_vs_base > 0 ? '+' : ''}₹${va.delta_vs_base?.toFixed(2)}` : '—'}
                    </td>
                    <td className={clsx('px-4 py-2.5 text-sm font-mono font-semibold', va.delta_pct < 0 ? 'text-emerald-600' : va.delta_pct > 0 ? 'text-red-500' : '')}>
                      {va.delta_pct !== 0 ? `${va.delta_pct > 0 ? '+' : ''}${va.delta_pct?.toFixed(1)}%` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'recommendations' && (
        <div className="space-y-4">
          <RecommendationsPanel recommendations={recommendations} />
          {/* AI Analysis placeholder */}
          <div className="rounded-xl border border-dashed border-surface-300 bg-surface-50 p-6 text-center">
            <Sparkles size={24} className="mx-auto text-surface-300 mb-2" />
            <h3 className="text-sm font-semibold text-surface-600 mb-1">AI-Powered Analysis</h3>
            <p className="text-xs text-surface-400 mb-3">Get deeper insights with GPT-powered analysis of your cost model</p>
            <button className="inline-flex items-center gap-1.5 rounded-lg bg-surface-200 px-4 py-2 text-xs font-medium text-surface-600 hover:bg-surface-300 transition-colors" disabled>
              <Sparkles size={14} /> Generate AI Analysis
            </button>
            <p className="text-[10px] text-surface-400 mt-2">Requires OpenAI API key in settings</p>
          </div>
        </div>
      )}
    </div>
  )
}
