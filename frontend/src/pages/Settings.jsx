import { useState } from 'react'
import FormField, { Input } from '../components/shared/FormField'
import { Settings as SettingsIcon, Key, Server, Info } from 'lucide-react'

export default function Settings() {
  const [openaiKey, setOpenaiKey] = useState('')
  const [s4hanaUrl, setS4hanaUrl] = useState('')

  return (
    <div className="max-w-2xl space-y-6">
      {/* OpenAI Configuration */}
      <div className="rounded-xl border border-surface-200 bg-white p-6 shadow-subtle">
        <div className="flex items-center gap-2 mb-4">
          <Key size={18} className="text-brand-500" />
          <h3 className="text-sm font-semibold text-surface-700">AI Analysis (OpenAI)</h3>
        </div>
        <p className="text-xs text-surface-400 mb-4">
          Configure your OpenAI API key to enable AI-powered cost analysis and negotiation insights.
        </p>
        <FormField label="OpenAI API Key">
          <Input
            type="password"
            value={openaiKey}
            onChange={e => setOpenaiKey(e.target.value)}
            placeholder="sk-..."
          />
        </FormField>
        <div className="mt-3 flex items-start gap-2 rounded-lg bg-blue-50 border border-blue-200 p-3">
          <Info size={14} className="text-blue-500 mt-0.5" />
          <p className="text-xs text-blue-700">
            API key is stored server-side via environment variable. Set <code className="bg-blue-100 px-1 rounded">OPENAI_API_KEY</code> in your backend .env file.
          </p>
        </div>
      </div>

      {/* S/4HANA Integration */}
      <div className="rounded-xl border border-surface-200 bg-white p-6 shadow-subtle">
        <div className="flex items-center gap-2 mb-4">
          <Server size={18} className="text-surface-400" />
          <h3 className="text-sm font-semibold text-surface-700">SAP S/4HANA Integration</h3>
          <span className="rounded-full bg-surface-100 px-2 py-0.5 text-[10px] font-semibold text-surface-500">Coming Soon</span>
        </div>
        <p className="text-xs text-surface-400 mb-4">
          Connect to SAP S/4HANA to sync materials, BOMs, and pricing data automatically.
        </p>
        <div className="space-y-3 opacity-50 pointer-events-none">
          <FormField label="S/4HANA Base URL">
            <Input value={s4hanaUrl} onChange={e => setS4hanaUrl(e.target.value)} placeholder="https://s4hana.example.com/sap/opu/odata/" disabled />
          </FormField>
          <FormField label="Client ID">
            <Input placeholder="Enter client ID" disabled />
          </FormField>
          <FormField label="Client Secret">
            <Input type="password" placeholder="Enter client secret" disabled />
          </FormField>
        </div>
        <div className="mt-4 rounded-lg bg-surface-50 border border-surface-200 p-3">
          <p className="text-xs text-surface-500">
            S/4HANA integration endpoints are stubbed (returning 501). Full implementation planned for Phase 2.
          </p>
        </div>
      </div>
    </div>
  )
}
