export { formatCandidateForUI } from '../../src/services/viewData.js'
export const state = { responses: {}, calls: [] }
const request = (name, args) => {
  state.calls.push({name,args})
  const response = state.responses[name]
  if (response instanceof Error || response?.reject) return Promise.reject(response.reject || response)
  return Promise.resolve(response)
}
export const getCandidates = (...args) => request('getCandidates', args)
export const getJobs = (...args) => request('getJobs', args)
export const getRanking = (...args) => request('getRanking', args)
export const getDashboardStats = (...args) => request('getDashboardStats', args)
export const getMatchDetails = (...args) => request('getMatchDetails', args)
export const getCandidateById = (...args) => request('getCandidateById', args)
export const runMatch = (...args) => request('runMatch', args)
export const createJob = (...args) => request('createJob', args)
export const uploadResumes = (...args) => request('uploadResumes', args)
