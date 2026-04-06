import api from './client'

export const fetchProcessTemplates = (params) => api.get('/process-templates', { params })
export const fetchProcessTemplate = (id) => api.get(`/process-templates/${id}`)
export const createProcessTemplate = (data) => api.post('/process-templates', data)
export const updateProcessTemplate = (id, data) => api.put(`/process-templates/${id}`, data)
export const deleteProcessTemplate = (id) => api.delete(`/process-templates/${id}`)
