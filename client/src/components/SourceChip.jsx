import React from 'react'
import { FileText, Bookmark } from 'lucide-react'

export default function SourceChip({ source }) {
  const { document_title, page_number, similarity } = source

  return (
    <div
      className="inline-flex items-center gap-1.5 rounded-lg border border-indigo-500/20 bg-indigo-950/40 px-2.5 py-1 text-[11px] font-medium text-indigo-300 shadow-sm hover:border-indigo-500/40 hover:bg-indigo-900/40 transition-all cursor-default"
      title={`Source: ${document_title} (Page ${page_number})${similarity ? ` • ${Math.round(similarity * 100)}% match` : ''}`}
    >
      <FileText className="h-3 w-3 text-indigo-400 shrink-0" />
      <span className="max-w-[180px] truncate">{document_title}</span>
      <span className="flex items-center gap-0.5 rounded bg-indigo-500/20 px-1 py-0.2 text-[10px] text-indigo-200">
        <Bookmark className="h-2.5 w-2.5" />
        p.{page_number}
      </span>
    </div>
  )
}
