import { ArrowUpRight, Briefcase, GraduationCap } from 'lucide-react'
import { Link } from 'react-router-dom'
import MatchScore from '../../matching/components/MatchScore'
import SkillBadge from '../../../core/components/SkillBadge'

export default function CandidateCard({ candidate }) {
  if (!candidate) return null

  let eduDisplay = 'N/A'
  if (typeof candidate.education === 'string' && candidate.education.trim()) {
    eduDisplay = candidate.education.split(',')[0].trim()
  } else if (Array.isArray(candidate.education) && candidate.education.length > 0) {
    const firstEdu = candidate.education[0]
    if (typeof firstEdu === 'string') {
      eduDisplay = firstEdu.split(',')[0].trim()
    } else if (firstEdu && typeof firstEdu === 'object') {
      eduDisplay = firstEdu.degree || firstEdu.institution || 'N/A'
    }
  } else if (candidate.education && typeof candidate.education === 'object') {
    eduDisplay = candidate.education.degree || candidate.education.institution || 'N/A'
  }

  const skillsList = Array.isArray(candidate.skills)
    ? candidate.skills.map(s => typeof s === 'string' ? s : (s.raw_skill || s.name || s.normalized_skill || ''))
    : []

  const targetId = candidate.match_id || candidate.candidate_id || candidate.id

  return (
    <div className="panel group p-6 shadow-apple-card transition-all duration-300 hover:-translate-y-1 hover:shadow-panel">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3.5">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-slate-900 via-napkin-indigo to-apple-blue font-black text-sm text-white shadow-md transition-transform duration-300 group-hover:scale-105">
            {candidate.initials || candidate.name?.substring(0, 2).toUpperCase() || 'CD'}
          </div>
          <div>
            <h3 className="font-extrabold text-slate-900 tracking-tight group-hover:text-apple-blue transition-colors">
              {candidate.name || 'Anonymous Candidate'}
            </h3>
            <p className="mt-0.5 text-xs font-semibold text-slate-500">{candidate.role || 'Role not specified'}</p>
          </div>
        </div>
        <MatchScore score={candidate.score} decision={candidate.decision} />
      </div>

      <div className="my-5 grid grid-cols-2 gap-3 text-xs text-slate-500 font-medium">
        <span className="flex items-center gap-2 rounded-xl bg-slate-50 p-2.5 border border-slate-100">
          <Briefcase size={14} className="text-apple-blue shrink-0" />
          <span className="truncate">{candidate.experience || 'Experience N/A'}</span>
        </span>
        <span className="flex items-center gap-2 rounded-xl bg-slate-50 p-2.5 border border-slate-100 truncate">
          <GraduationCap size={14} className="text-napkin-purple shrink-0" />
          <span className="truncate">{eduDisplay}</span>
        </span>
      </div>

      <div className="flex flex-wrap gap-1.5 min-h-[32px]">
        {skillsList.slice(0, 4).map((skill, idx) => (
          <SkillBadge key={`${skill}_${idx}`}>{skill}</SkillBadge>
        ))}
        {skillsList.length > 4 && (
          <span className="pill-badge bg-slate-100 text-slate-500">
            +{skillsList.length - 4} more
          </span>
        )}
      </div>

      <Link
        to={`/matches/${targetId}`}
        className="mt-5 flex items-center justify-between border-t border-slate-100 pt-4 text-xs font-bold text-slate-900 group-hover:text-apple-blue transition-colors"
      >
        <span>View Full Analysis</span>
        <ArrowUpRight size={16} className="transition-transform duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
      </Link>
    </div>
  )
}
