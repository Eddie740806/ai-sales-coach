"""
数据库 - SQLAlchemy ORM
"""
from sqlalchemy import create_engine, Column, String, Text, Integer, Float, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .config import settings

Base = declarative_base()

# 数据库模型
class ConversationModel(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True)
    sales_id = Column(String, index=True)
    customer_type = Column(String)
    scenario = Column(String)
    messages = Column(JSON)
    feedback_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    learning_insights = Column(JSON)

class TrainingContentModel(Base):
    __tablename__ = "training_contents"
    
    id = Column(String, primary_key=True)
    title = Column(String)
    content = Column(Text)
    content_type = Column(String)
    tags = Column(JSON)
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    usage_count = Column(Integer, default=0)
    effectiveness_score = Column(Float)

class SalesScriptModel(Base):
    __tablename__ = "sales_scripts"
    
    id = Column(String, primary_key=True)
    title = Column(String)
    script = Column(Text)
    scenario = Column(String)
    customer_type = Column(String)
    tags = Column(JSON)
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    success_rate = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    variants = Column(JSON)

class LearningInsightModel(Base):
    __tablename__ = "learning_insights"
    
    id = Column(String, primary_key=True)
    sales_id = Column(String, index=True)
    insight_type = Column(String)
    content = Column(Text)
    confidence = Column(Float)
    related_conversations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="sales")  # sales, trainer, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

# 数据库连接配置
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 最大溢出连接数
    pool_pre_ping=True,  # 连接前ping，自动重连
    echo=False  # 是否打印SQL（生产环境设为False）
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建所有表
Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库会话 - FastAPI依赖注入"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

