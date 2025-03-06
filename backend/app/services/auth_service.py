"""
Supabase認証サービス
JWTベースの認証を置き換える形でSupabaseの認証機能を利用します
"""
import logging
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from supabase import Client
from ..database_supabase import get_supabase

logger = logging.getLogger(__name__)

async def signup_user(email: str, password: str, name: str, supabase: Client = Depends(get_supabase)) -> Dict[str, Any]:
    """
    Supabaseを使用してユーザーを登録
    """
    try:
        # Supabaseでユーザー登録
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })
        
        # ユーザー登録に成功した場合、追加情報をプロフィールテーブルに保存
        if response.user and response.user.id:
            user_id = response.user.id
            
            # プロフィールテーブルにデータを挿入
            supabase.table("profiles").insert({
                "id": user_id,
                "name": name,
                "created_at": "now()",
                "updated_at": "now()"
            }).execute()
            
            return {
                "user_id": user_id,
                "email": email,
                "name": name,
                "access_token": response.session.access_token if response.session else None,
                "refresh_token": response.session.refresh_token if response.session else None
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ユーザー登録に失敗しました"
            )
            
    except Exception as e:
        logger.error(f"User signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ユーザー登録エラー: {str(e)}"
        )

async def login_user(email: str, password: str, supabase: Client = Depends(get_supabase)) -> Dict[str, Any]:
    """
    Supabaseを使用してユーザーログイン
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user and response.session:
            return {
                "user_id": response.user.id,
                "email": response.user.email,
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="メールアドレスまたはパスワードが正しくありません"
            )
            
    except Exception as e:
        logger.error(f"User login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ログインに失敗しました"
        )

async def validate_token(token: str, supabase: Client = Depends(get_supabase)) -> Optional[Dict[str, Any]]:
    """
    アクセストークンを検証してユーザー情報を取得
    """
    try:
        # アクセストークンを検証
        response = supabase.auth.get_user(token)
        
        if response and response.user:
            return {
                "user_id": response.user.id,
                "email": response.user.email
            }
        
        return None
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return None

async def logout_user(token: str, supabase: Client = Depends(get_supabase)) -> bool:
    """
    ユーザーをログアウト
    """
    try:
        # セッションを無効化
        supabase.auth.sign_out(token)
        return True
    except Exception as e:
        logger.error(f"User logout error: {str(e)}")
        return False
