import React, { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useChatStore } from '../store/chatStore'
import { 
  Plus, 
  MessageSquare, 
  Trash2, 
  Loader2, 
  MessagesSquare
} from 'lucide-react'

export default function Sidebar({ isOpen, onClose }) {
  const navigate = useNavigate()
  const { conversationId } = useParams()
  const {
    conversations,
    loadingConversations,
    fetchConversations,
    startNewChat,
    deleteConversation,
  } = useChatStore()

  useEffect(() => {
    fetchConversations()
  }, [fetchConversations])

  const handleNewChat = () => {
    startNewChat()
    navigate('/chat')
    if (onClose) onClose()
  }

  const handleSelectConv = (id) => {
    navigate(`/chat/${id}`)
    if (onClose) onClose()
  }

  const handleDeleteConv = async (e, id) => {
    e.stopPropagation()
    if (window.confirm('Delete this conversation?')) {
      await deleteConversation(id)
      if (conversationId === id) {
        navigate('/chat')
      }
    }
  }

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-30 bg-black/60 backdrop-blur-sm md:hidden"
        />
      )}

      <aside
        className={`fixed md:static inset-y-0 left-0 z-30 flex w-72 flex-col border-r border-slate-800/80 bg-slate-950/95 backdrop-blur-xl transition-transform duration-300 ease-in-out md:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* New Chat Button */}
        <div className="p-4">
          <button
            onClick={handleNewChat}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-600/25 hover:from-indigo-500 hover:to-violet-500 transition-all active:scale-[0.98]"
          >
            <Plus className="h-4 w-4" />
            New Conversation
          </button>
        </div>

        {/* History Header */}
        <div className="px-4 py-2 text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <MessagesSquare className="h-3.5 w-3.5 text-indigo-400" />
            Recent Chats
          </span>
          <span className="text-[11px] text-slate-400 font-normal">
            {conversations.length}
          </span>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          {loadingConversations ? (
            <div className="flex items-center justify-center py-8 text-slate-400">
              <Loader2 className="h-5 w-5 animate-spin text-indigo-500" />
            </div>
          ) : conversations.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-800 p-6 text-center text-slate-400">
              <MessageSquare className="mx-auto h-6 w-6 text-slate-400 mb-2" />
              <p className="text-xs">No conversations yet.</p>
              <p className="text-[11px] text-slate-400 mt-1">Start by asking a question!</p>
            </div>
          ) : (
            conversations.map((conv) => {
              const isActive = conversationId === conv.id
              return (
                <div
                  key={conv.id}
                  onClick={() => handleSelectConv(conv.id)}
                  className={`group relative flex cursor-pointer items-center justify-between rounded-xl px-3 py-2.5 text-xs transition-all ${
                    isActive
                      ? 'bg-indigo-600/15 text-indigo-300 font-medium border border-indigo-500/25'
                      : 'text-slate-300 hover:bg-slate-900 hover:text-slate-100'
                  }`}
                >
                  <div className="flex items-center gap-2.5 overflow-hidden">
                    <MessageSquare className={`h-4 w-4 shrink-0 ${isActive ? 'text-indigo-400' : 'text-slate-400 group-hover:text-slate-300'}`} />
                    <span className="truncate" title={conv.title}>
                      {conv.title || 'Untitled Conversation'}
                    </span>
                  </div>

                  <button
                    onClick={(e) => handleDeleteConv(e, conv.id)}
                    title="Delete Chat"
                    className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-all shrink-0 ml-1"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              )
            })
          )}
        </div>

        {/* Footer info */}
        <div className="border-t border-slate-900 p-3 text-center">
          <p className="text-[11px] text-slate-400">
            CampusMind RAG • Grounded in Official Docs
          </p>
        </div>
      </aside>
    </>
  )
}
