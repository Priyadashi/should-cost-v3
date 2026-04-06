import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, FileSpreadsheet, Package, Cog, Upload,
  Database, Wrench, GitBranch, Building2, Percent
} from 'lucide-react'
import clsx from 'clsx'

const nav = [
  { section: 'Overview', items: [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/cost-sheets', label: 'Cost Sheets', icon: FileSpreadsheet },
  ]},
  { section: 'Master Data', items: [
    { to: '/materials', label: 'Materials', icon: Database },
    { to: '/machines', label: 'Machines', icon: Wrench },
    { to: '/process-templates', label: 'Process Templates', icon: GitBranch },
    { to: '/vendors', label: 'Vendors', icon: Building2 },
    { to: '/overhead-profiles', label: 'Overhead Profiles', icon: Percent },
  ]},
  { section: 'Tools', items: [
    { to: '/excel-upload', label: 'Excel Import', icon: Upload },
    { to: '/settings', label: 'Settings', icon: Cog },
  ]},
]

export default function Sidebar() {
  return (
    <aside className="flex w-60 flex-col border-r border-surface-200 bg-white">
      <div className="flex h-14 items-center gap-2.5 border-b border-surface-200 px-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-500 text-white text-sm font-bold">
          SC
        </div>
        <div>
          <div className="text-sm font-semibold text-surface-800">Should-Cost</div>
          <div className="text-2xs text-surface-400">Modeling Platform</div>
        </div>
      </div>
      <nav className="flex-1 overflow-auto px-3 py-4">
        {nav.map((group) => (
          <div key={group.section} className="mb-5">
            <div className="mb-1.5 px-2 text-[10px] font-semibold uppercase tracking-wider text-surface-400">
              {group.section}
            </div>
            {group.items.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-[13px] font-medium transition-colors',
                    isActive
                      ? 'bg-brand-50 text-brand-700'
                      : 'text-surface-500 hover:bg-surface-100 hover:text-surface-700'
                  )
                }
              >
                <item.icon size={16} strokeWidth={1.8} />
                {item.label}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>
    </aside>
  )
}
