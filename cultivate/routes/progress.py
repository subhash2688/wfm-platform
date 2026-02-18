"""Progress route — scorecard, weekly goals, pipeline funnel, activity timeline."""
from datetime import date, timedelta
from flask import Blueprint, render_template, request, jsonify
from models.database import db_session
from models.prospect import Prospect
from models.outreach import OutreachEmail
from models.activity_log import ActivityLog
from models.weekly_goal import WeeklyGoal
from config import PIPELINE_STAGES

progress_bp = Blueprint('progress', __name__)


def get_week_start():
    """Get Monday of the current week."""
    today = date.today()
    return today - timedelta(days=today.weekday())


@progress_bp.route('/progress')
def index():
    prospects = db_session.query(Prospect).all()

    # Scorecard
    stats = {
        'total': len(prospects),
        'outreach_sent': sum(1 for p in prospects if p.pipeline_stage in ('3-Outreach Sent',)),
        'meetings': sum(1 for p in prospects if p.pipeline_stage == '4-Meeting Scheduled'),
        'proposals': sum(1 for p in prospects if p.pipeline_stage in ('5-Proposal Sent', '6-Under Review')),
        'funded': sum(1 for p in prospects if p.pipeline_stage == '7-Funded'),
        'total_received': sum(p.amount_received or 0 for p in prospects),
    }

    # Pipeline funnel
    stage_counts = {}
    for stage in PIPELINE_STAGES:
        stage_counts[stage] = sum(1 for p in prospects if p.pipeline_stage == stage)

    funnel = [
        {'label': 'Research', 'count': stage_counts.get('1-Research', 0)},
        {'label': 'Contact', 'count': stage_counts.get('2-Contact Identified', 0)},
        {'label': 'Outreach', 'count': stage_counts.get('3-Outreach Sent', 0)},
        {'label': 'Meeting', 'count': stage_counts.get('4-Meeting Scheduled', 0)},
        {'label': 'Proposal', 'count': stage_counts.get('5-Proposal Sent', 0) + stage_counts.get('6-Under Review', 0)},
        {'label': 'Funded', 'count': stage_counts.get('7-Funded', 0)},
    ]

    # Weekly goals
    week_start = get_week_start()
    goals = db_session.query(WeeklyGoal).filter_by(week_start=week_start).all()
    goal_map = {g.category: g for g in goals}

    categories = [
        ('emails_sent', 'Emails Sent'),
        ('meetings_scheduled', 'Meetings Scheduled'),
        ('grants_applied', 'Grants Applied'),
        ('contacts_added', 'Contacts Added'),
    ]
    weekly_goals = []
    for cat_key, cat_label in categories:
        g = goal_map.get(cat_key)
        target = g.target if g else 5
        actual = g.actual if g else 0
        pct = min(100, int((actual / target) * 100)) if target > 0 else 0
        weekly_goals.append({
            'id': g.id if g else None,
            'category': cat_key,
            'label': cat_label,
            'target': target,
            'actual': actual,
            'pct': pct,
        })

    # Activity timeline
    activities = (db_session.query(ActivityLog)
                  .order_by(ActivityLog.timestamp.desc())
                  .limit(20)
                  .all())

    return render_template('pages/progress.html',
                           active_page='progress',
                           stats=stats,
                           funnel=funnel,
                           weekly_goals=weekly_goals,
                           week_start=week_start,
                           activities=activities)


# ─── Weekly Goals APIs ───

@progress_bp.route('/api/weekly-goal', methods=['POST'])
def set_weekly_goal():
    data = request.json
    week_start = date.fromisoformat(data['week_start']) if data.get('week_start') else get_week_start()
    category = data.get('category')

    goal = db_session.query(WeeklyGoal).filter_by(
        week_start=week_start, category=category
    ).first()

    if goal:
        if 'target' in data:
            goal.target = int(data['target'])
        if 'actual' in data:
            goal.actual = int(data['actual'])
    else:
        goal = WeeklyGoal(
            week_start=week_start,
            category=category,
            target=int(data.get('target', 5)),
            actual=int(data.get('actual', 0)),
        )
        db_session.add(goal)

    db_session.commit()
    return jsonify(goal.to_dict())


@progress_bp.route('/api/weekly-goal/<int:goal_id>/increment', methods=['POST'])
def increment_weekly_goal(goal_id):
    goal = db_session.query(WeeklyGoal).get(goal_id)
    if not goal:
        return jsonify({'error': 'Not found'}), 404
    goal.actual = (goal.actual or 0) + 1
    db_session.commit()
    return jsonify(goal.to_dict())
