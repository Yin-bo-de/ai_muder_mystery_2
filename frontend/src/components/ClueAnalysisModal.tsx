import { Modal, Typography, Divider, Tag, Row, Col, Button } from 'antd'
import {
  BulbOutlined,
  EyeOutlined,
  QuestionCircleOutlined,
  TeamOutlined,
  LinkOutlined,
} from '@ant-design/icons'
import type { Clue, Suspect } from '../types/game'
import { useClueStore } from '../store/clueStore'

const { Title, Text, Paragraph } = Typography

interface ClueAnalysisModalProps {
  open: boolean
  onClose: () => void
  clue: Clue | null
  suspects: Suspect[]
}

// 根据线索类型生成侦探观察
const generateObservation = (clue: Clue): string => {
  const typeObservations: Record<string, string[]> = {
    physical: [
      `仔细观察${clue.name}，它的细节很有意思。`,
      `这个${clue.name}上面有一些值得注意的特征。`,
      `作为物证，${clue.name}能告诉我们很多信息。`,
    ],
    testimony: [
      `这份证词的措辞很值得推敲。`,
      `说这话的人当时是什么状态？`,
      `证词中的某些细节似乎暗示着什么。`,
    ],
    association: [
      `这几条线索放在一起看，事情就明朗了。`,
      `关联起来后，一个隐约的轮廓开始浮现。`,
      `这些线索之间的联系很有意思。`,
    ],
    decrypted: [
      `解密后的内容让人惊讶！`,
      `隐藏的信息终于浮出水面了。`,
      `这就是我们一直在找的关键！`,
    ],
    document: [
      `这份文档记录了一些重要信息。`,
      `字里行间都透露出线索。`,
      `仔细阅读每个字，都可能有新发现。`,
    ],
  }

  const observations = typeObservations[clue.clue_type] || typeObservations.physical
  return observations[Math.floor(Math.random() * observations.length)]
}

// 生成初步推测
const generateHypothesis = (clue: Clue): string => {
  if (clue.importance >= 0.8) {
    return `这绝对是关键线索！它的重要性不言而喻。${clue.points_to_suspect ? '看起来它直接指向了某个人。' : '需要结合其他线索来理解它的含义。'}`
  } else if (clue.importance >= 0.5) {
    return `这条线索很有价值。${clue.is_red_herring ? '不过，要小心它可能是干扰项。' : '它可能能帮我们缩小调查范围。'}`
  } else {
    return `虽然看起来不起眼，但不要轻易放过任何细节。${clue.is_red_herring ? '小心，这可能是凶手设下的迷魂阵。' : '也许在关键时刻能派上用场。'}`
  }
}

// 生成关联提示
const generateConnectionHint = (clue: Clue, collectedClues: Clue[]): string | null => {
  const relatedCollected = collectedClues.filter(
    c => c.clue_id !== clue.clue_id &&
    (clue.related_clues.includes(c.clue_id) ||
     c.related_clues.includes(clue.clue_id) ||
     c.scene === clue.scene)
  )

  if (relatedCollected.length === 0) {
    if (clue.required_clues.length > 0) {
      return '这条线索似乎还需要其他线索才能完全理解它的意义。继续搜查吧！'
    }
    return null
  }

  const relatedNames = relatedCollected.slice(0, 3).map(c => c.name).join('、')
  const hints = [
    `还记得「${relatedNames}」吗？把它们放在一起想想看。`,
    `「${relatedNames}」可能和这条线索有着某种联系。`,
    `试试把这条线索和「${relatedNames}」关联起来分析。`,
  ]
  return hints[Math.floor(Math.random() * hints.length)]
}

// 生成追问方向
const generateQuestionDirections = (clue: Clue, suspects: Suspect[]): string[] => {
  const directions: string[] = []

  if (clue.related_suspects.length > 0) {
    const relatedNames = clue.related_suspects
      .map(id => suspects.find(s => s.suspect_id === id)?.name || id)
      .join('、')

    directions.push(`${relatedNames}似乎和这条线索有关，可以找他们聊聊。`)
  }

  if (clue.points_to_suspect) {
    const suspectName = suspects.find(s => s.suspect_id === clue.points_to_suspect)?.name
    if (suspectName) {
      directions.push(`${suspectName}需要对这条线索给出一个合理的解释。`)
    }
  }

  if (clue.clue_type === 'physical') {
    directions.push('可以问问嫌疑人最后一次见到这个东西是什么时候。')
  } else if (clue.clue_type === 'testimony') {
    directions.push('这份证词的真实性需要验证，看看有没有其他人能佐证。')
  }

  if (directions.length === 0) {
    directions.push('把这条线索带给所有嫌疑人看看，观察他们的反应。')
  }

  return directions
}

