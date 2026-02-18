"""Volunteer-facing mobile web app routes — /v/ prefix."""
import json
import os
import time
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, g, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from models.database import db_session
from models.volunteer import Volunteer
from models.shift import Shift
from models.signup import Signup
from models.activity_log import ActivityLog
from services.sms_service import send_otp, verify_otp, normalize_phone
from services.volunteer_auth import volunteer_login_required, get_current_volunteer
from services.stats import get_volunteer_stats, get_shift_fill_count, get_volunteer_streak
from services.badges import get_earned_badges
from config import SMS_DEV_MODE, DEFAULT_CAMPUSES, SHIFT_TYPES, SHIFT_TYPE_INFO, MEALS_PER_SHIFT, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_PHOTO_SIZE, DAYS_OF_WEEK, AVAILABILITY_SLOTS

volunteer_bp = Blueprint('volunteer', __name__, url_prefix='/v')


@volunteer_bp.before_request
def update_last_seen():
    """Update volunteer's last_seen timestamp on each app access (max once per hour)."""
    from services.volunteer_auth import get_current_volunteer
    vol = get_current_volunteer()
    if vol:
        now = datetime.utcnow()
        if vol.last_seen is None or (now - vol.last_seen).total_seconds() > 3600:
            vol.last_seen = now
            db_session.commit()


# ── Auth routes (no login required) ──────────────────────────────

@volunteer_bp.route('/login', methods=['GET'])
def login():
    return render_template('volunteer/login.html')


@volunteer_bp.route('/login', methods=['POST'])
def login_post():
    phone = request.form.get('phone', '')
    phone_digits = normalize_phone(phone)
    if len(phone_digits) < 10:
        return render_template('volunteer/login.html', error='Please enter a valid phone number.')

    result = send_otp(phone)
    session['auth_phone'] = phone_digits
    session['dev_code'] = result.get('dev_code')
    return redirect(url_for('volunteer.verify'))


@volunteer_bp.route('/verify', methods=['GET'])
def verify():
    phone = session.get('auth_phone')
    if not phone:
        return redirect(url_for('volunteer.login'))
    dev_code = session.get('dev_code') if SMS_DEV_MODE else None
    return render_template('volunteer/verify.html', dev_code=dev_code)


@volunteer_bp.route('/verify', methods=['POST'])
def verify_post():
    phone = session.get('auth_phone')
    if not phone:
        return redirect(url_for('volunteer.login'))

    # Collect 6 digit fields into one code string
    code = request.form.get('code', '')
    if not code:
        digits = [request.form.get(f'd{i}', '') for i in range(1, 7)]
        code = ''.join(digits)

    if not verify_otp(phone, code):
        dev_code = session.get('dev_code') if SMS_DEV_MODE else None
        return render_template('volunteer/verify.html', error='Invalid or expired code. Please try again.', dev_code=dev_code)

    # OTP verified — look up volunteer by normalized phone
    volunteer = (db_session.query(Volunteer)
                 .filter(Volunteer.phone == phone)
                 .first())

    # Also try matching against stored phone formats
    if not volunteer:
        all_vols = db_session.query(Volunteer).all()
        for v in all_vols:
            if normalize_phone(v.phone) == phone:
                volunteer = v
                break

    if volunteer:
        session['volunteer_id'] = volunteer.id
        session.pop('auth_phone', None)
        session.pop('dev_code', None)
        next_url = session.pop('next_url', '/v/')
        return redirect(next_url)
    else:
        # New volunteer — send to registration
        return redirect(url_for('volunteer.register'))


@volunteer_bp.route('/register', methods=['GET'])
def register():
    phone = session.get('auth_phone')
    if not phone:
        return redirect(url_for('volunteer.login'))
    campuses = [c['name'] for c in DEFAULT_CAMPUSES]
    return render_template('volunteer/register.html', phone=phone, campuses=campuses, shift_types=SHIFT_TYPES)


