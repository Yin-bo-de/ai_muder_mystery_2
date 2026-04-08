import request from './api'
import type {
  GameStatusResponse,
  Clue,
} from '../types/game'

/**
 * 游戏相关API
 */

// 创建新案件
export interface CreateGameRequest {
  user_id?: string
  difficulty?: 'easy' | 'medium' | 'hard'
}

export interface CreateGameResponse {
  session_id: string
  case_basic_info: {
    case_id: string
    title: string
    description: string
    difficulty: string
    victim_name: string
    death_time: string
    death_cause: string
    scene: string
  }
  suspects: Array<{
    suspect_id: string
    name: string
    age: number
    gender: string
    occupation: string
    relationship_with_victim: string
    avatar?: string
  }>
  scenes: Array<{
    scene_id: string
    name: string
    description: string
    is_locked: boolean
  }>
}

// 防止重复请求的标记
let isCreatingCase = false

export const createNewCase = async (params?: CreateGameRequest): Promise<CreateGameResponse> => {
  console.log('[gameApi] createNewCase被调用，参数:', params)
  if (isCreatingCase) {
    console.warn('[gameApi] 案件生成中，拒绝重复请求')
    throw new Error('案件生成中，请不要重复点击')
  }

  try {
    isCreatingCase = true
    console.log('[gameApi] 发送POST请求到 /game/new')
    const result = await request.post('/game/new', params || {})
    console.log('[gameApi] API响应:', result)
    return result
  } catch (error) {
    console.error('[gameApi] 请求失败:', error)
    throw error
  } finally {
    // 1秒后重置标记，防止短时间内重复请求
    setTimeout(() => {
      isCreatingCase = false
    }, 1000)
  }
}

// 获取游戏状态
export const getGameStatus = async (sessionId: string): Promise<GameStatusResponse> => {
  return request.get(`/game/${sessionId}/status`)
}

// 提交勘查操作
export interface InvestigateRequest {
  scene: string
  item?: string
}

export interface InvestigateResponse {
  success: boolean
  clue_found: boolean
  clue?: Clue
  message: string
}

export const submitInvestigation = async (
  sessionId: string,
  params: InvestigateRequest
): Promise<InvestigateResponse> => {
  return request.post(`/game/${sessionId}/investigate`, params)
}

// 提交线索解密
export interface DecryptRequest {
  clue_id: string
  password?: string
  related_clues?: string[]
}

export interface DecryptResponse {
  success: boolean
  already_decrypted?: boolean
  decrypted_content: string
  message: string
}

export const decryptClue = async (
  sessionId: string,
  params: DecryptRequest
): Promise<DecryptResponse> => {
  return request.post(`/game/${sessionId}/decrypt`, params)
}

// 提交指认
export interface AccuseRequest {
  suspect_id: string
  motive: string
  modus_operandi: string
  evidence: string[]
}

export interface AccuseResponse {
  is_correct: boolean
  accuracy_score: number
  clue_completion_rate: number
  evidence_match_score: number
  report: {
    title: string
    description: string
    case_truth: {
      murderer_name: string
      murderer_occupation: string
      motive: string
      modus_operandi: string
      time_line: string
    }
    key_evidence: Array<{
      name: string
      description: string
    }>
    player_performance: {
      strengths: string[]
      weaknesses: string[]
      improvement_suggestions: string[]
    }
  }
  review: {
    rank: string
    comment: string
    play_time: number
    clues_collected: number
    total_clues: number
    wrong_guess_count: number
    dialogue_count: number
  }
  true_murderer_id: string
  true_murderer_name: string
}

export const submitAccusation = async (
  sessionId: string,
  params: AccuseRequest
): Promise<AccuseResponse> => {
  return request.post(`/game/${sessionId}/accuse`, params)
}

// 获取已收集线索列表
export const getCollectedClues = async (
  sessionId: string,
  clueType?: string
): Promise<Clue[]> => {
  return request.get(`/game/${sessionId}/clues`, {
    params: clueType ? { clue_type: clueType } : {},
  })
}

// 获取线索详情
export const getClueDetail = async (sessionId: string, clueId: string): Promise<Clue> => {
  return request.get(`/game/${sessionId}/clues/${clueId}`)
}

// 获取线索统计信息
export interface ClueStatistics {
  total_clues: number
  collected_clues: number
  completion_rate: number
  type_statistics: Record<string, number>
  status_statistics: Record<string, number>
  scene_statistics: Record<string, number>
  undiscovered_clues_count: number
}

export const getClueStatistics = async (sessionId: string): Promise<ClueStatistics> => {
  return request.get(`/game/${sessionId}/clues/statistics`)
}

// 关联线索
export const associateClues = async (
  sessionId: string,
  clueIds: string[]
): Promise<{
  success: boolean
  message: string
  common_suspects: string[]
  associated_clues: string[]
}> => {
  return request.post(`/game/${sessionId}/clues/associate`, clueIds)
}

// 获取线索提示
export const getClueHints = async (
  sessionId: string
): Promise<Array<{ hint: string; scene: string }>> => {
  return request.get(`/game/${sessionId}/clues/hints`)
}

