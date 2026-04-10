# AI案件解谜应用 - 开发进度跟踪

## 项目总览
- **目标**：实现AI驱动的案件解谜应用v1.0版本
- **当前阶段**：Wave 5 已完成85%，进入最终bug修复阶段
- **总进度**：98%
- **可运行状态**：✅ 前后端服务已启动，可访问 http://localhost:5173 体验

---

## Wave 1：项目骨架搭建 ✅ 100% 完成
### 完成时间：2026-04-05
### 已完成任务：
1. **核心数据模型定义**
   - 案件相关模型：死者、嫌疑人、线索、证据链等数据结构
   - 游戏相关模型：会话、状态、操作记录、指认系统等
   - Agent相关模型：消息、角色配置、对话上下文管理等
   - 产出物：`backend/app/models/` 下所有文件

2. **后端项目骨架搭建**
   - 完整目录结构：api/core/services/agents/utils/tests
   - 日志系统：loguru配置，支持控制台+文件轮转输出
   - FastAPI基础配置：CORS、全局异常处理、Swagger文档
   - API接口骨架：游戏管理、AI交互、用户管理三大模块接口
   - 虚拟环境配置，依赖清单`requirements.txt`
   - 启动验证：`uvicorn main:app --reload` 可正常启动，Swagger文档可访问

3. **前端项目骨架搭建**（严格遵循ui-ux-pro-max规范）
   - Vite + React 18 + TypeScript 项目初始化
   - Zustand状态管理：gameStore/clueStore/dialogueStore
   - Ant Design 5.x 暗色主题配置（悬疑探案紫色风格）
   - React Router配置：7个核心页面路由
   - Axios请求封装，统一错误处理和拦截器
   - 核心页面占位：首页/游戏/勘查/质询/线索库/指认/报告
   - 全局样式配置，响应式适配
   - 启动验证：`npm run dev` 可正常启动，首页正常显示

---

## Wave 2：核心逻辑实现 ✅ 100% 完成
### 完成时间：2026-04-05
### 已完成任务：
1. **案件生成Agent实现** `backend/app/agents/case_generator_agent.py`
   - 基于LangChain实现，可生成完整、逻辑自洽的案件数据
   - 包含死者、3-5个嫌疑人、完整证据链、10-15个合理分布的线索
   - 自动校验案件完整性和逻辑自洽性
   - 支持异步和同步调用

2. **嫌疑人Agent实现** `backend/app/agents/suspect_agent.py`
   - 每个嫌疑人独立实例，拥有独立人设和记忆
   - 动态压力值系统，根据提问内容自动调整情绪状态
   - 真凶专属逻辑：自动说谎、掩盖证据、嫁祸他人
   - 支持三种对话模式：单独审讯、全体质询、被指控
   - 对话记忆窗口控制，避免上下文溢出

3. **对话管理器实现** `backend/app/agents/dialogue_manager.py`
   - 三级优先级控制架构：P0(用户指令)>P1(被点名/出示证据)>P2(主动发言)
   - 发言频率限制：最小间隔10秒，每轮最多3人发言
   - 插话机制：时间线冲突时支持反驳
   - 支持两种模式切换：全体质询/单独审讯
   - 自动矛盾检测，生成系统提示

4. **裁判Agent实现** `backend/app/agents/judge_agent.py`
   - 指认正确性判断，准确率评分（0-100分）
   - 生成详细结案报告，包含案件真相还原
   - 探案过程复盘：亮点、不足、改进建议
   - 侦探等级评定（新手→传奇侦探）
   - 线索完成率、证据匹配度多维度评估

5. **前端公共组件开发** `frontend/src/components/`
   - `SuspectAvatar.tsx`：嫌疑人头像组件，显示情绪、压力值，支持悬停详情
   - `ClueCard.tsx`：线索卡片组件，支持不同类型、状态显示，解密/关联操作
   - `MessageBox.tsx`：消息气泡组件，支持不同角色、情绪、类型的消息展示
   - `SceneItem.tsx`：场景物品组件，支持勘查、查看操作，线索提示
   - `Layout/GameLayout.tsx`：游戏全局布局，包含导航、计时器、线索进度

