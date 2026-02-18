"""Shifts route — list, create, delete shifts."""
from datetime import date, datetime
from flask import Blueprint, render_template, request, jsonify
from models.database import db_session
from models.campus import Campus
from models.shift import Shift
from models.signup import Signup
from models.activity_log import ActivityLog
from services.stats import get_shift_fill_count, get_dashboard_stats
from config import SHIFT_TYPES, SERVICE_TYPES

shifts_bp = Blueprint('shifts', __name__)


@shifts_bp.route('/shifts')
def shift_list():
    shifts = (db_session.query(Shift)
              .order_by(Shift.date.asc(), Shift.start_time.asc())
              .all())

    # Attach filled count to each shift
    for s in shifts:
        s.filled = get_shift_fill_count(s.id)

    campuses = db_session.query(Campus).order_by(Campus.id).all()
    campus_names = [c.name for c in campuses]
    campus_colors = {c.name: c.color for c in campuses}
    gap_count = get_dashboard_stats()['gaps']

    return render_template('pages/shifts.html',
                           active_page='shifts',
                           shifts=shifts,
                           campuses=campus_names,
                           campus_colors=campus_colors,
                           shift_types=SHIFT_TYPES,
                           service_types=SERVICE_TYPES,
                           gap_count=gap_count)


@shifts_bp.route('/api/shifts', methods=['POST'])
def create_shift():
    data = request.json
    if not data.get('campus') or not data.get('date') or not data.get('start_time') or not data.get('end_time'):
        return jsonify({'error': 'Campus, date, start_time, and end_time are required'}), 400

    from datetime import time as _time
    st_parts = data['start_time'].split(':')
    et_parts = data['end_time'].split(':')

    shift = Shift(
        campus=data['campus'],
        date=date.fromisoformat(data['date']),
        start_time=_time(int(st_parts[0]), int(st_parts[1])),
        end_time=_time(int(et_parts[0]), int(et_parts[1])),
        shift_type=data.get('shift_type', 'Serving'),
        service_type=data.get('service_type', 'Catered Meal'),
        required_count=int(data.get('required_count', 4)),
        status='scheduled',
    )
    db_session.add(shift)

    log = ActivityLog(
        action_type='create',
        description=f'Created shift: {shift.shift_type} at {shift.campus} on {data["date"]}',
        shift_id=None,  # Not yet flushed
    )
    db_session.add(log)
    db_session.commit()

    log.shift_id = shift.id
    db_session.commit()

    return jsonify(shift.to_dict()), 201


@shifts_bp.route('/api/shifts/<int:shift_id>', methods=['PATCH'])
def update_shift(shift_id):
    shift = db_session.query(Shift).get(shift_id)
    if not shift:
        return jsonify({'error': 'Shift not found'}), 404

    data = request.json
    for field in ('campus', 'shift_type', 'service_type', 'status', 'required_count', 'notes'):
        if field in data:
            if field == 'required_count':
                setattr(shift, field, int(data[field]))
            else:
                setattr(shift, field, data[field])

    log = ActivityLog(
        action_type='update',
        description=f'Updated shift #{shift.id}: {", ".join(data.keys())}',
        shift_id=shift.id,
    )
    db_session.add(log)
    db_session.commit()

    return jsonify(shift.to_dict())


@shifts_bp.route('/api/shifts/<int:shift_id>', methods=['DELETE'])
def delete_shift(shift_id):
    shift = db_session.query(Shift).get(shift_id)
    if not shift:
        return jsonify({'error': 'Shift not found'}), 404

    # Delete associated signups first
    db_session.query(Signup).filter(Signup.shift_id == shift_id).delete()

    desc = f'Deleted shift: {shift.shift_type} at {shift.campus} on {shift.date}'
    db_session.delete(shift)

    log = ActivityLog(action_type='delete', description=desc)
    db_session.add(log)
    db_session.commit()

    return jsonify({'message': 'Shift deleted'})
