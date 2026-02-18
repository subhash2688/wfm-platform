"""Volunteer model — name, contact info, campus preferences, availability."""
import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from .database import Base


class Volunteer(Base):
    __tablename__ = 'volunteers'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(200))
    preferred_campuses = Column(Text, default='[]')  # JSON list
    preferred_shift_types = Column(Text, default='[]')  # JSON list
    availability = Column(Text, default='{}')  # JSON dict: {day: [time_slots]}
    photo = Column(String(200), nullable=True)
    is_youth = Column(Boolean, default=False)
    status = Column(String(20), default='new')
    notes = Column(Text)
    joined_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = Column(DateTime, nullable=True)   # Last volunteer app access

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_campuses(self):
        try:
            return json.loads(self.preferred_campuses or '[]')
        except (json.JSONDecodeError, TypeError):
            return []

    def set_campuses(self, campuses):
        self.preferred_campuses = json.dumps(campuses)

    def get_shift_types(self):
        try:
            return json.loads(self.preferred_shift_types or '[]')
        except (json.JSONDecodeError, TypeError):
            return []

    def set_shift_types(self, types):
        self.preferred_shift_types = json.dumps(types)

    def get_availability(self):
        try:
            return json.loads(self.availability or '{}')
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_availability(self, avail):
        self.availability = json.dumps(avail)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'email': self.email,
            'preferred_campuses': self.get_campuses(),
            'preferred_shift_types': self.get_shift_types(),
            'photo': self.photo,
            'is_youth': self.is_youth or False,
            'availability': self.get_availability(),
            'status': self.status,
            'notes': self.notes,
            'joined_date': self.joined_date.isoformat() if self.joined_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
