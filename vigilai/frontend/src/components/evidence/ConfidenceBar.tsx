import clsx from 'clsx'

interface Props {
  value: number  // 0-1
  showLabel?: boolean
}

export function ConfidenceBar({ value, showLabel = true }: Props) {
  const pct = Math.round(value * 100)
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
        <div
          className={clsx('h-full rounded-full transition-all', {
            'bg-green-500': pct >= 80,
            'bg-yellow-400': pct >= 60 && pct < 80,
            'bg-red-400': pct < 60,
          })}
          style={{ width: `${pct}%` }}
        />
      </div>
      {showLabel && <span className="text-xs font-semibold text-slate-600 w-9 text-right">{pct}%</span>}
    </div>
  )
}
