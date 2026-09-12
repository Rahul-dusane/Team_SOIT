import { useEffect, useState } from 'react'
import { BarChart3, BriefcaseBusiness, FileText, Users, Sparkles, ArrowRight, UploadCloud, Cpu, ShieldCheck, Layers, Award } from 'lucide-react'
import { Link } from 'react-router-dom'
import StatCard from '../../../core/components/StatCard'
import CandidateCard from '../../candidates/components/CandidateCard'
import ErrorBanner from '../../../core/components/ErrorBanner'
import { getCandidates, getDashboardStats, getJobs, formatCandidateForUI } from '../../../core/api/api'
import { formatJobForUI } from '../../../core/api/viewData'

export default function Dashboard() {
  const [stats, setStats] = useState({})
  const [candidates, setCandidates] = useState([])
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [errors, setErrors] = useState([])
  const [activeTab, setActiveTab] = useState(0)

  useEffect(() => {
    let active = true
    Promise.allSettled([getDashboardStats(), getCandidates(), getJobs()]).then(results => {
      if (!active) return
      const [s, c, j] = results
      if (s.status === 'fulfilled') setStats(s.value || {})
      if (c.status === 'fulfilled' && Array.isArray(c.value)) setCandidates(c.value.map(formatCandidateForUI))
      if (j.status === 'fulfilled' && Array.isArray(j.value)) setJobs(j.value.map(formatJobForUI))
      setErrors(
        results.flatMap((r, i) =>
          r.status === 'rejected'
            ? [`${['Statistics', 'Candidates', 'Jobs'][i]}: ${r.reason?.message || 'Server error'}`]
            : i > 0 && !Array.isArray(r.value)
            ? [`${['Statistics', 'Candidates', 'Jobs'][i]}: Invalid server payload.`]
            : []
        )
      )
      setLoading(false)
    })
    return () => { active = false }
  }, [])

  const showcaseTabs = [
    {
      id: 'pipeline',
      title: '5-Agent LangGraph Pipeline',
      icon: Cpu,
      eyebrow: 'Autonomous AI Orchestration',
      heading: 'Deterministic & LLM Reasoning Combined',
      description: 'Sequential multi-agent execution pipeline evaluating resume structure, job requirements, hard constraints, category weights, and recruiter summaries.',
      pills: ['Resume Structurer', 'Job Parser', 'Constraint Checker', 'Scorer Agent', 'Executive Summarizer']
    },
    {
      id: 'vector',
      title: '384-Dim Vector Matcher',
      icon: Layers,
      eyebrow: 'Semantic Precision',
      heading: 'Dense Passage Embeddings & Citations',
      description: 'High-dimensional semantic similarity indexing. Extracts grounded evidence passages directly from candidate PDF resumes with zero hallucination.',
      pills: ['MiniLM-L6-v2 Model', 'Sentence Transformers', 'Grounding Evidence', 'Cosine Similarity']
    },
    {
      id: 'rules',
      title: 'Mandatory Rule Engine',
      icon: ShieldCheck,
      eyebrow: 'Deterministic Safety',
      heading: 'Zero False Positive Safeguards',
      description: 'Strict mandatory constraint enforcement. Hard skill requirements, minimum experience cutoffs, and regulatory certifications override raw scores.',
      pills: ['Hard Skill Cutoff', 'Experience Boundary', 'Rejection Transparency', 'Constraint Auditing']
    },
    {
      id: 'matrix',
      title: 'Leaderboard & Comparison',
      icon: Award,
      eyebrow: 'Recruiter Cockpit',
      heading: 'Instant Candidate Benchmarking',
      description: 'Sorted compatibility leaderboards with top-3 podium highlights and side-by-side multi-candidate attribute matrices.',
      pills: ['Podium Highlights', 'Side-by-Side Matrix', 'Score Category Breakdown', 'Recruiter Briefing']
    }
  ]

  const currentShowcase = showcaseTabs[activeTab]

  return (
    <div className="space-y-8">
      {/* Apple Product Style Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl border border-slate-900/10 bg-gradient-to-r from-slate-900 via-slate-800 to-napkin-indigo p-8 sm:p-10 text-white shadow-2xl">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-3.5 py-1.5 text-xs font-semibold text-white backdrop-blur-md border border-white/15 mb-4">
            <Sparkles size={14} className="text-apple-blue animate-pulse" />
            <span>Apple Monolith Architecture · 5-Agent Pipeline</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black tracking-tight leading-tight">
            Recruitment Intelligence <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-white via-slate-200 to-apple-blue bg-clip-text text-transparent">
              Engineered with Precision
            </span>
          </h1>
          <p className="mt-3 text-sm text-slate-300 leading-relaxed font-normal">
            Automated resume parsing into 384-dim vector embeddings, passage evidence grounding, and multi-agent recruiter executive briefings.
          </p>

          <div className="mt-6 flex flex-wrap gap-3.5">
            <Link to="/resumes" className="btn-accent shadow-glow-purple">
              <UploadCloud size={18} /> Ingest Resumes
            </Link>
            <Link to="/ranking" className="btn-soft bg-white/10 text-white border-white/20 hover:bg-white/20">
              <BarChart3 size={18} /> View Leaderboard
            </Link>
          </div>
        </div>

        {/* Decorative Background Halo */}
        <div className="absolute -top-24 -right-24 h-96 w-96 rounded-full bg-apple-blue/20 blur-3xl pointer-events-none" />
      </div>

      {errors.map(error => (
        <ErrorBanner key={error} message={error} />
      ))}

      {/* Stat Card Grid */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {[
          ['Total Candidates', 'total_candidates', Users, 'blue'],
          ['Active Jobs', 'active_jobs', BriefcaseBusiness, 'purple'],
          ['Calculated Matches', 'total_matches', BarChart3, 'blue'],
          ['Strong Matches (>75%)', 'strong_matches', FileText, 'coral']
        ].map(([label, key, icon, tone]) => (
          <StatCard
            key={key}
            label={label}
            value={loading ? '...' : stats[key] ?? 0}
            icon={icon}
            tone={tone}
          />
        ))}
      </div>

      {/* Apple Keynote Interactive Feature Showcase Tabs */}
      <section className="panel p-8 shadow-apple-card space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/80 pb-4">
          <div>
            <span className="eyebrow">Apple Feature Keynote</span>
            <h3 className="text-xl font-black text-slate-900 tracking-tight">HireLens System Architecture</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {showcaseTabs.map((tab, idx) => {
              const Icon = tab.icon
              const isSelected = idx === activeTab
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(idx)}
                  className={`pill-badge border py-2 px-3.5 text-xs transition-all duration-200 ${
                    isSelected
                      ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                      : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <Icon size={14} className={isSelected ? 'text-apple-blue' : 'text-slate-400'} />
                  <span>{tab.title}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Selected Tab Content Showcase Display */}
        <div className="grid gap-6 lg:grid-cols-12 items-center animate-fade-in">
          <div className="lg:col-span-7 space-y-3">
            <span className="eyebrow text-apple-blue">{currentShowcase.eyebrow}</span>
            <h4 className="text-2xl font-black text-slate-900 tracking-tight">{currentShowcase.heading}</h4>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">{currentShowcase.description}</p>
            <div className="flex flex-wrap gap-2 pt-2">
              {currentShowcase.pills.map((pill, i) => (
                <span key={i} className="pill-badge bg-slate-100 text-slate-700 border border-slate-200/60 text-[11px]">
                  ✓ {pill}
                </span>
              ))}
            </div>
          </div>
          <div className="lg:col-span-5 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 p-6 text-white shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-700/80 pb-3 mb-3">
              <span className="text-xs font-bold text-slate-300 flex items-center gap-2">
                <Sparkles size={14} className="text-apple-blue animate-pulse" /> Live Feature Overview
              </span>
              <span className="pill-badge bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px]">
                Active Engine
              </span>
            </div>
            <div className="space-y-2 text-xs font-mono text-slate-300">
              <p>➜ Status: <span className="text-emerald-400">READY</span></p>
              <p>➜ Mode: <span className="text-apple-blue">MODULAR_MONOLITH</span></p>
              <p>➜ Pipeline: <span className="text-napkin-purple">5_LANGGRAPH_AGENTS</span></p>
              <p>➜ Embeddings: <span className="text-amber-400">384_DIM_DENSE</span></p>
            </div>
          </div>
        </div>
      </section>

      {/* Main Grid: Candidates Preview & Active Jobs */}
      <div className="grid gap-8 lg:grid-cols-12">
        {/* Candidates Column */}
        <section className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between px-1">
            <div>
              <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">Recent Candidates</h2>
              <p className="text-xs text-slate-500">Latest ingested profiles from database</p>
            </div>
            <Link to="/resumes" className="flex items-center gap-1 text-xs font-bold text-apple-blue hover:underline">
              View All <ArrowRight size={14} />
            </Link>
          </div>

          {loading ? (
            <div className="panel p-8 text-center text-slate-400">Loading candidate pool...</div>
          ) : candidates.length ? (
            <div className="grid gap-4 sm:grid-cols-2">
              {candidates.slice(0, 2).map(c => (
                <CandidateCard key={c.id || c.candidate_id} candidate={c} />
              ))}
            </div>
          ) : (
            <div className="panel p-8 text-center">
              <p className="text-sm font-medium text-slate-600">No candidates available in database.</p>
              <p className="text-xs text-slate-400 mt-1">Upload resumes to trigger ingestion.</p>
              <Link to="/resumes" className="btn-primary mt-4">
                Upload Resumes
              </Link>
            </div>
          )}
        </section>

        {/* Jobs Column */}
        <section className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between px-1">
            <div>
              <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">Active Job Profiles</h2>
              <p className="text-xs text-slate-500">Target roles for candidate matching</p>
            </div>
            <Link to="/jobs" className="flex items-center gap-1 text-xs font-bold text-apple-blue hover:underline">
              Browse All <ArrowRight size={14} />
            </Link>
          </div>

          <div className="space-y-3">
            {loading ? (
              <div className="panel p-8 text-center text-slate-400">Loading jobs...</div>
            ) : jobs.length ? (
              jobs.slice(0, 3).map(job => (
                <Link
                  key={job.id}
                  to={`/ranking?job_id=${encodeURIComponent(job.id)}`}
                  className="panel group flex items-center justify-between p-4 transition-all duration-200 hover:border-apple-blue/50 hover:shadow-md"
                >
                  <div className="flex items-center gap-3.5">
                    <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-100 text-slate-700 group-hover:bg-apple-blue/10 group-hover:text-apple-blue transition-colors">
                      <BriefcaseBusiness size={18} />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-slate-900 group-hover:text-apple-blue transition-colors">
                        {job.title}
                      </h4>
                      <p className="text-xs text-slate-500">{job.department} · Min {job.min_experience_months || 0} mos exp</p>
                    </div>
                  </div>
                  <ArrowRight size={16} className="text-slate-400 group-hover:text-apple-blue group-hover:translate-x-0.5 transition-all" />
                </Link>
              ))
            ) : (
              <div className="panel p-8 text-center">
                <p className="text-sm text-slate-600">No active job descriptions.</p>
                <Link to="/jobs/create" className="btn-soft mt-3">
                  Create First Job
                </Link>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  )
}
