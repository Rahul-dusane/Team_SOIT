import { Navigate, Route, Routes } from 'react-router-dom'
import MainLayout from './core/layouts/MainLayout'
import Dashboard from './modules/dashboard/pages/Dashboard'
import Resumes from './modules/candidates/pages/Resumes'
import Jobs from './modules/jobs/pages/Jobs'
import CreateJob from './modules/jobs/pages/CreateJob'
import Ranking from './modules/matching/pages/Ranking'
import MatchDetail from './modules/matching/pages/MatchDetail'
import Compare from './modules/matching/pages/Compare'

export default function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/resumes" element={<Resumes />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/jobs/create" element={<CreateJob />} />
        <Route path="/ranking" element={<Ranking />} />
        <Route path="/matches/:id" element={<MatchDetail />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}