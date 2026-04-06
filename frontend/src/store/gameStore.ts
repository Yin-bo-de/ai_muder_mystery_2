import { create } from 'zustand'

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

  setSessionId: (id) => set({ sessionId: id }),
  setCaseInfo: (info) => set({ caseInfo: info }),
  setGameStatus: (status) => set({ gameStatus: status }),
  setSuspects: (suspects) => set({ suspects }),
  updateCluesCount: (collected, total) => set({
    collectedCluesCount: collected,
    totalCluesCount: total,
  }),
  setCurrentMode: (mode) => set({ currentMode: mode }),
  incrementPlayTime: () => set((state) => ({ playTime: state.playTime + 1 })),
  incrementWrongGuess: () => set((state) => ({ wrongGuessCount: state.wrongGuessCount + 1 })),
  resetGame: () => set({
    sessionId: null,
    caseInfo: null,
    gameStatus: 'preparing',
    suspects: [],
    collectedCluesCount: 0,
    totalCluesCount: 0,
    currentMode: 'investigation',
    playTime: 0,
    wrongGuessCount: 0,
  }),
}))
