import { useEffect } from 'react'
import { useReportStore } from '../../store/reportStore'
import { ReportCard } from './ReportCard'
import { FileText, Loader2 } from 'lucide-react'
import clsx from 'clsx'

const FILTERS = [
  { value: 'all', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
]

export function ReportsList() {
  const { reports, loading, filter, fetchReports, setFilter } = useReportStore()

  useEffect(() => {
    fetchReports()
  }, [])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-slate-800">ADR Reports</h2>
        <div className="flex gap-1 bg-slate-100 rounded-lg p-1">
          {FILTERS.map(f => (
            <button
              key={f.value}
              onClick={() => setFilter(f.value)}
              className={clsx(
                'px-3 py-1 rounded-md text-xs font-semibold transition-colors',
                filter === f.value ? 'bg-white shadow text-slate-800' : 'text-slate-500 hover:text-slate-700',
              )}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12 text-slate-400">
          <Loader2 size={20} className="animate-spin mr-2" /> Loading reports…
        </div>
      ) : reports.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-slate-400">
          <FileText size={32} className="mb-2 opacity-40" />
          <p className="text-sm">No reports yet. Submit a narrative to get started.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map(r => <ReportCard key={r.id} report={r} />)}
        </div>
      )}
    </div>
  )
}
