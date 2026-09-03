import React from 'react'
import DocumentTable from '../components/DocumentTable'
import { ShieldCheck, BookOpen, Sparkles } from 'lucide-react'

export default function AdminDocuments() {
  return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-950 px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl space-y-8">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="flex items-center gap-1 rounded-md bg-amber-500/10 px-2.5 py-0.5 text-xs font-semibold text-amber-400 border border-amber-500/20">
                <ShieldCheck className="h-3.5 w-3.5" />
                Admin Portal
              </span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
              College Knowledge Base
            </h1>
            <p className="mt-1 text-sm text-slate-400">
              Manage official college publications, handbooks, notices, and exam timetables indexed for RAG.
            </p>
          </div>

          <div className="flex items-center gap-3 rounded-2xl glass-card px-4 py-3 border border-slate-800">
            <Sparkles className="h-5 w-5 text-indigo-400 shrink-0" />
            <div className="text-xs text-slate-300">
              <p className="font-semibold text-slate-200">Gemini 2.0 Flash + pgvector</p>
              <p className="text-slate-400">Vector Embeddings (768-dim)</p>
            </div>
          </div>
        </div>

        {/* Document Table Component */}
        <DocumentTable />
      </div>
    </div>
  )
}
