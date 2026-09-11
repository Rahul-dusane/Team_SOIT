import { useEffect, useState } from 'react'
import { ArrowLeft, CheckCircle2, FileSearch, MessageSquareText, ShieldAlert } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { Cell, Pie, PieChart, ResponsiveContainer } from 'recharts'
import EvidenceDrawer from '../components/EvidenceDrawer'
import AgentTimeline from '../components/AgentTimeline'
import MatchScore from '../components/MatchScore'
import ScoreBreakdown from '../components/ScoreBreakdown'
import SkillBadge from '../components/SkillBadge'
import ErrorBanner from '../components/ErrorBanner'
import { candidates as mockCandidates, scoreBreakdown as mockBreakdown } from '../data/mockData'
import { getMatchDetails, getCandidateById, formatCandidateForUI } from '../services/api'

export default function MatchDetail() {
  const { id } = useParams()
  const [candidate, setCandidate] = useState(mockCandidates[0])
  const [categoryBreakdown, setCategoryBreakdown] = useState(mockBreakdown)
  const [drawer, setDrawer] = useState(false)
  const [loading, setLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState(null)
  const [summaryData, setSummaryData] = useState({
    text: '',
    strengths: 'Production Python, API architecture, ownership',
    concerns: 'Kubernetes exposure is limited',
    interview: 'Probe scale, incident response, cloud depth'
  })

  useEffect(() => {
    async function loadMatchData() {
      try {
        setLoading(true)
        // Try match details first
        try {
          const matchData = await getMatchDetails(id)
          if (matchData && matchData.overall_score !== undefined) {
            const rawScore = Math.round(matchData.overall_score)
            setCandidate(old => ({
              ...old,
              id: matchData.match_id || id,
              candidate_id: matchData.candidate_id,
              score: rawScore,
              status: matchData.decision || matchData.overall_status || 'Strong'
            }))

            if (matchData.raw_score_breakdown) {
              const bd = matchData.raw_score_breakdown
              setCategoryBreakdown([
                { name: 'Skills', score: Math.round(bd.must_have || bd.skills || 90) },
                { name: 'Experience', score: Math.round(bd.experience || 85) },
                { name: 'Education', score: Math.round(bd.education || 80) },
                { name: 'Projects', score: Math.round(bd.projects || 88) },
                { name: 'Domain', score: Math.round(bd.domain || 85) },
                { name: 'Semantic', score: Math.round(bd.semantic || 90) }
              ])
            }

            if (matchData.summary) {
              setSummaryData({
                text: matchData.summary.summary_text || '',
                strengths: (matchData.summary.key_strengths || []).join(', ') || 'Solid core skills',
                concerns: (matchData.summary.key_gaps || []).join(', ') || 'Minor skill gaps',
                interview: 'Focus on production architecture depth'
              })
            }
            return
          }
        } catch (matchErr) {
          // fallback to candidate by ID lookup
        }

        const candData = await getCandidateById(id)
        if (candData) {
          const formatted = formatCandidateForUI(candData)
          setCandidate(formatted)
        } else {
          const fallbackCand = mockCandidates.find(item => item.id === Number(id) || String(item.id) === String(id)) || mockCandidates[0]
          setCandidate(fallbackCand)
        }

      } catch (err) {
        const fallbackCand = mockCandidates.find(item => item.id === Number(id) || String(item.id) === String(id)) || mockCandidates[0]
        setCandidate(fallbackCand)
        setErrorMsg(err.message || 'Match profile not found on server. Displaying demo profile.')
      } finally {
        setLoading(false)
      }
    }

    if (id) {
      loadMatchData()
    }
  }, [id])

  const pieData = [
    { name: 'Match', value: candidate.score || 85 },
    { name: 'Gap', value: 100 - (candidate.score || 85) }
  ]

  return (
    <div className="mx-auto max-w-7xl">
      <Link to="/ranking" className="mb-7 flex items-center gap-2 text-xs font-bold text-muted hover:text-ink">
        <ArrowLeft size={15} />Back to ranking
      </Link>

      {errorMsg && (
        <ErrorBanner message={errorMsg} onClose={() => setErrorMsg(null)} />
      )}

      {loading ? (
        <div className="panel p-12 text-center text-sm font-semibold text-muted">
          Loading match profile details...
        </div>
      ) : (
        <>
          <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
            <div className="flex items-center gap-4">
              <div className={`grid h-16 w-16 place-items-center rounded-2xl text-lg font-extrabold ${candidate.avatar}`}>
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
                <MatchScore score={candidate.score} size="lg" />
                <p className="mt-2 text-xs text-muted">
                  {candidate.score >= 85 ? 'Strong fit for this role' : candidate.score >= 70 ? 'Moderate fit for this role' : 'Requires detailed review'}
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
                        <Cell key={entry.name} fill={index === 0 ? '#14866d' : '#edf1f1'} />
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
                  <CheckCircle2 size={15} />Complete
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
              <ScoreBreakdown data={categoryBreakdown} />
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
                {summaryData.text || candidate.summary || 'A strong candidate with relevant experience and a clear track record of delivery.'}
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-3 md:grid-cols-1">
              <div className="rounded-xl bg-mint/60 p-3">
                <p className="mb-1 flex items-center gap-2 text-xs font-bold text-teal">
                  <CheckCircle2 size={14} />Strengths
                </p>
                <p className="text-xs leading-5 text-muted">{summaryData.strengths}</p>
              </div>

              <div className="rounded-xl bg-[#fff6d9] p-3">
                <p className="mb-1 flex items-center gap-2 text-xs font-bold text-[#a17612]">
                  <ShieldAlert size={14} />Concerns
                </p>
                <p className="text-xs leading-5 text-muted">{summaryData.concerns}</p>
              </div>

              <div className="rounded-xl bg-[#eef1f9] p-3">
                <p className="mb-1 text-xs font-bold text-[#5966a1]">Interview focus</p>
                <p className="text-xs leading-5 text-muted">{summaryData.interview}</p>
              </div>
            </div>
          </section>

          <EvidenceDrawer open={drawer} onClose={() => setDrawer(false)} />
        </>
      )}
    </div>
  )
}