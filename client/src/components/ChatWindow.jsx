import React, { useState, useRef, useEffect } from 'react'
import { useChatStore } from '../store/chatStore'
import MessageBubble from './MessageBubble'
import { 
  Send, 
  Loader2, 
  Sparkles, 
  Menu, 
  HelpCircle, 
  Award, 
  Calendar, 
  Building2,
  AlertCircle
} from 'lucide-react'

const SUGGESTED_QUESTIONS = [
  { icon: Award, text: "What are the eligibility criteria for merit scholarships?" },
  { icon: Calendar, text: "When do mid-term and final semester examinations start?" },
  { icon: Building2, text: "What are the rules, fees, and curfew timings for the hostel?" },
  { icon: HelpCircle, text: "What is the procedure and deadline for course registration?" },
]

export default function ChatWindow({ onToggleSidebar }) {
  const {
    messages,
    isAsking,
    error,
    sendMessage,
  } = useChatStore()

  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isAsking])

  const handleSubmit = async (e) => {
    e?.preventDefault()
    if (!input.trim() || isAsking) return

    const question = input.trim()
    setInput('')
    await sendMessage(question)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleSuggestedClick = (text) => {
    setInput(text)
    inputRef.current?.focus()
  }

  return (
    <div className="flex h-full flex-1 flex-col bg-slate-950">
      {/* Mobile Header Bar */}
      <div className="flex items-center justify-between border-b border-slate-800/80 px-4 py-3 md:hidden">
        <button
          onClick={onToggleSidebar}
          className="rounded-lg p-2 text-slate-400 hover:bg-slate-900 hover:text-white"
        >
          <Menu className="h-5 w-5" />
        </button>
        <span className="text-sm font-semibold text-slate-200">CampusMind AI</span>
        <div className="w-8" />
      </div>

      {/* Messages Stream or Empty State */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center px-4 text-center">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-500 text-white shadow-xl shadow-indigo-600/30 mb-5">
              <Sparkles className="h-8 w-8 animate-pulse" />
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
              Ask CampusMind AI
            </h2>
            <p className="mt-2 max-w-md text-sm text-slate-400">
              Your official college companion. Inquire about admissions, fees, hostel, exams, placement records, and campus policies.
            </p>

            {/* Suggested Prompts Grid */}
            <div className="mt-8 grid w-full max-w-2xl grid-cols-1 gap-3 sm:grid-cols-2 text-left">
              {SUGGESTED_QUESTIONS.map((item, idx) => {
                const Icon = item.icon
                return (
                  <button
                    key={idx}
                    onClick={() => handleSuggestedClick(item.text)}
                    className="flex items-start gap-3 rounded-xl border border-slate-800/80 bg-slate-900/50 p-3.5 text-xs text-slate-300 transition-all hover:border-indigo-500/40 hover:bg-indigo-950/20 hover:text-white"
                  >
                    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400">
                      <Icon className="h-4 w-4" />
                    </div>
                    <span className="leading-snug">{item.text}</span>
                  </button>
                )
              })}
            </div>
          </div>
        ) : (
          <div className="pb-4">
            {messages.map((msg, index) => (
              <MessageBubble key={msg.id || index} message={msg} />
            ))}

            {/* Loading / Thinking Bubble */}
            {isAsking && (
              <div className="py-5 px-4 sm:px-6 bg-slate-900/40 border-y border-slate-800/40">
                <div className="mx-auto flex max-w-3xl gap-4 md:gap-5">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 text-white shadow-md">
                    <Loader2 className="h-4 w-4 animate-spin" />
                  </div>
                  <div className="flex items-center gap-2 text-xs text-indigo-400">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
                    </span>
                    <span>Retrieving official documents and synthesizing answer...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Error alert if any */}
      {error && (
        <div className="mx-auto max-w-3xl px-4 py-2 w-full">
          <div className="flex items-center gap-2 rounded-xl bg-rose-500/10 border border-rose-500/20 p-3 text-xs text-rose-400">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Input Box Area */}
      <div className="border-t border-slate-800/80 bg-slate-950/80 p-4 backdrop-blur-md">
        <div className="mx-auto max-w-3xl">
          <form onSubmit={handleSubmit} className="relative flex items-center">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about the college (e.g. exams, hostel, fees, syllabus)..."
              disabled={isAsking}
              className="w-full rounded-2xl border border-slate-700/80 bg-slate-900/90 py-3.5 pl-4 pr-12 text-sm text-slate-100 placeholder-slate-500 shadow-inner focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!input.trim() || isAsking}
              className="absolute right-2 flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-md transition-all hover:bg-indigo-500 disabled:opacity-30 disabled:hover:bg-indigo-600"
            >
              {isAsking ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </button>
          </form>
          <p className="mt-2 text-center text-[11px] text-slate-500">
            CampusMind AI answers are strictly grounded in uploaded official college documents.
          </p>
        </div>
      </div>
    </div>
  )
}
