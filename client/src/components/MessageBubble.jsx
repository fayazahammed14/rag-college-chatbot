import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { GraduationCap, User, Copy, Check, Sparkles, BookOpen } from 'lucide-react'
import SourceChip from './SourceChip'

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const hasSources = message.sources && message.sources.length > 0

  return (
    <div className={`py-5 px-4 sm:px-6 transition-colors ${
      isUser ? 'bg-transparent' : 'bg-slate-900/40 border-y border-slate-800/40'
    }`}>
      <div className="mx-auto flex max-w-3xl gap-4 md:gap-5">
        {/* Avatar */}
        <div className="shrink-0">
          {isUser ? (
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-slate-800 text-slate-300 shadow">
              <User className="h-4 w-4" />
            </div>
          ) : (
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 text-white shadow-md shadow-indigo-600/20">
              <GraduationCap className="h-4 w-4" />
            </div>
          )}
        </div>

        {/* Content Body */}
        <div className="min-w-0 flex-1 space-y-2">
          {/* Header Role & Action */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-200">
                {isUser ? 'You' : 'CampusMind AI'}
              </span>
              {!isUser && (
                <span className="flex items-center gap-1 text-[10px] text-indigo-400 font-medium">
                  <Sparkles className="h-2.5 w-2.5" />
                  Verified RAG
                </span>
              )}
            </div>

            {!isUser && (
              <button
                onClick={handleCopy}
                title="Copy response"
                className="flex items-center gap-1 rounded-md px-2 py-0.5 text-[11px] text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors"
              >
                {copied ? (
                  <>
                    <Check className="h-3 w-3 text-emerald-400" />
                    <span className="text-emerald-400">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3 w-3" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            )}
          </div>

          {/* Markdown Message Text */}
          <div className="prose prose-invert prose-sm max-w-none text-slate-200 leading-relaxed break-words">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>

          {/* Source Citations */}
          {hasSources && (
            <div className="mt-4 pt-3 border-t border-slate-800/80">
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-400 mb-2">
                <BookOpen className="h-3.5 w-3.5 text-indigo-400" />
                <span>Referenced Official Sources ({message.sources.length}):</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {message.sources.map((src, i) => (
                  <SourceChip key={i} source={src} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
