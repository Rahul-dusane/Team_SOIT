import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCandidates, formatCandidateForUI } from '../services/api'
import ErrorBanner from '../components/ErrorBanner'

export default function Compare() {
  const [candidates, setCandidates] = useState([])
  const [selected, setSelected] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  useEffect(() => {
    let active = true
    getCandidates().then(data => {
      if (!active) return
      if (!Array.isArray(data)) throw new Error('Invalid candidate response.')
      setCandidates(data.map(formatCandidateForUI)); setSelected(data.slice(0,3).map(c => c.candidate_id))
    }).catch(e => { if (active) setError(e.message) }).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [])
  const rows = candidates.filter(c => selected.includes(c.id))
  return <div className="mx-auto max-w-7xl"><h1 className="mb-3 text-3xl font-extrabold">Compare candidates</h1><p className="mb-6 text-sm text-muted">Compare saved profile attributes. Job-specific scores are available in candidate ranking.</p><ErrorBanner message={error} />{loading ? <p>Loading candidates…</p> : error ? <p>Candidate data unavailable.</p> : !candidates.length ? <p>No candidates saved yet.</p> : <>
    <fieldset className="panel mb-6 flex flex-wrap gap-4 p-5"><legend>Select candidates</legend>{candidates.map(c => <label key={c.id} className="text-sm"><input type="checkbox" checked={selected.includes(c.id)} onChange={e => setSelected(old => e.target.checked ? [...old,c.id] : old.filter(id => id !== c.id))} /> {c.name}</label>)}</fieldset>
    {!rows.length ? <p>Select candidates to compare.</p> : <section className="panel overflow-x-auto p-6"><table className="w-full text-left text-sm"><thead><tr><th className="p-3">Attribute</th>{rows.map(c => <th className="p-3" key={c.id}><Link to={`/matches/${encodeURIComponent(c.id)}`}>{c.name}</Link></th>)}</tr></thead><tbody>{[['Role','role'],['Experience','experience'],['Education','education'],['Skills','skills'],['Projects recorded','projects'],['Certifications recorded','certifications']].map(([label,key]) => <tr key={key} className="border-t"><th className="p-3">{label}</th>{rows.map(c => <td key={c.id} className="p-3">{Array.isArray(c[key]) ? c[key].join(', ') || 'None recorded' : c[key] ?? 'Not provided'}</td>)}</tr>)}</tbody></table></section>}</>}
  </div>
}
