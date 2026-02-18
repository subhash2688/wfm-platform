"""Contact model — multiple contacts per prospect."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from .database import Base


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=False)
    name = Column(String(200))
    title = Column(String(200))
    email = Column(String(200))
    linkedin_url = Column(String(500))
    is_primary = Column(Boolean, default=False)
    source = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'prospect_id': self.prospect_id,
            'name': self.name,
            'title': self.title,
            'email': self.email,
            'linkedin_url': self.linkedin_url,
            'is_primary': self.is_primary,
            'source': self.source,
        }
