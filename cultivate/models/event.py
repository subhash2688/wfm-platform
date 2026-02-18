"""Event model — conferences, webinars, networking events to attend."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Date
from .database import Base


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    event_type = Column(String(50), default='networking')  # conference, webinar, info_session, networking
    date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    location = Column(String(300))
    url = Column(String(500))
    description = Column(Text)
    relevance = Column(Text)
    status = Column(String(50), default='upcoming')  # upcoming, registered, attended
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'event_type': self.event_type,
            'date': self.date.isoformat() if self.date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'location': self.location,
            'url': self.url,
            'description': self.description,
            'relevance': self.relevance,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
