import { useEffect, useState, useRef, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, User, Briefcase, Trophy, ArrowRight, Command, X, Sparkles } from 'lucide-react'
import { getCandidates, getJobs, formatCandidateForUI, formatJobForUI } from '../api/api'

export default function SpotlightSearch({ open, onClose }) {
  const navigate = useNavigate()
  const inputRef = useRef(null)
  const [query, setQuery] = useState('')
  const [candidates, setCandidates] = useState([])
  const [jobs, setJobs] = useState([])
  const [selectedIndex, setSelectedIndex] = useState(0)

  useEffect(() => {
    let active = true
    Promise.allSettled([getCandidates(), getJobs()]).then(([cRes, jRes]) => {
      if (!active) return
      if (cRes.status === 'fulfilled' && Array.isArray(cRes.value)) {
        setCandidates(cRes.value.map(formatCandidateForUI))
      }
      if (jRes.status === 'fulfilled' && Array.isArray(jRes.value)) {
        setJobs(jRes.value.map(formatJobForUI))
      }
    })
    return () => { active = false }
  }, [])

  useEffect(() => {
    if (open) {
      setQuery('')
      setSelectedIndex(0)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [open])

  // Filtered Spotlight Results
  const results = useMemo(() => {
    if (!query.trim()) return []
    const q = query.toLowerCase()

    const candidateMatches = candidates
      .filter(c => `${c.name || ''} ${c.role || ''} ${c.skills?.join(' ') || ''}`.toLowerCase().includes(q))
      .slice(0, 4)
      .map(c => ({
        id: c.id,
        type: 'candidate',
        title: c.name || 'Candidate',
        subtitle: c.role || 'Candidate Profile',
        badge: 'Candidate',
        url: `/matches/${encodeURIComponent(c.id)}`,
        icon: User
      }))

    const jobMatches = jobs
      .filter(j => `${j.title || ''} ${j.department || ''}`.toLowerCase().includes(q))
      .slice(0, 3)
      .map(j => ({
        id: j.id,
        type: 'job',
        title: j.title || 'Job Opening',
        subtitle: j.department || 'Job Position',
        badge: 'Job',
        url: `/ranking?job_id=${encodeURIComponent(j.id)}`,
        icon: Briefcase
      }))

    return [...candidateMatches, ...jobMatches]
  }, [query, candidates, jobs])

  // Reset selected index when results change
  useEffect(() => {
    setSelectedIndex(0)
  }, [results])

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      onClose()
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIndex(prev => (prev + 1) % Math.max(1, results.length))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIndex(prev => (prev - 1 + results.length) % Math.max(1, results.length))
    } else if (e.key === 'Enter' && results[selectedIndex]) {
      e.preventDefault()
      const target = results[selectedIndex]
      onClose()
      navigate(target.url)
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-slate-900/60 backdrop-blur-md animate-fade-in">
      <div
        className="w-full max-w-2xl overflow-hidden rounded-3xl border border-white/20 bg-white/90 backdrop-blur-2xl shadow-2xl transition-all"
        onKeyDown={handleKeyDown}
      >
        {/* Top Input Header Bar */}
        <div className="relative flex items-center border-b border-slate-200/80 px-5 py-4">
          <Search className="text-slate-400 mr-3" size={20} />
          <input
            ref={inputRef}
            type="text"
            className="w-full bg-transparent text-base font-bold text-slate-900 placeholder:text-slate-400 outline-none"
            placeholder="Search candidates, job roles, rankings..."
            value={query}
            aria-label="Spotlight Search"
            onChange={e => setQuery(e.target.value)}
          />
          {query ? (
            <button onClick={() => setQuery('')} className="p-1 text-slate-400 hover:text-slate-600 rounded-full">
              <X size={16} />
            </button>
          ) : (
            <span className="flex items-center gap-1 rounded-lg bg-slate-100 px-2 py-1 text-[10px] font-bold text-slate-400 font-mono">
              <Command size={10} /> K
            </span>
          )}
        </div>

        {/* Results Body */}
        <div className="max-h-96 overflow-y-auto p-3 space-y-1">
          {!query.trim() ? (
            <div className="py-8 text-center text-slate-400">
              <Sparkles size={24} className="mx-auto mb-2 text-apple-blue/60" />
              <p className="text-xs font-semibold text-slate-500">Type candidate names, roles, or job titles</p>
              <p className="text-[11px] text-slate-400 mt-0.5">Use <kbd className="font-mono bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">↑</kbd> <kbd className="font-mono bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">↓</kbd> to navigate, <kbd className="font-mono bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">Enter</kbd> to select</p>
            </div>
          ) : !results.length ? (
            <div className="py-8 text-center text-slate-400 text-xs font-semibold">
              No matching candidates or jobs found for "{query}"
            </div>
          ) : (
            results.map((item, idx) => {
              const Icon = item.icon
              const isSelected = idx === selectedIndex
              return (
                <div
                  key={`${item.type}-${item.id}-${idx}`}
                  onClick={() => {
                    onClose()
                    navigate(item.url)
                  }}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`flex items-center justify-between rounded-2xl p-3.5 cursor-pointer transition-all duration-150 ${
                    isSelected
                      ? 'bg-gradient-to-r from-slate-900 to-slate-800 text-white shadow-md'
                      : 'hover:bg-slate-100/80 text-slate-800'
                  }`}
                >
                  <div className="flex items-center gap-3.5">
                    <div className={`flex h-10 w-10 items-center justify-center rounded-xl font-extrabold ${
                      isSelected ? 'bg-apple-blue text-white' : 'bg-slate-100 text-slate-600'
                    }`}>
                      <Icon size={18} />
                    </div>
                    <div>
                      <h4 className="text-sm font-extrabold tracking-tight">{item.title}</h4>
                      <p className={`text-xs font-medium ${isSelected ? 'text-slate-300' : 'text-slate-500'}`}>
                        {item.subtitle}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={`pill-badge text-[10px] ${
                      isSelected
                        ? 'bg-white/20 text-white border border-white/30'
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      {item.badge}
                    </span>
                    <ArrowRight size={14} className={isSelected ? 'text-apple-blue' : 'text-slate-300'} />
                  </div>
                </div>
              )
            })
          )}
        </div>

        {/* Footer Bar */}
        <div className="flex items-center justify-between border-t border-slate-200/80 bg-slate-50/70 px-5 py-2.5 text-[11px] font-semibold text-slate-400">
          <span>HireLens Spotlight Search</span>
          <span>Press ESC to close</span>
        </div>
      </div>
    </div>
  )
}
