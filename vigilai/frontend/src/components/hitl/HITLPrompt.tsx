import { useState } from 'react'
import { usePipelineStore } from '../../store/pipelineStore'
import { resolveHITL } from '../../services/api'
import { useReportStore } from '../../store/reportStore'
import { AlertTriangle, CheckCircle2 } from 'lucide-react'
import clsx from 'clsx'

export function HITLPrompt() {
  const { hitlRequired, hitlCandidates, hitlReportId, clearHITL, updateNode } = usePipelineStore()
  const { fetchReports } = useReportStore()
  const [selected, setSelected] = useState<number | null>(null)
  const [resolving, setResolving] = useState(false)

  if (!hitlRequired) return null

  const handleConfirm = async () => {
    if (selected === null || !hitlReportId) return
    const candidate = hitlCandidates[selected]
    setResolving(true)
    try {
      await resolveHITL(hitlReportId, candidate.term, candidate.code)
      updateNode('Normalize', 'complete', `Officer selected: ${candidate.term}`)
      clearHITL()
      await fetchReports()
    } finally {
      setResolving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6 space-y-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center shrink-0">
            <AlertTriangle size={18} className="text-amber-600" />
          </div>
          <div>
            <h3 className="font-bold text-slate-800">Officer Action Required</h3>
            <p className="text-sm text-slate-500">WHO-ART confidence below threshold. Select the correct term.</p>
          </div>
        </div>

        <div className="space-y-2">
          {hitlCandidates.map((c, i) => (
            <button
              key={c.code}
              onClick={() => setSelected(i)}
              className={clsx(
                'w-full text-left px-4 py-3 rounded-xl border-2 transition-all',
                selected === i
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-slate-200 hover:border-slate-300 bg-white',
              )}
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">#{c.code}</span>
                  <span className="font-semibold text-slate-800 text-sm">{c.term}</span>
                </div>
                {selected === i && <CheckCircle2 size={16} className="text-blue-500" />}
              </div>
              {c.system_organ_class && (
                <p className="text-xs text-slate-400">{c.system_organ_class}</p>
              )}
              <div className="mt-2 flex items-center gap-2">
                <div className="flex-1 h-1.5 bg-slate-200 rounded-full">
                  <div
                    className="h-full bg-blue-400 rounded-full"
                    style={{ width: `${Math.round(c.score * 100)}%` }}
                  />
                </div>
                <span className="text-xs text-slate-500">{Math.round(c.score * 100)}%</span>
              </div>
            </button>
          ))}
        </div>

        <button
          onClick={handleConfirm}
          disabled={selected === null || resolving}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-semibold py-2.5 rounded-xl transition-colors"
        >
          {resolving ? 'Confirming…' : 'Confirm Selection & Resume Pipeline'}
        </button>
      </div>
    </div>
  )
}
