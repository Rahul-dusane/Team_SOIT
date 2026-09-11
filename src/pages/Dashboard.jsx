import { useEffect, useState } from 'react'
import { ArrowUpRight, BarChart3, BriefcaseBusiness, FileText, Plus, Users } from 'lucide-react'
import { Link } from 'react-router-dom'
import StatCard from '../components/StatCard'
import CandidateCard from '../components/CandidateCard'
import AgentTimeline from '../components/AgentTimeline'
import ErrorBanner from '../components/ErrorBanner'
import { candidates as mockCandidates, jobs as mockJobs } from '../data/mockData'
import { getCandidates, getDashboardStats, getJobs, formatCandidateForUI } from '../services/api'

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_candidates: 128,
    active_jobs: 12,
    total_matches: 246,
    strong_matches: 64
  })
  const [candidateList, setCandidateList] = useState(mockCandidates)
  const [jobList, setJobList] = useState(mockJobs)
  const [loading, setLoading] = useState(true)
  const [offlineNotice, setOfflineNotice] = useState(null)

  useEffect(() => {
    let isMounted = true

    async function loadDashboardData() {
      try {
        const [statsData, candsData, jobsData] = await Promise.allSettled([
          getDashboardStats(),
          getCandidates(),
          getJobs()
        ])

        if (!isMounted) return

        let isApiOffline = false

        if (statsData.status === 'fulfilled' && statsData.value) {
          const s = statsData.value
          setStats(old => ({
            ...old,
            total_candidates: s.total_candidates ?? old.total_candidates,
            active_jobs: s.active_jobs ?? old.active_jobs
          }))
        } else if (statsData.reason?.isOffline) {
          isApiOffline = true
        }

        if (candsData.status === 'fulfilled' && Array.isArray(candsData.value) && candsData.value.length > 0) {
          const formatted = candsData.value.map((c, i) => formatCandidateForUI(c, i))
          setCandidateList(formatted)
        } else {
          setCandidateList(mockCandidates)
        }

        if (jobsData.status === 'fulfilled' && Array.isArray(jobsData.value) && jobsData.value.length > 0) {
          setJobList(jobsData.value.map((j, i) => ({
            id: j.job_id || i + 1,
            title: j.title || 'Senior Software Engineer',
            department: j.department || j.domain?.[0] || 'Engineering',
            applicants: j.applicants || 12,
            updated: j.updated || 'Just now',
            status: j.status || 'Active',
            skills: j.must_have_skills || j.skills || ['Python', 'FastAPI']
          })))
        } else {
          setJobList(mockJobs)
        }

        if (isApiOffline) {
          setOfflineNotice('Backend server is offline or unreachable. Displaying workspace demo mode.')
        }

      } catch (err) {
        if (isMounted) {
          setOfflineNotice(err.message || 'Connecting to backend service...')
        }
      } finally {
        if (isMounted) setLoading(false)
      }
    }

    loadDashboardData()
    return () => { isMounted = false }
  }, [])

  return (
    <div className="mx-auto max-w-7xl">
      {offlineNotice && (
        <ErrorBanner
          message={offlineNotice}
          isOffline={true}
          onClose={() => setOfflineNotice(null)}
        />
      )}

      <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="eyebrow mb-2">Monday, September 11, 2026</p>
          <h1 className="text-3xl font-extrabold tracking-tight">Good morning, Anika</h1>
          <p className="mt-2 text-sm text-muted">Here’s what’s happening across your hiring workspace.</p>
        </div>
        <Link to="/jobs/create" className="btn-primary">
          <Plus size={17} />Create a job
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total candidates" value={String(stats.total_candidates)} change={12} icon={Users} />
        <StatCard label="Active jobs" value={String(stats.active_jobs)} change={8} icon={BriefcaseBusiness} />
        <StatCard label="Total matches" value={String(stats.total_matches)} change={18} icon={BarChart3} tone="coral" />
        <StatCard label="Strong matches" value={String(stats.strong_matches)} change={-4} icon={FileText} />
      </div>

      <div className="mt-8 grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <section className="panel p-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <p className="eyebrow mb-2">Top matches</p>
              <h2 className="text-xl font-extrabold">Candidates worth a look</h2>
            </div>
            <Link to="/ranking" className="flex items-center gap-1 text-xs font-bold text-teal">
              View all <ArrowUpRight size={14} />
            </Link>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {candidateList.slice(0, 2).map(c => (
              <CandidateCard key={c.id || c.candidate_id} candidate={c} />
            ))}
          </div>
        </section>

        <section className="panel p-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <p className="eyebrow mb-2">Pipeline snapshot</p>
              <h2 className="text-xl font-extrabold">Active jobs</h2>
            </div>
            <Link to="/jobs" className="text-xs font-bold text-teal">Manage</Link>
          </div>
          <div className="space-y-3">
            {jobList.map(job => (
              <div key={job.id} className="rounded-xl border p-4">
                <div className="flex justify-between">
                  <div>
                    <h3 className="text-sm font-bold">{job.title}</h3>
                    <p className="mt-1 text-xs text-muted">{job.department}</p>
                  </div>
                  <span className={`rounded-full px-2 py-1 text-[10px] font-bold ${job.status === 'Active' ? 'bg-mint text-teal' : 'bg-[#fff6d9] text-[#a17612]'}`}>
                    {job.status}
                  </span>
                </div>
                <div className="mt-4 flex justify-between text-xs text-muted">
                  <span>{job.applicants} applicants</span>
                  <span>{job.updated}</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="panel mt-6 p-6">
        <div className="mb-5">
          <p className="eyebrow mb-2">Live processing</p>
          <h2 className="text-xl font-extrabold">Agent workflow</h2>
        </div>
        <AgentTimeline />
      </section>
    </div>
  )
}