"""
持续学习系统
从对话和反馈中学习，不断改进
"""
from typing import List, Dict, Optional
from .models import Conversation, LearningInsight, SalesScript
from .database import SessionLocal, LearningInsightModel, ConversationModel
from .logger import logger
from datetime import datetime
import uuid

class LearningSystem:
    def __init__(self):
        self.insights: Dict[str, List[LearningInsight]] = {}
        self.patterns: Dict[str, Dict] = {}  # 发现的模式
    
    def analyze_conversation(self, conversation: Conversation) -> List[LearningInsight]:
        """分析对话，提取学习洞察"""
        insights = []
        
        # 1. 分析对话质量
        if conversation.feedback_score:
            if conversation.feedback_score >= 4.5:
                insights.append(LearningInsight(
                    insight_type="strength",
                    content=f"此次对话表现优秀（{conversation.feedback_score}分），建议记录为最佳实践",
                    confidence=0.9,
                    related_conversations=[conversation.id] if conversation.id else [],
                    created_at=datetime.now()
                ))
            elif conversation.feedback_score <= 2.5:
                insights.append(LearningInsight(
                    insight_type="improvement",
                    content=f"此次对话需要改进（{conversation.feedback_score}分），建议加强相关培训",
                    confidence=0.85,
                    related_conversations=[conversation.id] if conversation.id else [],
                    created_at=datetime.now()
                ))
        
        # 2. 识别常见问题模式
        common_issues = self._identify_common_issues(conversation)
        for issue in common_issues:
            insights.append(LearningInsight(
                insight_type="pattern",
                content=issue,
                confidence=0.75,
                created_at=datetime.now()
            ))
        
        # 保存洞察到数据库
        if conversation.sales_id:
            db = SessionLocal()
            try:
                for insight in insights:
                    insight_id = f"insight_{uuid.uuid4().hex[:8]}"
                    insight.id = insight_id
                    
                    db_insight = LearningInsightModel(
                        id=insight_id,
                        sales_id=conversation.sales_id,
                        insight_type=insight.insight_type,
                        content=insight.content,
                        confidence=insight.confidence,
                        related_conversations=insight.related_conversations,
                        created_at=insight.created_at
                    )
                    db.add(db_insight)
                
                db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"保存洞察错误：{e}", exc_info=True)
            finally:
                db.close()
            
            # 更新内存缓存
            if conversation.sales_id not in self.insights:
                self.insights[conversation.sales_id] = []
            self.insights[conversation.sales_id].extend(insights)
        
        return insights
    
    def _identify_common_issues(self, conversation: Conversation) -> List[str]:
        """识别常见问题 - 增强模式识别"""
        issues = []
        
        if not conversation.messages:
            return issues
        
        user_messages = [m for m in conversation.messages if m.role == "user"]
        assistant_messages = [m for m in conversation.messages if m.role == "assistant"]
        
        # 1. 对话长度分析
        if len(user_messages) > 10:
            issues.append("对话过长，可能表示需求未及时满足")
        
        # 2. 重复问题检测
        questions = [m.content.lower() for m in user_messages if "?" in m.content]
        if len(questions) > 2:
            unique_questions = set(questions)
            if len(unique_questions) < len(questions) * 0.7:
                issues.append("发现重复提问模式，建议优化话术")
        
        # 3. 响应时间分析（基于消息时间戳）
        if len(user_messages) > 1 and len(assistant_messages) > 0:
            # 检查是否有长时间等待（简化版）
            issues.append("建议关注响应速度，及时回复客户")
        
        # 4. 问题类型识别
        problem_keywords = {
            "价格异议": ["贵", "价格", "费用", "成本", "预算"],
            "功能疑虑": ["能", "可以", "功能", "特性", "支持"],
            "信任问题": ["真的", "确定", "保证", "可靠", "信任"]
        }
        
        all_user_text = " ".join([m.content.lower() for m in user_messages])
        detected_problems = []
        for problem_type, keywords in problem_keywords.items():
            if any(keyword in all_user_text for keyword in keywords):
                detected_problems.append(problem_type)
        
        if detected_problems:
            issues.append(f"检测到常见问题类型：{', '.join(detected_problems)}，建议针对性培训")
        
        return issues
    
    def update_script_effectiveness(self, script_id: str, success: bool):
        """更新话术效果 - 调用话术生成器的更新方法"""
        from .script_generator import script_generator
        script_generator.update_success_rate(script_id, success)
    
    def generate_personalized_training(self, sales_id: str) -> List[str]:
        """为特定业务员生成个性化训练建议 - 增强推荐"""
        # 从数据库加载洞察
        db = SessionLocal()
        try:
            db_insights = db.query(LearningInsightModel).filter(
                LearningInsightModel.sales_id == sales_id
            ).order_by(LearningInsightModel.created_at.desc()).limit(20).all()
            
            if not db_insights:
                return ["继续练习，保持良好表现"]
            
            improvements = [i for i in db_insights if i.insight_type == "improvement"]
            strengths = [i for i in db_insights if i.insight_type == "strength"]
            patterns = [i for i in db_insights if i.insight_type == "pattern"]
            
            suggestions = []
            
            # 1. 改进建议（按置信度排序）
            if improvements:
                sorted_improvements = sorted(improvements, key=lambda x: x.confidence, reverse=True)
                suggestions.extend([f"建议加强：{imp.content}" for imp in sorted_improvements[:3]])
            
            # 2. 优势保持
            if strengths:
                sorted_strengths = sorted(strengths, key=lambda x: x.confidence, reverse=True)
                suggestions.append(f"优势：{sorted_strengths[0].content}")
            
            # 3. 模式识别建议
            if patterns:
                pattern_summary = ", ".join([p.content[:30] for p in patterns[:2]])
                suggestions.append(f"发现模式：{pattern_summary}...")
            
            # 4. 推荐相关培训内容（基于问题类型）
            if improvements:
                # 从知识库推荐相关内容
                from .knowledge_base import knowledge_base
                from .models import ContentType
                
                # 提取关键词
                improvement_text = " ".join([imp.content for imp in improvements[:2]])
                recommended_content = knowledge_base.search_content(improvement_text)
                if len(recommended_content) > 2:
                    recommended_content = recommended_content[:2]
                
                if recommended_content:
                    suggestions.append(f"推荐培训内容：{recommended_content[0].title}")
            
            return suggestions if suggestions else ["表现良好，继续保持！"]
            
        finally:
            db.close()

# 全局学习系统实例
learning_system = LearningSystem()

