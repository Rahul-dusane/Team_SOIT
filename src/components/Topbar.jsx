import { Menu } from 'lucide-react'
import { Link } from 'react-router-dom'
export default function Topbar({ onMenu }) {
  return <header className="flex h-20 items-center gap-5 border-b bg-white px-5 sm:px-8"><button aria-label="Open menu" className="lg:hidden" onClick={onMenu}><Menu /></button><span className="text-sm font-bold">Hiring workspace</span><Link className="ml-auto text-sm text-teal" to="/resumes">Search candidates</Link><Link className="text-sm text-teal" to="/jobs">Browse jobs</Link></header>
}
