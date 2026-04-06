import { useState, useEffect } from 'react'
import { Typography, Row, Col, Tabs, Empty, Spin, message, Tag, Button, Modal, Form, Select } from 'antd'
import { FolderOpenOutlined, SearchOutlined, UnlockOutlined, LinkOutlined } from '@ant-design/icons'
import ClueCard from '@/components/ClueCard'
import { useGameStore } from '@/store/gameStore'
import { useClueStore } from '@/store/clueStore'
import { getCollectedClues, getClueStatistics, associateClues, decryptClue } from '@/services/gameApi'
import type { Clue, ClueType } from '@/types/game'

const { Title, Text } = Typography
const { TabPane } = Tabs
const { Option } = Select

const ClueLibrary = () => {
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<string>('all')
  const [statistics, setStatistics] = useState<any>(null)
  const [associateModalVisible, setAssociateModalVisible] = useState(false)
  const [decryptModalVisible, setDecryptModalVisible] = useState(false)
  const [selectedClue, setSelectedClue] = useState<Clue | null>(null)
  const [selectedCluesForAssociation, setSelectedCluesForAssociation] = useState<string[]>([])
  const [form] = Form.useForm()

  const { sessionId } = useGameStore()
  const { collectedClues, setCollectedClues, getClueById } = useClueStore()

  // 加载线索数据
  useEffect(() => {
    if (!sessionId) return
    loadClues()
  }, [sessionId, activeTab])

  const loadClues = async () => {
    setLoading(true)
    try {
      // 加载线索列表
      const type = activeTab === 'all' ? undefined : activeTab as ClueType
      const clues = await getCollectedClues(sessionId, type)
      setCollectedClues(clues)

      // 加载统计信息
      const stats = await getClueStatistics(sessionId)
      setStatistics(stats)
    } catch (error) {
      message.error('加载线索失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDecrypt = async (clue: Clue) => {
    setSelectedClue(clue)
    setDecryptModalVisible(true)
  }

  const handleDecryptSubmit = async () => {
    if (!sessionId || !selectedClue) return

    try {
      const values = await form.validateFields()
      await decryptClue(sessionId, {
        clue_id: selectedClue.clue_id,
        password: values.password,
      })

      message.success('解密成功！')
      setDecryptModalVisible(false)
      form.resetFields()
      loadClues() // 重新加载线索
    } catch (error) {
      message.error('解密失败，请检查密码是否正确')
    }
  }

  const handleAssociate = () => {
    if (collectedClues.length < 2) {
      message.warning('至少需要2条线索才能进行关联')
      return
    }
    setAssociateModalVisible(true)
  }

  const handleAssociateSubmit = async () => {
    if (!sessionId || selectedCluesForAssociation.length < 2) {
      message.warning('请至少选择2条线索')
      return
    }

    try {
      const result = await associateClues(sessionId, selectedCluesForAssociation)
      if (result.success) {
        message.success(result.message)
        setAssociateModalVisible(false)
        setSelectedCluesForAssociation([])
        loadClues() // 重新加载线索
      } else {
        message.warning(result.message)
      }
    } catch (error) {
      message.error('关联失败')
    }
  }

  const filteredClues = collectedClues.filter(clue => {
    if (activeTab === 'all') return true
    if (activeTab === 'decrypted') return clue.status === 'decrypted'
    if (activeTab === 'associated') return clue.status === 'associated'
    return clue.type === activeTab
  })

  const typeOptions = [
    { value: 'physical', label: '物证', color: '#1890ff' },
    { value: 'testimony', label: '证词', color: '#52c41a' },
    { value: 'association', label: '关联线索', color: '#faad14' },
    { value: 'decrypted', label: '解密线索', color: '#722ed1' },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2} style={{ color: '#fff', margin: 0 }}>
          <FolderOpenOutlined /> 线索库
        </Title>
        <Button
          type="primary"
          icon={<LinkOutlined />}
          onClick={handleAssociate}
          disabled={collectedClues.length < 2}
        >
          关联线索
        </Button>
      </div>

      {/* 统计信息 */}
      {statistics && (
        <div style={{ marginBottom: 24, display: 'flex', gap: 24, flexWrap: 'wrap' }}>
          <div style={{ background: '#141414', padding: '16px 24px', borderRadius: 8, border: '1px solid #303030' }}>
            <Text type="secondary" style={{ fontSize: '12px' }}>线索收集率</Text>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#722ed1' }}>
              {statistics.completion_rate}%
            </div>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {statistics.collected_clues}/{statistics.total_clues} 条
            </Text>
          </div>
          {typeOptions.map(type => (
            <div key={type.value} style={{ background: '#141414', padding: '16px 24px', borderRadius: 8, border: '1px solid #303030' }}>
              <Text type="secondary" style={{ fontSize: '12px' }}>{type.label}</Text>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: type.color }}>
                {statistics.type_statistics[type.value] || 0}
              </div>
            </div>
          ))}
        </div>
      )}

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        style={{ marginBottom: 24 }}
        items={[
          { key: 'all', label: '全部线索' },
          { key: 'physical', label: '物证' },
          { key: 'testimony', label: '证词' },
          { key: 'association', label: '关联线索' },
          { key: 'decrypted', label: '解密线索' },
        ]}
      />

      <Spin spinning={loading}>
        {filteredClues.length === 0 ? (
          <Empty
            description={`暂无${activeTab === 'all' ? '' : typeOptions.find(t => t.value === activeTab)?.label}线索`}
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            style={{ background: '#141414', padding: '48px 0', borderRadius: 8 }}
          />
        ) : (
          <Row gutter={[16, 16]}>
            {filteredClues.map(clue => (
              <Col key={clue.clue_id} xs={24} sm={12} md={8} lg={6}>
                <ClueCard
                  id={clue.clue_id}
                  name={clue.name}
                  description={clue.description}
                  type={clue.type}
                  status={clue.status}
                  scene={clue.scene}
                  relatedSuspects={clue.related_suspects}
                  onDecrypt={() => handleDecrypt(clue)}
                  onAssociate={() => {
                    setSelectedCluesForAssociation([clue.clue_id])
                    setAssociateModalVisible(true)
                  }}
                />
              </Col>
            ))}
          </Row>
        )}
      </Spin>

      {/* 解密弹窗 */}
      <Modal
        title="解密线索"
        open={decryptModalVisible}
        onCancel={() => setDecryptModalVisible(false)}
        onOk={handleDecryptSubmit}
        okText="解密"
        cancelText="取消"
      >
        {selectedClue && (
          <Form form={form} layout="vertical">
            <div style={{ marginBottom: 16 }}>
              <Text strong>线索：{selectedClue.name}</Text>
              <p style={{ color: 'rgba(255,255,255,0.65)', marginTop: 8 }}>
                {selectedClue.description}
              </p>
            </div>
            <Form.Item
              name="password"
              label="请输入解密密码"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password placeholder="请输入密码" />
            </Form.Item>
          </Form>
        )}
      </Modal>

      {/* 关联线索弹窗 */}
      <Modal
        title="关联线索"
        open={associateModalVisible}
        onCancel={() => setAssociateModalVisible(false)}
        onOk={handleAssociateSubmit}
        okText="关联"
        cancelText="取消"
        width={600}
      >
        <Form layout="vertical">
          <Form.Item
            label="请选择要关联的线索（至少2条）"
            rules={[{ required: true, message: '请选择线索' }]}
          >
            <Select
              mode="multiple"
              placeholder="选择要关联的线索"
              value={selectedCluesForAssociation}
              onChange={setSelectedCluesForAssociation}
              style={{ width: '100%' }}
            >
              {collectedClues.map(clue => (
                <Option key={clue.clue_id} value={clue.clue_id}>
                  {clue.name}
                  <Tag color={typeOptions.find(t => t.value === clue.type)?.color} style={{ marginLeft: 8 }}>
                    {typeOptions.find(t => t.value === clue.type)?.label}
                  </Tag>
                </Option>
              ))}
            </Select>
          </Form.Item>

          {selectedCluesForAssociation.length >= 2 && (
            <div style={{ background: '#1e1e1e', padding: 16, borderRadius: 6 }}>
              <Text strong>已选择的线索：</Text>
              <ul style={{ margin: '8px 0 0 0', paddingLeft: 20 }}>
                {selectedCluesForAssociation.map(id => {
                  const clue = getClueById(id)
                  return clue ? <li key={id}>{clue.name}</li> : null
                })}
              </ul>
            </div>
          )}
        </Form>
      </Modal>
    </div>
  )
}

export default ClueLibrary
