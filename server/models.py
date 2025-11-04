from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# 用户角色
class UserRole(str, Enum):
    TRAINER = "trainer"  # 培训师
    SALES = "sales"      # 业务员
    ADMIN = "admin"      # 管理员

# 内容类型
class ContentType(str, Enum):
    TRAINING_MATERIAL = "training_material"  # 培训材料
    SALES_SCRIPT = "sales_script"           # 销售话术
    Q_A = "qa"                               # 问答对
    BEST_PRACTICE = "best_practice"         # 最佳实践

# 对话记录
class ConversationMessage(BaseModel):
    role: str  # "user" 或 "assistant"
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class Conversation(BaseModel):
    id: Optional[str] = None
    sales_id: str
    customer_type: Optional[str] = None
    scenario: Optional[str] = None
    messages: List[ConversationMessage]
    feedback_score: Optional[float] = None  # 1-5分
    created_at: datetime
    learning_insights: Optional[Dict[str, Any]] = None

# 培训内容
class TrainingContent(BaseModel):
    id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    content: str = Field(..., min_length=1, max_length=10000, description="内容")
    content_type: ContentType
    tags: List[str] = Field(default_factory=list, max_items=20, description="标签列表")
    created_by: str = Field(..., min_length=1, max_length=100, description="创建者ID")
    created_at: datetime
    usage_count: int = Field(default=0, ge=0, description="使用次数")
    effectiveness_score: Optional[float] = Field(None, ge=0, le=5, description="效果评分")
    
    @validator('title', 'content', 'created_by')
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('字段不能为空')
        return v.strip()

# 话术
class SalesScript(BaseModel):
    id: Optional[str] = None
    title: str
    script: str
    scenario: str  # 使用场景
    customer_type: Optional[str] = None
    tags: List[str] = []
    created_by: str
    created_at: datetime
    success_rate: float = 0.0  # 成功率
    usage_count: int = 0
    variants: List[str] = []  # 话术变体

# 语音分析
class VoiceAnalysis(BaseModel):
    id: Optional[str] = None
    conversation_id: str
    audio_url: str
    transcription: str
    sentiment: Optional[str] = None  # positive, neutral, negative
    emotion: Optional[Dict[str, float]] = None
    speaking_rate: Optional[float] = None
    pause_patterns: Optional[List[float]] = None
    key_phrases: List[str] = []

# 学习洞察
class LearningInsight(BaseModel):
    id: Optional[str] = None
    sales_id: Optional[str] = None
    insight_type: str  # "improvement", "strength", "pattern"
    content: str
    confidence: float
    related_conversations: List[str] = []
    created_at: datetime

# API 请求/响应模型
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息内容")
    sales_id: str = Field(..., min_length=1, max_length=100, description="业务员ID")
    context: Optional[Dict[str, Any]] = None
    customer_type: Optional[str] = Field(None, max_length=50, description="客户类型")
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('消息不能为空')
        return v.strip()
    
    @validator('sales_id')
    def validate_sales_id(cls, v):
        if not v or not v.strip():
            raise ValueError('业务员ID不能为空')
        return v.strip()

class ChatResponse(BaseModel):
    response: str
    suggestions: List[str] = []
    related_scripts: List[str] = []
    confidence: float

# 分页响应模型
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

class ScriptGenerationRequest(BaseModel):
    scenario: str = Field(..., min_length=1, max_length=200, description="使用场景")
    customer_type: Optional[str] = Field(None, max_length=50, description="客户类型")
    requirements: Optional[str] = Field(None, max_length=1000, description="特殊要求")
    base_script_id: Optional[str] = Field(None, max_length=100, description="基础话术ID")
    
    @validator('scenario')
    def validate_scenario(cls, v):
        if not v or not v.strip():
            raise ValueError('场景不能为空')
        return v.strip()

# 认证相关模型
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")
    email: Optional[str] = Field(None, max_length=100, description="電子郵件")
    full_name: Optional[str] = Field(None, max_length=100, description="姓名")
    role: str = Field(default="sales", description="角色：sales, trainer, admin")
    
    @validator('username')
    def validate_username(cls, v):
        if not v or not v.strip():
            raise ValueError('用戶名不能為空')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用戶名只能包含字母、數字、下劃線和連字符')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if not v or not v.strip():
            raise ValueError('密碼不能為空')
        # 密码会在后端自动处理bcrypt限制，用户无需知道
        return v.strip()

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserInfo(BaseModel):
    id: str
    username: str
    email: Optional[str]
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

