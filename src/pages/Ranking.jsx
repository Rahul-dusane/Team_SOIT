import { useEffect, useMemo, useState } from 'react'
import { ArrowDownUp, ChevronDown, Filter, Search } from 'lucide-react'
import { Link } from 'react-router-dom'
import MatchScore from '../components/MatchScore'
import ErrorBanner from '../components/ErrorBanner'
import { candidates as mockCandidates } from '../data/mockData'
import { getRanking, getCandidates, formatCandidateForUI } from '../services/api'

export default function Ranking() {
  const [query, setQuery] = useState('')
  const [sort, setSort] = useState('score')
  const [candidateList, setCandidateList] = useState(mockCandidates)
  const [jobTitle, setJobTitle] = useState('Senior Backend Engineer')
  const [loading, setLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState(null)

  useEffect(() => {
    async function loadRankingData() {
      try {
        setLoading(true)
        const [rankingData, candidateData] = await Promise.allSettled([
          getRanking(),
          getCandidates()
        ])

        let baseCandidates = mockCandidates
        if (candidateData.status === 'fulfilled' && Array.isArray(candidateData.value) && candidateData.value.length > 0) {
          baseCandidates = candidateData.value.map((c, i) => formatCandidateForUI(c, i))
        }

        if (rankingData.status === 'fulfilled' && rankingData.value) {
          const rData = rankingData.value
          if (rData.job_title) {
            setJobTitle(rData.job_title)
          }

          if (Array.isArray(rData.rankings) && rData.rankings.length > 0) {
            // merge rankings with base candidates
            const rankedList = rData.rankings.map((r, idx) => {
              const matchedCand = baseCandidates.find(c => c.candidate_id === r.candidate_id || c.id === r.candidate_id)
              if (matchedCand) {
                return {
                  ...matchedCand,
                  score: Math.round(r.overall_score || matchedCand.score),
                  status: r.decision || matchedCand.status
                }
              }
              return formatCandidateForUI({
                candidate_id: r.candidate_id,
                name: `Candidate ${r.candidate_id}`,
                overall_score: r.overall_score,
                status: r.decision
              }, idx)
            })
            setCandidateList(rankedList)
          } else {
            setCandidateList(baseCandidates)
          }
        } else {
          setCandidateList(baseCandidates)
        }
      } catch (err) {
        setErrorMsg(err.message || 'Could not fetch live ranking from server. Showing demo rankings.')
        setCandidateList(mockCandidates)
      } finally {
        setLoading(false)
      }
    }
    loadRankingData()
  }, [])

  const filtered = useMemo(() => {
    return candidateList
      .filter(c => (c.name || '').toLowerCase().includes(query.toLowerCase()) || (c.role || '').toLowerCase().includes(query.toLowerCase()))
      .sort((a, b) => sort === 'score' ? (b.score || 0) - (a.score || 0) : (a.name || '').localeCompare(b.name || ''))
  }, [candidateList, query, sort])

  return (
    <div className="mx-auto max-w-7xl">
      {errorMsg && (
        <ErrorBanner message={errorMsg} onClose={() => setErrorMsg(null)} />
      )}

      <div className="mb-8">
        <p className="eyebrow mb-2">{jobTitle}</p>
        <h1 className="text-3xl font-extrabold tracking-tight">Candidate ranking</h1>
        <p className="mt-2 text-sm text-muted">{filtered.length} candidates ranked by relevance to this role.</p>
      </div>

      <div className="panel overflow-hidden">
        <div className="flex flex-col gap-3 border-b p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 text-muted" size={16} />
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search candidates"
              className="w-full rounded-lg border bg-canvas py-2 pl-9 pr-3 text-xs outline-none focus:border-teal sm:w-64"
            />
          </div>

          <div className="flex gap-2">
            <button className="btn-soft px-3">
              <Filter size={15} /> <span className="hidden sm:inline">Filter</span>
            </button>
            <button onClick={() => setSort(sort === 'score' ? 'name' : 'score')} className="btn-soft px-3">
              <ArrowDownUp size={15} /> <span className="hidden sm:inline">{sort === 'score' ? 'Sort by score' : 'Sort by name'}</span>
            </button>
          </div>
        </div>

        <div className="hidden grid-cols-[60px_1fr_150px_130px_120px] gap-4 border-b bg-canvas px-6 py-3 text-[10px] font-bold uppercase tracking-wider text-muted md:grid">
          <span>Rank</span>
          <span>Candidate</span>
          <span>Experience</span>
          <span>Match score</span>
          <span>Status</span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-sm font-semibold text-muted">
            Calculating rankings...
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center text-sm text-muted">
            No candidate rankings found.
          </div>
        ) : (
          <div>
            {filtered.map((candidate, index) => (
              <Link
                to={`/matches/${candidate.id || candidate.candidate_id}`}
                key={candidate.id || candidate.candidate_id || index}
                className="grid grid-cols-[1fr_auto] items-center gap-4 border-b px-5 py-4 transition last:border-0 hover:bg-canvas md:grid-cols-[60px_1fr_150px_130px_120px] md:px-6"
              >
                <span className="hidden text-sm font-extrabold text-muted md:block">
                  {String(index + 1).padStart(2, '0')}
                </span>

                <div className="flex items-center gap-3">
                  <div className={`grid h-9 w-9 place-items-center rounded-full text-[10px] font-extrabold ${candidate.avatar}`}>
                    {candidate.initials}
                  </div>
                  <div>
                    <p className="text-sm font-bold">{candidate.name}</p>
                    <p className="text-[11px] text-muted">{candidate.role}</p>
                  </div>
                </div>

                <span className="hidden text-xs text-muted md:block">{candidate.experience}</span>
                <MatchScore score={candidate.score} />
                <span className={`hidden rounded-full px-2 py-1 text-center text-[10px] font-bold md:block ${candidate.status === 'Strong' || candidate.status === 'HIGH' ? 'bg-mint text-teal' : candidate.status === 'Moderate' || candidate.status === 'MEDIUM' ? 'bg-[#fff6d9] text-[#a17612]' : 'bg-canvas text-muted'}`}>
                  {candidate.status}
                </span>
                <ChevronDown className="-rotate-90 text-muted md:hidden" size={16} />
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}