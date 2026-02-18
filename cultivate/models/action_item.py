"""ActionItem model — task checklist for fundraising actions."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date
from .database import Base


class ActionItem(Base):
    __tablename__ = 'action_items'

    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=True)
    description = Column(Text, nullable=False)
    action_type = Column(String(50), default='research')  # email, call, apply, research, attend, connect
    priority = Column(String(20), default='medium')  # high, medium, low
    status = Column(String(20), default='todo')  # todo, in_progress, done
    due_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'prospect_id': self.prospect_id,
            'description': self.description,
            'action_type': self.action_type,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
