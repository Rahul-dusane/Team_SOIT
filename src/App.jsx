import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './core/auth/AuthContext'
import ProtectedRoute from './core/auth/ProtectedRoute'
import PublicRoute from './core/auth/PublicRoute'
import MainLayout from './core/layouts/MainLayout'

// Auth Pages
import Login from './modules/auth/pages/Login'
import SignUp from './modules/auth/pages/SignUp'
import ForgotPassword from './modules/auth/pages/ForgotPassword'

// App Pages
import Dashboard from './modules/dashboard/pages/Dashboard'
import Resumes from './modules/candidates/pages/Resumes'
import Jobs from './modules/jobs/pages/Jobs'
import CreateJob from './modules/jobs/pages/CreateJob'
import Ranking from './modules/matching/pages/Ranking'
import MatchDetail from './modules/matching/pages/MatchDetail'
import Compare from './modules/matching/pages/Compare'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public Authentication Routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/signup"
          element={
            <PublicRoute>
              <SignUp />
            </PublicRoute>
          }
        />
        <Route
          path="/forgot-password"
          element={
            <PublicRoute>
              <ForgotPassword />
            </PublicRoute>
          }
        />

        {/* Protected Recruiter & Admin Workspace Routes */}
        <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
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
    </AuthProvider>
  )
}