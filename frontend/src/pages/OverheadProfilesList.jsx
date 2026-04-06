import { useState } from 'react'
import DataTable from '../components/shared/DataTable'
import Modal from '../components/shared/Modal'
import FormField, { Input } from '../components/shared/FormField'
import { useToast } from '../components/shared/Toast'
import { useOverheadProfiles, useCreateOverheadProfile, useUpdateOverheadProfile, useDeleteOverheadProfile } from '../hooks/useApi'

const emptyForm = {
  name: '',
  description: '',
  is_default: false,
  factory_overhead_pct: '',
  admin_overhead_pct: '',
  depreciation_pct: '',
  quality_cost_pct: '',
  profit_margin_pct: '',
  taxes_duties_pct: '',
  sga_pct: '',
  packaging_per_unit: '',
  freight_per_unit: '',
  other_logistics_per_unit: '',
}

const pctFmt = (v) => v != null ? <span className="font-mono">{(v * 100).toFixed(1)}%</span> : '\u2014'
const curFmt = (v) => v != null ? <span className="font-mono">{'\u20B9'}{Number(v).toFixed(2)}</span> : '\u2014'

export default function OverheadProfilesList() {
  const { data: profiles = [], isLoading } = useOverheadProfiles()
  const createMut = useCreateOverheadProfile()
  const updateMut = useUpdateOverheadProfile()
  const deleteMut = useDeleteOverheadProfile()
  const addToast = useToast()
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(emptyForm)

  const columns = [
    { header: 'Name', accessor: 'name', render: (r) => (
      <div className="flex items-center gap-2">
        <span className="font-medium">{r.name}</span>
        {r.is_default && <span className="rounded-full bg-brand-50 px-2 py-0.5 text-[10px] font-semibold text-brand-700">Default</span>}
      </div>
    )},
    { header: 'Factory OH', accessor: 'factory_overhead_pct', render: (r) => pctFmt(r.factory_overhead_pct) },
    { header: 'Admin OH', accessor: 'admin_overhead_pct', render: (r) => pctFmt(r.admin_overhead_pct) },
    { header: 'Profit', accessor: 'profit_margin_pct', render: (r) => pctFmt(r.profit_margin_pct) },
    { header: 'SGA', accessor: 'sga_pct', render: (r) => pctFmt(r.sga_pct) },
    { header: 'Packaging/unit', accessor: 'packaging_per_unit', render: (r) => curFmt(r.packaging_per_unit) },
    { header: 'Freight/unit', accessor: 'freight_per_unit', render: (r) => curFmt(r.freight_per_unit) },
  ]

  const openAdd = () => { setForm(emptyForm); setModal('add') }
  const openEdit = (row) => {
    setForm({
      name: row.name,
      description: row.description || '',
      is_default: row.is_default || false,
      factory_overhead_pct: row.factory_overhead_pct ?? '',
      admin_overhead_pct: row.admin_overhead_pct ?? '',
      depreciation_pct: row.depreciation_pct ?? '',
      quality_cost_pct: row.quality_cost_pct ?? '',
      profit_margin_pct: row.profit_margin_pct ?? '',
      taxes_duties_pct: row.taxes_duties_pct ?? '',
      sga_pct: row.sga_pct ?? '',
      packaging_per_unit: row.packaging_per_unit ?? '',
      freight_per_unit: row.freight_per_unit ?? '',
      other_logistics_per_unit: row.other_logistics_per_unit ?? '',
    })
    setModal(row)
  }
  const close = () => setModal(null)

  const parseNum = (v) => v !== '' && v != null ? parseFloat(v) : null

  const handleSave = async () => {
    try {
      const payload = {
        name: form.name,
        description: form.description,
        is_default: form.is_default,
        factory_overhead_pct: parseNum(form.factory_overhead_pct),
        admin_overhead_pct: parseNum(form.admin_overhead_pct),
        depreciation_pct: parseNum(form.depreciation_pct),
        quality_cost_pct: parseNum(form.quality_cost_pct),
        profit_margin_pct: parseNum(form.profit_margin_pct),
        taxes_duties_pct: parseNum(form.taxes_duties_pct),
        sga_pct: parseNum(form.sga_pct),
        packaging_per_unit: parseNum(form.packaging_per_unit),
        freight_per_unit: parseNum(form.freight_per_unit),
        other_logistics_per_unit: parseNum(form.other_logistics_per_unit),
      }
      if (modal === 'add') {
        await createMut.mutateAsync(payload)
        addToast('Overhead profile created successfully', 'success')
      } else {
        await updateMut.mutateAsync({ id: modal.id, data: payload })
        addToast('Overhead profile updated successfully', 'success')
      }
      close()
    } catch (err) {
      addToast(err?.response?.data?.detail || 'Failed to save overhead profile', 'error')
    }
  }

  const handleDelete = async (row) => {
    if (confirm(`Delete overhead profile "${row.name}"?`)) {
      try {
        await deleteMut.mutateAsync(row.id)
        addToast('Overhead profile deleted', 'success')
      } catch (err) {
        addToast(err?.response?.data?.detail || 'Failed to delete overhead profile', 'error')
      }
    }
  }

  return (
    <>
      <DataTable
        columns={columns}
        data={profiles}
        isLoading={isLoading}
        onAdd={openAdd}
        onEdit={openEdit}
        onDelete={handleDelete}
        addLabel="Add Profile"
        emptyMessage="No overhead profiles yet"
        searchable
      />
      <Modal open={!!modal} onClose={close} title={modal === 'add' ? 'Add Overhead Profile' : 'Edit Overhead Profile'} size="xl">
        <div className="grid grid-cols-2 gap-4">
          <FormField label="Name">
            <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Standard India Profile" />
          </FormField>
          <FormField label="Description">
            <Input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Optional description" />
          </FormField>
        </div>
        <div className="mt-3 flex items-center gap-2">
          <input
            type="checkbox"
            id="is_default"
            checked={form.is_default}
            onChange={(e) => setForm({ ...form, is_default: e.target.checked })}
            className="h-4 w-4 rounded border-surface-300 text-brand-500 focus:ring-brand-200"
          />
          <label htmlFor="is_default" className="text-sm text-surface-700">Set as default profile</label>
        </div>
        <div className="mt-4">
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-surface-400">Percentage Overheads (as decimal, e.g. 0.10 = 10%)</h3>
          <div className="grid grid-cols-3 gap-4">
            <FormField label="Factory Overhead">
              <Input type="number" step="0.001" value={form.factory_overhead_pct} onChange={(e) => setForm({ ...form, factory_overhead_pct: e.target.value })} placeholder="0.10" />
            </FormField>
            <FormField label="Admin Overhead">
              <Input type="number" step="0.001" value={form.admin_overhead_pct} onChange={(e) => setForm({ ...form, admin_overhead_pct: e.target.value })} placeholder="0.05" />
            </FormField>
            <FormField label="Depreciation">
              <Input type="number" step="0.001" value={form.depreciation_pct} onChange={(e) => setForm({ ...form, depreciation_pct: e.target.value })} placeholder="0.03" />
            </FormField>
            <FormField label="Quality Cost">
              <Input type="number" step="0.001" value={form.quality_cost_pct} onChange={(e) => setForm({ ...form, quality_cost_pct: e.target.value })} placeholder="0.02" />
            </FormField>
            <FormField label="Profit Margin">
              <Input type="number" step="0.001" value={form.profit_margin_pct} onChange={(e) => setForm({ ...form, profit_margin_pct: e.target.value })} placeholder="0.10" />
            </FormField>
            <FormField label="Taxes & Duties">
              <Input type="number" step="0.001" value={form.taxes_duties_pct} onChange={(e) => setForm({ ...form, taxes_duties_pct: e.target.value })} placeholder="0.05" />
            </FormField>
            <FormField label="SGA">
              <Input type="number" step="0.001" value={form.sga_pct} onChange={(e) => setForm({ ...form, sga_pct: e.target.value })} placeholder="0.03" />
            </FormField>
          </div>
        </div>
        <div className="mt-4">
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-surface-400">Per-unit Costs</h3>
          <div className="grid grid-cols-3 gap-4">
            <FormField label="Packaging/unit">
              <Input type="number" step="0.01" value={form.packaging_per_unit} onChange={(e) => setForm({ ...form, packaging_per_unit: e.target.value })} placeholder="0.00" />
            </FormField>
            <FormField label="Freight/unit">
              <Input type="number" step="0.01" value={form.freight_per_unit} onChange={(e) => setForm({ ...form, freight_per_unit: e.target.value })} placeholder="0.00" />
            </FormField>
            <FormField label="Other Logistics/unit">
              <Input type="number" step="0.01" value={form.other_logistics_per_unit} onChange={(e) => setForm({ ...form, other_logistics_per_unit: e.target.value })} placeholder="0.00" />
            </FormField>
          </div>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <button onClick={close} className="rounded-lg border border-surface-200 px-4 py-2 text-sm font-medium text-surface-600 hover:bg-surface-50">Cancel</button>
          <button onClick={handleSave} disabled={createMut.isPending || updateMut.isPending} className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50">
            {createMut.isPending || updateMut.isPending ? 'Saving...' : 'Save'}
          </button>
        </div>
      </Modal>
    </>
  )
}
