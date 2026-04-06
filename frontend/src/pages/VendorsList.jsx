import { useState } from 'react'
import DataTable from '../components/shared/DataTable'
import Modal from '../components/shared/Modal'
import FormField, { Input } from '../components/shared/FormField'
import { useToast } from '../components/shared/Toast'
import { useVendors, useCreateVendor, useUpdateVendor, useDeleteVendor } from '../hooks/useApi'

const emptyForm = { name: '', code: '', location: '', capabilities: '', certifications: '', contact_email: '', contact_phone: '', notes: '' }

export default function VendorsList() {
  const { data: vendors = [], isLoading } = useVendors()
  const createMut = useCreateVendor()
  const updateMut = useUpdateVendor()
  const deleteMut = useDeleteVendor()
  const addToast = useToast()
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(emptyForm)

  const columns = [
    { header: 'Name', accessor: 'name', render: (r) => <span className="font-medium">{r.name}</span> },
    { header: 'Code', accessor: 'code', render: (r) => r.code ? <span className="font-mono text-xs bg-surface-100 px-1.5 py-0.5 rounded">{r.code}</span> : '\u2014' },
    { header: 'Location', accessor: 'location', render: (r) => r.location || '\u2014' },
    { header: 'Capabilities', accessor: 'capabilities', render: (r) => {
      const caps = r.capabilities || []
      return caps.length > 0
        ? caps.map((c) => <span key={c} className="mr-1 inline-block rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-medium text-emerald-700">{c}</span>)
        : '\u2014'
    }},
    { header: 'Certifications', accessor: 'certifications', render: (r) => {
      const certs = r.certifications || []
      return certs.length > 0
        ? certs.map((c) => <span key={c} className="mr-1 inline-block rounded-full bg-amber-50 px-2 py-0.5 text-[11px] font-medium text-amber-700">{c}</span>)
        : '\u2014'
    }},
    { header: 'Email', accessor: 'contact_email', render: (r) => r.contact_email || '\u2014' },
  ]

  const openAdd = () => { setForm(emptyForm); setModal('add') }
  const openEdit = (row) => {
    setForm({
      name: row.name,
      code: row.code || '',
      location: row.location || '',
      capabilities: (row.capabilities || []).join(', '),
      certifications: (row.certifications || []).join(', '),
      contact_email: row.contact_email || '',
      contact_phone: row.contact_phone || '',
      notes: row.notes || '',
    })
    setModal(row)
  }
  const close = () => setModal(null)

  const handleSave = async () => {
    try {
      const payload = {
        ...form,
        capabilities: form.capabilities ? form.capabilities.split(',').map((s) => s.trim()).filter(Boolean) : [],
        certifications: form.certifications ? form.certifications.split(',').map((s) => s.trim()).filter(Boolean) : [],
      }
      if (modal === 'add') {
        await createMut.mutateAsync(payload)
        addToast('Vendor created successfully', 'success')
      } else {
        await updateMut.mutateAsync({ id: modal.id, data: payload })
        addToast('Vendor updated successfully', 'success')
      }
      close()
    } catch (err) {
      addToast(err?.response?.data?.detail || 'Failed to save vendor', 'error')
    }
  }

  const handleDelete = async (row) => {
    if (confirm(`Delete vendor "${row.name}"?`)) {
      try {
        await deleteMut.mutateAsync(row.id)
        addToast('Vendor deleted', 'success')
      } catch (err) {
        addToast(err?.response?.data?.detail || 'Failed to delete vendor', 'error')
      }
    }
  }

  return (
    <>
      <DataTable
        columns={columns}
        data={vendors}
        isLoading={isLoading}
        onAdd={openAdd}
        onEdit={openEdit}
        onDelete={handleDelete}
        addLabel="Add Vendor"
        emptyMessage="No vendors yet"
        searchable
      />
      <Modal open={!!modal} onClose={close} title={modal === 'add' ? 'Add Vendor' : 'Edit Vendor'} size="lg">
        <div className="grid grid-cols-2 gap-4">
          <FormField label="Name">
            <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Bharat Forge Ltd" />
          </FormField>
          <FormField label="Code">
            <Input value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} placeholder="e.g. VND-001" />
          </FormField>
          <FormField label="Location">
            <Input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} placeholder="e.g. Pune, India" />
          </FormField>
          <FormField label="Contact Email">
            <Input type="email" value={form.contact_email} onChange={(e) => setForm({ ...form, contact_email: e.target.value })} placeholder="vendor@example.com" />
          </FormField>
          <FormField label="Contact Phone">
            <Input value={form.contact_phone} onChange={(e) => setForm({ ...form, contact_phone: e.target.value })} placeholder="+91-XXXXXXXXXX" />
          </FormField>
          <FormField label="Capabilities">
            <Input value={form.capabilities} onChange={(e) => setForm({ ...form, capabilities: e.target.value })} placeholder="Forging, Machining, Heat Treatment" />
          </FormField>
          <FormField label="Certifications" className="col-span-2">
            <Input value={form.certifications} onChange={(e) => setForm({ ...form, certifications: e.target.value })} placeholder="ISO 9001, IATF 16949" />
          </FormField>
        </div>
        <FormField label="Notes" className="mt-4">
          <Input value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} placeholder="Optional notes" />
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
