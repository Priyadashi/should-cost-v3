import api from './client'

export const fetchMachines = () => api.get('/machines')
export const fetchMachine = (id) => api.get(`/machines/${id}`)
export const createMachine = (data) => api.post('/machines', data)
export const updateMachine = (id, data) => api.put(`/machines/${id}`, data)
export const deleteMachine = (id) => api.delete(`/machines/${id}`)
