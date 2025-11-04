"""
缓存系统 - LRU缓存实现
"""
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from collections import OrderedDict
from .config import settings
from .logger import logger

class LRUCache:
    """LRU缓存实现"""
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl  # 过期时间（秒）
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, datetime] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key not in self.cache:
            return None
        
        # 检查是否过期
        if key in self.timestamps:
            if datetime.now() - self.timestamps[key] > timedelta(seconds=self.ttl):
                self.delete(key)
                return None
        
        # 移到末尾（最近使用）
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def set(self, key: str, value: Any):
        """设置缓存值"""
        if key in self.cache:
            # 更新现有值
            self.cache.move_to_end(key)
        else:
            # 如果超过最大大小，删除最旧的
            if len(self.cache) >= self.max_size:
                oldest_key = next(iter(self.cache))
                self.delete(oldest_key)
        
        self.cache[key] = value
        self.timestamps[key] = datetime.now()
    
    def delete(self, key: str):
        """删除缓存"""
        if key in self.cache:
            del self.cache[key]
        if key in self.timestamps:
            del self.timestamps[key]
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.timestamps.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self.cache)

# 全局缓存实例
cache = LRUCache(max_size=200, ttl=settings.cache_ttl) if settings.cache_enabled else None

def cached(key_func: Optional[Callable] = None, ttl: Optional[int] = None):
    """缓存装饰器"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            if not cache:
                return func(*args, **kwargs)
            
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"缓存命中：{cache_key}")
                return cached_value
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            logger.debug(f"缓存设置：{cache_key}")
            return result
        
        return wrapper
    return decorator

