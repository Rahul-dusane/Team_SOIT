import { useEffect, useState, useCallback } from 'react'
import { FileText, Filter, Search, Upload } from 'lucide-react'
import UploadArea from '../components/UploadArea'
import CandidateCard from '../components/CandidateCard'
import ErrorBanner from '../components/ErrorBanner'
import { candidates as mockCandidates } from '../data/mockData'
import { getCandidates, formatCandidateForUI } from '../services/api'

export default function Resumes() {
  const [query, setQuery] = useState('')
  const [candidatesList, setCandidatesList] = useState(mockCandidates)
  const [loading, setLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState(null)

  const fetchCandidates = useCallback(async () => {
    try {
      setLoading(true)
      const data = await getCandidates()
      if (Array.isArray(data) && data.length > 0) {
        const formatted = data.map((c, i) => formatCandidateForUI(c, i))
        setCandidatesList(formatted)
      } else {
        setCandidatesList(mockCandidates)
      }
    } catch (err) {
      setErrorMsg(err.message || 'Could not fetch candidates from backend. Displaying demo candidates.')
      setCandidatesList(mockCandidates)
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
    (c.skills || []).some(s => s.toLowerCase().includes(query.toLowerCase()))
  )

  return (
    <div className="mx-auto max-w-7xl">
      {errorMsg && (
        <ErrorBanner message={errorMsg} onClose={() => setErrorMsg(null)} />
      )}

      <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="eyebrow mb-2">Talent pool</p>
          <h1 className="text-3xl font-extrabold tracking-tight">Resumes</h1>
          <p className="mt-2 text-sm text-muted">Upload and organize your candidate pipeline.</p>
        </div>
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          className="btn-primary"
        >
          <Upload size={16} />Upload resumes
        </button>
      </div>

      <div className="mb-8 grid gap-6 lg:grid-cols-[.8fr_1.2fr]">
        <UploadArea onUploadSuccess={fetchCandidates} />
        <div className="panel flex flex-col justify-between p-6">
          <div>
            <div className="mb-4 flex items-center gap-3">
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-mint text-teal">
                <FileText size={18} />
              </span>
              <div>
                <p className="font-bold">Resume parsing engine</p>
                <p className="text-xs text-muted">
                  {candidatesList.length} candidates in database
                </p>
              </div>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-[#edf1f1]">
              <div className="h-full w-[85%] rounded-full bg-teal" />
            </div>
          </div>
          <p className="mt-4 text-xs leading-5 text-muted">
            HireLens extracts experience, skills, education, projects, and certifications automatically with pgvector indexing.
          </p>
        </div>
      </div>

      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-extrabold">
            All candidates <span className="text-muted">({filtered.length})</span>
          </h2>
        </div>
        <div className="flex gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 text-muted" size={16} />
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              className="rounded-lg border bg-white py-2 pl-9 pr-3 text-xs outline-none focus:border-teal"
              placeholder="Search candidates by name, role, skill"
            />
          </div>
          <button className="btn-soft px-3">
            <Filter size={15} />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="panel p-12 text-center text-sm font-semibold text-muted">
          Loading candidates...
        </div>
      ) : filtered.length === 0 ? (
        <div className="panel p-12 text-center text-sm text-muted">
          No candidates found matching "{query}".
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((c, i) => (
            <CandidateCard key={c.id || c.candidate_id || i} candidate={c} />
          ))}
        </div>
      )}
    </div>
  )
}