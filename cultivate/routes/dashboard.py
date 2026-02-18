"""Dashboard route — GET / — pipeline overview."""
from flask import Blueprint, render_template
from sqlalchemy import func
from models.database import db_session
from models.prospect import Prospect
from models.activity_log import ActivityLog
from config import PIPELINE_STAGES

dashboard_bp = Blueprint('dashboard', __name__)


def stage_color(stage):
    colors = {
        '1-Research': 'blue',
        '2-Contact Identified': 'purple',
        '3-Outreach Sent': 'orange',
        '4-Meeting Scheduled': 'orange',
        '5-Proposal Sent': 'green',
        '6-Under Review': 'blue',
        '7-Funded': 'green',
        '8-Declined': 'rose',
    }
    return colors.get(stage, 'blue')


@dashboard_bp.route('/')
def index():
    prospects = db_session.query(Prospect).all()

    stats = {
        'total': len(prospects),
        'active_outreach': sum(1 for p in prospects if p.pipeline_stage in ['3-Outreach Sent', '4-Meeting Scheduled']),
        'proposals': sum(1 for p in prospects if p.pipeline_stage in ['5-Proposal Sent', '6-Under Review']),
        'funded': sum(1 for p in prospects if p.pipeline_stage == '7-Funded'),
        'total_ask': sum(p.ask_amount or 0 for p in prospects),
        'total_received': sum(p.amount_received or 0 for p in prospects),
    }

    # Stage counts
    stage_counts = {}
    for stage in PIPELINE_STAGES:
        stage_counts[stage] = sum(1 for p in prospects if p.pipeline_stage == stage)

    # Top 15 by score
    top_prospects = sorted(prospects, key=lambda p: p.total_score or 0, reverse=True)[:15]

    # Recent activity
    activities = (db_session.query(ActivityLog)
                  .order_by(ActivityLog.timestamp.desc())
                  .limit(20)
                  .all())

    return render_template('pages/dashboard.html',
                           active_page='dashboard',
                           stats=stats,
                           stage_counts=stage_counts,
                           top_prospects=top_prospects,
                           activities=activities,
                           stage_color=stage_color)
