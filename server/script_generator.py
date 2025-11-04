"""
话术生成器
AI辅助生成和优化销售话术
"""
from typing import List, Optional, Dict
from .models import SalesScript, ScriptGenerationRequest
from .knowledge_base import knowledge_base
from .llm_service import llm_service
from .database import SessionLocal, SalesScriptModel
from .logger import logger
from datetime import datetime
import uuid

class ScriptGenerator:
    def __init__(self):
        self.scripts: Dict[str, SalesScript] = {}
    
    def generate_script(self, request: ScriptGenerationRequest, created_by: str = "system") -> SalesScript:
        """生成新话术"""
        from .database import SessionLocal
        db = SessionLocal()
        try:
            # 1. 检索相关话术和培训内容
            related_content = knowledge_base.search_content(request.scenario, None, db)
        finally:
            db.close()
        
        # 2. 如果有基础话术，基于它优化
        if request.base_script_id:
            base_script = self.scripts.get(request.base_script_id)
            if base_script:
                script_text = self._optimize_script(base_script.script, request)
            else:
                script_text = self._generate_from_scratch(request, related_content)
        else:
            script_text = self._generate_from_scratch(request, related_content)
        
        # 3. 生成变体
        variants = self._generate_variants(script_text)
        
        # 4. 创建话术对象
        script_id = f"script_{uuid.uuid4().hex[:8]}"
        script = SalesScript(
            id=script_id,
            title=f"{request.scenario} - {request.customer_type or '通用'}",
            script=script_text,
            scenario=request.scenario,
            customer_type=request.customer_type,
            tags=[request.scenario, request.customer_type] if request.customer_type else [request.scenario],
            created_by=created_by,
            created_at=datetime.now(),
            variants=variants
        )
        
        # 保存到数据库
        db = SessionLocal()
        try:
            db_script = SalesScriptModel(
                id=script_id,
                title=script.title,
                script=script.script,
                scenario=script.scenario,
                customer_type=script.customer_type,
                tags=script.tags,
                created_by=script.created_by,
                created_at=script.created_at,
                success_rate=script.success_rate,
                usage_count=script.usage_count,
                variants=script.variants
            )
            db.add(db_script)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"话术保存错误：{e}", exc_info=True)
        finally:
            db.close()
        
        # 更新内存缓存
        self.scripts[script_id] = script
        
        return script
    
    def _generate_from_scratch(self, request: ScriptGenerationRequest, content: List) -> str:
        """從頭生成話術 - 使用LLM"""
        # 構建參考內容
        best_practices = ""
        if content:
            best_practices = "\n".join([f"- {c.title}: {c.content[:200]}" for c in content[:3]])
        
        # 使用LLM生成
        script = llm_service.generate_script(
            scenario=request.scenario,
            customer_type=request.customer_type,
            requirements=request.requirements
        )
        
        if best_practices:
            script += f"\n\n參考最佳實踐：\n{best_practices}"
        
        return script
    
    def _optimize_script(self, base_script: str, request: ScriptGenerationRequest) -> str:
        """优化现有话术 - 使用LLM"""
        try:
            # 構建優化提示
            prompt = f"""你是一個專業的銷售話術優化專家。請優化以下話術，使其更有效、更專業。

原始話術：
{base_script}

優化要求：
- 場景：{request.scenario}
- 客戶類型：{request.customer_type or '通用'}
- 特殊要求：{request.requirements or '無'}

請提供優化後的話術，保持原有結構但提升表達效果。

**重要：請務必使用繁體中文生成，不要使用簡體中文。**"""
            
            optimized = llm_service.generate_response(
                system_prompt="你是一個銷售話術優化專家，擅長將普通話術優化為更專業、更有效的版本。請使用繁體中文回答。",
                user_message=prompt,
                context=None
            )
            
            return optimized
        except Exception as e:
            logger.error(f"话术优化错误：{e}", exc_info=True)
            # 回退到简单优化
            return f"{base_script}\n\n优化建议：\n- 增加更多情感连接\n- 强化价值主张\n- 简化表达方式"
    
    def _generate_variants(self, script: str) -> List[str]:
        """生成话术变体 - 使用LLM生成多个版本"""
        variants = []
        styles = [
            ("正式版本", "使用正式、专业的语言风格"),
            ("友好版本", "使用友好、亲切的语言风格"),
            ("简洁版本", "使用简洁、直接的语言风格")
        ]
        
        try:
            for style_name, style_desc in styles:
                # 繁體中文風格名稱
                style_names_tw = {
                    "正式版本": "正式版本",
                    "友好版本": "友好版本",
                    "简洁版本": "簡潔版本"
                }
                style_name_tw = style_names_tw.get(style_name, style_name)
                
                prompt = f"""請將以下銷售話術改寫為{style_name_tw}（{style_desc}），保持核心內容和結構不變，只改變表達風格。

原始話術：
{script}

請生成{style_name_tw}。

**重要：請務必使用繁體中文生成，不要使用簡體中文。**"""
                
                variant = llm_service.generate_response(
                    system_prompt=f"你是一個銷售話術改寫專家，擅長將話術改寫為不同的語言風格。請使用繁體中文回答。",
                    user_message=prompt,
                    context=None
                )
                
                variants.append(variant)
        except Exception as e:
            logger.error(f"生成话术变体错误：{e}", exc_info=True)
            # 回退到简单版本
            variants = [
                f"变体1（正式版）：{script[:100]}...",
                f"变体2（友好版）：{script[:100]}...",
                f"变体3（简洁版）：{script[:100]}..."
            ]
        
        return variants[:3]  # 最多返回3个变体
    
    def get_script(self, script_id: str) -> Optional[SalesScript]:
        """获取话术 - 优先从缓存，否则从数据库"""
        # 先从缓存查找
        if script_id in self.scripts:
            return self.scripts[script_id]
        
        # 从数据库加载
        db = SessionLocal()
        try:
            db_script = db.query(SalesScriptModel).filter(
                SalesScriptModel.id == script_id
            ).first()
            
            if db_script:
                script = SalesScript(
                    id=db_script.id,
                    title=db_script.title,
                    script=db_script.script,
                    scenario=db_script.scenario,
                    customer_type=db_script.customer_type,
                    tags=db_script.tags or [],
                    created_by=db_script.created_by,
                    created_at=db_script.created_at,
                    success_rate=db_script.success_rate or 0.0,
                    usage_count=db_script.usage_count or 0,
                    variants=db_script.variants or []
                )
                # 更新缓存
                self.scripts[script_id] = script
                return script
        finally:
            db.close()
        
        return None
    
    def update_success_rate(self, script_id: str, success: bool):
        """更新话术成功率 - 同时更新数据库和缓存"""
        # 从数据库加载或获取
        script = self.get_script(script_id)
        if not script:
            return
        
        # 更新使用次数和成功率
        script.usage_count += 1
        if success:
            script.success_rate = (script.success_rate * (script.usage_count - 1) + 1) / script.usage_count
        else:
            script.success_rate = (script.success_rate * (script.usage_count - 1)) / script.usage_count
        
        # 更新数据库
        db = SessionLocal()
        try:
            db_script = db.query(SalesScriptModel).filter(
                SalesScriptModel.id == script_id
            ).first()
            
            if db_script:
                db_script.usage_count = script.usage_count
                db_script.success_rate = script.success_rate
                db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"更新话术成功率错误：{e}", exc_info=True)
        finally:
            db.close()
        
        # 更新缓存
        self.scripts[script_id] = script

# 全局话术生成器实例
script_generator = ScriptGenerator()

