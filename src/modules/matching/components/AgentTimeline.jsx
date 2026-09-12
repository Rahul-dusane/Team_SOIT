import { useState } from 'react'
import { CheckCircle2, Clock, Cpu, ChevronDown, ChevronUp, Sparkles, ArrowRight } from 'lucide-react'

export default function AgentTimeline({ logs = [] }) {
  const [expanded, setExpanded] = useState(null)

  if (!Array.isArray(logs) || !logs.length) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50/50 p-6 text-center">
        <Cpu size={24} className="mx-auto mb-2 text-slate-400" />
        <p className="text-sm font-medium text-slate-600">No agent execution logs recorded yet.</p>
        <p className="text-xs text-slate-400">Run the Match Engine to trigger the 5-agent LangGraph workflow.</p>
      </div>
    )
  }

  const sortedLogs = [...logs].sort((a, b) => (a.step_index ?? 0) - (b.step_index ?? 0))

  return (
    <div className="space-y-4">
      {/* Pipeline Visual Flow Ribbon */}
      <div className="relative flex flex-wrap items-center gap-3 overflow-x-auto pb-2">
        {sortedLogs.map((log, index) => {
          const isSelected = expanded === index
          const isSuccess = (log.status || '').toLowerCase().includes('success') || (log.status || '').toLowerCase().includes('completed')
          return (
            <div key={index} className="flex items-center gap-3">
              <button
                onClick={() => setExpanded(isSelected ? null : index)}
                className={`group relative flex items-center gap-3 rounded-2xl border p-3.5 text-left transition-all duration-200 ${
                  isSelected
                    ? 'border-napkin-purple bg-gradient-to-r from-napkin-purple/10 to-apple-blue/10 shadow-glow-purple ring-2 ring-napkin-purple/30'
                    : 'border-slate-200/80 bg-white hover:border-slate-300 hover:shadow-md'
                }`}
              >
                <div
                  className={`flex h-8 w-8 items-center justify-center rounded-xl font-bold text-xs ${
                    isSuccess
                      ? 'bg-emerald-500/10 text-emerald-600 border border-emerald-500/20'
                      : 'bg-napkin-purple/10 text-napkin-purple border border-napkin-purple/20'
                  }`}
                >
                  {log.step_index ?? index + 1}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-extrabold text-slate-900">{log.agent_name || 'Agent'}</span>
                    {log.duration_ms != null && (
                      <span className="flex items-center gap-1 rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-500">
                        <Clock size={10} />
                        {log.duration_ms}ms
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-slate-400 capitalize">{log.status || 'Success'}</p>
                </div>
                <div className="ml-2 text-slate-400 group-hover:text-slate-600">
                  {isSelected ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </div>
              </button>
              {index < sortedLogs.length - 1 && (
                <ArrowRight size={16} className="text-slate-300 hidden sm:block" />
              )}
            </div>
          )
        })}
      </div>

      {/* Expanded Details Drawer */}
      {expanded !== null && sortedLogs[expanded] && (
        <div className="rounded-2xl border border-napkin-purple/20 bg-gradient-to-br from-slate-900 to-slate-800 p-5 text-white shadow-xl animate-fade-in">
          <div className="flex items-center justify-between border-b border-slate-700/60 pb-3 mb-3">
            <div className="flex items-center gap-2.5">
              <Sparkles size={16} className="text-napkin-cyan animate-pulse" />
              <h4 className="text-sm font-bold text-white">
                Step {sortedLogs[expanded].step_index ?? expanded + 1}: {sortedLogs[expanded].agent_name}
              </h4>
            </div>
            <span className="pill-badge bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              <CheckCircle2 size={12} /> Executed Cleanly
            </span>
          </div>

          <div className="grid gap-4 text-xs sm:grid-cols-2">
            {sortedLogs[expanded].input_summary && (
              <div className="rounded-xl bg-slate-800/80 p-3 border border-slate-700/50">
                <span className="eyebrow text-slate-400 mb-1 block">Agent Input Context</span>
                <p className="text-slate-300 leading-relaxed font-mono text-[11px]">
                  {sortedLogs[expanded].input_summary}
                </p>
              </div>
            )}
            {sortedLogs[expanded].output_summary && (
              <div className="rounded-xl bg-slate-800/80 p-3 border border-slate-700/50">
                <span className="eyebrow text-slate-400 mb-1 block">Synthesized Output / Action</span>
                <p className="text-slate-300 leading-relaxed font-mono text-[11px]">
                  {sortedLogs[expanded].output_summary}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
