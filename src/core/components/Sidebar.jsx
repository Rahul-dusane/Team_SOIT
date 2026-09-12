import { NavLink } from 'react-router-dom'
import { BarChart3, BriefcaseBusiness, ChevronLeft, FileText, GitCompare, LayoutDashboard, Plus, Sparkles } from 'lucide-react'

const mainLinks = [
  { to: '/', label: 'Overview', icon: LayoutDashboard },
  { to: '/resumes', label: 'Candidate Pool', icon: FileText },
  { to: '/jobs', label: 'Active Jobs', icon: BriefcaseBusiness },
  { to: '/ranking', label: 'Leaderboard', icon: BarChart3 },
  { to: '/compare', label: 'Compare Engine', icon: GitCompare }
]

export default function Sidebar({ open, onClose }) {
  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-slate-200/70 bg-white/80 p-6 backdrop-blur-2xl transition-all duration-300 lg:static lg:translate-x-0 ${
        open ? 'translate-x-0 shadow-2xl' : '-translate-x-full'
      }`}
    >
      {/* Brand Header */}
      <div className="mb-8 flex items-center justify-between">
        <NavLink to="/" className="group flex items-center gap-3 text-lg font-bold tracking-tight text-slate-900">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-tr from-slate-900 via-napkin-indigo to-apple-blue shadow-glow text-white transition-transform duration-300 group-hover:scale-105">
            <Sparkles size={20} className="animate-pulse" />
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold text-slate-900 tracking-tight text-lg leading-none">Hire<span className="text-apple-blue">Lens</span></span>
            <span className="text-[10px] font-medium text-slate-400 tracking-wide uppercase mt-0.5">Modular Monolith</span>
          </div>
        </NavLink>
        <button
          className="rounded-full p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700 lg:hidden"
          onClick={onClose}
          aria-label="Close Sidebar"
        >
          <ChevronLeft size={20} />
        </button>
      </div>

      {/* Workspace Menu */}
      <div className="flex-1 space-y-6">
        <div>
          <p className="eyebrow mb-2.5 px-3">Workspace</p>
          <nav className="space-y-1.5">
            {mainLinks.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                onClick={onClose}
                className={({ isActive }) =>
                  `group relative flex items-center gap-3.5 rounded-2xl px-3.5 py-3 text-sm font-semibold transition-all duration-200 ${
                    isActive
                      ? 'bg-slate-900 text-white shadow-md shadow-slate-900/10'
                      : 'text-slate-600 hover:bg-slate-100/80 hover:text-slate-900'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon
                      size={19}
                      className={`transition-transform duration-200 group-hover:scale-110 ${
                        isActive ? 'text-apple-blue' : 'text-slate-400 group-hover:text-slate-700'
                      }`}
                    />
                    <span>{label}</span>
                    {isActive && (
                      <span className="ml-auto h-2 w-2 rounded-full bg-apple-blue shadow-glow" />
                    )}
                  </>
                )}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Action Section */}
        <div className="pt-4 border-t border-slate-200/60">
          <p className="eyebrow mb-2.5 px-3">Quick Actions</p>
          <NavLink
            to="/jobs/create"
            onClick={onClose}
            className="flex items-center gap-3.5 rounded-2xl border border-slate-200/80 bg-slate-50/80 px-3.5 py-3 text-sm font-semibold text-slate-700 backdrop-blur-sm transition-all duration-200 hover:border-apple-blue/40 hover:bg-apple-blue/5 hover:text-apple-blue"
          >
            <Plus size={19} className="text-apple-blue" />
            <span>Create New Job</span>
          </NavLink>
        </div>
      </div>

      {/* Footer System Status Card */}
      <div className="mt-auto rounded-2xl border border-slate-200/70 bg-gradient-to-b from-slate-50/80 to-slate-100/50 p-3.5 backdrop-blur-md">
        <div className="flex items-center gap-2.5 mb-1.5">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-bold text-slate-800">5 LangGraph Agents Active</span>
        </div>
        <p className="text-[11px] text-slate-500 leading-tight">Modular Monolith Architecture</p>
      </div>
    </aside>
  )
}
