import React from 'react'
import { AlertCircle, WifiOff, X } from 'lucide-react'

export default function ErrorBanner({ message, type = 'error', onClose, isOffline = false }) {
  if (!message) return null

  const isWarning = type === 'warning'

  return (
    <div className={`mb-6 flex items-center justify-between rounded-xl border p-4 text-sm font-semibold transition-all shadow-sm ${
      isOffline
        ? 'border-[#fcd34d] bg-[#fffbeb] text-[#92400e]'
        : isWarning
        ? 'border-[#fef08a] bg-[#fefce8] text-[#854d0e]'
        : 'border-[#fca5a5] bg-[#fef2f2] text-[#991b1b]'
    }`}>
      <div className="flex items-center gap-3">
        <span className="grid h-8 w-8 place-items-center rounded-lg bg-white/80 shrink-0">
          {isOffline ? <WifiOff size={18} className="text-[#b45309]" /> : <AlertCircle size={18} className={isWarning ? 'text-[#a16207]' : 'text-[#dc2626]'} />}
        </span>
        <div>
          <p className="font-bold text-xs uppercase tracking-wide opacity-80">
            {isOffline ? 'Offline Mode' : isWarning ? 'Notice' : 'Error'}
          </p>
          <p className="mt-0.5 text-xs leading-5">{message}</p>
        </div>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="rounded-md p-1.5 opacity-70 hover:opacity-100 hover:bg-black/5 transition"
          aria-label="Dismiss error"
        >
          <X size={16} />
        </button>
      )}
    </div>
  )
}
