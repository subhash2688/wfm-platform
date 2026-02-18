"""Settings route — DB stats, seed, export, reset, campus management."""
from flask import Blueprint, render_template, request, jsonify
from models.database import db_session, Base, engine
from models.campus import Campus
from models.volunteer import Volunteer
from models.shift import Shift
from models.signup import Signup
from models.recurring_series import RecurringSeries
from models.activity_log import ActivityLog
from services.seed_data import seed_all, seed_campuses
from services.stats import get_dashboard_stats
from config import COLOR_PALETTE

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings')
def settings():
    stats = {
        'volunteers': db_session.query(Volunteer).count(),
        'shifts': db_session.query(Shift).count(),
        'signups': db_session.query(Signup).count(),
        'recurring': db_session.query(RecurringSeries).count(),
        'activities': db_session.query(ActivityLog).count(),
    }

    campuses = db_session.query(Campus).order_by(Campus.id).all()
    gap_count = get_dashboard_stats()['gaps']

    return render_template('pages/settings.html',
                           active_page='settings',
                           stats=stats,
                           campuses=campuses,
                           color_palette=COLOR_PALETTE,
                           gap_count=gap_count)


@settings_bp.route('/api/campuses')
def list_campuses():
    campuses = db_session.query(Campus).order_by(Campus.id).all()
    return jsonify({'campuses': [c.to_dict() for c in campuses]})


@settings_bp.route('/api/campuses', methods=['POST'])
def create_campus():
    data = request.json
    if not data.get('name'):
        return jsonify({'error': 'Campus name is required'}), 400

    existing = db_session.query(Campus).filter_by(name=data['name']).first()
    if existing:
        return jsonify({'error': f'Campus "{data["name"]}" already exists'}), 400

    campus = Campus(
        name=data['name'],
        city=data.get('city', ''),
        zip_code=data.get('zip_code', ''),
        region=data.get('region', ''),
        color=data.get('color', 'blue'),
    )
    db_session.add(campus)

    log = ActivityLog(
        action_type='create',
        description=f'Added campus: {campus.name}',
    )
    db_session.add(log)
    db_session.commit()

    return jsonify(campus.to_dict()), 201


@settings_bp.route('/api/campuses/<int:campus_id>', methods=['DELETE'])
def delete_campus(campus_id):
    campus = db_session.query(Campus).get(campus_id)
    if not campus:
        return jsonify({'error': 'Campus not found'}), 404

    name = campus.name
    db_session.delete(campus)

    log = ActivityLog(action_type='delete', description=f'Removed campus: {name}')
    db_session.add(log)
    db_session.commit()

    return jsonify({'message': f'Campus "{name}" removed'})


@settings_bp.route('/api/seed', methods=['POST'])
def seed():
    count = db_session.query(Volunteer).count()
    if count > 0:
        return jsonify({'error': 'Database is not empty. Reset first if you want to re-seed.'}), 400

    # Ensure campuses exist before seeding
    seed_campuses()
    vol_count, shift_count = seed_all()
    return jsonify({'message': f'Seeded {vol_count} volunteers and {shift_count} shifts'})


@settings_bp.route('/api/reset-db', methods=['POST'])
def reset_db():
    # Delete all data from all tables
    db_session.query(Signup).delete()
    db_session.query(Shift).delete()
    db_session.query(Volunteer).delete()
    db_session.query(RecurringSeries).delete()
    db_session.query(ActivityLog).delete()
    db_session.query(Campus).delete()
    db_session.commit()

    log = ActivityLog(action_type='reset', description='Database reset — all data cleared')
    db_session.add(log)
    db_session.commit()

    return jsonify({'message': 'Database reset. Use Seed to repopulate.'})
