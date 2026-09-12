import { ArrowUpRight, Briefcase, GraduationCap } from 'lucide-react'
import { Link } from 'react-router-dom'
import MatchScore from './MatchScore'
import SkillBadge from './SkillBadge'

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

  return (
    <div className="panel p-5 transition hover:-translate-y-0.5 hover:shadow-lg">
      <div className="flex items-start justify-between">
        <div className="flex gap-3">
          <div className={`grid h-11 w-11 place-items-center rounded-full text-xs font-extrabold ${candidate.avatar || 'bg-mint text-teal'}`}>
            {candidate.initials || 'CD'}
          </div>
          <div>
            <h3 className="font-bold">{candidate.name || 'Candidate'}</h3>
            <p className="mt-0.5 text-xs text-muted">{candidate.role || 'Software Engineer'}</p>
          </div>
        </div>
        <MatchScore score={candidate.score} />
      </div>

      <div className="my-5 grid grid-cols-2 gap-3 text-xs text-muted">
        <span className="flex items-center gap-2">
          <Briefcase size={14} />{candidate.experience || '0 yrs'} experience
        </span>
        <span className="flex items-center gap-2 truncate">
          <GraduationCap size={14} className="shrink-0" />{eduDisplay}
        </span>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {skillsList.slice(0, 4).map((skill, idx) => (
          <SkillBadge key={`${skill}_${idx}`}>{skill}</SkillBadge>
        ))}
      </div>

      <Link
        to={`/matches/${candidate.match_id || candidate.candidate_id || candidate.id}`}
        className="mt-5 flex items-center justify-between border-t pt-4 text-xs font-bold text-teal"
      >
        View full profile <ArrowUpRight size={15} />
      </Link>
    </div>
  )
}