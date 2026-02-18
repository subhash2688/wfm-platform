"""Company detail route — GET /company/<id>."""
from flask import Blueprint, render_template, request, jsonify
from models.database import db_session
from models.prospect import Prospect
from models.foundation import FoundationData
from models.contact import Contact
from models.outreach import OutreachEmail
from models.activity_log import ActivityLog
from models.action_item import ActionItem
from config import PIPELINE_STAGES
from models.yearly_financial import YearlyFinancial
from models.foundation_grant import FoundationGrant
from models.foundation_officer import FoundationOfficer
from models.research_note import ResearchNote

company_bp = Blueprint('company', __name__)


@company_bp.route('/company/<int:prospect_id>')
def company_detail(prospect_id):
    prospect = db_session.query(Prospect).get(prospect_id)
    if not prospect:
        return 'Prospect not found', 404

    foundation = db_session.query(FoundationData).filter_by(prospect_id=prospect_id).first()
    email = db_session.query(OutreachEmail).filter_by(prospect_id=prospect_id).first()
    contacts = db_session.query(Contact).filter_by(prospect_id=prospect_id).all()
    action_items = db_session.query(ActionItem).filter_by(prospect_id=prospect_id).all()
    activities = (db_session.query(ActivityLog)
                  .filter_by(prospect_id=prospect_id)
                  .order_by(ActivityLog.timestamp.desc())
                  .limit(20)
                  .all())

    # Deep research data
    yearly_financials = []
    grantees = []
    officers = []
    research_notes = []
    max_grants = 0

    if foundation:
        yearly_financials = (db_session.query(YearlyFinancial)
                             .filter_by(foundation_data_id=foundation.id)
                             .order_by(YearlyFinancial.tax_year)
                             .all())
        grantees = (db_session.query(FoundationGrant)
                    .filter_by(foundation_data_id=foundation.id)
                    .order_by(FoundationGrant.amount.desc())
                    .limit(25)
                    .all())
        officers = (db_session.query(FoundationOfficer)
                    .filter_by(foundation_data_id=foundation.id)
                    .order_by(FoundationOfficer.compensation.desc())
                    .all())
        if yearly_financials:
            max_grants = max(y.total_grants_paid or 0 for y in yearly_financials)

    research_notes = (db_session.query(ResearchNote)
                      .filter_by(prospect_id=prospect_id)
                      .order_by(ResearchNote.created_at.desc())
                      .all())

    return render_template('pages/company.html',
                           active_page='progress',
                           prospect=prospect,
                           foundation=foundation,
                           email=email,
                           contacts=contacts,
                           action_items=action_items,
                           activities=activities,
                           yearly_financials=yearly_financials,
                           grantees=grantees,
                           officers=officers,
                           max_grants=max_grants,
                           research_notes=research_notes,
                           stages=PIPELINE_STAGES)
