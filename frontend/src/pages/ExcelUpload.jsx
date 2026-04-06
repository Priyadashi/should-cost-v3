import { useState, useRef } from 'react'
import { Upload, FileSpreadsheet, CheckCircle, AlertCircle, Download } from 'lucide-react'
import clsx from 'clsx'

export default function ExcelUpload() {
  const fileRef = useRef(null)
  const [file, setFile] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files[0]
    if (f && (f.name.endsWith('.xlsx') || f.name.endsWith('.xls'))) {
      setFile(f)
    }
  }

  const handleFileSelect = (e) => {
    const f = e.target.files[0]
    if (f) setFile(f)
  }

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch('/api/v1/excel/upload', { method: 'POST', body: formData })
      const data = await res.json()
      setResult({ success: true, data })
    } catch (err) {
      setResult({ success: false, error: err.message })
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Drop Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileRef.current?.click()}
        className={clsx(
          'cursor-pointer rounded-2xl border-2 border-dashed p-12 text-center transition-colors',
          dragOver ? 'border-brand-400 bg-brand-50' : 'border-surface-300 hover:border-brand-300 hover:bg-surface-50'
        )}
      >
        <input ref={fileRef} type="file" accept=".xlsx,.xls" onChange={handleFileSelect} className="hidden" />
        <Upload size={40} className={clsx('mx-auto mb-4', dragOver ? 'text-brand-500' : 'text-surface-300')} />
        <h3 className="text-base font-semibold text-surface-700 mb-1">
          {file ? file.name : 'Drop Excel file here or click to browse'}
        </h3>
        <p className="text-xs text-surface-400">Supports .xlsx and .xls files</p>
        {file && (
          <div className="mt-4 inline-flex items-center gap-2 rounded-lg bg-brand-50 px-3 py-2 text-xs font-medium text-brand-700">
            <FileSpreadsheet size={14} />
            {file.name} ({(file.size / 1024).toFixed(0)} KB)
          </div>
        )}
      </div>

      {/* Upload button */}
      {file && !result && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="w-full flex items-center justify-center gap-2 rounded-xl bg-brand-500 px-4 py-3 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50"
        >
          {uploading ? 'Processing...' : 'Upload & Parse'}
        </button>
      )}

      {/* Result */}
      {result && (
        <div className={clsx(
          'rounded-xl border p-5',
          result.success ? 'border-emerald-200 bg-emerald-50' : 'border-red-200 bg-red-50'
        )}>
          <div className="flex items-center gap-2 mb-2">
            {result.success
              ? <><CheckCircle size={18} className="text-emerald-600" /><span className="text-sm font-semibold text-emerald-700">Upload successful</span></>
              : <><AlertCircle size={18} className="text-red-600" /><span className="text-sm font-semibold text-red-700">Upload failed</span></>
            }
          </div>
          <p className="text-xs text-surface-600">
            {result.success ? `File "${result.data?.filename}" processed. Status: ${result.data?.status}` : result.error}
          </p>
          {result.success && (
            <button onClick={() => { setFile(null); setResult(null) }} className="mt-3 text-xs font-medium text-brand-600 hover:text-brand-700">
              Upload another file
            </button>
          )}
        </div>
      )}

      {/* Template download */}
      <div className="rounded-xl border border-surface-200 bg-white p-5 shadow-subtle">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-surface-700">Download Template</h3>
            <p className="text-xs text-surface-400 mt-0.5">Use this template to structure your cost data for upload</p>
          </div>
          <button className="flex items-center gap-1.5 rounded-lg border border-surface-200 px-3 py-2 text-xs font-medium text-surface-600 hover:bg-surface-50">
            <Download size={14} /> Download .xlsx
          </button>
        </div>
      </div>
    </div>
  )
}
