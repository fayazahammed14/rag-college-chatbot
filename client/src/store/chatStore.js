import { create } from 'zustand'
import { chatApi } from '../services/api'

export const useChatStore = create((set, get) => ({
  conversations: [],
  currentConversationId: null,
  messages: [],
  isAsking: false,
  loadingConversations: false,
  loadingMessages: false,
  error: null,

  fetchConversations: async () => {
    try {
      set({ loadingConversations: true, error: null })
      const res = await chatApi.getConversations()
      set({ conversations: res.data })
    } catch (err) {
      console.error('Error fetching conversations:', err)
      set({ error: 'Failed to load conversations' })
    } finally {
      set({ loadingConversations: false })
    }
  },

  selectConversation: async (conversationId) => {
    if (!conversationId) {
      set({ currentConversationId: null, messages: [] })
      return
    }

    try {
      set({ currentConversationId: conversationId, loadingMessages: true, error: null })
      const res = await chatApi.getConversation(conversationId)
      set({ messages: res.data.messages || [] })
    } catch (err) {
      console.error('Error loading conversation:', err)
      set({ error: 'Failed to load messages for conversation' })
    } finally {
      set({ loadingMessages: false })
    }
  },

  startNewChat: () => {
    set({ currentConversationId: null, messages: [], error: null })
  },

  sendMessage: async (question) => {
    const { currentConversationId, messages, conversations } = get()
    if (!question || !question.trim()) return

    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: question,
      sources: [],
      created_at: new Date().toISOString(),
    }

    // Optimistically update message list
    set({
      messages: [...messages, tempUserMsg],
      isAsking: true,
      error: null,
    })

    try {
      const res = await chatApi.ask({
        conversationId: currentConversationId || undefined,
        question: question.trim(),
      })

      const { answer, sources, conversationId } = res.data

      const assistantMsg = {
        id: `asst-${Date.now()}`,
        role: 'assistant',
        content: answer,
        sources: sources || [],
        created_at: new Date().toISOString(),
      }

      set((state) => ({
        currentConversationId: conversationId,
        messages: [...state.messages.filter(m => m.id !== tempUserMsg.id), tempUserMsg, assistantMsg],
        isAsking: false,
      }))

      // Refresh conversations list to update titles/ordering
      get().fetchConversations()

      return conversationId
    } catch (err) {
      console.error('Error sending message:', err)
      const errorMsg = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: "Sorry, I encountered an error answering your question. Please ensure the backend and Gemini API are connected.",
        sources: [],
        created_at: new Date().toISOString(),
      }
      set((state) => ({
        messages: [...state.messages, errorMsg],
        isAsking: false,
        error: err.response?.data?.detail || err.message,
      }))
    }
  },

  deleteConversation: async (conversationId) => {
    try {
      await chatApi.deleteConversation(conversationId)
      set((state) => {
        const remaining = state.conversations.filter((c) => c.id !== conversationId)
        const isCurrent = state.currentConversationId === conversationId
        return {
          conversations: remaining,
          currentConversationId: isCurrent ? null : state.currentConversationId,
          messages: isCurrent ? [] : state.messages,
        }
      })
    } catch (err) {
      console.error('Error deleting conversation:', err)
      set({ error: 'Failed to delete conversation' })
    }
  },
}))
