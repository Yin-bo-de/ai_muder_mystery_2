# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述
本项目是**AI驱动的案件解谜应用**，用户以侦探视角参与，所有嫌疑人角色由AI扮演，支持自由探案、线索搜查、对话质询、指认凶手上核心玩法，无需读本、无需等待队友，随时随地可体验完整案件解谜推理乐趣。

核心玩法流程：
1. 开局：系统自动生成完整案件（死者、嫌疑人、证据链、作案手法等）
2. 探案：用户可自由进行现场勘查（搜查线索）、对话质询（单独审讯/全体对峙）
3. 结案：用户收集足够证据后指认凶手，系统判断正确性并给出完整案件还原

## 技术栈
### 后端
- 语言：Python 3.10+
- 框架：FastAPI（API服务） + LangChain（AI Agent开发）
- 日志：loguru（结构化日志）
- 测试：pytest

### 前端
- 框架：React 18+ + Vite
- 状态管理：Zustand
- UI库：Ant Design
- 构建工具：Vite

### AI层
- 大模型：兼容OpenAI GPT系列、Anthropic Claude系列
- Agent架构：每个嫌疑人角色对应独立的LangChain Agent，严格控制上下文范围

## 项目结构
```
ai_muder_mystery_2/
├── backend/              # 后端服务
│   ├── app/              # FastAPI应用主目录
│   │   ├── api/          # API路由层
│   │   ├── core/         # 核心配置、常量定义
│   │   ├── agents/       # LangChain Agent实现（案件生成、AI角色逻辑）
│   │   ├── models/       # Pydantic数据模型
│   │   ├── services/     # 业务逻辑层
│   │   └── utils/        # 工具函数
│   ├── main.py           # 服务入口
│   ├── requirements.txt  # Python依赖
│   └── tests/            # 后端测试用例
├── frontend/             # 前端应用
│   ├── src/
│   │   ├── components/   # 公共组件
│   │   ├── pages/        # 页面组件
│   │   ├── store/        # Zustand状态管理
│   │   ├── services/     # API请求封装
│   │   └── utils/        # 工具函数
│   ├── package.json
│   └── vite.config.ts
├── docs/                 # 产品文档、PRD、设计文档
└── CLAUDE.md             # 本文件
```

## 常用命令
### 后端开发
```bash
# 启动虚拟环境
cd backend && python3 -m venv venv && source venv/bin/activate

# 安装依赖
cd backend && pip install -r requirements.txt

# 启动开发服务（端口8000，自动重载）
cd backend && uvicorn main:app --reload --port 8000

# 运行所有测试
cd backend && pytest tests/ -v

# 运行单个测试文件
cd backend && pytest tests/path/to/test_file.py -v

# 运行单个测试用例
cd backend && pytest tests/path/to/test_file.py::test_function -v
```

### 前端开发
```bash
# 安装依赖
cd frontend && npm install

# 启动开发服务（端口5173）
cd frontend && npm run dev

# 构建生产版本
cd frontend && npm run build

# 运行测试
cd frontend && npm run test
```

## 核心架构说明
1. **分层架构**：API层 → 业务服务层 → Agent层 → 模型调用层，各层职责清晰，降低耦合
2. **AI Agent设计**：
   - 每个嫌疑人角色对应独立的LangChain Agent，拥有独立的人设、记忆和行为规则
   - 案件生成由专门的Agent负责，生成完整的案件数据结构（死者信息、嫌疑人列表、证据链、时间线、作案逻辑等）
   - 所有Agent调用必须记录完整日志，包括请求参数、响应结果、耗时等
3. **游戏会话管理**：每个用户游戏会话独立，状态存储在后端，支持多用户同时在线
4. **线索系统**：支持三种线索类型（直接可用、可关联、需解密），自动处理线索关联和解密逻辑
5. **对话系统**：支持单独审讯、全体质询两种模式，自动识别用户提问意图，控制AI角色发言优先级和频率

## 开发规范
### 后端
- 严格遵循PEP8编码规范，使用类型注解提升代码可维护性
- 日志使用loguru，关键节点必须记录：
  - 案件生成的完整过程和结果
  - 用户交互请求/响应、耗时
  - 所有大模型调用的请求/响应
  - 异常捕获必须包含完整堆栈上下文
- LangChain相关代码优先使用LCEL（LangChain Expression Language）实现
- API接口自动生成Swagger文档，访问`http://localhost:8000/docs`查看

### 前端
- 使用函数式组件 + Hooks，遵循React最佳实践
- 全局状态使用Zustand管理，组件内部状态使用useState/useReducer
- API请求统一封装，错误处理逻辑集中管理
- 前端日志分级输出，关键交互节点必须记录（用户操作、API请求、状态变更等）

## 参考文档
- 产品PRD：`docs/2026-4-5-【PRD】AI案件解谜 产品文档（WIP）.md`
- 技术方案： `docs/技术架构设计方案.md`


## langChain迁移
旧的导入 (已失效)	新的导入 (正确)
from langchain.schema import Document ->	from langchain_core.documents import Document
from langchain.schema import BaseMessage, AIMessage, HumanMessage ->	from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain.schema import OutputParserException ->	from langchain_core.output_parsers import OutputParserException
from langchain.schema import LLMResult ->	from langchain_core.outputs import LLMResult
from langchain.schema import AgentAction, AgentFinish	-> from langchain_core.agents import AgentAction, AgentFinish
from langchain.schema import Document ->	from langchain_core.documents import Document
from langchain.schema import BaseRetriever ->	from langchain_core.retrievers import BaseRetriever
from langchain.schema import BaseMemory ->	from langchain.memory import BaseMemory（仍在 langchain 中）