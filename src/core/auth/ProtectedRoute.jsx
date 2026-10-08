import { Navigate, useLocation, Outlet } from 'react-router-dom'
import { useAuth } from './AuthContext'
import { Sparkles, ShieldAlert } from 'lucide-react'

export default function ProtectedRoute({ children, allowedRoles }) {
  const { user, isAuthenticated, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50/70 mesh-bg">
        <div className="flex flex-col items-center gap-4 p-8 rounded-3xl bg-white/80 border border-slate-200/80 shadow-2xl backdrop-blur-xl">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-slate-900 to-apple-blue shadow-glow text-white animate-spin">
            <Sparkles size={24} />
          </div>
          <div className="text-center">
            <h3 className="text-sm font-bold text-slate-800">Authenticating Session</h3>
            <p className="text-xs text-slate-500 mt-1">Connecting to HireLens Intelligence Gateway...</p>
          </div>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (allowedRoles && allowedRoles.length > 0 && !allowedRoles.includes(user?.role) && user?.role !== 'admin') {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center p-6 text-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-rose-50 border border-rose-200 text-rose-500 mb-4 shadow-sm">
          <ShieldAlert size={32} />
        </div>
        <h2 className="text-xl font-bold text-slate-900">Access Restricted</h2>
        <p className="text-sm text-slate-500 max-w-md mt-2">
          Your account role (<span className="font-semibold text-slate-700">{user?.role}</span>) does not possess administrative privileges required for this module.
        </p>
      </div>
    )
  }

  return children ? children : <Outlet />
}
