"""
Supabase認証を使用するための依存関係関数
"""
from typing import Generator, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from supabase import Client

from ..database_supabase import get_db, get_supabase
from ..services.auth_service import validate_token

# HTTPベアラートークン認証スキーム
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
) -> Dict[str, Any]:
    """
    Supabase認証トークンからユーザー情報を取得
    """
    token = credentials.credentials
    user_data = await validate_token(token, supabase)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証情報が無効です",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data

async def get_current_user_id(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> str:
    """
    現在のユーザーIDを取得
    """
    return current_user["user_id"]

async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    supabase: Client = Depends(get_supabase)
) -> Optional[Dict[str, Any]]:
    """
    トークンが提供された場合はユーザー情報を取得、なければNoneを返す
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_data = await validate_token(token, supabase)
        return user_data
    except Exception:
        return None

# SQLAlchemy DBセッションの依存関係はそのまま使用
get_supabase_db = get_db
