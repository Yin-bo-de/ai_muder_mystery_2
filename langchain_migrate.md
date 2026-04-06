# LangChain v1 Python 迁移指南

## 文档说明
本文档基于官方LangChain v1迁移指南整理，涵盖Python版本的完整迁移方案、导入路径变更、API调整和最佳实践。

官方源文档：https://docs.langchain.com/oss/python/migrate/langchain-v1

---

## 一、前置要求
### 1. Python版本要求
LangChain v1 要求 **Python 3.10 或更高版本**，已停止对Python 3.9及以下版本的支持。

### 2. 依赖升级
首先升级核心包到最新版本：
```bash
# 升级到最新版本
pip install -U langchain-core langchain

# 升级到指定稳定版本
pip install langchain-core==1.0.0 langchain==0.2.0
```

### 3. 安装langchain-classic（可选，按需）
如果项目使用了 legacy 功能（旧版chains、retrievers、indexing API、hub模块等），需要额外安装`langchain-classic`包：
```bash
pip install langchain-classic
```

---

## 二、核心架构变更说明
LangChain v1 对包结构进行了大幅精简，核心变更：
1. `langchain` 主包仅保留Agent开发的核心构建块，移除了大量历史遗留功能
2. 所有 legacy 功能（旧版chains、retrievers、indexing、hub等）迁移到 `langchain-classic` 包
3. 核心抽象层统一收敛到 `langchain-core` 包，所有集成功能收敛到 `langchain-community` 包
4. 第三方模型/工具集成独立为单独的包（如`langchain-openai`、`langchain-anthropic`等）

---

## 三、完整导入路径变更对照表

### 1. 核心抽象层（已从langchain迁移到langchain_core）
| 旧导入路径 | 新导入路径 |
|-----------|-----------|
| `from langchain.schema import Document` | `from langchain_core.documents import Document` |
| `from langchain.schema import BaseMessage, AIMessage, HumanMessage` | `from langchain_core.messages import BaseMessage, AIMessage, HumanMessage` |
| `from langchain.schema import OutputParserException` | `from langchain_core.output_parsers import OutputParserException` |
| `from langchain.schema import LLMResult` | `from langchain_core.outputs import LLMResult` |
| `from langchain.schema import AgentAction, AgentFinish` | `from langchain_core.agents import AgentAction, AgentFinish` |
| `from langchain.schema import BaseRetriever` | `from langchain_core.retrievers import BaseRetriever` |
| `from langchain.prompts import ChatPromptTemplate` | `from langchain_core.prompts.chat import ChatPromptTemplate` |
| `from langchain.output_parsers.string import StrOutputParser` | `from langchain_core.output_parsers.string import StrOutputParser` |
| `from langchain.runnables import RunnablePassthrough` | `from langchain_core.runnables.passthrough import RunnablePassthrough` |

### 2. Legacy功能（已从langchain迁移到langchain_classic）
| 旧导入路径 | 新导入路径 |
|-----------|-----------|
| `from langchain.chains import LLMChain, RetrievalQA` | `from langchain_classic.chains import LLMChain, RetrievalQA` |
| `from langchain.retrievers import *`（旧版retrievers） | `from langchain_classic.retrievers import *` |
| `from langchain.retrievers.contextual_compression import ContextualCompressionRetriever` | `from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever` |
| `from langchain.retrievers.document_compressors import FlashrankRerank` | `from langchain_classic.retrievers.document_compressors import FlashrankRerank` |
| `from langchain.retrievers.multi_query import MultiQueryRetriever` | `from langchain_classic.retrievers.multi_query import MultiQueryRetriever` |
| `from langchain.indexes import *` | `from langchain_classic.indexes import *` |
| `from langchain import hub` | `from langchain_classic import hub` |
| `from langchain.embeddings import *`（旧版embeddings实现） | `from langchain_classic.embeddings import *` |

### 3. 社区集成（已从langchain迁移到langchain_community）
| 旧导入路径 | 新导入路径 |
|-----------|-----------|
| `from langchain.document_loaders import TextLoader` | `from langchain_community.document_loaders import TextLoader` |
| `from langchain.vectorstores import FAISS, DeepLake` | `from langchain_community.vectorstores import FAISS, DeepLake` |
| `from langchain.callbacks import *` | `from langchain_community.callbacks import *` |

### 4. 第三方集成（独立为单独包）
| 旧导入路径 | 新导入路径 |
|-----------|-----------|
| `from langchain.llms import OpenAI` | `from langchain_openai import OpenAI` |
| `from langchain.chat_models import ChatOpenAI` | `from langchain_openai import ChatOpenAI` |
| `from langchain.embeddings import OpenAIEmbeddings` | `from langchain_openai import OpenAIEmbeddings` |
| `from langchain.chat_models import ChatAnthropic` | `from langchain_anthropic import ChatAnthropic` |
| `from langchain.text_splitter import RecursiveCharacterTextSplitter` | `from langchain_text_splitters import RecursiveCharacterTextSplitter` |

---

## 四、分步迁移指南
### 步骤1：检查Python版本
确保项目运行在Python 3.10+环境：
```bash
python --version
```

### 步骤2：升级所有LangChain相关依赖
```bash
# 升级核心包
pip install -U langchain-core langchain langchain-community

# 如果使用legacy功能，安装langchain-classic
pip install langchain-classic

# 升级第三方集成包
pip install -U langchain-openai langchain-anthropic langchain-text-splitters
```

### 步骤3：批量更新导入路径
按照上述对照表，批量替换项目中的导入路径，推荐使用IDE的全局替换功能。

### 步骤4：运行测试验证
运行项目单元测试，检查是否有导入错误或API调用错误。

### 步骤5：逐步重构legacy代码（可选）
对于使用`langchain_classic`的legacy代码，建议逐步重构为v1推荐的LCEL（LangChain Expression Language）写法，例如：
- 旧版`LLMChain` → 替换为LCEL链式调用
- 旧版`RetrievalQA` → 替换为RunnablePassthrough + 提示词 + 模型 + 输出解析器的组合

---

## 五、常见问题与注意事项
1. **导入错误排查**：如果遇到`ModuleNotFoundError`，优先检查是否安装了对应的包，以及导入路径是否正确。
2. **langchain-classic兼容性**：`langchain-classic`是过渡包，长期来看建议逐步迁移到LCEL写法，避免依赖legacy功能。
3. **类型提示问题**：v1版本提供了更完整的类型提示，如果遇到类型错误，优先检查API参数是否匹配最新文档。
4. **性能优化**：v1版本对核心路径进行了性能优化，迁移后建议对比性能指标，充分利用新版本的性能提升。
5. **文档参考**：最新API文档请访问[LangChain官方文档](https://docs.langchain.com/)，优先参考v1版本的文档。
