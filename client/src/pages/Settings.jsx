import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { profileApi } from '../services/api'
import { 
  User, 
  Mail, 
  ShieldCheck, 
  LogOut, 
  Activity, 
  Server, 
  Key, 
  Info,
  CheckCircle2,
  AlertCircle
} from 'lucide-react'

export default function Settings() {
  const navigate = useNavigate()
  const { user, profile, logout } = useAuthStore()
  const [backendHealth, setBackendHealth] = useState(null)
  const [checkingHealth, setCheckingHealth] = useState(true)

  useEffect(() => {
    const checkApi = async () => {
      try {
        const res = await profileApi.getHealth()
        setBackendHealth(res.data)
      } catch (err) {
        setBackendHealth({ status: 'error', message: 'Backend unreachable' })
      } finally {
        setCheckingHealth(false)
      }
    }
    checkApi()
  }, [])

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const isAdmin = profile?.role === 'admin'

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-950 px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">Account & Settings</h1>
          <p className="mt-1 text-sm text-slate-400">
            Manage your CampusMind AI profile and check system connectivity.
          </p>
        </div>

        {/* Profile Card */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl backdrop-blur-sm">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
            <User className="h-4 w-4 text-indigo-400" />
            Profile Information
          </h3>

          <div className="space-y-4">
            <div className="flex items-center justify-between py-3 border-b border-slate-800/80">
              <div>
                <p className="text-xs text-slate-400">Full Name</p>
                <p className="text-sm font-semibold text-slate-100 mt-0.5">
                  {profile?.name || user?.user_metadata?.name || 'User'}
                </p>
              </div>
            </div>

            <div className="flex items-center justify-between py-3 border-b border-slate-800/80">
              <div>
                <p className="text-xs text-slate-400">Email Address</p>
                <p className="text-sm font-semibold text-slate-100 mt-0.5">{user?.email}</p>
              </div>
            </div>

            <div className="flex items-center justify-between py-3 border-b border-slate-800/80">
              <div>
                <p className="text-xs text-slate-400">Access Role</p>
                <div className="mt-1">
                  <span className={`inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-semibold uppercase tracking-wider ${
                    isAdmin
                      ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                  }`}>
                    <ShieldCheck className="h-3.5 w-3.5" />
                    {profile?.role || 'student'}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between py-3">
              <div>
                <p className="text-xs text-slate-400">User ID</p>
                <p className="text-xs font-mono text-slate-400 mt-0.5">{user?.id}</p>
              </div>
            </div>
          </div>
        </div>

        {/* System & Health Status */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl backdrop-blur-sm">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
            <Server className="h-4 w-4 text-indigo-400" />
            System Status
          </h3>

          <div className="flex items-center justify-between rounded-xl bg-slate-950 p-4 border border-slate-800">
            <div className="flex items-center gap-3">
              <Activity className="h-5 w-5 text-indigo-400" />
              <div>
                <p className="text-sm font-medium text-slate-200">FastAPI & Supabase Link</p>
                <p className="text-xs text-slate-400">
                  {checkingHealth
                    ? 'Pinging backend...'
                    : backendHealth?.status === 'healthy'
                    ? 'Operational & Connected'
                    : 'Backend connection issue'}
                </p>
              </div>
            </div>

            <div>
              {checkingHealth ? (
                <span className="text-xs text-slate-400">Checking...</span>
              ) : backendHealth?.status === 'healthy' ? (
                <span className="flex items-center gap-1 text-xs font-semibold text-emerald-400">
                  <CheckCircle2 className="h-4 w-4" />
                  Online
                </span>
              ) : (
                <span className="flex items-center gap-1 text-xs font-semibold text-rose-400">
                  <AlertCircle className="h-4 w-4" />
                  Offline
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Log Out Button */}
        <div className="pt-2">
          <button
            onClick={handleLogout}
            className="flex w-full items-center justify-center gap-2 rounded-2xl border border-rose-500/20 bg-rose-500/10 py-3.5 text-sm font-semibold text-rose-400 hover:bg-rose-500/20 transition-all shadow-lg shadow-rose-900/10"
          >
            <LogOut className="h-4 w-4" />
            Sign Out of Account
          </button>
        </div>
      </div>
    </div>
  )
}
