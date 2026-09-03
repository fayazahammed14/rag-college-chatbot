import React from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { 
  GraduationCap, 
  MessageSquare, 
  FileText, 
  Settings, 
  LogOut, 
  ShieldCheck, 
  User
} from 'lucide-react'

export default function Navbar() {
  const { user, profile, logout } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const isAdmin = profile?.role === 'admin'

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6">
        {/* Logo & Brand */}
        <div className="flex items-center gap-6">
          <Link to="/chat" className="flex items-center gap-3 group">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 shadow-md group-hover:scale-105 transition-all">
              <GraduationCap className="h-6 w-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight text-white group-hover:text-indigo-400 transition-colors">
                  CampusMind <span className="text-indigo-500">AI</span>
                </span>
                <span className="rounded-md bg-indigo-500/10 px-2 py-0.5 text-[10px] font-semibold text-indigo-400 border border-indigo-500/20">
                  RAG
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-none">Official College Assistant</p>
            </div>
          </Link>

          {/* Navigation Links */}
          {user && (
            <nav className="hidden md:flex items-center gap-1 ml-4">
              <Link
                to="/chat"
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
                  location.pathname.startsWith('/chat')
                    ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <MessageSquare className="h-4 w-4" />
                Chat Assistant
              </Link>

              {isAdmin && (
                <Link
                  to="/admin/documents"
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
                    location.pathname.startsWith('/admin/documents')
                      ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/20'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                  }`}
                >
                  <FileText className="h-4 w-4" />
                  Knowledge Base
                </Link>
              )}
            </nav>
          )}
        </div>

        {/* User Menu / Auth actions */}
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-3">
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl glass-card">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-500/20 text-indigo-400">
                  {isAdmin ? <ShieldCheck className="h-4 w-4" /> : <User className="h-4 w-4" />}
                </div>
                <div className="text-left">
                  <p className="text-xs font-medium text-slate-200 leading-tight">
                    {profile?.name || user.email?.split('@')[0]}
                  </p>
                  <span className={`inline-block text-[10px] font-semibold uppercase tracking-wider ${
                    isAdmin ? 'text-amber-400' : 'text-indigo-400'
                  }`}>
                    {profile?.role || 'Student'}
                  </span>
                </div>
              </div>

              <Link
                to="/settings"
                title="Settings"
                className={`p-2 rounded-xl border transition-colors ${
                  location.pathname === '/settings'
                    ? 'bg-indigo-600/20 text-indigo-300 border-indigo-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border-slate-800'
                }`}
              >
                <Settings className="h-4 w-4" />
              </Link>

              <button
                onClick={handleLogout}
                title="Log Out"
                className="p-2 rounded-xl border border-slate-800 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 hover:border-rose-500/20 transition-colors"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className="px-4 py-2 text-xs font-semibold text-slate-300 hover:text-white transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 rounded-xl hover:bg-indigo-500 transition-all shadow-md shadow-indigo-600/20"
              >
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
