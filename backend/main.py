"""FastAPI应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.exceptions import AppBaseException
from app.utils.logger import logger

# 生命周期事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} 启动中...")
    logger.info(f"🔧 运行环境: {'开发' if settings.DEBUG else '生产'}")

    # 启动前初始化
    # TODO: 初始化数据库连接、模型客户端等

    yield

    # 关闭前清理
    logger.info(f"👋 {settings.PROJECT_NAME} 已关闭")

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI驱动的案件解谜应用API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# 注册路由
from app.api.v1 import game, agent, user
app.include_router(game.router, prefix=f"{settings.API_V1_STR}/game", tags=["游戏管理"])
app.include_router(agent.router, prefix=f"{settings.API_V1_STR}/agent", tags=["AI交互"])
app.include_router(user.router, prefix=f"{settings.API_V1_STR}/user", tags=["用户管理"])

# 根路径
@app.get("/", tags=["健康检查"])
async def root():
    """健康检查接口"""
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs" if settings.DEBUG else None,
    }

# 全局异常处理
from fastapi.responses import JSONResponse
@app.exception_handler(AppBaseException)
async def app_base_exception_handler(request, exc: AppBaseException):
    """自定义异常处理"""
    logger.error(f"请求异常: {exc.detail}, 路径: {request.url.path}, 方法: {request.method}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.detail,
            "data": exc.extra,
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
