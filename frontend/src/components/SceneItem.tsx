import { Card, Tooltip, Button } from 'antd'
import { SearchOutlined, EyeOutlined, LockOutlined } from '@ant-design/icons'

interface SceneItemProps {
  id: string
  name: string
  description: string
  image?: string
  isInvestigated: boolean
  hasClue: boolean
  isLocked: boolean
  onInvestigate: () => void
  onView: () => void
}

const SceneItem: React.FC<SceneItemProps> = ({
  name,
  description,
  image,
  isInvestigated,
  hasClue,
  isLocked,
  onInvestigate,
  onView,
}) => {
  return (
    <Card
      hoverable
      style={{
        width: 200,
        background: '#141414',
        border: `1px solid ${isInvestigated ? '#303030' : '#232323'}`,
        opacity: isLocked ? 0.5 : 1,
      }}
      className="card-hover"
      cover={
        image ? (
          <img
            alt={name}
            src={image}
            style={{
              height: 120,
              objectFit: 'cover',
              filter: isLocked ? 'grayscale(100%)' : 'none',
            }}
          />
        ) : (
          <div
            style={{
              height: 120,
              background: 'linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '32px',
              color: '#434343',
            }}
          >
            🔍
          </div>
        )
      }
      actions={[
        <Tooltip title="查看详情">
          <EyeOutlined
            key="view"
            onClick={(e) => {
              e.stopPropagation()
              onView()
            }}
            style={{ color: 'rgba(255,255,255,0.65)' }}
          />
        </Tooltip>,
        !isInvestigated && !isLocked ? (
          <Tooltip title="勘查">
            <SearchOutlined
              key="investigate"
              onClick={(e) => {
                e.stopPropagation()
                onInvestigate()
              }}
              style={{ color: '#722ed1' }}
            />
          </Tooltip>
        ) : isLocked ? (
          <Tooltip title="需要解锁">
            <LockOutlined key="locked" style={{ color: '#faad14' }} />
          </Tooltip>
        ) : (
          <Tooltip title="已勘查">
            <SearchOutlined key="investigated" style={{ color: '#52c41a' }} />
          </Tooltip>
        ),
      ]}
    >
      <Card.Meta
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ color: '#fff' }}>{name}</span>
            {hasClue && !isInvestigated && (
              <Tooltip title="这里可能有线索！">
                <span style={{ color: '#faad14', fontSize: '12px' }}>⭐</span>
              </Tooltip>
            )}
          </div>
        }
        description={
          <span style={{ color: 'rgba(255,255,255,0.45)', fontSize: '12px' }}>
            {isLocked ? '??? 该区域尚未解锁' : description}
          </span>
        }
      />
    </Card>
  )
}

export default SceneItem
