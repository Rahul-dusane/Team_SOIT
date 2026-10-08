import { createContext, useContext, useEffect, useState, useMemo } from 'react'
import { supabase, isSupabaseConfigured } from './supabaseClient'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null)
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Format user profile from Supabase user object
  const formatUser = (supabaseUser) => {
    if (!supabaseUser) return null
    const meta = supabaseUser.user_metadata || {}
    return {
      id: supabaseUser.id,
      email: supabaseUser.email,
      fullName: meta.full_name || meta.name || supabaseUser.email?.split('@')[0] || 'User',
      role: meta.role || 'recruiter',
      avatarUrl: meta.avatar_url || null,
      createdAt: supabaseUser.created_at,
      metadata: meta
    }
  }

  useEffect(() => {
    let mounted = true

    // 1. Check existing session on mount
    supabase.auth.getSession().then(({ data: { session: initialSession }, error }) => {
      if (error) {
        console.warn('Error fetching initial auth session:', error)
      }
      if (mounted) {
        setSession(initialSession)
        setUser(initialSession ? formatUser(initialSession.user) : null)
        setLoading(false)
      }
    }).catch(err => {
      console.error('Failed to get session:', err)
      if (mounted) setLoading(false)
    })

    // 2. Listen to real-time auth changes (sign in, sign out, token refresh)
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, currentSession) => {
      if (!mounted) return
      setSession(currentSession)
      setUser(currentSession ? formatUser(currentSession.user) : null)
      setLoading(false)
    })

    return () => {
      mounted = false
      if (subscription && typeof subscription.unsubscribe === 'function') {
        subscription.unsubscribe()
      }
    }
  }, [])

  // Sign In with email & password
  const signIn = async ({ email, password }) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: email.trim(),
      password
    })
    if (error) throw error
    return data
  }

  // Sign Up with email, password, full name, and role
  const signUp = async ({ email, password, fullName, role = 'recruiter' }) => {
    const { data, error } = await supabase.auth.signUp({
      email: email.trim(),
      password,
      options: {
        data: {
          full_name: fullName,
          role
        }
      }
    })
    if (error) throw error
    return data
  }

  // Sign Out
  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    setSession(null)
    setUser(null)
  }

  // Password reset request
  const resetPassword = async (email) => {
    const { data, error } = await supabase.auth.resetPasswordForEmail(email.trim(), {
      redirectTo: `${window.location.origin}/reset-password`
    })
    if (error) throw error
    return data
  }

  const value = useMemo(() => ({
    session,
    user,
    loading,
    isAuthenticated: Boolean(session && user),
    isSupabaseLive: isSupabaseConfigured,
    signIn,
    signUp,
    signOut,
    resetPassword,
  }), [session, user, loading])

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
