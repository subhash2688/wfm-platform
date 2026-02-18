"""Campus model — stores campus locations with colors."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from .database import Base


class Campus(Base):
    __tablename__ = 'campuses'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    city = Column(String(100))
    zip_code = Column(String(10))
    region = Column(String(100))
    color = Column(String(20), default='blue')  # blue, orange, purple, green, rose
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'zip_code': self.zip_code,
            'region': self.region,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
