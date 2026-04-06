import { useState, useRef, useEffect } from 'react'
import { Typography, Row, Col, Input, Button, Space, Radio, message, Empty } from 'antd'
import { MessageOutlined, SendOutlined, UserSwitchOutlined } from '@ant-design/icons'
import SuspectAvatar from '@/components/SuspectAvatar'
import MessageBox from '@/components/MessageBox'
import { useGameStore } from '@/store/gameStore'
import { useDialogueStore } from '@/store/dialogueStore'
import { sendMessage, switchInterrogationMode } from '@/services/agentApi'
import type { DialogueMode } from '@/types/game'

const { Title } = Typography
const { TextArea } = Input

// 模拟嫌疑人数据
const mockSuspects = [
  {
    suspect_id: 's1',
    name: '李四',
    age: 32,
    occupation: '外卖员',
    relationship_with_victim: '债主',
    motive: '死者欠他5万元不还',
    alibi: '案发时我在送外卖',
    secret: '他最近赌博输了很多钱',
    personality: '脾气暴躁，容易冲动',
    mood: 'calm',
    stress_level: 15,
  },
  {
    suspect_id: 's2',
    name: '王五',
    age: 28,
    occupation: '同事',
    relationship_with_victim: '同事',
    motive: '抢了他的晋升名额',
    alibi: '案发时我在公司加班',
    secret: '他偷偷挪用了公款',
    personality: '内向，心思缜密',
    mood: 'nervous',
    stress_level: 35,
  },
  {
    suspect_id: 's3',
    name: '赵六',
    age: 45,
    occupation: '房东',
    relationship_with_victim: '房东',
    motive: '死者长期拖欠房租',
    alibi: '案发时我在收其他房租',
    secret: '他有过犯罪前科',
    personality: '势利，贪小便宜',
    mood: 'angry',
    stress_level: 55,
  },
]

const Interrogation = () => {
  const [inputMessage, setInputMessage] = useState('')
  const [dialogueMode, setDialogueMode] = useState<DialogueMode>('group')
  const [selectedSuspect, setSelectedSuspect] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { sessionId, suspects } = useGameStore()
  const { messages, isSending, addMessage, setIsSending } = useDialogueStore()

  // 滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return
    if (!sessionId) {
      message.error('游戏会话不存在，请重新开始')
      return
    }

    const targetSuspects = dialogueMode === 'single' && selectedSuspect ? [selectedSuspect] : undefined

    // 添加用户消息
    addMessage({
      role: 'user',
      content: inputMessage.trim(),
      type: 'text',
    })

    setInputMessage('')
    setIsSending(true)

    try {
      const res = await sendMessage(sessionId, inputMessage.trim(), targetSuspects)

      // 添加嫌疑人回复
      res.responses.forEach((resp: any) => {
        addMessage({
          role: 'suspect',
          content: resp.content,
          sender_id: resp.suspect_id,
          sender_name: resp.name,
          mood: resp.mood,
          type: 'text',
        })
      })

      // 添加系统提示
      res.system_prompts.forEach((prompt: string) => {
        addMessage({
          role: 'system',
          content: prompt,
          type: 'system_prompt',
        })
      })

    } catch (error) {
      message.error('发送消息失败，请重试')
    } finally {
      setIsSending(false)
    }
  }

  const handleSwitchMode = async (mode: DialogueMode) => {
    if (!sessionId) {
      message.error('游戏会话不存在，请重新开始')
      return
    }

    try {
      await switchInterrogationMode(sessionId, mode, mode === 'single' ? selectedSuspect : undefined)
      setDialogueMode(mode)
      message.success(`已切换到${mode === 'single' ? '单独审讯' : '全体质询'}模式`)
    } catch (error) {
      message.error('切换模式失败')
    }
  }

  const handleSuspectSelect = (suspectId: string) => {
    setSelectedSuspect(suspectId)
    if (dialogueMode === 'single') {
      handleSwitchMode('single')
    }
  }

  const displaySuspects = suspects.length > 0 ? suspects : mockSuspects

  return (
    <div style={{ height: 'calc(100vh - 140px)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2} style={{ color: '#fff', margin: 0 }}>
          <MessageOutlined /> 质询嫌疑人
        </Title>

        <Space>
          <Radio.Group
            value={dialogueMode}
            onChange={(e) => handleSwitchMode(e.target.value)}
            buttonStyle="solid"
          >
            <Radio.Button value="group">全体质询</Radio.Button>
            <Radio.Button value="single">单独审讯</Radio.Button>
          </Radio.Group>
          {dialogueMode === 'single' && (
            <Button
              type="primary"
              icon={<UserSwitchOutlined />}
              onClick={() => setSelectedSuspect(null)}
            >
              选择审讯对象
            </Button>
          )}
        </Space>
      </div>

      {/* 嫌疑人列表 */}
      <div style={{ marginBottom: 24, display: 'flex', gap: 24, flexWrap: 'wrap' }}>
        {displaySuspects.map(suspect => (
          <SuspectAvatar
            key={suspect.suspect_id}
            name={suspect.name}
            mood={suspect.mood}
            stressLevel={suspect.stress_level}
            onClick={() => handleSuspectSelect(suspect.suspect_id)}
          />
        ))}
      </div>

      {/* 对话区域 */}
      <div
        style={{
          flex: 1,
          overflow: 'auto',
          background: '#141414',
          borderRadius: 8,
          padding: 24,
          marginBottom: 24,
          border: '1px solid #303030',
        }}
      >
        {messages.length === 0 ? (
          <Empty
            description="开始提问吧，看看嫌疑人会露出什么破绽..."
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            style={{ color: 'rgba(255,255,255,0.45)' }}
          />
        ) : (
          messages.map(msg => (
            <MessageBox
              key={msg.id}
              id={msg.id}
              role={msg.role}
              content={msg.content}
              senderName={msg.sender_name}
              timestamp={msg.timestamp}
              mood={msg.mood}
              type={msg.type}
            />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div style={{ display: 'flex', gap: 12 }}>
        <TextArea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder={`${dialogueMode === 'single' ? '对' + (selectedSuspect ? displaySuspects.find(s => s.suspect_id === selectedSuspect)?.name : '嫌疑人') : '对所有嫌疑人'}说点什么...`}
          rows={3}
          onPressEnter={(e) => {
            if (!e.shiftKey) {
              e.preventDefault()
              handleSendMessage()
            }
          }}
          disabled={isSending || (dialogueMode === 'single' && !selectedSuspect)}
          style={{ background: '#1e1e1e', border: '1px solid #303030', color: '#fff' }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSendMessage}
          loading={isSending}
          disabled={!inputMessage.trim() || (dialogueMode === 'single' && !selectedSuspect)}
          style={{ height: 'auto', alignSelf: 'flex-end' }}
        >
          发送
        </Button>
      </div>
    </div>
  )
}

export default Interrogation
