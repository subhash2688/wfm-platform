"""Grant deadlines / opportunities route — GET /deadlines."""
from flask import Blueprint, render_template, request, jsonify
from models.database import db_session
from models.grant_deadline import GrantDeadline

deadlines_bp = Blueprint('deadlines', __name__)


@deadlines_bp.route('/deadlines')
def deadlines():
    all_deadlines = db_session.query(GrantDeadline).all()

    # Separate by priority and type
    high_priority = [d for d in all_deadlines if d.priority == 'High']
    medium_priority = [d for d in all_deadlines if d.priority == 'Medium']
    low_priority = [d for d in all_deadlines if d.priority == 'Low']

    # Count by grant type
    type_counts = {}
    for d in all_deadlines:
        gt = d.grant_type or 'Cash'
        type_counts[gt] = type_counts.get(gt, 0) + 1

    # Count by status
    status_counts = {}
    for d in all_deadlines:
        s = d.status or 'Not Started'
        status_counts[s] = status_counts.get(s, 0) + 1

    return render_template('pages/deadlines.html',
                           active_page='deadlines',
                           deadlines=all_deadlines,
                           high_priority=high_priority,
                           medium_priority=medium_priority,
                           low_priority=low_priority,
                           type_counts=type_counts,
                           status_counts=status_counts)


@deadlines_bp.route('/api/deadline', methods=['POST'])
def add_deadline():
    data = request.json
    dl = GrantDeadline(
        company_name=data.get('company_name'),
        program_name=data.get('program_name'),
        focus_area=data.get('focus_area'),
        deadline=data.get('deadline'),
        award_range=data.get('award_range'),
        application_url=data.get('application_url'),
        grant_type=data.get('grant_type', 'Cash'),
        cycle=data.get('cycle'),
        eligibility=data.get('eligibility'),
        geographic_focus=data.get('geographic_focus'),
        application_process=data.get('application_process'),
        required_documents=data.get('required_documents'),
        contact_info=data.get('contact_info'),
        priority=data.get('priority', 'Medium'),
        status='Not Started',
    )
    db_session.add(dl)
    db_session.commit()
    return jsonify(dl.to_dict()), 201


@deadlines_bp.route('/api/deadline/<int:deadline_id>', methods=['PATCH'])
def update_deadline(deadline_id):
    dl = db_session.query(GrantDeadline).get(deadline_id)
    if not dl:
        return jsonify({'error': 'Not found'}), 404

    data = request.json
    for field in ('company_name', 'program_name', 'focus_area', 'deadline',
                  'award_range', 'application_url', 'status', 'notes',
                  'grant_type', 'cycle', 'eligibility', 'geographic_focus',
                  'application_process', 'required_documents', 'contact_info', 'priority'):
        if field in data:
            setattr(dl, field, data[field])

    db_session.commit()
    return jsonify(dl.to_dict())


@deadlines_bp.route('/api/deadline/<int:deadline_id>', methods=['DELETE'])
def delete_deadline(deadline_id):
    dl = db_session.query(GrantDeadline).get(deadline_id)
    if not dl:
        return jsonify({'error': 'Not found'}), 404
    db_session.delete(dl)
    db_session.commit()
    return jsonify({'ok': True})
