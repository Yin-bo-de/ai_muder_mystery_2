from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Union

class Settings(BaseSettings):
    """项目配置"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # 基础配置
    PROJECT_NAME: str = "AI Murder Mystery"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # 前端开发地址
        "http://127.0.0.1:5173",
    ]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    # OpenAI配置
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 32000

    # Anthropic配置
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"

    # 游戏配置
    MAX_WRONG_GUESS: int = 2  # 最大错误指认次数
    SESSION_EXPIRE_HOURS: int = 24  # 会话过期时间（小时）

    # Agent配置
    SUSPECT_AGENT_MAX_CONTEXT: int = 20  # 嫌疑人Agent最大上下文消息数
    CASE_GENERATE_TIMEOUT: int = 60  # 案件生成超时时间（秒）
    AGENT_RESPONSE_TIMEOUT: int = 30  # Agent响应超时时间（秒）

settings = Settings()
