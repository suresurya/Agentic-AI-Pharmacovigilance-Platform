import { ReportsList } from '../components/report/ReportsList'
import { BatchUpload } from '../components/narrative/BatchUpload'

export function Reports() {
  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Reports</h1>
      <ReportsList />
    </div>
  )
}

export function Batch() {
  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Batch Upload</h1>
      <BatchUpload />
    </div>
  )
}
