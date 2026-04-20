import { NarrativeInput } from '../components/narrative/NarrativeInput'
import { EntityHighlighter } from '../components/narrative/EntityHighlighter'
import { PipelineProgress } from '../components/pipeline/PipelineProgress'
import { ReportsList } from '../components/report/ReportsList'
import { HITLPrompt } from '../components/hitl/HITLPrompt'
import { useNarrativeStore } from '../store/narrativeStore'

export function Dashboard() {
  const { currentNarrative, entities } = useNarrativeStore()

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">VigilAI Dashboard</h1>
        <p className="text-slate-500 text-sm mt-0.5">Hinglish Pharmacovigilance · ADR Signal Detection</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Left column — input + pipeline */}
        <div className="xl:col-span-1 space-y-4">
          <NarrativeInput />
          <PipelineProgress />
        </div>

        {/* Center + right — narrative + reports */}
        <div className="xl:col-span-2 space-y-4">
          {currentNarrative && (
            <div className="bg-white border border-slate-200 rounded-xl p-5">
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-semibold text-slate-800">Source Narrative</h2>
                {currentNarrative.language_mix_ratio !== undefined && (
                  <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full font-medium">
                    {Math.round(currentNarrative.language_mix_ratio * 100)}% Hinglish
                  </span>
                )}
              </div>
              <EntityHighlighter
                text={currentNarrative.source_text}
                entities={entities}
              />
              {entities.length > 0 && (
                <div className="flex gap-3 mt-3 pt-3 border-t border-slate-100">
                  {['drug', 'symptom', 'dosage'].map(type => {
                    const count = entities.filter(e => e.entity_type === type).length
                    if (!count) return null
                    const colors = {
                      drug: 'bg-drug-light text-drug-text',
                      symptom: 'bg-symptom-light text-symptom-text',
                      dosage: 'bg-dosage-light text-dosage-text',
                    }
                    return (
                      <span key={type} className={`text-xs font-semibold px-2 py-0.5 rounded-full ${colors[type as keyof typeof colors]}`}>
                        {count} {type}
                      </span>
                    )
                  })}
                </div>
              )}
            </div>
          )}

          <ReportsList />
        </div>
      </div>

      <HITLPrompt />
    </div>
  )
}
