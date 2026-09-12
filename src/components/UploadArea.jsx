import { useState } from 'react'
import { CheckCircle2, FileUp, LoaderCircle, UploadCloud, AlertCircle } from 'lucide-react'
import { uploadResumes } from '../services/api'
import { uploadOutcome } from '../services/viewData'
import ErrorBanner from './ErrorBanner'

export default function UploadArea({ onUploadSuccess }) {
  const [fileList, setFileList] = useState([])
  const [uploading, setUploading] = useState(false)
  const [errorMsg, setErrorMsg] = useState(null)

  const handleFileChange = async (e) => {
    const selectedFiles = Array.from(e.target.files || [])
    if (selectedFiles.length === 0) return

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
      setFileList(old => old.map(item => item.batchId === batchId
        ? { ...item, ...uploadOutcome(response?.file_results?.[item.index]) } : item))
      if (onUploadSuccess) {
        onUploadSuccess(response)
      }
    } catch (err) {
      const msg = err.message || 'Upload failed. Please check backend connection.'
      setErrorMsg(msg)
      setFileList(old => old.map(item => {
        const found = item.batchId === batchId
        return found ? { ...item, status: 'Failed', error: msg } : item
      }))
    } finally {
      setUploading(false)
      // reset file input
      e.target.value = ''
    }
  }

  return (
    <div className="panel p-5">
      {errorMsg && (
        <ErrorBanner message={errorMsg} onClose={() => setErrorMsg(null)} />
      )}
      <label className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-[#cfe0dc] bg-[#fbfdfc] px-5 py-10 text-center transition hover:border-teal">
        <input
          type="file"
          multiple
          accept=".pdf,.docx,.txt"
          className="hidden"
          onChange={handleFileChange}
          disabled={uploading}
        />
        <span className="mb-3 grid h-12 w-12 place-items-center rounded-full bg-mint text-teal">
          <UploadCloud size={22} />
        </span>
        <span className="text-sm font-bold">Browse resume files</span>
        <span className="mt-2 text-xs text-muted">PDF, DOCX and TXT · Max 10 MB per file</span>
      </label>

      <div className="mt-5 space-y-2">
        {fileList.map((file, idx) => (
          <div key={`${file.name}_${idx}`} className="flex items-center justify-between rounded-lg bg-canvas px-3 py-3">
            <div className="flex items-center gap-2 text-xs font-semibold">
              <FileUp size={15} className="text-muted" />
              {file.name}
            </div>
            {['Parsed', 'Already stored'].includes(file.status) ? (
              <span className="flex items-center gap-1 text-[11px] font-bold text-teal">
                <CheckCircle2 size={15} />{file.status}
              </span>
            ) : file.status === 'Processing...' ? (
              <span className="flex items-center gap-1 text-[11px] font-bold text-[#a17612]">
                <LoaderCircle className="animate-spin" size={14} />Processing...
              </span>
            ) : (
              <span className="flex items-center gap-1 text-[11px] font-bold text-[#dc2626]" title={file.error}>
                <AlertCircle size={14} />Failed: {file.error}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}