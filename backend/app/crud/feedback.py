from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from ..models.feedback import Feedback
from ..models.activity import Activity
from ..schemas.feedback import FeedbackCreate

def create_feedback(db: Session, feedback: FeedbackCreate, user_id: int) -> Feedback:
    """
    フィードバックを作成
    """
    db_feedback = Feedback(
        user_id=user_id,
        activity_id=feedback.activity_id,
        rating=feedback.rating,
        fatigue_level=feedback.fatigue_level,
        location=feedback.location,
        duration=feedback.duration,
        completion_status=feedback.completion_status,
        comments=feedback.comments
    )
    
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    return db_feedback

def get_user_feedbacks(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[Feedback]:
    """
    ユーザーのフィードバックを取得
    """
    return db.query(Feedback).filter(
        Feedback.user_id == user_id
    ).order_by(
        desc(Feedback.created_at)
    ).offset(skip).limit(limit).all()

def get_activity_feedbacks(
    db: Session, activity_id: int, skip: int = 0, limit: int = 100
) -> List[Feedback]:
    """
    特定の活動に対するフィードバックを取得
    """
    return db.query(Feedback).filter(
        Feedback.activity_id == activity_id
    ).order_by(
        desc(Feedback.created_at)
    ).offset(skip).limit(limit).all()

def get_feedback(db: Session, feedback_id: int) -> Optional[Feedback]:
    """
    IDでフィードバックを取得
    """
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()

def get_user_feedback_summary(db: Session, user_id: int) -> Dict[str, Any]:
    """
    ユーザーのフィードバックサマリーを取得
    """
    # フィードバック数と平均評価の取得
    feedback_count_and_avg = db.query(
        func.count(Feedback.id).label("total"),
        func.avg(Feedback.rating).label("avg_rating")
    ).filter(
        Feedback.user_id == user_id
    ).first()
    
    # 完了率の計算
    completion_stats = db.query(
        Feedback.completion_status,
        func.count(Feedback.id).label("count")
    ).filter(
        Feedback.user_id == user_id
    ).group_by(
        Feedback.completion_status
    ).all()
    
    completion_data = {status: 0 for status in ["completed", "partial", "abandoned"]}
    total_feedbacks = 0
    
    for status, count in completion_stats:
        completion_data[status] = count
        total_feedbacks += count
    
    completion_rate = 0
    if total_feedbacks > 0:
        completion_rate = (completion_data["completed"] / total_feedbacks) * 100
    
    # 最もフィードバックの多いカテゴリー
    category_stats = db.query(
        Activity.category,
        func.count(Feedback.id).label("count")
    ).join(
        Activity, Feedback.activity_id == Activity.id
    ).filter(
        Feedback.user_id == user_id
    ).group_by(
        Activity.category
    ).order_by(
        desc("count")
    ).limit(1).first()
    
    most_used_category = category_stats[0] if category_stats else None
    
    # 評価傾向の計算（直近5つのフィードバックの評価平均と比較）
    recent_feedbacks = db.query(
        Feedback.rating
    ).filter(
        Feedback.user_id == user_id
    ).order_by(
        desc(Feedback.created_at)
    ).limit(5).all()
    
    older_feedbacks = db.query(
        Feedback.rating
    ).filter(
        Feedback.user_id == user_id
    ).order_by(
        desc(Feedback.created_at)
    ).offset(5).limit(5).all()
    
    recent_avg = sum([f.rating for f in recent_feedbacks]) / len(recent_feedbacks) if recent_feedbacks else 0
    older_avg = sum([f.rating for f in older_feedbacks]) / len(older_feedbacks) if older_feedbacks else 0
    
    improvement_trend = recent_avg - older_avg if older_feedbacks else 0
    
    return {
        "total_feedbacks": feedback_count_and_avg.total,
        "average_rating": round(feedback_count_and_avg.avg_rating, 1) if feedback_count_and_avg.avg_rating else 0,
        "completion_rate": round(completion_rate, 1),
        "most_used_category": most_used_category,
        "improvement_trend": round(improvement_trend, 1)
    }

def get_user_activity_preferences(db: Session, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    ユーザーが好む活動タイプを取得
    """
    # 高評価（7以上）の活動カテゴリーを取得
    high_rated_categories = db.query(
        Activity.category,
        func.avg(Feedback.rating).label("avg_rating"),
        func.count(Feedback.id).label("count")
    ).join(
        Activity, Feedback.activity_id == Activity.id
    ).filter(
        and_(
            Feedback.user_id == user_id,
            Feedback.rating >= 7
        )
    ).group_by(
        Activity.category
    ).order_by(
        desc("avg_rating"), 
        desc("count")
    ).limit(limit).all()
    
    return [
        {
            "category": category,
            "average_rating": float(avg_rating),
            "count": count
        }
        for category, avg_rating, count in high_rated_categories
    ]
