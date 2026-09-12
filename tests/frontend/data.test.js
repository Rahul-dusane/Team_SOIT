import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
const expect = actual => ({ toBe: expected => assert.equal(actual, expected), toBeNull: () => assert.equal(actual,null), toEqual: expected => assert.deepEqual(actual,expected) })
import { formatCandidateForUI, formatJobForUI, mergeRankings, uploadOutcome } from '../../src/services/viewData.js'
describe('truthful data mapping', () => {
  it('preserves real zero scores', () => expect(formatCandidateForUI({overall_score:0, score:90}).score).toBe(0))
  it('never invents scores or roles', () => { const c = formatCandidateForUI({education:[]}); expect(c.score).toBeNull(); expect(c.role).toBe('Role not provided'); expect(typeof c.education).toBe('string') })
  it('handles non-IT profiles and uncertain skills', () => { const c = formatCandidateForUI({name:'Asha Rao', experiences:[{role:'Registered Nurse'}], skills:[{raw_skill:'Patient triage'},null], education:[{degree:'BSN'}]}); expect(c.role).toBe('Registered Nurse'); expect(c.skills).toEqual(['Patient triage']); expect(c.education).toBe('BSN') })
  it('distinguishes absent experience from zero months', () => { expect(formatCandidateForUI({}).experience).toBe('Not provided'); expect(formatCandidateForUI({total_experience_months:0}).experience).toBe('0 months') })
  it('does not invent job applicants or skills', () => { expect(formatJobForUI({job_id:'j',applicants:0}).applicants).toBe(0); expect(formatJobForUI({job_id:'j'}).skills).toEqual([]); expect(formatJobForUI({}).applicants).toBeNull() })
  it('preserves match identity and rank; overrides stale profile score', () => { const [c] = mergeRankings({job_id:'j', rankings:[{candidate_id:'c',match_id:'m',rank:2,overall_score:0}]},[{candidate_id:'c',score:91}]); expect(c.match_id).toBe('m'); expect(c.rank).toBe(2); expect(c.score).toBe(0) })
  it('empty ranking never falls back to candidates', () => expect(mergeRankings({rankings:[]},[{candidate_id:'c'}])).toEqual([]))
  it('missing ranking score never reuses profile score', () => expect(mergeRankings({rankings:[{candidate_id:'c'}]},[{candidate_id:'c',score:91}])[0].score).toBeNull())
  it('reports partial upload failure and duplicate separately', () => { expect(uploadOutcome({status:'failed',error:'Bad PDF'})).toEqual({status:'Failed',error:'Bad PDF'}); expect(uploadOutcome({status:'duplicate'}).status).toBe('Already stored'); expect(uploadOutcome().status).toBe('Failed') })
})
