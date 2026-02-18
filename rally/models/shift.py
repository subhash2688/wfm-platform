"""Shift model — campus, date, time, type, required volunteer count."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey
from .database import Base


class Shift(Base):
    __tablename__ = 'shifts'

    id = Column(Integer, primary_key=True)
    campus = Column(String(100), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    shift_type = Column(String(50), default='Serving')
    service_type = Column(String(50), default='Catered Meal')  # Pre-packed Meal or Catered Meal
    required_count = Column(Integer, default=4)
    status = Column(String(20), default='scheduled')
    notes = Column(String(500))
    recurring_series_id = Column(Integer, ForeignKey('recurring_series.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def duration_hours(self):
        """Calculate shift duration in hours."""
        if self.start_time and self.end_time:
            start_mins = self.start_time.hour * 60 + self.start_time.minute
            end_mins = self.end_time.hour * 60 + self.end_time.minute
            return round((end_mins - start_mins) / 60, 1)
        return 0

    def to_dict(self):
        return {
            'id': self.id,
            'campus': self.campus,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'shift_type': self.shift_type,
            'service_type': self.service_type,
            'required_count': self.required_count,
            'status': self.status,
            'notes': self.notes,
            'recurring_series_id': self.recurring_series_id,
            'duration_hours': self.duration_hours,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
