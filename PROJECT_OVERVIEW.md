# AI谋杀之谜项目 - 项目概览

## 项目简介
这是一个**AI驱动的案件解谜应用**，用户以侦探视角参与，所有嫌疑人角色由AI扮演，支持自由探案、线索搜查、对话质询、指认凶手上核心玩法。

## 技术栈

### 后端
- **语言**: Python 3.10+
- **框架**: FastAPI (API服务) + LangChain (AI Agent开发)
- **日志**: loguru (结构化日志)
- **测试**: pytest

### 前端
- **框架**: React 18+ + Vite
- **状态管理**: Zustand
- **UI库**: Ant Design
- **构建工具**: Vite

### AI层
- **大模型**: 兼容OpenAI GPT系列、Anthropic Claude系列
- **Agent架构**: 每个嫌疑人角色对应独立的LangChain Agent

## 项目目录结构

```
ai_muder_mystery_2/
├── backend/                          # 后端服务
│   ├── app/
│   │   ├── api/                      # API路由层
│   │   ├── core/                     # 核心配置、常量定义
│   │   │   ├── config.py            # 配置管理
│   │   │   ├── constants.py         # 常量定义
│   │   │   └── exceptions.py        # 异常定义
│   │   ├── agents/                   # LangChain Agent实现
│   │   │   ├── case_generator_agent.py    # 案件生成Agent
│   │   │   ├── dialogue_manager.py        # 对话管理器
│   │   │   ├── contradiction_detector.py  # 矛盾检测器
│   │   │   ├── refusal_decision_engine.py # 反驳决策引擎
│   │   │   └── suspect_agent.py          # 嫌疑人Agent
│   │   ├── models/                   # 数据模型
│   │   │   ├── case.py              # 案件模型
│   │   │   ├── game.py              # 游戏模型
│   │   │   └── agent.py             # Agent模型
│   │   ├── services/                 # 业务逻辑层
│   │   │   ├── game_service.py      # 游戏服务
│   │   │   ├── dialogue_service.py  # 对话服务
│   │   │   └── session_service.py   # 会话服务
│   │   └── utils/                    # 工具函数
│   │       └── logger.py            # 日志工具
│   ├── main.py                       # 服务入口
│   ├── requirements.txt              # Python依赖
│   └── tests/                        # 后端测试用例
├── frontend/                         # 前端应用
│   ├── src/
│   │   ├── components/               # 公共组件
│   │   │   ├── ClueCard.tsx         # 线索卡片
│   │   │   ├── MessageBox.tsx       # 消息框
│   │   │   ├── SuspectAvatar.tsx    # 嫌疑人头像
│   │   │   ├── SuspectMentions.tsx  # @嫌疑人组件
│   │   │   ├── SceneItem.tsx        # 场景项
│   │   │   └── TypewriterText.tsx   # 打字机文本
│   │   ├── pages/                    # 页面组件
│   │   │   ├── Interrogation.tsx    # 质询页面
│   │   │   ├── Investigation.tsx    # 勘查页面
│   │   │   └── ClueLibrary.tsx      # 线索库页面
│   │   ├── store/                    # Zustand状态管理
│   │   │   ├── gameStore.ts         # 游戏状态
│   │   │   ├── dialogueStore.ts     # 对话状态
│   │   │   └── clueStore.ts         # 线索状态
│   │   ├── services/                 # API请求封装
│   │   │   ├── agentApi.ts          # Agent API
│   │   │   └── gameApi.ts           # 游戏API
│   │   ├── types/                    # TypeScript类型定义
│   │   │   └── game.ts              # 游戏类型
│   │   └── utils/                    # 工具函数
│   ├── package.json
│   ├── vite.config.ts
│   └── playwright.config.ts         # E2E测试配置
├── docs/                             # 产品文档、PRD、设计文档
├── CLAUDE.md                         # Claude Code项目指导
└── PROJECT_OVERVIEW.md               # 本文件
```

## 核心架构说明

### 1. 分层架构
- **API层** → **业务服务层** → **Agent层** → **模型调用层**

