import { useState } from 'react'
import type { Report } from '../../types'
import { EvidencePanel } from '../evidence/EvidencePanel'
import { ConfidenceBar } from '../evidence/ConfidenceBar'
import { useReportStore } from '../../store/reportStore'
import { exportReport } from '../../services/api'
import { ChevronDown, ChevronUp, Download, CheckCircle, XCircle, Edit2 } from 'lucide-react'
import clsx from 'clsx'

interface Props {
  report: Report
}

const STATUS_STYLES = {
  pending: 'bg-amber-100 text-amber-700',
  approved: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
  modified: 'bg-blue-100 text-blue-700',
}

export function ReportCard({ report }: Props) {
  const [expanded, setExpanded] = useState(false)
  const { reviewReport } = useReportStore()

  const handleExport = async () => {
    const { data } = await exportReport(report.id)
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report-${report.id.slice(0, 8)}.json`
    a.click()
  }

  const ev = report.evidence
  const drugName = ev?.drug_span ?? 'Unknown drug'
  const symptomName = ev?.reaction_span ?? report.normalized_term ?? 'Unknown symptom'

  return (
    <div className={clsx(
      'bg-white border rounded-xl overflow-hidden transition-all',
      report.officer_status === 'approved' ? 'border-green-200' :
      report.officer_status === 'rejected' ? 'border-red-200 opacity-60' :
      'border-slate-200'
    )}>
      {/* Header */}
      <div className="px-4 py-3 flex items-center gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-semibold text-slate-800 text-sm truncate">{drugName}</span>
            <span className="text-slate-400">→</span>
            <span className="font-semibold text-slate-800 text-sm truncate">{symptomName}</span>
            <span className={clsx(
              'px-2 py-0.5 rounded-full text-xs font-bold shrink-0',
              report.relation_type === 'Causes-ADR' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
            )}>
              {report.relation_type}
            </span>
          </div>
          <div className="mt-1.5 max-w-xs">
            <ConfidenceBar value={report.confidence} />
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <span className={clsx('px-2 py-0.5 rounded-full text-xs font-semibold', STATUS_STYLES[report.officer_status])}>
            {report.officer_status}
          </span>
          <button onClick={() => setExpanded(v => !v)} className="text-slate-400 hover:text-slate-700 transition-colors p-1">
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        </div>
      </div>

      {/* WHO-ART term */}
      {report.normalized_term && !expanded && (
        <div className="px-4 pb-2.5">
          <span className="text-xs text-slate-500">WHO-ART: </span>
          <span className="text-xs font-medium text-slate-700">{report.normalized_term}</span>
          {report.whoart_code && <span className="text-xs text-slate-400 ml-1 font-mono">#{report.whoart_code}</span>}
        </div>
      )}

      {/* Expanded evidence */}
      {expanded && (
        <div className="px-4 pb-4 space-y-4 border-t border-slate-100 pt-3">
          <EvidencePanel report={report} />

          {/* Action buttons */}
          {report.officer_status === 'pending' && (
            <div className="flex gap-2">
              <button
                onClick={() => reviewReport(report.id, 'approve')}
                className="flex-1 flex items-center justify-center gap-1.5 bg-green-600 hover:bg-green-700 text-white text-sm font-semibold py-2 rounded-lg transition-colors"
              >
                <CheckCircle size={14} /> Approve
              </button>
              <button
                onClick={() => reviewReport(report.id, 'reject')}
                className="flex-1 flex items-center justify-center gap-1.5 bg-red-600 hover:bg-red-700 text-white text-sm font-semibold py-2 rounded-lg transition-colors"
              >
                <XCircle size={14} /> Reject
              </button>
              <button
                onClick={handleExport}
                className="flex items-center justify-center gap-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-semibold py-2 px-3 rounded-lg transition-colors"
              >
                <Download size={14} />
              </button>
            </div>
          )}
          {report.officer_status !== 'pending' && (
            <button
              onClick={handleExport}
              className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800 transition-colors"
            >
              <Download size={12} /> Export JSON
            </button>
          )}
        </div>
      )}
    </div>
  )
}
