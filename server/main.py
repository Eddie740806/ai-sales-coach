from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from .database import get_db
import os
try:
    from .rate_limit import limiter, RATE_LIMITS
    from slowapi.errors import RateLimitExceeded
    from slowapi import _rate_limit_exceeded_handler
    RATE_LIMITING_ENABLED = True
except ImportError:
    # 如果slowapi未安装，使用模拟装饰器
    RATE_LIMITING_ENABLED = False
    limiter = None
    RATE_LIMITS = {}
    
    def rate_limit_decorator(limit: str):
        def decorator(func):
            return func
        return decorator
    
    class RateLimitExceeded(Exception):
        pass
    
    def _rate_limit_exceeded_handler(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )

from .models import (
    ChatRequest, ChatResponse, 
    TrainingContent, ContentType,
    Conversation, ConversationMessage,
    ScriptGenerationRequest, SalesScript,
    VoiceAnalysis,
    PaginatedResponse,
    RegisterRequest, LoginRequest, TokenResponse, UserInfo
)
from .knowledge_base import knowledge_base
from .conversation_engine import conversation_engine
from .learning_system import learning_system
from .voice_processor import voice_processor
from .script_generator import script_generator
from .logger import logger
from .auth import (
    authenticate_user, create_user, create_access_token,
    verify_token, get_user_by_id
)
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI(title="AI Sales Coach Platform", version="1.0.0")

# 静态文件服务
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    # 静态资源（CSS, JS, 图片等）
    static_dir = frontend_path
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/")
    def serve_frontend():
        """提供前端页面"""
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "前端文件未找到，请检查frontend目录"}

# 添加速率限制（如果可用）
if RATE_LIMITING_ENABLED and limiter:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 启动时初始化示例数据（如果数据库为空）
@app.on_event("startup")
async def startup_event():
    from .database import SessionLocal, TrainingContentModel
    db = SessionLocal()
    try:
        count = db.query(TrainingContentModel).count()
        if count == 0:
            from .logger import logger
            logger.info("检测到空数据库，正在初始化示例数据...")
            from .init_data import init_sample_data
            init_sample_data()
    finally:
        db.close()

# CORS配置 - 从环境变量读取或使用默认值
from .config import settings
import os

allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
if os.getenv("ENV") == "development":
    allowed_origins = ["*"]  # 开发环境允许所有来源

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ==================== API根路径 ====================
@app.get("/api")
def api_root():
    return {
        "message": "欢迎使用 AI Sales Coach Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "api_base": "/api"
    }

# ==================== 认证相关 ====================
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """获取当前登录用户"""
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效的認證令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效的認證令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用戶不存在或已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    """用戶註冊"""
    try:
        user = create_user(
            db=db,
            username=user_data.username,
            password=user_data.password,
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role
        )
        
        # 生成token
        access_token = create_access_token(data={"sub": user.id, "username": user.username, "role": user.role})
        
        return TokenResponse(
            access_token=access_token,
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"註冊錯誤：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"註冊失敗：{str(e)}")

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """用戶登入"""
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用戶名或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成token
    access_token = create_access_token(data={"sub": user.id, "username": user.username, "role": user.role})
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    )

@app.get("/api/auth/me", response_model=UserInfo)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """獲取當前用戶信息"""
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

# ==================== 健康检查 ====================
@app.get("/health")
def health():
    """
    健康检查端点
    
    返回服务器运行状态和版本信息
    """
    return {"ok": True, "data": "server ok", "version": "1.0.0"}

# ==================== 对话API ====================
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: Request, chat_request: ChatRequest, current_user = Depends(get_current_user)):
    """
    业务员与AI教练对话
    
    - **message**: 业务员的问题或消息
    - **sales_id**: 业务员唯一标识
    - **customer_type**: 客户类型（可选）
    
    返回AI教练的建议和推荐话术
    """
    try:
        # 使用当前登录用户的ID
        chat_request.sales_id = current_user.id
        response = conversation_engine.chat(chat_request)
        
        # 验证响应格式
        if not response or not hasattr(response, 'response') or not response.response:
            logger.error(f"对话引擎返回无效响应：{response}")
            raise HTTPException(status_code=500, detail="AI教練未能生成有效回應，請稍後再試")
        
        # 保存对话记录（会自动保存到数据库）
        # 使用当前登录用户的ID作为sales_id
        try:
            conversation = Conversation(
                sales_id=current_user.id,  # 使用登录用户的ID
                customer_type=chat_request.customer_type,
                messages=[
                    ConversationMessage(
                        role="user",
                        content=chat_request.message,
                        timestamp=datetime.now()
                    ),
                    ConversationMessage(
                        role="assistant",
                        content=response.response,
                        timestamp=datetime.now()
                    )
                ],
                created_at=datetime.now()
            )
            conversation_engine.save_conversation(current_user.id, conversation)
            
            # 分析对话，提取学习洞察（异步执行，不影响响应）
            try:
                learning_system.analyze_conversation(conversation)
            except Exception as learn_error:
                logger.error(f"学习系统分析失败：{learn_error}", exc_info=True)
                # 分析失败不影响响应返回
        except Exception as save_error:
            logger.error(f"保存对话失败：{save_error}", exc_info=True)
            # 即使保存失败也继续返回响应，保证用户体验
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"聊天API错误：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"處理請求時發生錯誤：{str(e)}")

