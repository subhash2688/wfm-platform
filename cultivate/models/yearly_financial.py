"""Yearly financial data from 990 filings — multi-year trends."""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, UniqueConstraint
from .database import Base


class YearlyFinancial(Base):
    __tablename__ = 'yearly_financials'
    __table_args__ = (
        UniqueConstraint('foundation_data_id', 'tax_year', name='uq_foundation_year'),
    )

    id = Column(Integer, primary_key=True)
    foundation_data_id = Column(Integer, ForeignKey('foundation_data.id'), nullable=False)
    tax_year = Column(Integer, nullable=False)

    total_assets = Column(Float, default=0)
    total_grants_paid = Column(Float, default=0)
    total_revenue = Column(Float, default=0)
    total_expenses = Column(Float, default=0)

    # Revenue breakdown
    contributions_received = Column(Float, default=0)
    investment_income = Column(Float, default=0)
    capital_gains = Column(Float, default=0)
    other_income = Column(Float, default=0)

    # Expense breakdown
    grants_to_orgs = Column(Float, default=0)
    admin_expenses = Column(Float, default=0)
    officer_compensation = Column(Float, default=0)
    program_expenses = Column(Float, default=0)

    # Filing metadata
    object_id = Column(String(50))
    pdf_url = Column(String(500))
    filing_type = Column(String(20))

    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'foundation_data_id': self.foundation_data_id,
            'tax_year': self.tax_year,
            'total_assets': self.total_assets,
            'total_grants_paid': self.total_grants_paid,
            'total_revenue': self.total_revenue,
            'total_expenses': self.total_expenses,
            'contributions_received': self.contributions_received,
            'investment_income': self.investment_income,
            'grants_to_orgs': self.grants_to_orgs,
            'admin_expenses': self.admin_expenses,
            'officer_compensation': self.officer_compensation,
            'object_id': self.object_id,
            'pdf_url': self.pdf_url,
            'filing_type': self.filing_type,
        }
