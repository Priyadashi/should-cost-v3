import api from './client'

export const fetchCostSheets = (params) => api.get('/cost-sheets', { params })
export const fetchCostSheet = (id) => api.get(`/cost-sheets/${id}`)
export const createCostSheet = (data) => api.post('/cost-sheets', data)
export const updateCostSheet = (id, data) => api.put(`/cost-sheets/${id}`, data)
export const deleteCostSheet = (id) => api.delete(`/cost-sheets/${id}`)
export const calculateCostSheet = (id, data = {}) => api.post(`/cost-sheets/${id}/calculate`, data)
export const fetchResults = (id) => api.get(`/cost-sheets/${id}/results`)
export const fetchRecommendations = (id) => api.get(`/cost-sheets/${id}/recommendations`)
export const compareCostSheets = (sheetIds) => api.post('/cost-sheets/compare', { sheet_ids: sheetIds })
