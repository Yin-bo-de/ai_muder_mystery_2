import { ReactNode, useState, useEffect } from 'react'
import { Layout, Menu, Button, Badge, Space, Typography, Progress, message } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  HomeOutlined,
  SearchOutlined,
  MessageOutlined,
  FolderOpenOutlined,
  UserOutlined,
  FileTextOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons'
import { useGameStore } from '@/store/gameStore'
import { useClueStore } from '@/store/clueStore'

const { Header, Sider, Content } = Layout
const { Text } = Typography

interface GameLayoutProps {
  children: ReactNode
}

const GameLayout: React.FC<GameLayoutProps> = ({ children }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)
  const [playTime, setPlayTime] = useState(0)

  const { sessionId, currentMode, playTime: storePlayTime, incrementPlayTime, collectedCluesCount, totalCluesCount } = useGameStore()
  const { collectedClues } = useClueStore()

  // 路由守卫：检查是否有有效的游戏会话
  useEffect(() => {
    if (!sessionId) {
      message.error('请先开始新案件')
      navigate('/')
    }
  }, [sessionId, navigate])

  // 游戏计时器
  useEffect(() => {
    const timer = setInterval(() => {
      incrementPlayTime()
      setPlayTime(storePlayTime)
    }, 1000)

    return () => clearInterval(timer)
  }, [incrementPlayTime, storePlayTime])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const menuItems = [
    {
      key: '/investigation',
      icon: <SearchOutlined />,
      label: '现场勘查',
    },
    {
      key: '/interrogation',
      icon: <MessageOutlined />,
      label: '质询嫌疑人',
    },
    {
      key: '/clues',
      icon: <FolderOpenOutlined />,
      label: '线索库',
      badge: collectedClues.length,
    },
    {
      key: '/accuse',
      icon: <UserOutlined />,
      label: '指认凶手',
    },
    {
      key: '/report',
      icon: <FileTextOutlined />,
      label: '结案报告',
    },
  ]

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  const clueCompletionRate = totalCluesCount > 0 ? Math.round((collectedCluesCount / totalCluesCount) * 100) : 0

  return (
    <Layout style={{ minHeight: '100vh', background: '#0a0a0a' }}>
      <Header
        style={{
          background: '#141414',
          borderBottom: '1px solid #303030',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <Button
            type="text"
            icon={<HomeOutlined />}
            onClick={() => navigate('/')}
            style={{ color: '#fff', fontSize: '18px' }}
          />
          <Text strong style={{ color: '#722ed1', fontSize: '20px' }}>
            🔍 AI侦探社
          </Text>
        </div>

        <Space size="large">
          <Space>
            <ClockCircleOutlined style={{ color: '#faad14' }} />
            <Text style={{ color: '#fff' }}>{formatTime(playTime)}</Text>
          </Space>

          <div style={{ width: 150 }}>
            <Progress
              percent={clueCompletionRate}
              size="small"
              strokeColor="#722ed1"
              format={(percent) => `线索 ${percent}%`}
            />
          </div>

          <Badge count={collectedClues.length} color="#722ed1">
            <Button
              type="primary"
              icon={<FolderOpenOutlined />}
              onClick={() => navigate('/clues')}
            >
              线索库
            </Button>
          </Badge>
        </Space>
      </Header>

      <Layout>
        <Sider
          width={200}
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          style={{ background: '#141414', borderRight: '1px solid #303030' }}
        >
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            style={{ height: '100%', borderRight: 0, background: '#141414' }}
            items={menuItems.map((item) => ({
              key: item.key,
              icon: item.icon,
              label: item.badge ? (
                <Badge count={item.badge} offset={[10, 0]} color="#722ed1">
                  {item.label}
                </Badge>
              ) : (
                item.label
              ),
            }))}
            onClick={handleMenuClick}
          />
        </Sider>

        <Content
          style={{
            margin: '24px',
            minHeight: 280,
            background: '#0a0a0a',
            overflow: 'auto',
          }}
        >
          {children}
        </Content>
      </Layout>
    </Layout>
  )
}

export default GameLayout
