/**
 * 游戏相关类型定义
 */

// 游戏状态
export type GameStatus = 'preparing' | 'in_progress' | 'completed' | 'failed'

// 用户操作类型
export type OperationType = 'investigate' | 'talk' | 'accuse' | 'decrypt' | 'switch_mode'

// 对话模式
export type DialogueMode = 'single' | 'group'

// 嫌疑人情绪状态
export type SuspectMood = 'calm' | 'nervous' | 'angry' | 'scared' | 'guilty'

// 线索类型
export type ClueType = 'physical' | 'testimony' | 'association' | 'decrypted'

// 线索状态
export type ClueStatus = 'undiscovered' | 'discovered' | 'decrypted' | 'associated'

// 消息角色
export type MessageRole = 'system' | 'user' | 'suspect' | 'judge'

// 消息优先级
export enum MessagePriority {
  P0 = 0,
  P1 = 1,
  P2 = 2,
}

// 消息类型
export type MessageType = 'text' | 'system_prompt' | 'evidence' | 'accusation'

// 线索接口
export interface Clue {
  clue_id: string
  name: string
  description: string
  type: ClueType
  status: ClueStatus
  scene: string
  related_suspects: string[]
  unlock_condition?: string
}

// 嫌疑人接口
export interface Suspect {
  suspect_id: string
  name: string
  age: number
  gender: string
  occupation: string
  relationship_with_victim: string
  motive: string
  alibi: string
  secret: string
  personality: string
  avatar?: string
}

// 嫌疑人状态
export interface SuspectState {
  suspect_id: string
  stress_level: number
  mood: SuspectMood
  lied_count: number
}

// 消息接口
export interface Message {
  id: string
  role: MessageRole
  content: string
  sender_id?: string
  sender_name?: string
  timestamp: number
  mood?: SuspectMood
  type: MessageType
}

// 案件基础信息
export interface CaseBasicInfo {
  case_id: string
  title: string
  description: string
  difficulty: string
  victim_name: string
  death_time: string
  death_cause: string
  scene: string
}

// 游戏状态响应
export interface GameStatusResponse {
  session_id: string
  game_status: GameStatus
  collected_clues_count: number
  total_clues_count: number
  play_time: number
  wrong_guess_count: number
  max_wrong_guess: number
  suspect_states: SuspectState[]
  current_mode: string
}

// 游戏会话信息
export interface GameSession {
  session_id: string
  user_id: string
  case: any
  game_status: GameStatus
  collected_clues: Clue[]
  dialogue_history: Message[]
  suspect_states: Record<string, SuspectState>
  user_operations: any[]
  wrong_guess_count: number
  start_time: string
  last_active_time: string
}
