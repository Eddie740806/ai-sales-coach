"""
速率限制 - 使用slowapi
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)

# 速率限制配置
RATE_LIMITS = {
    "default": "100/minute",  # 默认限制
    "chat": "30/minute",  # 对话API限制
    "search": "60/minute",  # 搜索API限制
    "generate": "10/minute",  # 生成API限制
}

