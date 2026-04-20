import { useState, useRef } from 'react'
import { submitBatch } from '../../services/api'
import { Upload, CheckCircle2, AlertCircle } from 'lucide-react'
import clsx from 'clsx'

export function BatchUpload() {
  const [dragOver, setDragOver] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<{ count: number; job_ids: string[] } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const processFile = async (file: File) => {
    if (!file.name.endsWith('.csv')) {
      setError('Only CSV files are supported')
      return
    }
    setUploading(true)
    setError(null)
    setResult(null)
    try {
      const { data } = await submitBatch(file)
      setResult(data)
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="font-semibold text-slate-800">Batch Upload</h2>
      <div
        onDragOver={e => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={e => {
          e.preventDefault()
          setDragOver(false)
          const file = e.dataTransfer.files[0]
          if (file) processFile(file)
        }}
        onClick={() => inputRef.current?.click()}
        className={clsx(
          'border-2 border-dashed rounded-xl p-10 flex flex-col items-center gap-3 cursor-pointer transition-colors',
          dragOver ? 'border-blue-400 bg-blue-50' : 'border-slate-200 hover:border-slate-300 bg-white',
        )}
      >
        <Upload size={28} className="text-slate-400" />
        <div className="text-center">
          <p className="text-sm font-medium text-slate-700">Drop CSV file here or click to browse</p>
          <p className="text-xs text-slate-400 mt-1">CSV must have a "text" or "narrative" column</p>
        </div>
        <input ref={inputRef} type="file" accept=".csv" className="hidden" onChange={e => {
          const f = e.target.files?.[0]
          if (f) processFile(f)
        }} />
      </div>

      {uploading && (
        <p className="text-sm text-blue-600 text-center">Uploading and queuing narratives…</p>
      )}
      {result && (
        <div className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-lg p-3">
          <CheckCircle2 size={16} className="text-green-600" />
          <p className="text-sm text-green-800">
            Queued <span className="font-bold">{result.count}</span> narratives for processing
          </p>
        </div>
      )}
      {error && (
        <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg p-3">
          <AlertCircle size={16} className="text-red-600" />
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}
    </div>
  )
}
