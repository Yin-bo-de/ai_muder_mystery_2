# AI侦探社 - 快速启动指南

## 🚀 项目概述
AI驱动的案件解谜应用，用户以侦探视角参与，所有嫌疑人角色由AI扮演，支持自由探案、线索搜查、对话质询、指认凶手上核心玩法。

## 📋 前置要求
- Python 3.9+
- Node.js 16+
- OpenAI API Key（必须，案件生成和AI对话需要）

## 🔧 启动步骤

### 1. 后端启动
```bash
# 进入后端目录
cd backend

# 激活虚拟环境
source venv/bin/activate

# 安装依赖（首次运行）
pip install -r requirements.txt

# 配置环境变量
# 编辑 .env 文件，填入你的 OpenAI API Key
OPENAI_API_KEY=sk-xxx

# 启动后端服务
uvicorn main:app --reload --port 8000
```

后端启动成功后，访问 http://localhost:8000/docs 可以查看Swagger API文档。

### 2. 前端启动
```bash
# 进入前端目录
cd frontend

# 安装依赖（首次运行）
npm install

# 启动前端开发服务
npm run dev
```

前端启动成功后，访问 http://localhost:5173 即可进入游戏。

## 🎮 游戏流程
1. **首页**：点击"开始新案件"按钮
2. **案件生成**：AI自动生成完整案件，包含死者、嫌疑人、证据链
3. **现场勘查**：点击场景物品进行勘查，收集线索
4. **质询嫌疑人**：与嫌疑人对话，提问质询，观察情绪变化
5. **线索库**：查看已收集的线索，支持解密和线索关联
6. **指认凶手**：选择你认为的凶手，陈述动机和作案手法，提交证据
7. **结案报告**：查看指认结果和完整案件真相

## 🔧 开发说明

### 技术栈
- **后端**：Python 3.9+、FastAPI、LangChain、OpenAI GPT
- **前端**：React 18、TypeScript、Vite、Zustand、Ant Design（暗色主题）
- **AI模型**：支持OpenAI GPT-3.5/4、Anthropic Claude系列

### 项目结构
```
ai_muder_mystery_2/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── api/          # API路由层
│   │   ├── core/         # 核心配置
│   │   ├── agents/       # LangChain Agent实现
│   │   ├── models/       # Pydantic数据模型
│   │   ├── services/     # 业务逻辑层
│   │   └── utils/        # 工具函数
│   ├── main.py           # 服务入口
│   └── requirements.txt  # Python依赖
├── frontend/             # 前端应用
│   ├── src/
│   │   ├── pages/        # 页面组件
│   │   ├── components/   # 公共组件
│   │   ├── store/        # Zustand状态管理
│   │   ├── services/     # API请求封装
│   │   └── utils/        # 工具函数
│   └── package.json
├── docs/                 # 项目文档
└── QUICKSTART.md         # 本文件
```

## 📝 注意事项
1. 首次启动需要配置OpenAI API Key，否则案件生成和对话功能无法使用
2. 开发阶段会话存储在内存中，重启后端服务会丢失所有游戏数据
3. 案件生成需要10-30秒时间，请耐心等待
4. 每个嫌疑人都是独立的AI Agent，拥有独立的人设和记忆，会根据你的提问做出不同反应
5. 嫌疑人有压力值系统，压力越高回答越可能出现破绽

## 🐛 常见问题

### 后端启动报错
- 确保Python版本>=3.9
- 检查依赖是否安装完整：`pip install -r requirements.txt`
- 检查.env文件中的API Key是否正确配置

### 前端无法连接后端
- 确保后端服务已启动，端口8000没有被占用
- 检查CORS配置是否包含前端地址
- 可以直接访问http://localhost:8000测试后端是否正常

### AI响应慢或失败
- 检查网络连接是否可以访问OpenAI API
- 可以尝试配置OPENAI_BASE_URL使用代理地址
- 适当调整超时时间配置

## 🎯 功能特性
- ✅ 完整的游戏流程：案件生成→勘查→对话→指认→结案
- ✅ 每个嫌疑人独立AI Agent，人设稳定
- ✅ 动态压力值系统，嫌疑人情绪会随提问变化
- ✅ 真凶会合理说谎，掩盖作案事实
- ✅ 线索系统：物证、证词、关联线索、解密线索
- ✅ 对话管理：支持单独审讯和全体质询模式
- ✅ 智能裁判系统，自动评估推理准确率
- ✅ 完整的结案报告和探案评价
- ✅ 暗色悬疑主题UI，沉浸式探案体验
