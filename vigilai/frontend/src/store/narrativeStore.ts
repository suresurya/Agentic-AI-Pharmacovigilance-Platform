import { create } from 'zustand'
import type { Narrative, Entity } from '../types'

interface NarrativeStore {
  currentNarrative: Narrative | null
  entities: Entity[]
  submitting: boolean
  setNarrative: (n: Narrative) => void
  setEntities: (e: Entity[]) => void
  setSubmitting: (v: boolean) => void
  reset: () => void
}

export const useNarrativeStore = create<NarrativeStore>((set) => ({
  currentNarrative: null,
  entities: [],
  submitting: false,
  setNarrative: (n) => set({ currentNarrative: n }),
  setEntities: (e) => set({ entities: e }),
  setSubmitting: (v) => set({ submitting: v }),
  reset: () => set({ currentNarrative: null, entities: [], submitting: false }),
}))
