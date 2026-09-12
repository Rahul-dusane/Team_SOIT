export default function AgentTimeline({ logs = [] }) {
  if (!Array.isArray(logs) || !logs.length) return <p className="text-sm text-muted">No agent execution logs available.</p>
  return <ol className="flex flex-wrap gap-3">{[...logs].sort((a,b) => a.step_index - b.step_index).map((log, i) => <li key={i} className="rounded-lg bg-canvas p-3 text-xs"><strong>{log.agent_name || 'Unnamed agent'}</strong><p>{log.status || 'Status unavailable'}{typeof log.duration_ms === 'number' ? ` · ${log.duration_ms} ms` : ''}</p></li>)}</ol>
}
