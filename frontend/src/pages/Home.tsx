import { Button, Card, Typography, Space, App as AntdApp } from 'antd'
import { useNavigate } from 'react-router-dom'
import { PlayCircleOutlined, BookOutlined, TrophyOutlined } from '@ant-design/icons'

const { Title, Paragraph } = Typography

const Home = () => {
  const navigate = useNavigate()
  const { message } = AntdApp.useApp()

  const startNewGame = () => {
    navigate('/game')
  }

  const showUnderDevelopment = () => {
    message.info('功能开发中，敬请期待')
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)',
      padding: '24px',
    }}>
      <Card
        style={{
          maxWidth: 800,
          width: '100%',
          background: 'rgba(20, 20, 20, 0.9)',
          backdropFilter: 'blur(10px)',
          border: '1px solid #303030',
          borderRadius: '16px',
          boxShadow: '0 8px 32px rgba(114, 46, 209, 0.3)',
        }}
        styles={{ body: { padding: '64px 48px' } }}
      >
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <Title level={1} style={{ color: '#722ed1', marginBottom: '16px', fontSize: '48px' }}>
            🔍 AI侦探社
          </Title>
          <Paragraph style={{ fontSize: '18px', color: 'rgba(255,255,255,0.75)', marginBottom: 0 }}>
            沉浸式AI驱动案件解谜体验，无需读本，无需队友，随时开启探案之旅
          </Paragraph>
        </div>

        <Space orientation="vertical" size="large" style={{ width: '100%' }}>
          <Button
            type="primary"
            size="large"
            icon={<PlayCircleOutlined />}
            onClick={startNewGame}
            style={{
              height: '56px',
              fontSize: '18px',
              background: 'linear-gradient(135deg, #722ed1 0%, #9254de 100%)',
              border: 'none',
              boxShadow: '0 4px 16px rgba(114, 46, 209, 0.4)',
            }}
            block
          >
            开始新案件
          </Button>

          <Space style={{ width: '100%' }}>
            <Button
              size="large"
              icon={<BookOutlined />}
              onClick={showUnderDevelopment}
              style={{
                flex: 1,
                height: '48px',
                background: '#1e1e1e',
                border: '1px solid #303030',
                color: 'rgba(255,255,255,0.85)',
              }}
            >
              案件记录
            </Button>
            <Button
              size="large"
              icon={<TrophyOutlined />}
              onClick={showUnderDevelopment}
              style={{
                flex: 1,
                height: '48px',
                background: '#1e1e1e',
                border: '1px solid #303030',
                color: 'rgba(255,255,255,0.85)',
              }}
            >
              成就系统
            </Button>
          </Space>
        </Space>

        <div style={{ marginTop: '48px', textAlign: 'center' }}>
          <Paragraph style={{ color: 'rgba(255,255,255,0.45)', fontSize: '14px' }}>
            🌌 每个案件由AI独立。生成，剧情独一无二，逻辑严谨自洽
          </Paragraph>
        </div>
      </Card>
    </div>
  )
}

export default Home
