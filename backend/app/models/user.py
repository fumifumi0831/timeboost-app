from sqlalchemy import Column, Integer, String, DateTime, func, JSON
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    interests = Column(String)  # JSON文字列で格納
    work_style = Column(String, nullable=False)
    rest_preferences = Column(String)  # JSON文字列で格納
    textual_profile = Column(String)  # AI生成された文章形式のプロファイル
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
