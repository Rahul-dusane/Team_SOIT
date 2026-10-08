import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://grcihwgasjgofsrlhdox.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const isSupabaseConfigured = Boolean(
  supabaseAnonKey &&
  supabaseAnonKey !== 'your_supabase_anon_key_here' &&
  supabaseAnonKey.trim() !== ''
)

// In-memory listeners for fallback client
let fallbackListeners = []
let currentFallbackSession = null

// Restore session from localStorage if present
try {
  const saved = localStorage.getItem('hirelens_auth_session')
  if (saved) {
    currentFallbackSession = JSON.parse(saved)
  }
} catch (e) {
  console.warn('Could not restore cached auth session:', e)
}

function notifyFallbackListeners(event, session) {
  fallbackListeners.forEach((callback) => {
    try {
      callback(event, session)
    } catch (err) {
      console.error('Auth state listener error:', err)
    }
  })
}

// Fallback client mirroring Supabase Auth API
const fallbackSupabaseClient = {
  auth: {
    async getSession() {
      return { data: { session: currentFallbackSession }, error: null }
    },
    async getUser() {
      return { data: { user: currentFallbackSession?.user || null }, error: null }
    },
    async signInWithPassword({ email, password }) {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
        const response = await fetch(`${apiUrl}/auth/signin`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        })
        const data = await response.json()
        if (!response.ok) {
          return { data: { user: null, session: null }, error: { message: data.detail || 'Sign-in failed' } }
        }
        const session = {
          access_token: data.access_token,
          token_type: data.token_type,
          user: {
            id: data.user.id,
            email: data.user.email,
            user_metadata: {
              full_name: data.user.full_name,
              role: data.user.role
            }
          }
        }
        currentFallbackSession = session
        localStorage.setItem('hirelens_auth_session', JSON.stringify(session))
        notifyFallbackListeners('SIGNED_IN', session)
        return { data: { user: session.user, session }, error: null }
      } catch (err) {
        return { data: { user: null, session: null }, error: { message: err.message || 'Network error connecting to backend auth' } }
      }
    },
    async signUp({ email, password, options = {} }) {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
        const fullName = options.data?.full_name || ''
        const role = options.data?.role || 'recruiter'
        const response = await fetch(`${apiUrl}/auth/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, full_name: fullName, role })
        })
        const data = await response.json()
        if (!response.ok) {
          return { data: { user: null, session: null }, error: { message: data.detail || 'Sign-up failed' } }
        }
        const session = {
          access_token: data.access_token,
          token_type: data.token_type,
          user: {
            id: data.user.id,
            email: data.user.email,
            user_metadata: {
              full_name: data.user.full_name,
              role: data.user.role
            }
          }
        }
        currentFallbackSession = session
        localStorage.setItem('hirelens_auth_session', JSON.stringify(session))
        notifyFallbackListeners('SIGNED_IN', session)
        return { data: { user: session.user, session }, error: null }
      } catch (err) {
        return { data: { user: null, session: null }, error: { message: err.message || 'Network error connecting to backend auth' } }
      }
    },
    async signOut() {
      currentFallbackSession = null
      localStorage.removeItem('hirelens_auth_session')
      notifyFallbackListeners('SIGNED_OUT', null)
      return { error: null }
    },
    async resetPasswordForEmail(email) {
      return {
        data: {},
        error: null
      }
    },
    onAuthStateChange(callback) {
      fallbackListeners.push(callback)
      // Invoke immediately with current session
      callback(currentFallbackSession ? 'INITIAL_SESSION' : 'SIGNED_OUT', currentFallbackSession)
      return {
        data: {
          subscription: {
            unsubscribe: () => {
              fallbackListeners = fallbackListeners.filter((cb) => cb !== callback)
            }
          }
        }
      }
    }
  }
}

// Export official Supabase client if configured, otherwise smart proxy client
export const supabase = isSupabaseConfigured
  ? createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true
      }
    })
  : fallbackSupabaseClient

export default supabase
