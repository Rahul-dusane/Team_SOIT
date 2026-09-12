export default function ScoreBreakdown({ data = [] }) {
  if (!data.length) return <p className="text-sm text-muted">Score breakdown unavailable.</p>
  return <div className="space-y-3"><p className="text-xs text-muted">Raw weighted contributions before final scoring rules.</p>{data.map(item => <div key={item.name} className="flex justify-between border-b py-2 text-sm"><span>{item.name.replaceAll('_', ' ')}</span><span>{item.score} points</span></div>)}</div>
}
