"""Activity log model — audit trail per prospect."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from .database import Base


class ActivityLog(Base):
    __tablename__ = 'activity_log'

    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=True)
    action_type = Column(String(50))  # import, score, fetch_990, email_draft, stage_change, edit
    description = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'prospect_id': self.prospect_id,
            'action_type': self.action_type,
            'description': self.description,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }
