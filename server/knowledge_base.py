"""
知识库管理模块
负责存储、检索和管理所有培训内容和知识
"""
from typing import List, Dict, Optional
from .models import TrainingContent, ContentType
from .vector_db import vector_db
from .database import SessionLocal, TrainingContentModel, get_db
from sqlalchemy.orm import Session
from .logger import logger
from .cache import cache, cached
import json
from datetime import datetime
import uuid

class KnowledgeBase:
    def __init__(self):
        # 内存缓存
        self.contents: Dict[str, TrainingContent] = {}
        self.search_index: Dict[str, List[str]] = {}  # tag -> content_ids
        # 启动时从数据库加载所有内容
        self._load_from_database()
    
    def _load_from_database(self):
        """从数据库加载所有内容到内存缓存"""
        db = SessionLocal()
        try:
            db_contents = db.query(TrainingContentModel).all()
            for db_content in db_contents:
                content = TrainingContent(
                    id=db_content.id,
                    title=db_content.title,
                    content=db_content.content,
                    content_type=ContentType(db_content.content_type),
                    tags=db_content.tags or [],
                    created_by=db_content.created_by,
                    created_at=db_content.created_at,
                    usage_count=db_content.usage_count or 0,
                    effectiveness_score=db_content.effectiveness_score
                )
                self.contents[content.id] = content
                
                # 更新搜索索引
                for tag in content.tags:
                    if tag not in self.search_index:
                        self.search_index[tag] = []
                    if content.id not in self.search_index[tag]:
                        self.search_index[tag].append(content.id)
        except Exception as e:
            logger.error(f"从数据库加载内容错误：{e}", exc_info=True)
        finally:
            db.close()
    
    def add_content(self, content: TrainingContent, db: Optional[Session] = None) -> str:
        """添加培训内容"""
        content_id = content.id or f"kb_{uuid.uuid4().hex[:8]}"
        content.id = content_id
        
        # 保存到数据库
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            db_content = TrainingContentModel(
                id=content_id,
                title=content.title,
                content=content.content,
                content_type=content.content_type.value,
                tags=content.tags,
                created_by=content.created_by,
                created_at=content.created_at or datetime.now(),
                usage_count=content.usage_count,
                effectiveness_score=content.effectiveness_score
            )
            db.add(db_content)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"数据库保存错误：{e}", exc_info=True)
        finally:
            if should_close:
                db.close()
        
        # 添加到向量数据库（确保metadata包含id）
        vector_db.add_content(
            content_id=content_id,
            text=f"{content.title}\n{content.content}",
            metadata={
                "id": content_id,  # 确保包含id
                "title": content.title,
                "content_type": content.content_type.value,
                "tags": ",".join(content.tags),
                "created_by": content.created_by
            }
        )
        
        # 更新内存缓存
        self.contents[content_id] = content
        
        # 更新搜索索引
        for tag in content.tags:
            if tag not in self.search_index:
                self.search_index[tag] = []
            self.search_index[tag].append(content_id)
        
        return content_id
    
    def search_content(self, query: str, content_type: Optional[ContentType] = None, db: Optional[Session] = None) -> List[TrainingContent]:
        """搜索相关内容 - 使用向量搜索和缓存"""
        # 生成缓存键
        cache_key = f"search:{query}:{content_type.value if content_type else 'all'}"
        
        # 尝试从缓存获取
        if cache:
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"搜索缓存命中：{query}")
                return cached_result
        # 1. 使用向量数据库搜索
        vector_results = vector_db.search(query, n_results=10)
        
        # 2. 从数据库加载完整内容
        results = []
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            for result in vector_results:
                # 从metadata中提取content_id
                content_id = result.get('metadata', {}).get('id')
                if not content_id:
                    continue
                
                db_content = db.query(TrainingContentModel).filter(
                    TrainingContentModel.id == content_id
                ).first()
                
                if db_content:
                    # 过滤内容类型
                    if content_type and db_content.content_type != content_type.value:
                        continue
                    
                    # 转换为模型
                    content = TrainingContent(
                        id=db_content.id,
                        title=db_content.title,
                        content=db_content.content,
                        content_type=ContentType(db_content.content_type),
                        tags=db_content.tags or [],
                        created_by=db_content.created_by,
                        created_at=db_content.created_at,
                        usage_count=db_content.usage_count,
                        effectiveness_score=db_content.effectiveness_score
                    )
                    results.append(content)
        finally:
            if should_close:
                db.close()
        
        # 3. 如果向量搜索没结果，回退到关键词搜索
        if not results:
            query_lower = query.lower()
            for content in self.contents.values():
                if content_type and content.content_type != content_type:
                    continue
                
                if (query_lower in content.title.lower() or 
                    query_lower in content.content.lower() or
                    any(query_lower in tag.lower() for tag in content.tags)):
                    results.append(content)
        
        # 4. 按相关性排序
        sorted_results = sorted(results, key=lambda x: (x.effectiveness_score or 0, x.usage_count), reverse=True)
        
        # 缓存结果
        if cache:
            cache.set(cache_key, sorted_results)
        
        return sorted_results
    
    def get_content(self, content_id: str, db: Optional[Session] = None) -> Optional[TrainingContent]:
        """获取特定内容 - 优先从缓存，否则从数据库"""
        # 先从缓存查找
        if content_id in self.contents:
            return self.contents[content_id]
        
        # 从数据库加载
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            db_content = db.query(TrainingContentModel).filter(
                TrainingContentModel.id == content_id
            ).first()
            
            if db_content:
                content = TrainingContent(
                    id=db_content.id,
                    title=db_content.title,
                    content=db_content.content,
                    content_type=ContentType(db_content.content_type),
                    tags=db_content.tags or [],
                    created_by=db_content.created_by,
                    created_at=db_content.created_at,
                    usage_count=db_content.usage_count or 0,
                    effectiveness_score=db_content.effectiveness_score
                )
                # 更新缓存
                self.contents[content_id] = content
                return content
        finally:
            if should_close:
                db.close()
        
        return None
    
    def get_by_tags(self, tags: List[str]) -> List[TrainingContent]:
        """根据标签获取内容"""
        content_ids = set()
        for tag in tags:
            if tag in self.search_index:
                content_ids.update(self.search_index[tag])
        
        return [self.contents[cid] for cid in content_ids if cid in self.contents]
    
    def update_effectiveness(self, content_id: str, score: float):
        """更新内容效果评分"""
        if content_id in self.contents:
            self.contents[content_id].effectiveness_score = score
            self.contents[content_id].usage_count += 1

# 全局知识库实例
knowledge_base = KnowledgeBase()

