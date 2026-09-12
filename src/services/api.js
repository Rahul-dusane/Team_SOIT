import axios from 'axios'

export { formatCandidateForUI, getInitials } from './viewData'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const apiKey = import.meta.env.VITE_API_KEY
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    let errorMessage = 'An unexpected error occurred.'
    let statusCode = error.response ? error.response.status : 0
    let isOffline = !error.response

    if (isOffline) {
      errorMessage = 'Backend server is unreachable. Data could not be loaded.'
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