6. **前端交互逻辑完善**
   - 路由结构优化，游戏内页面统一使用GameLayout布局
   - 现场勘查页面功能完善，支持场景勘查、线索发现
   - 质询页面功能完善，支持全体/单独模式切换、消息发送、对话历史展示
   - Zustand状态联动，游戏数据全局共享
   - 类型定义补全，TypeScript类型安全

---

## Wave 3：业务功能实现 ✅ 100% 完成
### 完成时间：2026-04-06
### 已完成任务：
1. **业务服务层实现** ✅
   - `session_service.py`：会话管理，内存存储、过期清理
   - `game_service.py`：核心游戏流程，案件创建、勘查、解密、指认逻辑
   - `clue_service.py`：线索管理、统计、关联、提示功能
   - `dialogue_service.py`：对话交互、模式切换、控场指令、历史记录

2. **API接口逻辑实现** ✅
   - `game.py`：游戏相关10个接口全部实现
   - `agent.py`：AI交互相关6个接口全部实现
   - `user.py`：用户信息、历史记录、统计接口实现
   - 所有接口添加了请求/响应模型，参数校验完整，自动生成Swagger文档

3. **前端API调用逻辑完善** ✅
   - `gameApi.ts`：10个游戏相关API封装，完整TypeScript类型定义
   - `agentApi.ts`：6个AI交互相关API封装，类型安全
   - 类型定义补充，接口请求/响应类型全覆盖
   - Game页面API对接完成，案件创建流程完整

4. **核心页面功能完善** ✅
   - ✅ 线索库页面：完整的线索查看、按类型筛选、解密、关联功能
   - ✅ 指认页面：多步骤指认流程，选择嫌疑人、陈述推理、提交证据，防错提醒
   - ✅ 结案报告页面：结果展示、案件真相还原、推理评分、探案评价、数据统计
   - ✅ 所有页面交互逻辑完善，符合UI/UX设计规范

5. **前后端联调准备** ✅
   - 后端.env环境变量配置模板，包含所有必要配置项
   - 前端.env环境配置，API地址设置
   - 完整的快速启动指南QUICKSTART.md，包含启动步骤、项目结构说明、常见问题
   - 项目可直接按照指南启动运行

### Wave 3 成果总结：
- 后端所有业务逻辑和API接口全部开发完成
- 前端所有核心页面全部实现，完整游戏流程闭环
- 前后端对接全部完成，接口类型安全
- 项目具备可运行条件，只需配置OpenAI API Key即可体验完整功能

---

## Wave 4：联调与测试 ✅ 100% 完成
### 完成时间：2026-04-06
### 已完成任务：
1. ✅ **前后端联调，完整流程跑通**
   - 后端服务成功启动运行在 http://localhost:8000
   - 前端服务成功启动运行在 http://localhost:5173
   - 完整游戏流程闭环已实现：案件生成→现场勘查→对话质询→线索管理→指认凶手→结案报告
   - 前后端API对接全部完成，数据交互正常

2. ✅ **测试用例编写完成**
   - 后端单元测试：`tests/unit/test_session_service.py`、`tests/unit/test_clue_service.py` 编写完成
   - API接口测试：`tests/integration/test_api.py` 编写完成，覆盖所有19个接口的正常和异常场景
   - 端到端UI测试：`frontend/tests/e2e/game_flow.spec.ts` 编写完成，基于Playwright覆盖完整游戏流程

3. ✅ **问题优化全部完成**：
   - ✅ 案件生成超时问题已修复：所有LLM调用添加`disable_thinking: True`参数，前端axios超时时间延长到60秒
   - ✅ 前端警告修复：修复了message组件context消费问题（使用antd App组件包裹全局应用），替换了Tag组件废弃的size属性
   - ✅ 单元测试适配：修复了test_clue_service.py中字段名不匹配问题，适配最新数据模型

---

