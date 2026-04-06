import { useLocation } from 'react-router-dom'
import { Search, Bell } from 'lucide-react'

const titles = {
  '/dashboard': 'Dashboard',
  '/cost-sheets': 'Cost Sheets',
  '/materials': 'Materials',
  '/machines': 'Machines',
  '/process-templates': 'Process Templates',
  '/vendors': 'Vendors',
  '/overhead-profiles': 'Overhead Profiles',
  '/excel-upload': 'Excel Import',
  '/settings': 'Settings',
}

export default function TopBar() {
  const { pathname } = useLocation()
  const title = titles[pathname] || 'Should-Cost Platform'

  return (
    <header className="flex h-14 items-center justify-between border-b border-surface-200 bg-white px-6">
      <h1 className="text-lg font-semibold text-surface-800">{title}</h1>
      <div className="flex items-center gap-3">
        <div className="relative">
          <Search size={15} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-surface-400" />
          <input
            placeholder="Search..."
            className="h-8 w-56 rounded-lg border border-surface-200 bg-surface-50 pl-8 pr-3 text-xs text-surface-600 placeholder:text-surface-400 outline-none focus:border-brand-300 focus:ring-1 focus:ring-brand-200"
          />
        </div>
        <button className="relative flex h-8 w-8 items-center justify-center rounded-lg border border-surface-200 text-surface-400 hover:bg-surface-100">
          <Bell size={15} />
        </button>
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-xs font-bold text-brand-700">
          AS
        </div>
      </div>
    </header>
  )
}
