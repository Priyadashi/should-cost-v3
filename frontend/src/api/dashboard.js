import api from './client'

export const fetchDashboardSummary = () => api.get('/dashboard/summary')
export const fetchRecentActivity = (limit = 10) => api.get('/dashboard/recent-activity', { params: { limit } })
