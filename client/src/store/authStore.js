import { create } from 'zustand'
import { supabase } from '../services/supabaseClient'
import { profileApi } from '../services/api'

export const useAuthStore = create((set, get) => ({
  user: null,
  profile: null,
  session: null,
  loading: true,
  error: null,

  initialize: async () => {
    try {
      set({ loading: true })
      const { data: { session } } = await supabase.auth.getSession()

      if (session?.user) {
        set({ session, user: session.user })
        try {
          const res = await profileApi.getMe()
          set({ profile: res.data })
        } catch (err) {
          // If backend profile fetch fails, use auth user metadata
          set({
            profile: {
              id: session.user.id,
              name: session.user.user_metadata?.name || session.user.email?.split('@')[0],
              role: session.user.user_metadata?.role || 'student',
              email: session.user.email,
            }
          })
        }
      } else {
        set({ session: null, user: null, profile: null })
      }

      // Listen to auth changes
      supabase.auth.onAuthStateChange(async (event, currentSession) => {
        if (currentSession?.user) {
          set({ session: currentSession, user: currentSession.user })
          try {
            const res = await profileApi.getMe()
            set({ profile: res.data })
          } catch (e) {
            set({
              profile: {
                id: currentSession.user.id,
                name: currentSession.user.user_metadata?.name || currentSession.user.email?.split('@')[0],
                role: currentSession.user.user_metadata?.role || 'student',
                email: currentSession.user.email,
              }
            })
          }
        } else {
          set({ session: null, user: null, profile: null })
        }
      })
    } catch (err) {
      console.error('Error initializing auth store:', err)
      set({ error: err.message })
    } finally {
      set({ loading: false })
    }
  },

  login: async (email, password) => {
    set({ loading: true, error: null })
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) throw error

      set({ session: data.session, user: data.user })
      try {
        const res = await profileApi.getMe()
        set({ profile: res.data })
      } catch (e) {
        set({
          profile: {
            id: data.user.id,
            name: data.user.user_metadata?.name || data.user.email?.split('@')[0],
            role: data.user.user_metadata?.role || 'student',
            email: data.user.email,
          }
        })
      }
      return { success: true }
    } catch (err) {
      set({ error: err.message })
      return { success: false, error: err.message }
    } finally {
      set({ loading: false })
    }
  },

  signup: async (email, password, name, role = 'student') => {
    set({ loading: true, error: null })
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { name, role },
        },
      })
      if (error) throw error

      // If session is immediately returned (email confirmation disabled in Supabase)
      if (data.session) {
        set({ session: data.session, user: data.user })
        try {
          const res = await profileApi.getMe()
          set({ profile: res.data })
        } catch (e) {
          set({
            profile: {
              id: data.user.id,
              name: name || email.split('@')[0],
              role: role,
              email: email,
            }
          })
        }
      }
      return { success: true, data }
    } catch (err) {
      set({ error: err.message })
      return { success: false, error: err.message }
    } finally {
      set({ loading: false })
    }
  },

  logout: async () => {
    try {
      await supabase.auth.signOut()
      set({ user: null, profile: null, session: null, error: null })
    } catch (err) {
      console.error('Logout error:', err)
    }
  },
}))
