# 测试执行指南

本目录包含AI案件解谜应用的完整测试套件。

## 目录结构

```
tests/
├── unit/                      # 单元测试
│   ├── test_clue_service.py
│   └── test_session_service.py
├── integration/               # 集成测试
│   └── test_api.py
├── functional/                # 功能接口测试（新增）
│   ├── test_game_api.py       # 游戏管理API测试
│   └── test_agent_api.py      # AI交互API测试
├── e2e/                       # 端到端测试（新增）
│   └── test_e2e_game.py       # 完整游戏流程E2E测试
└── README.md                   # 本文件
```

## 测试方案文档

完整的功能测试方案请参考：
`docs/功能测试方案.md`

## 前置条件

1. Python 3.10+
2. 后端依赖已安装：`cd backend && pip install -r requirements.txt`
3. 前端依赖已安装：`cd frontend && npm install`

## 运行测试

### 1. 单元测试

```bash
cd backend

# 运行所有单元测试
pytest tests/unit/ -v

# 运行特定单元测试
pytest tests/unit/test_clue_service.py -v
pytest tests/unit/test_session_service.py::TestSessionService::test_create_session -v
```

### 2. 集成测试

```bash
cd backend

# 运行集成测试
pytest tests/integration/ -v
```

### 3. 功能接口测试

```bash
cd backend

# 运行所有功能接口测试
pytest tests/functional/ -v

# 仅运行游戏API测试
pytest tests/functional/test_game_api.py -v

# 仅运行Agent API测试
pytest tests/functional/test_agent_api.py -v

# 生成测试覆盖率报告
pytest tests/functional/ --cov=app --cov-report=html
```

### 4. 端到端测试（使用agent-browser）

#### 前置条件
- 后端服务运行在 `http://localhost:8000`
- 前端服务运行在 `http://localhost:5173`

#### 启动服务

```bash
# 终端1: 启动后端
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# 终端2: 启动前端
cd frontend
npm run dev
```

#### 使用agent-browser执行E2E测试

在Claude Code中执行：

```
/agent-browser
```

然后使用以下代码调用测试：

```python
# 这是一个示例，实际使用时需要根据agent-browser的API调整
from tests.e2e.test_e2e_game import run_e2e_tests

# 假设browser是agent-browser提供的实例
await run_e2e_tests(browser)
```

## 测试用例覆盖

### 接口测试覆盖

| 测试模块 | 用例数量 | 覆盖用例ID |
|---------|---------|-----------|
| 游戏创建 | 6 | API-GAME-001 ~ API-GAME-006 |
| 游戏状态 | 5 | API-GAME-010 ~ API-GAME-014 |
| 现场勘查 | 6 | API-GAME-020 ~ API-GAME-025 |
| 线索解密 | 6 | API-GAME-030 ~ API-GAME-035 |
| 指认凶手 | 8 | API-GAME-040 ~ API-GAME-047 |
| 线索管理 | 9 | API-GAME-050 ~ API-GAME-082 |
| 发送消息 | 10 | API-AGENT-001 ~ API-AGENT-010 |
| 切换模式 | 5 | API-AGENT-020 ~ API-AGENT-024 |
| 控场指令 | 5 | API-AGENT-030 ~ API-AGENT-034 |
| 对话历史 | 5 | API-AGENT-040 ~ API-AGENT-044 |
| 嫌疑人状态 | 4 | API-AGENT-050 ~ API-AGENT-053 |
| **总计** | **79** | |

### 端到端测试覆盖

| 测试用例 | 测试目标 | 优先级 |
|---------|---------|-------|
| E2E-001 | 标准完整探案流程（正确指认） | P0 |
| E2E-002 | 错误指认流程 | P0 |
| E2E-003 | 线索解密与关联 | P1 |
| E2E-004 | 矛盾检测与系统提示 | P1 |
| E2E-005 | 单独审讯与保密对话 | P1 |
| E2E-006 | @嫌疑人功能与多选 | P0 |
| E2E-007 | 打字机效果与跳过动画 | P2 |
| E2E-008 | 控场指令 | P2 |
| E2E-009 | 卡关提示 | P2 |
| E2E-010 | 游戏超时强制结案 | P2 |

## 冒烟测试清单

每次代码提交后执行：

- [ ] 后端健康检查接口通过：`GET /` 返回200
- [ ] API文档可访问：`GET /docs`
- [ ] 前端首页可加载
- [ ] 可以创建新案件：`POST /api/v1/game/new`

## 缺陷等级定义

| 等级 | 描述 | 示例 |
|------|------|------|
| P0 - 阻塞 | 无法进行测试，核心功能不可用 | 无法创建案件、页面白屏 |
| P1 - 严重 | 核心功能异常，主要流程无法完成 | 无法指认凶手、线索不保存 |
| P2 - 一般 | 次要功能异常，不影响主要流程 | 打字机效果失效、UI样式问题 |
| P3 - 轻微 | 体验优化建议 | 文案错别字、按钮位置不理想 |

## 测试数据

测试使用模拟数据（mock），不依赖真实的AI模型调用，确保测试快速、稳定、可重复。

## 持续集成

建议在CI/CD流程中：

1. 每次PR自动运行单元测试和集成测试
2. 每日自动运行完整功能接口测试
3. 发布前手动运行端到端测试

## 常见问题

### Q: 功能测试需要启动后端服务吗？
A: 不需要。现有的功能测试使用mock，不依赖真实服务。如果需要做真实API集成测试，可以启动服务后运行。

### Q: E2E测试可以在CI中运行吗？
A: 可以，但需要配置headless浏览器环境。建议先在本地验证通过。

### Q: 如何添加新的测试用例？
A:
1. 接口测试：在 `tests/functional/` 对应文件中添加
2. E2E测试：在 `tests/e2e/test_e2e_game.py` 的 `GameE2ETests` 类中添加新方法

## 参考文档

- 产品PRD: `docs/2026-4-5-【PRD】AI案件解谜 产品文档（WIP）.md`
- 技术方案: `docs/技术架构设计方案.md`
- 测试方案: `docs/功能测试方案.md`

