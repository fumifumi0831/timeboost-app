from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import json
import logging

from ...database import get_db
from ...models.user import User
from ...schemas.activity import Activity, ActivityCreate, ActivityUpdate, ActivityFilter
from ...crud import activity as crud_activity
from ...crud import feedback as crud_feedback
from ...api.deps import get_current_user, get_current_user_id, get_optional_current_user
from ...services import ai_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[Activity])
def read_activities(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    全ての活動を取得
    """
    activities = crud_activity.get_activities(db, skip=skip, limit=limit)
    
    # JSONフィールドをパースして返す
    for activity in activities:
        activity.locations = json.loads(activity.locations) 
        activity.steps = json.loads(activity.steps) if activity.steps else []
        activity.benefits = json.loads(activity.benefits) if activity.benefits else []
    
    return activities

@router.get("/recommended", response_model=List[Activity])
async def get_recommended_activities(
    fatigue_level: int = Query(..., ge=1, le=10),
    location: str = Query(...),
    duration: int = Query(..., ge=15, le=60),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    ユーザーの状態に応じて推奨活動を取得
    ログインしていればパーソナライズされた結果を返す
    """
    # 基本的なフィルタリング
    activities = crud_activity.get_filtered_activities(
        db, fatigue_level=fatigue_level, location=location, duration=duration
    )
    
    # JSONフィールドのパース
    for activity in activities:
        activity.locations = json.loads(activity.locations)
        activity.steps = json.loads(activity.steps) if activity.steps else []
        activity.benefits = json.loads(activity.benefits) if activity.benefits else []
    
    # ログインしていない場合は基本的なフィルタリング結果を返す
    if not current_user:
        return activities
    
    try:
        # ユーザープロファイルに基づいてパーソナライズ
        from ...crud.user import get_user_profile
        profile = get_user_profile(db, current_user.id)
        
        if not profile or not profile.textual_profile:
            return activities
        
        # 過去のフィードバックを取得
        feedbacks = crud_feedback.get_user_feedbacks(db, current_user.id, limit=10)
        feedback_data = []
        
        for fb in feedbacks:
            activity_data = db.query(crud_activity.Activity).filter_by(id=fb.activity_id).first()
            if activity_data:
                feedback_data.append({
                    "activity_id": fb.activity_id,
                    "activity_title": activity_data.title,
                    "activity_category": activity_data.category,
                    "rating": fb.rating,
                    "fatigue_level": fb.fatigue_level,
                    "completion_status": fb.completion_status
                })
        
        # Gemini 2.0 Flashを使用してパーソナライズ
        preferred_categories = await ai_service.personalize_activities(
            profile.textual_profile, fatigue_level, feedback_data
        )
        
        # 推奨カテゴリに応じてアクティビティを並べ替え
        def get_category_priority(activity):
            try:
                category = activity.category
                if category in preferred_categories:
                    return preferred_categories.index(category)
                return len(preferred_categories)
            except:
                return len(preferred_categories) + 1
        
        activities.sort(key=get_category_priority)
        
    except Exception as e:
        logger.error(f"パーソナライズ中にエラーが発生しました: {str(e)}")
        # エラーが発生しても基本的な結果を返す
    
    return activities

@router.post("/", response_model=Activity)
def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    新しい活動を作成
    """
    # 管理者権限チェックなどが必要な場合はここに追加
    
    db_activity = crud_activity.create_activity(db, activity)
    
    # JSONフィールドのパース
    db_activity.locations = json.loads(db_activity.locations)
    db_activity.steps = json.loads(db_activity.steps) if db_activity.steps else []
    db_activity.benefits = json.loads(db_activity.benefits) if db_activity.benefits else []
    
    return db_activity

@router.get("/{activity_id}", response_model=Activity)
def read_activity(
    activity_id: int,
    db: Session = Depends(get_db)
):
    """
    指定されたIDの活動を取得
    """
    db_activity = crud_activity.get_activity(db, activity_id)
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # JSONフィールドのパース
    db_activity.locations = json.loads(db_activity.locations)
    db_activity.steps = json.loads(db_activity.steps) if db_activity.steps else []
    db_activity.benefits = json.loads(db_activity.benefits) if db_activity.benefits else []
    
    return db_activity

@router.put("/{activity_id}", response_model=Activity)
def update_activity(
    activity_id: int,
    activity: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    指定されたIDの活動を更新
    """
    # 管理者権限チェックなどが必要な場合はここに追加
    
    db_activity = crud_activity.get_activity(db, activity_id)
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    db_activity = crud_activity.update_activity(db, db_activity, activity)
    
    # JSONフィールドのパース
    db_activity.locations = json.loads(db_activity.locations)
    db_activity.steps = json.loads(db_activity.steps) if db_activity.steps else []
    db_activity.benefits = json.loads(db_activity.benefits) if db_activity.benefits else []
    
    return db_activity

@router.delete("/{activity_id}")
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    指定されたIDの活動を削除
    """
    # 管理者権限チェックなどが必要な場合はここに追加
    
    db_activity = crud_activity.get_activity(db, activity_id)
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    crud_activity.delete_activity(db, db_activity)
    
    return {"ok": True}
