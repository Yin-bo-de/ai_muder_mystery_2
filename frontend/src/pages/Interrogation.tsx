import { useState, useRef, useEffect } from 'react'
import { Typography, Row, Col, Input, Button, Space, Radio, message, Empty } from 'antd'
import { MessageOutlined, SendOutlined, UserSwitchOutlined } from '@ant-design/icons'
import SuspectAvatar from '@/components/SuspectAvatar'
import MessageBox from '@/components/MessageBox'
import SuspectMentions from '@/components/SuspectMentions'
import { useGameStore } from '@/store/gameStore'
import { useDialogueStore } from '@/store/dialogueStore'
import { sendMessage, switchInterrogationMode } from '@/services/agentApi'
import type { DialogueMode, Suspect } from '@/types/game'

const { Title } = Typography
const { TextArea } = Input

// 模拟嫌疑人数据
const mockSuspects: Suspect[] = [
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
    avatar: '',
    gender: '男',
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
    avatar: '',
    gender: '男',
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
    avatar: '',
    gender: '男',
  },
]

// 保密标签组件
const SecretLabel = () => (
  <div style={{
    display: 'inline-block',
    background: '#dc2626',
    color: '#fff',
    padding: '2px 8px',
    borderRadius: 4,
    fontSize: 12,
    fontWeight: 'bold'
  }}>
    保密
  </div>
)

