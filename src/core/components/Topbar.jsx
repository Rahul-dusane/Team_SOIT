import { Menu, Search, Command } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Topbar({ onMenu, onSpotlight }) {
  return (
    <header className="sticky top-0 z-30 flex h-20 items-center justify-between border-b border-slate-200/70 bg-white/70 px-6 backdrop-blur-xl sm:px-10">
      <div className="flex items-center gap-4">
        <button
          aria-label="Open menu"
          className="rounded-2xl border border-slate-200/80 p-2 text-slate-600 backdrop-blur-md hover:bg-slate-100 hover:text-slate-900 lg:hidden"
          onClick={onMenu}
        >
          <Menu size={20} />
        </button>
        <div className="hidden sm:flex flex-col">
          <h2 className="text-sm font-extrabold text-slate-900 tracking-tight">Recruitment Intelligence Cockpit</h2>
          <p className="text-[11px] text-slate-400 font-medium">Apple Monolith Architecture · 5-Agent Pipeline</p>
        </div>
      </div>

      <div className="flex items-center gap-3.5">
        {/* Apple Spotlight Search Trigger Button */}
        <button
          onClick={onSpotlight}
          className="flex items-center gap-3 rounded-full border border-slate-200/80 bg-slate-50/80 px-4 py-2 text-xs font-semibold text-slate-600 transition-all duration-200 hover:border-apple-blue/50 hover:bg-white hover:text-slate-900 hover:shadow-sm"
        >
          <Search size={14} className="text-apple-blue" />
          <span className="hidden sm:inline">Spotlight Search...</span>
          <span className="flex items-center gap-0.5 rounded-md bg-white border border-slate-200/80 px-1.5 py-0.5 text-[10px] font-bold text-slate-500 font-mono shadow-2xs">
            <Command size={9} /> K
          </span>
        </button>

        <Link
          to="/jobs"
          className="rounded-full bg-slate-900 px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all duration-200 hover:bg-apple-blue hover:shadow-glow"
        >
          View Jobs
        </Link>

        <div className="h-8 w-px bg-slate-200/70 hidden sm:block" />

        <div className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-tr from-slate-900 to-napkin-purple text-xs font-bold text-white shadow-sm">
            AI
          </span>
        </div>
      </div>
    </header>
  )
}