const ClueAnalysisModal: React.FC<ClueAnalysisModalProps> = ({
  open,
  onClose,
  clue,
  suspects,
}) => {
  const { collectedClues } = useClueStore()

  if (!clue) return null

  const observation = generateObservation(clue)
  const hypothesis = generateHypothesis(clue)
  const connectionHint = generateConnectionHint(clue, collectedClues)
  const questionDirections = generateQuestionDirections(clue, suspects)

  const typeConfig = {
    physical: { color: '#1890ff', text: '物证', icon: <EyeOutlined /> },
    testimony: { color: '#52c41a', text: '证词', icon: <TeamOutlined /> },
    association: { color: '#faad14', text: '关联线索', icon: <LinkOutlined /> },
    decrypt: { color: '#722ed1', text: '需解密', icon: <BulbOutlined /> },
    document: { color: '#13c2c2', text: '文档', icon: <EyeOutlined /> },
  }

  const typeInfo = typeConfig[clue.clue_type] || typeConfig.physical

  return (
    <Modal
      open={open}
      onCancel={onClose}
      footer={[
        <Button key="close" onClick={onClose}>
          关闭笔记
        </Button>,
      ]}
      width={700}
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <BulbOutlined style={{ color: '#ffd700', fontSize: '24px' }} />
          <span>侦探笔记</span>
        </div>
      }
    >
      <div style={{
        background: 'linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%)',
        borderRadius: 8,
        padding: 24,
        border: '1px solid #303030',
      }}>
        {/* 线索标题 */}
        <div style={{ marginBottom: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <Title level={3} style={{ color: '#ffd700', margin: 0 }}>
              📌 {clue.name}
            </Title>
            <Tag color={typeInfo.color} icon={typeInfo.icon}>
              {typeInfo.text}
            </Tag>
          </div>
          <Text type="secondary" style={{ fontSize: '13px' }}>
            发现地点: {clue.scene} · {clue.location}
          </Text>
        </div>

        <Divider style={{ borderColor: '#303030', margin: '16px 0' }} />

        {/* 线索描述 */}
        <div style={{ marginBottom: 20 }}>
          <div style={{
            background: 'rgba(255, 215, 0, 0.1)',
            padding: 16,
            borderRadius: 6,
            borderLeft: '4px solid #ffd700',
          }}>
            <Text style={{ color: 'rgba(255, 255, 255, 0.88)', fontSize: '15px' }}>
              {clue.description}
            </Text>
            {clue.content && (
              <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid rgba(255, 215, 0, 0.2)' }}>
                <Text style={{ color: 'rgba(255, 255, 255, 0.75)', fontSize: '14px' }}>
                  💡 {clue.content}
                </Text>
              </div>
            )}
            {clue.hidden_content && clue.status === 'decrypted' && (
              <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid rgba(255, 215, 0, 0.2)' }}>
                <Text style={{ color: '#ff6b6b', fontSize: '14px', fontWeight: 'bold' }}>
                  🔓 {clue.hidden_content}
                </Text>
              </div>
            )}
          </div>
        </div>

        {/* 侦探观察 */}
        <div style={{ marginBottom: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <EyeOutlined style={{ color: '#52c41' }} />
            <Text strong style={{ color: '#52c41' }}>侦探观察</Text>
          </div>
          <Paragraph style={{ color: 'rgba(255, 255, 255, 0.75)', margin: 0, paddingLeft: 24 }}>
            {observation}
          </Paragraph>
        </div>

        {/* 初步推测 */}
        <div style={{ marginBottom: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <BulbOutlined style={{ color: '#faad14' }} />
            <Text strong style={{ color: '#faad14' }}>初步推测</Text>
          </div>
          <Paragraph style={{ color: 'rgba(255, 255, 255, 0.75)', margin: 0, paddingLeft: 24 }}>
            {hypothesis}
          </Paragraph>
        </div>

        {/* 关联提示 */}
        {connectionHint && (
          <div style={{ marginBottom: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <LinkOutlined style={{ color: '#722ed1' }} />
              <Text strong style={{ color: '#722ed1' }}>线索关联</Text>
            </div>
            <div style={{
              background: 'rgba(114, 46, 209, 0.15)',
              padding: 12,
              borderRadius: 6,
              paddingLeft: 24,
            }}>
              <Text style={{ color: 'rgba(255, 255, 255, 0.85)' }}>
                💭 {connectionHint}
              </Text>
            </div>
          </div>
        )}

        {/* 追问方向 */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <QuestionCircleOutlined style={{ color: '#1890ff' }} />
            <Text strong style={{ color: '#1890ff' }}>追问方向</Text>
          </div>
          <ul style={{ margin: 0, paddingLeft: 40 }}>
            {questionDirections.map((direction, index) => (
              <li key={index} style={{ marginBottom: 8 }}>
                <Text style={{ color: 'rgba(255, 255, 255, 0.75)' }}>
                  {direction}
                </Text>
              </li>
            ))}
          </ul>
        </div>

        {/* 相关嫌疑人 */}
        {clue.related_suspects.length > 0 && (
          <div style={{ marginTop: 20, paddingTop: 20, borderTop: '1px solid #303030' }}>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              相关嫌疑人: {clue.related_suspects.map(id => {
                const suspect = suspects.find(s => s.suspect_id === id)
                return suspect?.name || id
              }).join('、')}
            </Text>
          </div>
        )}
      </div>
    </Modal>
  )
}

export default ClueAnalysisModal
