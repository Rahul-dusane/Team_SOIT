import { AlertTriangle, X } from 'lucide-react'

export default function ErrorBanner({ message, onClose }) {
  if (!message) return null

  return (
    <div className="mb-6 flex items-center justify-between rounded-2xl border border-rose-500/20 bg-rose-500/10 p-4 text-xs font-semibold text-rose-700 shadow-xs backdrop-blur-md animate-fade-in">
      <div className="flex items-center gap-2.5">
        <AlertTriangle size={16} className="shrink-0 text-rose-600" />
        <span>{message}</span>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="rounded-full p-1 text-rose-500 hover:bg-rose-500/20 hover:text-rose-800 transition"
          aria-label="Close error message"
        >
          <X size={14} />
        </button>
      )}
    </div>
  )
}
