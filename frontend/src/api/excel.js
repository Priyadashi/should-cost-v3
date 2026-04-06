import api from './client'

export const uploadExcel = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/excel/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const fetchUploadStatus = (id) => api.get(`/excel/upload/${id}/status`)
export const downloadTemplate = () => api.get('/excel/download/template')
export const downloadCostSheet = (id) => api.get(`/excel/download/cost-sheet/${id}`)
