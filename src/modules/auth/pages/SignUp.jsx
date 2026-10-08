import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../../core/auth/AuthContext'
import {
  Sparkles,
  Mail,
  Lock,
  User,
  Briefcase,
  ArrowRight,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react'

export default function SignUp() {
  const { signUp, isSupabaseLive } = useAuth()
  const navigate = useNavigate()

  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [role, setRole] = useState('recruiter')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [successMsg, setSuccessMsg] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    if (password.length < 6) {
      setError('Password must be at least 6 characters in length.')
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match. Please verify your entries.')
      return
    }

    try {
      setLoading(true)
      await signUp({
        email,
        password,
        fullName,
        role
      })
      setSuccessMsg('Account created successfully! Redirecting to dashboard...')
      setTimeout(() => {
        navigate('/', { replace: true })
      }, 1200)
    } catch (err) {
      console.error('Sign-up error:', err)
      setError(err.message || 'Failed to register account. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50/60 mesh-bg px-4 py-12 selection:bg-apple-blue/20 selection:text-apple-blue">
      <div className="w-full max-w-md">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-3 group mb-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-slate-900 via-napkin-indigo to-apple-blue shadow-glow text-white transition-transform duration-300 group-hover:scale-105">
              <Sparkles size={24} className="animate-pulse" />
            </div>
            <div className="text-left">
              <span className="font-extrabold text-slate-900 tracking-tight text-2xl leading-none">
                Hire<span className="text-apple-blue">Lens</span>
              </span>
              <span className="block text-[10px] font-semibold text-slate-400 tracking-wider uppercase mt-1">
                Recruitment Intelligence Cockpit
              </span>
            </div>
          </Link>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Create your account</h1>
          <p className="text-sm text-slate-500 mt-1">
            Join the agentic talent matching workspace
          </p>
        </div>

        {/* Card */}
        <div className="rounded-3xl border border-slate-200/80 bg-white/80 p-8 shadow-xl backdrop-blur-2xl transition-all duration-300">
          {error && (
            <div className="mb-5 flex items-start gap-3 rounded-2xl bg-rose-50/80 border border-rose-200/80 p-3.5 text-xs text-rose-800">
              <AlertCircle size={16} className="text-rose-500 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {successMsg && (
            <div className="mb-5 flex items-start gap-3 rounded-2xl bg-emerald-50/80 border border-emerald-200/80 p-3.5 text-xs text-emerald-800">
              <CheckCircle2 size={16} className="text-emerald-500 shrink-0 mt-0.5" />
              <span>{successMsg}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Full Name
              </label>
              <div className="relative">
                <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Alex Mercer"
                  className="w-full rounded-2xl border border-slate-200/90 bg-white/90 pl-10 pr-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 transition-all duration-200 focus:border-apple-blue focus:outline-none focus:ring-4 focus:ring-apple-blue/10"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Work Email
              </label>
              <div className="relative">
                <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="recruiter@enterprise.com"
                  className="w-full rounded-2xl border border-slate-200/90 bg-white/90 pl-10 pr-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 transition-all duration-200 focus:border-apple-blue focus:outline-none focus:ring-4 focus:ring-apple-blue/10"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Recruitment Role (RBAC)
              </label>
              <div className="relative">
                <Briefcase size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full appearance-none rounded-2xl border border-slate-200/90 bg-white/90 pl-10 pr-8 py-3 text-sm font-medium text-slate-900 transition-all duration-200 focus:border-apple-blue focus:outline-none focus:ring-4 focus:ring-apple-blue/10"
                >
                  <option value="recruiter">Talent Acquisition Recruiter</option>
                  <option value="hiring_manager">Hiring Manager</option>
                  <option value="interviewer">Technical Interviewer</option>
                  <option value="admin">Platform Administrator</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Password (min 6 characters)
              </label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full rounded-2xl border border-slate-200/90 bg-white/90 pl-10 pr-10 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 transition-all duration-200 focus:border-apple-blue focus:outline-none focus:ring-4 focus:ring-apple-blue/10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Confirm Password
              </label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full rounded-2xl border border-slate-200/90 bg-white/90 pl-10 pr-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 transition-all duration-200 focus:border-apple-blue focus:outline-none focus:ring-4 focus:ring-apple-blue/10"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 flex items-center justify-center gap-2 rounded-2xl bg-slate-900 px-5 py-3.5 text-sm font-bold text-white shadow-md transition-all duration-200 hover:bg-apple-blue hover:shadow-glow disabled:opacity-50 disabled:pointer-events-none"
            >
              {loading ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  <span>Registering Account...</span>
                </>
              ) : (
                <>
                  <span>Create Account</span>
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>
        </div>

        {/* Footer Link */}
        <p className="mt-6 text-center text-xs text-slate-500">
          Already have an account?{' '}
          <Link to="/login" className="font-bold text-apple-blue hover:underline">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  )
}
