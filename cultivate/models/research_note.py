"""Research notes — news, insights, connections for prospects."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from .database import Base


class ResearchNote(Base):
    __tablename__ = 'research_notes'

    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=False)

    note_type = Column(String(50))  # news, insight, connection, csr_update
    title = Column(String(500))
    content = Column(Text)
    source_url = Column(String(500))
    published_date = Column(String(50))

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'prospect_id': self.prospect_id,
            'note_type': self.note_type,
            'title': self.title,
            'content': self.content,
            'source_url': self.source_url,
            'published_date': self.published_date,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
