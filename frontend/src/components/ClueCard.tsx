import { Card, Tag, Typography, Button, Tooltip } from 'antd'
import { SearchOutlined, LockOutlined, UnlockOutlined, LinkOutlined } from '@ant-design/icons'
import type { ClueType, ClueStatus } from '../types/game'

const { Text, Paragraph } = Typography

interface ClueCardProps {
  id: string
  name: string
  description: string
  type: ClueType
  status: ClueStatus
  scene: string
  relatedSuspects: string[]
  unlockCondition?: string
  onDecrypt?: () => void
  onAssociate?: () => void
  onClick?: () => void
  size?: 'small' | 'default'
}

const typeConfig = {
  physical: { color: '#1890ff', text: '物证', icon: <SearchOutlined /> },
  testimony: { color: '#52c41a', text: '证词', icon: <LinkOutlined /> },
  association: { color: '#faad14', text: '关联线索', icon: <LinkOutlined /> },
  decrypted: { color: '#722ed1', text: '解密线索', icon: <UnlockOutlined /> },
}

const statusConfig = {
  undiscovered: { color: '#8c8c8c', text: '未发现' },
  discovered: { color: '#1890ff', text: '已发现' },
  decrypted: { color: '#722ed1', text: '已解密' },
  associated: { color: '#52c41a', text: '已关联' },
}

const ClueCard: React.FC<ClueCardProps> = ({
  id,
  name,
  description,
  type,
  status,
  scene,
  relatedSuspects,
  unlockCondition,
  onDecrypt,
  onAssociate,
  onClick,
  size = 'default',
}) => {
  const typeInfo = typeConfig[type]
  const statusInfo = statusConfig[status]

  const isLocked = status === 'undiscovered'
  const canDecrypt = type === 'decrypted' && status === 'discovered'
  const canAssociate = type === 'association' && status === 'discovered'

  return (
    <Card
      size={size}
      hoverable
      onClick={onClick}
      style={{
        marginBottom: 12,
        background: isLocked ? '#1a1a1a' : '#141414',
        border: `1px solid ${isLocked ? '#2a2a2a' : '#303030'}`,
        opacity: isLocked ? 0.6 : 1,
      }}
      className="card-hover"
      extra={
        <div style={{ display: 'flex', gap: 4 }}>
          <Tag color={typeInfo.color} icon={typeInfo.icon}>
            {typeInfo.text}
          </Tag>
          <Tag color={statusInfo.color}>
            {statusInfo.text}
          </Tag>
        </div>
      }
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {isLocked && <LockOutlined style={{ color: '#faad14' }} />}
          <Text strong style={{ color: '#fff' }}>{name}</Text>
        </div>
      }
    >
      <Paragraph
        style={{
          color: isLocked ? '#8c8c8c' : 'rgba(255,255,255,0.85)',
          marginBottom: 12,
          minHeight: 44,
        }}
        ellipsis={{ rows: 2 }}
      >
        {isLocked ? '??? 该线索尚未被发现' : description}
      </Paragraph>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px' }}>
        <Text type="secondary" style={{ fontSize: '12px' }}>
          发现地点: {scene}
        </Text>

        <div style={{ display: 'flex', gap: 4 }}>
          {canDecrypt && (
            <Tooltip title="需要解密">
              <Button
                type="primary"
                size="small"
                icon={<UnlockOutlined />}
                onClick={(e) => {
                  e.stopPropagation()
                  onDecrypt?.()
                }}
              >
                解密
              </Button>
            </Tooltip>
          )}

          {canAssociate && (
            <Tooltip title="可以关联">
              <Button
                type="default"
                size="small"
                icon={<LinkOutlined />}
                onClick={(e) => {
                  e.stopPropagation()
                  onAssociate?.()
                }}
              >
                关联
              </Button>
            </Tooltip>
          )}
        </div>
      </div>

      {relatedSuspects.length > 0 && !isLocked && (
        <div style={{ marginTop: 8 }}>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            相关嫌疑人: {relatedSuspects.join(', ')}
          </Text>
        </div>
      )}
    </Card>
  )
}

export default ClueCard
