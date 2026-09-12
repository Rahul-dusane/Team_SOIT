import { useEffect, useState } from 'react'
import { ArrowLeft, CheckCircle2, FileSearch, MessageSquareText, ShieldAlert, Play } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { Cell, Pie, PieChart, ResponsiveContainer } from 'recharts'
import EvidenceDrawer from '../components/EvidenceDrawer'
import AgentTimeline from '../components/AgentTimeline'
import MatchScore from '../components/MatchScore'
import ScoreBreakdown from '../components/ScoreBreakdown'
import SkillBadge from '../components/SkillBadge'
import ErrorBanner from '../components/ErrorBanner'
import { candidates as mockCandidates, scoreBreakdown as mockBreakdown } from '../data/mockData'
import { getMatchDetails, getCandidateById, runMatch, formatCandidateForUI } from '../services/api'

export default function MatchDetail() {
  const { id } = useParams()
  const [candidate, setCandidate] = useState(null)
  const [categoryBreakdown, setCategoryBreakdown] = useState(null)
  const [assessments, setAssessments] = useState([])
  const [drawer, setDrawer] = useState(false)
  const [loading, setLoading] = useState(true)
  const [runningMatch, setRunningMatch] = useState(false)
  const [errorMsg, setErrorMsg] = useState(null)
  const [hasMatchData, setHasMatchData] = useState(false)
  const [summaryData, setSummaryData] = useState({
    text: '',
    strengths: '',
    concerns: '',
    interview: ''
  })

  const loadMatchData = async () => {
    try {
      setLoading(true)
      setErrorMsg(null)

      // 1. Try fetching match record by match_id or candidate_id
      try {
        const matchData = await getMatchDetails(id)
        if (matchData && matchData.overall_score !== undefined) {
          const rawScore = Math.round(matchData.overall_score)

          // Fetch full candidate profile if available
          let baseCand = null
          if (matchData.candidate_id) {
            try {
              const cObj = await getCandidateById(matchData.candidate_id)
              if (cObj) baseCand = formatCandidateForUI(cObj)
            } catch (e) { /* ignore */ }
          }

          if (!baseCand) {
            baseCand = mockCandidates.find(item => item.id === Number(id) || String(item.id) === String(id) || item.candidate_id === matchData.candidate_id) || formatCandidateForUI({ candidate_id: matchData.candidate_id || id, name: `Candidate ${matchData.candidate_id || id}` })
          }

          setCandidate({
            ...baseCand,
            id: matchData.match_id || id,
            candidate_id: matchData.candidate_id || baseCand.candidate_id,
            job_id: matchData.job_id,
            score: rawScore,
            status: matchData.decision || matchData.overall_status || 'Strong'
          })

          setHasMatchData(true)

          if (matchData.raw_score_breakdown) {
            const bd = matchData.raw_score_breakdown
            setCategoryBreakdown([
              { name: 'Skills', score: Math.round(bd.must_have || bd.skills || 0) },
              { name: 'Experience', score: Math.round(bd.experience || 0) },
              { name: 'Education', score: Math.round(bd.education || 0) },
              { name: 'Projects', score: Math.round(bd.projects || 0) },
              { name: 'Domain', score: Math.round(bd.domain || 0) },
              { name: 'Semantic', score: Math.round(bd.semantic || 0) }
            ])
          }

          if (matchData.assessments) {
            setAssessments(matchData.assessments)
          }

          if (matchData.summary) {
            setSummaryData({
              text: matchData.summary.summary_text || '',
              strengths: (matchData.summary.key_strengths || []).join(', ') || 'Demonstrated core capabilities',
              concerns: (matchData.summary.key_gaps || []).join(', ') || 'None identified',
              interview: 'Probe technical depth and system design principles'
            })
          }
          return
        }
      } catch (matchErr) {
        // No match record found yet for this ID
      }

      // 2. Try fetching candidate profile by candidate_id
      try {
        const candData = await getCandidateById(id)
        if (candData) {
          const formatted = formatCandidateForUI(candData)
          setCandidate({
            ...formatted,
            score: null // No fake score!
          })
          setHasMatchData(false)
          setErrorMsg(`No match analysis record found for candidate '${id}'. Click 'Run Match Engine' below to compute real scores.`)
          return
        }
      } catch (candErr) {
        // Not in backend database
      }

      // 3. Fallback to mock data ONLY if matching mock ID (for initial demo state)
      const mockCand = mockCandidates.find(item => item.id === Number(id) || String(item.id) === String(id) || item.candidate_id === id)
      if (mockCand) {
        setCandidate(mockCand)
        setCategoryBreakdown(mockBreakdown)
        setHasMatchData(true)
        setSummaryData({
          text: mockCand.summary || 'A strong candidate with relevant experience.',
          strengths: 'Production Python, API architecture, ownership',
          concerns: 'Kubernetes exposure is limited',
          interview: 'Probe scale, incident response, cloud depth'
        })
        return
      }

      // 4. Record truly missing
      setCandidate(null)
      setErrorMsg(`No candidate or match record found for identifier '${id}'.`)

    } catch (err) {
      setCandidate(null)
      setErrorMsg(err.message || `Could not retrieve match details for '${id}'.`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (id) {
      loadMatchData()
    }
  }, [id])

  const handleRunMatch = async () => {
    if (!candidate) return
    const cid = candidate.candidate_id || id
    const jid = candidate.job_id || 'J01'
    setRunningMatch(true)
    setErrorMsg(null)
    try {
      await runMatch(cid, jid)
      await loadMatchData()
    } catch (err) {
      setErrorMsg(err.message || 'Failed to run candidate match engine.')
    } finally {
      setRunningMatch(false)
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl">
        <Link to="/ranking" className="mb-7 flex items-center gap-2 text-xs font-bold text-muted hover:text-ink">
          <ArrowLeft size={15} />Back to ranking
        </Link>
        <div className="panel p-12 text-center text-sm font-semibold text-muted">
          Loading match profile details...
        </div>
      </div>
    )
  }

  if (!candidate && errorMsg) {
    return (
      <div className="mx-auto max-w-7xl">
        <Link to="/ranking" className="mb-7 flex items-center gap-2 text-xs font-bold text-muted hover:text-ink">
          <ArrowLeft size={15} />Back to ranking
        </Link>
        <ErrorBanner message={errorMsg} onClose={() => setErrorMsg(null)} />
        <div className="panel p-12 text-center">
          <h2 className="text-xl font-extrabold text-ink">Match Profile Not Found</h2>
          <p className="mt-2 text-xs text-muted">No candidate record or match result exists for ID '{id}'.</p>
          <Link to="/ranking" className="btn-primary mt-6 inline-flex">
            Back to Ranking
          </Link>
        </div>
      </div>
    )
  }

  const pieScore = candidate?.score ?? 0
  const pieData = [
    { name: 'Match', value: pieScore },
    { name: 'Gap', value: Math.max(0, 100 - pieScore) }
  ]

  return (
    <div className="mx-auto max-w-7xl">
      <Link to="/ranking" className="mb-7 flex items-center gap-2 text-xs font-bold text-muted hover:text-ink">
        <ArrowLeft size={15} />Back to ranking
      </Link>

      {errorMsg && (
        <ErrorBanner
          message={errorMsg}
          type={!hasMatchData ? 'warning' : 'error'}
          onClose={() => setErrorMsg(null)}
        />
      )}

      {!hasMatchData && (
        <div className="mb-6 flex items-center justify-between rounded-xl border border-[#bae6fd] bg-[#f0f9ff] p-4 text-xs">
          <div>
            <p className="font-bold text-[#0369a1]">Match Analysis Pending</p>
            <p className="mt-1 text-[#0284c7]">Real-time match scoring has not been executed for candidate '{candidate.name}'.</p>
          </div>
          <button
            onClick={handleRunMatch}
            disabled={runningMatch}
            className="btn-primary shrink-0 py-2 text-xs"
          >
            <Play size={14} />{runningMatch ? 'Computing Score...' : 'Run Match Engine'}
          </button>
        </div>
      )}

      <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div className="flex items-center gap-4">
          <div className={`grid h-16 w-16 place-items-center rounded-2xl text-lg font-extrabold ${candidate.avatar || 'bg-mint text-teal'}`}>
            {candidate.initials}
          </div>
          <div>
            <p className="eyebrow mb-2">Match profile</p>
            <h1 className="text-3xl font-extrabold tracking-tight">{candidate.name}</h1>
            <p className="mt-1 text-sm text-muted">{candidate.role} · Senior Backend Engineer</p>
          </div>
        </div>
        <button className="btn-primary">
          <MessageSquareText size={16} />Add interview note
        </button>
      </div>

      <div className="grid gap-6 xl:grid-cols-[.8fr_1.2fr]">
        <section className="panel flex items-center justify-between p-6">
          <div>
            <p className="eyebrow mb-3">Overall match score</p>
            {candidate.score !== null ? (
              <MatchScore score={candidate.score} size="lg" />
            ) : (
              <div className="text-2xl font-extrabold text-muted">Uncalculated</div>
            )}
            <p className="mt-2 text-xs text-muted">
              {candidate.score === null
                ? 'Run match calculation to compute score'
                : candidate.score >= 85
                ? 'Strong fit for this role'
                : candidate.score >= 70
                ? 'Moderate fit for this role'
                : 'Requires detailed recruiter review'}
            </p>
          </div>
          <div className="h-36 w-36">
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  innerRadius={48}
                  outerRadius={62}
                  startAngle={90}
                  endAngle={-270}
                  strokeWidth={0}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={entry.name} fill={index === 0 && candidate.score !== null ? '#14866d' : '#edf1f1'} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="panel p-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <p className="eyebrow mb-2">Agent workflow</p>
              <h2 className="text-xl font-extrabold">How we reached this score</h2>
            </div>
            <span className="flex items-center gap-1 text-xs font-bold text-teal">
              <CheckCircle2 size={15} />{hasMatchData ? 'Complete' : 'Pending'}
            </span>
          </div>
          <AgentTimeline />
        </section>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <section className="panel p-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <p className="eyebrow mb-2">Score breakdown</p>
              <h2 className="text-xl font-extrabold">Role fit by category</h2>
            </div>
            <FileSearch className="text-muted" size={20} />
          </div>
          {categoryBreakdown ? (
            <ScoreBreakdown data={categoryBreakdown} />
          ) : (
            <div className="p-8 text-center text-xs text-muted">
              Run match engine to compute category breakdowns.
            </div>
          )}
        </section>

        <section className="panel p-6">
          <div className="mb-5">
            <p className="eyebrow mb-2">Skill analysis</p>
            <h2 className="text-xl font-extrabold">What they bring</h2>
          </div>
          <div className="space-y-5">
            <div>
              <p className="mb-2 text-xs font-bold text-muted">Matched skills</p>
              <div className="flex flex-wrap gap-2">
                {(candidate.skills || []).map(skill => (
                  <SkillBadge key={skill} onClick={() => setDrawer(true)}>
                    {skill}
                  </SkillBadge>
                ))}
              </div>
            </div>

            <div>
              <p className="mb-2 text-xs font-bold text-muted">Transferable skills</p>
              <div className="flex flex-wrap gap-2">
                <SkillBadge type="transferable">Azure → AWS</SkillBadge>
              </div>
            </div>

            <div>
              <p className="mb-2 text-xs font-bold text-muted">Missing skills</p>
              <div className="flex flex-wrap gap-2">
                {(candidate.gaps || []).length > 0 ? (
                  candidate.gaps.map(skill => (
                    <SkillBadge key={skill} type="missing">{skill}</SkillBadge>
                  ))
                ) : (
                  <span className="text-xs text-muted">No critical missing skills</span>
                )}
              </div>
            </div>
          </div>
        </section>
      </div>

      <section className="panel mt-6 grid gap-6 p-6 md:grid-cols-2">
        <div>
          <p className="eyebrow mb-2">Recruiter summary</p>
          <h2 className="text-xl font-extrabold">A considered recommendation</h2>
          <p className="mt-3 text-sm leading-7 text-muted">
            {summaryData.text || candidate.summary || 'Candidate profile loaded. Run match engine for detailed recruiter briefing.'}
          </p>
        </div>

        <div className="grid gap-3 sm:grid-cols-3 md:grid-cols-1">
          <div className="rounded-xl bg-mint/60 p-3">
            <p className="mb-1 flex items-center gap-2 text-xs font-bold text-teal">
              <CheckCircle2 size={14} />Strengths
            </p>
            <p className="text-xs leading-5 text-muted">{summaryData.strengths || 'Core technical capabilities'}</p>
          </div>

          <div className="rounded-xl bg-[#fff6d9] p-3">
            <p className="mb-1 flex items-center gap-2 text-xs font-bold text-[#a17612]">
              <ShieldAlert size={14} />Concerns
            </p>
            <p className="text-xs leading-5 text-muted">{summaryData.concerns || 'None identified'}</p>
          </div>

          <div className="rounded-xl bg-[#eef1f9] p-3">
            <p className="mb-1 text-xs font-bold text-[#5966a1]">Interview focus</p>
            <p className="text-xs leading-5 text-muted">{summaryData.interview || 'Probe system architecture depth'}</p>
          </div>
        </div>
      </section>

      <EvidenceDrawer open={drawer} onClose={() => setDrawer(false)} />
    </div>
  )
}