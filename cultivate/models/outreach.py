"""Outreach email model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from .database import Base


class OutreachEmail(Base):
    __tablename__ = 'outreach_emails'

    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=False)
    subject = Column(String(300))
    body = Column(Text)
    status = Column(String(50), default='draft')  # draft, reviewed, sent
    personalization_notes = Column(Text)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'prospect_id': self.prospect_id,
            'subject': self.subject,
            'body': self.body,
            'status': self.status,
            'personalization_notes': self.personalization_notes,
            'word_count': self.word_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
