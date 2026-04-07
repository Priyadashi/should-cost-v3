import { useState } from 'react'
import DataTable from '../components/shared/DataTable'
import Modal from '../components/shared/Modal'
import FormField, { Input, Select } from '../components/shared/FormField'
import { useToast } from '../components/shared/Toast'
import { useMachines, useProcessTemplates, useCreateProcessTemplate, useUpdateProcessTemplate, useDeleteProcessTemplate } from '../hooks/useApi'

const COMMODITY_OPTIONS = ['Forging', 'Casting', 'Fabrication']

const emptyForm = {
  name: '',
  commodity_type: 'Forging',
  category: '',
  sequence_order: '',
  default_machine_id: '',
  default_cycle_time_min: '',
  default_setup_time_min: '',
  default_batch_size: '100',
  default_operators: '1',
  default_labor_rate_per_hr: '',
  default_tooling_cost_per_unit: '0',
  description: '',
}

export default function ProcessTemplatesList() {
  const [commodityFilter, setCommodityFilter] = useState(undefined)
  const { data: templates = [], isLoading } = useProcessTemplates(commodityFilter)
  const { data: machines = [] } = useMachines()
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
    { header: 'Category', accessor: 'category', render: (r) => r.category || '—' },
    { header: 'Seq.', accessor: 'sequence_order', render: (r) => <span className="font-mono">{r.sequence_order ?? '—'}</span> },
    {
      header: 'Machine',
      accessor: 'default_machine_id',
      render: (r) => {
        const m = machines.find(m => m.id === r.default_machine_id)
        return m ? <span className="text-xs text-surface-600">{m.name}</span> : '—'
      },
    },
    { header: 'Cycle (min)', accessor: 'default_cycle_time_min', render: (r) => r.default_cycle_time_min != null ? <span className="font-mono">{r.default_cycle_time_min}</span> : '—' },
    { header: 'Setup (min)', accessor: 'default_setup_time_min', render: (r) => r.default_setup_time_min != null ? <span className="font-mono">{r.default_setup_time_min}</span> : '—' },
    { header: 'Batch', accessor: 'default_batch_size', render: (r) => <span className="font-mono">{r.default_batch_size ?? 100}</span> },
    { header: 'Operators', accessor: 'default_operators', render: (r) => <span className="font-mono">{r.default_operators ?? 1}</span> },
    { header: 'Labor ₹/hr', accessor: 'default_labor_rate_per_hr', render: (r) => r.default_labor_rate_per_hr != null ? <span className="font-mono text-brand-700 font-semibold">₹{r.default_labor_rate_per_hr}</span> : '—' },
    { header: 'Tooling ₹/pc', accessor: 'default_tooling_cost_per_unit', render: (r) => r.default_tooling_cost_per_unit != null ? <span className="font-mono">₹{r.default_tooling_cost_per_unit}</span> : '—' },
  ]

  const openAdd = () => { setForm(emptyForm); setModal('add') }
  const openEdit = (row) => {
    setForm({
      name: row.name,
      commodity_type: row.commodity_type || 'Forging',
      category: row.category || '',
      sequence_order: row.sequence_order ?? '',
      default_machine_id: row.default_machine_id ?? '',
      default_cycle_time_min: row.default_cycle_time_min ?? '',
      default_setup_time_min: row.default_setup_time_min ?? '',
      default_batch_size: row.default_batch_size ?? 100,
      default_operators: row.default_operators ?? 1,
      default_labor_rate_per_hr: row.default_labor_rate_per_hr ?? '',
      default_tooling_cost_per_unit: row.default_tooling_cost_per_unit ?? 0,
      description: row.description || '',
    })
    setModal(row)
  }
  const close = () => setModal(null)

  const handleSave = async () => {
    try {
      const payload = {
        ...form,
        sequence_order: form.sequence_order !== '' ? parseInt(form.sequence_order) : 0,
        default_machine_id: form.default_machine_id !== '' ? parseInt(form.default_machine_id) : null,
        default_cycle_time_min: form.default_cycle_time_min !== '' ? parseFloat(form.default_cycle_time_min) : null,
        default_setup_time_min: form.default_setup_time_min !== '' ? parseFloat(form.default_setup_time_min) : null,
        default_batch_size: form.default_batch_size !== '' ? parseInt(form.default_batch_size) : 100,
        default_operators: form.default_operators !== '' ? parseInt(form.default_operators) : 1,
        default_labor_rate_per_hr: form.default_labor_rate_per_hr !== '' ? parseFloat(form.default_labor_rate_per_hr) : null,
        default_tooling_cost_per_unit: form.default_tooling_cost_per_unit !== '' ? parseFloat(form.default_tooling_cost_per_unit) : 0,
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

  const f = (k) => (e) => setForm({ ...form, [k]: e.target.value })

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
      <Modal open={!!modal} onClose={close} title={modal === 'add' ? 'Add Process Template' : 'Edit Process Template'} size="xl">
        <div className="grid grid-cols-3 gap-4">
          <FormField label="Operation Name" className="col-span-2">
            <Input value={form.name} onChange={f('name')} placeholder="e.g. Rough Turning" />
          </FormField>
          <FormField label="Commodity Type">
            <Select value={form.commodity_type} onChange={f('commodity_type')}>
              {COMMODITY_OPTIONS.map((c) => <option key={c}>{c}</option>)}
            </Select>
          </FormField>
          <FormField label="Category">
            <Input value={form.category} onChange={f('category')} placeholder="e.g. Machining" />
          </FormField>
          <FormField label="Sequence Order">
            <Input type="number" step="1" value={form.sequence_order} onChange={f('sequence_order')} placeholder="e.g. 10" />
          </FormField>
          <FormField label="Default Machine">
            <Select value={form.default_machine_id} onChange={f('default_machine_id')}>
              <option value="">None</option>
              {machines.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
            </Select>
          </FormField>
          <FormField label="Cycle Time (min)">
            <Input type="number" step="0.1" value={form.default_cycle_time_min} onChange={f('default_cycle_time_min')} placeholder="0.0" />
          </FormField>
          <FormField label="Setup Time (min)">
            <Input type="number" step="0.1" value={form.default_setup_time_min} onChange={f('default_setup_time_min')} placeholder="0.0" />
          </FormField>
          <FormField label="Batch Size">
            <Input type="number" value={form.default_batch_size} onChange={f('default_batch_size')} placeholder="100" />
          </FormField>
          <FormField label="Operators">
            <Input type="number" value={form.default_operators} onChange={f('default_operators')} placeholder="1" />
          </FormField>
          <FormField label="Labor Rate (₹/hr)">
            <Input type="number" step="0.01" value={form.default_labor_rate_per_hr} onChange={f('default_labor_rate_per_hr')} placeholder="0.00" />
          </FormField>
          <FormField label="Tooling Cost (₹/pc)">
            <Input type="number" step="0.01" value={form.default_tooling_cost_per_unit} onChange={f('default_tooling_cost_per_unit')} placeholder="0.00" />
          </FormField>
        </div>
        <FormField label="Description" className="mt-4">
          <Input value={form.description} onChange={f('description')} placeholder="Optional description" />
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
