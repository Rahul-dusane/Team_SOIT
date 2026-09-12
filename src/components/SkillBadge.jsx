export default function SkillBadge({ children, type = 'recorded', onClick }) {
  const colors = { recorded: 'bg-canvas text-muted', matched: 'bg-mint text-teal', missing: 'bg-[#fff0eb] text-coral', transferable: 'bg-[#fff6d9] text-[#a17612]' }
  const props = { className: `rounded-md px-2.5 py-1 text-[11px] font-bold ${colors[type] || colors.recorded}` }
  return onClick ? <button {...props} onClick={onClick}>{children}</button> : <span {...props}>{children}</span>
}
