import { useEffect, useState } from 'react'
import { BarChart3, BriefcaseBusiness, FileText, Users } from 'lucide-react'
import { Link } from 'react-router-dom'
import StatCard from '../components/StatCard'
import CandidateCard from '../components/CandidateCard'
import ErrorBanner from '../components/ErrorBanner'
import { getCandidates, getDashboardStats, getJobs, formatCandidateForUI } from '../services/api'
import { formatJobForUI } from '../services/viewData'

export default function Dashboard() {
  const [stats, setStats] = useState({})
  const [candidates, setCandidates] = useState([])
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [errors, setErrors] = useState([])
  useEffect(() => {
    let active = true
    Promise.allSettled([getDashboardStats(), getCandidates(), getJobs()]).then(results => {
      if (!active) return
      const [s,c,j] = results
      if (s.status === 'fulfilled') setStats(s.value || {})
      if (c.status === 'fulfilled' && Array.isArray(c.value)) setCandidates(c.value.map(formatCandidateForUI))
      if (j.status === 'fulfilled' && Array.isArray(j.value)) setJobs(j.value.map(formatJobForUI))
      setErrors(results.flatMap((r,i) => r.status === 'rejected' ? [`${['Statistics','Candidates','Jobs'][i]}: ${r.reason.message}`] : i > 0 && !Array.isArray(r.value) ? [`${['Statistics','Candidates','Jobs'][i]}: Invalid server response.`] : []))
      setLoading(false)
    })
    return () => { active = false }
  }, [])
  return <div className="mx-auto max-w-7xl">
    <h1 className="mb-2 text-3xl font-extrabold">Workspace overview</h1><p className="mb-8 text-sm text-muted">{new Date().toLocaleDateString(undefined, { dateStyle: 'full' })}</p>
    {errors.map(error => <ErrorBanner key={error} message={error} />)}
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{[['Total candidates','total_candidates',Users],['Active jobs','active_jobs',BriefcaseBusiness],['Total matches','total_matches',BarChart3],['Strong matches','strong_matches',FileText]].map(([label,key,icon]) => <StatCard key={key} label={label} value={loading ? 'Loading…' : stats[key] ?? 'Unavailable'} icon={icon} />)}</div>
    <div className="mt-8 grid gap-6 xl:grid-cols-2"><section className="panel p-6"><h2 className="mb-5 text-xl font-bold">Candidate profiles</h2>{loading ? <p>Loading candidates…</p> : candidates.length ? <div className="grid gap-4">{candidates.slice(0,2).map(c => <CandidateCard key={c.id} candidate={c} />)}</div> : <p>No candidate data to display.</p>}<Link to="/resumes" className="mt-5 block text-teal">View candidates</Link></section>
    <section className="panel p-6"><h2 className="mb-5 text-xl font-bold">Saved jobs</h2>{loading ? <p>Loading jobs…</p> : jobs.length ? jobs.map(job => <Link className="mb-3 block rounded-xl border p-4" key={job.id} to={`/ranking?job_id=${encodeURIComponent(job.id)}`}><strong>{job.title}</strong><p className="text-sm text-muted">{job.department}</p></Link>) : <p>No job data to display.</p>}<Link to="/jobs" className="text-teal">View jobs</Link></section></div>
  </div>
}
