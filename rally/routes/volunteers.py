"""Volunteers route — list, create, update, delete, CSV export."""
import json
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, Response
from models.database import db_session
from models.campus import Campus
from models.volunteer import Volunteer
from models.signup import Signup
from models.activity_log import ActivityLog
from services.stats import get_volunteer_stats, get_dashboard_stats
from services.export import export_volunteers_csv

volunteers_bp = Blueprint('volunteers', __name__)


@volunteers_bp.route('/volunteers')
def volunteer_list():
    volunteers = (db_session.query(Volunteer)
                  .order_by(Volunteer.last_name)
                  .all())

    # Attach stats to each volunteer
    for v in volunteers:
        v.stats = get_volunteer_stats(v.id)

    campuses = db_session.query(Campus).order_by(Campus.id).all()
    campus_names = [c.name for c in campuses]
    campus_colors = {c.name: c.color for c in campuses}
    gap_count = get_dashboard_stats()['gaps']

    return render_template('pages/volunteers.html',
                           active_page='volunteers',
                           volunteers=volunteers,
                           campuses=campus_names,
                           campus_colors=campus_colors,
                           gap_count=gap_count,
                           now=datetime.utcnow())


@volunteers_bp.route('/api/volunteers', methods=['POST'])
def create_volunteer():
    data = request.json
    if not data.get('first_name') or not data.get('last_name') or not data.get('phone'):
        return jsonify({'error': 'first_name, last_name, and phone are required'}), 400

    # Check for duplicate phone
    existing = db_session.query(Volunteer).filter_by(phone=data['phone']).first()
    if existing:
        return jsonify({'error': f'A volunteer with phone {data["phone"]} already exists'}), 400

    vol = Volunteer(
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data['phone'],
        email=data.get('email'),
        preferred_campuses=json.dumps(data.get('preferred_campuses', [])),
        is_youth=bool(data.get('is_youth', False)),
        status='new',
    )
    db_session.add(vol)

    log = ActivityLog(
        action_type='create',
        description=f'Added volunteer: {vol.first_name} {vol.last_name}',
    )
    db_session.add(log)
    db_session.commit()

    log.volunteer_id = vol.id
    db_session.commit()

    return jsonify(vol.to_dict()), 201


@volunteers_bp.route('/api/volunteers/<int:vol_id>', methods=['PATCH'])
def update_volunteer(vol_id):
    vol = db_session.query(Volunteer).get(vol_id)
    if not vol:
        return jsonify({'error': 'Volunteer not found'}), 404

    data = request.json
    for field in ('first_name', 'last_name', 'phone', 'email', 'status', 'notes'):
        if field in data:
            setattr(vol, field, data[field])

    if 'is_youth' in data:
        vol.is_youth = bool(data['is_youth'])

    if 'preferred_campuses' in data:
        vol.preferred_campuses = json.dumps(data['preferred_campuses'])

    if 'availability' in data:
        vol.availability = json.dumps(data['availability'])

    log = ActivityLog(
        action_type='update',
        description=f'Updated {vol.full_name}: {", ".join(data.keys())}',
        volunteer_id=vol.id,
    )
    db_session.add(log)
    db_session.commit()

    return jsonify(vol.to_dict())


@volunteers_bp.route('/api/volunteers/<int:vol_id>', methods=['DELETE'])
def delete_volunteer(vol_id):
    vol = db_session.query(Volunteer).get(vol_id)
    if not vol:
        return jsonify({'error': 'Volunteer not found'}), 404

    name = vol.full_name
    db_session.query(Signup).filter(Signup.volunteer_id == vol_id).delete()
    db_session.delete(vol)

    log = ActivityLog(action_type='delete', description=f'Removed volunteer: {name}')
    db_session.add(log)
    db_session.commit()

    return jsonify({'message': f'Volunteer {name} removed'})


@volunteers_bp.route('/api/export/csv')
def export_csv():
    csv_data = export_volunteers_csv()
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=wfm_volunteers.csv'},
    )
