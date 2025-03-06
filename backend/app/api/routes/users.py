from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import logging

from ...database import get_db
from ...models.user import User, UserProfile
from ...schemas.user import User as UserSchema
from ...schemas.user import UserCreate, UserProfileCreate, UserProfileUpdate, UserProfile as UserProfileSchema
from ...crud import user as crud_user
from ...api.deps import get_current_user, get_current_user_id
from ...services import ai_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(get_current_user)
):
    """
    現在のログインユーザー情報を取得
    """
    return current_user

@router.get("/profile", response_model=UserProfileSchema)
async def read_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    現在のログインユーザーのプロファイルを取得
    """
    profile = crud_user.get_user_profile(db, current_user.id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="プロファイルが見つかりません")
    
    # JSONフィールドのパース
    profile.interests = json.loads(profile.interests) if profile.interests else []
    profile.rest_preferences = json.loads(profile.rest_preferences) if profile.rest_preferences else []
    
    return profile

@router.post("/profile", response_model=UserProfileSchema)
async def create_or_update_profile(
    profile: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ユーザープロファイルを作成または更新
    """
    # 既存のプロファイルを確認
    existing_profile = crud_user.get_user_profile(db, current_user.id)
    
    if existing_profile:
        # プロファイルの更新
        updated_profile = crud_user.update_user_profile(db, existing_profile, profile)
        
        # Gemini 2.0 Flashを使用してAIプロファイルを生成
        try:
            preferences = {
                "interests": profile.interests,
                "work_style": profile.work_style,
                "rest_preferences": profile.rest_preferences
            }
            
            textual_profile = await ai_service.generate_textual_profile(preferences)
            
            # 生成されたテキストプロファイルを保存
            updated_profile = crud_user.update_user_profile_text(db, updated_profile, textual_profile)
        except Exception as e:
            logger.error(f"AIプロファイル生成中にエラーが発生しました: {str(e)}")
            # AIプロファイル生成に失敗しても処理は続行
        
        # JSONフィールドのパース
        updated_profile.interests = json.loads(updated_profile.interests) if updated_profile.interests else []
        updated_profile.rest_preferences = json.loads(updated_profile.rest_preferences) if updated_profile.rest_preferences else []
        
        return updated_profile
    else:
        # 新しいプロファイルの作成
        new_profile = UserProfileCreate(
            interests=profile.interests,
            work_style=profile.work_style,
            rest_preferences=profile.rest_preferences
        )
        
        created_profile = crud_user.create_user_profile(db, new_profile, current_user.id)
        
        # Gemini 2.0 Flashを使用してAIプロファイルを生成
        try:
            preferences = {
                "interests": profile.interests,
                "work_style": profile.work_style,
                "rest_preferences": profile.rest_preferences
            }
            
            textual_profile = await ai_service.generate_textual_profile(preferences)
            
            # 生成されたテキストプロファイルを保存
            created_profile = crud_user.update_user_profile_text(db, created_profile, textual_profile)
        except Exception as e:
            logger.error(f"AIプロファイル生成中にエラーが発生しました: {str(e)}")
            # AIプロファイル生成に失敗しても処理は続行
        
        # JSONフィールドのパース
        created_profile.interests = json.loads(created_profile.interests) if created_profile.interests else []
        created_profile.rest_preferences = json.loads(created_profile.rest_preferences) if created_profile.rest_preferences else []
        
        return created_profile

@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    指定されたIDのユーザー情報を取得
    """
    # 管理者権限チェックなどが必要な場合はここに追加
    
    db_user = crud_user.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    
    return db_user