@app.post("/api/conversations/{conversation_id}/feedback")
async def submit_feedback(conversation_id: str, score: float, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """提交对话反馈评分"""
    from .database import ConversationModel
    
    # 验证分数范围
    if score < 0 or score > 5:
        raise HTTPException(status_code=400, detail="评分必须在0-5之间")
    
    try:
        db_conversation = db.query(ConversationModel).filter(
            ConversationModel.id == conversation_id
        ).first()
        
        if not db_conversation:
            raise HTTPException(status_code=404, detail="對話不存在")
        
        # 验证对话属于当前用户（除非是管理员）
        if current_user.role != "admin" and db_conversation.sales_id != current_user.id:
            raise HTTPException(status_code=403, detail="無權限對此對話進行反饋")
        
        # 更新反馈分数
        db_conversation.feedback_score = score
        db.commit()
        
        # 触发学习系统分析
        from .models import Conversation, ConversationMessage
        messages = [
            ConversationMessage(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]) if isinstance(msg["timestamp"], str) else msg["timestamp"],
                metadata=msg.get("metadata")
            )
            for msg in db_conversation.messages
        ]
        
        conversation = Conversation(
            id=db_conversation.id,
            sales_id=db_conversation.sales_id,
            customer_type=db_conversation.customer_type,
            scenario=db_conversation.scenario,
            messages=messages,
            feedback_score=score,
            created_at=db_conversation.created_at,
            learning_insights=db_conversation.learning_insights
        )
        learning_system.analyze_conversation(conversation)
        
        return {"ok": True, "message": "反馈已记录", "conversation_id": conversation_id, "score": score}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新反馈失败：{str(e)}")

