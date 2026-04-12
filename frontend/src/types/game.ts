/**
 * 游戏相关类型定义
 */

// 游戏状态
export type GameStatus = 'preparing' | 'in_progress' | 'completed' | 'failed'

// 用户操作类型
export type OperationType = 'investigate' | 'send_message' | 'accuse' | 'decrypt' | 'change_mode' | 'command'

// 对话模式
export type DialogueMode = 'single' | 'group'

// 嫌疑人情绪状态
export type SuspectMood = 'calm' | 'nervous' | 'angry' | 'scared' | 'guilty'

// 线索类型
export type ClueType = 'physical' | 'testimony' | 'association' | 'decrypt' | 'document'

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

// 矛盾类型
export type ContradictionType = 'timeline' | 'spatial' | 'evidence'

// 矛盾点接口
export interface ContradictionPoint {
  contradiction_id: string
  contradiction_type: ContradictionType
  description: string
  involved_suspects: string[]
  trigger_condition: Record<string, any>
  hint_for_user: string
  related_clue_id?: string
  clue_location?: string
}

// 威胁程度
export type ThreatLevel = 'low' | 'medium' | 'high' | 'critical'

// 反驳决策
export interface RefusalDecision {
  should_refuse: boolean
  threat_level: ThreatLevel
  has_counter_evidence: boolean
  refusal_reason?: string
}

// 被提及的嫌疑人
export interface MentionedSuspect {
  suspect_id: string
  name: string
}

// 线索接口
export interface Clue {
  clue_id: string
  name: string
  clue_type: ClueType
  status: ClueStatus
  description: string
  location: string
  scene: string
  content?: string
  hidden_content?: string
  related_clues: string[]
  required_password?: string
  required_clues: string[]
  importance: number
  points_to_suspect?: string
  related_suspects: string[]
  is_red_herring: boolean
}

// 嫌疑人接口
export interface Suspect {
  suspect_id: string
  name: string
  age: number
  gender: string
  occupation: string
  description: string
  personality_traits: string[]
  relationship_with_victim: string
  motive?: string
  alibi: string
  alibi_reliability: number
  timeline: Record<string, string>
  secrets: string[]
  is_murderer: boolean
  avatar?: string
  background_story: string
  refusal_threshold: number
  counter_evidence: string[]
  personality_modifier: number
  spatial_relationships: Record<string, string>
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
  contradiction_points: ContradictionPoint[]
  refusal_count: number
}
