"""Home route — Rally dashboard."""
from datetime import date, datetime
from flask import Blueprint, render_template
from models.database import db_session
from models.campus import Campus
from models.volunteer import Volunteer
from models.shift import Shift
from models.signup import Signup
from models.activity_log import ActivityLog
from services.stats import get_dashboard_stats, get_shift_fill_count

home_bp = Blueprint('home', __name__)


def _short_campus(campus):
    """De Anza College → De Anza"""
    return campus.replace(' College', '')


def _get_campus_colors():
    """Return {campus_name: color} dict from DB."""
    campuses = db_session.query(Campus).all()
    return {c.name: c.color for c in campuses}


def _format_time(t):
    """Format time like '9 AM', '2 PM', '10:30 AM'"""
    hour = t.hour % 12 or 12
    period = 'AM' if t.hour < 12 else 'PM'
    if t.minute == 0:
        return f'{hour} {period}'
    return f'{hour}:{t.minute:02d} {period}'


def _format_time_range(start, end):
    """Format range like '9 AM – 1 PM' or '2 – 5 PM'"""
    start_period = 'AM' if start.hour < 12 else 'PM'
    end_period = 'AM' if end.hour < 12 else 'PM'
    end_str = _format_time(end)
    if start_period == end_period:
        hour = start.hour % 12 or 12
        start_short = str(hour) if start.minute == 0 else f'{hour}:{start.minute:02d}'
        return f'{start_short} – {end_str}'
    return f'{_format_time(start)} – {end_str}'


def _relative_date(d):
    """Return relative date: Today, Tomorrow, Wed, Next Mon, Feb 28."""
    today = date.today()
    delta = (d - today).days
    if delta == 0:
        return 'Today'
    if delta == 1:
        return 'Tomorrow'
    if delta < 7:
        return d.strftime('%a')
    if delta < 14:
        return 'Next ' + d.strftime('%a')
    return d.strftime('%b %d')


def _fill_class(filled, required):
    """Return CSS color class for fill rate."""
    if required == 0:
        return 'green'
    ratio = filled / required
    if ratio >= 1:
        return 'green'
    if ratio >= 0.6:
        return 'orange'
    return 'rose'


def _avatar_color(name):
    """Pick a consistent color for a person's name."""
    colors = ['green', 'orange', 'purple', 'blue', 'rose']
    return colors[hash(name) % len(colors)]


@home_bp.route('/')
def index():
    stats = get_dashboard_stats()
    today = date.today()

    campus_colors = _get_campus_colors()

    # Upcoming shifts with fill counts (top 5)
    upcoming_shifts = (db_session.query(Shift)
                       .filter(Shift.date >= today)
                       .filter(Shift.status == 'scheduled')
                       .order_by(Shift.date, Shift.start_time)
                       .limit(5)
                       .all())

    shift_items = []
    for shift in upcoming_shifts:
        filled = get_shift_fill_count(shift.id)
        shift_items.append({
            'id': shift.id,
            'type': shift.shift_type,
            'campus': _short_campus(shift.campus),
            'campus_class': campus_colors.get(shift.campus, 'blue'),
            'date_label': _relative_date(shift.date),
            'time_label': _format_time_range(shift.start_time, shift.end_time),
            'filled': filled,
            'required': shift.required_count,
            'fill_class': _fill_class(filled, shift.required_count),
        })

    # Build recent activity feed from signups + new volunteers + log
    activities = []

    # Recent signups (most recent action per signup)
    recent_signups = (db_session.query(Signup, Volunteer, Shift)
                      .join(Volunteer, Signup.volunteer_id == Volunteer.id)
                      .join(Shift, Signup.shift_id == Shift.id)
                      .order_by(Signup.signed_up_at.desc())
                      .limit(10)
                      .all())

    for signup, vol, shift in recent_signups:
        # Use the most recent status transition
        action = 'signed up'
        ts = signup.signed_up_at
        if signup.status == 'confirmed' and signup.confirmed_at:
            action = 'confirmed'
            ts = signup.confirmed_at
        elif signup.status == 'checked_in' and signup.checked_in_at:
            action = 'checked in'
            ts = signup.checked_in_at
        elif signup.status == 'completed' and signup.completed_at:
            action = 'completed'
            ts = signup.completed_at

        initials = (vol.first_name[0] + vol.last_name[0]).upper()
        activities.append({
            'initials': initials,
            'color': _avatar_color(vol.first_name + vol.last_name),
            'title': f'{vol.first_name} {vol.last_name} {action}',
            'detail': f'{shift.shift_type} at {_short_campus(shift.campus)} \u00b7 {_relative_date(shift.date)}',
            'timestamp': ts,
        })

    # New volunteers
    new_vols = (db_session.query(Volunteer)
                .filter(Volunteer.status == 'new')
                .order_by(Volunteer.joined_date.desc())
                .limit(5)
                .all())

    for vol in new_vols:
        campuses = vol.get_campuses()
        campus_label = _short_campus(campuses[0]) if campuses else 'No campus'
        initials = (vol.first_name[0] + vol.last_name[0]).upper()
        activities.append({
            'initials': initials,
            'color': _avatar_color(vol.first_name + vol.last_name),
            'title': f'{vol.first_name} {vol.last_name} joined',
            'detail': f'New volunteer \u00b7 {campus_label}',
            'timestamp': vol.joined_date,
        })

    # System events from activity log
    log_entries = (db_session.query(ActivityLog)
                   .order_by(ActivityLog.timestamp.desc())
                   .limit(3)
                   .all())

    for entry in log_entries:
        activities.append({
            'initials': '\u2605',
            'color': 'blue',
            'title': entry.description,
            'detail': entry.action_type.replace('_', ' ').title(),
            'timestamp': entry.timestamp,
        })

    # Sort by timestamp descending, take top 5
    activities.sort(
        key=lambda x: x['timestamp'] if x['timestamp'] else datetime.min,
        reverse=True
    )
    activities = activities[:5]

    return render_template('pages/home.html',
                           active_page='home',
                           stats=stats,
                           shift_items=shift_items,
                           activities=activities)
