import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Typography,
  Card,
  Row,
  Col,
  Form,
  Input,
  Select,
  Button,
  message,
  Steps,
  Alert,
  Progress,
  Space,
  Tag,
  Modal,
} from 'antd'
import { WarningOutlined, CheckCircleOutlined, SearchOutlined } from '@ant-design/icons'
import SuspectAvatar from '@/components/SuspectAvatar'
import { useGameStore } from '@/store/gameStore'
import { useClueStore } from '@/store/clueStore'
import { submitAccusation, type AccuseRequest, type AccuseResponse } from '@/services/gameApi'

const { Title, Text, Paragraph } = Typography
const { Step } = Steps
const { TextArea } = Input
const { Option } = Select

const Accuse = () => {
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [selectedSuspect, setSelectedSuspect] = useState<string | null>(null)
  const [confirmVisible, setConfirmVisible] = useState(false)
  const [accuseResult, setAccuseResult] = useState<AccuseResponse | null>(null)

  const { sessionId, suspects, wrongGuessCount, maxWrongGuess = 2 } = useGameStore()
  const { collectedClues } = useClueStore()

  useEffect(() => {
    if (!sessionId) {
      message.error('请先开始游戏')
      navigate('/')
    }
  }, [sessionId, navigate])

  // 剩余指认次数
  const remainingAttempts = maxWrongGuess - wrongGuessCount
  const canAccuse = remainingAttempts > 0

  // 步骤配置
  const steps = [
    { title: '选择嫌疑人', description: '选择你认为的真凶' },
    { title: '陈述推理', description: '说明动机和作案手法' },
    { title: '提交证据', description: '选择支持你推理的证据' },
    { title: '确认提交', description: '确认你的指认' },
  ]

  const handleNextStep = () => {
    if (currentStep === 0 && !selectedSuspect) {
      message.warning('请先选择你认为的凶手')
      return
    }

    form.validateFields([currentStep === 1 ? ['motive', 'modus_operandi'] : 'evidence'])
      .then(() => {
        if (currentStep < steps.length - 1) {
          setCurrentStep(currentStep + 1)
        } else {
          setConfirmVisible(true)
        }
      })
      .catch(() => {
        message.error('请完善当前步骤的信息')
      })
  }

  const handlePrevStep = () => {
    setCurrentStep(currentStep - 1)
  }

  const handleSelectSuspect = (suspectId: string) => {
    setSelectedSuspect(suspectId)
    form.setFieldValue('suspect_id', suspectId)
  }

  const handleSubmitAccusation = async () => {
    if (!sessionId || !selectedSuspect) return

    setLoading(true)
    setConfirmVisible(false)

    try {
      const values = await form.validateFields()
      const params: AccuseRequest = {
        suspect_id: selectedSuspect,
        motive: values.motive,
        modus_operandi: values.modus_operandi,
        evidence: values.evidence || [],
      }

      const result = await submitAccusation(sessionId, params)
      setAccuseResult(result)

      message.success('指认提交成功！')

      // 存储结果到sessionStorage，跳转到报告页面
      sessionStorage.setItem('accuseResult', JSON.stringify(result))
      navigate('/report')

    } catch (error: any) {
      if (error?.response?.data?.code === 10002) {
        // 游戏已结束，跳转到报告页面
        navigate('/report')
      } else {
        message.error('提交指认失败，请重试')
      }
    } finally {
      setLoading(false)
    }
  }

  // 获取选中的嫌疑人信息
  const selectedSuspectInfo = suspects.find(s => s.suspect_id === selectedSuspect)

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto' }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={2} style={{ color: '#fff', marginBottom: 16 }}>
          <SearchOutlined /> 指认凶手
        </Title>

        <Alert
          showIcon
          type={remainingAttempts > 1 ? 'warning' : 'error'}
          message={`剩余指认机会：${remainingAttempts}次`}
          description={remainingAttempts === 1 ? '这是最后一次机会，请谨慎选择！' : '错误超过2次游戏会直接结束，请慎重考虑。'}
          style={{ marginBottom: 24 }}
        />
      </div>

      <Steps current={currentStep} items={steps} style={{ marginBottom: 32 }} />

      <Card style={{ background: '#141414', border: '1px solid #303030' }} bodyStyle={{ padding: '32px' }}>
        <Form form={form} layout="vertical">
          {/* 步骤1：选择嫌疑人 */}
          {currentStep === 0 && (
            <div>
              <Title level={4} style={{ color: '#fff', marginBottom: 24 }}>
                请选择你认为的凶手：
              </Title>
              <Row gutter={[24, 24]}>
                {suspects.map(suspect => (
                  <Col key={suspect.suspect_id} xs={24} sm={12} md={8}>
                    <div
                      onClick={() => canAccuse && handleSelectSuspect(suspect.suspect_id)}
                      style={{
                        padding: '16px',
                        border: `2px solid ${selectedSuspect === suspect.suspect_id ? '#722ed1' : '#303030'}`,
                        borderRadius: 8,
                        background: selectedSuspect === suspect.suspect_id ? 'rgba(114, 46, 209, 0.1)' : '#1e1e1e',
                        cursor: canAccuse ? 'pointer' : 'not-allowed',
                        opacity: canAccuse ? 1 : 0.6,
                      }}
                      className="card-hover"
                    >
                      <div style={{ display: 'flex', gap: 16, alignItems: 'center', marginBottom: 12 }}>
                        <SuspectAvatar
                          name={suspect.name}
                          mood="calm"
                          stressLevel={0}
                          size="small"
                        />
                        <div>
                          <Text strong style={{ color: '#fff', fontSize: '16px' }}>{suspect.name}</Text>
                          <p style={{ color: 'rgba(255,255,255,0.65)', fontSize: '12px', margin: 0 }}>
                            {suspect.occupation}
                          </p>
                        </div>
                      </div>
                      <Paragraph style={{ color: 'rgba(255,255,255,0.65)', fontSize: '13px', margin: 0 }}>
                        与死者关系：{suspect.relationship_with_victim}
                      </Paragraph>
                    </div>
                  </Col>
                ))}
              </Row>
            </div>
          )}

          {/* 步骤2：陈述推理 */}
          {currentStep === 1 && selectedSuspectInfo && (
            <div>
              <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center', gap: 16 }}>
                <SuspectAvatar
                  name={selectedSuspectInfo.name}
                  mood="calm"
                  stressLevel={0}
                  size="small"
                />
                <div>
                  <Title level={4} style={{ color: '#fff', margin: 0 }}>
                    你指认的凶手是：{selectedSuspectInfo.name}
                  </Title>
                  <Text type="secondary">{selectedSuspectInfo.occupation}</Text>
                </div>
              </div>

              <Form.Item
                name="motive"
                label="你认为他/她的作案动机是什么？"
                rules={[{ required: true, message: '请描述作案动机' }]}
              >
                <TextArea
                  rows={4}
                  placeholder="请详细描述你推理的作案动机..."
                  style={{ background: '#1e1e1e', border: '1px solid #303030', color: '#fff' }}
                />
              </Form.Item>

              <Form.Item
                name="modus_operandi"
                label="你认为他/她的作案手法是怎样的？"
                rules={[{ required: true, message: '请描述作案手法' }]}
              >
                <TextArea
                  rows={6}
                  placeholder="请详细描述作案过程、时间线、使用的凶器等..."
                  style={{ background: '#1e1e1e', border: '1px solid #303030', color: '#fff' }}
                />
              </Form.Item>
            </div>
          )}

          {/* 步骤3：提交证据 */}
          {currentStep === 2 && (
            <div>
              <Title level={4} style={{ color: '#fff', marginBottom: 24 }}>
                请选择能够支持你推理的关键证据（可多选）：
              </Title>

              {collectedClues.length === 0 ? (
                <Alert
                  type="warning"
                  message="你还没有收集到任何线索，无法提交证据"
                  showIcon
                />
              ) : (
                <>
                  <Alert
                    type="info"
                    message={`当前已收集 ${collectedClues.length} 条线索，请选择最关键的证据来支持你的推理`}
                    showIcon
                    style={{ marginBottom: 24 }}
                  />

                  <Form.Item
                    name="evidence"
                    rules={[{ required: true, message: '请至少选择一个证据' }]}
                  >
                    <Select
                      mode="multiple"
                      placeholder="选择关键证据"
                      style={{ width: '100%' }}
                      maxTagCount="responsive"
                    >
                      {collectedClues.map(clue => (
                        <Option key={clue.clue_id} value={clue.clue_id}>
                          <Space>
                            <Tag color={
                              clue.type === 'physical' ? '#1890ff' :
                              clue.type === 'testimony' ? '#52c41a' :
                              clue.type === 'association' ? '#faad14' : '#722ed1'
                            }>
                              {clue.type === 'physical' ? '物证' :
                               clue.type === 'testimony' ? '证词' :
                               clue.type === 'association' ? '关联' : '解密'}
                            </Tag>
                            {clue.name}
                          </Space>
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>

                  <div style={{ marginTop: 16 }}>
                    <Text strong style={{ color: '#fff' }}>已选证据：</Text>
                    <div style={{ marginTop: 8, display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                      {form.getFieldValue('evidence')?.map((id: string) => {
                        const clue = collectedClues.find(c => c.clue_id === id)
                        return clue ? (
                          <Tag key={id} color="blue">
                            {clue.name}
                          </Tag>
                        ) : null
                      })}
                    </div>
                  </div>
                </>
              )}
            </div>
          )}

          {/* 步骤4：确认提交 */}
          {currentStep === 3 && (
            <div>
              <Title level={4} style={{ color: '#fff', marginBottom: 24 }}>
                确认你的指认信息：
              </Title>

              <Card style={{ background: '#1e1e1e', border: '1px solid #303030', marginBottom: 24 }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text strong style={{ color: '#fff', minWidth: 80, display: 'inline-block' }}>指认凶手：</Text>
                    <Text style={{ color: 'rgba(255,255,255,0.85)' }}>
                      {selectedSuspectInfo?.name} ({selectedSuspectInfo?.occupation})
                    </Text>
                  </div>
                  <div>
                    <Text strong style={{ color: '#fff', minWidth: 80, display: 'inline-block' }}>作案动机：</Text>
                    <Text style={{ color: 'rgba(255,255,255,0.85)' }}>{form.getFieldValue('motive')}</Text>
                  </div>
                  <div>
                    <Text strong style={{ color: '#fff', minWidth: 80, display: 'inline-block' }}>作案手法：</Text>
                    <Text style={{ color: 'rgba(255,255,255,0.85)' }}>{form.getFieldValue('modus_operandi')}</Text>
                  </div>
                  <div>
                    <Text strong style={{ color: '#fff', minWidth: 80, display: 'inline-block' }}>提交证据：</Text>
                    <div style={{ marginTop: 4, display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                      {form.getFieldValue('evidence')?.map((id: string) => {
                        const clue = collectedClues.find(c => c.clue_id === id)
                        return clue ? <Tag key={id} size="small">{clue.name}</Tag> : null
                      })}
                    </div>
                  </div>
                </Space>
              </Card>

              <Alert
                showIcon
                type="warning"
                icon={<WarningOutlined />}
                title="请谨慎确认"
                description="提交后将无法修改，如果指认错误将会消耗一次机会，错误2次游戏将直接结束。"
              />
            </div>
          )}

          {/* 操作按钮 */}
          <div style={{ marginTop: 32, display: 'flex', justifyContent: 'space-between' }}>
            <Button
              disabled={currentStep === 0 || loading}
              onClick={handlePrevStep}
            >
              上一步
            </Button>

            <Space>
              <Button
                type="default"
                onClick={() => navigate('/investigation')}
                disabled={loading}
              >
                返回继续调查
              </Button>

              <Button
                type="primary"
                danger={currentStep === steps.length - 1}
                onClick={handleNextStep}
                loading={loading}
                disabled={!canAccuse}
              >
                {currentStep === steps.length - 1 ? '提交指认' : '下一步'}
              </Button>
            </Space>
          </div>
        </Form>
      </Card>

      {/* 确认弹窗 */}
      <Modal
        title="确认提交指认？"
        open={confirmVisible}
        onOk={handleSubmitAccusation}
        onCancel={() => setConfirmVisible(false)}
        okText="确认提交"
        cancelText="取消"
        okButtonProps={{ danger: true, loading }}
      >
        <p>你确定要提交指认吗？这将消耗一次指认机会。</p>
        <p>当前剩余机会：<strong style={{ color: '#faad14' }}>{remainingAttempts}次</strong></p>
      </Modal>
    </div>
  )
}

export default Accuse
