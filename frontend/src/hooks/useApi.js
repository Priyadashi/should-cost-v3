import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as materialsApi from '../api/materials'
import * as machinesApi from '../api/machines'
import * as vendorsApi from '../api/vendors'
import * as processTemplatesApi from '../api/processTemplates'
import * as overheadProfilesApi from '../api/overheadProfiles'
import * as partsApi from '../api/parts'
import * as costSheetsApi from '../api/costSheets'
import * as dashboardApi from '../api/dashboard'

// Generic CRUD hook factory
function useCrudHooks(key, api) {
  const useList = (params) => useQuery({ queryKey: [key, params], queryFn: () => api.fetchAll ? api.fetchAll(params) : api.fetch(params) })
  const useOne = (id) => useQuery({ queryKey: [key, id], queryFn: () => api.fetchOne(id), enabled: !!id })

  const useCreate = () => {
    const qc = useQueryClient()
    return useMutation({
      mutationFn: api.create,
      onSuccess: () => qc.invalidateQueries({ queryKey: [key] }),
    })
  }

  const useUpdate = () => {
    const qc = useQueryClient()
    return useMutation({
      mutationFn: ({ id, data }) => api.update(id, data),
      onSuccess: () => qc.invalidateQueries({ queryKey: [key] }),
    })
  }

  const useDelete = () => {
    const qc = useQueryClient()
    return useMutation({
      mutationFn: api.remove,
      onSuccess: () => qc.invalidateQueries({ queryKey: [key] }),
    })
  }

  return { useList, useOne, useCreate, useUpdate, useDelete }
}

// Materials
export const useMaterials = () => useQuery({ queryKey: ['materials'], queryFn: materialsApi.fetchMaterials })
export const useMaterial = (id) => useQuery({ queryKey: ['materials', id], queryFn: () => materialsApi.fetchMaterial(id), enabled: !!id })
export const useCreateMaterial = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: materialsApi.createMaterial, onSuccess: () => qc.invalidateQueries({ queryKey: ['materials'] }) })
}
export const useUpdateMaterial = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ id, data }) => materialsApi.updateMaterial(id, data), onSuccess: () => qc.invalidateQueries({ queryKey: ['materials'] }) })
}
export const useDeleteMaterial = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: materialsApi.deleteMaterial, onSuccess: () => qc.invalidateQueries({ queryKey: ['materials'] }) })
}

// Machines
export const useMachines = () => useQuery({ queryKey: ['machines'], queryFn: machinesApi.fetchMachines })
export const useMachine = (id) => useQuery({ queryKey: ['machines', id], queryFn: () => machinesApi.fetchMachine(id), enabled: !!id })
export const useCreateMachine = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: machinesApi.createMachine, onSuccess: () => qc.invalidateQueries({ queryKey: ['machines'] }) })
}
export const useUpdateMachine = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ id, data }) => machinesApi.updateMachine(id, data), onSuccess: () => qc.invalidateQueries({ queryKey: ['machines'] }) })
}
export const useDeleteMachine = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: machinesApi.deleteMachine, onSuccess: () => qc.invalidateQueries({ queryKey: ['machines'] }) })
}

// Vendors
export const useVendors = () => useQuery({ queryKey: ['vendors'], queryFn: vendorsApi.fetchVendors })
export const useCreateVendor = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: vendorsApi.createVendor, onSuccess: () => qc.invalidateQueries({ queryKey: ['vendors'] }) })
}
export const useUpdateVendor = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ id, data }) => vendorsApi.updateVendor(id, data), onSuccess: () => qc.invalidateQueries({ queryKey: ['vendors'] }) })
}
export const useDeleteVendor = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: vendorsApi.deleteVendor, onSuccess: () => qc.invalidateQueries({ queryKey: ['vendors'] }) })
}

