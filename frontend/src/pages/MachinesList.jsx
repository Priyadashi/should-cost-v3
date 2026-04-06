import { useState } from 'react'
import DataTable from '../components/shared/DataTable'
import Modal from '../components/shared/Modal'
import FormField, { Input, Select } from '../components/shared/FormField'
import { useToast } from '../components/shared/Toast'
import { useMachines, useCreateMachine, useUpdateMachine, useDeleteMachine } from '../hooks/useApi'

const emptyForm = { name: '', machine_type: '', hourly_rate: '', currency: 'INR', power_kw: '', commodity_types: '', description: '' }

export default function MachinesList() {
  const { data: machines = [], isLoading } = useMachines()
  const createMut = useCreateMachine()
  const updateMut = useUpdateMachine()
  const deleteMut = useDeleteMachine()
  const addToast = useToast()
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(emptyForm)

  const columns = [
    { header: 'Name', accessor: 'name', render: (r) => <span className="font-medium">{r.name}</span> },
    { header: 'Type', accessor: 'machine_type' },
    { header: 'Hourly Rate', accessor: 'hourly_rate', render: (r) => <span className="font-mono text-brand-700 font-semibold">{r.currency === 'USD' ? '$' : r.currency === 'EUR' ? '\u20AC' : '\u20B9'}{r.hourly_rate}/hr</span> },
    { header: 'Power (kW)', accessor: 'power_kw', render: (r) => r.power_kw ? <span className="font-mono">{r.power_kw}</span> : '\u2014' },
    { header: 'Commodities', accessor: 'commodity_types', render: (r) => {
      const types = r.commodity_types || []
      return types.length > 0
        ? types.map((t) => <span key={t} className="mr-1 inline-block rounded-full bg-surface-100 px-2 py-0.5 text-[11px] font-medium text-surface-600">{t}</span>)
        : '\u2014'
    }},
  ]

  const openAdd = () => { setForm(emptyForm); setModal('add') }
  const openEdit = (row) => {
    setForm({
      name: row.name,
      machine_type: row.machine_type || '',
      hourly_rate: row.hourly_rate,
      currency: row.currency || 'INR',
      power_kw: row.power_kw || '',
      commodity_types: (row.commodity_types || []).join(', '),
      description: row.description || '',
    })
    setModal(row)
  }
  const close = () => setModal(null)

  const handleSave = async () => {
    try {
      const payload = {
        ...form,
        hourly_rate: parseFloat(form.hourly_rate),
        power_kw: form.power_kw ? parseFloat(form.power_kw) : null,
        commodity_types: form.commodity_types ? form.commodity_types.split(',').map((s) => s.trim()).filter(Boolean) : [],
      }
      if (modal === 'add') {
        await createMut.mutateAsync(payload)
        addToast('Machine created successfully', 'success')
      } else {
        await updateMut.mutateAsync({ id: modal.id, data: payload })
        addToast('Machine updated successfully', 'success')
      }
      close()
    } catch (err) {
      addToast(err?.response?.data?.detail || 'Failed to save machine', 'error')
    }
  }

  const handleDelete = async (row) => {
    if (confirm(`Delete machine "${row.name}"?`)) {
      try {
        await deleteMut.mutateAsync(row.id)
        addToast('Machine deleted', 'success')
      } catch (err) {
        addToast(err?.response?.data?.detail || 'Failed to delete machine', 'error')
      }
    }
  }

  return (
    <>
      <DataTable
        columns={columns}
        data={machines}
        isLoading={isLoading}
        onAdd={openAdd}
        onEdit={openEdit}
        onDelete={handleDelete}
        addLabel="Add Machine"
        emptyMessage="No machines yet"
        searchable
      />
      <Modal open={!!modal} onClose={close} title={modal === 'add' ? 'Add Machine' : 'Edit Machine'}>
        <div className="grid grid-cols-2 gap-4">
          <FormField label="Name">
            <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. CNC Lathe 200T" />
          </FormField>
          <FormField label="Machine Type">
            <Input value={form.machine_type} onChange={(e) => setForm({ ...form, machine_type: e.target.value })} placeholder="e.g. CNC Lathe" />
          </FormField>
          <FormField label="Hourly Rate">
            <Input type="number" step="0.01" value={form.hourly_rate} onChange={(e) => setForm({ ...form, hourly_rate: e.target.value })} placeholder="0.00" />
          </FormField>
          <FormField label="Currency">
            <Select value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })}>
              <option>INR</option>
              <option>USD</option>
              <option>EUR</option>
            </Select>
          </FormField>
          <FormField label="Power (kW)">
            <Input type="number" step="0.1" value={form.power_kw} onChange={(e) => setForm({ ...form, power_kw: e.target.value })} placeholder="e.g. 15.5" />
          </FormField>
          <FormField label="Commodity Types">
            <Input value={form.commodity_types} onChange={(e) => setForm({ ...form, commodity_types: e.target.value })} placeholder="Forging, Casting, Fabrication" />
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
    </>
  )
}
