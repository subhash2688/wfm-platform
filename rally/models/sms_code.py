"""SmsCode model — OTP codes for volunteer phone authentication."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from .database import Base


class SmsCode(Base):
    __tablename__ = 'sms_codes'

    id = Column(Integer, primary_key=True)
    phone = Column(String(20), nullable=False, index=True)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'code': self.code,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'used': self.used,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
