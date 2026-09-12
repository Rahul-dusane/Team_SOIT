import { ArrowDownRight, ArrowUpRight } from 'lucide-react'

export default function StatCard({ label, value, change, icon: Icon, tone = 'blue' }) {
  const isPositive = typeof change === 'number' && change >= 0

  return (
    <div className="panel group p-6 shadow-apple-card transition-all duration-300 hover:-translate-y-1 hover:shadow-panel">
      <div className="flex items-start justify-between mb-4">
        <div
          className={`flex h-11 w-11 items-center justify-center rounded-2xl transition-transform duration-300 group-hover:scale-110 ${
            tone === 'purple'
              ? 'bg-napkin-purple/10 text-napkin-purple border border-napkin-purple/20'
              : tone === 'coral'
              ? 'bg-rose-500/10 text-rose-600 border border-rose-500/20'
              : 'bg-apple-blue/10 text-apple-blue border border-apple-blue/20'
          }`}
        >
          <Icon size={20} />
        </div>

        {typeof change === 'number' && Number.isFinite(change) && (
          <span
            className={`pill-badge ${
              isPositive
                ? 'bg-emerald-500/10 text-emerald-600 border border-emerald-500/20'
                : 'bg-rose-500/10 text-rose-600 border border-rose-500/20'
            }`}
          >
            {isPositive ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}
            {Math.abs(change)}%
          </span>
        )}
      </div>

      <p className="eyebrow tracking-wider">{label}</p>
      <p className="mt-1 text-3xl font-black tracking-tight text-slate-900">{value}</p>
    </div>
  )
}
