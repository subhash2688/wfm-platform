"""Activity log model — audit trail for volunteer management."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from .database import Base


class ActivityLog(Base):
    __tablename__ = 'activity_log'

    id = Column(Integer, primary_key=True)
    action_type = Column(String(50))  # create, update, delete, check_in, signup, seed, export
    description = Column(Text)
    volunteer_id = Column(Integer, ForeignKey('volunteers.id'), nullable=True)
    shift_id = Column(Integer, ForeignKey('shifts.id'), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'action_type': self.action_type,
            'description': self.description,
            'volunteer_id': self.volunteer_id,
            'shift_id': self.shift_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }
