import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'

export default function PublicRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return null
  }

  if (isAuthenticated) {
    const destination = location.state?.from?.pathname || '/'
    return <Navigate to={destination} replace />
  }

  return children
}
