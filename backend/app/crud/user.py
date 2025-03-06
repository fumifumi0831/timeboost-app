from typing import Optional, List
from sqlalchemy.orm import Session
import json
from passlib.context import CryptContext

from ..models.user import User, UserProfile
from ..schemas.user import UserCreate, UserProfileCreate, UserProfileUpdate

# パスワードハッシュのためのパスワードコンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    IDでユーザーを取得
    """
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    メールアドレスでユーザーを取得
    """
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    全ユーザーを取得
    """
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    """
    新しいユーザーを作成
    """
    # パスワードをハッシュ化
    hashed_password = pwd_context.hash(user.password)
    
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        name=user.name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    パスワードを検証
    """
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    ユーザーを認証
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    
    return user

def get_user_profile(db: Session, user_id: int) -> Optional[UserProfile]:
    """
    ユーザープロファイルを取得
    """
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

def create_user_profile(db: Session, profile: UserProfileCreate, user_id: int) -> UserProfile:
    """
    ユーザープロファイルを作成
    """
    db_profile = UserProfile(
        user_id=user_id,
        interests=json.dumps(profile.interests),
        work_style=profile.work_style,
        rest_preferences=json.dumps(profile.rest_preferences)
    )
    
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return db_profile

def update_user_profile(
    db: Session, db_profile: UserProfile, profile_update: UserProfileUpdate
) -> UserProfile:
    """
    ユーザープロファイルを更新
    """
    # 更新するデータを準備
    update_data = profile_update.dict(exclude_unset=True)
    
    # JSON文字列に変換が必要なフィールドの処理
    if "interests" in update_data:
        update_data["interests"] = json.dumps(update_data["interests"])
    
    if "rest_preferences" in update_data:
        update_data["rest_preferences"] = json.dumps(update_data["rest_preferences"])
    
    # モデルの更新
    for key, value in update_data.items():
        setattr(db_profile, key, value)
    
    db.commit()
    db.refresh(db_profile)
    
    return db_profile

def update_user_profile_text(
    db: Session, db_profile: UserProfile, textual_profile: str
) -> UserProfile:
    """
    AI生成されたテキストプロファイルを更新
    """
    db_profile.textual_profile = textual_profile
    
    db.commit()
    db.refresh(db_profile)
    
    return db_profile
