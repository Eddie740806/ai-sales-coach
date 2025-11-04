"""
用户认证模块
处理用户注册、登录、JWT token生成和验证
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .database import UserModel, SessionLocal
from .logger import logger
from .config import settings
import secrets

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = getattr(settings, 'secret_key', None) or secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30天

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    import bcrypt
    
    # 处理超长密码：截断到72字节
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        # 确保UTF-8字符完整性
        while len(password_bytes) > 0 and password_bytes[-1] & 0xC0 == 0x80:
            password_bytes = password_bytes[:-1]
    
    # 使用bcrypt验证
    try:
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception:
        # 如果直接验证失败，尝试使用passlib（兼容旧格式）
        return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """加密密码"""
    # bcrypt限制密码长度为72字节，自动截断以保持用户体验友好
    # 直接使用bcrypt而不是通过passlib，确保截断逻辑生效
    import bcrypt
    
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # 截断到72字节，确保不会破坏UTF-8字符
        password_bytes = password_bytes[:72]
        # 如果截断破坏了UTF-8字符，向后查找最后一个完整字符
        while len(password_bytes) > 0 and password_bytes[-1] & 0xC0 == 0x80:
            password_bytes = password_bytes[:-1]
    
    # 直接使用bcrypt进行哈希
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # 返回字符串格式（passlib格式兼容）
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """验证JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_user_by_username(db: Session, username: str) -> Optional[UserModel]:
    """根据用户名获取用户"""
    return db.query(UserModel).filter(UserModel.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
    """根据邮箱获取用户"""
    return db.query(UserModel).filter(UserModel.email == email).first()

def get_user_by_id(db: Session, user_id: str) -> Optional[UserModel]:
    """根据ID获取用户"""
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def create_user(
    db: Session,
    username: str,
    password: str,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    role: str = "sales"
) -> UserModel:
    """创建新用户"""
    # 检查用户名是否已存在
    if get_user_by_username(db, username):
        raise ValueError("用戶名已存在")
    
    # 检查邮箱是否已存在
    if email and get_user_by_email(db, email):
        raise ValueError("電子郵件已存在")
    
    # 密码长度会在get_password_hash中自动处理，无需在这里验证
    # 生成用户ID
    user_id = f"user_{secrets.token_urlsafe(8)}"
    
    # 创建用户
    user = UserModel(
        id=user_id,
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        full_name=full_name or username,
        role=role,
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"新用戶註冊：{username} (ID: {user_id})")
    return user

def authenticate_user(db: Session, username: str, password: str) -> Optional[UserModel]:
    """验证用户登录"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    if not user.is_active:
        return None
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.commit()
    
    logger.info(f"用戶登入：{username}")
    return user

