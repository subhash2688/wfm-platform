"""Foundation 990 data model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from .database import Base


class FoundationData(Base):
    __tablename__ = 'foundation_data'

    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=False, unique=True)

    foundation_name = Column(String(300))
    ein = Column(String(20))
    tax_period = Column(String(20))

    # --- Financial summary ---
    total_assets = Column(Float, default=0)
    total_grants_paid = Column(Float, default=0)
    total_revenue = Column(Float, default=0)
    average_grant_size = Column(Float, default=0)
    num_grantees = Column(Integer, default=0)
    total_expenses = Column(Float, default=0)

    # --- Revenue breakdown ---
    contributions_received = Column(Float, default=0)   # grscontrgifts — corporate contributions
    investment_income = Column(Float, default=0)         # intrstrvnue + dividndsamt
    capital_gains = Column(Float, default=0)             # totexcapgn
    other_income = Column(Float, default=0)              # otherincamt

    # --- Expense breakdown ---
    grants_to_orgs = Column(Float, default=0)            # contrpdpbks (990-PF)
    admin_expenses = Column(Float, default=0)            # topradmnexpnsa
    officer_compensation = Column(Float, default=0)      # topradmnexpnsb / compofficers
    program_expenses = Column(Float, default=0)          # totexpnsexempt

    # --- Net investment & distribution ---
    net_investment_income = Column(Float, default=0)     # netinvstinc
    minimum_investment_return = Column(Float, default=0) # cmpmininvstret
    distributable_amount = Column(Float, default=0)      # distribamt

    # --- Classification ---
    ntee_code = Column(String(10))
    ntee_description = Column(String(200))
    subsection_code = Column(String(5))      # 3 = 501(c)(3)
    foundation_code = Column(String(5))      # 4 = private foundation
    filing_type = Column(String(20))         # 990, 990-PF, 990-EZ

    # --- Program areas / causes ---
    program_areas = Column(Text)             # JSON list of cause categories
    focus_keywords = Column(Text)            # extracted keywords from mission

    # --- Location ---
    foundation_city = Column(String(100))
    foundation_state = Column(String(10))
    foundation_address = Column(String(300))
    foundation_zip = Column(String(20))

    # --- Foundation website ---
    foundation_url = Column(String(500))

    # --- Grant application info ---
    grant_types = Column(Text)               # JSON: what types of grants they give
    application_url = Column(String(500))
    application_info = Column(Text)          # notes about application process
    gives_to_individuals = Column(String(5)) # Y/N
    gives_to_orgs = Column(String(5))        # Y/N
    furnishes_goods = Column(String(5))      # Y/N (in-kind)

    # --- Fit assessment ---
    fit_assessment = Column(String(50))
    mission_statement = Column(Text)
    geographic_focus = Column(String(200))

    # --- Deep research ---
    mission_overlap_score = Column(Float, default=0)    # % of grants to food/education/community
    bay_area_grant_pct = Column(Float, default=0)       # % of grants to Bay Area orgs
    giving_trend = Column(String(20))                   # growing, stable, declining
    years_of_data = Column(Integer, default=0)
    deep_research_at = Column(DateTime)

    # --- Raw data ---
    pdf_url = Column(String(500))
    raw_response = Column(Text)  # JSON

    fetched_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'prospect_id': self.prospect_id,
            'foundation_name': self.foundation_name,
            'ein': self.ein,
            'total_assets': self.total_assets,
            'total_grants_paid': self.total_grants_paid,
            'total_revenue': self.total_revenue,
            'total_expenses': self.total_expenses,
            'average_grant_size': self.average_grant_size,
            'num_grantees': self.num_grantees,
            'tax_period': self.tax_period,
            'contributions_received': self.contributions_received,
            'investment_income': self.investment_income,
            'capital_gains': self.capital_gains,
            'grants_to_orgs': self.grants_to_orgs,
            'admin_expenses': self.admin_expenses,
            'officer_compensation': self.officer_compensation,
            'program_expenses': self.program_expenses,
            'net_investment_income': self.net_investment_income,
            'distributable_amount': self.distributable_amount,
            'ntee_code': self.ntee_code,
            'ntee_description': self.ntee_description,
            'filing_type': self.filing_type,
            'program_areas': self.program_areas,
            'foundation_city': self.foundation_city,
            'foundation_state': self.foundation_state,
            'foundation_url': self.foundation_url,
            'gives_to_individuals': self.gives_to_individuals,
            'gives_to_orgs': self.gives_to_orgs,
            'furnishes_goods': self.furnishes_goods,
            'fit_assessment': self.fit_assessment,
            'mission_statement': self.mission_statement,
            'geographic_focus': self.geographic_focus,
            'mission_overlap_score': self.mission_overlap_score,
            'bay_area_grant_pct': self.bay_area_grant_pct,
            'giving_trend': self.giving_trend,
            'years_of_data': self.years_of_data,
            'deep_research_at': self.deep_research_at.isoformat() if self.deep_research_at else None,
            'pdf_url': self.pdf_url,
            'fetched_at': self.fetched_at.isoformat() if self.fetched_at else None,
        }
