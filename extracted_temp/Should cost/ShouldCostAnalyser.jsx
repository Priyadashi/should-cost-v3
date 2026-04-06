import { useState } from "react";

const USERS = [
  { id: 1, name: "Arjun Sharma", email: "arjun@mfg.com", password: "demo123", role: "Cost Engineer", avatar: "AS" },
  { id: 2, name: "Priya Nair", email: "priya@mfg.com", password: "demo123", role: "Senior Analyst", avatar: "PN" },
];
const CATEGORIES = ["Forging", "Casting", "Fabrication"];
const PROCESSES_BY_CAT = {
  Forging: ["Billet Cutting", "Heating", "Forging Press", "Trimming", "Heat Treatment", "Shot Blasting", "CNC Machining"],
  Casting: ["Pattern Making", "Moulding", "Melting", "Pouring", "Knockout", "Fettling", "Heat Treatment", "Machining"],
  Fabrication: ["Shearing", "Bending", "MIG Welding", "Grinding", "Drilling", "Surface Treatment", "Painting"],
};
const MACHINES_DB = [
  { id: 1, name: "CNC Machining Center", mhr: 1800 },
  { id: 2, name: "Hydraulic Press 500T", mhr: 2200 },
  { id: 3, name: "MIG Welding Station", mhr: 950 },
  { id: 4, name: "Lathe Machine", mhr: 1200 },
  { id: 5, name: "Induction Heater", mhr: 1600 },
  { id: 6, name: "Shot Blasting Machine", mhr: 800 },
  { id: 7, name: "Heat Treatment Furnace", mhr: 1400 },
  { id: 8, name: "Press Brake", mhr: 1100 },
];
const MATERIALS_DB = [
  { id: 1, grade: "EN8 (Medium Carbon Steel)", rate: 68 },
  { id: 2, grade: "EN19 (Alloy Steel)", rate: 95 },
  { id: 3, grade: "SS304 (Stainless Steel)", rate: 210 },
  { id: 4, grade: "IS2062 E250 (Mild Steel)", rate: 58 },
  { id: 5, grade: "EN24 (High Tensile Steel)", rate: 112 },
  { id: 6, grade: "ADC12 (Aluminium Die Cast)", rate: 185 },
  { id: 7, grade: "GG25 (Grey Cast Iron)", rate: 52 },
];
const OVERHEAD_FIELDS = [
  { key: "factory", label: "Factory Overhead" },
  { key: "admin", label: "Admin Overhead" },
  { key: "depreciation", label: "Depreciation" },
  { key: "quality", label: "Quality Cost" },
  { key: "profit", label: "Profit Margin" },
  { key: "taxes", label: "Taxes & Duties" },
];
const SAMPLE_SHEETS = [
  { id: 1, name: "Connecting Rod - EN8", partNo: "CR-2024-001", category: "Forging", status: "Final", createdAt: "2024-01-15", grand: 487.32, scenarios: 2 },
  { id: 2, name: "Pump Housing - GG25", partNo: "PH-2024-007", category: "Casting", status: "Draft", createdAt: "2024-01-22", grand: 1243.80, scenarios: 1 },
  { id: 3, name: "Bracket Assembly - IS2062", partNo: "BA-2024-012", category: "Fabrication", status: "Review", createdAt: "2024-02-03", grand: 312.55, scenarios: 0 },
];

