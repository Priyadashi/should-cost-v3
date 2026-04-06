import { useNavigate } from 'react-router-dom'
import { useDashboardSummary, useRecentActivity } from '../hooks/useApi'
import { StatusBadge, CurrencyDisplay } from '../components/shared/StatusBadge'
import {
  FileSpreadsheet, Package, Database, Wrench, TrendingUp, Plus,
  ArrowRight, Clock
} from 'lucide-react'
import { formatCurrency } from '../utils/formatCurrency'

function StatCard({ icon: Icon, label, value, sub, color = 'brand' }) {
  const colorMap = {
    brand: 'bg-brand-50 text-brand-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    blue: 'bg-blue-50 text-blue-600',
    purple: 'bg-purple-50 text-purple-600',
  }
  return (
    <div className="rounded-xl border border-surface-200 bg-white p-5 shadow-subtle">
      <div className="flex items-center gap-3">
        <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${colorMap[color]}`}>
          <Icon size={18} />
        </div>
        <div>
          <div className="text-2xl font-bold text-surface-800 font-mono">{value}</div>
          <div className="text-xs text-surface-400">{label}</div>
        </div>
      </div>
      {sub && <div className="mt-2 text-xs text-surface-500">{sub}</div>}
    </div>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()
  const { data: summary, isLoading: loadingSummary } = useDashboardSummary()
  const { data: activity, isLoading: loadingActivity } = useRecentActivity(8)

  const s = summary || {}

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard icon={FileSpreadsheet} label="Cost Sheets" value={s.total_cost_sheets ?? '—'} sub={`${s.calculated_sheets ?? 0} calculated, ${s.draft_sheets ?? 0} draft`} />
        <StatCard icon={Package} label="Parts" value={s.total_parts ?? '—'} color="blue" />
        <StatCard icon={Database} label="Materials" value={s.total_materials ?? '—'} color="purple" />
        <StatCard icon={TrendingUp} label="Annual Opportunity" value={s.total_annual_opportunity ? formatCurrency(s.total_annual_opportunity) : '—'} color="emerald" />
      </div>

      {/* Quick Actions */}
      <div className="rounded-xl border border-surface-200 bg-white p-5 shadow-subtle">
        <h3 className="mb-3 text-sm font-semibold text-surface-700">Quick Actions</h3>
        <div className="flex gap-3">
          <button onClick={() => navigate('/cost-sheets/new')} className="flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-600 transition-colors">
            <Plus size={16} /> New Cost Sheet
          </button>
          <button onClick={() => navigate('/excel-upload')} className="flex items-center gap-2 rounded-lg border border-surface-200 px-4 py-2.5 text-sm font-medium text-surface-600 hover:bg-surface-50 transition-colors">
            Import Excel
          </button>
          <button onClick={() => navigate('/cost-sheets')} className="flex items-center gap-2 rounded-lg border border-surface-200 px-4 py-2.5 text-sm font-medium text-surface-600 hover:bg-surface-50 transition-colors">
            View All Sheets <ArrowRight size={14} />
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="rounded-xl border border-surface-200 bg-white shadow-subtle">
        <div className="flex items-center justify-between border-b border-surface-100 px-5 py-3">
          <h3 className="text-sm font-semibold text-surface-700">Recent Activity</h3>
          <button onClick={() => navigate('/cost-sheets')} className="text-xs font-medium text-brand-600 hover:text-brand-700">
            View all
          </button>
        </div>
        <div className="divide-y divide-surface-100">
          {loadingActivity ? (
            <div className="px-5 py-8 text-center text-sm text-surface-400">Loading...</div>
          ) : !activity?.length ? (
            <div className="px-5 py-8 text-center text-sm text-surface-400">
              No activity yet. Create your first cost sheet to get started.
            </div>
          ) : (
            activity.map((item) => (
              <div
                key={item.id}
                onClick={() => item.status === 'calculated' ? navigate(`/cost-sheets/${item.id}/output`) : navigate(`/cost-sheets/${item.id}/edit`)}
                className="flex items-center justify-between px-5 py-3 cursor-pointer hover:bg-surface-50/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <FileSpreadsheet size={16} className="text-surface-400" />
                  <div>
                    <div className="text-sm font-medium text-surface-700">{item.scenario_name}</div>
                    <div className="text-xs text-surface-400">{item.part_name} ({item.part_no})</div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  {item.should_cost && (
                    <CurrencyDisplay value={item.should_cost} className="text-sm font-semibold text-surface-700" />
                  )}
                  {item.gap_pct != null && (
                    <span className={`text-xs font-semibold font-mono ${item.gap_pct > 0 ? 'text-emerald-600' : item.gap_pct < 0 ? 'text-red-500' : 'text-surface-400'}`}>
                      {item.gap_pct > 0 ? '+' : ''}{item.gap_pct}%
                    </span>
                  )}
                  <StatusBadge status={item.status} />
                  {item.updated_at && (
                    <span className="flex items-center gap-1 text-[11px] text-surface-400">
                      <Clock size={11} />
                      {new Date(item.updated_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
