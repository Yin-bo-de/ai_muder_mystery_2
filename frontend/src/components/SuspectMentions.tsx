import { Mentions } from 'antd'
import type { MentionsProps } from 'antd/es/mentions'
import type { Suspect } from '../types/game'

interface SuspectMentionsProps extends Omit<MentionsProps, 'onChange'> {
  suspects: Suspect[]
  value: string
  onChange: (value: string, targetSuspects: string[]) => void
}

const { Option } = Mentions

const SuspectMentions: React.FC<SuspectMentionsProps> = ({
  suspects,
  value,
  onChange,
  ...props
}) => {
  const handleChange = (val: string) => {
    // 解析文本中的 @嫌疑人 标签，提取嫌疑人ID
    const targetSuspects: string[] = []
    const mentionRegex = /@\[([^]]+)\]\(([^)]+)\)/g
    let match

    while ((match = mentionRegex.exec(val)) !== null) {
      const suspectId = match[2]
      if (!targetSuspects.includes(suspectId)) {
        targetSuspects.push(suspectId)
      }
    }

    onChange(val, targetSuspects)
  }

  const renderOption = (suspect: Suspect) => (
    <Option key={suspect.suspect_id} value={suspect.suspect_id}>
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
      placeholder="输入消息，支持 @嫌疑人 提问..."
      style={{ width: '100%' }}
      {...props}
    >
      {suspects.map(renderOption)}
    </Mentions>
  )
}

export default SuspectMentions