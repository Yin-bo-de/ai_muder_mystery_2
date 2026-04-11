import { Mentions } from 'antd'
import type { MentionsProps } from 'antd/es/mentions'
import type { Suspect } from '../types/game'

interface SuspectMentionsProps extends Omit<MentionsProps, 'onChange' | 'onKeyDown'> {
  suspects: Suspect[]
  value: string
  onChange: (value: string, targetSuspects: string[]) => void
  onSend?: () => void
  onKeyDown?: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void
}

const { Option } = Mentions

const SuspectMentions: React.FC<SuspectMentionsProps> = ({
  suspects,
  value,
  onChange,
  onSend,
  onKeyDown,
  ...props
}) => {
  // 建立名字到ID的映射
  const nameToIdMap = new Map(suspects.map(s => [s.name, s.suspect_id]))

  const handleChange = (val: string) => {
    // 解析文本中的 @嫌疑人 标签，提取嫌疑人ID
    const targetSuspects: string[] = []

    // Antd Mentions 使用名字作为value时的格式: @[名字](名字)
    const mentionRegex = /@\[([^\]]+)\]\([^)]+\)/g
    let match

    while ((match = mentionRegex.exec(val)) !== null) {
      const name = match[1]
      const suspectId = nameToIdMap.get(name)
      if (suspectId && !targetSuspects.includes(suspectId)) {
        targetSuspects.push(suspectId)
      }
    }

    onChange(val, targetSuspects)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // 如果有自定义onKeyDown，先调用它
    if (onKeyDown) {
      onKeyDown(e)
      return
    }

    // 默认处理：Enter发送，Shift+Enter换行
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (onSend) {
        onSend()
      }
    }
  }

  const renderOption = (suspect: Suspect) => (
    <Option key={suspect.suspect_id} value={suspect.name}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontWeight: 500 }}>{suspect.name}</span>
        <span style={{ fontSize: '12px', color: 'rgba(255,255,255,0.45)' }}>
          ({suspect.occupation})
        </span>
      </div>
    </Option>
  )

  return (
    <Mentions
      value={value}
      onChange={handleChange}
      onKeyDown={handleKeyDown}
      placeholder="输入消息，支持 @嫌疑人 提问..."
      style={{ width: '100%' }}
      {...props}
    >
      {suspects.map(renderOption)}
    </Mentions>
  )
}

export default SuspectMentions
