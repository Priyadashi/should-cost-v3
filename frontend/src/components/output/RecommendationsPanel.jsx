import { AlertTriangle, TrendingDown, Lightbulb, Target } from 'lucide-react'
import clsx from 'clsx'

const severityConfig = {
  high: { icon: AlertTriangle, bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', badge: 'bg-red-100 text-red-700' },
  medium: { icon: TrendingDown, bg: 'bg-brand-50', border: 'border-brand-200', text: 'text-brand-700', badge: 'bg-brand-100 text-brand-700' },
  low: { icon: Lightbulb, bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', badge: 'bg-blue-100 text-blue-700' },
}

export default function RecommendationsPanel({ recommendations = [] }) {
  if (!recommendations.length) {
    return (
      <div className="rounded-xl border border-surface-200 bg-white p-8 text-center">
        <Target size={24} className="mx-auto text-surface-300 mb-2" />
        <p className="text-sm text-surface-400">No recommendations generated yet. Calculate cost sheet first.</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {recommendations.map((rec, i) => {
        const config = severityConfig[rec.severity] || severityConfig.medium
        const Icon = config.icon
        return (
          <div key={i} className={clsx('rounded-xl border p-4', config.bg, config.border)}>
            <div className="flex items-start gap-3">
              <Icon size={18} className={config.text} />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-semibold text-surface-800">{rec.title}</span>
                  <span className={clsx('rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase', config.badge)}>
                    {rec.severity}
                  </span>
                  {rec.potential_savings_pct > 0 && (
                    <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold text-emerald-700">
                      ~{rec.potential_savings_pct}% savings
                    </span>
                  )}
                </div>
                <p className="text-xs text-surface-600 leading-relaxed">{rec.description}</p>
                <div className="mt-1.5 flex gap-2">
                  <span className="text-[10px] font-medium text-surface-400 bg-surface-100 rounded px-1.5 py-0.5">{rec.category}</span>
                  <span className="text-[10px] font-mono text-surface-400">{rec.rule_id}</span>
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