@volunteer_bp.route('/register', methods=['POST'])
def register_post():
    phone = session.get('auth_phone')
    if not phone:
        return redirect(url_for('volunteer.login'))

    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    selected_campuses = request.form.getlist('campuses')
    selected_shift_types = request.form.getlist('shift_types')
    is_youth = request.form.get('is_youth') == 'yes'

    if not first_name or not last_name:
        campuses = [c['name'] for c in DEFAULT_CAMPUSES]
        return render_template('volunteer/register.html', phone=phone, campuses=campuses,
                               shift_types=SHIFT_TYPES,
                               error='Please enter your first and last name.')

    volunteer = Volunteer(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        preferred_campuses=json.dumps(selected_campuses) if selected_campuses else '[]',
        preferred_shift_types=json.dumps(selected_shift_types) if selected_shift_types else '[]',
        is_youth=is_youth,
        status='active',
    )
    db_session.add(volunteer)
    db_session.flush()

    log = ActivityLog(
        action_type='create',
        description=f'Volunteer {first_name} {last_name} self-registered via mobile app',
        volunteer_id=volunteer.id,
    )
    db_session.add(log)
    db_session.commit()

    session['volunteer_id'] = volunteer.id
    session.pop('auth_phone', None)
    session.pop('dev_code', None)
    next_url = session.pop('next_url', '/v/')
    return redirect(next_url)


@volunteer_bp.route('/logout')
def logout():
    session.pop('volunteer_id', None)
    session.pop('auth_phone', None)
    session.pop('dev_code', None)
    return redirect(url_for('volunteer.login'))


# ── Direct signup link (handles auth redirect) ──────────────────

@volunteer_bp.route('/signup/<int:shift_id>')
def direct_signup(shift_id):
    volunteer = get_current_volunteer()
    if volunteer:
        return redirect(url_for('volunteer.shift_detail', shift_id=shift_id))
    session['next_url'] = f'/v/shifts/{shift_id}'
    return redirect(url_for('volunteer.login'))


# ── Protected routes ─────────────────────────────────────────────

@volunteer_bp.route('/')
@volunteer_login_required
def shifts_browse():
    today = date.today()
    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)
    campus_filter = request.args.get('campus', 'all')

    # Get ALL upcoming scheduled shifts (unfiltered) for contextual sections
    all_shifts = (db_session.query(Shift)
                  .filter(Shift.date >= today, Shift.status == 'scheduled')
                  .order_by(Shift.date, Shift.start_time)
                  .all())

    all_shift_data = []
    for s in all_shifts:
        fill = get_shift_fill_count(s.id)
        my_signup = (db_session.query(Signup)
                     .filter(Signup.shift_id == s.id,
                             Signup.volunteer_id == g.volunteer.id,
                             Signup.status.in_(['signed_up', 'confirmed', 'checked_in']))
                     .first())
        all_shift_data.append({
            'shift': s,
            'filled': fill,
            'spots_left': max(0, s.required_count - fill),
            'my_signup': my_signup,
            'is_today': s.date == today,
        })

    # Apply campus filter for main list
    if campus_filter != 'all':
        shift_data = [item for item in all_shift_data if item['shift'].campus == campus_filter]
    else:
        shift_data = all_shift_data

    # Contextual sections — always use full unfiltered data
    today_items = [item for item in all_shift_data if item['is_today'] and item['my_signup']]
    tomorrow_items = [item for item in all_shift_data if item['shift'].date == tomorrow and item['my_signup']]
    urgent_items = [item for item in all_shift_data
                    if item['shift'].date <= day_after
                    and item['spots_left'] > 0
                    and item['filled'] < item['shift'].required_count * 0.5
                    and not item['my_signup']]

    campuses = [c['name'] for c in DEFAULT_CAMPUSES]
    prefs_stale = (g.volunteer.updated_at is None or
                   g.volunteer.updated_at < datetime.utcnow() - timedelta(days=30))
    return render_template('volunteer/shifts.html',
                           shift_data=shift_data,
                           campuses=campuses,
                           campus_filter=campus_filter,
                           prefs_stale=prefs_stale,
                           today_items=today_items,
                           tomorrow_items=tomorrow_items,
                           urgent_items=urgent_items,
                           active_tab='shifts',
                           volunteer=g.volunteer)