// Process Templates
export const useProcessTemplates = (commodity) => useQuery({
  queryKey: ['processTemplates', commodity],
  queryFn: () => processTemplatesApi.fetchProcessTemplates({ commodity_type: commodity })
})
export const useCreateProcessTemplate = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: processTemplatesApi.createProcessTemplate, onSuccess: () => qc.invalidateQueries({ queryKey: ['processTemplates'] }) })
}
export const useUpdateProcessTemplate = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ id, data }) => processTemplatesApi.updateProcessTemplate(id, data), onSuccess: () => qc.invalidateQueries({ queryKey: ['processTemplates'] }) })
}
export const useDeleteProcessTemplate = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: processTemplatesApi.deleteProcessTemplate, onSuccess: () => qc.invalidateQueries({ queryKey: ['processTemplates'] }) })
}

// Overhead Profiles
export const useOverheadProfiles = () => useQuery({ queryKey: ['overheadProfiles'], queryFn: overheadProfilesApi.fetchOverheadProfiles })
export const useCreateOverheadProfile = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: overheadProfilesApi.createOverheadProfile, onSuccess: () => qc.invalidateQueries({ queryKey: ['overheadProfiles'] }) })
}
export const useUpdateOverheadProfile = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ id, data }) => overheadProfilesApi.updateOverheadProfile(id, data), onSuccess: () => qc.invalidateQueries({ queryKey: ['overheadProfiles'] }) })
}
export const useDeleteOverheadProfile = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: overheadProfilesApi.deleteOverheadProfile, onSuccess: () => qc.invalidateQueries({ queryKey: ['overheadProfiles'] }) })
}

// Parts
export const useParts = (params) => useQuery({ queryKey: ['parts', params], queryFn: () => partsApi.fetchParts(params) })
export const usePart = (id) => useQuery({ queryKey: ['parts', id], queryFn: () => partsApi.fetchPart(id), enabled: !!id })
export const useCreatePart = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: partsApi.createPart, onSuccess: () => qc.invalidateQueries({ queryKey: ['parts'] }) })
}
export const useUpdatePart = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ id, data }) => partsApi.updatePart(id, data), onSuccess: () => qc.invalidateQueries({ queryKey: ['parts'] }) })
}
export const useDeletePart = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: partsApi.deletePart, onSuccess: () => qc.invalidateQueries({ queryKey: ['parts'] }) })
}
export const useReplaceBom = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ partId, lines }) => partsApi.replaceBom(partId, lines), onSuccess: (_, { partId }) => qc.invalidateQueries({ queryKey: ['parts', partId] }) })
}
export const useReplaceRouting = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ partId, steps }) => partsApi.replaceRouting(partId, steps), onSuccess: (_, { partId }) => qc.invalidateQueries({ queryKey: ['parts', partId] }) })
}

// Cost Sheets
export const useCostSheets = (params) => useQuery({ queryKey: ['costSheets', params], queryFn: () => costSheetsApi.fetchCostSheets(params) })
export const useCostSheet = (id) => useQuery({ queryKey: ['costSheets', id], queryFn: () => costSheetsApi.fetchCostSheet(id), enabled: !!id })
export const useCreateCostSheet = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: costSheetsApi.createCostSheet, onSuccess: () => qc.invalidateQueries({ queryKey: ['costSheets'] }) })
}
export const useUpdateCostSheet = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ id, data }) => costSheetsApi.updateCostSheet(id, data), onSuccess: () => qc.invalidateQueries({ queryKey: ['costSheets'] }) })
}
export const useDeleteCostSheet = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: costSheetsApi.deleteCostSheet, onSuccess: () => qc.invalidateQueries({ queryKey: ['costSheets'] }) })
}
export const useCalculateCostSheet = () => {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ id, data }) => costSheetsApi.calculateCostSheet(id, data), onSuccess: (_, { id }) => { qc.invalidateQueries({ queryKey: ['costSheets'] }); qc.invalidateQueries({ queryKey: ['costSheets', id] }) } })
}
export const useCompareCostSheets = () => {
  return useMutation({ mutationFn: costSheetsApi.compareCostSheets })
}

// Dashboard
export const useDashboardSummary = () => useQuery({ queryKey: ['dashboard', 'summary'], queryFn: dashboardApi.fetchDashboardSummary })
export const useRecentActivity = (limit) => useQuery({ queryKey: ['dashboard', 'activity', limit], queryFn: () => dashboardApi.fetchRecentActivity(limit) })
