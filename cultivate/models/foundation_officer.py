"""Foundation officers/board from Part VII of 990 filings."""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from .database import Base


class FoundationOfficer(Base):
    __tablename__ = 'foundation_officers'

    id = Column(Integer, primary_key=True)
    foundation_data_id = Column(Integer, ForeignKey('foundation_data.id'), nullable=False)
    tax_year = Column(Integer)

    name = Column(String(300))
    title = Column(String(300))
    hours_per_week = Column(Float, default=0)
    compensation = Column(Float, default=0)

    is_officer = Column(Boolean, default=False)
    is_director = Column(Boolean, default=False)
    is_trustee = Column(Boolean, default=False)
    is_key_employee = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'foundation_data_id': self.foundation_data_id,
            'tax_year': self.tax_year,
            'name': self.name,
            'title': self.title,
            'hours_per_week': self.hours_per_week,
            'compensation': self.compensation,
            'is_officer': self.is_officer,
            'is_director': self.is_director,
            'is_trustee': self.is_trustee,
            'is_key_employee': self.is_key_employee,
        }
