import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { GitCompare, CheckCircle2, ArrowUpRight } from 'lucide-react'
import { getCandidates, formatCandidateForUI } from '../../../core/api/api'
import ErrorBanner from '../../../core/components/ErrorBanner'

export default function Compare() {
  const [candidates, setCandidates] = useState([])
  const [selected, setSelected] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    getCandidates()
      .then(data => {
        if (!active) return
        if (!Array.isArray(data)) throw new Error('Invalid candidate response.')
        const formatted = data.map(formatCandidateForUI)
        setCandidates(formatted)
        setSelected(formatted.slice(0, 3).map(c => c.id))
      })
      .catch(e => { if (active) setError(e.message) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [])

  const selectedCandidates = candidates.filter(c => selected.includes(c.id))

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div>
        <div className="inline-flex items-center gap-1.5 pill-badge bg-apple-blue/10 text-apple-blue border border-apple-blue/20 mb-2">
          <GitCompare size={12} /> Candidate Comparison Engine
        </div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Side-by-Side Matrix</h1>
        <p className="mt-1 text-sm text-slate-500">Compare skills, experience, education, and domain attributes across multiple candidates.</p>
      </div>

      <ErrorBanner message={error} />

      {loading ? (
        <div className="panel p-12 text-center text-slate-400 font-medium">Loading candidate data for comparison...</div>
      ) : !candidates.length ? (
        <div className="panel p-12 text-center text-slate-500">No candidate profiles stored in database.</div>
      ) : (
        <>
          {/* Candidate Selection Pills */}
          <div className="panel p-6 shadow-apple-card space-y-3">
            <span className="eyebrow block">Select Candidates to Compare (Max 4)</span>
            <div className="flex flex-wrap gap-2.5">
              {candidates.map(c => {
                const isSelected = selected.includes(c.id)
                return (
                  <button
                    key={c.id}
                    onClick={() =>
                      setSelected(old =>
                        isSelected ? old.filter(id => id !== c.id) : old.length < 4 ? [...old, c.id] : old
                      )
                    }
                    className={`pill-badge border py-2 px-4 transition-all duration-200 ${
                      isSelected
                        ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                        : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    {isSelected && <CheckCircle2 size={13} className="text-apple-blue" />}
                    <span>{c.name}</span>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Comparison Matrix Table */}
          {!selectedCandidates.length ? (
            <div className="panel p-12 text-center text-slate-500">Select at least one candidate above to generate comparison matrix.</div>
          ) : (
            <div className="panel overflow-x-auto p-6 shadow-panel">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200/80">
                    <th className="p-4 font-black text-slate-900 uppercase tracking-wider w-44">Attribute</th>
                    {selectedCandidates.map(c => (
                      <th key={c.id} className="p-4 font-black text-slate-900 text-sm">
                        <Link to={`/matches/${encodeURIComponent(c.id)}`} className="hover:text-apple-blue flex items-center gap-1">
                          {c.name} <ArrowUpRight size={14} />
                        </Link>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {[
                    ['Primary Role', 'role'],
                    ['Experience', 'experience'],
                    ['Education', 'education'],
                    ['Skills', 'skills'],
                    ['Projects', 'projects'],
                    ['Certifications', 'certifications']
                  ].map(([label, key]) => (
                    <tr key={key} className="hover:bg-slate-50/50 transition-colors">
                      <td className="p-4 font-bold text-slate-800">{label}</td>
                      {selectedCandidates.map(c => (
                        <td key={c.id} className="p-4 text-slate-600 font-medium">
                          {Array.isArray(c[key]) ? (
                            <div className="flex flex-wrap gap-1">
                              {c[key].length ? (
                                c[key].map((item, idx) => (
                                  <span key={idx} className="pill-badge bg-slate-100 text-slate-700">
                                    {typeof item === 'string' ? item : item.name || item.raw_skill}
                                  </span>
                                ))
                              ) : (
                                <span className="text-slate-400">None</span>
                              )}
                            </div>
                          ) : (
                            c[key] || <span className="text-slate-400">Not provided</span>
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  )
}