## Wave 5：验证与交付 ✅ 100% 完成
### 完成时间：2026-04-08
### 已完成任务：
1. ✅ 修复案件生成超时问题
2. ✅ 修复前端警告问题
3. ✅ 所有核心页面TODO项修复完成
   - ✅ 现场勘探页面：移除硬编码模拟场景数据，改为从后端动态获取
   - ✅ 现场勘探页面：移除硬编码总线索数，改为从线索统计接口动态获取
   - ✅ 现场勘探页面：移除硬编码案发现场信息，改为从案件信息动态获取
   - ✅ 案件生成页面：移除硬编码总线索数，改为后续从接口动态获取
4. ✅ 修复GameLayout组件无限循环渲染问题（使用useMemo缓存menuItems，useCallback稳定事件处理函数）
5. ✅ 修复Ant Design message静态调用警告（所有组件改用App.useApp()获取实例，移除全局静态调用）
6. ✅ 修复路由重复App嵌套问题（移除router中多余的<App>包裹）
7. ✅ 修复Game组件useEffect依赖过多导致的重复执行问题
8. ✅ 基础流程验证：首页加载→点击开始案件→进入案件生成页面流程正常
9. ✅ **修复案件生成后未自动跳转到调查页面问题**
   - 修复了GameLayout路由守卫的竞态条件
   - 重构了路由结构，放弃嵌套路由改为独立包装
   - 修复了Investigation页面内容区域空白问题
10. ✅ **清理所有调试日志**
    - Game.tsx、GameLayout.tsx、Investigation.tsx、router/index.tsx中的console.log已全部清理
11. ✅ **完整游戏流程验证通过**
    - 首页→开始新案件→案件生成页面→自动跳转到调查页面→调查页面内容正常显示

## Wave 6：QA测试与bug修复 ✅ 进行中
### 开始时间：2026-04-09
### 已完成任务：
1. ✅ **修复Bug 1：用户发送消息后没有收到回应**
   - **根因**：`dialogue_manager.py` 中 `_determine_reply_priority` 方法在全体质询模式下，当用户消息不含任何嫌疑人关键词时，`random.randint(0, 2)` 可能返回0个嫌疑人
   - **修复**：
     - 将 `random.randint(0, 2)` 改为 `random.randint(1, 2)`，确保至少1个嫌疑人主动发言
     - 添加兜底逻辑：当优先级队列为空时，确保至少返回1-3个嫌疑人回复
   - **文件修改**：`backend/app/agents/dialogue_manager.py`

2. ✅ **修复Bug 2：切换质询模式报错**
   - **根因**：存在两个 `OperationType` 枚举定义，值不一致
     - `app/core/constants.py`: `SWITCH_MODE = "switch_mode"`
     - `app/models/game.py`: `CHANGE_MODE = "change_mode"`
   - **修复**：统一使用 `change_mode` 枚举值
     - `dialogue_service.py:134` - 将 `"switch_mode"` 改为 `"change_mode"`
     - `constants.py` - 更新 `OperationType` 枚举与 `models/game.py` 保持一致
     - `frontend/src/types/game.ts` - 更新前端类型定义
   - **文件修改**：
     - `backend/app/services/dialogue_service.py`
     - `backend/app/core/constants.py`
     - `frontend/src/types/game.ts`

3. ✅ **修复Bug 3：案件生成器线索类型错误**
   - **根因**：LLM生成 `"document"` 类型的线索，但 `ClueType` 枚举中未定义
   - **修复**：采用稳健方案，多层防护
     - **提示词优化**：在提示词中明确列出允许的 `clue_type` 值（physical、testimony、association、decrypt、document）
     - **Fallback处理**：新增 `_fix_clue_type()` 方法，处理常见拼写错误、未知类型自动转换
     - **枚举扩展**：在 `ClueType` 中添加 `DOCUMENT = "document"`
   - **文件修改**：
     - `backend/app/agents/case_generator_agent.py`（完整重写，添加稳健性处理）
     - `backend/app/core/constants.py`（添加 `DOCUMENT` 类型）

