import { useEffect, useState } from 'react'
import { getAnalytics } from '../services/api'

interface Stats {
  total: number
  pending: number
  approved: number
  rejected: number
  causes_adr: number
  possible_adr: number
}

export function Analytics() {
  const [stats, setStats] = useState<Stats | null>(null)

  useEffect(() => {
    getAnalytics().then(r => setStats(r.data))
  }, [])

  if (!stats) return <div className="p-6 text-slate-400">Loading analytics…</div>

  const cards = [
    { label: 'Total Reports', value: stats.total, color: 'bg-blue-50 text-blue-700' },
    { label: 'Pending Review', value: stats.pending, color: 'bg-amber-50 text-amber-700' },
    { label: 'Approved', value: stats.approved, color: 'bg-green-50 text-green-700' },
    { label: 'Rejected', value: stats.rejected, color: 'bg-red-50 text-red-700' },
    { label: 'Causes-ADR', value: stats.causes_adr, color: 'bg-red-50 text-red-700' },
    { label: 'Possible-ADR', value: stats.possible_adr, color: 'bg-yellow-50 text-yellow-700' },
  ]

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Analytics</h1>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {cards.map(c => (
          <div key={c.label} className={`${c.color} rounded-xl p-5`}>
            <p className="text-3xl font-bold">{c.value}</p>
            <p className="text-sm font-medium mt-1 opacity-80">{c.label}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
