from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from pydantic import ValidationError

from ..database import SessionLocal
from ..config import settings
from ..schemas.user import TokenData
from ..models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_db() -> Generator:
    """データベースセッションを取得するための依存関数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    JWTトークンからユーザーを取得する依存関数
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効です",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

def get_current_user_id(
    current_user: User = Depends(get_current_user)
) -> int:
    """現在のユーザーIDを取得する依存関数"""
    return current_user.id

def get_optional_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Optional[User]:
    """
    JWTトークンからユーザーを取得するが、認証に失敗しても例外を発生させない
    """
    try:
        return get_current_user(db, token)
    except HTTPException:
        return None
