import axios from 'axios'

export const api = axios.create({ baseURL: 'http://localhost:8000/api/v1' })
export const uploadResumes = (files, onUploadProgress) => api.post('/resumes/upload', files, { onUploadProgress })
export const getCandidates = () => api.get('/candidates')
export const getJobs = () => api.get('/jobs')
export const getRanking = (params) => api.get('/ranking', { params })
export const getMatchDetails = (id) => api.get(`/matches/${id}`)