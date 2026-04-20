import axios from 'axios'
import type { Narrative, Report, Entity } from '../types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

// Auth
export const login = (email: string, password: string) =>
  api.post('/api/v1/auth/token', { email, password })

// Narratives
export const submitNarrative = (text: string, source_type = 'manual') =>
  api.post<Narrative>('/api/v1/narratives/', { source_text: text, source_type })

export const getNarrative = (id: string) =>
  api.get<Narrative>(`/api/v1/narratives/${id}/`)

export const getNarrativeEntities = (id: string) =>
  api.get<Entity[]>(`/api/v1/narratives/${id}/entities/`)

export const submitBatch = (file: File) => {
  const fd = new FormData()
  fd.append('file', file)
  return api.post('/api/v1/narratives/batch/', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// Reports
export const getReports = (params?: { status?: string; skip?: number; limit?: number }) =>
  api.get<Report[]>('/api/v1/reports/', { params })

export const getReport = (id: string) =>
  api.get<Report>(`/api/v1/reports/${id}/`)

export const reviewReport = (
  id: string,
  action: string,
  notes?: string,
  corrected_term?: string,
  corrected_whoart_code?: string,
) =>
  api.patch<Report>(`/api/v1/reports/${id}/review/`, {
    action, notes, corrected_term, corrected_whoart_code,
  })

export const exportReport = (id: string) =>
  api.get(`/api/v1/reports/${id}/export/`)

export const getAnalytics = () =>
  api.get('/api/v1/reports/analytics/')

// HITL
export const resolveHITL = (reportId: string, selected_term: string, selected_code: string) =>
  api.post(`/api/v1/reports/${reportId}/resolve-hitl/`, { selected_term, selected_code })

// WHO-ART search
export const searchWHOART = (q: string) =>
  api.get('/api/v1/whoart/search/', { params: { q } })

export default api
