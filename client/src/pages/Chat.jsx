import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useChatStore } from '../store/chatStore'
import Sidebar from '../components/Sidebar'
import ChatWindow from '../components/ChatWindow'

export default function Chat() {
  const { conversationId } = useParams()
  const { selectConversation, startNewChat } = useChatStore()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    if (conversationId) {
      selectConversation(conversationId)
    } else {
      startNewChat()
    }
  }, [conversationId, selectConversation, startNewChat])

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden bg-slate-950">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <ChatWindow onToggleSidebar={() => setSidebarOpen((prev) => !prev)} />
    </div>
  )
}
