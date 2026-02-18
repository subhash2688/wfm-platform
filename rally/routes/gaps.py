"""Gaps route — unfilled shifts with smart suggestions."""
import urllib.parse
from datetime import date
from flask import Blueprint, render_template, jsonify, request
from models.database import db_session
from models.shift import Shift
from services.stats import get_shift_fill_count, get_dashboard_stats
from services.scoring import score_volunteers_for_shift

gaps_bp = Blueprint('gaps', __name__)


@gaps_bp.route('/gaps')
def gap_list():
    today = date.today()

    upcoming = (db_session.query(Shift)
                .filter(Shift.date >= today)
                .filter(Shift.status == 'scheduled')
                .order_by(Shift.date.asc(), Shift.start_time.asc())
                .all())

    gaps = []
    for shift in upcoming:
        filled = get_shift_fill_count(shift.id)
        if filled < shift.required_count:
            days_away = (shift.date - today).days
            gaps.append({
                'shift': shift,
                'filled': filled,
                'needed': shift.required_count - filled,
                'days_away': days_away,
            })

    # Sort by urgency: fewest days away first, then by biggest gap
    gaps.sort(key=lambda g: (g['days_away'], -g['needed']))

    gap_count = len(gaps)

    return render_template('pages/gaps.html',
                           active_page='gaps',
                           gaps=gaps,
                           gap_count=gap_count)


@gaps_bp.route('/api/gaps/<int:shift_id>/suggestions')
def get_suggestions(shift_id):
    shift = db_session.query(Shift).get(shift_id)
    suggestions = score_volunteers_for_shift(shift_id)

    # Enrich each suggestion with a WhatsApp URL if the volunteer has a phone
    if shift:
        base_url = request.host_url.rstrip('/')
        signup_url = f"{base_url}/v/signup/{shift_id}"
        campus_short = shift.campus.split(' College')[0]
        date_str = shift.date.strftime('%A, %b %-d')
        time_str = shift.start_time.strftime('%-I:%M %p')
        for s in suggestions:
            phone = s['volunteer'].get('phone', '')
            if phone:
                digits = ''.join(c for c in phone if c.isdigit())
                if len(digits) == 10:
                    digits = '1' + digits
                msg = (
                    f"Hi {s['volunteer'].get('first_name', '')}! "
                    f"We need a volunteer for a {shift.shift_type} shift at {campus_short} "
                    f"on {date_str} at {time_str}. "
                    f"Interested? Sign up here: {signup_url}"
                )
                s['wa_url'] = f"https://wa.me/{digits}?text={urllib.parse.quote(msg)}" if digits else None
            else:
                s['wa_url'] = None

    return jsonify({'suggestions': suggestions})
