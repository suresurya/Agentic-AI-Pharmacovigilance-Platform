import { useState } from 'react'
import { Send, Loader2 } from 'lucide-react'
import { submitNarrative, getNarrativeEntities } from '../../services/api'
import { pipelineWS } from '../../services/websocket'
import { useNarrativeStore } from '../../store/narrativeStore'
import { usePipelineStore } from '../../store/pipelineStore'
import { useReportStore } from '../../store/reportStore'
import type { Report } from '../../types'

const DEMO_NARRATIVES = [
  'Maine kal raat metformin 500mg li aur subah uthke bahut ulti jaisi feeling thi, haath bhi kaanp rahe the',
  'Amlodipine aur metformin dono le raha hun, chakkar aa rahe hain aur kamzori bhi feel ho rahi hai',
  'Paracetamol khane ke baad rash ho gaya aur khujli bhi bahut zyada thi',
  'Aspirin le raha hun sar dard ke liye, koi side effect nahi aaya',
  'Metformin lene ke baad chakkar nahi aaya, sab theek hai',
]

export function NarrativeInput() {
  const [text, setText] = useState('')
  const { setNarrative, setEntities, setSubmitting, submitting } = useNarrativeStore()
  const { resetPipeline, startPipeline, updateNode, setHITL } = usePipelineStore()
  const { addReport, fetchReports } = useReportStore()

  const handleSubmit = async () => {
    if (!text.trim() || submitting) return
    setSubmitting(true)
    resetPipeline()
    startPipeline()

    try {
      const { data: narrative } = await submitNarrative(text.trim())
      setNarrative(narrative)

      // Connect WebSocket
      const unsub = pipelineWS.onEvent(async (event) => {
        if (event.event === 'node_complete' && event.node) {
          updateNode(event.node, 'complete', event.output_preview)
        }
        if (event.event === 'pipeline_error' && event.node) {
          updateNode(event.node, 'error')
        }
        if (event.event === 'hitl_required') {
          setHITL(event.candidates ?? [], event.report_id ?? '')
          updateNode('Normalize', 'running', 'Officer input required')
        }
        if (event.event === 'pipeline_complete') {
          setSubmitting(false)
          unsub()
          // Fetch entities for highlighting
          try {
            const { data: entities } = await getNarrativeEntities(narrative.id)
            setEntities(entities)
          } catch {}
          fetchReports()
        }
      })

      pipelineWS.connect(narrative.id)
    } catch (e) {
      setSubmitting(false)
      console.error(e)
    }
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-slate-800">Submit Narrative</h2>
        <span className="text-xs text-slate-400">{text.length}/5000</span>
      </div>

      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        rows={4}
        placeholder="Enter Hinglish patient narrative… e.g. 'Maine metformin li aur ulti jaisi feeling aayi'"
        className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-slate-400"
        disabled={submitting}
      />

      {/* Demo shortcuts */}
      <div>
        <p className="text-xs text-slate-400 mb-1.5">Quick demo:</p>
        <div className="flex flex-wrap gap-1.5">
          {DEMO_NARRATIVES.map((n, i) => (
            <button
              key={i}
              onClick={() => setText(n)}
              className="text-xs bg-slate-100 hover:bg-blue-50 hover:text-blue-700 text-slate-600 px-2 py-1 rounded transition-colors"
            >
              Demo {i + 1}
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={!text.trim() || submitting}
        className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-semibold py-2.5 rounded-lg transition-colors"
      >
        {submitting ? (
          <><Loader2 size={16} className="animate-spin" /> Processing…</>
        ) : (
          <><Send size={16} /> Analyse Narrative</>
        )}
      </button>
    </div>
  )
}
