import axios from 'axios'
import { supabase } from './supabaseClient'

const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${backendUrl}/api`,
})

// Attach Bearer token from Supabase session
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession()
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

export const profileApi = {
  getMe: () => api.get('/profile/me'),
  getHealth: () => api.get('/health'),
}

export const documentApi = {
  upload: (formData) => api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  list: () => api.get('/documents'),
  getStatus: (id) => api.get(`/documents/${id}/status`),
  update: (id, formData) => api.put(`/documents/${id}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  delete: (id) => api.delete(`/documents/${id}`),
}

export const chatApi = {
  ask: (payload) => api.post('/chat/ask', payload),
  getConversations: () => api.get('/conversations'),
  getConversation: (id) => api.get(`/conversations/${id}`),
  deleteConversation: (id) => api.delete(`/conversations/${id}`),
}

export default api
