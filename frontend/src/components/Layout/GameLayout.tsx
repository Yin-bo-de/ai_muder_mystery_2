import { ReactNode, useState, useEffect, useMemo, useCallback, useRef } from 'react'
import { Layout, Menu, Button, Badge, Space, Typography, Progress, App as AntdApp } from 'antd'
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
  const { message } = AntdApp.useApp()

  // 稳定的 state 选择，避免不必要的重渲染
  const incrementPlayTime = useGameStore(state => state.incrementPlayTime)
  const sessionId = useGameStore(state => state.sessionId)
  const playTime = useGameStore(state => state.playTime)
  const collectedCluesCount = useGameStore(state => state.collectedCluesCount)
  const totalCluesCount = useGameStore(state => state.totalCluesCount)
  const collectedCluesLength = useClueStore(state => state.collectedClues.length)

  // 使用 ref 记录是否已经重定向，避免重复导航
  const redirectedRef = useRef(false)

  // 路由守卫：检查是否有有效的游戏会话
  useEffect(() => {
    if (sessionId) {
      // 有 sessionId，确保不重定向
      redirectedRef.current = false
      return
    }

    // 没有 sessionId，需要重定向
    if (!redirectedRef.current) {
      redirectedRef.current = true
      message.error('请先开始新案件')
      navigate('/')
    }
  }, [sessionId, navigate, message])

  // 游戏计时器 - 只依赖sessionId变化时设置
  useEffect(() => {
    if (!sessionId) return  // 没有会话时不启动计时器

    const timer = setInterval(() => {
      incrementPlayTime()
    }, 1000)

    return () => clearInterval(timer)
  }, [sessionId, incrementPlayTime])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  // 使用 useMemo 缓存 menuItems，避免每次渲染都创建新数组
  const menuItems = useMemo(() => [
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
      badge: collectedCluesLength,
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
  ], [collectedCluesLength])

  // 使用 useCallback 稳定 handleMenuClick
  const handleMenuClick = useCallback(({ key }: { key: string }) => {
    navigate(key)
  }, [navigate])

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

          <Badge count={collectedCluesLength} color="#722ed1">
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
            items={menuItems}
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
