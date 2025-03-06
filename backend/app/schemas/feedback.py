from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

from .activity import Location


class CompletionStatus(str, Enum):
    completed = "completed"
    partial = "partial"
    abandoned = "abandoned"


class FeedbackBase(BaseModel):
    activity_id: int
    rating: int = Field(..., ge=1, le=10)
    fatigue_level: int = Field(..., ge=1, le=10)
    location: Location
    duration: int = Field(..., ge=15, le=60)
    completion_status: CompletionStatus
    comments: Optional[str] = None


class FeedbackCreate(FeedbackBase):
    pass


class Feedback(FeedbackBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackSummary(BaseModel):
    average_rating: float
    total_feedbacks: int
    completion_rate: float  # 完全完了率
    favorite_location: Location
    common_fatigue_level: int  # 最も頻繁に記録された疲労度


class FeedbackWithActivity(Feedback):
    activity_title: str
    activity_category: str
