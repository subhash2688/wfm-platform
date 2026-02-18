"""Foundation grantee data from Schedule I of 990 filings."""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, Text, ForeignKey
from .database import Base


class FoundationGrant(Base):
    __tablename__ = 'foundation_grants'

    id = Column(Integer, primary_key=True)
    foundation_data_id = Column(Integer, ForeignKey('foundation_data.id'), nullable=False)
    tax_year = Column(Integer)

    grantee_name = Column(String(500))
    grantee_ein = Column(String(20))
    amount = Column(Float, default=0)
    purpose = Column(Text)

    # Location
    grantee_city = Column(String(100))
    grantee_state = Column(String(10))
    grantee_zip = Column(String(20))

    # Auto-tagged category
    category = Column(String(50))  # food_hunger, education, health, community, youth, environment, arts, workforce, other
    category_confidence = Column(String(10), default='medium')  # high, medium, low
    is_bay_area = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'foundation_data_id': self.foundation_data_id,
            'tax_year': self.tax_year,
            'grantee_name': self.grantee_name,
            'grantee_ein': self.grantee_ein,
            'amount': self.amount,
            'purpose': self.purpose,
            'grantee_city': self.grantee_city,
            'grantee_state': self.grantee_state,
            'grantee_zip': self.grantee_zip,
            'category': self.category,
            'category_confidence': self.category_confidence,
            'is_bay_area': self.is_bay_area,
        }
