import { create } from 'zustand'

interface Message {
  id: string
  role: 'system' | 'user' | 'suspect' | 'judge'
  content: string
  senderId?: string
  senderName?: string
  timestamp: number
  mood?: 'calm' | 'nervous' | 'angry' | 'scared' | 'guilty'
  type: 'text' | 'system_prompt' | 'evidence' | 'accusation'
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
}

export const useDialogueStore = create<DialogueState>((set) => ({
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
}))
