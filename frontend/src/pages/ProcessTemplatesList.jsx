import { useState } from 'react'
import DataTable from '../components/shared/DataTable'
import Modal from '../components/shared/Modal'
import FormField, { Input, Select } from '../components/shared/FormField'
import { useToast } from '../components/shared/Toast'
import { useProcessTemplates, useCreateProcessTemplate, useUpdateProcessTemplate, useDeleteProcessTemplate } from '../hooks/useApi'

const COMMODITY_OPTIONS = ['Forging', 'Casting', 'Fabrication']

const emptyForm = {
  name: '',
  commodity_type: 'Forging',
  category: '',
  sequence_order: '',
  default_cycle_time_min: '',
  default_setup_time_min: '',
  default_labor_rate_per_hr: '',
  description: '',
}

export default function ProcessTemplatesList() {
  const [commodityFilter, setCommodityFilter] = useState(undefined)
  const { data: templates = [], isLoading } = useProcessTemplates(commodityFilter)
  const createMut = useCreateProcessTemplate()
  const updateMut = useUpdateProcessTemplate()
  const deleteMut = useDeleteProcessTemplate()
  const addToast = useToast()
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(emptyForm)

  const columns = [
    { header: 'Name', accessor: 'name', render: (r) => <span className="font-medium">{r.name}</span> },
    { header: 'Commodity', accessor: 'commodity_type', render: (r) => (
      <span className="inline-block rounded-full bg-blue-50 px-2 py-0.5 text-[11px] font-semibold text-blue-700">{r.commodity_type}</span>
    )},
    { header: 'Category', accessor: 'category', render: (r) => r.category || '\u2014' },
    { header: 'Seq.', accessor: 'sequence_order', render: (r) => <span className="font-mono">{r.sequence_order ?? '\u2014'}</span> },
    { header: 'Cycle Time', accessor: 'default_cycle_time_min', render: (r) => r.default_cycle_time_min != null ? <span className="font-mono">{r.default_cycle_time_min} min</span> : '\u2014' },
    { header: 'Setup Time', accessor: 'default_setup_time_min', render: (r) => r.default_setup_time_min != null ? <span className="font-mono">{r.default_setup_time_min} min</span> : '\u2014' },
    { header: 'Labor Rate/hr', accessor: 'default_labor_rate_per_hr', render: (r) => r.default_labor_rate_per_hr != null ? <span className="font-mono text-brand-700 font-semibold">{'\u20B9'}{r.default_labor_rate_per_hr}</span> : '\u2014' },
  ]

  const openAdd = () => { setForm(emptyForm); setModal('add') }
  const openEdit = (row) => {
    setForm({
      name: row.name,
      commodity_type: row.commodity_type || 'Forging',
      category: row.category || '',
      sequence_order: row.sequence_order ?? '',
      default_cycle_time_min: row.default_cycle_time_min ?? '',
      default_setup_time_min: row.default_setup_time_min ?? '',
      default_labor_rate_per_hr: row.default_labor_rate_per_hr ?? '',
      description: row.description || '',
    })
    setModal(row)
  }
  const close = () => setModal(null)

  const handleSave = async () => {
    try {
      const payload = {
        ...form,
        sequence_order: form.sequence_order !== '' ? parseInt(form.sequence_order) : null,
        default_cycle_time_min: form.default_cycle_time_min !== '' ? parseFloat(form.default_cycle_time_min) : null,
        default_setup_time_min: form.default_setup_time_min !== '' ? parseFloat(form.default_setup_time_min) : null,
        default_labor_rate_per_hr: form.default_labor_rate_per_hr !== '' ? parseFloat(form.default_labor_rate_per_hr) : null,
      }
      if (modal === 'add') {
        await createMut.mutateAsync(payload)
        addToast('Process template created successfully', 'success')
      } else {
        await updateMut.mutateAsync({ id: modal.id, data: payload })
        addToast('Process template updated successfully', 'success')
      }
      close()
    } catch (err) {
      addToast(err?.response?.data?.detail || 'Failed to save process template', 'error')
    }
  }

  const handleDelete = async (row) => {
    if (confirm(`Delete process template "${row.name}"?`)) {
      try {
        await deleteMut.mutateAsync(row.id)
        addToast('Process template deleted', 'success')
      } catch (err) {
        addToast(err?.response?.data?.detail || 'Failed to delete process template', 'error')
      }
    }
  }

  return (
    <div>
      <div className="mb-4 flex items-center gap-3">
        <label className="text-xs font-semibold uppercase tracking-wider text-surface-400">Commodity Filter</label>
        <select
          value={commodityFilter || ''}
          onChange={(e) => setCommodityFilter(e.target.value || undefined)}
          className="h-8 rounded-lg border border-surface-200 bg-surface-50 px-3 text-xs text-surface-700 outline-none focus:border-brand-300 focus:ring-1 focus:ring-brand-200"
        >
          <option value="">All Commodities</option>
          {COMMODITY_OPTIONS.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>
      <DataTable
        columns={columns}
        data={templates}
        isLoading={isLoading}
        onAdd={openAdd}
        onEdit={openEdit}
        onDelete={handleDelete}
        addLabel="Add Template"
        emptyMessage="No process templates yet"
        searchable
      />
      <Modal open={!!modal} onClose={close} title={modal === 'add' ? 'Add Process Template' : 'Edit Process Template'} size="lg">
        <div className="grid grid-cols-2 gap-4">
          <FormField label="Name">
            <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Rough Turning" />
          </FormField>
          <FormField label="Commodity Type">
            <Select value={form.commodity_type} onChange={(e) => setForm({ ...form, commodity_type: e.target.value })}>
              {COMMODITY_OPTIONS.map((c) => <option key={c}>{c}</option>)}
            </Select>
          </FormField>
          <FormField label="Category">
            <Input value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} placeholder="e.g. Machining" />
          </FormField>
          <FormField label="Sequence Order">
            <Input type="number" step="1" value={form.sequence_order} onChange={(e) => setForm({ ...form, sequence_order: e.target.value })} placeholder="e.g. 10" />
          </FormField>
          <FormField label="Default Cycle Time (min)">
            <Input type="number" step="0.1" value={form.default_cycle_time_min} onChange={(e) => setForm({ ...form, default_cycle_time_min: e.target.value })} placeholder="0.0" />
          </FormField>
          <FormField label="Default Setup Time (min)">
            <Input type="number" step="0.1" value={form.default_setup_time_min} onChange={(e) => setForm({ ...form, default_setup_time_min: e.target.value })} placeholder="0.0" />
          </FormField>
          <FormField label="Default Labor Rate/hr">
            <Input type="number" step="0.01" value={form.default_labor_rate_per_hr} onChange={(e) => setForm({ ...form, default_labor_rate_per_hr: e.target.value })} placeholder="0.00" />
          </FormField>
        </div>
        <FormField label="Description" className="mt-4">
          <Input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Optional description" />
        </FormField>
        <div className="mt-4 flex justify-end gap-2">
          <button onClick={close} className="rounded-lg border border-surface-200 px-4 py-2 text-sm font-medium text-surface-600 hover:bg-surface-50">Cancel</button>
          <button onClick={handleSave} disabled={createMut.isPending || updateMut.isPending} className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50">
            {createMut.isPending || updateMut.isPending ? 'Saving...' : 'Save'}
          </button>
        </div>
      </Modal>
    </div>
  )
}
