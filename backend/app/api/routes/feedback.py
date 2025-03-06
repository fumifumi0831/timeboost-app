from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.user import User
from ...schemas.feedback import Feedback, FeedbackCreate, FeedbackSummary, FeedbackWithActivity
from ...crud import feedback as crud_feedback
from ...api.deps import get_current_user, get_current_user_id

router = APIRouter()

@router.post("/", response_model=Feedback)
def create_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    フィードバックを作成
    """
    return crud_feedback.create_feedback(db, feedback, current_user_id)

@router.get("/me", response_model=List[Feedback])
def read_user_feedbacks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    現在のユーザーのフィードバックを取得
    """
    feedbacks = crud_feedback.get_user_feedbacks(db, current_user_id, skip=skip, limit=limit)
    return feedbacks

@router.get("/activity/{activity_id}", response_model=List[Feedback])
def read_activity_feedbacks(
    activity_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    指定された活動のフィードバックを取得
    """
    # 管理者権限チェックなどが必要な場合はここに追加
    
    feedbacks = crud_feedback.get_activity_feedbacks(db, activity_id, skip=skip, limit=limit)
    return feedbacks

@router.get("/summary", response_model=Dict[str, Any])
def get_user_feedback_summary(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    ユーザーのフィードバックサマリーを取得
    """
    summary = crud_feedback.get_user_feedback_summary(db, current_user_id)
    
    # カテゴリの割合を計算（もし必要なら）
    if summary["most_used_category"]:
        # 簡単のため、とりあえず仮の割合を設定
        summary["most_used_category_percentage"] = 40
    
    return {
        "summary": summary
    }

@router.get("/preferences", response_model=List[Dict[str, Any]])
def get_user_activity_preferences(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    ユーザーが好む活動タイプを取得
    """
    preferences = crud_feedback.get_user_activity_preferences(db, current_user_id)
    return preferences

@router.get("/{feedback_id}", response_model=Feedback)
def read_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    指定されたIDのフィードバックを取得
    """
    feedback = crud_feedback.get_feedback(db, feedback_id)
    if feedback is None:
        raise HTTPException(status_code=404, detail="フィードバックが見つかりません")
    
    # 自分のフィードバックか、管理者のみアクセス可能
    if feedback.user_id != current_user.id:
        # 管理者権限チェックなどが必要な場合はここに追加
        raise HTTPException(status_code=403, detail="アクセス権限がありません")
    
    return feedback
