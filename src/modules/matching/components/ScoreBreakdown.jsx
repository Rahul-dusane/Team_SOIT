import { CheckCircle, Award, Briefcase, GraduationCap, Target, Cpu, BookOpen, Layers } from 'lucide-react'

const CATEGORY_ICONS = {
  must_have: Target,
  preferred: Award,
  experience: Briefcase,
  role: Cpu,
  semantic: Layers,
  education: GraduationCap,
  projects: BookOpen,
  domain: CheckCircle
}

export default function ScoreBreakdown({ data = [] }) {
  if (!Array.isArray(data) || !data.length) {
    return <p className="text-sm text-slate-400">Score breakdown metrics unavailable.</p>
  }

  return (
    <div className="space-y-3.5">
      {data.map(item => {
        const key = item.name.toLowerCase()
        const Icon = CATEGORY_ICONS[key] || Target
        const formattedName = item.name.replaceAll('_', ' ').toUpperCase()
        const val = typeof item.score === 'number' ? item.score : 0
        const percentage = Math.min(100, Math.max(0, val))

        const barColor =
          percentage >= 75
            ? 'bg-gradient-to-r from-apple-blue to-napkin-indigo'
            : percentage >= 40
            ? 'bg-gradient-to-r from-amber-400 to-amber-500'
            : 'bg-gradient-to-r from-rose-400 to-rose-500'

        return (
          <div key={item.name} className="group rounded-2xl border border-slate-100 bg-slate-50/60 p-3 transition-all duration-200 hover:bg-white hover:shadow-sm">
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <div className="flex h-7 w-7 items-center justify-center rounded-xl bg-white text-slate-600 shadow-sm border border-slate-200/60 group-hover:text-apple-blue">
                  <Icon size={14} />
                </div>
                <span className="text-xs font-bold text-slate-800 tracking-wide">{formattedName}</span>
              </div>
              <span className="text-xs font-extrabold text-slate-900 font-mono">{val.toFixed(1)}%</span>
            </div>

            {/* Visual Progress Bar Meter */}
            <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200/70">
              <div
                className={`h-full ${barColor} rounded-full transition-all duration-700 ease-out`}
                style={{ width: `${percentage}%` }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}
