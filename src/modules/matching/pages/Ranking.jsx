import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Trophy, Search, Award, ArrowUpRight } from 'lucide-react'
import MatchScore from '../components/MatchScore'
import ErrorBanner from '../../../core/components/ErrorBanner'
import { getRanking, getCandidates, getJobs } from '../../../core/api/api'
import { mergeRankings } from '../../../core/api/viewData'

export default function Ranking() {
  const [params, setParams] = useSearchParams()
  const jobId = params.get('job_id') || ''
  const [jobs, setJobs] = useState([])
  const [rows, setRows] = useState([])
  const [title, setTitle] = useState('')
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    setLoading(true); setRows([]); setTitle(''); setError('')
    Promise.all([getRanking(jobId), getCandidates(), getJobs()])
      .then(([ranking, candidates, jobs]) => {
        if (!active) return
        if (!Array.isArray(candidates) || !Array.isArray(jobs)) throw new Error('Invalid server response.')
        setJobs(jobs)
        setRows(mergeRankings(ranking, candidates))
        setTitle(ranking.job_title || 'Target Job')
      })
      .catch(e => { if (active) setError(e.message) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [jobId])

  const filtered = useMemo(
    () => rows.filter(c => `${c.name || ''} ${c.role || ''}`.toLowerCase().includes(query.toLowerCase())),
    [rows, query]
  )

  const topThree = filtered.slice(0, 3)

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <div className="inline-flex items-center gap-1.5 pill-badge bg-napkin-purple/10 text-napkin-purple border border-napkin-purple/20 mb-2">
            <Trophy size={12} /> Candidate Leaderboard
          </div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Rankings Engine</h1>
          <p className="mt-1 text-sm text-slate-500">Sorted compatibility rankings for <span className="font-bold text-slate-800">{title}</span></p>
        </div>

        {/* Job Selector Dropdown & Search */}
        <div className="flex flex-wrap gap-3">
          <select
            aria-label="Ranking job"
            className="rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-xs font-bold text-slate-800 shadow-xs outline-none focus:border-apple-blue"
            value={jobId}
            onChange={e => setParams(e.target.value ? { job_id: e.target.value } : {})}
          >
            <option value="">Select Job Filter</option>
            {jobs.map(j => (
              <option key={j.job_id} value={j.job_id}>
                {j.title}
              </option>
            ))}
          </select>

          <div className="relative">
            <Search className="absolute left-3.5 top-3 text-slate-400" size={15} />
            <input
              aria-label="Search ranked candidates"
              className="rounded-2xl border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-xs font-semibold text-slate-800 outline-none focus:border-apple-blue"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search by candidate or role..."
            />
          </div>
        </div>
      </div>

      <ErrorBanner message={error} />

      {/* Top 3 Podium Highlights Grid */}
      {!loading && topThree.length > 0 && (
        <div className="grid gap-6 sm:grid-cols-3">
          {topThree.map((candidate, idx) => {
            const ranks = ['1st Place', '2nd Place', '3rd Place']
            const badgeColors = [
              'bg-amber-500/10 text-amber-600 border-amber-500/30',
              'bg-slate-200/80 text-slate-700 border-slate-300',
              'bg-orange-500/10 text-orange-700 border-orange-500/20'
            ]
            return (
              <div
                key={candidate.match_id || candidate.id || idx}
                className="panel relative overflow-hidden p-6 shadow-apple-card transition-all duration-300 hover:-translate-y-1"
              >
                <div className="flex items-center justify-between mb-4">
                  <span className={`pill-badge ${badgeColors[idx]}`}>
                    <Award size={13} /> {ranks[idx]}
                  </span>
                  <MatchScore score={candidate.score} decision={candidate.decision} />
                </div>

                <h3 className="text-base font-extrabold text-slate-900 tracking-tight">
                  {candidate.name || 'Candidate'}
                </h3>
                <p className="text-xs text-slate-500 font-medium">{candidate.role || 'Role N/A'}</p>
                <p className="mt-1 text-[11px] text-slate-400">Exp: {candidate.experience || 'N/A'}</p>

                <Link
                  to={`/matches/${encodeURIComponent(candidate.match_id || candidate.id)}`}
                  className="mt-4 flex items-center justify-between pt-3 border-t border-slate-100 text-xs font-bold text-apple-blue"
                >
                  <span>Inspect Analysis</span>
                  <ArrowUpRight size={15} />
                </Link>
              </div>
            )
          })}
        </div>
      )}

      {/* Full Leaderboard Table Section */}
      <section className="panel p-6 shadow-panel">
        <h3 className="text-base font-extrabold text-slate-900 tracking-tight mb-4">
          Complete Leaderboard List ({filtered.length})
        </h3>

        {loading ? (
          <p className="py-8 text-center text-slate-400">Computing candidate rankings...</p>
        ) : error ? (
          <p className="py-8 text-center text-slate-500">Rankings unavailable.</p>
        ) : !filtered.length ? (
          <p className="py-8 text-center text-slate-400">No candidate rankings found for this query.</p>
        ) : (
          <div className="divide-y divide-slate-100">
            {filtered.map(c => (
              <Link
                key={c.match_id || c.id}
                to={`/matches/${encodeURIComponent(c.match_id || c.id)}`}
                className="group flex flex-wrap items-center justify-between gap-4 py-4 px-2 transition-colors duration-200 hover:bg-slate-50/80 rounded-2xl"
              >
                <div className="flex items-center gap-4">
                  <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-slate-100 text-xs font-extrabold text-slate-700 font-mono">
                    #{c.rank ?? '-'}
                  </span>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900 group-hover:text-apple-blue transition-colors">
                      {c.name}
                    </h4>
                    <p className="text-xs text-slate-500">
                      {c.role || 'Role N/A'} · {c.experience || 'No exp data'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  <MatchScore score={c.score} decision={c.decision} />
                  <ArrowUpRight size={18} className="text-slate-300 group-hover:text-apple-blue group-hover:translate-x-0.5 transition-all" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
