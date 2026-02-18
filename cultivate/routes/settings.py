"""Settings route — GET /settings — lightweight DB overview."""
from flask import Blueprint, render_template
from models.database import db_session
from models.prospect import Prospect
from models.foundation import FoundationData
from models.outreach import OutreachEmail
from models.grant_deadline import GrantDeadline
from models.contact import Contact
from models.activity_log import ActivityLog
from models.action_item import ActionItem
from models.event import Event
from config import INDUSTRIES

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings')
def settings():
    stats = {
        'prospects': db_session.query(Prospect).count(),
        'foundations': db_session.query(FoundationData).count(),
        'emails': db_session.query(OutreachEmail).count(),
        'deadlines': db_session.query(GrantDeadline).count(),
        'contacts': db_session.query(Contact).count(),
        'action_items': db_session.query(ActionItem).count(),
        'events': db_session.query(Event).count(),
        'activities': db_session.query(ActivityLog).count(),
    }

    return render_template('pages/settings.html',
                           active_page='settings',
                           stats=stats,
                           industries=INDUSTRIES)
