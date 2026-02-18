"""Home route — Cultivate landing page."""
from flask import Blueprint, render_template
from models.database import db_session
from models.prospect import Prospect
from models.foundation import FoundationData
from models.outreach import OutreachEmail
from models.contact import Contact
from models.grant_deadline import GrantDeadline
from models.action_item import ActionItem
from models.event import Event
from models.activity_log import ActivityLog

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def index():
    prospects = db_session.query(Prospect).all()
    total_prospects = len(prospects)

    # Live counts
    foundations_count = db_session.query(FoundationData).count()
    emails_count = db_session.query(OutreachEmail).count()
    contacts_count = db_session.query(Contact).count()
    actions_todo = db_session.query(ActionItem).filter(ActionItem.status != 'done').count()

    # Pipeline stats
    outreach_active = sum(1 for p in prospects if p.pipeline_stage in (
        '3-Outreach Sent', '4-Meeting Scheduled', '5-Proposal Sent', '6-Under Review'))
    total_raised = sum(p.amount_received or 0 for p in prospects)

    # Campus counts
    campus_counts = {
        'De Anza College': 0,
        'Foothill College': 0,
        'Chabot College': 0,
    }
    for p in prospects:
        campus = p.nearest_campus or ''
        if campus == 'All Campuses':
            for k in campus_counts:
                campus_counts[k] += 1
        elif campus in campus_counts:
            campus_counts[campus] += 1

    # Recent activity (last 5)
    activities = (db_session.query(ActivityLog)
                  .order_by(ActivityLog.timestamp.desc())
                  .limit(5)
                  .all())

    return render_template('pages/home.html',
                           active_page='home',
                           total_prospects=total_prospects,
                           foundations_count=foundations_count,
                           emails_count=emails_count,
                           actions_todo=actions_todo,
                           outreach_active=outreach_active,
                           total_raised=total_raised,
                           campus_counts=campus_counts,
                           activities=activities)
