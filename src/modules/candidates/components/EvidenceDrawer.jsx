import { X, FileText, CheckCircle2, Bookmark, Sparkles } from 'lucide-react'

export default function EvidenceDrawer({ open, onClose, evidence }) {
  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex justify-end bg-slate-900/40 backdrop-blur-md transition-opacity duration-300 animate-fade-in"
      onClick={onClose}
    >
      <aside
        role="dialog"
        aria-label="Resume Grounding Evidence Citation"
        className="relative flex h-full w-full max-w-lg flex-col border-l border-white/20 bg-white/90 p-8 shadow-2xl backdrop-blur-2xl transition-transform duration-300 ease-out sm:rounded-l-3xl"
        onClick={e => e.stopPropagation()}
      >
        {/* Header Bar */}
        <div className="flex items-center justify-between border-b border-slate-200/70 pb-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-apple-blue/10 text-apple-blue shadow-xs">
              <FileText size={20} />
            </div>
            <div>
              <h3 className="text-base font-extrabold text-slate-900 tracking-tight">Grounding Citation</h3>
              <p className="text-xs text-slate-500 font-medium">Verified Resume Passage Evidence</p>
            </div>
          </div>

          <button
            aria-label="Close evidence citation"
            onClick={onClose}
            className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-slate-100/80 text-slate-500 transition-all duration-200 hover:bg-slate-200 hover:text-slate-900 active:scale-95"
          >
            <X size={18} />
          </button>
        </div>

        {/* Citation Metadata Badges */}
        <div className="my-5 flex flex-wrap gap-2">
          {evidence?.candidate_skill && (
            <span className="pill-badge bg-apple-blue/10 text-apple-blue border border-apple-blue/20">
              <Sparkles size={12} /> Skill: {evidence.candidate_skill}
            </span>
          )}
          {evidence?.page_number != null && (
            <span className="pill-badge bg-slate-100 text-slate-700 border border-slate-200">
              <Bookmark size={12} className="text-slate-400" /> Source Page #{evidence.page_number}
            </span>
          )}
          {evidence?.confidence != null && (
            <span className="pill-badge bg-emerald-500/10 text-emerald-700 border border-emerald-500/20">
              <CheckCircle2 size={12} /> Confidence: {Math.round(evidence.confidence * 100)}%
            </span>
          )}
        </div>

        {/* Verified Passage Text Block */}
        <div className="flex-1 overflow-y-auto rounded-2xl border border-slate-200/80 bg-slate-50/70 p-5 shadow-xs">
          <span className="eyebrow block mb-2 text-slate-400">Exact Document Passage</span>
          <blockquote className="text-xs text-slate-800 leading-relaxed font-mono whitespace-pre-wrap">
            "{evidence?.evidence_passage || evidence?.matched_text || 'Grounding evidence text passage not returned by server.'}"
          </blockquote>
        </div>

        {/* Footer */}
        <div className="mt-6 pt-4 border-t border-slate-200/60 flex items-center justify-between text-xs text-slate-400">
          <span>HireLens Evidence Grounding Engine</span>
          <button
            onClick={onClose}
            className="btn-soft text-xs py-2 px-4"
          >
            Dismiss
          </button>
        </div>
      </aside>
    </div>
  )
}
