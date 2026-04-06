import { Avatar, Badge, Tooltip } from 'antd'
import { UserOutlined } from '@ant-design/icons'
import type { SuspectMood } from '../types/game'

interface SuspectAvatarProps {
  name: string
  avatar?: string
  mood: SuspectMood
  stressLevel: number
  isMurderer?: boolean
  size?: 'small' | 'default' | 'large'
  onClick?: () => void
}

const moodConfig = {
  calm: { color: '#52c41a', text: '镇定', badgeColor: 'success' },
  nervous: { color: '#faad14', text: '紧张', badgeColor: 'warning' },
  angry: { color: '#f5222d', text: '愤怒', badgeColor: 'error' },
  scared: { color: '#722ed1', text: '害怕', badgeColor: 'processing' },
  guilty: { color: '#eb2f96', text: '心虚', badgeColor: 'error' },
}

const SuspectAvatar: React.FC<SuspectAvatarProps> = ({
  name,
  avatar,
  mood = 'calm',
  stressLevel,
  isMurderer = false,
  size = 'default',
  onClick,
}) => {
  const moodInfo = moodConfig[mood]
  const sizeMap = {
    small: 48,
    default: 64,
    large: 80,
  }

  const getStressColor = () => {
    if (stressLevel < 20) return '#52c41a'
    if (stressLevel < 40) return '#faad14'
    if (stressLevel < 60) return '#fa8c16'
    if (stressLevel < 80) return '#f5222d'
    return '#eb2f96'
  }

  return (
    <Tooltip
      title={
        <div>
          <div style={{ fontWeight: 'bold', marginBottom: 4 }}>{name}</div>
          <div>情绪: <span style={{ color: moodInfo.color }}>{moodInfo.text}</span></div>
          <div>压力值: <span style={{ color: getStressColor() }}>{stressLevel}%</span></div>
        </div>
      }
    >
      <div
        style={{
          position: 'relative',
          display: 'inline-block',
          cursor: onClick ? 'pointer' : 'default',
        }}
        onClick={onClick}
      >
        <Badge
          status={moodInfo.badgeColor as any}
          text={moodInfo.text}
          style={{
            position: 'absolute',
            top: -8,
            right: -8,
            fontSize: '12px',
          }}
        />
        <Avatar
          size={sizeMap[size]}
          src={avatar}
          icon={<UserOutlined />}
          style={{
            border: `3px solid ${getStressColor()}`,
            boxShadow: `0 0 12px ${getStressColor()}40`,
            transition: 'all 0.3s ease',
          }}
          className="card-hover"
        >
          {name.charAt(0)}
        </Avatar>

        {/* 压力值进度条 */}
        <div
          style={{
            width: '100%',
            height: 4,
            backgroundColor: '#303030',
            borderRadius: 2,
            marginTop: 4,
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${stressLevel}%`,
              height: '100%',
              backgroundColor: getStressColor(),
              transition: 'width 0.5s ease',
            }}
          />
        </div>
      </div>
    </Tooltip>
  )
}

export default SuspectAvatar
