export function formatCandidateForUI(candidate, index = 0) {
  if (!candidate) return null

  const id = candidate.candidate_id || candidate.id || `CAND_${index}`
  const name = candidate.name || 'Anonymous Candidate'
  const role = candidate.role || (candidate.experiences?.[0]?.role) || 'Software Engineer'
  const expMonths = candidate.total_experience_months ?? 0
  const expYears = (expMonths / 12).toFixed(1)
  const experienceStr = `${expYears} yrs (${expMonths} mos)`

  let educationStr = 'Not provided'
  if (Array.isArray(candidate.education) && candidate.education.length > 0) {
    const first = candidate.education[0]
    educationStr = typeof first === 'string' ? first : `${first.degree || ''} ${first.field || ''}`.trim() || first.institution || 'Degree recorded'
  } else if (typeof candidate.education === 'string') {
    educationStr = candidate.education
  }

  const rawSkills = Array.isArray(candidate.skills)
    ? candidate.skills.map(s => (typeof s === 'string' ? s : s.raw_skill || s.normalized_skill || s.name)).filter(Boolean)
    : []

  const initials = name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()

  return {
    ...candidate,
    id,
    candidate_id: id,
    name,
    role,
    experience: experienceStr,
    education: educationStr,
    skills: rawSkills,
    initials,
    score: candidate.overall_score ?? candidate.score ?? null
  }
}

export function formatJobForUI(job) {
  if (!job) return null
  const id = job.job_id || job.id
  const title = job.title || 'Untitled Role'
  const department = job.department || 'Engineering'
  const minExp = job.min_experience_months || 0
  const mustHave = Array.isArray(job.must_have_skills) ? job.must_have_skills : []
  const preferred = Array.isArray(job.preferred_skills) ? job.preferred_skills : []

  return {
    ...job,
    id,
    job_id: id,
    title,
    department,
    status: job.status || 'Active',
    skills: [...mustHave, ...preferred],
    min_experience_months: minExp,
    applicants: job.applicants ?? null
  }
}

export function uploadOutcome(resultItem) {
  if (!resultItem) return { status: 'Parsed' }
  if (resultItem.status === 'duplicate') {
    return { status: 'Already stored', candidate_id: resultItem.candidate_id }
  }
  if (resultItem.status === 'success') {
    return { status: 'Parsed', candidate_id: resultItem.candidate_id }
  }
  return { status: 'Failed', error: resultItem.message || 'Processing error' }
}

export function mergeRankings(rankingPayload, candidatesList = []) {
  const rankedItems = (rankingPayload && Array.isArray(rankingPayload.rankings)) ? rankingPayload.rankings : []
  const rankedCandidateIds = new Set(rankedItems.map(r => r.candidate_id))

  const rankedList = rankedItems.map(rankItem => {
    const matchedCandidate = (candidatesList || []).find(c => (c.candidate_id || c.id) === rankItem.candidate_id)
    const formatted = formatCandidateForUI(matchedCandidate || { candidate_id: rankItem.candidate_id })

    return {
      ...formatted,
      rank: rankItem.rank,
      match_id: rankItem.match_id,
      score: rankItem.overall_score,
      status: rankItem.overall_status,
      decision: rankItem.decision || rankItem.overall_status
    }
  })

  const unrankedList = (candidatesList || [])
    .filter(c => !rankedCandidateIds.has(c.candidate_id || c.id))
    .map(c => {
      const formatted = formatCandidateForUI(c)
      return {
        ...formatted,
        rank: '-',
        match_id: null,
        score: null,
        status: 'Not Scored Yet',
        decision: 'Not Scored Yet'
      }
    })

  return [...rankedList, ...unrankedList]
}
