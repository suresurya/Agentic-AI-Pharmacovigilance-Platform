import { create } from 'zustand'
import type { Report } from '../types'
import { getReports, reviewReport as apiReview } from '../services/api'

interface ReportStore {
  reports: Report[]
  loading: boolean
  filter: string
  fetchReports: (status?: string) => Promise<void>
  reviewReport: (id: string, action: string, notes?: string) => Promise<void>
  setFilter: (f: string) => void
  addReport: (r: Report) => void
}

export const useReportStore = create<ReportStore>((set, get) => ({
  reports: [],
  loading: false,
  filter: 'all',

  fetchReports: async (status) => {
    set({ loading: true })
    try {
      const params = status && status !== 'all' ? { status } : undefined
      const { data } = await getReports(params)
      set({ reports: data })
    } finally {
      set({ loading: false })
    }
  },

  reviewReport: async (id, action, notes) => {
    const { data } = await apiReview(id, action, notes)
    set(s => ({ reports: s.reports.map(r => r.id === id ? data : r) }))
  },

  setFilter: (f) => {
    set({ filter: f })
    get().fetchReports(f === 'all' ? undefined : f)
  },

  addReport: (r) =>
    set(s => ({ reports: [r, ...s.reports.filter(x => x.id !== r.id)] })),
}))
