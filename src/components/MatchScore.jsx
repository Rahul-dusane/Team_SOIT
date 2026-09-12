export default function MatchScore({ score, size = 'md' }) {
  if (typeof score !== 'number' || !Number.isFinite(score)) return <span className="text-xs text-muted">Not scored</span>
  return <div className={`font-extrabold text-teal ${size === 'lg' ? 'text-5xl' : 'text-xl'}`}>{score}<span className="text-sm">%</span></div>
}
