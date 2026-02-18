"""Shift detail route — single shift view with signup management."""
import urllib.parse
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from models.database import db_session
from models.shift import Shift
from models.signup import Signup
from models.volunteer import Volunteer
from models.activity_log import ActivityLog
from services.stats import get_shift_fill_count, get_dashboard_stats


def _format_wa_phone(phone):
    """Return E.164-ish number for wa.me URLs (digits only, 1-prefix for US)."""
    digits = ''.join(c for c in (phone or '') if c.isdigit())
    if len(digits) == 10:
        return '1' + digits
    return digits if digits else None

shift_detail_bp = Blueprint('shift_detail', __name__)


@shift_detail_bp.route('/shifts/<int:shift_id>')
def detail(shift_id):
    shift = db_session.query(Shift).get(shift_id)
    if not shift:
        return 'Shift not found', 404

    filled = get_shift_fill_count(shift_id)

    # Get signups with volunteer names
    signups_raw = (db_session.query(Signup)
                   .filter(Signup.shift_id == shift_id)
                   .order_by(Signup.signed_up_at)
                   .all())

    signups = []
    signed_up_ids = set()
    for su in signups_raw:
        vol = db_session.query(Volunteer).get(su.volunteer_id)
        su.volunteer_name = vol.full_name if vol else f'Volunteer #{su.volunteer_id}'
        # Build per-volunteer WhatsApp reminder URL
        if vol and vol.phone:
            wa_num = _format_wa_phone(vol.phone)
            campus_short = shift.campus.split(' College')[0]
            msg = (
                f"Hi {vol.first_name}! Just a reminder about your "
                f"{shift.shift_type} shift at {campus_short} on "
                f"{shift.date.strftime('%A, %b %-d')} at "
                f"{shift.start_time.strftime('%-I:%M %p')}. "
                f"Thank you for volunteering!"
            )
            su.whatsapp_url = f"https://wa.me/{wa_num}?text={urllib.parse.quote(msg)}" if wa_num else None
        else:
            su.whatsapp_url = None
        signups.append(su)
        signed_up_ids.add(su.volunteer_id)

    # Available volunteers (active, not already signed up)
    available = (db_session.query(Volunteer)
                 .filter(Volunteer.status.in_(['active', 'new']))
                 .order_by(Volunteer.last_name)
                 .all())
    available = [v for v in available if v.id not in signed_up_ids]

    # Shareable signup link + WhatsApp broadcast URL
    base_url = request.host_url.rstrip('/')
    signup_url = f"{base_url}/v/signup/{shift_id}"
    campus_short = shift.campus.split(' College')[0]
    share_msg = (
        f"Hi! We need volunteers for a {shift.shift_type} shift at {campus_short} "
        f"on {shift.date.strftime('%A, %b %-d')} "
        f"({shift.start_time.strftime('%-I:%M %p')} – {shift.end_time.strftime('%-I:%M %p')}). "
        f"Sign up here: {signup_url}"
    )
    share_wa_url = f"https://wa.me/?text={urllib.parse.quote(share_msg)}"

    gap_count = get_dashboard_stats()['gaps']

    return render_template('pages/shift_detail.html',
                           active_page='shifts',
                           shift=shift,
                           filled=filled,
                           signups=signups,
                           available_volunteers=available,
                           gap_count=gap_count,
                           signup_url=signup_url,
                           share_wa_url=share_wa_url)


@shift_detail_bp.route('/api/shifts/<int:shift_id>/signup', methods=['POST'])
def add_signup(shift_id):
    shift = db_session.query(Shift).get(shift_id)
    if not shift:
        return jsonify({'error': 'Shift not found'}), 404

    data = request.json
    vol_id = data.get('volunteer_id')
    if not vol_id:
        return jsonify({'error': 'volunteer_id is required'}), 400

    # Check for existing signup
    existing = (db_session.query(Signup)
                .filter(Signup.volunteer_id == vol_id, Signup.shift_id == shift_id)
                .first())
    if existing:
        return jsonify({'error': 'Volunteer already signed up for this shift'}), 400

    signup = Signup(
        volunteer_id=vol_id,
        shift_id=shift_id,
        status='signed_up',
    )
    db_session.add(signup)

    vol = db_session.query(Volunteer).get(vol_id)
    vol_name = vol.full_name if vol else f'#{vol_id}'
    log = ActivityLog(
        action_type='signup',
        description=f'{vol_name} signed up for {shift.shift_type} at {shift.campus} on {shift.date}',
        volunteer_id=vol_id,
        shift_id=shift_id,
    )
    db_session.add(log)
    db_session.commit()

    return jsonify(signup.to_dict()), 201


@shift_detail_bp.route('/api/shifts/<int:shift_id>', methods=['PATCH'])
def update_shift(shift_id):
    shift = db_session.query(Shift).get(shift_id)
    if not shift:
        return jsonify({'error': 'Shift not found'}), 404
    data = request.json or {}
    if 'notes' in data:
        shift.notes = (data['notes'] or '').strip()[:500] or None
    db_session.commit()
    return jsonify(shift.to_dict())


@shift_detail_bp.route('/api/signups/<int:signup_id>', methods=['PATCH'])
def update_signup(signup_id):
    signup = db_session.query(Signup).get(signup_id)
    if not signup:
        return jsonify({'error': 'Signup not found'}), 404

    data = request.json
    new_status = data.get('status')
    if not new_status:
        return jsonify({'error': 'status is required'}), 400

    old_status = signup.status
    signup.status = new_status
    now = datetime.utcnow()

    # Track timestamp for each state transition
    if new_status == 'confirmed':
        signup.confirmed_at = now
    elif new_status == 'checked_in':
        signup.checked_in_at = now
    elif new_status == 'completed':
        signup.completed_at = now
    elif new_status == 'cancelled':
        signup.cancelled_at = now

    vol = db_session.query(Volunteer).get(signup.volunteer_id)
    vol_name = vol.full_name if vol else f'#{signup.volunteer_id}'
    log = ActivityLog(
        action_type='update',
        description=f'{vol_name} status: {old_status} → {new_status}',
        volunteer_id=signup.volunteer_id,
        shift_id=signup.shift_id,
    )
    db_session.add(log)
    db_session.commit()

    return jsonify(signup.to_dict())
