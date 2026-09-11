import { useRef, useState } from 'react'
import { CheckCircle2, FileUp, LoaderCircle, UploadCloud } from 'lucide-react'

export default function UploadArea() {
  const inputRef = useRef(null)
  const [files, setFiles] = useState([
    { name: 'Rahul.pdf', done: true },
    { name: 'Priya.pdf', done: true },
    { name: 'Amit.pdf', done: false },
  ])

  const addFiles = (fileList) => {
    const added = [...fileList].filter((file) => /\.(pdf|docx)$/i.test(file.name)).map((file) => ({ name: file.name, done: false }))
    if (!added.length) return
    setFiles((current) => [...current, ...added])
    setTimeout(() => setFiles((current) => current.map((file) => ({ ...file, done: true }))), 1200)
  }

  return <div className="panel p-5">
    <div role="button" tabIndex={0} onClick={() => inputRef.current?.click()} onKeyDown={(event) => event.key === 'Enter' && inputRef.current?.click()} onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); addFiles(event.dataTransfer.files) }} className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-[#cfe0dc] bg-[#fbfdfc] px-5 py-10 text-center transition hover:border-teal">
      <input ref={inputRef} type="file" multiple accept=".pdf,.docx" className="hidden" onChange={(event) => addFiles(event.target.files)} />
      <span className="mb-3 grid h-12 w-12 place-items-center rounded-full bg-mint text-teal"><UploadCloud size={22} /></span>
      <span className="text-sm font-bold">Drop resumes here or browse files</span>
      <span className="mt-2 text-xs text-muted">PDF and DOCX · Max 10 MB per file</span>
    </div>
    <div className="mt-5 space-y-2">{files.map((file) => <div key={file.name} className="flex items-center justify-between rounded-lg bg-canvas px-3 py-3"><div className="flex items-center gap-2 text-xs font-semibold"><FileUp size={15} className="text-muted" />{file.name}</div>{file.done ? <span className="flex items-center gap-1 text-[11px] font-bold text-teal"><CheckCircle2 size={15} />Parsed</span> : <span className="flex items-center gap-1 text-[11px] font-bold text-[#a17612]"><LoaderCircle className="animate-spin" size={14} />Processing...</span>}</div>)}</div>
  </div>
}