# ==================== 知识库API ====================
@app.post("/api/knowledge/content", response_model=TrainingContent)
async def add_training_content(request: Request, content: TrainingContent, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """培训师添加培训内容"""
    content.created_at = datetime.now()
    # 使用当前登录用户作为创建者
    content.created_by = current_user.id
    content_id = knowledge_base.add_content(content, db)
    content.id = content_id
    return content

@app.get("/api/knowledge/content", response_model=PaginatedResponse)
async def search_content(
    request: Request,
    query: str,
    content_type: ContentType = None,
    page: int = 1,
    page_size: int = 10,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """搜索培训内容（支持分页）"""
    # 验证分页参数
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10
    
    # 获取所有结果
    all_results = knowledge_base.search_content(query, content_type, db)
    total = len(all_results)
    
    # 计算分页
    start = (page - 1) * page_size
    end = start + page_size
    items = all_results[start:end]
    
    # 计算总页数
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@app.get("/api/knowledge/content/{content_id}", response_model=TrainingContent)
async def get_content(content_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取特定内容"""
    content = knowledge_base.get_content(content_id, db)
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")
    return content

# ==================== 话术生成API ====================
@app.post("/api/scripts/generate", response_model=SalesScript)
async def generate_script(request: Request, script_request: ScriptGenerationRequest, current_user = Depends(get_current_user)):
    """
    生成销售话术
    
    - **scenario**: 使用场景（必需）
    - **customer_type**: 客户类型（可选）
    - **requirements**: 特殊要求（可选）
    - **base_script_id**: 基础话术ID（可选，用于优化现有话术）
    
    返回生成的销售话术和变体
    """
    script = script_generator.generate_script(script_request, created_by=current_user.id)
    return script

@app.get("/api/scripts", response_model=PaginatedResponse)
async def list_scripts(
    page: int = 1,
    page_size: int = 10,
    scenario: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取话术列表（支持分页）"""
    from .database import SalesScriptModel
    from typing import Optional
    
    # 验证分页参数
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10
    
    try:
        # 构建查询
        query = db.query(SalesScriptModel)
        if scenario:
            query = query.filter(SalesScriptModel.scenario == scenario)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        start = (page - 1) * page_size
        db_scripts = query.order_by(
            SalesScriptModel.success_rate.desc(),
            SalesScriptModel.usage_count.desc()
        ).offset(start).limit(page_size).all()
        
        # 转换为模型
        scripts = []
        for db_script in db_scripts:
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
            scripts.append(script)
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size
        
        return PaginatedResponse(
            items=scripts,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取话术列表失败：{str(e)}")

@app.get("/api/scripts/{script_id}", response_model=SalesScript)
async def get_script(script_id: str, current_user = Depends(get_current_user)):
    """获取话术"""
    script = script_generator.get_script(script_id)
    if not script:
        raise HTTPException(status_code=404, detail="话术不存在")
    return script

@app.post("/api/scripts/{script_id}/test")
async def test_script(script_id: str, success: bool, current_user = Depends(get_current_user)):
    """测试话术效果"""
    script_generator.update_success_rate(script_id, success)
    return {"ok": True, "message": "測試結果已記錄"}

# ==================== 学习系统API ====================
@app.get("/api/conversations")
async def list_conversations(
    sales_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取对话列表（支持分页）"""
    from .database import ConversationModel
    
    try:
        # 构建查询 - 只允许查看自己的对话，除非是管理员
        query = db.query(ConversationModel)
        if current_user.role != "admin":
            # 非管理员只能查看自己的对话
            query = query.filter(ConversationModel.sales_id == current_user.id)
        elif sales_id:
            # 管理员可以指定查看特定用户的对话
            query = query.filter(ConversationModel.sales_id == sales_id)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        start = (page - 1) * page_size
        db_conversations = query.order_by(
            ConversationModel.created_at.desc()
        ).offset(start).limit(page_size).all()
        
        # 转换为模型
        conversations = []
        for db_conv in db_conversations:
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
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size
        
        return PaginatedResponse(
            items=conversations,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话列表失败：{str(e)}")

@app.get("/api/learning/insights/{sales_id}")
async def get_insights(sales_id: str, current_user = Depends(get_current_user)):
    """获取业务员的学习洞察"""
    # 只允许查看自己的洞察，或管理员查看任何人的
    if current_user.role != "admin" and sales_id != current_user.id:
        raise HTTPException(status_code=403, detail="無權限查看其他用戶的學習洞察")
    
    training_suggestions = learning_system.generate_personalized_training(sales_id)
    return {
        "sales_id": sales_id,
        "suggestions": training_suggestions,
        "insights": learning_system.insights.get(sales_id, [])
    }

# ==================== 语音处理API ====================
@app.post("/api/voice/process")
async def process_audio(audio_url: str, conversation_id: str, current_user = Depends(get_current_user)):
    """处理录音档"""
    # 验证对话属于当前用户
    from .database import ConversationModel, SessionLocal
    db = SessionLocal()
    try:
        conversation = db.query(ConversationModel).filter(
            ConversationModel.id == conversation_id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="對話不存在")
        if current_user.role != "admin" and conversation.sales_id != current_user.id:
            raise HTTPException(status_code=403, detail="無權限處理此對話的錄音")
    finally:
        db.close()
    
    analysis = voice_processor.process_audio(audio_url, conversation_id)
    return analysis

# ==================== 数据分析API ====================
@app.get("/api/analytics/dashboard")
async def get_dashboard(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取数据分析仪表板 - 从数据库统计真实数据"""
    from .database import ConversationModel, TrainingContentModel, SalesScriptModel
    
    try:
        # 统计对话数
        total_conversations = db.query(ConversationModel).count()
        
        # 统计活跃业务员（有对话记录的唯一sales_id）
        active_sales = db.query(ConversationModel.sales_id).distinct().count()
        
        # 统计培训内容数
        total_content = db.query(TrainingContentModel).count()
        
        # 统计话术数
        total_scripts = db.query(SalesScriptModel).count()
        
        # 获取表现最好的话术（按成功率和使用次数）
        top_scripts = db.query(SalesScriptModel).order_by(
            SalesScriptModel.success_rate.desc(),
            SalesScriptModel.usage_count.desc()
        ).limit(5).all()
        
        top_performing_scripts = [
            {
                "id": script.id,
                "title": script.title,
                "success_rate": script.success_rate or 0.0,
                "usage_count": script.usage_count or 0
            }
            for script in top_scripts
        ]
        
        # 统计平均反馈分数
        avg_feedback = db.query(func.avg(ConversationModel.feedback_score)).filter(
            ConversationModel.feedback_score.isnot(None)
        ).scalar() or 0.0
        
        return {
            "total_conversations": total_conversations,
            "total_content": total_content,
            "total_scripts": total_scripts,
            "active_sales": active_sales,
            "average_feedback_score": round(float(avg_feedback), 2),
            "top_performing_scripts": top_performing_scripts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仪表板数据失败：{str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
