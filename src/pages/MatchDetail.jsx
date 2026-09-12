import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import AgentTimeline from '../components/AgentTimeline'
import MatchScore from '../components/MatchScore'
import ScoreBreakdown from '../components/ScoreBreakdown'
import EvidenceDrawer from '../components/EvidenceDrawer'
import ErrorBanner from '../components/ErrorBanner'
import { getMatchDetails, getCandidateById, getJobs, runMatch, formatCandidateForUI } from '../services/api'

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
      if (result) setMatch(result)
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
  const breakdown = Object.entries(match?.raw_score_breakdown || match?.score_breakdown || {}).filter(([,v]) => typeof v === 'number' && Number.isFinite(v)).map(([name, score]) => ({ name, score }))
  const summary = match?.summary
  const job = jobs.find(j => j.job_id === match?.job_id)
  return <div className="mx-auto max-w-7xl"><Link className="mb-6 block text-teal" to="/ranking">← Back to ranking</Link><ErrorBanner message={error} />
    {loading ? <p className="panel p-8">Loading profile and match…</p> : !candidate ? <p className="panel p-8">Profile data unavailable.</p> : <>
      <h1 className="text-3xl font-extrabold">{candidate.name}</h1><p className="my-3 text-muted">{candidate.role} · {candidate.experience}</p><p className="mb-6 text-sm">Education: {candidate.education}</p>
      <section className="panel mb-6 p-6"><h2 className="text-xl font-bold">Overall match score</h2><p className="my-3">{match ? `Job: ${job?.title || match.job_id}` : 'No saved match analysis available.'}</p><MatchScore score={match?.overall_score} size="lg" />{match && <p className="mt-3">Reported decision: {match.decision || match.overall_status || 'Unavailable'}</p>}
      {!match && <div className="mt-5 flex flex-wrap gap-3"><select aria-label="Job to match" value={jobId} onChange={e => setJobId(e.target.value)} className="rounded-lg border p-3"><option value="">Select a saved job</option>{jobs.map(j => <option value={j.job_id} key={j.job_id}>{j.title}</option>)}</select><button className="btn-primary" disabled={!jobId || running} onClick={calculate}>{running ? 'Computing…' : 'Run Match Engine'}</button></div>}</section>
      <section className="panel mb-6 p-6"><h2 className="mb-4 text-xl font-bold">Recorded agent workflow</h2><AgentTimeline logs={match?.agent_logs} /></section>
      <div className="grid gap-6 lg:grid-cols-2"><section className="panel p-6"><h2 className="mb-4 text-xl font-bold">Score breakdown</h2><ScoreBreakdown data={breakdown} /></section><section className="panel p-6"><h2 className="mb-4 text-xl font-bold">Skills recorded in profile</h2><p className="text-sm">{candidate.skills.join(', ') || 'No skills recorded.'}</p><h3 className="my-4 font-bold">Requirement assessments</h3>{match?.assessments?.length ? match.assessments.map((a,i) => <div key={a.requirement_id || i} className="border-b py-3 text-sm"><p>{a.description || a.requirement_id}</p><p>Status: {a.status ? a.status.replace('_', ' ') : 'Not satisfied'}</p>{a.earned_score != null && <p>Earned score: {a.earned_score}{a.max_score != null ? ` / ${a.max_score}` : ''}</p>}</div>) : <p className="text-sm text-muted">No requirement assessments available.</p>}</section></div>
      <section className="panel mt-6 p-6"><h2 className="mb-4 text-xl font-bold">Recruiter summary</h2><p>{summary?.summary_text || 'No recruiter summary available.'}</p><p className="mt-4">Strengths: {summary?.key_strengths?.join(', ') || 'Not provided'}</p><p className="mt-2">Gaps: {summary?.key_gaps?.join(', ') || 'Not provided'}</p><p className="mt-2">Recommendation: {summary?.recommendation || 'Not provided'}</p></section>
      <section className="panel mt-6 p-6"><h2 className="mb-4 text-xl font-bold">Evidence and uncertainty</h2>{match?.evidence_items?.length ? match.evidence_items.map((item,i) => <button className="btn-soft mr-3" key={i} onClick={() => setEvidence(item)}>View evidence {i+1}</button>) : <p>No evidence passages provided by the server.</p>}{match?.uncertainty_flags?.length > 0 && <ul className="mt-4 list-inside list-disc">{match.uncertainty_flags.map((flag,i) => <li key={i}>{flag}</li>)}</ul>}</section>
    </>}<EvidenceDrawer open={!!evidence} evidence={evidence} onClose={() => setEvidence(null)} />
  </div>
}
