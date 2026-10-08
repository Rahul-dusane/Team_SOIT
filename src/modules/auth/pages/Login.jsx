import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../../core/auth/AuthContext'
import {
  Sparkles,
  Mail,
  Lock,
  ArrowRight,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle2,
  ShieldCheck,
  Cpu
} from 'lucide-react'

export default function Login() {
  const { signIn, isSupabaseLive } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const from = location.state?.from?.pathname || '/'

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email || !password) {
      setError('Please provide both your email address and password.')
      return
    }

    try {
      setLoading(true)
      setError(null)
      await signIn({ email, password })
      navigate(from, { replace: true })
    } catch (err) {
      console.error('Sign-in error:', err)
      setError(err.message || 'Failed to sign in. Please verify your credentials.')
    } finally {
      setLoading(false)
    }
  }

  const fillDemoCredentials = (demoEmail, demoPass) => {
    setEmail(demoEmail)
    setPassword(demoPass)
    setError(null)
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
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Welcome back</h1>
          <p className="text-sm text-slate-500 mt-1">
            Sign in to access your talent intelligence workflows
          </p>
        </div>

        {/* Card */}
        <div className="rounded-3xl border border-slate-200/80 bg-white/80 p-8 shadow-xl backdrop-blur-2xl transition-all duration-300">
          {/* Supabase Status Pill */}
          <div className="mb-6 flex items-center justify-between rounded-xl bg-slate-50 border border-slate-200/70 px-3.5 py-2">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-xs font-semibold text-slate-700">
                {isSupabaseLive ? 'Supabase Auth Gateway Active' : 'Supabase Auth (Integrated Mode)'}
              </span>
            </div>
            <span className="text-[10px] font-bold text-apple-blue bg-apple-blue/10 px-2 py-0.5 rounded-full uppercase tracking-wider">
              Secure
            </span>
          </div>

          {error && (
            <div className="mb-5 flex items-start gap-3 rounded-2xl bg-rose-50/80 border border-rose-200/80 p-3.5 text-xs text-rose-800">
              <AlertCircle size={16} className="text-rose-500 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
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
                  placeholder="recruiter@company.com"
                  className="w-full rounded-2xl border border-slate-200/90 bg-white/90 pl-10 pr-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 transition-all duration-200 focus:border-apple-blue focus:outline-none focus:ring-4 focus:ring-apple-blue/10"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Password
                </label>
                <Link
                  to="/forgot-password"
                  className="text-xs font-semibold text-apple-blue hover:text-apple-blue/80 transition-colors"
                >
                  Forgot password?
                </Link>
              </div>
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
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
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
                  <span>Signing In...</span>
                </>
              ) : (
                <>
                  <span>Sign In to Cockpit</span>
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Fill Buttons */}
          <div className="mt-6 pt-5 border-t border-slate-200/60">
            <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2.5 text-center">
              One-Click Demo Credentials
            </p>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => fillDemoCredentials('recruiter@hirelens.ai', 'password123')}
                className="flex items-center justify-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50/80 px-2.5 py-2 text-xs font-semibold text-slate-700 transition-all hover:bg-white hover:border-apple-blue/50"
              >
                <ShieldCheck size={13} className="text-apple-blue" />
                <span>Recruiter Demo</span>
              </button>
              <button
                type="button"
                onClick={() => fillDemoCredentials('admin@hirelens.ai', 'adminpassword123')}
                className="flex items-center justify-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50/80 px-2.5 py-2 text-xs font-semibold text-slate-700 transition-all hover:bg-white hover:border-apple-blue/50"
              >
                <Cpu size={13} className="text-napkin-purple" />
                <span>Admin Demo</span>
              </button>
            </div>
          </div>
        </div>

        {/* Footer Link */}
        <p className="mt-6 text-center text-xs text-slate-500">
          Don't have an enterprise account?{' '}
          <Link to="/signup" className="font-bold text-apple-blue hover:underline">
            Create an Account
          </Link>
        </p>
      </div>
    </div>
  )
}
