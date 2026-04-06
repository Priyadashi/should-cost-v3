import { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { usePart, useParts, useMaterials, useMachines, useOverheadProfiles, useCreatePart, useCreateCostSheet, useCalculateCostSheet, useReplaceBom, useReplaceRouting } from '../hooks/useApi'
import FormField, { Input, Select } from '../components/shared/FormField'
import { CurrencyDisplay } from '../components/shared/StatusBadge'
import { Plus, Trash2, GripVertical, Calculator, Save, ArrowLeft } from 'lucide-react'
import clsx from 'clsx'

const TABS = [
  { id: 'bom', label: 'Raw Material' },
  { id: 'routing', label: 'Process Routing' },
  { id: 'overhead', label: 'Overheads' },
]

export default function CostSheetBuilder() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isEditing = !!id

  // Data queries
  const { data: materials = [] } = useMaterials()
  const { data: machines = [] } = useMachines()
  const { data: overheadProfiles = [] } = useOverheadProfiles()
  const { data: parts = [] } = useParts()
  const { data: existingPart } = usePart(isEditing ? null : null) // TODO: load from cost sheet

  // Mutations
  const createPart = useCreatePart()
  const createCostSheet = useCreateCostSheet()
  const calculateSheet = useCalculateCostSheet()
  const replaceBom = useReplaceBom()
  const replaceRouting = useReplaceRouting()

  // Form state
  const [activeTab, setActiveTab] = useState('bom')
  const [partForm, setPartForm] = useState({
    part_no: '', name: '', commodity_type: 'Forging', annual_volume: '5000',
  })
  const [selectedPartId, setSelectedPartId] = useState('')
  const [quotedPrice, setQuotedPrice] = useState('')
  const [scenarioName, setScenarioName] = useState('Base Scenario')
  const [selectedProfileId, setSelectedProfileId] = useState('')

  // BOM lines
  const [bomLines, setBomLines] = useState([
    { material_id: '', gross_weight_kg: '', net_weight_kg: '', scrap_rate_per_kg: '0' }
  ])

  // Routing steps
  const [routingSteps, setRoutingSteps] = useState([])

  // Overhead overrides
  const [overheadOverrides, setOverheadOverrides] = useState({})

  const [saving, setSaving] = useState(false)
  const [calculating, setCalculating] = useState(false)

  // When a profile is selected, load its values
  const selectedProfile = useMemo(() => {
    return overheadProfiles.find(p => String(p.id) === String(selectedProfileId))
  }, [overheadProfiles, selectedProfileId])

  // Auto-select default profile
  useEffect(() => {
    if (overheadProfiles.length && !selectedProfileId) {
      const def = overheadProfiles.find(p => p.is_default) || overheadProfiles[0]
      if (def) setSelectedProfileId(String(def.id))
    }
  }, [overheadProfiles])

  // Live cost calculations
  const liveBomCost = useMemo(() => {
    let total = 0
    bomLines.forEach(line => {
      const mat = materials.find(m => String(m.id) === String(line.material_id))
      if (!mat) return
      const gross = parseFloat(line.gross_weight_kg) || 0
      const net = parseFloat(line.net_weight_kg) || 0
      const grossCost = gross * mat.rate_per_kg
      const scrapCredit = (gross - net) * mat.rate_per_kg * mat.scrap_recovery_pct
      total += grossCost - scrapCredit
    })
    return total
  }, [bomLines, materials])

  const liveRoutingCost = useMemo(() => {
    let total = 0
    routingSteps.forEach(step => {
      const mach = machines.find(m => String(m.id) === String(step.machine_id))
      const rate = mach ? mach.hourly_rate : 0
      const cycle = parseFloat(step.cycle_time_min) || 0
      const setup = parseFloat(step.setup_time_min) || 0
      const batchSize = parseInt(step.batch_size) || 100
      const laborRate = parseFloat(step.labor_rate_per_hr) || 0
      const operators = parseInt(step.operators) || 1
      const machineCost = (cycle / 60) * rate
      const setupCost = (setup / 60) * rate / batchSize
      const laborTime = cycle + setup / batchSize
      const laborCost = (laborTime / 60) * laborRate * operators
      const tooling = parseFloat(step.tooling_cost_per_unit) || 0
      total += machineCost + setupCost + laborCost + tooling
    })
    return total
  }, [routingSteps, machines])

  const liveOverheadCost = useMemo(() => {
    if (!selectedProfile) return 0
    const base = liveRoutingCost
    const oh = selectedProfile
    return base * (oh.factory_overhead_pct + oh.admin_overhead_pct + oh.depreciation_pct + oh.quality_cost_pct)
  }, [liveRoutingCost, selectedProfile])

  const liveTotal = liveBomCost + liveRoutingCost + liveOverheadCost

  // BOM handlers
  const addBomLine = () => setBomLines([...bomLines, { material_id: '', gross_weight_kg: '', net_weight_kg: '', scrap_rate_per_kg: '0' }])
  const updateBomLine = (i, field, value) => {
    const lines = [...bomLines]
    lines[i] = { ...lines[i], [field]: value }
    setBomLines(lines)
  }
  const removeBomLine = (i) => setBomLines(bomLines.filter((_, j) => j !== i))

  // Routing handlers
  const addRoutingStep = () => setRoutingSteps([...routingSteps, {
    sequence: routingSteps.length + 1, operation_name: '', machine_id: '',
    cycle_time_min: '', setup_time_min: '0', batch_size: '100',
    operators: '1', labor_rate_per_hr: '350', tooling_cost_per_unit: '0',
  }])
  const updateRoutingStep = (i, field, value) => {
    const steps = [...routingSteps]
    steps[i] = { ...steps[i], [field]: value }
    setRoutingSteps(steps)
  }
  const removeRoutingStep = (i) => setRoutingSteps(
    routingSteps.filter((_, j) => j !== i).map((s, j) => ({ ...s, sequence: j + 1 }))
  )

  // Save & Calculate
  const handleCalculate = async () => {
    try {
      setCalculating(true)
      let partId = selectedPartId

      // Create part if new
      if (!partId) {
        const part = await createPart.mutateAsync({
          part_no: partForm.part_no || `PART-${Date.now()}`,
          name: partForm.name || 'Unnamed Part',
          commodity_type: partForm.commodity_type,
          annual_volume: parseInt(partForm.annual_volume) || 1000,
        })
        partId = part.id
        setSelectedPartId(String(partId))
      }

      // Save BOM
      const bomPayload = bomLines
        .filter(l => l.material_id)
        .map(l => ({
          material_id: parseInt(l.material_id),
          gross_weight_kg: parseFloat(l.gross_weight_kg) || 0,
          net_weight_kg: parseFloat(l.net_weight_kg) || 0,
          scrap_rate_per_kg: parseFloat(l.scrap_rate_per_kg) || 0,
        }))
      await replaceBom.mutateAsync({ partId, lines: bomPayload })

      // Save Routing
      const routingPayload = routingSteps
        .filter(s => s.operation_name)
        .map(s => ({
          sequence: s.sequence,
          operation_name: s.operation_name,
          machine_id: s.machine_id ? parseInt(s.machine_id) : null,
          cycle_time_min: parseFloat(s.cycle_time_min) || 0,
          setup_time_min: parseFloat(s.setup_time_min) || 0,
          batch_size: parseInt(s.batch_size) || 100,
          operators: parseInt(s.operators) || 1,
          labor_rate_per_hr: parseFloat(s.labor_rate_per_hr) || 0,
          tooling_cost_per_unit: parseFloat(s.tooling_cost_per_unit) || 0,
        }))
      await replaceRouting.mutateAsync({ partId, steps: routingPayload })

      // Create cost sheet
      const sheet = await createCostSheet.mutateAsync({
        part_id: parseInt(partId),
        scenario_name: scenarioName,
        quoted_price: parseFloat(quotedPrice) || 0,
        overhead_profile_id: selectedProfileId ? parseInt(selectedProfileId) : null,
      })

      // Calculate
      const result = await calculateSheet.mutateAsync({
        id: sheet.id,
        data: { batch_size: 100, learning_curve_factor: 1.0 },
      })

      navigate(`/cost-sheets/${sheet.id}/output`)
    } catch (err) {
      console.error('Calculate failed:', err)
      alert('Calculation failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setCalculating(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="flex items-center gap-1 rounded-lg border border-surface-200 px-3 py-1.5 text-xs font-medium text-surface-500 hover:bg-surface-50">
            <ArrowLeft size={14} /> Back
          </button>
          <h2 className="text-lg font-semibold text-surface-800">
            {partForm.name || 'New Cost Sheet'}
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCalculate}
            disabled={calculating}
            className="flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50 transition-colors"
          >
            <Calculator size={16} />
            {calculating ? 'Calculating...' : 'Calculate'}
          </button>
        </div>
      </div>

      {/* Part Header */}
      <div className="rounded-xl border border-surface-200 bg-white p-5 shadow-subtle">
        <div className="grid grid-cols-5 gap-4">
          <FormField label="Part Name">
            <Input value={partForm.name} onChange={e => setPartForm({...partForm, name: e.target.value})} placeholder="e.g. Connecting Rod" />
          </FormField>
          <FormField label="Part Number">
            <Input value={partForm.part_no} onChange={e => setPartForm({...partForm, part_no: e.target.value})} placeholder="e.g. CR-2024-001" />
          </FormField>
          <FormField label="Annual Volume">
            <Input type="number" value={partForm.annual_volume} onChange={e => setPartForm({...partForm, annual_volume: e.target.value})} />
          </FormField>
          <FormField label="Commodity">
            <Select value={partForm.commodity_type} onChange={e => setPartForm({...partForm, commodity_type: e.target.value})}>
              <option>Forging</option><option>Casting</option><option>Fabrication</option>
            </Select>
          </FormField>
          <FormField label="Quoted Price (₹/unit)">
            <Input type="number" value={quotedPrice} onChange={e => setQuotedPrice(e.target.value)} placeholder="0.00" />
          </FormField>
        </div>
      </div>

      {/* Main Content: Tabs + Live Sidebar */}
      <div className="grid grid-cols-[1fr_280px] gap-4">
        <div>
          {/* Tabs */}
          <div className="flex border-b border-surface-200 mb-4">
            {TABS.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={clsx(
                  'px-4 py-2.5 text-xs font-semibold uppercase tracking-wider border-b-2 transition-colors',
                  activeTab === tab.id
                    ? 'border-brand-500 text-brand-600'
                    : 'border-transparent text-surface-400 hover:text-surface-600'
                )}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* BOM Tab */}
          {activeTab === 'bom' && (
            <div className="space-y-3">
              {bomLines.map((line, i) => {
                const mat = materials.find(m => String(m.id) === String(line.material_id))
                const gross = parseFloat(line.gross_weight_kg) || 0
                const net = parseFloat(line.net_weight_kg) || 0
                const grossCost = mat ? gross * mat.rate_per_kg : 0
                const scrapCredit = mat ? (gross - net) * mat.rate_per_kg * mat.scrap_recovery_pct : 0
                const netCost = grossCost - scrapCredit
                const yieldPct = gross > 0 ? (net / gross * 100) : 0

                return (
                  <div key={i} className="rounded-xl border border-surface-200 bg-white p-4 shadow-subtle">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-semibold text-surface-400 uppercase">Material #{i + 1}</span>
                      {bomLines.length > 1 && (
                        <button onClick={() => removeBomLine(i)} className="text-surface-400 hover:text-red-500">
                          <Trash2 size={14} />
                        </button>
                      )}
                    </div>
                    <div className="grid grid-cols-4 gap-3 mb-3">
                      <FormField label="Material Grade" className="col-span-2">
                        <Select value={line.material_id} onChange={e => updateBomLine(i, 'material_id', e.target.value)}>
                          <option value="">Select material...</option>
                          {materials.map(m => (
                            <option key={m.id} value={m.id}>{m.grade} — ₹{m.rate_per_kg}/kg</option>
                          ))}
                        </Select>
                      </FormField>
                      <FormField label="Gross Weight (kg)">
                        <Input type="number" step="0.01" value={line.gross_weight_kg} onChange={e => updateBomLine(i, 'gross_weight_kg', e.target.value)} placeholder="0.00" />
                      </FormField>
                      <FormField label="Net Weight (kg)">
                        <Input type="number" step="0.01" value={line.net_weight_kg} onChange={e => updateBomLine(i, 'net_weight_kg', e.target.value)} placeholder="0.00" />
                      </FormField>
                    </div>
                    {mat && (
                      <div className="grid grid-cols-4 gap-3 rounded-lg bg-surface-50 p-3">
                        <div>
                          <div className="text-[10px] font-semibold text-surface-400 uppercase">Rate</div>
                          <div className="text-sm font-semibold font-mono text-brand-600">₹{mat.rate_per_kg}/kg</div>
                        </div>
                        <div>
                          <div className="text-[10px] font-semibold text-surface-400 uppercase">Gross Cost</div>
                          <div className="text-sm font-mono">₹{grossCost.toFixed(2)}</div>
                        </div>
                        <div>
                          <div className="text-[10px] font-semibold text-surface-400 uppercase">Scrap Credit</div>
                          <div className="text-sm font-mono text-emerald-600">-₹{scrapCredit.toFixed(2)}</div>
                        </div>
                        <div>
                          <div className="text-[10px] font-semibold text-surface-400 uppercase">Net RM Cost</div>
                          <div className="text-sm font-bold font-mono text-surface-800">₹{netCost.toFixed(2)}</div>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
              <button onClick={addBomLine} className="flex items-center gap-1.5 rounded-lg border border-dashed border-surface-300 px-4 py-2.5 text-xs font-medium text-surface-500 hover:border-brand-300 hover:text-brand-600 w-full justify-center">
                <Plus size={14} /> Add Material
              </button>
            </div>
          )}

          {/* Routing Tab */}
          {activeTab === 'routing' && (
            <div className="space-y-3">
              {routingSteps.length === 0 ? (
                <div className="rounded-xl border border-surface-200 bg-white p-8 text-center">
                  <p className="text-sm text-surface-400 mb-3">No process steps yet</p>
                  <button onClick={addRoutingStep} className="inline-flex items-center gap-1.5 rounded-lg bg-brand-500 px-4 py-2 text-xs font-semibold text-white hover:bg-brand-600">
                    <Plus size={14} /> Add Process Step
                  </button>
                </div>
              ) : (
                <>
                  <div className="rounded-xl border border-surface-200 bg-white shadow-subtle overflow-hidden">
                    <table className="w-full">
                      <thead>
                        <tr className="bg-surface-50 border-b border-surface-100">
                          {['#', 'Operation', 'Machine', 'Cycle (min)', 'Setup (min)', 'Batch', 'Operators', 'Labor ₹/hr', 'Tooling ₹/pc', 'Cost', ''].map(h => (
                            <th key={h} className="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-wider text-surface-400">{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {routingSteps.map((step, i) => {
                          const mach = machines.find(m => String(m.id) === String(step.machine_id))
                          const rate = mach ? mach.hourly_rate : 0
                          const cycle = parseFloat(step.cycle_time_min) || 0
                          const setup = parseFloat(step.setup_time_min) || 0
                          const batch = parseInt(step.batch_size) || 100
                          const laborRate = parseFloat(step.labor_rate_per_hr) || 0
                          const ops = parseInt(step.operators) || 1
                          const mcCost = (cycle / 60) * rate
                          const setupCost = (setup / 60) * rate / batch
                          const laborTime = cycle + setup / batch
                          const laborCost = (laborTime / 60) * laborRate * ops
                          const tooling = parseFloat(step.tooling_cost_per_unit) || 0
                          const total = mcCost + setupCost + laborCost + tooling

                          return (
                            <tr key={i} className="border-b border-surface-100 last:border-0">
                              <td className="px-3 py-2 text-xs text-surface-400 font-mono">{step.sequence}</td>
                              <td className="px-3 py-2">
                                <Input value={step.operation_name} onChange={e => updateRoutingStep(i, 'operation_name', e.target.value)} placeholder="e.g. Forging Press" className="!h-7 !text-xs" />
                              </td>
                              <td className="px-3 py-2">
                                <Select value={step.machine_id} onChange={e => updateRoutingStep(i, 'machine_id', e.target.value)} className="!h-7 !text-xs">
                                  <option value="">Select...</option>
                                  {machines.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
                                </Select>
                              </td>
                              <td className="px-3 py-2"><Input type="number" step="0.1" value={step.cycle_time_min} onChange={e => updateRoutingStep(i, 'cycle_time_min', e.target.value)} className="!h-7 !text-xs !w-16" /></td>
                              <td className="px-3 py-2"><Input type="number" step="0.1" value={step.setup_time_min} onChange={e => updateRoutingStep(i, 'setup_time_min', e.target.value)} className="!h-7 !text-xs !w-16" /></td>
                              <td className="px-3 py-2"><Input type="number" value={step.batch_size} onChange={e => updateRoutingStep(i, 'batch_size', e.target.value)} className="!h-7 !text-xs !w-16" /></td>
                              <td className="px-3 py-2"><Input type="number" value={step.operators} onChange={e => updateRoutingStep(i, 'operators', e.target.value)} className="!h-7 !text-xs !w-12" /></td>
                              <td className="px-3 py-2"><Input type="number" value={step.labor_rate_per_hr} onChange={e => updateRoutingStep(i, 'labor_rate_per_hr', e.target.value)} className="!h-7 !text-xs !w-16" /></td>
                              <td className="px-3 py-2"><Input type="number" value={step.tooling_cost_per_unit} onChange={e => updateRoutingStep(i, 'tooling_cost_per_unit', e.target.value)} className="!h-7 !text-xs !w-16" /></td>
                              <td className="px-3 py-2">
                                <span className={clsx('text-xs font-semibold font-mono', total > 0 ? 'text-emerald-600' : 'text-surface-400')}>
                                  {total > 0 ? `₹${total.toFixed(2)}` : '—'}
                                </span>
                              </td>
                              <td className="px-3 py-2">
                                <button onClick={() => removeRoutingStep(i)} className="text-surface-400 hover:text-red-500"><Trash2 size={13} /></button>
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                      <tfoot>
                        <tr className="bg-surface-50 border-t border-surface-200">
                          <td colSpan={9} className="px-3 py-2 text-xs font-semibold text-surface-500 uppercase">Total Process Cost</td>
                          <td className="px-3 py-2">
                            <span className="text-sm font-bold font-mono text-emerald-600">₹{liveRoutingCost.toFixed(2)}</span>
                          </td>
                          <td></td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                  <button onClick={addRoutingStep} className="flex items-center gap-1.5 rounded-lg border border-dashed border-surface-300 px-4 py-2.5 text-xs font-medium text-surface-500 hover:border-brand-300 hover:text-brand-600 w-full justify-center">
                    <Plus size={14} /> Add Process Step
                  </button>
                </>
              )}
            </div>
          )}

          {/* Overhead Tab */}
          {activeTab === 'overhead' && (
            <div className="space-y-4">
              <div className="rounded-xl border border-surface-200 bg-white p-5 shadow-subtle">
                <FormField label="Overhead Profile" className="mb-4">
                  <Select value={selectedProfileId} onChange={e => setSelectedProfileId(e.target.value)}>
                    <option value="">Select profile...</option>
                    {overheadProfiles.map(p => (
                      <option key={p.id} value={p.id}>{p.name}{p.is_default ? ' (Default)' : ''}</option>
                    ))}
                  </Select>
                </FormField>
                {selectedProfile && (
                  <div className="grid grid-cols-3 gap-4">
                    {[
                      ['Factory Overhead', 'factory_overhead_pct'],
                      ['Admin Overhead', 'admin_overhead_pct'],
                      ['Depreciation', 'depreciation_pct'],
                      ['Quality Cost', 'quality_cost_pct'],
                      ['Profit Margin', 'profit_margin_pct'],
                      ['Taxes & Duties', 'taxes_duties_pct'],
                      ['SGA', 'sga_pct'],
                    ].map(([label, key]) => (
                      <div key={key} className="rounded-lg bg-surface-50 p-3">
                        <div className="text-[10px] font-semibold text-surface-400 uppercase mb-1">{label}</div>
                        <div className="text-lg font-bold font-mono text-surface-700">
                          {(selectedProfile[key] * 100).toFixed(0)}%
                        </div>
                      </div>
                    ))}
                    {[
                      ['Packaging/unit', 'packaging_per_unit'],
                      ['Freight/unit', 'freight_per_unit'],
                    ].map(([label, key]) => (
                      <div key={key} className="rounded-lg bg-surface-50 p-3">
                        <div className="text-[10px] font-semibold text-surface-400 uppercase mb-1">{label}</div>
                        <div className="text-lg font-bold font-mono text-surface-700">
                          ₹{selectedProfile[key]}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <FormField label="Scenario Name">
                <Input value={scenarioName} onChange={e => setScenarioName(e.target.value)} />
              </FormField>
            </div>
          )}
        </div>

        {/* Live Cost Sidebar */}
        <div className="space-y-3">
          <div className="sticky top-20 space-y-3">
            <div className="rounded-xl border border-surface-200 bg-white p-4 shadow-subtle">
              <div className="text-xs font-semibold text-surface-400 uppercase mb-3">Live Cost Preview</div>
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-surface-500">Raw Material</span>
                  <span className="text-sm font-semibold font-mono text-surface-700">₹{liveBomCost.toFixed(2)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-surface-500">Process Cost</span>
                  <span className="text-sm font-semibold font-mono text-surface-700">₹{liveRoutingCost.toFixed(2)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-surface-500">Overhead</span>
                  <span className="text-sm font-semibold font-mono text-surface-700">₹{liveOverheadCost.toFixed(2)}</span>
                </div>
                <div className="border-t border-surface-200 pt-2 flex items-center justify-between">
                  <span className="text-xs font-semibold text-surface-600">Estimated Total</span>
                  <span className="text-lg font-bold font-mono text-brand-600">₹{liveTotal.toFixed(2)}</span>
                </div>
              </div>
            </div>

            {quotedPrice && liveTotal > 0 && (
              <div className="rounded-xl border border-surface-200 bg-white p-4 shadow-subtle">
                <div className="text-xs font-semibold text-surface-400 uppercase mb-2">Gap Analysis</div>
                {(() => {
                  const quoted = parseFloat(quotedPrice)
                  const gap = quoted - liveTotal
                  const gapPct = quoted > 0 ? (gap / quoted * 100) : 0
                  return (
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-xs text-surface-500">Quoted</span>
                        <span className="text-sm font-mono">₹{quoted.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-xs text-surface-500">Gap</span>
                        <span className={clsx('text-sm font-bold font-mono', gap > 0 ? 'text-emerald-600' : 'text-red-500')}>
                          {gap > 0 ? '+' : ''}₹{gap.toFixed(2)} ({gapPct.toFixed(1)}%)
                        </span>
                      </div>
                    </div>
                  )
                })()}
              </div>
            )}

            <button
              onClick={handleCalculate}
              disabled={calculating || liveBomCost === 0}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-brand-500 px-4 py-3 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50 transition-colors"
            >
              <Calculator size={16} />
              {calculating ? 'Calculating...' : 'Calculate & View Results'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
