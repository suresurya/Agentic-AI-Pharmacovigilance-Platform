import type { Report } from '../../types'
import { ConfidenceBar } from './ConfidenceBar'
import { CheckCircle, XCircle, Clock, Zap } from 'lucide-react'
import clsx from 'clsx'

interface Props {
  report: Report
}

const CAUSAL_LABELS: Record<string, string> = {
  temporal_proximity_post_ingestion: 'Temporal proximity after ingestion',
  patient_self_attribution: 'Patient self-attribution',
  concurrent_occurrence: 'Concurrent occurrence',
  negative_association: 'Negative association',
  no_clear_pattern: 'No clear pattern',
}

export function EvidencePanel({ report }: Props) {
  const ev = report.evidence

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-4">
      {/* Drug + Symptom chips */}
      <div className="flex gap-3 flex-wrap">
        <div className="bg-drug-light border border-drug-border rounded-lg px-3 py-2 min-w-[120px]">
          <p className="text-xs font-semibold text-drug-text uppercase tracking-wide mb-0.5">Drug</p>
          <p className="font-semibold text-slate-800">{ev?.drug_span ?? '—'}</p>
        </div>
        <div className="flex items-center text-slate-400 font-bold text-lg">→</div>
        <div className="bg-symptom-light border border-symptom-border rounded-lg px-3 py-2 min-w-[120px]">
          <p className="text-xs font-semibold text-symptom-text uppercase tracking-wide mb-0.5">Symptom</p>
          <p className="font-semibold text-slate-800">{ev?.reaction_span ?? '—'}</p>
        </div>
      </div>

      {/* Relation + Confidence */}
      <div className="flex items-center gap-3">
        <span className={clsx(
          'px-2.5 py-1 rounded-full text-xs font-bold',
          report.relation_type === 'Causes-ADR' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
        )}>
          {report.relation_type}
        </span>
        <div className="flex-1">
          <ConfidenceBar value={report.confidence} />
        </div>
      </div>

      {/* WHO-ART term */}
      {report.normalized_term && (
        <div className="bg-slate-50 rounded-lg px-3 py-2 flex items-center gap-2">
          <Zap size={14} className="text-blue-500" />
          <span className="text-sm text-slate-700">
            <span className="font-semibold">WHO-ART:</span> {report.normalized_term}
            {report.whoart_code && (
              <span className="ml-2 text-xs text-slate-500 font-mono">#{report.whoart_code}</span>
            )}
          </span>
        </div>
      )}

      {/* Evidence details */}
      {ev && (
        <div className="border-t border-slate-100 pt-4 space-y-2.5">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Evidence</p>

          {ev.temporal_marker && (
            <div className="flex gap-2 items-start">
              <Clock size={13} className="text-slate-400 mt-0.5 shrink-0" />
              <div>
                <p className="text-xs text-slate-500">Temporal marker</p>
                <p className="text-sm text-slate-800">
                  <span className="font-mono bg-slate-100 px-1 rounded">"{ev.temporal_marker}"</span>
                  {ev.temporal_marker_translation && (
                    <span className="text-slate-500 ml-1">— {ev.temporal_marker_translation}</span>
                  )}
                </p>
              </div>
            </div>
          )}

          {ev.causal_pattern && (
            <div className="flex gap-2 items-start">
              <Zap size={13} className="text-slate-400 mt-0.5 shrink-0" />
              <div>
                <p className="text-xs text-slate-500">Causal pattern</p>
                <p className="text-sm text-slate-800">{CAUSAL_LABELS[ev.causal_pattern] ?? ev.causal_pattern}</p>
              </div>
            </div>
          )}

          <div className="flex gap-2 items-start">
            {ev.negation_detected
              ? <XCircle size={13} className="text-red-400 mt-0.5 shrink-0" />
              : <CheckCircle size={13} className="text-green-500 mt-0.5 shrink-0" />
            }
            <div>
              <p className="text-xs text-slate-500">Negation check</p>
              <p className="text-sm text-slate-800">{ev.negation_detected ? 'Negation detected' : 'None detected'}</p>
            </div>
          </div>

          {ev.plain_language_reason && (
            <div className="bg-blue-50 border border-blue-100 rounded-lg p-3">
              <p className="text-xs font-semibold text-blue-600 mb-1">Reason</p>
              <p className="text-sm text-slate-700 leading-relaxed">{ev.plain_language_reason}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
