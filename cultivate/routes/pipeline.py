"""Pipeline route — GET /pipeline — full prospect table with inline editing."""
from flask import Blueprint, render_template, request, jsonify
from models.database import db_session
from models.prospect import Prospect
from models.activity_log import ActivityLog
from config import PIPELINE_STAGES, INDUSTRIES
from services.scoring import auto_score_prospect, auto_score_all

pipeline_bp = Blueprint('pipeline', __name__)


@pipeline_bp.route('/pipeline')
def pipeline():
    prospects = (db_session.query(Prospect)
                 .order_by(Prospect.total_score.desc())
                 .all())

    # Get unique industries from data
    industries_in_data = sorted(set(p.industry for p in prospects if p.industry))

    return render_template('pages/pipeline.html',
                           active_page='pipeline',
                           prospects=prospects,
                           stages=PIPELINE_STAGES,
                           industries=industries_in_data)


@pipeline_bp.route('/api/prospect/<int:prospect_id>', methods=['PATCH'])
def update_prospect(prospect_id):
    """Inline update a prospect field."""
    prospect = db_session.query(Prospect).get(prospect_id)
    if not prospect:
        return jsonify({'error': 'Not found'}), 404

    data = request.json
    changed = []

    for field, value in data.items():
        if hasattr(prospect, field):
            old_val = getattr(prospect, field)
            if field in ('alignment_score', 'proximity_score', 'capacity_score'):
                value = int(value)
                if value < 0 or value > 5:
                    continue
            elif field in ('ask_amount', 'amount_received'):
                value = float(value) if value else 0
            setattr(prospect, field, value)
            changed.append(f'{field}: {old_val}→{value}')

    if any(f in data for f in ('alignment_score', 'proximity_score', 'capacity_score')):
        prospect.recalculate_total()

    if changed:
        log = ActivityLog(
            prospect_id=prospect.id,
            action_type='edit',
            description=f'Updated {prospect.company_name}: {", ".join(changed)}',
        )
        db_session.add(log)
        db_session.commit()

    return jsonify(prospect.to_dict())


@pipeline_bp.route('/api/prospect', methods=['POST'])
def add_prospect():
    """Add a new prospect."""
    data = request.json
    if not data.get('company_name'):
        return jsonify({'error': 'Company name is required'}), 400

    existing = db_session.query(Prospect).filter_by(company_name=data['company_name']).first()
    if existing:
        return jsonify({'error': 'Company already exists'}), 400

    prospect = Prospect(
        company_name=data['company_name'],
        industry=data.get('industry'),
        hq_city=data.get('hq_city'),
        nearest_campus=data.get('nearest_campus'),
        focus_areas=data.get('focus_areas'),
        foundation_name=data.get('foundation_name'),
        pipeline_stage='1-Research',
    )
    auto_score_prospect(prospect, commit=False)
    db_session.add(prospect)

    log = ActivityLog(
        action_type='import',
        description=f'Manually added prospect: {prospect.company_name}',
    )
    db_session.add(log)
    db_session.commit()

    return jsonify(prospect.to_dict()), 201


@pipeline_bp.route('/api/auto-score-all', methods=['POST'])
def api_auto_score_all():
    """Auto-score all prospects."""
    count = auto_score_all()
    return jsonify({'message': f'Auto-scored {count} prospects', 'updated': count})


@pipeline_bp.route('/api/auto-score/<int:prospect_id>', methods=['POST'])
def api_auto_score(prospect_id):
    """Auto-score a single prospect."""
    prospect = db_session.query(Prospect).get(prospect_id)
    if not prospect:
        return jsonify({'error': 'Not found'}), 404
    auto_score_prospect(prospect)
    return jsonify(prospect.to_dict())
