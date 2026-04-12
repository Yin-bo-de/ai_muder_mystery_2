import { Card, Tag, Typography, Button, Tooltip } from 'antd'
import { SearchOutlined, LockOutlined, UnlockOutlined, LinkOutlined, EyeOutlined } from '@ant-design/icons'
import type { ClueType, ClueStatus, Suspect } from '../types/game'

const { Text, Paragraph } = Typography

interface ClueCardProps {
  id: string
  name: string
  description: string
  type: ClueType
  status: ClueStatus
  scene: string
  relatedSuspects: string[]
  suspects?: Suspect[]
  unlockCondition?: string
  onDecrypt?: () => void
  onAssociate?: () => void
  onClick?: () => void
  size?: 'small' | 'default'
  showViewHint?: boolean
}

const typeConfig = {
  physical: { color: '#1890ff', text: '物证', icon: <SearchOutlined /> },
  testimony: { color: '#52c41a', text: '证词', icon: <LinkOutlined /> },
  association: { color: '#faad14', text: '关联线索', icon: <LinkOutlined /> },
  decrypt: { color: '#722ed1', text: '需解密', icon: <LockOutlined /> },
  document: { color: '#13c2c2', text: '文档', icon: <SearchOutlined /> },
}

const statusConfig = {
  undiscovered: { color: '#8c8c8c', text: '未发现' },
  hidden: { color: '#8c8c8c', text: '未发现' },
  discovered: { color: '#1890ff', text: '已发现' },
  collected: { color: '#1890ff', text: '已收集' },
  decrypted: { color: '#722ed1', text: '已解密' },
  unlocked: { color: '#722ed1', text: '已解锁' },
  associated: { color: '#52c41a', text: '已关联' },
  locked: { color: '#faad14', text: '已锁定' },
}

const ClueCard: React.FC<ClueCardProps> = ({
  id,
  name,
  description,
  type,
  status,
  scene,
  relatedSuspects,
  suspects = [],
  unlockCondition,
  onDecrypt,
  onAssociate,
  onClick,
  size = 'default',
  showViewHint = true,
}) => {
  const typeInfo = typeConfig[type] || { color: '#8c8c8c', text: '未知类型', icon: <SearchOutlined /> }
  const statusInfo = statusConfig[status] || { color: '#8c8c8c', text: '未知状态' }

  const isLocked = status === 'undiscovered'
  const canDecrypt = type === 'decrypt' && status !== 'decrypted'
  const canAssociate = type === 'association' && status === 'discovered'

  // 将嫌疑人ID转换为名字
  const getSuspectName = (suspectId: string): string => {
    const suspect = suspects.find(s => s.suspect_id === suspectId)
    return suspect?.name || suspectId
  }

  const relatedSuspectNames = relatedSuspects.map(getSuspectName)

  return (
    <Card
      size={size}
      hoverable={!isLocked}
      onClick={!isLocked ? onClick : undefined}
      style={{
        marginBottom: 12,
        background: isLocked ? '#1a1a1a' : '#141414',
        border: `1px solid ${isLocked ? '#2a2a2a' : '#303030'}`,
        opacity: isLocked ? 0.6 : 1,
        cursor: isLocked ? 'not-allowed' : 'pointer',
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
          {!isLocked && showViewHint && (
            <Tag color="blue" icon={<EyeOutlined />} style={{ fontSize: '11px', marginLeft: 'auto' }}>
              查看笔记
            </Tag>
          )}
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
            相关嫌疑人: {relatedSuspectNames.join(', ')}
          </Text>
        </div>
      )}
    </Card>
  )
}

export default ClueCard
