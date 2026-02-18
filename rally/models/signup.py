"""Signup model — links volunteer to shift with status tracking."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from .database import Base


class Signup(Base):
    __tablename__ = 'signups'

    id = Column(Integer, primary_key=True)
    volunteer_id = Column(Integer, ForeignKey('volunteers.id'), nullable=False)
    shift_id = Column(Integer, ForeignKey('shifts.id'), nullable=False)
    status = Column(String(20), default='signed_up')
    signed_up_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    checked_in_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    notes = Column(String(500))

    __table_args__ = (
        UniqueConstraint('volunteer_id', 'shift_id', name='uq_volunteer_shift'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'volunteer_id': self.volunteer_id,
            'shift_id': self.shift_id,
            'status': self.status,
            'signed_up_at': self.signed_up_at.isoformat() if self.signed_up_at else None,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None,
            'checked_in_at': self.checked_in_at.isoformat() if self.checked_in_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'notes': self.notes,
        }