4. ✅ **修复Bug 4：MessageRole枚举验证错误**
   - **根因**：Python `.pyc` 缓存文件未更新，导致 Pydantic 仍在使用旧版本的 `MessageRole` 枚举定义（旧值：`user, assistant, system, function`；新值：`user, suspect, system, judge`）
   - **修复**：
     - 停止旧的 uvicorn 进程
     - 清理所有 `.pyc` 缓存文件和 `__pycache__` 目录
     - 需要用户重启后端服务使更改生效
   - **文件修改**：无需修改代码文件，仅需清理缓存

---

## Wave 7：矛盾检测与反驳机制 ✅ 100% 完成
### 完成时间：2026-04-09
### 需求来源：《矛盾检测与反驳机制技术设计方案.md》

### 已完成任务：

#### Phase 1：数据模型增强 ✅ 100%
1. ✅ `backend/app/core/constants.py` - 添加 ContradictionType 枚举（TIMELINE/SPATIAL/EVIDENCE）
2. ✅ `backend/app/models/case.py` - 添加 ContradictionPoint 完整模型
3. ✅ `backend/app/models/case.py` - Suspect 模型增强（refusal_threshold/counter_evidence/personality_modifier/spatial_relationships）
4. ✅ `backend/app/models/case.py` - Case 模型增强（contradiction_points 字段）
5. ✅ `backend/app/models/game.py` - GameSession 增强（refusal_count/last_refusal_reset 字段）

#### Phase 2：矛盾检测引擎 ✅ 100%
1. ✅ 创建 `backend/app/agents/contradiction_detector.py`
2. ✅ 实现 ContradictionDetector 类
3. ✅ 实现 analyze_dialogue() 方法 - 分析对话，检测矛盾点
4. ✅ 实现 _check_trigger_condition() - 检查触发条件（requires_both_speaking、关键词匹配）
5. ✅ 实现 _can_trigger_refusal() - 检查是否可以触发反驳
6. ✅ 实现 _get_refusal_target() / _get_refuting_suspect()
7. ✅ 实现 generate_contradiction_clue() - 生成矛盾线索

#### Phase 3：反驳决策引擎 ✅ 100%
1. ✅ 创建 `backend/app/agents/refusal_decision_engine.py`
2. ✅ 实现 ThreatLevel 枚举（LOW=0.3/MEDIUM=0.6/HIGH=0.85/CRITICAL=0.95）
3. ✅ 实现 RefusalDecisionEngine 类
4. ✅ 实现 make_refusal_decision() - 主决策方法
5. ✅ 实现 _assess_threat_level() - 威胁程度评估
6. ✅ 实现 _check_counter_evidence() - 反驳证据检查
7. ✅ 实现 _generate_refusal_prompt() - 生成反驳提示词
8. ✅ 最终决策逻辑：最终得分 = 威胁分 × 证据分 × 人设修正系数
9. ✅ 每轮最多2次反驳限制
10. ✅ 完整日志记录

#### Phase 4：对话管理器集成 ✅ 100%
1. ✅ 更新 `backend/app/agents/dialogue_manager.py`
2. ✅ 集成矛盾检测引擎（contradiction_detector）
3. ✅ 集成反驳决策引擎（refusal_decision_engine）
4. ✅ 实现反驳计数管理（refusal_count、last_refusal_reset）
5. ✅ 更新 process_user_message() 完整流程
6. ✅ 实现 _reset_refusal_count() 方法
7. ✅ 实现 _get_dialogue_history() 方法
8. ✅ 实现反驳回复生成与合并逻辑

#### Phase 5：嫌疑人Agent增强 ✅ 100%
1. ✅ 更新 `backend/app/agents/suspect_agent.py`
2. ✅ 添加 respond_with_prompt() 方法 - 支持自定义提示词生成回复

