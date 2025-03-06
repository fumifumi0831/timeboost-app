from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ActivityCategory(str, Enum):
    relaxation = "relaxation"
    light_exercise = "light_exercise"
    desk_work = "desk_work"
    short_focus = "short_focus"
    location_specific = "location_specific"


class Location(str, Enum):
    home = "home"
    office = "office"
    cafe = "cafe"
    commuting = "commuting"
    other = "other"


class FatigueRange(BaseModel):
    min: int = Field(..., ge=1, le=10)
    max: int = Field(..., ge=1, le=10)


class ActivityBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10)
    category: ActivityCategory
    duration: int = Field(..., description="活動時間（分）", ge=5, le=120)
    locations: List[Location]
    fatigue_range: FatigueRange
    steps: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    image_url: Optional[str] = None
    scientific_basis: Optional[str] = None


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(ActivityBase):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[ActivityCategory] = None
    duration: Optional[int] = Field(None, description="活動時間（分）", ge=5, le=120)
    locations: Optional[List[Location]] = None
    fatigue_range: Optional[FatigueRange] = None


class Activity(ActivityBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActivityFilter(BaseModel):
    fatigue_level: int = Field(..., ge=1, le=10)
    location: Location
    duration: int = Field(..., ge=15, le=60)


class ActivityRecommendation(BaseModel):
    activities: List[Activity]
    reasoning: Optional[str] = None
