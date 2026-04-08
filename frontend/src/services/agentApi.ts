import request from './api'
import type { Message, SuspectState, DialogueMode } from '../types/game'

/**
 * AI交互相关API
 */

// 发送消息
export interface SendMessageRequest {
  message: string
  target_suspects?: string[]
  message_type?: 'text' | 'system_prompt' | 'evidence' | 'accusation'
}

export interface SendMessageResponse {
  success: boolean
  responses: Array<{
    suspect_id: string
    name: string
    content: string
    mood: string
    stress_level: number
    lied: boolean
    priority: number
  }>
  system_prompts: string[]
  dialogue_mode: DialogueMode
}

export const sendMessage = async (
  sessionId: string,
  params: SendMessageRequest
): Promise<SendMessageResponse> => {
  return request.post(`/agent/${sessionId}/send`, params)
}

// 切换审讯模式
export interface SwitchModeRequest {
  mode: DialogueMode
  suspect_id?: string
}

export interface SwitchModeResponse {
  mode: DialogueMode
  suspect_id?: string
  suspect_name?: string
  message: string
}

export const switchInterrogationMode = async (
  sessionId: string,
  params: SwitchModeRequest
): Promise<SwitchModeResponse> => {
  return request.post(`/agent/${sessionId}/mode`, params)
}

// 执行控场指令
export interface ControlCommandRequest {
  command: string
}

export interface ControlCommandResponse {
  success: boolean
  result: string
  command: string
}

export const executeControlCommand = async (
  sessionId: string,
  params: ControlCommandRequest
): Promise<ControlCommandResponse> => {
  return request.post(`/agent/${sessionId}/command`, params)
}

// 获取对话历史
export interface DialogueHistoryResponse {
  total: number
  limit: number
  offset: number
  messages: Message[]
}

export const getDialogueHistory = async (
  sessionId: string,
  limit?: number,
  offset?: number
): Promise<DialogueHistoryResponse> => {
  return request.get(`/agent/${sessionId}/history`, {
    params: {
      limit: limit || 100,
      offset: offset || 0,
    },
  })
}

// 获取嫌疑人状态
export const getSuspectStates = async (
  sessionId: string
): Promise<SuspectState[]> => {
  return request.get(`/agent/${sessionId}/suspects/states`)
}

