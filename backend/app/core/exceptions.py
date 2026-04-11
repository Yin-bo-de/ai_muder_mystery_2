"""自定义异常类"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status

class AppBaseException(HTTPException):
    """应用基础异常类"""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail: str = "服务器内部错误"
    default_code: int = 50000

    def __init__(
        self,
        detail: Optional[str] = None,
        code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None,
        **extra: Any,
    ) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.default_detail,
            headers=headers,
        )
        self.code = code or self.default_code
        self.extra = extra

class BadRequestException(AppBaseException):
    """请求参数错误"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "请求参数错误"
    default_code = 40000

class UnauthorizedException(AppBaseException):
    """未授权"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "未授权访问"
    default_code = 40100

class ForbiddenException(AppBaseException):
    """禁止访问"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "禁止访问"
    default_code = 40300

class NotFoundException(AppBaseException):
    """资源不存在"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "资源不存在"
    default_code = 40400

class ConflictException(AppBaseException):
    """资源冲突"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = "资源冲突"
    default_code = 40900

class ValidationException(AppBaseException):
    """数据验证失败"""
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    default_detail = "数据验证失败"
    default_code = 42200

class BusinessException(AppBaseException):
    """业务逻辑异常"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "业务逻辑错误"
    default_code = 50000

# 业务异常细分
class SessionNotFoundException(BusinessException):
    """会话不存在"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "游戏会话不存在"
    default_code = 10001

class GameCompletedException(BusinessException):
    """游戏已结束"""
    default_detail = "游戏已结束，无法进行操作"
    default_code = 10002

class CaseGenerateException(BusinessException):
    """案件生成失败"""
    default_detail = "案件生成失败，请重试"
    default_code = 20001

class AgentResponseException(BusinessException):
    """Agent响应失败"""
    default_detail = "AI响应失败，请重试"
    default_code = 20002

class ClueNotFoundException(BusinessException):
    """线索不存在"""
    default_detail = "线索不存在"
    default_code = 30001

class ClueDecryptException(BusinessException):
    """线索解密失败"""
    default_detail = "解密失败，请检查密码或关联线索是否正确"
    default_code = 30002

class AccusationInvalidException(BusinessException):
    """指认信息无效"""
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    default_detail = "指认信息不完整，请补充必要信息"
    default_code = 30003

class ModelInvokeException(BusinessException):
    """模型调用失败"""
    default_detail = "AI模型调用失败，请稍后重试"
    default_code = 40001

class QuotaExceededException(BusinessException):
    """配额不足"""
    default_detail = "API调用配额不足，请联系管理员"
    default_code = 40002
