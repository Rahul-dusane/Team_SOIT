import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import {
  LogOut,
  User,
  Shield,
  ChevronDown,
  Sparkles,
  CheckCircle2,
  ExternalLink,
} from 'lucide-react'

export default function UserMenu() {
  const { user, signOut, isSupabaseLive } = useAuth()
  const [open, setOpen] = useState(false)
  const menuRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  if (!user) return null

  const getInitials = (name) => {
    if (!name) return 'HL'
    const parts = name.trim().split(' ')
    if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
    return name.slice(0, 2).toUpperCase()
  }

  const roleLabels = {
    admin: 'Administrator',
    recruiter: 'Senior Recruiter',
    hiring_manager: 'Hiring Manager',
    interviewer: 'Interviewer',
    viewer: 'Viewer',
    user: 'Recruiter'
  }

  const handleSignOut = async () => {
    try {
      await signOut()
      navigate('/login', { replace: true })
    } catch (err) {
      console.error('Error signing out:', err)
    }
  }

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2.5 rounded-full border border-slate-200/80 bg-white/80 p-1.5 pr-3 text-left transition-all duration-200 hover:border-apple-blue/40 hover:bg-white hover:shadow-sm"
        aria-expanded={open}
        aria-haspopup="true"
      >
        <span className="relative flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-tr from-slate-900 via-napkin-indigo to-apple-blue text-xs font-bold text-white shadow-sm">
          {getInitials(user.fullName)}
          <span className="absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full border-2 border-white bg-emerald-500" />
        </span>
        <div className="hidden md:flex flex-col">
          <span className="text-xs font-bold text-slate-800 leading-tight">
            {user.fullName}
          </span>
          <span className="text-[10px] font-medium text-slate-400 capitalize">
            {roleLabels[user.role] || user.role}
          </span>
        </div>
        <ChevronDown size={14} className={`text-slate-400 transition-transform duration-200 ${open ? 'rotate-180' : ''}`} />
      </button>

      {/* Flyout Menu */}
      {open && (
        <div className="absolute right-0 mt-2 w-72 origin-top-right rounded-3xl border border-slate-200/90 bg-white/95 p-3 shadow-2xl backdrop-blur-2xl ring-1 ring-black/5 animate-in fade-in zoom-in-95 duration-150 z-50">
          {/* Header Profile Details */}
          <div className="rounded-2xl bg-gradient-to-br from-slate-50 to-slate-100/70 p-3.5 border border-slate-200/60 mb-2">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-900 text-sm font-bold text-white shadow-md">
                {getInitials(user.fullName)}
              </span>
              <div className="flex flex-col min-w-0">
                <span className="text-xs font-bold text-slate-900 truncate">
                  {user.fullName}
                </span>
                <span className="text-[11px] text-slate-500 truncate">
                  {user.email}
                </span>
              </div>
            </div>
            <div className="mt-2.5 flex items-center justify-between border-t border-slate-200/50 pt-2 text-[10px]">
              <span className="font-semibold text-slate-400 uppercase tracking-wider">Role</span>
              <span className="rounded-md bg-apple-blue/10 px-2 py-0.5 font-bold text-apple-blue">
                {roleLabels[user.role] || user.role}
              </span>
            </div>
          </div>

          {/* Supabase Connection Status */}
          <div className="px-3 py-2 flex items-center justify-between text-[11px] text-slate-600 border-b border-slate-100 mb-1">
            <span className="flex items-center gap-1.5">
              <Sparkles size={12} className="text-apple-blue" />
              <span>Supabase Auth</span>
            </span>
            <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-600">
              <CheckCircle2 size={11} /> Connected
            </span>
          </div>

          {/* Menu Items */}
          <div className="space-y-0.5">
            <button
              onClick={() => {
                setOpen(false)
                navigate('/resumes')
              }}
              className="w-full flex items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100/80 transition-colors"
            >
              <User size={14} className="text-slate-400" />
              <span>Talent Workspace</span>
            </button>
          </div>

          {/* Sign Out Button */}
          <div className="mt-2 pt-2 border-t border-slate-100">
            <button
              onClick={handleSignOut}
              className="w-full flex items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-semibold text-rose-600 hover:bg-rose-50/80 transition-colors"
            >
              <LogOut size={14} className="text-rose-500" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
