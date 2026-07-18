import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1' })

export const getDashboard   = () => api.get('/dashboard')
export const getHealth      = () => api.get('/business-health')
export const getAlerts      = () => api.get('/alerts')
export const getTimeline    = () => api.get('/timeline')
export const getRevenueForecast  = () => api.get('/forecast/revenue')
export const getCashflowForecast = () => api.get('/forecast/cashflow')
export const getDemandForecast   = () => api.get('/forecast/demand')
export const getCustomerRisk     = () => api.get('/risk/customers')
export const getSupplierRisk     = () => api.get('/risk/suppliers')
export const getPricing          = () => api.get('/pricing')
export const getAgents       = () => api.get('/agents')
export const getRecommendations  = () => api.get('/recommendations')
export const simulate = (data: object) => api.post('/simulate', data)
export const sendChat = (question: string) =>
  api.post('/ai/chat', { question })
export const getExecutiveBrief = () => api.get('/ai/executive-brief')
export const getDecisionHistory  = () => api.get('/decision-history')

export const uploadFile = (category: string, file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/upload/${category}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const uploadSampleDoc = (sampleKey: string) =>
  api.post('/upload/sample', { sample_key: sampleKey })

export default api
