"""WeeklyGoal model — target vs actual tracking per week."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Date
from .database import Base


class WeeklyGoal(Base):
    __tablename__ = 'weekly_goals'

    id = Column(Integer, primary_key=True)
    week_start = Column(Date, nullable=False)
    category = Column(String(50), nullable=False)  # emails_sent, meetings_scheduled, grants_applied, contacts_added
    target = Column(Integer, default=0)
    actual = Column(Integer, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'week_start': self.week_start.isoformat() if self.week_start else None,
            'category': self.category,
            'target': self.target,
            'actual': self.actual,
            'notes': self.notes,
        }
