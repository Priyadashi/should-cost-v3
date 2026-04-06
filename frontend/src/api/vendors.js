import api from './client'

export const fetchVendors = () => api.get('/vendors')
export const fetchVendor = (id) => api.get(`/vendors/${id}`)
export const createVendor = (data) => api.post('/vendors', data)
export const updateVendor = (id, data) => api.put(`/vendors/${id}`, data)
export const deleteVendor = (id) => api.delete(`/vendors/${id}`)
