import { useEffect, useState } from 'react'
import { ArrowUpRight, BriefcaseBusiness, Plus, Sparkles, Building2, CheckCircle2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import ErrorBanner from '../../../core/components/ErrorBanner'
import SkillBadge from '../../../core/components/SkillBadge'
import { formatJobForUI } from '../../../core/api/viewData'
import { getJobs } from '../../../core/api/api'

export default function Jobs() {
  const [jobList, setJobList] = useState([])
  const [loading, setLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState(null)

  useEffect(() => {
    async function loadJobs() {
      try {
        setLoading(true)
        const data = await getJobs()
        if (Array.isArray(data) && data.length > 0) {
          const formatted = data.map(formatJobForUI)
          setJobList(formatted)
        } else {
          setJobList([])
        }
      } catch (err) {
        setErrorMsg(err.message || 'Could not fetch jobs from backend server.')
        setJobList([])
      } finally {
        setLoading(false)
      }
    }
    loadJobs()
  }, [])

  return (
    <div className="space-y-8">
      {errorMsg && <ErrorBanner message={errorMsg} onClose={() => setErrorMsg(null)} />}

      {/* Header Banner */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <div className="inline-flex items-center gap-1.5 pill-badge bg-apple-blue/10 text-apple-blue border border-apple-blue/20 mb-2">
            <Sparkles size={12} /> Job Profile Definitions
          </div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Active Jobs</h1>
          <p className="mt-1 text-sm text-slate-500">Define job requirements, mandatory constraints, and run candidate rankings.</p>
        </div>

        <Link to="/jobs/create" className="btn-primary">
          <Plus size={17} /> Create New Job
        </Link>
      </div>

      {/* Job Card Grid */}
      {loading ? (
        <div className="panel p-12 text-center text-slate-400 font-medium">Loading job definitions from database...</div>
      ) : jobList.length === 0 ? (
        <div className="panel p-12 text-center text-slate-500">
          No job profiles created yet. Click "Create New Job" to define target requirements.
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {jobList.map(job => (
            <div
              key={job.id || job.job_id}
              className="panel group p-6 shadow-apple-card transition-all duration-300 hover:-translate-y-1 hover:shadow-panel flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-slate-900 to-apple-blue text-white shadow-md transition-transform duration-300 group-hover:scale-105">
                    <BriefcaseBusiness size={22} />
                  </div>
                  <span className="pill-badge bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">
                    <CheckCircle2 size={12} /> Active
                  </span>
                </div>

                <h3 className="text-lg font-black text-slate-900 tracking-tight group-hover:text-apple-blue transition-colors">
                  {job.title}
                </h3>
                <p className="mt-0.5 text-xs font-semibold text-slate-500 flex items-center gap-1.5">
                  <Building2 size={13} className="text-slate-400" />
                  {job.department} · Min {job.min_experience_months || 0} mos exp
                </p>

                <div className="my-5 flex flex-wrap gap-1.5 min-h-[32px]">
                  {(job.skills || []).slice(0, 5).map(skill => (
                    <SkillBadge key={skill}>{skill}</SkillBadge>
                  ))}
                </div>
              </div>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400">Target Role Match</span>
                <Link
                  to={`/ranking?job_id=${encodeURIComponent(job.id || job.job_id)}`}
                  className="flex items-center gap-1 text-xs font-extrabold text-apple-blue group-hover:underline"
                >
                  View Leaderboard <ArrowUpRight size={15} />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
