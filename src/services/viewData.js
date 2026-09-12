export const numberOrNull = value => typeof value === 'number' && Number.isFinite(value) ? value : null
export const textOr = (value, fallback = 'Not provided') => typeof value === 'string' && value.trim() ? value : fallback
export const skillNames = value => Array.isArray(value) ? value.map(s => typeof s === 'string' ? s : s?.raw_skill || s?.name || s?.normalized_skill).filter(s => typeof s === 'string' && s.trim()) : []

export function getInitials(name) {
  const parts = textOr(name, '?').trim().split(/\s+/)
  return (parts[0][0] + (parts.length > 1 ? parts.at(-1)[0] : '')).toUpperCase()
}

export function formatCandidateForUI(cand) {
  if (!cand) return null
  const first = Array.isArray(cand.education) ? cand.education[0] : cand.education
  const education = typeof first === 'string' ? first : [first?.degree, first?.field, first?.institution].filter(Boolean).join(', ')
  const score = numberOrNull(cand.overall_score ?? cand.score)
  const months = numberOrNull(cand.total_experience_months)
  return {
    ...cand,
    id: cand.candidate_id ?? cand.id,
    candidate_id: cand.candidate_id ?? cand.id,
    name: textOr(cand.name, 'Name not provided'),
    initials: getInitials(cand.name),
    role: textOr(cand.experiences?.[0]?.role ?? cand.role, 'Role not provided'),
    experience: months === null ? textOr(cand.experience) : `${months} months`,
    education: textOr(education),
    skills: skillNames(cand.skills),
    projects: Array.isArray(cand.projects) ? cand.projects.length : numberOrNull(cand.projects),
    certifications: Array.isArray(cand.certifications) ? cand.certifications.length : numberOrNull(cand.certifications),
    score,
    status: textOr(cand.decision ?? cand.status, score === null ? 'Not scored' : 'Not provided'),
    avatar: 'bg-mint text-teal',
    summary: textOr(cand.summary_text ?? cand.summary, ''),
  }
}

export function formatJobForUI(job) {
  return { ...job, id: job.job_id, title: textOr(job.title), department: textOr(job.department ?? job.domain?.[0]),
    applicants: numberOrNull(job.applicants), updated: textOr(job.updated), status: textOr(job.status),
    skills: skillNames(job.must_have_skills ?? job.skills) }
}

export function mergeRankings(data, candidates) {
  if (!Array.isArray(data?.rankings)) throw new Error('Invalid ranking response.')
  return data.rankings.map(row => formatCandidateForUI({
    ...candidates.find(c => (c.candidate_id ?? c.id) === row.candidate_id),
    ...row, job_id: data.job_id, overall_score: numberOrNull(row.overall_score), score: null,
  }))
}

export function uploadOutcome(result) {
  if (result?.status === 'success') return { status: 'Parsed' }
  if (result?.status === 'duplicate') return { status: 'Already stored' }
  return { status: 'Failed', error: textOr(result?.error, 'The server did not confirm successful processing.') }
}
