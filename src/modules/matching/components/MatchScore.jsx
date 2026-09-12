import { Sparkles, ShieldAlert, CheckCircle2 } from 'lucide-react'

export default function MatchScore({ score, size = 'md', decision }) {
  if (typeof score !== 'number' || !Number.isFinite(score)) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-500">
        Not Scored Yet
      </span>
    )
  }

  const roundedScore = Math.round(score)
  const isRejected = score === 0 || (decision || '').includes('REJECTED')
  const isStrong = score >= 75
  const isModerate = score >= 50 && score < 75

  // SVG Ring calculation
  const radius = size === 'lg' ? 44 : 22
  const strokeWidth = size === 'lg' ? 8 : 4
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (score / 100) * circumference

  const strokeColor = isRejected
    ? '#f43f5e'
    : isStrong
    ? '#0071e3'
    : isModerate
    ? '#f59e0b'
    : '#10b981'

  return (
    <div className="flex items-center gap-4">
      {/* Radial SVG Ring */}
      <div className="relative flex items-center justify-center">
        <svg
          className={`${size === 'lg' ? 'h-28 w-28' : 'h-14 w-14'} -rotate-90 transform`}
          viewBox="0 0 100 100"
        >
          {/* Background Ring */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            stroke="#e2e8f0"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Foreground Animated Ring */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Center Percentage Display */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span
            className={`font-black tracking-tight text-slate-900 ${
              size === 'lg' ? 'text-2xl' : 'text-xs'
            }`}
          >
            {roundedScore}%
          </span>
        </div>
      </div>

      {/* Decision Status Pill */}
      {size === 'lg' && (
        <div className="flex flex-col">
          <div className="flex items-center gap-1.5 mb-1">
            {isRejected ? (
              <span className="pill-badge bg-rose-500/10 text-rose-600 border border-rose-500/20">
                <ShieldAlert size={14} /> Mandatory Failed
              </span>
            ) : isStrong ? (
              <span className="pill-badge bg-apple-blue/10 text-apple-blue border border-apple-blue/20">
                <Sparkles size={14} /> Exceptional Fit
              </span>
            ) : (
              <span className="pill-badge bg-amber-500/10 text-amber-600 border border-amber-500/20">
                <CheckCircle2 size={14} /> Qualified Fit
              </span>
            )}
          </div>
          <span className="text-xs font-semibold text-slate-500">
            {isRejected ? 'Score set to 0% due to constraint check' : `Weighted Compatibility Index: ${score.toFixed(1)}%`}
          </span>
        </div>
      )}
    </div>
  )
}
