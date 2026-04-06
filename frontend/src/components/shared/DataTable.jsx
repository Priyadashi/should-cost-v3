import { useState } from 'react'
import { ChevronUp, ChevronDown, Search, Plus, Pencil, Trash2 } from 'lucide-react'
import clsx from 'clsx'

export default function DataTable({
  columns,
  data = [],
  onAdd,
  onEdit,
  onDelete,
  searchable = true,
  addLabel = 'Add New',
  emptyMessage = 'No data found',
  isLoading = false,
}) {
  const [search, setSearch] = useState('')
  const [sortCol, setSortCol] = useState(null)
  const [sortDir, setSortDir] = useState('asc')

  const filtered = data.filter((row) => {
    if (!search) return true
    return columns.some((col) => {
      const val = col.accessor ? row[col.accessor] : ''
      return String(val).toLowerCase().includes(search.toLowerCase())
    })
  })

  const sorted = [...filtered].sort((a, b) => {
    if (!sortCol) return 0
    const col = columns.find((c) => c.accessor === sortCol)
    if (!col) return 0
    const aVal = a[sortCol] ?? ''
    const bVal = b[sortCol] ?? ''
    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return sortDir === 'asc' ? aVal - bVal : bVal - aVal
    }
    return sortDir === 'asc'
      ? String(aVal).localeCompare(String(bVal))
      : String(bVal).localeCompare(String(aVal))
  })

  const toggleSort = (accessor) => {
    if (sortCol === accessor) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc')
    } else {
      setSortCol(accessor)
      setSortDir('asc')
    }
  }

  return (
    <div className="rounded-xl border border-surface-200 bg-white shadow-card">
      {/* Toolbar */}
      <div className="flex items-center justify-between border-b border-surface-200 px-4 py-3">
        {searchable && (
          <div className="relative">
            <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-surface-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search..."
              className="h-8 w-64 rounded-lg border border-surface-200 bg-surface-50 pl-8 pr-3 text-xs outline-none focus:border-brand-300 focus:ring-1 focus:ring-brand-200"
            />
          </div>
        )}
        <div className="flex items-center gap-2">
          <span className="text-xs text-surface-400">{filtered.length} items</span>
          {onAdd && (
            <button
              onClick={onAdd}
              className="flex items-center gap-1.5 rounded-lg bg-brand-500 px-3 py-1.5 text-xs font-semibold text-white hover:bg-brand-600 transition-colors"
            >
              <Plus size={14} />
              {addLabel}
            </button>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-surface-100 bg-surface-50/50">
              {columns.map((col) => (
                <th
                  key={col.accessor || col.header}
                  onClick={() => col.accessor && col.sortable !== false && toggleSort(col.accessor)}
                  className={clsx(
                    'px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-surface-400',
                    col.accessor && col.sortable !== false && 'cursor-pointer select-none hover:text-surface-600'
                  )}
                  style={col.width ? { width: col.width } : undefined}
                >
                  <div className="flex items-center gap-1">
                    {col.header}
                    {sortCol === col.accessor && (
                      sortDir === 'asc' ? <ChevronUp size={12} /> : <ChevronDown size={12} />
                    )}
                  </div>
                </th>
              ))}
              {(onEdit || onDelete) && (
                <th className="w-20 px-4 py-2.5 text-right text-[11px] font-semibold uppercase tracking-wider text-surface-400">
                  Actions
                </th>
              )}
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={columns.length + (onEdit || onDelete ? 1 : 0)} className="px-4 py-12 text-center text-sm text-surface-400">
                  Loading...
                </td>
              </tr>
            ) : sorted.length === 0 ? (
              <tr>
                <td colSpan={columns.length + (onEdit || onDelete ? 1 : 0)} className="px-4 py-12 text-center text-sm text-surface-400">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              sorted.map((row, i) => (
                <tr key={row.id || i} className="border-b border-surface-100 last:border-0 hover:bg-surface-50/50 transition-colors">
                  {columns.map((col) => (
                    <td key={col.accessor || col.header} className="px-4 py-3 text-sm text-surface-700">
                      {col.render ? col.render(row) : row[col.accessor]}
                    </td>
                  ))}
                  {(onEdit || onDelete) && (
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        {onEdit && (
                          <button
                            onClick={() => onEdit(row)}
                            className="rounded-md p-1.5 text-surface-400 hover:bg-surface-100 hover:text-surface-600"
                          >
                            <Pencil size={14} />
                          </button>
                        )}
                        {onDelete && (
                          <button
                            onClick={() => onDelete(row)}
                            className="rounded-md p-1.5 text-surface-400 hover:bg-red-50 hover:text-red-500"
                          >
                            <Trash2 size={14} />
                          </button>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