const C = { bg: "#040b17", surface: "#0c1526", border: "#1e293b", text: "#e2e8f0", muted: "#475569", dim: "#334155", amber: "#f59e0b", green: "#34d399", blue: "#3b82f6", purple: "#a78bfa", red: "#ef4444", indigo: "#818cf8" };
const inp = (ex = {}) => ({ background: "#070d1a", border: `1px solid ${C.border}`, borderRadius: 7, color: C.text, padding: "8px 12px", fontSize: 12, outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box", ...ex });
const btn = (ex = {}) => ({ border: "none", borderRadius: 7, cursor: "pointer", fontFamily: "inherit", fontWeight: 700, fontSize: 11, ...ex });
const card = (ex = {}) => ({ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, padding: "18px 20px", ...ex });
const lbl = { fontSize: 9, color: C.dim, fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 5, display: "block" };

const newScenario = (name = "Base Scenario") => ({ id: Date.now() + Math.random(), name, rm: { materialId: "", grossWt: "", netWt: "", scrapPct: "", scrapRate: "" }, processes: [], overhead: { factory: "", admin: "", depreciation: "", quality: "", profit: "", taxes: "" } });
const calcRM = (rm) => { const mat = MATERIALS_DB.find(m => m.id === +rm.materialId); const rate = mat ? mat.rate : 0; const g = +rm.grossWt || 0, n = +rm.netWt || 0, sp = +rm.scrapPct || 0, sr = +rm.scrapRate || 0; const gross = g * rate, scrapCredit = (g - n) * (sp / 100) * sr; return { gross, scrapCredit, net: Math.max(gross - scrapCredit, 0), yield: g ? (n / g * 100) : 0, rate }; };
const calcProc = (processes) => { let machine = 0, manpower = 0, setup = 0, tooling = 0; processes.forEach(p => { const mc = p.mhr && p.cycleTime ? (p.mhr / 60) * +p.cycleTime : 0; machine += mc; manpower += +p.manpower || 0; setup += +p.setup || 0; tooling += +p.tooling || 0; }); return { machine, manpower, setup, tooling, total: machine + manpower + setup + tooling }; };
const calcOH = (oh, base) => { let total = 0; const breakdown = {}; OVERHEAD_FIELDS.forEach(({ key }) => { const v = base * ((+oh[key] || 0) / 100); breakdown[key] = v; total += v; }); return { breakdown, total }; };
const calcGrand = (scenario) => { const rm = calcRM(scenario.rm), proc = calcProc(scenario.processes); const base = rm.net + proc.total, oh = calcOH(scenario.overhead, base); return { rm, proc, oh, base, grand: base + oh.total }; };

function WaterfallChart({ scenarios }) {
  const colors = [C.amber, C.blue];
  const allCalcs = scenarios.map(s => calcGrand(s));
  const segments = ["Raw Material", "Machine", "Manpower", "Setup", "Tooling", "Overheads", "Total"];
  const getVals = (c) => [c.rm.net, c.proc.machine, c.proc.manpower, c.proc.setup, c.proc.tooling, c.oh.total, c.grand];
  const allVals = allCalcs.flatMap(c => getVals(c));
  const maxVal = Math.max(...allVals) * 1.2 || 100;
  const W = 580, H = 230, pad = { l: 65, r: 10, t: 24, b: 64 };
  const chartW = W - pad.l - pad.r, chartH = H - pad.t - pad.b;
  const barW = scenarios.length === 1 ? 44 : 28;
  const slotW = chartW / segments.length;
  return (
    <svg width="100%" viewBox={`0 0 ${W} ${H}`} style={{ fontFamily: "inherit" }}>
      {[0, 0.25, 0.5, 0.75, 1].map(r => { const y = pad.t + chartH * (1 - r); return <g key={r}><line x1={pad.l} x2={W - pad.r} y1={y} y2={y} stroke={C.border} strokeWidth={0.5} /><text x={pad.l - 6} y={y + 3} fontSize={7} fill={C.dim} textAnchor="end">₹{Math.round(maxVal * r)}</text></g>; })}
      {segments.map((seg, si) => { const cx = pad.l + slotW * si + slotW / 2; return (<g key={seg}>{allCalcs.map((c, ci) => { const val = getVals(c)[si]; const barH = (val / maxVal) * chartH; const x = cx + (ci - (scenarios.length - 1) / 2) * (barW + 8) - barW / 2; const y = pad.t + chartH - barH; const isTotal = si === segments.length - 1; return (<g key={ci}><rect x={x} y={y} width={barW} height={Math.max(barH, 1)} fill={isTotal ? colors[ci] : colors[ci] + "88"} rx={3} />{barH > 14 && <text x={x + barW / 2} y={y - 4} fontSize={6.5} fill={colors[ci]} textAnchor="middle" fontWeight="700">₹{val.toFixed(0)}</text>}</g>); })}<text x={cx} y={H - pad.b + 14} fontSize={7.5} fill={C.muted} textAnchor="middle">{seg}</text></g>); })}
      {scenarios.map((s, i) => (<g key={i} transform={`translate(${pad.l + i * 140},${H - 10})`}><rect width={10} height={10} fill={colors[i]} rx={2} /><text x={14} y={8} fontSize={8} fill={C.muted}>{s.name}</text></g>))}
    </svg>
  );
}

function ComparisonTable({ scenarios }) {
  if (scenarios.length < 2) return null;
  const [a, b] = scenarios.map(s => calcGrand(s));
  const rows = [{ l: "Raw Material Cost", av: a.rm.net, bv: b.rm.net }, { l: "  ↳ Material Rate (₹/kg)", av: a.rm.rate, bv: b.rm.rate, sub: true }, { l: "Machine Cost", av: a.proc.machine, bv: b.proc.machine }, { l: "Manpower Cost", av: a.proc.manpower, bv: b.proc.manpower }, { l: "Setup Cost", av: a.proc.setup, bv: b.proc.setup }, { l: "Tooling Cost", av: a.proc.tooling, bv: b.proc.tooling }, { l: "Total Process Cost", av: a.proc.total, bv: b.proc.total, bold: true }, { l: "Overhead Cost", av: a.oh.total, bv: b.oh.total }, { l: "TOTAL SHOULD COST", av: a.grand, bv: b.grand, total: true }];
  return (
    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
      <thead><tr style={{ background: "#07101f", borderBottom: `1px solid ${C.border}` }}>{["Cost Element", scenarios[0].name, scenarios[1].name, "Diff (₹)", "Diff (%)"].map((h, i) => <th key={h} style={{ padding: "9px 12px", textAlign: i === 0 ? "left" : "right", color: i === 1 ? C.amber : i === 2 ? C.blue : C.dim, fontSize: 9, fontWeight: 700, letterSpacing: "0.08em" }}>{h.toUpperCase()}</th>)}</tr></thead>
      <tbody>{rows.map(({ l, av, bv, sub, bold, total }) => { const d = bv - av, pct = av ? (d / av * 100) : 0, dc = d < 0 ? C.green : d > 0 ? C.red : C.muted; return (<tr key={l} style={{ borderBottom: `1px solid ${total ? C.green + "44" : "#0a1525"}`, background: total ? "#1a3528" : sub ? "transparent" : C.surface }}><td style={{ padding: sub ? "5px 12px 5px 20px" : "9px 12px", color: total ? C.green : sub ? C.dim : C.muted, fontSize: sub ? 10 : 12, fontWeight: bold || total ? 700 : 400 }}>{l}</td><td style={{ padding: "9px 12px", textAlign: "right", color: total ? C.amber : C.text, fontWeight: total ? 800 : 400, fontSize: total ? 14 : 12 }}>₹{av.toFixed(2)}</td><td style={{ padding: "9px 12px", textAlign: "right", color: total ? C.blue : C.text, fontWeight: total ? 800 : 400, fontSize: total ? 14 : 12 }}>₹{bv.toFixed(2)}</td><td style={{ padding: "9px 12px", textAlign: "right", color: dc, fontWeight: 600 }}>{d !== 0 ? `${d > 0 ? "+" : ""}₹${d.toFixed(2)}` : "—"}</td><td style={{ padding: "9px 12px", textAlign: "right", color: dc, fontWeight: 600 }}>{pct !== 0 ? `${pct > 0 ? "+" : ""}${pct.toFixed(1)}%` : "—"}</td></tr>); })}</tbody>
    </table>
  );
}

function ProcRow({ p, i, cat, onUp, onRem }) {
  const mc = p.mhr && p.cycleTime ? (p.mhr / 60) * +p.cycleTime : 0;
  const tot = mc + (+p.manpower || 0) + (+p.setup || 0) + (+p.tooling || 0);
  return (
    <tr style={{ borderBottom: `1px solid #07101f` }}>
      <td style={{ padding: "6px 8px", color: C.dim, fontSize: 11 }}>{i + 1}</td>
      <td style={{ padding: "6px 8px" }}><select value={p.name} onChange={e => onUp(i, "name", e.target.value)} style={inp({ width: 140, padding: "5px 8px", fontSize: 11 })}><option value="">-- Process --</option>{(PROCESSES_BY_CAT[cat] || []).map(x => <option key={x}>{x}</option>)}</select></td>
      <td style={{ padding: "6px 8px" }}><select value={p.machineId} onChange={e => { const m = MACHINES_DB.find(m => m.id === +e.target.value); onUp(i, "machineId", e.target.value); if (m) onUp(i, "mhr", m.mhr); }} style={inp({ width: 160, padding: "5px 8px", fontSize: 11 })}><option value="">-- Machine --</option>{MACHINES_DB.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}</select></td>
      <td style={{ padding: "6px 8px", textAlign: "right", color: C.amber, fontWeight: 700, fontSize: 11 }}>{p.mhr ? `₹${p.mhr.toLocaleString()}` : "—"}</td>
      <td style={{ padding: "6px 8px" }}><input type="number" value={p.cycleTime} onChange={e => onUp(i, "cycleTime", e.target.value)} placeholder="min" style={inp({ width: 60, textAlign: "right", padding: "5px 7px", fontSize: 11 })} /></td>
      <td style={{ padding: "6px 8px", textAlign: "right", color: C.indigo, fontWeight: 600, fontSize: 11 }}>{mc > 0 ? `₹${mc.toFixed(2)}` : "—"}</td>
      <td style={{ padding: "6px 8px" }}><input type="number" value={p.manpower} onChange={e => onUp(i, "manpower", e.target.value)} placeholder="₹" style={inp({ width: 70, textAlign: "right", padding: "5px 7px", fontSize: 11 })} /></td>
      <td style={{ padding: "6px 8px" }}><input type="number" value={p.setup} onChange={e => onUp(i, "setup", e.target.value)} placeholder="₹" style={inp({ width: 70, textAlign: "right", padding: "5px 7px", fontSize: 11 })} /></td>
      <td style={{ padding: "6px 8px" }}><input type="number" value={p.tooling} onChange={e => onUp(i, "tooling", e.target.value)} placeholder="₹" style={inp({ width: 70, textAlign: "right", padding: "5px 7px", fontSize: 11 })} /></td>
      <td style={{ padding: "6px 8px" }}><div style={{ background: tot > 0 ? "#1a3528" : "#0c1526", border: `1px solid ${tot > 0 ? C.green : C.border}`, borderRadius: 6, padding: "5px 8px", color: tot > 0 ? C.green : C.dim, fontWeight: 700, textAlign: "right", fontSize: 11, minWidth: 65 }}>{tot > 0 ? `₹${tot.toFixed(2)}` : "—"}</div></td>
      <td style={{ padding: "6px 8px" }}><button onClick={() => onRem(i)} style={btn({ background: "transparent", border: `1px solid ${C.red}44`, color: C.red, padding: "3px 7px", fontSize: 10 })}>✕</button></td>
    </tr>
  );
}

function CostSheetEditor({ onBack }) {
  const [partName, setPartName] = useState(""); const [partNo, setPartNo] = useState(""); const [qty, setQty] = useState(""); const [category, setCategory] = useState("Forging");
  const [scenarios, setScenarios] = useState([newScenario("Base Scenario")]); const [activeScen, setActiveScen] = useState(0); const [activeTab, setActiveTab] = useState("rm"); const [showOutput, setShowOutput] = useState(false);
  const scen = scenarios[activeScen];
  const updScen = (field, val) => { const s = [...scenarios]; s[activeScen] = { ...s[activeScen], [field]: val }; setScenarios(s); };
  const updRM = (f, v) => updScen("rm", { ...scen.rm, [f]: v });
  const updOH = (f, v) => updScen("overhead", { ...scen.overhead, [f]: v });
  const addProc = () => updScen("processes", [...scen.processes, { name: "", machineId: "", mhr: null, cycleTime: "", manpower: "", setup: "", tooling: "" }]);
  const updProc = (i, f, v) => { const ps = [...scen.processes]; ps[i] = { ...ps[i], [f]: v }; updScen("processes", ps); };
  const remProc = (i) => updScen("processes", scen.processes.filter((_, j) => j !== i));
  const addScenario = () => { if (scenarios.length >= 2) return; const s = [...scenarios, newScenario("Scenario 2")]; setScenarios(s); setActiveScen(s.length - 1); };
  const calc = calcGrand(scen);
  const matFound = MATERIALS_DB.find(m => m.id === +scen.rm.materialId);

  return (
    <div style={{ minHeight: "100vh", background: C.bg, fontFamily: "'IBM Plex Mono',monospace", color: C.text }}>
      <div style={{ background: C.bg, borderBottom: `1px solid ${C.border}`, padding: "0 20px", height: 52, display: "flex", alignItems: "center", justifyContent: "space-between", position: "sticky", top: 0, zIndex: 99 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <button onClick={onBack} style={btn({ background: "transparent", border: `1px solid ${C.border}`, color: C.muted, padding: "5px 12px" })}>← Back</button>
          <div style={{ fontSize: 12, fontWeight: 700 }}>{partName || "New Cost Sheet"}</div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={() => setShowOutput(!showOutput)} style={btn({ background: showOutput ? C.amber : "transparent", border: `1px solid ${showOutput ? C.amber : C.border}`, color: showOutput ? "#000" : C.muted, padding: "6px 14px" })}>{showOutput ? "← Edit Inputs" : "View Output →"}</button>
          <button style={btn({ background: `linear-gradient(135deg,${C.amber},#d97706)`, color: "#000", padding: "6px 14px" })}>Save Sheet</button>
        </div>
      </div>
      <div style={{ padding: "18px 20px", maxWidth: 1280, margin: "0 auto" }}>
        <div style={{ ...card(), display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 14, marginBottom: 16 }}>
          {[{ l: "Part Name", v: partName, s: setPartName, p: "e.g. Connecting Rod" }, { l: "Part Number", v: partNo, s: setPartNo, p: "e.g. CR-001" }, { l: "Annual Qty", v: qty, s: setQty, p: "0", t: "number" }].map(({ l, v, s, p, t }) => (
            <div key={l}><label style={lbl}>{l}</label><input type={t || "text"} value={v} onChange={e => s(e.target.value)} placeholder={p} style={inp()} /></div>
          ))}
          <div><label style={lbl}>Category</label><select value={category} onChange={e => setCategory(e.target.value)} style={inp()}>{CATEGORIES.map(c => <option key={c}>{c}</option>)}</select></div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
          {scenarios.map((s, i) => <button key={s.id} onClick={() => setActiveScen(i)} style={btn({ background: activeScen === i ? (i === 0 ? C.amber + "22" : C.blue + "22") : "transparent", border: `1px solid ${activeScen === i ? (i === 0 ? C.amber : C.blue) : C.border}`, color: activeScen === i ? (i === 0 ? C.amber : C.blue) : C.muted, padding: "7px 16px", borderRadius: 8 })}>{s.name}</button>)}
          {scenarios.length < 2 && <button onClick={addScenario} style={btn({ background: "transparent", border: `1px dashed ${C.border}`, color: C.dim, padding: "7px 14px", borderRadius: 8 })}>+ Add Scenario</button>}
          {scenarios.length === 2 && <div style={{ marginLeft: "auto", fontSize: 10, color: C.green, border: `1px solid ${C.green}44`, borderRadius: 6, padding: "4px 10px" }}>⚡ Comparison Active</div>}
        </div>
        {!showOutput ? (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: 16 }}>
            <div>
              <div style={{ display: "flex", borderBottom: `1px solid ${C.border}`, marginBottom: 16 }}>
                {[["rm", "Raw Material"], ["process", "Process Cost"], ["overhead", "Overheads"]].map(([id, label]) => <button key={id} onClick={() => setActiveTab(id)} style={btn({ background: "transparent", border: "none", borderBottom: activeTab === id ? `2px solid ${C.amber}` : "2px solid transparent", color: activeTab === id ? C.amber : C.dim, padding: "9px 18px", borderRadius: 0, fontSize: 10, letterSpacing: "0.07em" })}>{label.toUpperCase()}</button>)}
              </div>
              {activeTab === "rm" && (
                <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                  <div style={card()}>
                    <div style={{ fontSize: 10, fontWeight: 700, color: C.dim, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 12, paddingBottom: 8, borderBottom: `1px solid ${C.border}` }}>Material Selection</div>
                    <div style={{ marginBottom: 14 }}><label style={lbl}>Material Grade (Database)</label><select value={scen.rm.materialId} onChange={e => updRM("materialId", e.target.value)} style={inp()}><option value="">-- Select Material --</option>{MATERIALS_DB.map(m => <option key={m.id} value={m.id}>{m.grade} — ₹{m.rate}/kg</option>)}</select></div>
                    {matFound && <div style={{ background: "#07101f", borderRadius: 8, padding: "10px 14px", marginBottom: 14 }}><span style={{ color: C.dim, fontSize: 10 }}>Rate: <strong style={{ color: C.amber }}>₹{matFound.rate}/kg</strong> &nbsp;|&nbsp; {matFound.grade}</span></div>}
                    <div style={{ fontSize: 10, fontWeight: 700, color: C.dim, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 12, paddingBottom: 8, borderBottom: `1px solid ${C.border}` }}>Weight & Scrap</div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
                      {[["grossWt", "Gross Weight (kg)"], ["netWt", "Net Weight (kg)"], ["scrapPct", "Scrap Recovery (%)"], ["scrapRate", "Scrap Rate (₹/kg)"]].map(([k, l]) => <div key={k}><label style={lbl}>{l}</label><input type="number" placeholder="0.00" value={scen.rm[k] || ""} onChange={e => updRM(k, e.target.value)} style={inp()} /></div>)}
                    </div>
                  </div>
                  <div style={card({ background: "#07101f" })}>
                    <div style={{ fontSize: 10, fontWeight: 700, color: C.dim, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 12 }}>RM Cost Output</div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                      {[{ l: "Gross Cost", v: `₹${calc.rm.gross.toFixed(2)}` }, { l: "Scrap Credit", v: `₹${calc.rm.scrapCredit.toFixed(2)}` }, { l: "Net RM Cost", v: `₹${calc.rm.net.toFixed(2)}`, hi: true }, { l: "Yield %", v: `${calc.rm.yield.toFixed(1)}%` }].map(({ l, v, hi }) => (
                        <div key={l} style={{ background: hi ? "#1a3528" : C.surface, border: `1px solid ${hi ? C.green : C.border}`, borderRadius: 8, padding: "10px 12px" }}>
                          <div style={{ fontSize: 9, color: C.dim, fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 4 }}>{l}</div>
                          <div style={{ fontSize: 15, fontWeight: 800, color: hi ? C.green : C.text }}>{v}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
              {activeTab === "process" && (
                <div style={card()}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
                    <div style={{ fontSize: 10, fontWeight: 700, color: C.dim, letterSpacing: "0.1em", textTransform: "uppercase" }}>Process Operations — {category}</div>
                    <button onClick={addProc} style={btn({ background: `linear-gradient(135deg,${C.amber},#d97706)`, color: "#000", padding: "6px 13px" })}>+ Add Process</button>
                  </div>
                  <div style={{ overflowX: "auto" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                      <thead><tr style={{ background: "#07101f", borderBottom: `1px solid ${C.border}` }}>{["#", "Process", "Machine", "MHR", "Cycle(min)", "Mach.Cost", "Manpower", "Setup", "Tooling", "Total", ""].map(h => <th key={h} style={{ padding: "7px 8px", textAlign: "left", color: C.dim, fontSize: 8, fontWeight: 700, letterSpacing: "0.07em", textTransform: "uppercase", whiteSpace: "nowrap" }}>{h}</th>)}</tr></thead>
                      <tbody>
                        {scen.processes.length === 0 ? <tr><td colSpan={11} style={{ padding: "30px", textAlign: "center", color: C.border }}><div style={{ fontSize: 20, marginBottom: 6 }}>⚙</div><div style={{ fontSize: 11 }}>Click + Add Process to begin</div></td></tr> : scen.processes.map((p, i) => <ProcRow key={i} p={p} i={i} cat={category} onUp={updProc} onRem={remProc} />)}
                      </tbody>
                      {scen.processes.length > 0 && <tfoot><tr style={{ background: "#07101f", borderTop: `1px solid ${C.border}` }}><td colSpan={9} style={{ padding: "8px", color: C.muted, fontWeight: 700, fontSize: 9 }}>TOTAL PROCESS COST</td><td style={{ padding: "8px" }}><div style={{ background: "#1a3528", border: `1px solid ${C.green}`, borderRadius: 6, padding: "5px 8px", color: C.green, fontWeight: 900, fontSize: 13, textAlign: "right" }}>₹{calc.proc.total.toFixed(2)}</div></td><td></td></tr></tfoot>}
                    </table>
                  </div>
                </div>
              )}
              {activeTab === "overhead" && (
                <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                  <div style={card()}>
                    <div style={{ fontSize: 10, fontWeight: 700, color: C.dim, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 14 }}>Overhead Rates (% of Base Cost)</div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
                      {OVERHEAD_FIELDS.map(({ key, label }) => <div key={key}><label style={lbl}>{label}</label><div style={{ position: "relative" }}><input type="number" placeholder="0" value={scen.overhead[key] || ""} onChange={e => updOH(key, e.target.value)} style={inp({ paddingRight: 28 })} /><span style={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", color: C.dim, fontSize: 11 }}>%</span></div></div>)}
                    </div>
                  </div>
                  <div style={card({ background: "#07101f" })}>
                    <div style={{ fontSize: 10, fontWeight: 700, color: C.dim, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 12 }}>Overhead Breakdown</div>
                    {OVERHEAD_FIELDS.map(({ key, label }) => { const pct = +scen.overhead[key] || 0, val = calc.base * pct / 100; return (<div key={key} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 12px", background: C.surface, borderRadius: 7, marginBottom: 5 }}><span style={{ color: C.muted, fontSize: 11 }}>{label}</span><div style={{ display: "flex", gap: 14 }}><span style={{ color: C.dim, fontSize: 10 }}>{pct}%</span><span style={{ color: C.text, fontWeight: 700, minWidth: 70, textAlign: "right" }}>₹{val.toFixed(2)}</span></div></div>); })}
                    <div style={{ display: "flex", justifyContent: "space-between", padding: "10px 12px", background: "#1a3528", borderRadius: 7, border: `1px solid ${C.green}`, marginTop: 8 }}><span style={{ color: C.green, fontWeight: 700 }}>Total Overhead</span><span style={{ color: C.green, fontWeight: 900, fontSize: 14 }}>₹{calc.oh.total.toFixed(2)}</span></div>
                  </div>
                </div>
              )}
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div style={card({ background: "#07101f" })}>
                <div style={{ fontSize: 10, fontWeight: 700, color: C.dim, letterSpacing: "0.1em", marginBottom: 10 }}>LIVE COST SUMMARY</div>
                <div style={{ fontSize: 10, color: C.amber, fontWeight: 700, marginBottom: 8 }}>{scen.name}</div>
                {[{ l: "Raw Material", v: calc.rm.net, c: C.blue }, { l: "Process Total", v: calc.proc.total, c: C.purple }, { l: "Overhead", v: calc.oh.total, c: C.amber }].map(({ l, v, c }) => <div key={l} style={{ display: "flex", justifyContent: "space-between", padding: "7px 0", borderBottom: `1px solid #07101f` }}><span style={{ color: C.muted, fontSize: 11 }}>{l}</span><span style={{ color: c, fontWeight: 600, fontSize: 11 }}>₹{v.toFixed(2)}</span></div>)}
                <div style={{ marginTop: 10, padding: "12px 14px", background: "#1a3528", borderRadius: 10, border: `1px solid ${C.green}` }}>
                  <div style={{ fontSize: 9, color: C.green, letterSpacing: "0.1em" }}>TOTAL SHOULD COST</div>
                  <div style={{ fontSize: 24, fontWeight: 900, color: C.green, marginTop: 4 }}>₹{calc.grand.toFixed(2)}</div>
                  <div style={{ fontSize: 9, color: C.dim }}>per piece</div>
                </div>
              </div>
              <div style={card()}>
                <div style={{ fontSize: 10, fontWeight: 700, color: C.dim, letterSpacing: "0.1em", marginBottom: 10 }}>COST SPLIT</div>
                {[{ l: "RM", v: calc.rm.net, c: C.blue }, { l: "Process", v: calc.proc.total, c: C.purple }, { l: "Overhead", v: calc.oh.total, c: C.amber }].map(({ l, v, c }) => { const pct = calc.grand ? (v / calc.grand * 100) : 0; return (<div key={l} style={{ marginBottom: 10 }}><div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}><span style={{ fontSize: 10, color: C.muted }}>{l}</span><span style={{ fontSize: 10, color: c, fontWeight: 700 }}>{pct.toFixed(1)}%</span></div><div style={{ background: "#07101f", borderRadius: 4, height: 6 }}><div style={{ width: `${pct}%`, height: "100%", background: c, borderRadius: 4, transition: "width 0.3s" }} /></div></div>); })}
              </div>
            </div>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ display: "grid", gridTemplateColumns: scenarios.length === 2 ? "1fr 1fr" : "1fr", gap: 12 }}>
              {scenarios.map((s, i) => { const c = calcGrand(s), col = i === 0 ? C.amber : C.blue; return (<div key={s.id} style={{ ...card(), border: `1px solid ${col}44` }}><div style={{ fontSize: 9, color: col, fontWeight: 700, letterSpacing: "0.1em", marginBottom: 10 }}>{s.name.toUpperCase()}</div><div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 8 }}>{[["Raw Material", c.rm.net, C.blue], ["Process", c.proc.total, C.purple], ["Overhead", c.oh.total, C.amber], ["Total", c.grand, C.green]].map(([label, val, color]) => (<div key={label} style={{ background: "#07101f", borderRadius: 7, padding: "8px 10px" }}><div style={{ fontSize: 8, color: C.dim, textTransform: "uppercase", letterSpacing: "0.07em" }}>{label}</div><div style={{ fontSize: label === "Total" ? 14 : 12, fontWeight: 800, color, marginTop: 4 }}>₹{val.toFixed(2)}</div></div>))}</div></div>); })}
            </div>
            <div style={card()}><div style={{ fontSize: 10, fontWeight: 700, color: C.dim, letterSpacing: "0.1em", marginBottom: 14 }}>COST WATERFALL CHART</div><WaterfallChart scenarios={scenarios} /></div>
            {scenarios.length === 2 && (
              <div style={card()}>
                <div style={{ fontSize: 10, fontWeight: 700, color: C.dim, letterSpacing: "0.1em", marginBottom: 14 }}>SCENARIO COMPARISON</div>
                <ComparisonTable scenarios={scenarios} />
                {(() => { const [a, b] = scenarios.map(s => calcGrand(s)); const saving = a.grand - b.grand; return (<div style={{ marginTop: 14, padding: "12px 16px", background: "#07101f", borderRadius: 8, display: "flex", alignItems: "center", gap: 16 }}><div style={{ fontSize: 10, color: C.dim }}>Scenario 2 vs Base:</div><div style={{ fontSize: 16, fontWeight: 900, color: saving > 0 ? C.green : C.red }}>{saving > 0 ? "▼" : "▲"} ₹{Math.abs(saving).toFixed(2)} / piece</div><div style={{ fontSize: 10, color: saving > 0 ? C.green : C.red }}>({saving > 0 ? "-" : "+"}{Math.abs(a.grand ? saving / a.grand * 100 : 0).toFixed(1)}%)</div>{qty && <div style={{ fontSize: 10, color: C.muted }}>Annual: ₹{(Math.abs(saving) * +qty).toLocaleString()}</div>}</div>); })()}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function Dashboard({ user, onNew, onLogout }) {
  const [search, setSearch] = useState("");
  const filtered = SAMPLE_SHEETS.filter(s => s.name.toLowerCase().includes(search.toLowerCase()) || s.partNo.toLowerCase().includes(search.toLowerCase()));
  const statusColor = { Final: C.green, Draft: C.amber, Review: C.blue };
  return (
    <div style={{ minHeight: "100vh", background: C.bg, fontFamily: "'IBM Plex Mono',monospace", color: C.text }}>
      <div style={{ background: C.bg, borderBottom: `1px solid ${C.border}`, padding: "0 24px", height: 52, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 26, height: 26, background: `linear-gradient(135deg,${C.amber},${C.red})`, borderRadius: 6, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 900, fontSize: 12, color: "#000" }}>₹</div>
          <div><div style={{ fontWeight: 800, fontSize: 12, letterSpacing: "0.08em" }}>SHOULD COST ANALYSER</div><div style={{ fontSize: 8, color: C.dim, letterSpacing: "0.1em" }}>MANUFACTURING COST ENGINEERING</div></div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 28, height: 28, background: `linear-gradient(135deg,${C.purple},${C.blue})`, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 800 }}>{user.avatar}</div>
          <div><div style={{ fontSize: 11, fontWeight: 700 }}>{user.name}</div><div style={{ fontSize: 9, color: C.dim }}>{user.role}</div></div>
          <button onClick={onLogout} style={btn({ background: "transparent", border: `1px solid ${C.border}`, color: C.dim, padding: "5px 10px" })}>Logout</button>
        </div>
      </div>
      <div style={{ padding: "24px", maxWidth: 1200, margin: "0 auto" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12, marginBottom: 24 }}>
          {[{ l: "Total Cost Sheets", v: 3, c: C.blue, icon: "📋" }, { l: "Final / Approved", v: 1, c: C.green, icon: "✅" }, { l: "Draft / Review", v: 2, c: C.amber, icon: "📝" }, { l: "With Scenarios", v: 2, c: C.purple, icon: "⚡" }].map(({ l, v, c, icon }) => (
            <div key={l} style={card()}><div style={{ display: "flex", justifyContent: "space-between" }}><div style={{ fontSize: 9, color: C.dim, fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase" }}>{l}</div><div style={{ fontSize: 18 }}>{icon}</div></div><div style={{ fontSize: 28, fontWeight: 900, color: c, marginTop: 8 }}>{v}</div></div>
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
          <div><div style={{ fontSize: 13, fontWeight: 700 }}>Cost Sheets</div><div style={{ fontSize: 10, color: C.dim }}>All should cost analyses</div></div>
          <div style={{ display: "flex", gap: 8 }}>
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search..." style={inp({ width: 200, padding: "7px 12px", fontSize: 11 })} />
            <button onClick={onNew} style={btn({ background: `linear-gradient(135deg,${C.amber},#d97706)`, color: "#000", padding: "7px 16px" })}>+ New Cost Sheet</button>
          </div>
        </div>
        <div style={card({ padding: 0, overflow: "hidden" })}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr style={{ background: "#07101f", borderBottom: `1px solid ${C.border}` }}>{["Part Name", "Part No.", "Category", "Status", "Scenarios", "Should Cost", "Created", "Actions"].map(h => <th key={h} style={{ padding: "10px 16px", textAlign: "left", color: C.dim, fontSize: 9, fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase" }}>{h}</th>)}</tr></thead>
            <tbody>
              {filtered.map((s, i) => (
                <tr key={s.id} style={{ borderBottom: `1px solid #07101f`, background: i % 2 === 0 ? C.surface : "#0a1220" }}>
                  <td style={{ padding: "12px 16px", fontWeight: 600, fontSize: 12 }}>{s.name}</td>
                  <td style={{ padding: "12px 16px", color: C.dim, fontSize: 11 }}>{s.partNo}</td>
                  <td style={{ padding: "12px 16px" }}><span style={{ background: C.border + "44", borderRadius: 5, padding: "3px 8px", fontSize: 10, color: C.muted }}>{s.category}</span></td>
                  <td style={{ padding: "12px 16px" }}><span style={{ background: statusColor[s.status] + "22", border: `1px solid ${statusColor[s.status]}44`, borderRadius: 5, padding: "3px 8px", fontSize: 10, color: statusColor[s.status], fontWeight: 700 }}>{s.status}</span></td>
                  <td style={{ padding: "12px 16px" }}>{s.scenarios > 0 ? <span style={{ color: C.purple, fontWeight: 700, fontSize: 11 }}>⚡ {s.scenarios}</span> : <span style={{ color: C.border }}>—</span>}</td>
                  <td style={{ padding: "12px 16px", color: C.green, fontWeight: 800, fontSize: 13 }}>₹{s.grand.toFixed(2)}</td>
                  <td style={{ padding: "12px 16px", color: C.dim, fontSize: 10 }}>{s.createdAt}</td>
                  <td style={{ padding: "12px 16px" }}><button onClick={onNew} style={btn({ background: "transparent", border: `1px solid ${C.border}`, color: C.muted, padding: "4px 10px", fontSize: 10 })}>Open</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function Login({ onLogin }) {
  const [email, setEmail] = useState(""); const [pass, setPass] = useState(""); const [err, setErr] = useState("");
  const handleLogin = () => { const u = USERS.find(u => u.email === email && u.password === pass); if (u) onLogin(u); else setErr("Invalid credentials. Try arjun@mfg.com / demo123"); };
  return (
    <div style={{ minHeight: "100vh", background: C.bg, fontFamily: "'IBM Plex Mono',monospace", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ width: 380 }}>
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{ width: 48, height: 48, background: `linear-gradient(135deg,${C.amber},${C.red})`, borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 900, fontSize: 22, color: "#000", margin: "0 auto 16px" }}>₹</div>
          <div style={{ fontSize: 18, fontWeight: 800, letterSpacing: "0.08em" }}>SHOULD COST ANALYSER</div>
          <div style={{ fontSize: 10, color: C.dim, letterSpacing: "0.12em", marginTop: 4 }}>MANUFACTURING COST ENGINEERING</div>
        </div>
        <div style={card()}>
          <div style={{ fontSize: 11, fontWeight: 700, color: C.muted, marginBottom: 20, letterSpacing: "0.1em" }}>SIGN IN TO CONTINUE</div>
          <div style={{ marginBottom: 14 }}><label style={lbl}>Email Address</label><input type="email" value={email} onChange={e => { setEmail(e.target.value); setErr(""); }} placeholder="you@company.com" style={inp()} onKeyDown={e => e.key === "Enter" && handleLogin()} /></div>
          <div style={{ marginBottom: 20 }}><label style={lbl}>Password</label><input type="password" value={pass} onChange={e => { setPass(e.target.value); setErr(""); }} placeholder="••••••••" style={inp()} onKeyDown={e => e.key === "Enter" && handleLogin()} /></div>
          {err && <div style={{ fontSize: 10, color: C.red, marginBottom: 14, padding: "8px 12px", background: C.red + "11", borderRadius: 7, border: `1px solid ${C.red}44` }}>{err}</div>}
          <button onClick={handleLogin} style={btn({ background: `linear-gradient(135deg,${C.amber},#d97706)`, color: "#000", padding: "10px", width: "100%", fontSize: 12, letterSpacing: "0.06em" })}>SIGN IN</button>
          <div style={{ marginTop: 16, padding: "10px 12px", background: "#07101f", borderRadius: 7, fontSize: 10, color: C.dim }}>Demo: <span style={{ color: C.amber }}>arjun@mfg.com</span> / <span style={{ color: C.amber }}>demo123</span></div>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [view, setView] = useState("dashboard");
  if (!user) return <Login onLogin={u => { setUser(u); setView("dashboard"); }} />;
  if (view === "editor") return <CostSheetEditor onBack={() => setView("dashboard")} />;
  return <Dashboard user={user} onNew={() => setView("editor")} onLogout={() => setUser(null)} />;
}