const Interrogation = () => {
  const [inputMessage, setInputMessage] = useState('')
  const [dialogueMode, setDialogueMode] = useState<DialogueMode>('group')
  const [selectedSuspect, setSelectedSuspect] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [targetSuspects, setTargetSuspects] = useState<string[]>([])
  // 记录当前对话视图切换时间，只有切换后收到的新消息才显示打字机效果
  const [viewSwitchedAt, setViewSwitchedAt] = useState(Date.now())
  // 记录当前的对话视图key（用于判断是否切换了视图）
  const [currentViewKey, setCurrentViewKey] = useState('group')

  const { sessionId, suspects } = useGameStore()
  const {
    messages,
    isSending,
    addMessage,
    setIsSending,
    setDialogueMode: setStoreDialogueMode,
    addSystemPrompt,
    getFilteredMessages,
  } = useDialogueStore()

  // 滚动到底部 - 视图切换时直接跳转，新消息时平滑滚动
  const [needsForceScroll, setNeedsForceScroll] = useState(true)

  useEffect(() => {
    if (messagesEndRef.current) {
      if (needsForceScroll) {
        // 视图切换时直接跳转到最新消息，不使用平滑滚动
        messagesEndRef.current.scrollIntoView({ behavior: 'auto' })
        setNeedsForceScroll(false)
      } else {
        // 新消息时使用平滑滚动
        messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
      }
    }
  }, [messages, needsForceScroll])

  // 计算当前视图的key
  const getViewKey = (mode: DialogueMode, suspectId: string | null): string => {
    return mode === 'single' && suspectId ? `single_${suspectId}` : 'group'
  }

  // 监听对话模式和嫌疑人变化，更新视图切换时间
  useEffect(() => {
    const newViewKey = getViewKey(dialogueMode, selectedSuspect)
    if (newViewKey !== currentViewKey) {
      console.log(`[Interrogation] 切换对话视图: ${currentViewKey} -> ${newViewKey}`)
      setCurrentViewKey(newViewKey)
      setViewSwitchedAt(Date.now())
      setNeedsForceScroll(true)
    }
  }, [dialogueMode, selectedSuspect, currentViewKey])

  const handleInputChange = (value: string, newTargetSuspects: string[]) => {
    setInputMessage(value)
    setTargetSuspects(newTargetSuspects)
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return
    if (!sessionId) {
      message.error('游戏会话不存在，请重新开始')
      return
    }

    const messageContent = inputMessage.trim()
    const finalTargetSuspects = dialogueMode === 'single' && selectedSuspect
      ? [selectedSuspect]
      : (targetSuspects.length > 0 ? targetSuspects : undefined)

    // 添加用户消息
    addMessage({
      role: 'user',
      content: messageContent,
      type: 'text',
      dialogueMode: dialogueMode,
      suspectId: selectedSuspect || undefined,
    })

    setInputMessage('')
    setTargetSuspects([])
    setIsSending(true)

    try {
      const res = await sendMessage(sessionId, {
        message: messageContent,
        target_suspects: finalTargetSuspects
      })

      // 按顺序显示嫌疑人回复，每条间隔3.5秒（足够打字机显示完）
      res.responses.forEach((resp: any, index: number) => {
        setTimeout(() => {
          addMessage({
            role: 'suspect',
            content: resp.content,
            sender_id: resp.suspect_id,
            sender_name: resp.name,
            mood: resp.mood,
            type: resp.is_refusal ? 'text' : 'text',
            dialogueMode: dialogueMode,
            suspectId: resp.suspect_id,
          })
        }, index * 3500)
      })

      // 添加系统提示（直接显示）
      res.system_prompts.forEach((prompt: string) => {
        addMessage({
          role: 'system',
          content: prompt,
          type: 'system_prompt',
          dialogueMode: dialogueMode,
          suspectId: selectedSuspect || undefined,
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
      const params: any = { mode }
      if (mode === 'single' && selectedSuspect) {
        params.suspect_id = selectedSuspect
      }
      await switchInterrogationMode(sessionId, params)
      setDialogueMode(mode)
      setStoreDialogueMode(mode, selectedSuspect)
      message.success(`已切换到${mode === 'single' ? '单独审讯' : '全体质询'}模式`)
    } catch (error) {
      message.error('切换模式失败')
    }
  }

  const handleSuspectSelect = async (suspectId: string) => {
    if (!sessionId) {
      message.error('游戏会话不存在，请重新开始')
      return
    }

    try {
      const params: any = { mode: 'single', suspect_id: suspectId }
      await switchInterrogationMode(sessionId, params)
      setSelectedSuspect(suspectId)
      setDialogueMode('single')
      setStoreDialogueMode('single', suspectId)
      message.success(`已切换到单独审讯模式，现在可以单独审讯 ${displaySuspects.find(s => s.suspect_id === suspectId)?.name}`)
    } catch (error) {
      message.error('切换模式失败')
    }
  }

  const displaySuspects = suspects.length > 0 ? suspects : mockSuspects

  // 单独审讯模式的背景变暗效果
  const interrogationOverlayStyle = {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0, 0, 0, 0.7)',
    zIndex: 99,
    display: dialogueMode === 'single' ? 'block' : 'none',
    pointerEvents: 'none' as const,
  }

  return (
    <div style={{ position: 'relative', height: 'calc(100vh - 140px)', display: 'flex', flexDirection: 'column' }}>
      {/* 单独审讯模式背景变暗效果 */}
      <div style={interrogationOverlayStyle} />

      <div style={{
        marginBottom: 24,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        position: 'relative' as const,
        zIndex: 100,
      }}>
        <Title level={2} style={{ color: '#fff', margin: 0 }}>
          <MessageOutlined /> 质询嫌疑人
          {dialogueMode === 'single' && (
            <span style={{ marginLeft: 12 }}>
              <SecretLabel />
            </span>
          )}
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
      <div style={{
        marginBottom: 24,
        display: 'flex',
        gap: 24,
        flexWrap: 'wrap',
        position: 'relative' as const,
        zIndex: 100,
      }}>
        {displaySuspects.map(suspect => {
          const isSelected = selectedSuspect === suspect.suspect_id
          const isGrayscale = dialogueMode === 'single' && !isSelected

          return (
            <div
              key={suspect.suspect_id}
              style={{
                filter: isGrayscale ? 'grayscale(100%)' : 'none',
                opacity: isGrayscale ? 0.5 : 1,
                transition: 'all 0.3s ease',
              }}
            >
              <SuspectAvatar
                name={suspect.name}
                mood={(suspect as any).mood || 'calm'}
                stressLevel={(suspect as any).stress_level || 0}
                onClick={() => handleSuspectSelect(suspect.suspect_id)}
                selected={isSelected}
              />
            </div>
          )
        })}
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
          position: 'relative' as const,
          zIndex: 100,
        }}
      >
        {(() => {
          const filteredMessages = getFilteredMessages(dialogueMode, selectedSuspect)
          return filteredMessages.length === 0 ? (
            <Empty
              description="开始提问吧，看看嫌疑人会露出什么破绽..."
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              style={{ color: 'rgba(255,255,255,0.45)' }}
            />
          ) : (
            filteredMessages.map((msg) => {
              // 只有当前视图切换后收到的新消息才使用打字机效果
              const isNewMessageForCurrentView = msg.timestamp >= viewSwitchedAt
              return (
                <MessageBox
                  key={msg.id}
                  id={msg.id}
                  role={msg.role}
                  content={msg.content}
                  senderName={msg.sender_name}
                  timestamp={msg.timestamp}
                  mood={msg.mood}
                  type={msg.type}
                  enableTypewriter={isNewMessageForCurrentView && msg.role === 'suspect'}
                />
              )
            })
          )
        })()}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div style={{ display: 'flex', gap: 12, position: 'relative' as const, zIndex: 100 }}>
        <SuspectMentions
          suspects={displaySuspects}
          value={inputMessage}
          onChange={handleInputChange}
          onSend={handleSendMessage}
          placeholder={`${dialogueMode === 'single' ? '对' + (selectedSuspect ? displaySuspects.find(s => s.suspect_id === selectedSuspect)?.name : '嫌疑人') : '对所有嫌疑人'}说点什么... (输入@可指定嫌疑人，Enter发送，Shift+Enter换行)`}
          disabled={isSending || (dialogueMode === 'single' && !selectedSuspect)}
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
