import axios from 'axios'

const AVATAR_STYLES = [
  'bg-[#d9efe4] text-[#16856c]',
  'bg-[#fce4dc] text-[#c45f45]',
  'bg-[#e4e7f8] text-[#5c63ae]',
  'bg-[#f9edc9] text-[#aa7a12]',
  'bg-[#dceef4] text-[#347b91]',
  'bg-[#eedff1] text-[#945da1]',
  'bg-[#e5ecec] text-[#537475]',
  'bg-[#f8e1e2] text-[#b35e68]',
  'bg-[#e2e9f5] text-[#5574a9]',
  'bg-[#e9ecd6] text-[#798343]'
]

export function getInitials(name) {
  if (!name) return 'CD'
  const parts = name.trim().split(/\s+/)
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
  }
  return name.slice(0, 2).toUpperCase()
}

export function formatCandidateForUI(cand, index = 0) {
  if (!cand) return null

  const id = cand.candidate_id || cand.id || `cand_${index + 1}`
  const name = cand.name || 'Anonymous Candidate'
  const initials = getInitials(name)
  const role = cand.experiences?.[0]?.role || cand.role || 'Software Engineer'
  const expMonths = cand.total_experience_months || 0
  const expYears = expMonths > 0 ? Math.round(expMonths / 12) : 0
  const experience = expYears > 0 ? `${expYears} yrs` : (cand.experience || '0 yrs')
  
  const eduFirst = Array.isArray(cand.education) && cand.education.length > 0 ? cand.education[0] : null
  const education = typeof eduFirst === 'string' 
    ? eduFirst 
    : (eduFirst?.degree ? `${eduFirst.degree}${eduFirst.field ? ', ' + eduFirst.field : ''}` : (cand.education || 'N/A'))

  const skills = (cand.skills || []).map(s => typeof s === 'string' ? s : (s.raw_skill || s.name || s.normalized_skill || ''))
  const projects = Array.isArray(cand.projects) ? cand.projects.length : (cand.projects || 0)
  const certifications = Array.isArray(cand.certifications) ? cand.certifications.length : (cand.certifications || 0)
  const score = Math.round(cand.overall_score || cand.score || 75)
  const status = cand.status || (score >= 85 ? 'Strong' : score >= 70 ? 'Moderate' : 'Review')
  const gaps = cand.gaps || cand.skill_gaps?.critical || []
  const avatar = cand.avatar || AVATAR_STYLES[index % AVATAR_STYLES.length]
  const summary = cand.summary || cand.summary_text || 'Candidate profile extracted by HireLens.'

  return {
    ...cand,
    id,
    candidate_id: cand.candidate_id || String(id),
    name,
    initials,
    role,
    experience,
    education,
    skills,
    projects,
    certifications,
    score,
    status,
    gaps,
    avatar,
    summary
  }
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    let errorMessage = 'An unexpected error occurred.'
    let statusCode = error.response ? error.response.status : 0
    let isOffline = !error.response

    if (isOffline) {
      errorMessage = 'Backend server is unreachable. Operating in demo mode.'
    } else if (error.response.data && error.response.data.detail) {
      errorMessage = typeof error.response.data.detail === 'string'
        ? error.response.data.detail
        : JSON.stringify(error.response.data.detail)
    } else if (statusCode === 400) {
      errorMessage = 'Invalid request parameters or file upload format.'
    } else if (statusCode === 401) {
      errorMessage = 'Unauthorized: Invalid or missing API key.'
    } else if (statusCode === 404) {
      errorMessage = 'Requested resource not found on server.'
    } else if (statusCode === 422) {
      errorMessage = 'Validation error: Please check required input fields.'
    } else if (statusCode >= 500) {
      errorMessage = 'Internal server error. Please try again later.'
    }

    return Promise.reject({
      status: statusCode,
      message: errorMessage,
      isOffline,
      originalError: error,
    })
  }
)

export const getDashboardStats = () => api.get('/stats').then(res => res.data)

export const uploadResumes = (files, onUploadProgress) => {
  const formData = new FormData()
  const fileArray = Array.from(files)
  fileArray.forEach(file => {
    formData.append('files', file)
  })
  return api.post('/resumes/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress
  }).then(res => res.data)
}

export const getCandidates = () => api.get('/candidates').then(res => res.data)

export const getCandidateById = (id) => api.get(`/candidates/${id}`).then(res => res.data)

export const getJobs = () => api.get('/jobs').then(res => res.data)

export const createJob = (jobData) => api.post('/jobs', jobData).then(res => res.data)

export const getRanking = (jobId) => {
  const url = jobId ? `/ranking/${jobId}` : '/ranking'
  return api.get(url).then(res => res.data)
}

export const getMatchDetails = (id) => api.get(`/matches/${id}`).then(res => res.data)

export const runMatch = (candidateId, jobId) => api.post('/matches/run', { candidate_id: candidateId, job_id: jobId }).then(res => res.data)