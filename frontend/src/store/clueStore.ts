import { create } from 'zustand'
import type { Clue as GlobalClue, ClueType, ClueStatus } from '../types/game'

interface Clue {
  id: string
  clue_id?: string
  name: string
  description: string
  type: ClueType
  status: ClueStatus
  scene: string
  relatedSuspects: string[]
  unlockCondition?: string
}

interface ClueState {
  collectedClues: Clue[]
  currentSceneClues: Clue[]
  selectedClue: Clue | null
  filterType: string | null

  addClue: (clue: any) => boolean
  setCollectedClues: (clues: Clue[]) => void
  setCurrentSceneClues: (clues: Clue[]) => void
  setSelectedClue: (clue: Clue | null) => void
  setFilterType: (type: string | null) => void
  updateClueStatus: (clueId: string, status: string) => void
  getClueById: (clueId: string) => Clue | undefined
  hasClue: (clueId: string) => boolean
  resetClues: () => void
}

// 获取线索的唯一ID（兼容clue_id和id字段）
const getClueUniqueId = (clue: any): string => {
  return clue.clue_id || clue.id
}

export const useClueStore = create<ClueState>((set, get) => ({
  collectedClues: [],
  currentSceneClues: [],
  selectedClue: null,
  filterType: null,

  addClue: (clue) => {
    const state = get()
    const clueId = getClueUniqueId(clue)

    // 检查是否已存在
    if (state.hasClue(clueId)) {
      console.warn(`[clueStore] 线索 ${clueId} 已存在，跳过重复添加`)
      return false
    }

    // 标准化线索对象
    const normalizedClue: Clue = {
      ...clue,
      id: clueId,
      type: (clue.type || clue.clue_type || 'physical').toLowerCase(),
      status: (clue.status || 'discovered').toLowerCase(),
      relatedSuspects: clue.related_suspects || clue.relatedSuspects || [],
    }

    set((state) => ({
      collectedClues: [...state.collectedClues, normalizedClue],
    }))
    return true
  },

  setCollectedClues: (clues) => set({ collectedClues: clues }),
  setCurrentSceneClues: (clues) => set({ currentSceneClues: clues }),
  setSelectedClue: (clue) => set({ selectedClue: clue }),
  setFilterType: (type) => set({ filterType: type }),

  updateClueStatus: (clueId, status) => set((state) => ({
    collectedClues: state.collectedClues.map((clue) =>
      getClueUniqueId(clue) === clueId ? { ...clue, status } : clue
    ),
  })),

  getClueById: (clueId) => {
    const state = get()
    return state.collectedClues.find((clue) => getClueUniqueId(clue) === clueId)
  },

  hasClue: (clueId) => {
    const state = get()
    return state.collectedClues.some((clue) => getClueUniqueId(clue) === clueId)
  },

  resetClues: () => set({
    collectedClues: [],
    currentSceneClues: [],
    selectedClue: null,
    filterType: null,
  }),
}))
