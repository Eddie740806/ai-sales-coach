"""
对话引擎 - RAG系统
结合知识库和LLM生成智能回复
"""
from typing import List, Dict, Optional
from .models import ChatRequest, ChatResponse, Conversation, ConversationMessage
from .knowledge_base import knowledge_base
from .llm_service import llm_service
from .database import SessionLocal, ConversationModel
from .logger import logger
from .cache import cache
from datetime import datetime
import uuid

class ConversationEngine:
    def __init__(self):
        # 这里应该集成实际的LLM（OpenAI, Anthropic, 本地模型等）
        # 暂时用模拟响应
        self.conversation_history: Dict[str, List[Conversation]] = {}
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        """处理对话请求"""
        # 1. 从知识库检索相关内容
        from .database import SessionLocal
        db = SessionLocal()
        try:
            relevant_content = knowledge_base.search_content(request.message, None, db) or []
        except Exception as e:
            logger.error(f"搜索知识库错误：{e}", exc_info=True)
            relevant_content = []
        finally:
            db.close()
        
        # 2. 获取用户的历史对话（用于上下文）
        # 使用request.sales_id作为用户标识（可能是用户ID或sales_id）
        user_id = request.sales_id
        # 优先从数据库加载，如果内存中有则使用内存的
        user_history = self.conversation_history.get(user_id, [])
        if not user_history:
            # 从数据库加载最近10条对话
            user_history = self.get_conversation_history(user_id, limit=10)
            # 更新内存缓存
            if user_history:
                self.conversation_history[user_id] = user_history
        
        # 3. 构建上下文提示
        context = self._build_context(relevant_content, user_history, request)
        
        # 4. 生成回复（使用真实LLM）
        response_text = self._generate_response(request.message, context, user_history)
        
        # 5. 提取相关话术建议
        suggestions = self._extract_suggestions(relevant_content, request)
        
        # 6. 返回响应
        return ChatResponse(
            response=response_text,
            suggestions=suggestions[:3],  # 前3个建议
            related_scripts=self._get_related_scripts(request),
            confidence=0.85
        )
    
    def _build_context(self, content: List, history: List[Conversation], request: ChatRequest) -> str:
        """构建上下文"""
        context_parts = []
        
        # 添加相關培訓內容
        for item in content[:3]:  # 取前3個最相關的
            context_parts.append(f"培訓內容：{item.title}\n{item.content[:200]}...")
        
        # 添加歷史對話摘要
        if history:
            recent = history[-1]  # 最近的對話
            context_parts.append(f"最近對話場景：{recent.scenario}")
        
        return "\n\n".join(context_parts)
    
    def _generate_response(self, message: str, context: str, history: List[Conversation]) -> str:
        """生成回复 - 使用真实LLM"""
        system_prompt = """你是一個專業的銷售教練AI助手。你的任務是：
1. 幫助業務員解決銷售過程中的問題
2. 提供基於最佳實踐的建議
3. 推薦合適的話術和策略
4. 持續學習和改進

請用專業、友好、實用的方式回答，並給出具體的行動建議。

**重要：請務必使用繁體中文回答，不要使用簡體中文。所有回應都必須是繁體中文。**"""
        
        # 构建历史对话
        conversation_history = []
        for conv in history[-3:]:  # 最近3次对话
            for msg in conv.messages[-4:]:  # 每次对话最近4条消息
                conversation_history.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # 调用LLM服务
        response = llm_service.generate_response(
            system_prompt=system_prompt,
            user_message=message,
            context=context,
            conversation_history=conversation_history
        )
        
        return response
    
    def _extract_suggestions(self, content: List, request: ChatRequest) -> List[str]:
        """提取建議"""
        suggestions = []
        for item in content[:2]:
            suggestions.append(f"參考：{item.title}")
        return suggestions
    
    def _get_related_scripts(self, request: ChatRequest) -> List[str]:
        """获取相关话术"""
        # 这里应该从话术库中检索
        return ["script_001", "script_002"]
    
    def save_conversation(self, sales_id: str, conversation: Conversation):
        """保存对话记录到数据库和内存"""
        # 生成对话ID
        if not conversation.id:
            conversation.id = f"conv_{uuid.uuid4().hex[:8]}"
        
        # 保存到数据库
        db = SessionLocal()
        try:
            # 转换消息为JSON格式
            messages_json = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if isinstance(msg.timestamp, datetime) else str(msg.timestamp),
                    "metadata": msg.metadata
                }
                for msg in conversation.messages
            ]
            
            db_conversation = ConversationModel(
                id=conversation.id,
                sales_id=conversation.sales_id,
                customer_type=conversation.customer_type,
                scenario=conversation.scenario,
                messages=messages_json,
                feedback_score=conversation.feedback_score,
                created_at=conversation.created_at,
                learning_insights=conversation.learning_insights
            )
            db.add(db_conversation)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"保存对话到数据库错误：{e}", exc_info=True)
        finally:
            db.close()
        
        # 同时保存到内存缓存（用于快速访问）
        if sales_id not in self.conversation_history:
            self.conversation_history[sales_id] = []
        self.conversation_history[sales_id].append(conversation)
    
    def get_conversation_history(self, sales_id: str, limit: int = 10) -> List[Conversation]:
        """从数据库加载对话历史（带缓存）"""
        # 生成缓存键
        cache_key = f"history:{sales_id}:{limit}"
        
        # 尝试从缓存获取
        if cache:
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"对话历史缓存命中：{sales_id}")
                return cached_result
        db = SessionLocal()
        try:
            db_conversations = db.query(ConversationModel).filter(
                ConversationModel.sales_id == sales_id
            ).order_by(ConversationModel.created_at.desc()).limit(limit).all()
            
            conversations = []
            for db_conv in db_conversations:
                # 转换消息
                messages = [
                    ConversationMessage(
                        role=msg["role"],
                        content=msg["content"],
                        timestamp=datetime.fromisoformat(msg["timestamp"]) if isinstance(msg["timestamp"], str) else msg["timestamp"],
                        metadata=msg.get("metadata")
                    )
                    for msg in db_conv.messages
                ]
                
                conversation = Conversation(
                    id=db_conv.id,
                    sales_id=db_conv.sales_id,
                    customer_type=db_conv.customer_type,
                    scenario=db_conv.scenario,
                    messages=messages,
                    feedback_score=db_conv.feedback_score,
                    created_at=db_conv.created_at,
                    learning_insights=db_conv.learning_insights
                )
                conversations.append(conversation)
            
            # 缓存结果
            if cache:
                cache.set(cache_key, conversations)
            
            return conversations
        finally:
            db.close()

# 全局对话引擎实例
conversation_engine = ConversationEngine()

