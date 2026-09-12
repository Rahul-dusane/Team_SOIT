import { useEffect, useState, useCallback } from 'react'
import { FileText, Search, Sparkles } from 'lucide-react'
import UploadArea from '../components/UploadArea'
import CandidateCard from '../components/CandidateCard'
import ErrorBanner from '../../../core/components/ErrorBanner'
import { getCandidates, formatCandidateForUI } from '../../../core/api/api'

export default function Resumes() {
  const [query, setQuery] = useState('')
  const [candidatesList, setCandidatesList] = useState([])
  const [loading, setLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState(null)

  const fetchCandidates = useCallback(async () => {
    try {
      setLoading(true)
      setErrorMsg(null)
      const data = await getCandidates()
      if (Array.isArray(data) && data.length > 0) {
        const formatted = data.map((c, i) => formatCandidateForUI(c, i))
        setCandidatesList(formatted)
      } else {
        setCandidatesList([])
      }
    } catch (err) {
      setErrorMsg(err.message || 'Could not fetch candidates from backend.')
      setCandidatesList([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchCandidates()
  }, [fetchCandidates])

  const filtered = candidatesList.filter(c =>
    (c.name || '').toLowerCase().includes(query.toLowerCase()) ||
    (c.role || '').toLowerCase().includes(query.toLowerCase()) ||
    (c.skills || []).some(s => typeof s === 'string' && s.toLowerCase().includes(query.toLowerCase()))
  )

  return (
    <div className="space-y-8">
      {errorMsg && <ErrorBanner message={errorMsg} onClose={() => setErrorMsg(null)} />}

      {/* Header Banner */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <div className="inline-flex items-center gap-1.5 pill-badge bg-apple-blue/10 text-apple-blue border border-apple-blue/20 mb-2">
            <Sparkles size={12} /> Candidate Pool Management
          </div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Ingested Resumes</h1>
          <p className="mt-1 text-sm text-slate-500">Upload, search, and manage candidate vectors stored in PostgreSQL pgvector.</p>
        </div>
      </div>

      {/* Upload Zone & Stats Grid */}
      <div className="grid gap-8 lg:grid-cols-12">
        <div className="lg:col-span-7">
          <UploadArea onUploadSuccess={fetchCandidates} />
        </div>

        <div className="lg:col-span-5">
          <div className="panel h-full flex flex-col justify-between p-6 bg-gradient-to-br from-white to-slate-50/80 shadow-apple-card">
            <div>
              <div className="mb-4 flex items-center gap-3.5">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-slate-900 to-napkin-purple text-white shadow-md">
                  <FileText size={22} />
                </div>
                <div>
                  <h3 className="text-base font-extrabold text-slate-900">384-Dim Vector Index</h3>
                  <p className="text-xs font-semibold text-slate-500">
                    {loading ? 'Fetching candidate index...' : `${candidatesList.length} total candidates stored`}
                  </p>
                </div>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Resumes uploaded are automatically chunked into passages and embedded using <code className="font-mono text-[11px] bg-slate-100 px-1.5 py-0.5 rounded text-apple-blue">sentence-transformers/all-MiniLM-L6-v2</code> for exact and semantic skill matching.
              </p>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-200/60 flex items-center justify-between text-xs font-semibold text-slate-500">
              <span>Status: Ready for Matching</span>
              <span className="flex h-2 w-2 rounded-full bg-emerald-500 shadow-glow" />
            </div>
          </div>
        </div>
      </div>

      {/* Candidate Grid Section */}
      <div className="space-y-4">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">
              All Candidates <span className="text-slate-400 font-normal">({filtered.length})</span>
            </h2>
          </div>

          <div className="relative w-full sm:w-80">
            <Search className="absolute left-3.5 top-3 text-slate-400" size={16} />
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-xs font-semibold text-slate-800 placeholder-slate-400 outline-none transition-all focus:border-apple-blue focus:ring-2 focus:ring-apple-blue/20"
              placeholder="Search by name, role, skill..."
            />
          </div>
        </div>

        {loading ? (
          <div className="panel p-12 text-center text-slate-400 font-medium">Loading candidate profiles from database...</div>
        ) : filtered.length === 0 ? (
          <div className="panel p-12 text-center text-slate-500">
            No candidates match your search filter "{query}".
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            {filtered.map((c, i) => (
              <CandidateCard key={c.id || c.candidate_id || i} candidate={c} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
