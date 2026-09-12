export default function SkillBadge({ children, type = 'recorded', onClick }) {
  const styles = {
    recorded: 'bg-slate-100/80 text-slate-700 border border-slate-200/60',
    matched: 'bg-emerald-500/10 text-emerald-700 border border-emerald-500/20 shadow-xs',
    missing: 'bg-rose-500/10 text-rose-700 border border-rose-500/20',
    transferable: 'bg-amber-500/10 text-amber-700 border border-amber-500/20'
  }

  const className = `pill-badge ${styles[type] || styles.recorded} transition-all duration-200 ${
    onClick ? 'cursor-pointer hover:scale-105 active:scale-95' : ''
  }`

  return onClick ? (
    <button type="button" className={className} onClick={onClick}>
      {children}
    </button>
  ) : (
    <span className={className}>{children}</span>
  )
}
