import api from './client'

export const fetchParts = (params) => api.get('/parts', { params })
export const fetchPart = (id) => api.get(`/parts/${id}`)
export const createPart = (data) => api.post('/parts', data)
export const updatePart = (id, data) => api.put(`/parts/${id}`, data)
export const deletePart = (id) => api.delete(`/parts/${id}`)
export const fetchBom = (partId) => api.get(`/parts/${partId}/bom`)
export const replaceBom = (partId, lines) => api.put(`/parts/${partId}/bom`, lines)
export const fetchRouting = (partId) => api.get(`/parts/${partId}/routing`)
export const replaceRouting = (partId, steps) => api.put(`/parts/${partId}/routing`, steps)
