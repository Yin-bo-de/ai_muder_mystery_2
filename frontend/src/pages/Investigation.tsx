import { useState, useEffect, useRef } from 'react'
import { Typography, Row, Col, Card, Descriptions, Modal, Avatar, Tag, Collapse, Space, App as AntdApp, Button } from 'antd'
import { SearchOutlined, InfoCircleOutlined, TeamOutlined, BulbOutlined } from '@ant-design/icons'
import SceneItem from '@/components/SceneItem'
import ClueCard from '@/components/ClueCard'
import ClueAnalysisModal from '@/components/ClueAnalysisModal'
import { useGameStore } from '@/store/gameStore'
import { useClueStore } from '@/store/clueStore'
import { submitInvestigation, getClueStatistics, getClueHints } from '@/services/gameApi'
import type { Clue } from '@/types/game'

const { Title, Text, Paragraph } = Typography

const Investigation = () => {
  const [scenes, setScenes] = useState<any[]>([])
  const [selectedScene, setSelectedScene] = useState<any>(null)
  const [selectedSuspect, setSelectedSuspect] = useState<any>(null)
  const [investigating, setInvestigating] = useState(false)
  const [analysisModalVisible, setAnalysisModalVisible] = useState(false)
  const [selectedClue, setSelectedClue] = useState<Clue | null>(null)
  const [clueHints, setClueHints] = useState<Array<{ hint: string; scene: string }>>([])
  const [showHintBanner, setShowHintBanner] = useState(false)
  const { message } = AntdApp.useApp()

  // 追踪是否已经显示过线索提示错误（避免频繁打扰用户）
  const hasShownHintError = useRef(false)

  const { sessionId, caseInfo, suspects, totalCluesCount, updateCluesCount } = useGameStore()
  const { addClue, collectedClues } = useClueStore()

  useEffect(() => {
    // 从caseInfo获取场景数据
    if (caseInfo?.scenes) {
      const initialScenes = caseInfo.scenes.map((scene: any) => ({
        id: scene.scene_id,
        name: scene.name,
        description: scene.description,
        isInvestigated: false,
        hasClue: true,
        isLocked: scene.is_locked,
      }))
      setScenes(initialScenes)
    }

    // 获取线索统计信息，更新总线索数
    if (sessionId) {
      getClueStatistics(sessionId)
        .then(stats => {
          updateCluesCount(collectedClues.length, stats.total_clues)
        })
        .catch(err => {
          console.error('Failed to get clue statistics:', err)
        })
    }
  }, [caseInfo, sessionId, collectedClues.length, updateCluesCount])

  const handleInvestigate = async (sceneId: string) => {
    if (!sessionId) {
      message.error('游戏会话不存在，请重新开始')
      return
    }

    setInvestigating(true)
    try {
      const res = await submitInvestigation(sessionId, { scene: sceneId })

      if (res.clue_found) {
        const added = addClue(res.clue)
        if (added) {
          updateCluesCount(collectedClues.length + 1, totalCluesCount)
          message.success(`发现新线索：${res.clue.name}`)
        } else {
          message.info(`这条线索「${res.clue.name}」已经收集过了`)
        }
      } else {
        message.info('这里没有发现有价值的线索')
      }

      // 更新场景状态
      setScenes(scenes.map(scene =>
        scene.id === sceneId
          ? { ...scene, isInvestigated: true, hasClue: false }
          : scene
      ))

    } catch (error) {
      message.error('勘查失败，请重试')
    } finally {
      setInvestigating(false)
    }
  }

  const handleViewScene = (scene: any) => {
    setSelectedScene(scene)
  }

  const handleViewAnalysis = (clue: Clue) => {
    setSelectedClue(clue)
    setAnalysisModalVisible(true)
  }

  const fetchClueHints = async () => {
    if (!sessionId) return
    try {
      const hints = await getClueHints(sessionId)
      if (hints && hints.length > 0) {
        setClueHints(hints)
        setShowHintBanner(true)
      }
    } catch (error) {
      console.error('获取线索提示失败:', error)
      // 只在首次失败时提示用户，避免频繁打扰
      if (!hasShownHintError.current) {
        hasShownHintError.current = true
        message.warning('侦探提示服务暂时不可用，稍后会自动重试')
      }
    }
  }

  useEffect(() => {
    // 定期检查新线索提示（每30秒）
    fetchClueHints()
    const interval = setInterval(fetchClueHints, 30000)
    return () => clearInterval(interval)
  }, [sessionId])

  // 如果没有案件信息，显示加载状态
  if (!caseInfo) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '50vh',
        color: '#fff'
      }}>
        <Text>加载中...</Text>
      </div>
    )
  }

  return (
    <div>
      <Title level={2} style={{ color: '#fff', marginBottom: 24 }}>
        <SearchOutlined /> 现场勘查
      </Title>

      {/* 新线索提示横幅 */}
      {showHintBanner && clueHints.length > 0 && (
        <Card
          style={{
            marginBottom: 24,
            background: 'linear-gradient(135deg, rgba(114, 46, 209, 0.2) 0%, rgba(114, 46, 209, 0.1) 100%)',
            border: '1px solid #722ed1',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <BulbOutlined style={{ color: '#ffd700', fontSize: '24px' }} />
              <div>
                <Text strong style={{ color: '#fff', fontSize: '15px' }}>
                  🕵️ 侦探提示
                </Text>
                <div style={{ marginTop: 4 }}>
                  {clueHints.map((hint, index) => (
                    <Text key={index} style={{ color: 'rgba(255, 255, 255, 0.8)', display: 'block' }}>
                      • {hint.hint}
                    </Text>
                  ))}
                </div>
              </div>
            </div>
            <Button
              size="small"
              onClick={() => setShowHintBanner(false)}
              style={{ background: 'rgba(255, 255, 255, 0.1)', border: 'none', color: '#fff' }}
            >
              知道了
            </Button>
          </div>
        </Card>
      )}

      <Card style={{ marginBottom: 24, background: '#141414' }}>
        <Descriptions title="案发现场信息" column={2}>
          <Descriptions.Item label="地点">{caseInfo.scene}</Descriptions.Item>
          <Descriptions.Item label="死者">{caseInfo.victim_name}</Descriptions.Item>
          <Descriptions.Item label="死亡时间">{caseInfo.death_time}</Descriptions.Item>
          <Descriptions.Item label="死因">{caseInfo.death_cause}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Collapse
        defaultActiveKey={['1']}
        style={{ marginBottom: 24, background: '#141414', border: 'none' }}
        items={[
          {
            key: '1',
            label: <Space><InfoCircleOutlined /> 案件背景</Space>,
            children: (
              <Paragraph style={{ color: 'rgba(255,255,255,0.85)', fontSize: '15px', lineHeight: '1.8' }}>
                {caseInfo.description}
              </Paragraph>
            ),
          }
        ]}
      />

      <Card
        title={<Space><TeamOutlined /> 嫌疑人列表</Space>}
        style={{ marginBottom: 24, background: '#141414' }}
      >
        <Row gutter={[16, 16]}>
          {suspects.map(suspect => (
            <Col key={suspect.suspect_id} xs={24} sm={12} md={6}>
              <Card
                hoverable
                size="small"
                style={{ background: '#1e1e1e', border: '1px solid #303030', cursor: 'pointer' }}
                onClick={() => setSelectedSuspect(suspect)}
                bodyStyle={{ padding: '16px' }}
              >
                <Space>
                  <Avatar size={48} style={{ background: '#722ed1' }}>
                    {suspect.name.charAt(0)}
                  </Avatar>
                  <div>
                    <Text strong style={{ color: '#fff', fontSize: '16px' }}>{suspect.name}</Text>
                    <br />
                    <Tag color="purple" style={{ marginTop: '4px' }}>{suspect.occupation}</Tag>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {suspect.relationship_with_victim}
                    </Text>
                  </div>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      <Title level={4} style={{ color: '#fff', marginBottom: 16 }}>
        可勘查区域
      </Title>

      <Row gutter={[16, 16]} style={{ marginBottom: 32 }}>
        {scenes.map(scene => (
          <Col key={scene.id} xs={24} sm={12} md={8} lg={6}>
            <SceneItem
              {...scene}
              onInvestigate={() => handleInvestigate(scene.id)}
              onView={() => handleViewScene(scene)}
            />
          </Col>
        ))}
      </Row>

      {collectedClues.length > 0 && (
        <>
          <Title level={4} style={{ color: '#fff', marginBottom: 16 }}>
            本次勘查发现的线索
          </Title>
          <Row gutter={[16, 16]}>
            {collectedClues.slice(-3).map(clue => (
              <Col key={clue.clue_id} xs={24} sm={12} md={8}>
                <ClueCard
                  id={clue.clue_id}
                  name={clue.name}
                  description={clue.description}
                  type={(clue.type || clue.clue_type || 'physical').toLowerCase() as any}
                  status={(clue.status || 'discovered').toLowerCase() as any}
                  scene={clue.scene}
                  relatedSuspects={clue.related_suspects || []}
                  suspects={suspects}
                  onClick={() => handleViewAnalysis(clue)}
                />
              </Col>
            ))}
          </Row>
        </>
      )}

      <Modal
        title="场景详情"
        open={!!selectedScene}
        onCancel={() => setSelectedScene(null)}
        footer={null}
      >
        {selectedScene && (
          <>
            <Title level={4}>{selectedScene.name}</Title>
            <Text>{selectedScene.description}</Text>
          </>
        )}
      </Modal>

      <Modal
        title="嫌疑人信息"
        open={!!selectedSuspect}
        onCancel={() => setSelectedSuspect(null)}
        footer={null}
        width={600}
      >
        {selectedSuspect && (
          <>
            <Space style={{ marginBottom: '24px' }}>
              <Avatar size={64} style={{ background: '#722ed1' }}>
                {selectedSuspect.name.charAt(0)}
              </Avatar>
              <div>
                <Title level={3} style={{ margin: 0, marginBottom: '8px' }}>{selectedSuspect.name}</Title>
                <Tag color="purple">{selectedSuspect.occupation}</Tag>
                <Text type="secondary" style={{ marginLeft: '8px' }}>
                  {selectedSuspect.age}岁 · {selectedSuspect.gender}
                </Text>
              </div>
            </Space>

            <Descriptions column={1} bordered style={{ marginBottom: '16px' }}>
              <Descriptions.Item label="与死者关系">{selectedSuspect.relationship_with_victim}</Descriptions.Item>
              <Descriptions.Item label="初步描述">{selectedSuspect.description}</Descriptions.Item>
            </Descriptions>

            <Paragraph type="secondary">
              💡 提示：你可以在「质询嫌疑人」页面与嫌疑人对话，获取更多信息和证词。
            </Paragraph>
          </>
        )}
      </Modal>

      {/* 侦探分析笔记弹窗 */}
      <ClueAnalysisModal
        open={analysisModalVisible}
        onClose={() => setAnalysisModalVisible(false)}
        clue={selectedClue}
        suspects={suspects}
      />
    </div>
  )
}

export default Investigation
