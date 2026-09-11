import { useEffect, useState } from 'react'
import { ArrowUpRight, BriefcaseBusiness, MoreHorizontal, Plus } from 'lucide-react'
import { Link } from 'react-router-dom'
import ErrorBanner from '../components/ErrorBanner'
import { jobs as mockJobs } from '../data/mockData'
import { getJobs } from '../services/api'

export default function Jobs() {
  const [jobList, setJobList] = useState(mockJobs)
  const [loading, setLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState(null)

  useEffect(() => {
    async function loadJobs() {
      try {
        setLoading(true)
        const data = await getJobs()
        if (Array.isArray(data) && data.length > 0) {
          const formatted = data.map((j, idx) => ({
            id: j.job_id || idx + 1,
            job_id: j.job_id,
            title: j.title || 'Software Engineer',
            department: j.department || j.domain?.[0] || 'Engineering',
            applicants: j.applicants || 15,
            updated: j.updated || 'Active',
            status: j.status || 'Active',
            skills: j.must_have_skills || j.skills || ['Python', 'FastAPI']
          }))
          setJobList(formatted)
        } else {
          setJobList(mockJobs)
        }
      } catch (err) {
        setErrorMsg(err.message || 'Could not fetch jobs from backend server. Showing demo jobs.')
        setJobList(mockJobs)
      } finally {
        setLoading(false)
      }
    }
    loadJobs()
  }, [])

  return (
    <div className="mx-auto max-w-7xl">
      {errorMsg && (
        <ErrorBanner message={errorMsg} onClose={() => setErrorMsg(null)} />
      )}

      <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="eyebrow mb-2">Hiring workspace</p>
          <h1 className="text-3xl font-extrabold tracking-tight">Jobs</h1>
          <p className="mt-2 text-sm text-muted">Create requirements and find the right people faster.</p>
        </div>
        <Link to="/jobs/create" className="btn-primary">
          <Plus size={17} />Create job
        </Link>
      </div>

      {loading ? (
        <div className="panel p-12 text-center text-sm font-semibold text-muted">
          Loading job definitions...
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {jobList.map(job => (
            <div className="panel p-5" key={job.id || job.job_id}>
              <div className="mb-7 flex items-start justify-between">
                <span className="grid h-11 w-11 place-items-center rounded-xl bg-mint text-teal">
                  <BriefcaseBusiness size={20} />
                </span>
                <button className="text-muted">
                  <MoreHorizontal size={18} />
                </button>
              </div>
              <span className={`rounded-full px-2 py-1 text-[10px] font-bold ${job.status === 'Active' ? 'bg-mint text-teal' : 'bg-[#fff6d9] text-[#a17612]'}`}>
                {job.status}
              </span>
              <h2 className="mt-3 text-lg font-extrabold">{job.title}</h2>
              <p className="mt-1 text-xs text-muted">{job.department}</p>
              <div className="my-6 flex flex-wrap gap-1.5">
                {(job.skills || []).map(skill => (
                  <span className="rounded-md bg-canvas px-2 py-1 text-[10px] font-bold text-muted" key={skill}>
                    {skill}
                  </span>
                ))}
              </div>
              <div className="flex items-center justify-between border-t pt-4 text-xs text-muted">
                <span>{job.applicants} applicants</span>
                <Link to="/ranking" className="flex items-center gap-1 font-bold text-teal">
                  View ranking <ArrowUpRight size={14} />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}