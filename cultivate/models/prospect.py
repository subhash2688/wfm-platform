"""Prospect model — mirrors the Excel Prospect Pipeline tab."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from .database import Base


class Prospect(Base):
    __tablename__ = 'prospects'

    id = Column(Integer, primary_key=True)
    company_name = Column(String(200), nullable=False, unique=True)
    industry = Column(String(100))
    hq_city = Column(String(100))
    nearest_campus = Column(String(100))

    # Giving info
    giving_channel = Column(String(200))
    focus_areas = Column(Text)
    has_foundation = Column(Boolean, default=False)
    foundation_name = Column(String(200))
    csr_page_url = Column(String(500))

    # Contact (primary — for quick access; full contacts in contacts table)
    contact_name = Column(String(200))
    contact_title = Column(String(200))
    contact_email = Column(String(200))
    contact_linkedin = Column(String(500))

    # Scores
    alignment_score = Column(Integer, default=0)
    proximity_score = Column(Integer, default=0)
    capacity_score = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    score_override = Column(Boolean, default=False)

    # Pipeline
    pipeline_stage = Column(String(50), default='1-Research')
    last_action = Column(String(200))
    last_action_date = Column(String(50))
    next_step = Column(String(200))
    next_step_date = Column(String(50))
    ask_amount = Column(Float, default=0)
    amount_received = Column(Float, default=0)
    notes = Column(Text)

    # Metadata
    research_status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def recalculate_total(self):
        self.total_score = (self.alignment_score or 0) + (self.proximity_score or 0) + (self.capacity_score or 0)

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'industry': self.industry,
            'hq_city': self.hq_city,
            'nearest_campus': self.nearest_campus,
            'giving_channel': self.giving_channel,
            'focus_areas': self.focus_areas,
            'has_foundation': self.has_foundation,
            'foundation_name': self.foundation_name,
            'csr_page_url': self.csr_page_url,
            'contact_name': self.contact_name,
            'contact_title': self.contact_title,
            'contact_email': self.contact_email,
            'contact_linkedin': self.contact_linkedin,
            'alignment_score': self.alignment_score,
            'proximity_score': self.proximity_score,
            'capacity_score': self.capacity_score,
            'total_score': self.total_score,
            'score_override': self.score_override,
            'pipeline_stage': self.pipeline_stage,
            'last_action': self.last_action,
            'last_action_date': self.last_action_date,
            'next_step': self.next_step,
            'next_step_date': self.next_step_date,
            'ask_amount': self.ask_amount,
            'amount_received': self.amount_received,
            'notes': self.notes,
            'research_status': self.research_status,
        }