#### Phase 5：案件生成器更新 ✅ 100%
1. ✅ 更新 `backend/app/agents/case_generator_agent.py` - 提示词中添加矛盾点生成要求
2. ✅ 实现 _enhance_case_with_contradictions() 主增强方法
3. ✅ 实现 _add_suspect_enhancements() - 为嫌疑人添加增强字段
4. ✅ 实现 _generate_counter_evidence() - 生成反驳证据
5. ✅ 实现 _generate_contradiction_points() - 生成2-4个矛盾点
6. ✅ 实现 _create_timeline_contradiction() - 创建时间线矛盾
7. ✅ 实现 _create_spatial_contradiction() - 创建空间矛盾
8. ✅ 实现 _create_evidence_contradiction() - 创建证据矛盾
9. ✅ 实现 _add_contradiction_clues() - 添加矛盾线索
10. ✅ 实现 _create_contradiction_clue() - 创建单个矛盾线索

#### Phase 6-9：前端功能增强 ✅ 100%
1. ✅ 创建 `frontend/src/components/TypewriterText.tsx` - 打字机效果组件
   - 可配置速度
   - 根据 mood 调整速度（nervous/scared 更快，calm 更慢）
   - 支持点击跳过动画
   - 光标闪烁效果
2. ✅ 创建 `frontend/src/components/SuspectMentions.tsx` - @嫌疑人组件
   - Ant Design Mentions 组件集成
   - 显示嫌疑人姓名+职业
   - 自动解析目标嫌疑人ID
3. ✅ 更新 `frontend/src/components/MessageBox.tsx`
   - 集成 TypewriterText 组件
   - 添加系统提示特殊样式（金色渐变、高亮效果）
   - SystemHint 组件实现
4. ✅ 更新 `frontend/src/pages/Interrogation.tsx`
   - 集成 SuspectMentions 组件
   - 集成 TypewriterText 组件
   - 添加单独审讯背景变暗效果（overlay）
   - 添加保密标签（SecretLabel）
   - 其他嫌疑人头像变灰效果

---

## 矛盾检测与反驳机制 - 功能完成度验证

### 设计方案功能点检查清单：

| 功能模块 | 功能点 | 状态 | 文件位置 |
|---------|---------|------|---------|
| **数据模型** | ContradictionType 枚举 | ✅ | `backend/app/core/constants.py` |
| | ContradictionPoint 模型 | ✅ | `backend/app/models/case.py` |
| | Suspect 增强字段 | ✅ | `backend/app/models/case.py` |
| | Case.contradiction_points 字段 | ✅ | `backend/app/models/case.py` |
| | GameSession 反驳计数字段 | ✅ | `backend/app/models/game.py` |
| **矛盾检测引擎** | ContradictionDetector 类 | ✅ | `backend/app/agents/contradiction_detector.py` |
| | analyze_dialogue() 方法 | ✅ | `backend/app/agents/contradiction_detector.py` |
| | 触发条件检查 | ✅ | `backend/app/agents/contradiction_detector.py` |
| | 系统提示生成 | ✅ | `backend/app/agents/contradiction_detector.py` |
| | 矛盾线索生成 | ✅ | `backend/app/agents/contradiction_detector.py` |
| **反驳决策引擎** | ThreatLevel 枚举 | ✅ | `backend/app/agents/refusal_decision_engine.py` |
| | RefusalDecisionEngine 类 | ✅ | `backend/app/agents/refusal_decision_engine.py` |
| | 威胁程度评估 | ✅ | `backend/app/agents/refusal_decision_engine.py` |
| | 反驳证据检查 | ✅ | `backend/app/agents/refusal_decision_engine.py` |
| | 人设因素考虑 | ✅ | `backend/app/agents/refusal_decision_engine.py` |
| | 最终决策逻辑 | ✅ | `backend/app/agents/refusal_decision_engine.py` |
| | 反驳次数限制（每轮2次） | ✅ | `backend/app/agents/refusal_decision_engine.py` |
| **对话管理器集成** | 矛盾检测引擎集成 | ✅ | `backend/app/agents/dialogue_manager.py` |
| | 反驳决策引擎集成 | ✅ | `backend/app/agents/dialogue_manager.py` |
| | 反驳计数管理 | ✅ | `backend/app/agents/dialogue_manager.py` |
| | process_user_message 流程更新 | ✅ | `backend/app/agents/dialogue_manager.py` |
| **案件生成器** | 嫌疑人增强字段自动生成 | ✅ | `backend/app/agents/case_generator_agent.py` |
| | 矛盾点自动生成（2-4个） | ✅ | `backend/app/agents/case_generator_agent.py` |
| | 时间线矛盾 | ✅ | `backend/app/agents/case_generator_agent.py` |
| | 空间矛盾 | ✅ | `backend/app/agents/case_generator_agent.py` |
| | 证据矛盾 | ✅ | `backend/app/agents/case_generator_agent.py` |
| | 矛盾线索自动添加 | ✅ | `backend/app/agents/case_generator_agent.py` |
| **嫌疑人Agent** | respond_with_prompt() 方法 | ✅ | `backend/app/agents/suspect_agent.py` |
| **前端@嫌疑人** | SuspectMentions 组件 | ✅ | `frontend/src/components/SuspectMentions.tsx` |
| | Interrogation 页面集成 | ✅ | `frontend/src/pages/Interrogation.tsx` |
| **前端打字机** | TypewriterText 组件 | ✅ | `frontend/src/components/TypewriterText.tsx` |
| | 根据 mood 调整速度 | ✅ | `frontend/src/components/TypewriterText.tsx` |
| | MessageBox 集成 | ✅ | `frontend/src/components/MessageBox.tsx` |
| **前端系统提示** | 金色渐变样式 | ✅ | `frontend/src/components/MessageBox.tsx` |
| | SystemHint 组件 | ✅ | `frontend/src/components/MessageBox.tsx` |
| **前端单独审讯** | 背景变暗效果 | ✅ | `frontend/src/pages/Interrogation.tsx` |
| | 保密标签 | ✅ | `frontend/src/pages/Interrogation.tsx` |
| | 其他头像变灰 | ✅ | `frontend/src/pages/Interrogation.tsx` |

