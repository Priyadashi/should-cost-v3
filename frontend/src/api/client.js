import axios from 'axios'

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL || '') + '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// Ensure trailing slashes to avoid 307 redirects that strip CORS headers
api.interceptors.request.use((config) => {
  if (config.url) {
    const [path, query] = config.url.split('?')
    if (!path.endsWith('/')) {
      config.url = path + '/' + (query ? '?' + query : '')
    }
  }
  return config
})

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const message = err.response?.data?.detail || err.message
    console.error('API Error:', message)
    return Promise.reject(err)
  }
)

export default api
