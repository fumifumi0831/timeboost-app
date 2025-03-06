from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from ..database import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-10
    fatigue_level = Column(Integer, nullable=False)  # 1-10
    location = Column(String, nullable=False)  # 'home', 'office', 'cafe', etc.
    duration = Column(Integer, nullable=False)  # 選択した時間（分）
    completion_status = Column(String, nullable=False)  # 'completed', 'partial', 'abandoned'
    comments = Column(String)
    created_at = Column(DateTime, default=func.now())
