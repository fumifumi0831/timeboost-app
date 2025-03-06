from typing import List, Optional
from sqlalchemy.orm import Session
import json

from ..models.activity import Activity
from ..schemas.activity import ActivityCreate, ActivityUpdate, ActivityFilter

def get_activity(db: Session, activity_id: int) -> Optional[Activity]:
    """
    IDで活動を取得
    """
    return db.query(Activity).filter(Activity.id == activity_id).first()

def get_activities(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Activity]:
    """
    全活動を取得
    """
    return db.query(Activity).offset(skip).limit(limit).all()

def get_filtered_activities(
    db: Session, 
    fatigue_level: int,
    location: str,
    duration: int,
    category: Optional[str] = None,
    limit: int = 10
) -> List[Activity]:
    """
    フィルター条件に合致する活動を取得
    """
    query = db.query(Activity)
    
    # 疲労レベルのフィルタリング
    query = query.filter(
        Activity.fatigue_min <= fatigue_level,
        Activity.fatigue_max >= fatigue_level
    )
    
    # 時間のフィルタリング
    # 指定された時間以下の活動を取得（最大25%増しまで許容）
    max_duration = duration * 1.25
    query = query.filter(Activity.duration <= max_duration)
    
    # ロケーションのフィルタリング
    # JSONフィールドをフィルタリングするには、各レコードを取得して
    # Pythonでフィルタリングするか、データベースの拡張機能を使用する必要がある
    activities = query.all()
    filtered_activities = []
    
    for activity in activities:
        locations = json.loads(activity.locations)
        if location in locations:
            # カテゴリーフィルターが指定されている場合
            if category and activity.category != category:
                continue
            
            filtered_activities.append(activity)
    
    # 指定された上限数に制限
    return filtered_activities[:limit]

def create_activity(db: Session, activity: ActivityCreate) -> Activity:
    """
    新しい活動を作成
    """
    db_activity = Activity(
        title=activity.title,
        description=activity.description,
        category=activity.category,
        duration=activity.duration,
        locations=json.dumps([loc for loc in activity.locations]),
        fatigue_min=activity.fatigue_range.min,
        fatigue_max=activity.fatigue_range.max,
        steps=json.dumps(activity.steps) if activity.steps else None,
        benefits=json.dumps(activity.benefits) if activity.benefits else None,
        image_url=activity.image_url,
        scientific_basis=activity.scientific_basis
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def update_activity(
    db: Session, db_activity: Activity, activity_update: ActivityUpdate
) -> Activity:
    """
    活動を更新
    """
    update_data = activity_update.dict(exclude_unset=True)
    
    # 特殊なフィールドの処理
    if "fatigue_range" in update_data:
        update_data["fatigue_min"] = update_data["fatigue_range"].min
        update_data["fatigue_max"] = update_data["fatigue_range"].max
        del update_data["fatigue_range"]
    
    if "locations" in update_data:
        update_data["locations"] = json.dumps([loc for loc in update_data["locations"]])
    
    if "steps" in update_data and update_data["steps"] is not None:
        update_data["steps"] = json.dumps(update_data["steps"])
    
    if "benefits" in update_data and update_data["benefits"] is not None:
        update_data["benefits"] = json.dumps(update_data["benefits"])
    
    # モデルの更新
    for key, value in update_data.items():
        setattr(db_activity, key, value)
    
    db.commit()
    db.refresh(db_activity)
    return db_activity

def delete_activity(db: Session, db_activity: Activity) -> None:
    """
    活動を削除
    """
    db.delete(db_activity)
    db.commit()
