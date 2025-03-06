"""
Supabase認証を使用するためのAPIエンドポイント
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ...schemas.user import UserCreate, Token
from ...services.auth_service import signup_user, login_user, logout_user

router = APIRouter()
security = HTTPBearer()

@router.post("/signup", response_model=Dict[str, Any])
async def signup(user_in: UserCreate) -> Any:
    """
    新規ユーザー登録
    """
    user_data = await signup_user(
        email=user_in.email,
        password=user_in.password,
        name=user_in.name
    )
    
    return {
        "access_token": user_data.get("access_token"),
        "token_type": "bearer",
        "user": {
            "id": user_data.get("user_id"),
            "email": user_data.get("email"),
            "name": user_data.get("name")
        }
    }

@router.post("/login", response_model=Dict[str, Any]) 
async def login(email: str, password: str) -> Any:
    """
    ユーザーログイン
    """
    user_data = await login_user(email=email, password=password)
    
    return {
        "access_token": user_data.get("access_token"),
        "token_type": "bearer",
        "user": {
            "id": user_data.get("user_id"),
            "email": user_data.get("email")
        }
    }

@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    ユーザーログアウト
    """
    token = credentials.credentials
    success = await logout_user(token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ログアウトに失敗しました"
        )
    
    return {"message": "ログアウトしました"}
