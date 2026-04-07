import { useNavigate } from 'react-router-dom'
import DataTable from '../components/shared/DataTable'
import { StatusBadge, CurrencyDisplay } from '../components/shared/StatusBadge'
import { useToast } from '../components/shared/Toast'
import { useCostSheets, useDeleteCostSheet } from '../hooks/useApi'

export default function CostSheetsList() {
  const { data: costSheets = [], isLoading } = useCostSheets()
  const deleteMut = useDeleteCostSheet()
  const addToast = useToast()
  const navigate = useNavigate()

  const columns = [
    {
      header: 'Scenario',
      accessor: 'scenario_name',
      render: (r) => (
        <button
          onClick={() => handleRowClick(r)}
          className="font-medium text-brand-600 hover:text-brand-700 hover:underline text-left"
        >
          {r.scenario_name || 'Untitled'}
        </button>
      ),
    },
    { header: 'Part Name', accessor: 'part_name', render: (r) => r.part_name || '\u2014' },
    { header: 'Part No.', accessor: 'part_no', render: (r) => r.part_no ? <span className="font-mono text-xs">{r.part_no}</span> : '\u2014' },
    {
      header: 'Status',
      accessor: 'status',
      render: (r) => <StatusBadge status={r.status} />,
    },
    {
      header: 'Should Cost',
      accessor: 'should_cost',
      render: (r) => {
        const cost = r.result_summary?.should_cost ?? r.should_cost
        return cost != null ? <CurrencyDisplay value={cost} className="font-semibold text-brand-700" /> : '\u2014'
      },
    },
    {
      header: 'Quoted / Supplier',
      accessor: 'quoted_price',
      render: (r) => {
        const quoted = r.quoted_price
        const supplier = r.supplier_name
        if (!quoted && !supplier) return '\u2014'
        return (
          <div className="leading-tight">
            {quoted != null && (
              <div className="font-mono font-semibold text-surface-700 text-sm">
                ₹{quoted.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
            )}
            {supplier && (
              <div className="text-[11px] text-surface-400 truncate max-w-[120px]">{supplier}</div>
            )}
          </div>
        )
      },
    },
    {
      header: 'Gap %',
      accessor: 'gap_pct',
      render: (r) => {
        let gap = r.result_summary?.gap_pct ?? r.gap_pct
        if (gap == null) return '\u2014'
        if (Math.abs(gap) < 1 && gap !== 0) gap = gap * 100
        const isNeg = gap < 0
        return (
          <span className={`font-mono font-semibold ${isNeg ? 'text-emerald-600' : 'text-red-600'}`}>
            {isNeg ? '' : '+'}{gap.toFixed(1)}%
          </span>
        )
      },
    },
    {
      header: 'Calculated',
      accessor: 'calculated_at',
      render: (r) => r.calculated_at
        ? <span className="text-xs text-surface-500">{new Date(r.calculated_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</span>
        : '\u2014',
    },
  ]

  const handleRowClick = (row) => {
    if (row.status === 'calculated' || row.status === 'approved') {
      navigate(`/cost-sheets/${row.id}/output`)
    } else {
      navigate(`/cost-sheets/${row.id}/edit`)
    }
  }

  const handleAdd = () => {
    navigate('/cost-sheets/new')
  }

  const handleDelete = async (row) => {
    if (confirm(`Delete cost sheet "${row.scenario_name || 'Untitled'}"?`)) {
      try {
        await deleteMut.mutateAsync(row.id)
        addToast('Cost sheet deleted', 'success')
      } catch (err) {
        addToast(err?.response?.data?.detail || 'Failed to delete cost sheet', 'error')
      }
    }
  }

  return (
    <DataTable
      columns={columns}
      data={costSheets}
      isLoading={isLoading}
      onAdd={handleAdd}
      onEdit={handleRowClick}
      onDelete={handleDelete}
      addLabel="New Cost Sheet"
      emptyMessage="No cost sheets yet. Create your first one!"
      searchable
    />
  )
}
