import { create } from 'zustand'
import { shallow } from 'zustand/shallow'

interface GameState {
  sessionId: string | null
  caseInfo: any | null
  gameStatus: 'preparing' | 'in_progress' | 'completed' | 'failed'
  suspects: any[]
  collectedCluesCount: number
  totalCluesCount: number
  currentMode: 'investigation' | 'interrogation' | 'accuse' | 'report'
  playTime: number
  wrongGuessCount: number

  setSessionId: (id: string) => void
  setCaseInfo: (info: any) => void
  setGameStatus: (status: 'preparing' | 'in_progress' | 'completed' | 'failed') => void
  setSuspects: (suspects: any[]) => void
  updateCluesCount: (collected: number, total: number) => void
  setCurrentMode: (mode: 'investigation' | 'interrogation' | 'accuse' | 'report') => void
  incrementPlayTime: () => void
  incrementWrongGuess: () => void
  resetGame: () => void
}

export const useGameStore = create<GameState>((set) => ({
  sessionId: null,
  caseInfo: null,
  gameStatus: 'preparing',
  suspects: [],
  collectedCluesCount: 0,
  totalCluesCount: 0,
  currentMode: 'investigation',
  playTime: 0,
  wrongGuessCount: 0,

  setSessionId: (id) => {
    console.log('[gameStore] setSessionId被调用:', id)
    set({ sessionId: id })
  },
  setCaseInfo: (info) => {
    console.log('[gameStore] setCaseInfo被调用:', info)
    set({ caseInfo: info })
  },
  setGameStatus: (status) => {
    console.log('[gameStore] setGameStatus被调用:', status)
    set({ gameStatus: status })
  },
  setSuspects: (suspects) => {
    console.log('[gameStore] setSuspects被调用，数量:', suspects.length)
    set({ suspects })
  },
  updateCluesCount: (collected, total) => {
    console.log('[gameStore] updateCluesCount被调用:', { collected, total })
    set({
      collectedCluesCount: collected,
      totalCluesCount: total,
    })
  },
  setCurrentMode: (mode) => {
    console.log('[gameStore] setCurrentMode被调用:', mode)
    set({ currentMode: mode })
  },
  incrementPlayTime: () => set((state) => ({ playTime: state.playTime + 1 })),
  incrementWrongGuess: () => set((state) => ({ wrongGuessCount: state.wrongGuessCount + 1 })),
  resetGame: () => {
    console.log('[gameStore] resetGame被调用')
    set({
      sessionId: null,
      caseInfo: null,
      gameStatus: 'preparing',
      suspects: [],
      collectedCluesCount: 0,
      totalCluesCount: 0,
      currentMode: 'investigation',
      playTime: 0,
      wrongGuessCount: 0,
    })
  },
}))
