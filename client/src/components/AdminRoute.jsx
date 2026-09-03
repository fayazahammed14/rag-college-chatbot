import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { ShieldAlert, Loader2 } from 'lucide-react'

export default function AdminRoute({ children }) {
  const { user, profile, loading } = useAuthStore()
  const location = useLocation()

  if (loading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-slate-950">
        <Loader2 className="h-10 w-10 animate-spin text-indigo-500" />
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (profile?.role !== 'admin') {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-slate-950 p-6">
        <div className="glass-panel max-w-md rounded-2xl p-8 text-center shadow-2xl">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-rose-500/20 text-rose-400">
            <ShieldAlert className="h-8 w-8" />
          </div>
          <h2 className="text-xl font-bold text-slate-100">Admin Access Required</h2>
          <p className="mt-2 text-sm text-slate-400">
            This area is restricted to college administrators. Your account currently holds the <span className="font-semibold text-indigo-400">{profile?.role || 'student'}</span> role.
          </p>
          <div className="mt-6 flex justify-center gap-3">
            <a
              href="/chat"
              className="rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-md hover:bg-indigo-500 transition-all"
            >
              Go to Chat Assistant
            </a>
          </div>
        </div>
      </div>
    )
  }

  return children
}
