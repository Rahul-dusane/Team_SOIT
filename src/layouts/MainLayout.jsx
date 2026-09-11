import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import Topbar from '../components/Topbar'
export default function MainLayout() { const [open, setOpen] = useState(false); return <div className="flex min-h-screen bg-canvas"><Sidebar open={open} onClose={() => setOpen(false)} /><div className="flex min-w-0 flex-1 flex-col"><Topbar onMenu={() => setOpen(true)} /><main className="flex-1 p-5 sm:p-8"><Outlet /></main></div></div> }