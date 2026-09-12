import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import MatchScore from '../components/MatchScore'
import ErrorBanner from '../components/ErrorBanner'
import { getRanking, getCandidates, getJobs } from '../services/api'
import { mergeRankings } from '../services/viewData'

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
    Promise.all([getRanking(jobId), getCandidates(), getJobs()]).then(([ranking, candidates, jobs]) => {
      if (!active) return
      if (!Array.isArray(candidates) || !Array.isArray(jobs)) throw new Error('Invalid server response.')
      setJobs(jobs); setRows(mergeRankings(ranking,candidates)); setTitle(ranking.job_title || 'Job title unavailable')
    }).catch(e => { if (active) setError(e.message) }).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [jobId])
  const filtered = useMemo(() => rows.filter(c => `${c.name} ${c.role}`.toLowerCase().includes(query.toLowerCase())), [rows, query])
  return <div className="mx-auto max-w-7xl"><h1 className="text-3xl font-extrabold">Candidate ranking</h1><p className="my-3 text-muted">{title}</p><ErrorBanner message={error} />
    <div className="my-6 flex flex-wrap gap-3"><select aria-label="Ranking job" className="rounded-lg border p-3" value={jobId} onChange={e => setParams(e.target.value ? { job_id: e.target.value } : {})}><option value="">Default job</option>{jobs.map(j => <option key={j.job_id} value={j.job_id}>{j.title}</option>)}</select><input aria-label="Search ranked candidates" className="rounded-lg border p-3" value={query} onChange={e => setQuery(e.target.value)} placeholder="Search ranked candidates" /></div>
    <section className="panel p-6">{loading ? <p>Loading rankings…</p> : error ? <p>Rankings unavailable.</p> : !filtered.length ? <p>No candidate rankings found.</p> : filtered.map(c => <Link key={c.match_id} to={`/matches/${encodeURIComponent(c.match_id)}`} className="flex items-center justify-between gap-4 border-b py-5"><span className="text-muted">Rank {c.rank ?? 'unavailable'}</span><div className="flex-1"><strong>{c.name}</strong><p className="text-sm text-muted">{c.role} · {c.experience}</p></div><MatchScore score={c.score} /><span className="text-xs">{c.status}</span></Link>)}</section>
  </div>
}