### 2. AI Agent设计
- 每个嫌疑人角色对应独立的LangChain Agent
- 案件生成由专门的Agent负责
- 所有Agent调用必须记录完整日志

### 3. 游戏会话管理
- 每个用户游戏会话独立，状态存储在后端
- 支持多用户同时在线

### 4. 线索系统
- 支持三种线索类型：直接可用、可关联、需解密
- 自动处理线索关联和解密逻辑

### 5. 对话系统
- 支持单独审讯、全体质询两种模式
- 自动识别用户提问意图
- 控制AI角色发言优先级和频率

## 最近修复的关键问题

### 2026-04-11 修复内容：
1. ✅ 切换单独审讯角色不生效 - 每次切换都调用后端API
2. ✅ 角色头像下方显示名字 - 修改SuspectAvatar组件
3. ✅ 聊天记录按对话模式+角色维度区分 - 扩展Message接口，添加dialogueMode和suspectId
4. ✅ @功能显示名字而非ID - 使用名字作为Mentions的value，内部通过名字反向查找ID
5. ✅ 回车发送/Shift+Enter换行 - 在SuspectMentions中添加键盘事件处理
6. ✅ 页面跳转后保持消息滚动位置 - 记录componentMountedAt，只有新消息才用打字机效果
7. ✅ 线索相关嫌疑人显示名字而非代号 - 修改ClueCard组件，添加suspects属性和ID→名字转换

## 常用命令

### 后端开发
```bash
cd backend && python3 -m venv venv && source venv/bin/activate
cd backend && pip install -r requirements.txt
cd backend && uvicorn main:app --reload --port 8000
cd backend && pytest tests/ -v
```

### 前端开发
```bash
cd frontend && npm install
cd frontend && npm run dev
cd frontend && npm run build
```

## 关键文件速查

| 功能 | 文件路径 |
|------|---------|
| 质询页面 | frontend/src/pages/Interrogation.tsx |
| 勘查页面 | frontend/src/pages/Investigation.tsx |
| 线索库页面 | frontend/src/pages/ClueLibrary.tsx |
| 对话状态管理 | frontend/src/store/dialogueStore.ts |
| 消息组件 | frontend/src/components/MessageBox.tsx |
| 线索卡片组件 | frontend/src/components/ClueCard.tsx |
| 嫌疑人头像组件 | frontend/src/components/SuspectAvatar.tsx |
| @嫌疑人组件 | frontend/src/components/SuspectMentions.tsx |
| 对话管理器 | backend/app/agents/dialogue_manager.py |
| 对话服务 | backend/app/services/dialogue_service.py |
| 类型定义 | frontend/src/types/game.ts |

## 数据模型关键说明

### Message (对话消息)
```typescript
interface Message {
  id: string
  role: 'system' | 'user' | 'suspect' | 'judge'
  content: string
  sender_id?: string
  sender_name?: string
  timestamp: number
  mood?: 'calm' | 'nervous' | 'angry' | 'scared' | 'guilty'
  type: 'text' | 'system_prompt' | 'evidence' | 'accusation'
  dialogueMode: 'single' | 'group'  // 新增：对话模式
  suspectId?: string                 // 新增：关联的嫌疑人ID
}
```

### Clue (线索)
```typescript
interface Clue {
  clue_id: string
  name: string
  clue_type: ClueType
  status: ClueStatus
  description: string
  location: string
  scene: string
  related_suspects: string[]  // 相关嫌疑人ID列表
}
```

### Suspect (嫌疑人)
```typescript
interface Suspect {
  suspect_id: string
  name: string
  age: number
  gender: string
  occupation: string
  relationship_with_victim: string
  motive?: string
  alibi: string
  is_murderer: boolean
}
```

## 注意事项

1. **会话管理**: 游戏会话ID通过gameStore管理，所有API请求需要携带sessionId
2. **状态同步**: 前端状态(Zustand)需要与后端状态保持同步
3. **日志记录**: 所有AI模型调用必须记录完整日志(请求参数、响应结果、耗时)
4. **消息过滤**: 对话消息根据dialogueMode和suspectId进行过滤显示
5. **打字机效果**: 只有组件挂载后收到的新消息才使用打字机效果
