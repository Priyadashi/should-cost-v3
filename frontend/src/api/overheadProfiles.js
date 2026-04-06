import api from './client'

export const fetchOverheadProfiles = () => api.get('/overhead-profiles')
export const fetchOverheadProfile = (id) => api.get(`/overhead-profiles/${id}`)
export const createOverheadProfile = (data) => api.post('/overhead-profiles', data)
export const updateOverheadProfile = (id, data) => api.put(`/overhead-profiles/${id}`, data)
export const deleteOverheadProfile = (id) => api.delete(`/overhead-profiles/${id}`)
