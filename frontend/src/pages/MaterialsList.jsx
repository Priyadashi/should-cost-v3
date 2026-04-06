import { useState } from 'react'
import DataTable from '../components/shared/DataTable'
import Modal from '../components/shared/Modal'
import FormField, { Input, Select } from '../components/shared/FormField'
import { useToast } from '../components/shared/Toast'
import { useMaterials, useCreateMaterial, useUpdateMaterial, useDeleteMaterial } from '../hooks/useApi'

const emptyForm = { grade: '', material_type: 'Steel', rate_per_kg: '', currency: 'INR', scrap_recovery_pct: '0.35', region: '', description: '' }

export default function MaterialsList() {
  const { data: materials = [], isLoading } = useMaterials()
  const createMut = useCreateMaterial()
  const updateMut = useUpdateMaterial()
  const deleteMut = useDeleteMaterial()
  const addToast = useToast()
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(emptyForm)

  const columns = [
    { header: 'Grade', accessor: 'grade', render: (r) => <span className="font-medium">{r.grade}</span> },
    { header: 'Type', accessor: 'material_type' },
    { header: 'Rate/kg', accessor: 'rate_per_kg', render: (r) => <span className="font-mono text-brand-700 font-semibold">{r.currency === 'USD' ? '$' : r.currency === 'EUR' ? '\u20AC' : '\u20B9'}{r.rate_per_kg}</span> },
    { header: 'Currency', accessor: 'currency' },
    { header: 'Scrap Recovery', accessor: 'scrap_recovery_pct', render: (r) => <span className="font-mono">{(r.scrap_recovery_pct * 100).toFixed(0)}%</span> },
    { header: 'Region', accessor: 'region', render: (r) => r.region || '\u2014' },
  ]

  const openAdd = () => { setForm(emptyForm); setModal('add') }
  const openEdit = (row) => {
    setForm({
      grade: row.grade,
      material_type: row.material_type,
      rate_per_kg: row.rate_per_kg,
      currency: row.currency,
      scrap_recovery_pct: row.scrap_recovery_pct,
      region: row.region || '',
      description: row.description || '',
    })
    setModal(row)
  }
  const close = () => setModal(null)

  const handleSave = async () => {
    try {
      const payload = { ...form, rate_per_kg: parseFloat(form.rate_per_kg), scrap_recovery_pct: parseFloat(form.scrap_recovery_pct) }
      if (modal === 'add') {
        await createMut.mutateAsync(payload)
        addToast('Material created successfully', 'success')
      } else {
        await updateMut.mutateAsync({ id: modal.id, data: payload })
        addToast('Material updated successfully', 'success')
      }
      close()
    } catch (err) {
      addToast(err?.response?.data?.detail || 'Failed to save material', 'error')
    }
  }

  const handleDelete = async (row) => {
    if (confirm(`Delete material "${row.grade}"?`)) {
      try {
        await deleteMut.mutateAsync(row.id)
        addToast('Material deleted', 'success')
      } catch (err) {
        addToast(err?.response?.data?.detail || 'Failed to delete material', 'error')
      }
    }
  }

  return (
    <>
      <DataTable
        columns={columns}
        data={materials}
        isLoading={isLoading}
        onAdd={openAdd}
        onEdit={openEdit}
        onDelete={handleDelete}
        addLabel="Add Material"
        emptyMessage="No materials yet"
        searchable
      />
      <Modal open={!!modal} onClose={close} title={modal === 'add' ? 'Add Material' : 'Edit Material'}>
        <div className="grid grid-cols-2 gap-4">
          <FormField label="Grade">
            <Input value={form.grade} onChange={(e) => setForm({ ...form, grade: e.target.value })} placeholder="e.g. EN8 (Medium Carbon Steel)" />
          </FormField>
          <FormField label="Material Type">
            <Select value={form.material_type} onChange={(e) => setForm({ ...form, material_type: e.target.value })}>
              <option>Steel</option>
              <option>Aluminum</option>
              <option>Cast Iron</option>
              <option>Stainless Steel</option>
              <option>Other</option>
            </Select>
          </FormField>
          <FormField label="Rate per kg">
            <Input type="number" step="0.01" value={form.rate_per_kg} onChange={(e) => setForm({ ...form, rate_per_kg: e.target.value })} placeholder="0.00" />
          </FormField>
          <FormField label="Currency">
            <Select value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })}>
              <option>INR</option>
              <option>USD</option>
              <option>EUR</option>
            </Select>
          </FormField>
          <FormField label="Scrap Recovery %">
            <Input type="number" step="0.01" value={form.scrap_recovery_pct} onChange={(e) => setForm({ ...form, scrap_recovery_pct: e.target.value })} placeholder="0.35" />
          </FormField>
          <FormField label="Region">
            <Input value={form.region} onChange={(e) => setForm({ ...form, region: e.target.value })} placeholder="e.g. India" />
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
