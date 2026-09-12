import React, { act } from 'react'
import { createRoot } from 'react-dom/client'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { state } from './fixtureApi'
import Dashboard from '../../src/pages/Dashboard'
import Jobs from '../../src/pages/Jobs'
import Resumes from '../../src/pages/Resumes'
import Ranking from '../../src/pages/Ranking'
import Compare from '../../src/pages/Compare'
import MatchDetail from '../../src/pages/MatchDetail'
import CreateJob from '../../src/pages/CreateJob'
import UploadArea from '../../src/components/UploadArea'
import AgentTimeline from '../../src/components/AgentTimeline'
import EvidenceDrawer from '../../src/components/EvidenceDrawer'
import MatchScore from '../../src/components/MatchScore'
globalThis.IS_REACT_ACT_ENVIRONMENT = true
const fixture = document.getElementById('fixture')
const candidate = {candidate_id:'nurse-1',name:'Asha Rao',experiences:[{role:'Nurse'}],skills:['Patient triage'],education:[],total_experience_months:0}
const job = {job_id:'ward-1',title:'Ward Nurse'}
let root, passed=0, failed=0
function assert(condition,message) { if (!condition) throw new Error(message) }
const text = () => fixture.textContent
const contains = value => assert(text().includes(value),`Missing: ${value}`)
const absent = value => assert(!text().includes(value),`Unexpected: ${value}`)
const button = name => [...fixture.querySelectorAll('button')].find(b => b.textContent.includes(name))
async function mount(component,path='/') {
  root = createRoot(fixture)
  await act(async () => { root.render(<MemoryRouter initialEntries={[path]}><Routes><Route path="*" element={component}/><Route path="/matches/:id" element={<MatchDetail/>}/></Routes></MemoryRouter>); await new Promise(r=>setTimeout(r,0)) })
}
async function test(name, fn) {
  state.responses = { getCandidates:[candidate], getJobs:[job], getRanking:{job_id:job.job_id,job_title:job.title,rankings:[]}, getDashboardStats:{total_candidates:1,active_jobs:1}, getMatchDetails:{reject:{status:404,message:'Not found'}}, getCandidateById:candidate }
  state.calls=[]
  try { await fn(); passed++; const li=document.createElement('li'); li.textContent=`PASS: ${name}`; document.getElementById('results').append(li) }
  catch(error) { failed++; const li=document.createElement('li'); li.textContent=`FAIL: ${name}: ${error.message}`; document.getElementById('results').append(li) }
  finally { if(root) await act(async()=>root.unmount()); root=null }
}
await test('Loading overview contains no sample counts', async()=>{state.responses.getDashboardStats=new Promise(()=>{}); await mount(<Dashboard/>); contains('Loading'); absent('128'); absent('Rahul')})
await test('Overview displays returned counts and unknown missing metrics', async()=>{await mount(<Dashboard/>); contains('Asha Rao'); contains('Unavailable'); absent('Anika'); absent('91%')})
await test('Partial overview failure retains only successful data', async()=>{state.responses.getDashboardStats={reject:{message:'Stats denied'}}; await mount(<Dashboard/>); contains('Statistics: Stats denied'); contains('Asha Rao')})
for(const [Page,name,empty] of [[Resumes,'Resumes','No candidates found'],[Jobs,'Jobs','No jobs saved yet'],[Compare,'Compare','No candidates saved yet'],[Ranking,'Ranking','No candidate rankings found']]) {
  await test(`${name}: empty response does not restore demo records`,async()=>{state.responses.getCandidates=[];state.responses.getJobs=[];await mount(<Page/>);contains(empty);absent('Rahul');absent('Priya')})
  await test(`${name}: rejected request exposes failure without sample records`,async()=>{state.responses.getCandidates={reject:{message:'Unauthorized'}};state.responses.getJobs={reject:{message:'Unauthorized'}};await mount(<Page/>);contains('Unauthorized');absent('Asha Rao');absent('Rahul')})
}
await test('Ranking preserves zero score and exact match link',async()=>{state.responses.getRanking={job_id:job.job_id,job_title:job.title,rankings:[{candidate_id:candidate.candidate_id,match_id:'saved-match',rank:1,overall_score:0,decision:'REJECTED'}]};await mount(<Ranking/>,'/ranking?job_id=ward-1');contains('0%');contains('REJECTED');assert(fixture.querySelector('a[href="/matches/saved-match"]'),'wrong match URL');assert(state.calls.find(c=>c.name==='getRanking').args[0]==='ward-1','wrong job')})
await test('Compare uses real profile attributes',async()=>{await mount(<Compare/>);contains('Patient triage');contains('0 months');absent('86%');absent('Skills score')})
await test('Compare selection removes the selected profile column',async()=>{await mount(<Compare/>);await act(async()=>fixture.querySelector('input[type=checkbox]').click());contains('Select candidates to compare.');assert(!fixture.querySelector('table'),'stale comparison table')})
await test('Missing match requires explicit saved job selection',async()=>{await mount(<MatchDetail/>,'/matches/nurse-1');contains('Asha Rao');contains('Not scored');assert(button('Run Match Engine').disabled,'default job chosen without user input');assert(!state.calls.some(c=>c.name==='runMatch'),'unexpected match execution')})
await test('Match authorization failure never falls back to profile',async()=>{state.responses.getMatchDetails={reject:{status:401,message:'Access denied'}};await mount(<MatchDetail/>,'/matches/1');contains('Access denied');assert(!state.calls.some(c=>c.name==='getCandidateById'),'auth error swallowed');absent('Rahul')})
await test('Saved match shows actual zero, raw points, and failed agent',async()=>{state.responses.getMatchDetails={match_id:'m',candidate_id:candidate.candidate_id,job_id:job.job_id,overall_score:0,raw_score_breakdown:{preferred:2.5,must_have:0},agent_logs:[{agent_name:'Resume Agent',status:'failed',step_index:1}],summary:{}};await mount(<MatchDetail/>,'/matches/m');contains('0%');contains('2.5 points');contains('failed');contains('No evidence passages');absent('Complete')})
await test('Uploading mixed results distinguishes parsed, failed, duplicate',async()=>{state.responses.uploadResumes={file_results:[{status:'success'},{status:'failed',error:'Unreadable document'},{status:'duplicate'}]};await mount(<UploadArea/>);absent('Rahul');const input=fixture.querySelector('input[type=file]');Object.defineProperty(input,'files',{configurable:true,value:[new File(['a'],'a.txt'),new File(['b'],'b.txt'),new File(['c'],'c.txt')]});await act(async()=>input.dispatchEvent(new Event('change',{bubbles:true})));contains('Parsed');contains('Failed: Unreadable document');contains('Already stored')})
await test('Upload missing per-file confirmation fails closed',async()=>{state.responses.uploadResumes={};await mount(<UploadArea/>);const input=fixture.querySelector('input[type=file]');Object.defineProperty(input,'files',{value:[new File(['a'],'a.txt')]});await act(async()=>input.dispatchEvent(new Event('change',{bubbles:true})));contains('did not confirm');absent('Parsed')})
await test('Job form starts without seeded role or skills',async()=>{await mount(<CreateJob/>);assert(fixture.querySelector('input[placeholder="e.g. Senior Backend Engineer"]').value==='','seeded title');assert(fixture.querySelector('textarea').value==='','seeded description');contains('0 entered');absent('AI extraction')})
await test('Job submission carries the entered description without hidden defaults',async()=>{state.responses.createJob={job_id:'new'};await mount(<CreateJob/>);const input=fixture.querySelector('input[placeholder="e.g. Senior Backend Engineer"]');const desc=fixture.querySelector('textarea');await act(async()=>{Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(input,'Ward Nurse');input.dispatchEvent(new Event('input',{bubbles:true}));Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(desc,'Provide patient care');desc.dispatchEvent(new Event('input',{bubbles:true}))});await act(async()=>fixture.querySelector('form').dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})));const payload=state.calls.find(c=>c.name==='createJob')?.args[0];assert(payload?.description==='Provide patient care','description omitted');assert(payload.min_experience_months===0,'hidden experience');assert(!payload.requirements.length,'seeded requirements')})
await test('Missing score and agent records display unknown',async()=>{await mount(<><MatchScore/><AgentTimeline/></>);contains('Not scored');contains('No agent execution logs available.')})
await test('Evidence displays only returned passage and page',async()=>{await mount(<EvidenceDrawer open evidence={{evidence_passage:'Provided patient triage',page_number:3}} onClose={()=>{}}/>);contains('Provided patient triage');contains('Page 3');absent('50k');absent('94%')})
document.getElementById('summary').textContent=`${passed} passed; ${failed} failed; ${passed+failed} total`
