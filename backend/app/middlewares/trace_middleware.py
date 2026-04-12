"""追踪中间件 - 为请求添加唯一追踪ID"""
import uuid
import contextvars
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


# 上下文变量，用于存储当前请求的追踪ID
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


class TraceMiddleware(BaseHTTPMiddleware):
    """追踪中间件

    为每个请求生成或继承唯一追踪ID
    """

    # 追踪ID的HTTP头名称
    TRACE_ID_HEADER = "X-Request-ID"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """中间件处理逻辑"""
        # 1. 从请求头获取或生成追踪ID
        trace_id = request.headers.get(self.TRACE_ID_HEADER)
        if not trace_id:
            trace_id = str(uuid.uuid4())

        # 2. 存储到上下文变量
        request_id_var.set(trace_id)

        # 3. 记录请求开始
        logger.info(f"[{trace_id}] 请求开始: {request.method} {request.url.path}")

        # 4. 继续处理请求
        response = await call_next(request)

        # 5. 将追踪ID添加到响应头
        response.headers[self.TRACE_ID_HEADER] = trace_id

        # 6. 记录请求结束
        logger.info(f"[{trace_id}] 请求完成: {request.method} {request.url.path}, 状态码: {response.status_code}")

        return response


def get_request_id() -> str:
    """获取当前请求的追踪ID"""
    return request_id_var.get()


def with_request_id(message: str) -> str:
    """将追踪ID添加到消息中"""
    trace_id = get_request_id()
    return f"[{trace_id}] {message}"
