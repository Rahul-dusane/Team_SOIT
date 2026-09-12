import { useState } from 'react'
import { CheckCircle2, FileUp, LoaderCircle, UploadCloud, AlertCircle, FileText } from 'lucide-react'
import { uploadResumes } from '../../../core/api/api'
import { uploadOutcome } from '../../../core/api/viewData'
import ErrorBanner from '../../../core/components/ErrorBanner'

export default function UploadArea({ onUploadSuccess }) {
  const [fileList, setFileList] = useState([])
  const [uploading, setUploading] = useState(false)
  const [errorMsg, setErrorMsg] = useState(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleFileChange = async (e) => {
    const selectedFiles = Array.from(e.target.files || [])
    if (selectedFiles.length === 0) return
    await processUpload(selectedFiles)
    e.target.value = ''
  }

  const processUpload = async (selectedFiles) => {
    setErrorMsg(null)
    const allowedExts = ['.pdf', '.docx', '.txt']
    const batchId = crypto.randomUUID()
    const validFiles = []
    const newItems = []

    for (const file of selectedFiles) {
      const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase()
      if (!allowedExts.includes(ext)) {
        setErrorMsg(`Unsupported file format '${ext}'. Please upload PDF, DOCX, or TXT resumes.`)
        return
      }
      if (file.size > 10 * 1024 * 1024) {
        setErrorMsg(`File '${file.name}' exceeds maximum allowed size of 10 MB.`)
        return
      }
      validFiles.push(file)
      newItems.push({ name: file.name, batchId, index: newItems.length, status: 'Processing...' })
    }

    setFileList(old => [...newItems, ...old])
    setUploading(true)

    try {
      const response = await uploadResumes(validFiles)
      setFileList(old =>
        old.map(item =>
          item.batchId === batchId
            ? { ...item, ...uploadOutcome(response?.file_results?.[item.index]) }
            : item
        )
      )
      if (onUploadSuccess) {
        onUploadSuccess(response)
      }
    } catch (err) {
      const msg = err.message || 'Upload failed. Please check backend connection.'
      setErrorMsg(msg)
      setFileList(old =>
        old.map(item => {
          const found = item.batchId === batchId
          return found ? { ...item, status: 'Failed', error: msg } : item
        })
      )
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="panel p-6 shadow-apple-card border-slate-200/80">
      {errorMsg && <ErrorBanner message={errorMsg} onClose={() => setErrorMsg(null)} />}

      <label
        onDragOver={e => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={e => {
          e.preventDefault()
          setIsDragging(false)
          if (e.dataTransfer.files?.length) processUpload(Array.from(e.dataTransfer.files))
        }}
        className={`group relative flex cursor-pointer flex-col items-center justify-center rounded-3xl border-2 border-dashed p-8 text-center transition-all duration-300 ${
          isDragging
            ? 'border-apple-blue bg-apple-blue/5 shadow-glow scale-[1.01]'
            : 'border-slate-200/90 bg-slate-50/50 hover:border-apple-blue/50 hover:bg-slate-50'
        }`}
      >
        <input
          type="file"
          multiple
          accept=".pdf,.docx,.txt"
          className="hidden"
          onChange={handleFileChange}
          disabled={uploading}
        />

        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-slate-900 to-napkin-purple text-white shadow-lg transition-transform duration-300 group-hover:scale-110">
          <UploadCloud size={28} />
        </div>

        <span className="text-base font-extrabold text-slate-900 tracking-tight">
          Drop Resumes Here or <span className="text-apple-blue underline underline-offset-4">Browse Files</span>
        </span>
        <p className="mt-1.5 text-xs text-slate-500 max-w-sm">
          Supports <span className="font-semibold text-slate-700">PDF, DOCX, TXT</span> up to 10 MB per file. Text is parsed into 384-dim vector embeddings automatically.
        </p>

        {/* Allowed Format Pills */}
        <div className="mt-4 flex gap-2">
          {['.PDF', '.DOCX', '.TXT'].map(fmt => (
            <span key={fmt} className="pill-badge bg-white text-slate-600 border border-slate-200/80 shadow-xs">
              <FileText size={12} className="text-apple-blue" /> {fmt}
            </span>
          ))}
        </div>
      </label>

      {/* Uploaded File Trajectory List */}
      {fileList.length > 0 && (
        <div className="mt-6 space-y-2.5">
          <p className="eyebrow px-1">Processing Activity Log</p>
          {fileList.map((file, idx) => (
            <div
              key={`${file.name}_${idx}`}
              className="flex items-center justify-between rounded-2xl border border-slate-200/70 bg-white p-3.5 shadow-xs transition-all duration-200"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-100 text-slate-600">
                  <FileUp size={18} />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-900">{file.name}</p>
                  <p className="text-[11px] text-slate-400">Postgres & Vector Store</p>
                </div>
              </div>

              {['Parsed', 'Already stored'].includes(file.status) ? (
                <span className="pill-badge bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">
                  <CheckCircle2 size={13} /> {file.status}
                </span>
              ) : file.status === 'Processing...' ? (
                <span className="pill-badge bg-amber-500/10 text-amber-600 border border-amber-500/20">
                  <LoaderCircle className="animate-spin" size={13} /> Processing...
                </span>
              ) : (
                <span className="pill-badge bg-rose-500/10 text-rose-600 border border-rose-500/20" title={file.error}>
                  <AlertCircle size={13} /> Failed: {file.error}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
