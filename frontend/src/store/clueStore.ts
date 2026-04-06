import { create } from 'zustand'

interface Clue {
  id: string
  name: string
  description: string
  type: 'physical' | 'testimony' | 'association' | 'decrypted'
  status: 'undiscovered' | 'discovered' | 'decrypted' | 'associated'
  scene: string
  relatedSuspects: string[]
  unlockCondition?: string
}

interface ClueState {
  collectedClues: Clue[]
  currentSceneClues: Clue[]
  selectedClue: Clue | null
  filterType: string | null

  addClue: (clue: Clue) => void
  setCollectedClues: (clues: Clue[]) => void
  setCurrentSceneClues: (clues: Clue[]) => void
  setSelectedClue: (clue: Clue | null) => void
  setFilterType: (type: string | null) => void
  updateClueStatus: (clueId: string, status: string) => void
  getClueById: (clueId: string) => Clue | undefined
  resetClues: () => void
}

export const useClueStore = create<ClueState>((set, get) => ({
  collectedClues: [],
  currentSceneClues: [],
  selectedClue: null,
  filterType: null,

  addClue: (clue) => set((state) => ({
    collectedClues: [...state.collectedClues, clue],
  })),
  setCollectedClues: (clues) => set({ collectedClues: clues }),
  setCurrentSceneClues: (clues) => set({ currentSceneClues: clues }),
  setSelectedClue: (clue) => set({ selectedClue: clue }),
  setFilterType: (type) => set({ filterType: type }),
  updateClueStatus: (clueId, status) => set((state) => ({
    collectedClues: state.collectedClues.map((clue) =>
      clue.id === clueId ? { ...clue, status } : clue
    ),
  })),
  getClueById: (clueId) => get().collectedClues.find((clue) => clue.id === clueId),
  resetClues: () => set({
    collectedClues: [],
    currentSceneClues: [],
    selectedClue: null,
    filterType: null,
  }),
}))
