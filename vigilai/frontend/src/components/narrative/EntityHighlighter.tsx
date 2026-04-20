import type { Entity } from '../../types'
import clsx from 'clsx'

interface Props {
  text: string
  entities: Entity[]
}

const TYPE_STYLES = {
  drug: 'bg-drug-light border-b-2 border-drug-border text-drug-text',
  symptom: 'bg-symptom-light border-b-2 border-symptom-border text-symptom-text',
  dosage: 'bg-dosage-light border-b-2 border-dosage-border text-dosage-text',
}

export function EntityHighlighter({ text, entities }: Props) {
  if (!entities.length) {
    return <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">{text}</p>
  }

  // Build sorted, non-overlapping segments
  const sorted = [...entities].sort((a, b) => a.char_start - b.char_start)
  const segments: { text: string; entity?: Entity }[] = []
  let cursor = 0

  for (const entity of sorted) {
    const start = Math.max(entity.char_start, cursor)
    const end = Math.min(entity.char_end, text.length)
    if (start >= end) continue
    if (start > cursor) segments.push({ text: text.slice(cursor, start) })
    segments.push({ text: text.slice(start, end), entity })
    cursor = end
  }
  if (cursor < text.length) segments.push({ text: text.slice(cursor) })

  return (
    <p className="text-slate-700 leading-loose whitespace-pre-wrap text-base">
      {segments.map((seg, i) =>
        seg.entity ? (
          <span
            key={i}
            className={clsx('px-0.5 rounded cursor-default group relative', TYPE_STYLES[seg.entity.entity_type])}
            title={`${seg.entity.entity_type.toUpperCase()} — ${Math.round(seg.entity.confidence * 100)}% confidence`}
          >
            {seg.text}
            <span className="absolute -top-6 left-0 hidden group-hover:block bg-slate-800 text-white text-xs px-2 py-0.5 rounded whitespace-nowrap z-10">
              {seg.entity.entity_type.toUpperCase()} {Math.round(seg.entity.confidence * 100)}%
            </span>
          </span>
        ) : (
          <span key={i}>{seg.text}</span>
        )
      )}
    </p>
  )
}
