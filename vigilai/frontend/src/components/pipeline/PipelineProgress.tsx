import { usePipelineStore } from '../../store/pipelineStore'
import { CheckCircle2, Circle, Loader2, XCircle, ChevronRight } from 'lucide-react'
import clsx from 'clsx'

const NODE_ICONS: Record<string, string> = {
  Ingest: '📥',
  Preprocess: '🔧',
  NER: '🏷️',
  Relation: '🔗',
  Normalize: '📋',
  Report: '📄',
}

export function PipelineProgress() {
  const { nodes, isRunning } = usePipelineStore()

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-slate-800">Pipeline Progress</h2>
        {isRunning && (
          <span className="flex items-center gap-1 text-xs text-blue-600 font-medium">
            <Loader2 size={12} className="animate-spin" /> Running
          </span>
        )}
      </div>

      <div className="space-y-2">
        {nodes.map((node, i) => (
          <div key={node.name}>
            <div className={clsx(
              'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all',
              node.status === 'running' && 'bg-blue-50 border border-blue-200',
              node.status === 'complete' && 'bg-green-50',
              node.status === 'error' && 'bg-red-50',
              node.status === 'waiting' && 'opacity-50',
            )}>
              <span className="text-base w-5 text-center">{NODE_ICONS[node.name]}</span>
              <span className="flex-1 text-sm font-medium text-slate-700">{node.name}</span>
              {node.status === 'waiting' && <Circle size={14} className="text-slate-300" />}
              {node.status === 'running' && <Loader2 size={14} className="text-blue-500 animate-spin" />}
              {node.status === 'complete' && <CheckCircle2 size={14} className="text-green-500" />}
              {node.status === 'error' && <XCircle size={14} className="text-red-500" />}
            </div>
            {node.output_preview && node.status === 'complete' && (
              <p className="text-xs text-slate-400 pl-11 pb-1">{node.output_preview}</p>
            )}
            {i < nodes.length - 1 && (
              <div className="pl-[18px]">
                <ChevronRight size={12} className="text-slate-300 -rotate-90 mx-auto" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
