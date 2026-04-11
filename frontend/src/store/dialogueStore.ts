import { create } from 'zustand'

interface Message {
  id: string
  role: 'system' | 'user' | 'suspect' | 'judge'
  content: string
  sender_id?: string
  sender_name?: string
  timestamp: number
  mood?: 'calm' | 'nervous' | 'angry' | 'scared' | 'guilty'
  type: 'text' | 'system_prompt' | 'evidence' | 'accusation'
  dialogueMode: 'single' | 'group'
  suspectId?: string
}

interface DialogueState {
  messages: Message[]
  dialogueMode: 'single' | 'group'
  currentSuspectId: string | null
  isSending: boolean
  systemPrompts: string[]

  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void
  setMessages: (messages: Message[]) => void
  setDialogueMode: (mode: 'single' | 'group', suspectId?: string) => void
  setIsSending: (sending: boolean) => void
  addSystemPrompt: (prompt: string) => void
  clearMessages: () => void
  resetDialogue: () => void
  getFilteredMessages: (mode: 'single' | 'group', suspectId?: string | null) => Message[]
}

export const useDialogueStore = create<DialogueState>((set, get) => ({
  messages: [],
  dialogueMode: 'group',
  currentSuspectId: null,
  isSending: false,
  systemPrompts: [],

  addMessage: (message) => set((state) => ({
    messages: [
      ...state.messages,
      {
        ...message,
        id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: Date.now(),
        dialogueMode: message.dialogueMode || state.dialogueMode,
        suspectId: message.suspectId || state.currentSuspectId,
      },
    ],
  })),
  setMessages: (messages) => set({ messages }),
  setDialogueMode: (mode, suspectId = null) => set({
    dialogueMode: mode,
    currentSuspectId: suspectId,
  }),
  setIsSending: (sending) => set({ isSending: sending }),
  addSystemPrompt: (prompt) => set((state) => ({
    systemPrompts: [...state.systemPrompts, prompt],
  })),
  clearMessages: () => set({ messages: [] }),
  resetDialogue: () => set({
    messages: [],
    dialogueMode: 'group',
    currentSuspectId: null,
    isSending: false,
    systemPrompts: [],
  }),
  getFilteredMessages: (mode: 'single' | 'group', suspectId?: string | null) => {
    const state = get()
    return state.messages.filter(msg => {
      // 首先按对话模式过滤
      if (msg.dialogueMode !== mode) return false

      // 单独审讯模式：只显示当前审讯角色的对话 + 用户消息 + 系统消息
      if (mode === 'single' && suspectId) {
        // 如果是用户或系统消息，直接显示
        if (msg.role === 'user' || msg.role === 'system') {
          // 确保这条用户/系统消息属于当前这个嫌疑人的单独审讯
          return msg.suspectId === suspectId
        }
        // 如果是嫌疑人消息，只显示当前审讯角色的消息
        return msg.suspectId === suspectId
      }

      // 全体质询模式：显示所有全体模式的消息
      return true
    })
  },
}))
