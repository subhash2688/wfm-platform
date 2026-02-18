"""Recurring series model — template for repeating shifts."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Time, Boolean, DateTime
from .database import Base


class RecurringSeries(Base):
    __tablename__ = 'recurring_series'

    id = Column(Integer, primary_key=True)
    campus = Column(String(100), nullable=False)
    day_of_week = Column(String(10), nullable=False)  # Monday, Tuesday, etc.
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    shift_type = Column(String(50), default='Food Distribution')
    required_count = Column(Integer, default=4)
    frequency = Column(String(20), default='weekly')  # weekly, biweekly, monthly
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'campus': self.campus,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'shift_type': self.shift_type,
            'required_count': self.required_count,
            'frequency': self.frequency,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
