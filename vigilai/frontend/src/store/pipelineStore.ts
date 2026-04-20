import { create } from 'zustand'
import type { PipelineNode, WHOARTCandidate } from '../types'

const NODE_NAMES = ['Ingest', 'Preprocess', 'NER', 'Relation', 'Normalize', 'Report']

interface PipelineStore {
  nodes: PipelineNode[]
  hitlRequired: boolean
  hitlCandidates: WHOARTCandidate[]
  hitlReportId: string | null
  isRunning: boolean
  resetPipeline: () => void
  startPipeline: () => void
  updateNode: (name: string, status: PipelineNode['status'], preview?: string) => void
  setHITL: (candidates: WHOARTCandidate[], reportId: string) => void
  clearHITL: () => void
}

export const usePipelineStore = create<PipelineStore>((set) => ({
  nodes: NODE_NAMES.map(n => ({ name: n, status: 'waiting' })),
  hitlRequired: false,
  hitlCandidates: [],
  hitlReportId: null,
  isRunning: false,

  resetPipeline: () =>
    set({
      nodes: NODE_NAMES.map(n => ({ name: n, status: 'waiting' })),
      hitlRequired: false,
      hitlCandidates: [],
      hitlReportId: null,
      isRunning: false,
    }),

  startPipeline: () =>
    set(s => ({
      isRunning: true,
      nodes: s.nodes.map((n, i) => ({ ...n, status: i === 0 ? 'running' : 'waiting' })),
    })),

  updateNode: (name, status, preview) =>
    set(s => {
      const nodes = s.nodes.map(n => n.name === name ? { ...n, status, output_preview: preview } : n)
      // Auto-advance next node to 'running'
      if (status === 'complete') {
        const idx = NODE_NAMES.indexOf(name)
        if (idx >= 0 && idx < NODE_NAMES.length - 1) {
          const next = NODE_NAMES[idx + 1]
          return { nodes: nodes.map(n => n.name === next ? { ...n, status: 'running' } : n) }
        }
      }
      return { nodes }
    }),

  setHITL: (candidates, reportId) =>
    set({ hitlRequired: true, hitlCandidates: candidates, hitlReportId: reportId }),

  clearHITL: () =>
    set({ hitlRequired: false, hitlCandidates: [], hitlReportId: null }),
}))
