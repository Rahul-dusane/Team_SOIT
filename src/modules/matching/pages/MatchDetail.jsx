import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Play, Sparkles, CheckCircle2, FileText, Layers, Award } from 'lucide-react'
import AgentTimeline from '../components/AgentTimeline'
import MatchScore from '../components/MatchScore'
import ScoreBreakdown from '../components/ScoreBreakdown'
import EvidenceDrawer from '../../candidates/components/EvidenceDrawer'
import ErrorBanner from '../../../core/components/ErrorBanner'
import SkillBadge from '../../../core/components/SkillBadge'
import { getMatchDetails, getCandidateById, getJobs, runMatch, formatCandidateForUI } from '../../../core/api/api'

export default function MatchDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [candidate, setCandidate] = useState(null)
  const [match, setMatch] = useState(null)
  const [jobs, setJobs] = useState([])
  const [jobId, setJobId] = useState('')
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')
  const [evidence, setEvidence] = useState(null)

  useEffect(() => {
    let active = true
    setLoading(true); setCandidate(null); setMatch(null); setError(''); setEvidence(null); setJobs([]); setJobId('')
    async function load() {
      let result = null
      try { result = await getMatchDetails(id) } catch (e) { if (e.status !== 404) throw e }
      if (!active) return
      if (result && result.status !== 'no_match' && result.match_id) setMatch(result)
      const profile = await getCandidateById(result?.candidate_id || id)
      if (!active) return
      setCandidate(formatCandidateForUI(profile))
      const savedJobs = await getJobs()
      if (!active) return
      if (!Array.isArray(savedJobs)) throw new Error('Invalid jobs response.')
      setJobs(savedJobs); setJobId(result?.job_id || (savedJobs.length > 0 ? savedJobs[0].job_id : ''))
    }
    load().catch(e => { if (active) setError(e.message) }).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [id])

  async function calculate() {
    if (!candidate || !jobId) return
    setRunning(true); setError('')
    try {
      const result = await runMatch(candidate.candidate_id, jobId)
      if (!result?.match_id) throw new Error('Server did not return a saved match identifier.')
      const detail = await getMatchDetails(result.match_id)
      setMatch(detail)
      navigate(`/matches/${encodeURIComponent(result.match_id)}`)
    } catch (e) { setError(e.message) } finally { setRunning(false) }
  }

  const breakdown = Object.entries(match?.raw_score_breakdown || match?.score_breakdown || {})
    .filter(([, v]) => typeof v === 'number' && Number.isFinite(v))
    .map(([name, score]) => ({ name, score }))

  const summary = match?.summary

  return (
    <div className="space-y-8">
      {/* Top Navigation Back Action */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-bold text-slate-700 shadow-xs transition hover:border-slate-300 hover:bg-slate-50"
        >
          <ArrowLeft size={14} /> Back to Leaderboard
        </button>

        {match?.created_at && (
          <span className="text-xs text-slate-400 font-mono">
            Analyzed: {new Date(match.created_at).toLocaleString()}
          </span>
        )}
      </div>

      <ErrorBanner message={error} />

      {loading ? (
        <div className="panel p-12 text-center text-slate-400">Loading candidate analysis & match details...</div>
      ) : !candidate ? (
        <div className="panel p-12 text-center text-slate-500">Candidate profile data unavailable.</div>
      ) : (
        <>
          {/* Header Profile Hero Card */}
          <div className="panel p-8 shadow-panel">
            <div className="flex flex-wrap items-center justify-between gap-6">
              <div className="flex items-center gap-5">
                <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-gradient-to-tr from-slate-900 via-napkin-indigo to-apple-blue font-black text-xl text-white shadow-lg">
                  {candidate?.initials || candidate?.name?.substring(0, 2).toUpperCase() || 'CD'}
                </div>
                <div>
                  <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
                    {candidate?.name || 'Anonymous Candidate'}
                  </h1>
                  <p className="mt-1 text-sm font-semibold text-slate-500">
                    {candidate?.role || 'Role not provided'} · {candidate?.experience || 'No experience data'}
                  </p>
                  <p className="mt-0.5 text-xs text-slate-400">Education: {candidate?.education || 'Not provided'}</p>
                </div>
              </div>

              {/* Match Score Display */}
              <div className="rounded-2xl border border-slate-100 bg-slate-50/70 p-4 shadow-xs">
                <MatchScore score={match?.overall_score} decision={match?.decision || match?.overall_status} size="lg" />
              </div>
            </div>

            {/* Run Match Action Panel */}
            {!match && (
              <div className="mt-6 rounded-2xl border border-apple-blue/20 bg-apple-blue/5 p-5">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <h4 className="text-sm font-extrabold text-slate-900">Calculate Compatibility Match</h4>
                    <p className="text-xs text-slate-500">Select a job description and launch the 5-agent engine.</p>
                  </div>
                  <div className="flex flex-wrap items-center gap-3">
                    <select
                      aria-label="Job to match"
                      value={jobId}
                      onChange={e => setJobId(e.target.value)}
                      className="rounded-2xl border border-slate-300 bg-white px-4 py-2.5 text-xs font-semibold text-slate-800 shadow-xs focus:border-apple-blue focus:outline-none"
                    >
                      <option value="">Select a saved job</option>
                      {jobs && Array.isArray(jobs)
                        ? jobs.map(j => (
                            <option value={j?.job_id || ''} key={j?.job_id || ''}>
                              {j?.title || 'Unknown Job'}
                            </option>
                          ))
                        : null}
                    </select>
                    <button
                      className="btn-accent"
                      disabled={!jobId || running}
                      onClick={calculate}
                    >
                      {running ? (
                        <>Computing Match...</>
                      ) : (
                        <>
                          <Play size={16} /> Run Match Engine
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Agent Workflow Timeline Visualizer */}
          <div className="panel p-6">
            <h3 className="text-base font-extrabold text-slate-900 tracking-tight mb-4 flex items-center gap-2">
              <Sparkles size={18} className="text-napkin-purple" />
              Recorded LangGraph Multi-Agent Workflow
            </h3>
            <AgentTimeline logs={match?.agent_logs} />
          </div>

          {/* Main 2-Column Analytics Grid */}
          <div className="grid gap-8 lg:grid-cols-12">
            {/* Left Column: Score Breakdown & Executive Briefing */}
            <div className="lg:col-span-6 space-y-8">
              {/* Category Score Breakdown */}
              <section className="panel p-6">
                <h3 className="text-base font-extrabold text-slate-900 tracking-tight mb-4 flex items-center gap-2">
                  <Layers size={18} className="text-apple-blue" />
                  Category Score Breakdown
                </h3>
                <ScoreBreakdown data={breakdown} />
              </section>

              {/* Recruiter Executive Summary */}
              <section className="panel p-6">
                <h3 className="text-base font-extrabold text-slate-900 tracking-tight mb-4 flex items-center gap-2">
                  <Award size={18} className="text-napkin-indigo" />
                  Recruiter Executive Briefing
                </h3>
                <div className="space-y-4 text-xs text-slate-700 leading-relaxed">
                  <div className="rounded-2xl border border-slate-100 bg-slate-50 p-4">
                    <p className="font-medium">{summary?.summary_text || 'No recruiter summary generated yet. Run the match engine.'}</p>
                  </div>

                  {summary?.key_strengths && Array.isArray(summary.key_strengths) && summary.key_strengths.length > 0 && (
                    <div>
                      <span className="eyebrow text-emerald-600 block mb-1">Key Strengths</span>
                      <div className="flex flex-wrap gap-1.5">
                        {summary.key_strengths.map((s, idx) => (
                          <span key={idx} className="pill-badge bg-emerald-500/10 text-emerald-700 border border-emerald-500/20">
                            ✓ {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {summary?.key_gaps && Array.isArray(summary.key_gaps) && summary.key_gaps.length > 0 && (
                    <div>
                      <span className="eyebrow text-rose-600 block mb-1">Critical Skill Gaps</span>
                      <div className="flex flex-wrap gap-1.5">
                        {summary.key_gaps.map((g, idx) => (
                          <span key={idx} className="pill-badge bg-rose-500/10 text-rose-700 border border-rose-500/20">
                            ⚠ {g}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {summary?.recommendation && (
                    <div className="pt-2 border-t border-slate-100">
                      <span className="eyebrow block mb-1">Recruiter Recommendation</span>
                      <p className="font-bold text-slate-900">{summary.recommendation}</p>
                    </div>
                  )}
                </div>
              </section>
            </div>

            {/* Right Column: Requirement Assessments & Passages */}
            <div className="lg:col-span-6 space-y-8">
              <section className="panel p-6">
                <h3 className="text-base font-extrabold text-slate-900 tracking-tight mb-4 flex items-center gap-2">
                  <CheckCircle2 size={18} className="text-emerald-500" />
                  Requirement Assessments & Passages
                </h3>

                <div className="mb-4">
                  <p className="eyebrow mb-2">Recorded Profile Skills</p>
                  <div className="flex flex-wrap gap-1.5">
                    {candidate?.skills && Array.isArray(candidate.skills) && candidate.skills.length > 0 ? (
                      candidate.skills.map((sk, idx) => <SkillBadge key={idx}>{sk}</SkillBadge>)
                    ) : (
                      <span className="text-xs text-slate-400">No skills parsed</span>
                    )}
                  </div>
                </div>

                <p className="eyebrow mb-2">Evidence-Backed Requirements</p>
                {match?.assessments && Array.isArray(match.assessments) && match.assessments.length ? (
                  <div className="space-y-3">
                    {match.assessments.map((a, i) => {
                      const isSatisfied = a?.status === 'satisfied' || a?.status === 'partially_supported'
                      return (
                        <div
                          key={a?.requirement_id || i}
                          className="rounded-2xl border border-slate-100 bg-slate-50/70 p-3.5 text-xs transition-all hover:bg-white"
                        >
                          <div className="flex items-start justify-between gap-2">
                            <p className="font-bold text-slate-900">{a?.description || a?.requirement_id || 'Requirement'}</p>
                            <span
                              className={`pill-badge shrink-0 ${
                                isSatisfied
                                  ? 'bg-emerald-500/10 text-emerald-600 border border-emerald-500/20'
                                  : 'bg-rose-500/10 text-rose-600 border border-rose-500/20'
                              }`}
                            >
                              {a?.status ? a.status.replace('_', ' ') : 'Unsatisfied'}
                            </span>
                          </div>
                          {a?.earned_score != null && (
                            <p className="mt-2 text-slate-500 font-mono text-[11px]">
                              Earned Contribution: {a.earned_score} {a?.max_score != null ? `/ ${a.max_score} pts` : ''}
                            </p>
                          )}
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400">No requirement assessments recorded for this match.</p>
                )}
              </section>

              {/* Evidence Grounding Passages */}
              {(Array.isArray(match?.evidence_items) && match.evidence_items.length > 0) ||
              (Array.isArray(match?.uncertainty_flags) && match.uncertainty_flags.length > 0) ? (
                <section className="panel p-6">
                  <h3 className="text-base font-extrabold text-slate-900 tracking-tight mb-4 flex items-center gap-2">
                    <FileText size={18} className="text-apple-blue" />
                    Grounding Evidence Citations
                  </h3>

                  {Array.isArray(match?.evidence_items) && match.evidence_items.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {match.evidence_items.map((item, i) => (
                        <button
                          className="btn-soft text-xs py-2 px-3"
                          key={i}
                          onClick={() => setEvidence(item)}
                        >
                          Inspect Passage Citation #{i + 1}
                        </button>
                      ))}
                    </div>
                  )}

                  {Array.isArray(match?.uncertainty_flags) && match.uncertainty_flags.length > 0 && (
                    <div className="mt-4 rounded-2xl bg-amber-500/10 p-3.5 border border-amber-500/20">
                      <span className="eyebrow text-amber-700 block mb-1">Uncertainty Flags</span>
                      <ul className="space-y-1 text-xs text-amber-800 font-medium">
                        {match.uncertainty_flags.map((flag, i) => (
                          <li key={i}>• {flag}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </section>
              ) : null}
            </div>
          </div>
        </>
      )}

      <EvidenceDrawer open={!!evidence} evidence={evidence} onClose={() => setEvidence(null)} />
    </div>
  )
}
