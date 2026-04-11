import { Avatar, Typography, Tag, Tooltip } from 'antd'
import { UserOutlined, RobotOutlined, SoundOutlined } from '@ant-design/icons'
import TypewriterText from './TypewriterText'
import type { MessageRole, MessageType, SuspectMood } from '../types/game'

const { Text, Paragraph } = Typography

interface MessageBoxProps {
  id: string
  role: MessageRole
  content: string
  senderName?: string
  senderAvatar?: string
  timestamp: number
  mood?: SuspectMood
  type?: MessageType
  isNew?: boolean
  enableTypewriter?: boolean
  onTypewriterComplete?: (messageId: string) => void
}

const roleConfig = {
  system: {
    bgColor: '#141414',
    textColor: '#faad14',
    icon: <SoundOutlined />,
    name: '系统提示',
    align: 'center',
  },
  user: {
    bgColor: '#722ed1',
    textColor: '#fff',
    icon: <UserOutlined />,
    name: '你',
    align: 'right',
  },
  suspect: {
    bgColor: '#1e1e1e',
    textColor: 'rgba(255,255,255,0.88)',
    icon: <RobotOutlined />,
    name: '嫌疑人',
    align: 'left',
  },
  judge: {
    bgColor: '#52c41a',
    textColor: '#fff',
    icon: <SoundOutlined />,
    name: '裁判',
    align: 'center',
  },
}

const moodConfig = {
  calm: { color: '#52c41a', text: '镇定' },
  nervous: { color: '#faad14', text: '紧张' },
  angry: { color: '#f5222d', text: '愤怒' },
  scared: { color: '#722ed1', text: '害怕' },
  guilty: { color: '#eb2f96', text: '心虚' },
  sad: { color: '#1890ff', text: '悲伤' },
  surprised: { color: '#13c2c2', text: '惊讶' },
}

const SystemHint = ({ content }: { content: string }) => (
  <div style={{
    background: 'linear-gradient(135deg, #ffd700 0%, #ff8c00 100%)',
    borderRadius: 8,
    padding: '12px 16px',
    margin: '12px 0',
    border: '1px solid #ffd700',
    boxShadow: '0 4px 12px rgba(255, 215, 0, 0.2)'
  }}>
    <span style={{
      color: '#000',
      fontWeight: 'bold',
      fontSize: 14
    }}>
      📌 {content}
    </span>
  </div>
)

const MessageBox: React.FC<MessageBoxProps> = ({
  id,
  role,
  content,
  senderName,
  senderAvatar,
  timestamp,
  mood,
  type = 'text',
  isNew = false,
  enableTypewriter = false,
  onTypewriterComplete,
}) => {
  const config = roleConfig[role]
  const isSystem = role === 'system' || role === 'judge'
  const isSystemPrompt = type === 'system_prompt'

  const formatTime = (ts: number) => {
    const date = new Date(ts)
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  }

  if (isSystemPrompt || (isSystem && content.includes('【'))) {
    return (
      <div style={{ textAlign: 'center', margin: '16px 0' }} className="fade-in">
        <SystemHint content={content} />
      </div>
    )
  }

  if (isSystem) {
    return (
      <div style={{ textAlign: 'center', margin: '16px 0' }} className="fade-in">
        <Tag
          color={role === 'judge' ? 'success' : 'warning'}
          style={{
            fontSize: '12px',
            padding: '4px 12px',
            borderRadius: '12px',
          }}
        >
          {config.icon} {content}
        </Tag>
      </div>
    )
  }

  const isRight = config.align === 'right'

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: isRight ? 'flex-end' : 'flex-start',
        marginBottom: 16,
        gap: 12,
        alignItems: 'flex-start',
      }}
      className={isNew ? 'fade-in' : ''}
    >
      {!isRight && (
        <Avatar
          src={senderAvatar}
          icon={config.icon}
          style={{
            flexShrink: 0,
            marginTop: 4,
          }}
        >
          {senderName?.charAt(0) || config.name.charAt(0)}
        </Avatar>
      )}

      <div style={{ maxWidth: '70%' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            marginBottom: 4,
            justifyContent: isRight ? 'flex-end' : 'flex-start',
          }}
        >
          {!isRight && (
            <>
              <Text strong style={{ color: '#fff', fontSize: '14px' }}>
                {senderName || config.name}
              </Text>
              {mood && moodConfig[mood as keyof typeof moodConfig] && (
                <Tag color={moodConfig[mood as keyof typeof moodConfig].color}>
                  {moodConfig[mood as keyof typeof moodConfig].text}
                </Tag>
              )}
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {formatTime(timestamp)}
              </Text>
            </>
          )}

          {isRight && (
            <>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {formatTime(timestamp)}
              </Text>
              <Text strong style={{ color: '#fff', fontSize: '14px' }}>
                {senderName || config.name}
              </Text>
            </>
          )}
        </div>

        <div
          style={{
            background: config.bgColor,
            color: config.textColor,
            padding: '12px 16px',
            borderRadius: isRight ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
            wordBreak: 'break-word',
            boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
            position: 'relative',
          }}
        >
          <Paragraph style={{ margin: 0, color: config.textColor }}>
            {enableTypewriter && role === 'suspect' ? (
              <TypewriterText
                text={content.replace(/@\[([^\]]+)\]\([^)]+\)/g, '@$1')}
                mood={mood}
                onComplete={onTypewriterComplete ? () => onTypewriterComplete(id) : undefined}
              />
            ) : (
              content.replace(/@\[([^\]]+)\]\([^)]+\)/g, '@$1')
            )}
          </Paragraph>
        </div>
      </div>

      {isRight && (
        <Avatar
          src={senderAvatar}
          icon={config.icon}
          style={{
            flexShrink: 0,
            marginTop: 4,
          }}
        >
          {senderName?.charAt(0) || config.name.charAt(0)}
        </Avatar>
      )}
    </div>
  )
}

export default MessageBox
