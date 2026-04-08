import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Spin, Typography, Card, Progress, App as AntdApp } from 'antd'
import { useGameStore } from '@/store/gameStore'
import { createNewCase, type CreateGameResponse } from '@/services/gameApi'

const { Title, Paragraph } = Typography

const Game = () => {
  const navigate = useNavigate()
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState(false)
  const { message } = AntdApp.useApp()
  const { setSessionId, setCaseInfo, setGameStatus, setSuspects, updateCluesCount } = useGameStore()
  const initialized = useRef(false)
  const navigatingRef = useRef(false)

  useEffect(() => {
    // 防止重复初始化
    if (initialized.current) return
    initialized.current = true

    let progressInterval: NodeJS.Timeout | null = null

    const initGame = async () => {
      try {
        // 模拟进度条
        progressInterval = setInterval(() => {
          setProgress(prev => {
            if (prev >= 90) {
              if (progressInterval) clearInterval(progressInterval)
              return prev
            }
            return prev + 10
          })
        }, 300)

        // 调用API创建新案件
        const res: CreateGameResponse = await createNewCase({
          difficulty: 'medium',
        })

        if (progressInterval) clearInterval(progressInterval)
        setProgress(100)

        // 更新全局状态
        setSessionId(res.session_id)
        setCaseInfo({
          ...res.case_basic_info,
          scenes: res.scenes,
        })
        setSuspects(res.suspects)
        setGameStatus('in_progress')
        updateCluesCount(0, 0)

        message.success('案件生成成功！开始你的探案之旅吧')

        // 延迟后跳转到现场勘查页面 - 确保状态已更新
        navigatingRef.current = true
        setTimeout(() => {
          navigate('/investigation', { replace: true })
        }, 800)

      } catch (error: any) {
        console.error('[Game] 创建案件失败:', error)
        setError(true)
        message.error('案件生成失败，请重试')
      }
    }

    initGame()

    return () => {
      if (progressInterval) clearInterval(progressInterval)
    }
  }, [setSessionId, setCaseInfo, setSuspects, setGameStatus, updateCluesCount, navigate, message])

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)',
    }}>
      <Card
        style={{
          maxWidth: 600,
          width: '90%',
          background: 'rgba(20, 20, 20, 0.9)',
          border: '1px solid #303030',
          textAlign: 'center',
          boxShadow: '0 8px 32px rgba(114, 46, 209, 0.3)',
        }}
        styles={{ body: { padding: '48px 32px' } }}
      >
        {!error ? (
          <>
            <Spin size="large" style={{ marginBottom: '32px' }} />
            <Title level={3} style={{ color: '#722ed1', marginBottom: '16px' }}>
              案件生成中...
            </Title>
            <Paragraph style={{ color: 'rgba(255,255,255,0.65)', marginBottom: '32px' }}>
              AI正在精心构思案件剧情、人物关系和证据链，请稍候...
            </Paragraph>
            <Progress
              percent={progress}
              strokeColor={{
                '0%': '#722ed1',
                '100%': '#9254de',
              }}
              showInfo={false}
            />
            <Paragraph style={{ color: 'rgba(255,255,255,0.45)', fontSize: '12px', marginTop: '16px' }}>
              {progress < 30 ? '正在构思案件背景...' :
               progress < 60 ? '正在设计人物关系和作案手法...' :
               progress < 90 ? '正在布置线索和证据链...' : '生成完成，即将进入游戏...'}
            </Paragraph>
          </>
        ) : (
          <>
            <Title level={3} style={{ color: '#f5222d', marginBottom: '16px' }}>
              案件生成失败
            </Title>
            <Paragraph style={{ color: 'rgba(255,255,255,0.65)', marginBottom: '32px' }}>
              抱歉，案件生成过程中出现错误，请点击下方按钮重试。
            </Paragraph>
            <button
              onClick={() => window.location.reload()}
              style={{
                background: '#722ed1',
                color: '#fff',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '16px',
              }}
            >
              重新生成
            </button>
          </>
        )}
      </Card>
    </div>
  )
}

export default Game
