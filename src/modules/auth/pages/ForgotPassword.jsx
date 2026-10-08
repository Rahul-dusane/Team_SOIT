import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../../core/auth/AuthContext'
import { Sparkles, Mail, ArrowRight, ArrowLeft, CheckCircle2, AlertCircle } from 'lucide-react'

export default function ForgotPassword() {
  const { resetPassword } = useAuth()
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email) return

    try {
      setLoading(true)
      setError(null)
      await resetPassword(email)
      setSuccess(true)
    } catch (err) {
      setError(err.message || 'Unable to send password reset instructions.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50/60 mesh-bg px-4 py-12 selection:bg-apple-blue/20 selection:text-apple-blue">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-3 group mb-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-slate-900 via-napkin-indigo to-apple-blue shadow-glow text-white">
              <Sparkles size={24} />
            </div>
            <div className="text-left">
              <span className="font-extrabold text-slate-900 tracking-tight text-2xl leading-none">
                Hire<span className="text-apple-blue">Lens</span>
              </span>
            </div>
          </Link>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Reset your password</h1>
          <p className="text-sm text-slate-500 mt-1">
            Enter your email and we'll send a recovery link
          </p>
        </div>

        <div className="rounded-3xl border border-slate-200/80 bg-white/80 p-8 shadow-xl backdrop-blur-2xl">
          {success ? (
            <div className="text-center space-y-4 py-2">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600 border border-emerald-200">
                <CheckCircle2 size={28} />
              </div>
              <h3 className="text-base font-bold text-slate-900">Check your inbox</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                We've sent password reset instructions to <span className="font-semibold text-slate-800">{email}</span>.
              </p>
              <Link
                to="/login"
                className="inline-flex items-center gap-2 text-xs font-bold text-apple-blue hover:underline pt-2"
              >
                <ArrowLeft size={14} /> Back to Sign In
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="flex items-start gap-3 rounded-2xl bg-rose-50/80 border border-rose-200/80 p-3.5 text-xs text-rose-800">
                  <AlertCircle size={16} className="text-rose-500 shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

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
                    className="w-full rounded-2xl border border-slate-200/90 bg-white/90 pl-10 pr-4 py-3 text-sm font-medium text-slate-900 placeholder:text-slate-400 transition-all focus:border-apple-blue focus:outline-none focus:ring-4 focus:ring-apple-blue/10"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 rounded-2xl bg-slate-900 px-5 py-3.5 text-sm font-bold text-white shadow-md hover:bg-apple-blue transition-all disabled:opacity-50"
              >
                {loading ? 'Sending Instructions...' : 'Send Reset Link'}
                <ArrowRight size={16} />
              </button>

              <div className="text-center pt-2">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800"
                >
                  <ArrowLeft size={13} /> Back to Sign In
                </Link>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