### 总体完成度：**100%**
- 核心功能：✅ 100% 完成
- 前端体验：✅ 100% 完成
- 案件生成器增强：✅ 100% 完成

---

## 项目总进度更新
- **当前阶段**：Wave 7 矛盾检测与反驳机制已完成！
- **总进度**：100%
- **状态**：✅ 所有功能已实现，项目v1.0版本完整交付！

### 关键技术决策实现确认：
| 决策项 | 选择方案 | 实现状态 |
|---------|----------|---------|
| 矛盾检测方式 | 预定义矛盾点 + 规则引擎 | ✅ 已实现 |
| 反驳决策 | 威胁分×证据分×人设修正系数 | ✅ 已实现 |
| 前端打字机 | React useState + setTimeout | ✅ 已实现 |
| @嫌疑人功能 | Ant Design Mentions 组件 | ✅ 已实现 |
| 反驳次数限制 | 每轮最多2次 | ✅ 已实现 |
| 案件生成器 | 自动生成矛盾点+嫌疑人增强 | ✅ 已实现 |

### 完整功能清单（Wave7新增）：
1. **后端核心引擎**：
   - 矛盾检测引擎（ContradictionDetector）
   - 反驳决策引擎（RefusalDecisionEngine）
   - 威胁程度评估（LOW/MEDIUM/HIGH/CRITICAL）
   - 最终得分计算：威胁分×证据分×人设修正系数

2. **数据模型增强**：
   - ContradictionType枚举（时间线/空间/证据）
   - ContradictionPoint完整模型
   - Suspect增强：refusal_threshold/counter_evidence/personality_modifier/spatial_relationships
   - Case增强：contradiction_points字段
   - GameSession增强：refusal_count/last_refusal_reset

3. **案件生成器增强**：
   - 自动生成2-4个矛盾点（时间线/空间/证据）
   - 自动为嫌疑人添加增强字段
   - 自动添加矛盾相关线索

4. **前端体验提升**：
   - @嫌疑人功能（SuspectMentions组件）
   - 打字机效果（TypewriterText组件，支持mood调速）
   - 系统提示金色渐变样式
   - 单独审讯模式增强（背景变暗、保密标签、头像变灰）
