"""Grant deadline / grant opportunity model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from .database import Base


class GrantDeadline(Base):
    __tablename__ = 'grant_deadlines'

    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=True)
    company_name = Column(String(200))
    program_name = Column(String(300))
    focus_area = Column(String(200))

    # Timing
    application_opens = Column(String(50))
    deadline = Column(String(50))
    cycle = Column(String(100))          # Rolling, Annual, Quarterly, etc.

    # Grant details
    award_range = Column(String(100))
    grant_type = Column(String(100))     # Cash, In-Kind, Product, Ad Credits

    # Eligibility
    eligibility = Column(Text)           # Who can apply
    geographic_focus = Column(String(200))
    requires_501c3 = Column(String(5), default='Y')

    # Application process
    application_url = Column(String(500))
    application_process = Column(Text)   # How to apply step by step
    required_documents = Column(Text)    # What you need to submit
    contact_info = Column(Text)          # Contact person / email

    # Status tracking
    status = Column(String(50), default='Not Started')
    priority = Column(String(20), default='Medium')  # High, Medium, Low

    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'prospect_id': self.prospect_id,
            'company_name': self.company_name,
            'program_name': self.program_name,
            'focus_area': self.focus_area,
            'application_opens': self.application_opens,
            'deadline': self.deadline,
            'cycle': self.cycle,
            'award_range': self.award_range,
            'grant_type': self.grant_type,
            'eligibility': self.eligibility,
            'geographic_focus': self.geographic_focus,
            'requires_501c3': self.requires_501c3,
            'application_url': self.application_url,
            'application_process': self.application_process,
            'required_documents': self.required_documents,
            'contact_info': self.contact_info,
            'status': self.status,
            'priority': self.priority,
            'notes': self.notes,
        }
