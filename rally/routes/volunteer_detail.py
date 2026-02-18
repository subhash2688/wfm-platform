"""Volunteer detail route — profile with stats and shift history."""
import urllib.parse
from flask import Blueprint, render_template
from models.database import db_session
from models.volunteer import Volunteer
from models.shift import Shift
from models.signup import Signup
from services.stats import get_volunteer_stats, get_dashboard_stats

volunteer_detail_bp = Blueprint('volunteer_detail', __name__)


@volunteer_detail_bp.route('/volunteers/<int:vol_id>')
def detail(vol_id):
    volunteer = db_session.query(Volunteer).get(vol_id)
    if not volunteer:
        return 'Volunteer not found', 404

    stats = get_volunteer_stats(vol_id)

    # Build shift history
    signups = (db_session.query(Signup)
               .filter(Signup.volunteer_id == vol_id)
               .order_by(Signup.signed_up_at.desc())
               .all())

    shift_history = []
    for su in signups:
        shift = db_session.query(Shift).get(su.shift_id)
        if shift:
            shift_history.append({
                'shift_id': shift.id,
                'date': shift.date.strftime('%a, %b %d, %Y') if shift.date else '',
                'campus': shift.campus,
                'shift_type': shift.shift_type,
                'time': f'{shift.start_time.strftime("%I:%M %p")} – {shift.end_time.strftime("%I:%M %p")}' if shift.start_time else '',
                'signup_status': su.status,
            })

    gap_count = get_dashboard_stats()['gaps']

    # Last seen display
    from datetime import datetime as dt
    last_seen_display = None
    last_seen_days = None
    if volunteer.last_seen:
        delta = dt.utcnow() - volunteer.last_seen
        days = delta.days
        last_seen_days = days
        if days == 0:
            last_seen_display = 'Today'
        elif days == 1:
            last_seen_display = 'Yesterday'
        elif days < 30:
            last_seen_display = f'{days} days ago'
        elif days < 60:
            last_seen_display = 'About a month ago'
        else:
            last_seen_display = f'{days // 30} months ago'

    # WhatsApp direct link for this volunteer
    wa_url = None
    if volunteer.phone:
        digits = ''.join(c for c in volunteer.phone if c.isdigit())
        if len(digits) == 10:
            digits = '1' + digits
        if digits:
            msg = f"Hi {volunteer.first_name}! This is the World Food Movement volunteer team reaching out."
            wa_url = f"https://wa.me/{digits}?text={urllib.parse.quote(msg)}"

    return render_template('pages/volunteer_detail.html',
                           active_page='volunteers',
                           volunteer=volunteer,
                           stats=stats,
                           shift_history=shift_history,
                           gap_count=gap_count,
                           wa_url=wa_url,
                           last_seen_display=last_seen_display,
                           last_seen_days=last_seen_days)