@volunteer_bp.route('/shifts/<int:shift_id>')
@volunteer_login_required
def shift_detail(shift_id):
    today = date.today()
    shift = db_session.query(Shift).get(shift_id)
    if not shift:
        return redirect(url_for('volunteer.shifts_browse'))

    fill = get_shift_fill_count(shift.id)
    my_signup = (db_session.query(Signup)
                 .filter(Signup.shift_id == shift.id,
                         Signup.volunteer_id == g.volunteer.id,
                         Signup.status.in_(['signed_up', 'confirmed', 'checked_in']))
                 .first())

    # Who else is coming
    attendees = (db_session.query(Volunteer)
                 .join(Signup, Signup.volunteer_id == Volunteer.id)
                 .filter(Signup.shift_id == shift.id,
                         Signup.status.in_(['signed_up', 'confirmed', 'checked_in']))
                 .order_by(Volunteer.first_name)
                 .all())
    other_attendees = [v for v in attendees if v.id != g.volunteer.id]

    shift_info = SHIFT_TYPE_INFO.get(shift.shift_type)

    return render_template('volunteer/shift_detail.html',
                           shift=shift,
                           filled=fill,
                           spots_left=max(0, shift.required_count - fill),
                           my_signup=my_signup,
                           is_today=shift.date == today,
                           is_past=shift.date < today,
                           other_attendees=other_attendees,
                           shift_info=shift_info,
                           active_tab='shifts',
                           volunteer=g.volunteer)


@volunteer_bp.route('/api/signup/<int:shift_id>', methods=['POST'])
@volunteer_login_required
def api_signup(shift_id):
    shift = db_session.query(Shift).get(shift_id)
    if not shift:
        return jsonify({'error': 'Shift not found'}), 404

    # Check for duplicate
    existing = (db_session.query(Signup)
                .filter(Signup.shift_id == shift_id,
                        Signup.volunteer_id == g.volunteer.id,
                        Signup.status.in_(['signed_up', 'confirmed', 'checked_in']))
                .first())
    if existing:
        return jsonify({'error': 'Already signed up for this shift'}), 400

    # Check spots available
    fill = get_shift_fill_count(shift_id)
    if fill >= shift.required_count:
        return jsonify({'error': 'This shift is full'}), 400

    signup = Signup(
        volunteer_id=g.volunteer.id,
        shift_id=shift_id,
        status='signed_up',
    )
    db_session.add(signup)

    log = ActivityLog(
        action_type='signup',
        description=f'{g.volunteer.full_name} signed up for {shift.campus} shift on {shift.date}',
        volunteer_id=g.volunteer.id,
        shift_id=shift_id,
    )
    db_session.add(log)
    db_session.commit()

    return jsonify({'success': True, 'message': 'Signed up successfully!'})


@volunteer_bp.route('/api/cancel/<int:signup_id>', methods=['POST'])
@volunteer_login_required
def api_cancel(signup_id):
    signup = db_session.query(Signup).get(signup_id)
    if not signup or signup.volunteer_id != g.volunteer.id:
        return jsonify({'error': 'Signup not found'}), 404

    if signup.status in ('cancelled', 'completed', 'no_show'):
        return jsonify({'error': 'Cannot cancel this signup'}), 400

    signup.status = 'cancelled'
    signup.cancelled_at = datetime.utcnow()

    shift = db_session.query(Shift).get(signup.shift_id)
    log = ActivityLog(
        action_type='update',
        description=f'{g.volunteer.full_name} cancelled signup for {shift.campus} shift on {shift.date}',
        volunteer_id=g.volunteer.id,
        shift_id=signup.shift_id,
    )
    db_session.add(log)
    db_session.commit()

    return jsonify({'success': True, 'message': 'Signup cancelled.'})


@volunteer_bp.route('/api/checkin/<int:shift_id>', methods=['POST'])
@volunteer_login_required
def api_checkin(shift_id):
    shift = db_session.query(Shift).get(shift_id)
    if not shift:
        return jsonify({'error': 'Shift not found'}), 404

    today = date.today()
    if shift.date != today:
        return jsonify({'error': 'Check-in is only available on the day of the shift'}), 400

    signup = (db_session.query(Signup)
              .filter(Signup.shift_id == shift_id,
                      Signup.volunteer_id == g.volunteer.id,
                      Signup.status.in_(['signed_up', 'confirmed']))
              .first())
    if not signup:
        return jsonify({'error': 'No active signup found for this shift'}), 404

    signup.status = 'checked_in'
    signup.checked_in_at = datetime.utcnow()

    log = ActivityLog(
        action_type='check_in',
        description=f'{g.volunteer.full_name} checked in for {shift.campus} shift',
        volunteer_id=g.volunteer.id,
        shift_id=shift_id,
    )
    db_session.add(log)
    db_session.commit()

    return jsonify({'success': True, 'message': "You're checked in! Thank you!"})


