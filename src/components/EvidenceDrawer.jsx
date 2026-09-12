import { X } from 'lucide-react'
export default function EvidenceDrawer({ open, onClose, evidence }) {
  if (!open) return null
  return <div className="fixed inset-0 z-50 bg-ink/20" onClick={onClose}><aside role="dialog" aria-label="Resume evidence" className="absolute inset-y-0 right-0 w-full max-w-md bg-white p-7" onClick={e => e.stopPropagation()}><button aria-label="Close evidence" onClick={onClose}><X /></button><h2 className="my-5 text-xl font-bold">Resume evidence</h2><p>{evidence?.evidence_passage || evidence?.matched_text || 'Evidence text not provided by the server.'}</p>{evidence?.page_number != null && <p className="mt-4">Page {evidence.page_number}</p>}</aside></div>
}
