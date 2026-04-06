import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import CostSheetsList from './pages/CostSheetsList'
import CostSheetBuilder from './pages/CostSheetBuilder'
import CostSheetOutput from './pages/CostSheetOutput'
import ScenarioComparison from './pages/ScenarioComparison'
import MaterialsList from './pages/MaterialsList'
import MachinesList from './pages/MachinesList'
import ProcessTemplatesList from './pages/ProcessTemplatesList'
import VendorsList from './pages/VendorsList'
import OverheadProfilesList from './pages/OverheadProfilesList'
import ExcelUpload from './pages/ExcelUpload'
import Settings from './pages/Settings'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/cost-sheets" element={<CostSheetsList />} />
        <Route path="/cost-sheets/new" element={<CostSheetBuilder />} />
        <Route path="/cost-sheets/:id/edit" element={<CostSheetBuilder />} />
        <Route path="/cost-sheets/:id/output" element={<CostSheetOutput />} />
        <Route path="/cost-sheets/compare" element={<ScenarioComparison />} />
        <Route path="/materials" element={<MaterialsList />} />
        <Route path="/machines" element={<MachinesList />} />
        <Route path="/process-templates" element={<ProcessTemplatesList />} />
        <Route path="/vendors" element={<VendorsList />} />
        <Route path="/overhead-profiles" element={<OverheadProfilesList />} />
        <Route path="/excel-upload" element={<ExcelUpload />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}
