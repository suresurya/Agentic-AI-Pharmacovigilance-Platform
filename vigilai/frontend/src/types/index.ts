export interface Entity {
  id: string
  narrative_id: string
  entity_text: string
  entity_type: 'drug' | 'symptom' | 'dosage'
  char_start: number
  char_end: number
  confidence: number
  source_model: string
}

export interface Evidence {
  drug_span?: string
  reaction_span?: string
  temporal_marker?: string | null
  temporal_marker_translation?: string | null
  causal_pattern?: string
  negation_detected?: boolean
  plain_language_reason?: string
}

export interface Report {
  id: string
  narrative_id: string
  drug_entity_id?: string
  symptom_entity_id?: string
  relation_type: 'Causes-ADR' | 'Possible-ADR'
  confidence: number
  evidence?: Evidence
  normalized_term?: string
  whoart_code?: string
  officer_status: 'pending' | 'approved' | 'rejected' | 'modified'
  officer_notes?: string
  created_at: string
}

export interface Narrative {
  id: string
  source_text: string
  source_type: string
  language_mix_ratio?: number
  status: string
  created_at: string
}

export interface WHOARTCandidate {
  rank: number
  term: string
  code: string
  system_organ_class?: string
  score: number
}

export interface PipelineNode {
  name: string
  status: 'waiting' | 'running' | 'complete' | 'error'
  output_preview?: string
}

export interface WSEvent {
  event: string
  node?: string
  status?: string
  output_preview?: string
  timestamp?: string
  next_node?: string
  candidates?: WHOARTCandidate[]
  report_id?: string
  message?: string
  error?: string
}