@volunteer_bp.route('/my-shifts')
@volunteer_login_required
def my_shifts():
    today = date.today()
    vid = g.volunteer.id

    # Get all non-cancelled signups with their shifts
    signups = (db_session.query(Signup, Shift)
               .join(Shift, Signup.shift_id == Shift.id)
               .filter(Signup.volunteer_id == vid,
                       Signup.status != 'cancelled')
               .order_by(Shift.date.desc())
               .all())

    upcoming = []
    past = []
    for signup, shift in signups:
        entry = {'signup': signup, 'shift': shift}
        if shift.date >= today and shift.status == 'scheduled':
            upcoming.append(entry)
        else:
            past.append(entry)

    # Sort upcoming by date ascending
    upcoming.sort(key=lambda x: x['shift'].date)

    # Stats
    stats = get_volunteer_stats(vid)
    streak = get_volunteer_streak(vid)
    badges = get_earned_badges(stats['total_shifts'])

    # Post-shift acknowledgment — most recent completed shift within last 7 days
    week_ago = today - timedelta(days=7)
    recent_completion = None
    for entry in past:
        if (entry['signup'].status in ('completed', 'checked_in')
                and entry['shift'].date >= week_ago):
            vol_count = get_shift_fill_count(entry['shift'].id)
            recent_completion = {
                'shift': entry['shift'],
                'vol_count': vol_count,
                'meals': MEALS_PER_SHIFT,
            }
            break

    return render_template('volunteer/my_shifts.html',
                           upcoming=upcoming,
                           past=past,
                           stats=stats,
                           streak=streak,
                           badges=badges,
                           recent_completion=recent_completion,
                           active_tab='my_shifts',
                           volunteer=g.volunteer)


@volunteer_bp.route('/profile')
@volunteer_login_required
def profile():
    vid = g.volunteer.id
    stats = get_volunteer_stats(vid)
    badges = get_earned_badges(stats['total_shifts'])
    campuses = [c['name'] for c in DEFAULT_CAMPUSES]

    return render_template('volunteer/profile.html',
                           stats=stats,
                           badges=badges,
                           campuses=campuses,
                           shift_types=SHIFT_TYPES,
                           days_of_week=DAYS_OF_WEEK,
                           availability_slots=AVAILABILITY_SLOTS,
                           active_tab='profile',
                           volunteer=g.volunteer)


@volunteer_bp.route('/api/profile', methods=['POST'])
@volunteer_login_required
def api_profile_update():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    v = g.volunteer
    if 'first_name' in data:
        v.first_name = data['first_name'].strip()
    if 'last_name' in data:
        v.last_name = data['last_name'].strip()
    if 'preferred_campuses' in data:
        v.set_campuses(data['preferred_campuses'])
    if 'preferred_shift_types' in data:
        v.set_shift_types(data['preferred_shift_types'])
    if 'is_youth' in data:
        v.is_youth = bool(data['is_youth'])
    if 'availability' in data and isinstance(data['availability'], dict):
        v.set_availability(data['availability'])

    v.updated_at = datetime.utcnow()
    db_session.commit()

    return jsonify({'success': True, 'message': 'Profile updated!'})


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@volunteer_bp.route('/api/photo', methods=['POST'])
@volunteer_login_required
def api_photo_upload():
    if 'photo' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not _allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Use PNG, JPG, or WebP.'}), 400

    # Check file size
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_PHOTO_SIZE:
        return jsonify({'error': 'File too large. Maximum 5 MB.'}), 400

    v = g.volunteer
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f'vol_{v.id}_{int(time.time())}.{ext}'

    # Delete old photo if exists
    if v.photo:
        old_path = os.path.join(UPLOAD_FOLDER, v.photo)
        if os.path.exists(old_path):
            os.remove(old_path)

    file.save(os.path.join(UPLOAD_FOLDER, filename))
    v.photo = filename
    db_session.commit()

    photo_url = url_for('static', filename=f'uploads/volunteers/{filename}')
    return jsonify({'success': True, 'photo_url': photo_url})
