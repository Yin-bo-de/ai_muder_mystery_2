import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Typography,
  Card,
  Row,
  Col,
  Button,
  Descriptions,
  Tag,
  Divider,
  List,
  Result,
  Statistic,
  Progress,
  Space,
  Avatar,
} from 'antd'
import {
  TrophyOutlined,
  CloseCircleOutlined,
  ReloadOutlined,
  HomeOutlined,
  UserOutlined,
} from '@ant-design/icons'
import type { AccuseResponse } from '@/services/gameApi'

const { Title, Text, Paragraph } = Typography

const Report = () => {
  const navigate = useNavigate()
  const [result, setResult] = useState<AccuseResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 从sessionStorage读取指认结果
    const resultStr = sessionStorage.getItem('accuseResult')
    if (resultStr) {
      try {
        const data = JSON.parse(resultStr)
        setResult(data)
      } catch (e) {
        console.error('Failed to parse accuse result:', e)
      }
    }
    setLoading(false)
  }, [])

  if (loading) {
    return (
      <div style={{ minHeight: '60vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <div style={{ color: '#fff' }}>加载中...</div>
      </div>
    )
  }

  if (!result) {
    return (
      <div style={{ minHeight: '60vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
        <Title level={3} style={{ color: '#fff', marginBottom: 24 }}>
          没有找到结案报告
        </Title>
        <Button type="primary" onClick={() => navigate('/')}>
          返回首页
        </Button>
      </div>
    )
  }

  const isCorrect = result.is_correct
  const { report, review } = result

  // 评分对应的等级和颜色
  const getScoreConfig = (score: number) => {
    if (score >= 90) return { color: '#52c41a', level: 'S级', desc: '完美推理' }
    if (score >= 80) return { color: '#1890ff', level: 'A级', desc: '优秀侦探' }
    if (score >= 70) return { color: '#13c2c2', level: 'B级', desc: '良好推理' }
    if (score >= 60) return { color: '#faad14', level: 'C级', desc: '合格侦探' }
    return { color: '#f5222d', level: 'D级', desc: '仍需努力' }
  }

  const scoreConfig = getScoreConfig(result.accuracy_score)

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px 0' }}>
      {/* 结果头部 */}
      <Card style={{ marginBottom: 24, border: 'none', background: 'transparent' }} bodyStyle={{ padding: 0 }}>
        <Result
          status={isCorrect ? 'success' : 'error'}
          icon={isCorrect ? <TrophyOutlined style={{ color: '#faad14' }} /> : <CloseCircleOutlined />}
          title={
            <span style={{ color: isCorrect ? '#52c41a' : '#f5222d', fontSize: '32px' }}>
              {report.title}
            </span>
          }
          subTitle={
            <div>
              <Paragraph style={{ fontSize: '16px', color: 'rgba(255,255,255,0.75)', margin: '8px 0 24px 0' }}>
                {report.description}
              </Paragraph>
              <Space size="large">
                <Statistic
                  title="推理准确率"
                  value={result.accuracy_score}
                  suffix="%"
                  valueStyle={{ color: scoreConfig.color }}
                />
                <Statistic
                  title="线索完成率"
                  value={result.clue_completion_rate}
                  suffix="%"
                  valueStyle={{ color: '#1890ff' }}
                />
                <Statistic
                  title="证据匹配度"
                  value={result.evidence_match_score}
                  suffix="%"
                  valueStyle={{ color: '#52c41a' }}
                />
              </Space>
            </div>
          }
          extra={
            <Space>
              <Button
                type="primary"
                icon={<ReloadOutlined />}
                onClick={() => {
                  sessionStorage.removeItem('accuseResult')
                  navigate('/game')
                }}
              >
                再玩一局
              </Button>
              <Button
                icon={<HomeOutlined />}
                onClick={() => {
                  sessionStorage.removeItem('accuseResult')
                  navigate('/')
                }}
              >
                返回首页
              </Button>
            </Space>
          }
        />
      </Card>

      <Row gutter={[24, 24]}>
        {/* 左侧：案件真相 */}
        <Col xs={24} lg={16}>
          <Card
            title={<Title level={4} style={{ color: '#fff', margin: 0 }}>🔍 案件真相</Title>}
            style={{ background: '#141414', border: '1px solid #303030' }}
          >
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="真凶" span={1}>
                <Space>
                  <Avatar size="small" icon={<UserOutlined />} />
                  <Text strong style={{ color: '#fff' }}>
                    {report.case_truth.murderer_name}
                  </Text>
                  <Tag color="red">{report.case_truth.murderer_occupation}</Tag>
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="侦探评级" span={1}>
                <Tag color={scoreConfig.color} style={{ fontSize: '14px', padding: '2px 12px' }}>
                  {review.rank}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="作案动机" span={2}>
                {report.case_truth.motive}
              </Descriptions.Item>
              <Descriptions.Item label="作案手法" span={2}>
                {report.case_truth.modus_operandi}
              </Descriptions.Item>
              <Descriptions.Item label="时间线" span={2}>
                {report.case_truth.time_line}
              </Descriptions.Item>
            </Descriptions>

            <Divider style={{ borderColor: '#303030', margin: '24px 0' }} />

            <Title level={5} style={{ color: '#fff', marginBottom: 16 }}>
              📌 关键证据
            </Title>
            <List
              dataSource={report.key_evidence}
              renderItem={(item) => (
                <List.Item style={{ borderBottom: '1px solid #303030' }}>
                  <List.Item.Meta
                    title={<Text strong style={{ color: '#fff' }}>{item.name}</Text>}
                    description={<Text type="secondary">{item.description}</Text>}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 右侧：探案评价 */}
        <Col xs={24} lg={8}>
          <Card
            title={<Title level={4} style={{ color: '#fff', margin: 0 }}>📊 探案评价</Title>}
            style={{ background: '#141414', border: '1px solid #303030', marginBottom: 24 }}
          >
            <div style={{ marginBottom: 24 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <Text type="secondary">综合评分</Text>
                <Text strong style={{ color: scoreConfig.color, fontSize: '20px' }}>
                  {result.accuracy_score}分
                </Text>
              </div>
              <Progress
                percent={result.accuracy_score}
                strokeColor={scoreConfig.color}
                size="small"
                showInfo={false}
              />
              <div style={{ textAlign: 'center', marginTop: 8 }}>
                <Tag color={scoreConfig.color}>{scoreConfig.level} · {scoreConfig.desc}</Tag>
              </div>
            </div>

            <Divider style={{ borderColor: '#303030', margin: '16px 0' }} />

            <div style={{ marginBottom: 16 }}>
              <Text strong style={{ color: '#52c41a' }}>✨ 推理亮点</Text>
              <List
                size="small"
                dataSource={report.player_performance.strengths}
                renderItem={(item) => (
                  <List.Item style={{ border: 'none', padding: '4px 0' }}>
                    <Text type="secondary">• {item}</Text>
                  </List.Item>
                )}
              />
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong style={{ color: '#faad14' }}>⚠️ 存在不足</Text>
              <List
                size="small"
                dataSource={report.player_performance.weaknesses}
                renderItem={(item) => (
                  <List.Item style={{ border: 'none', padding: '4px 0' }}>
                    <Text type="secondary">• {item}</Text>
                  </List.Item>
                )}
              />
            </div>

            <div>
              <Text strong style={{ color: '#1890ff' }}>💡 改进建议</Text>
              <List
                size="small"
                dataSource={report.player_performance.improvement_suggestions}
                renderItem={(item) => (
                  <List.Item style={{ border: 'none', padding: '4px 0' }}>
                    <Text type="secondary">• {item}</Text>
                  </List.Item>
                )}
              />
            </div>
          </Card>

          <Card
            title={<Title level={4} style={{ color: '#fff', margin: 0 }}>📈 游戏数据</Title>}
            style={{ background: '#141414', border: '1px solid #303030' }}
          >
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div>
                <Text type="secondary" style={{ fontSize: '12px' }}>游戏时长</Text>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#fff' }}>
                  {review.play_time} 分钟
                </div>
              </div>

              <div>
                <Text type="secondary" style={{ fontSize: '12px' }}>线索收集</Text>
                <div style={{ marginBottom: 4 }}>
                  <Text strong style={{ color: '#fff', fontSize: '20px' }}>{review.clues_collected}</Text>
                  <Text type="secondary">/{review.total_clues} 条</Text>
                </div>
                <Progress
                  percent={Math.round((review.clues_collected / review.total_clues) * 100)}
                  size="small"
                  strokeColor="#722ed1"
                  showInfo={false}
                />
              </div>

              <div>
                <Text type="secondary" style={{ fontSize: '12px' }}>对话次数</Text>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#fff' }}>
                  {review.dialogue_count} 次
                </div>
              </div>

              <div>
                <Text type="secondary" style={{ fontSize: '12px' }}>错误指认</Text>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f5222d' }}>
                  {review.wrong_guess_count} 次
                </div>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* 侦探评语 */}
      <Card style={{ background: '#141414', border: '1px solid #303030', marginTop: 24 }}>
        <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
          <Avatar size={64} style={{ background: '#722ed1' }}>
            <UserOutlined />
          </Avatar>
          <div style={{ flex: 1 }}>
            <Title level={4} style={{ color: '#fff', marginBottom: 8 }}>
              侦探评语
            </Title>
            <Paragraph style={{ color: 'rgba(255,255,255,0.75)', fontSize: '16px', lineHeight: 1.8 }}>
              {review.comment}
            </Paragraph>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default Report
