from sqlalchemy import Column, Integer, String, DateTime, func
from ..database import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)  # 'relaxation', 'light_exercise', 'desk_work', 'short_focus', 'location_specific'
    duration = Column(Integer, nullable=False)  # 分単位: 15, 30, 45, 60
    locations = Column(String, nullable=False)  # JSONで格納: ['home', 'office', 'cafe', etc.]
    fatigue_min = Column(Integer, nullable=False)  # 1-10
    fatigue_max = Column(Integer, nullable=False)  # 1-10
    steps = Column(String)  # JSONで手順を格納
    benefits = Column(String)  # JSON形式で効果を格納
    image_url = Column(String)
    scientific_basis = Column(String)  # 科学的根拠（論文参照など）
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
