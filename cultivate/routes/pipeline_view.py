"""Pipeline route — prospect table, scoring, import/export."""
import os
from flask import Blueprint, render_template, request, jsonify, send_file
from models.database import db_session, init_db, Base, engine
from models.prospect import Prospect
from models.foundation import FoundationData
from models.outreach import OutreachEmail
from models.grant_deadline import GrantDeadline
from models.contact import Contact
from models.activity_log import ActivityLog
from config import PIPELINE_STAGES, INDUSTRIES
from services.scoring import auto_score_prospect, auto_score_all
from services.import_excel import import_from_excel
from services.export_excel import export_to_excel

pipeline_view_bp = Blueprint('pipeline_view', __name__)


@pipeline_view_bp.route('/pipeline')
def index():
    prospects = (db_session.query(Prospect)
                 .order_by(Prospect.total_score.desc())
                 .all())

    industries_in_data = sorted(set(p.industry for p in prospects if p.industry))

    db_stats = {
        'prospects': len(prospects),
        'foundations': db_session.query(FoundationData).count(),
        'emails': db_session.query(OutreachEmail).count(),
        'deadlines': db_session.query(GrantDeadline).count(),
        'contacts': db_session.query(Contact).count(),
    }

    return render_template('pages/pipeline.html',
                           active_page='pipeline',
                           prospects=prospects,
                           stages=PIPELINE_STAGES,
                           industries=industries_in_data,
                           db_stats=db_stats)


# ─── Prospect APIs ───

@pipeline_view_bp.route('/api/prospect/<int:prospect_id>', methods=['PATCH'])
def update_prospect(prospect_id):
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
            changed.append(f'{field}: {old_val}->{value}')

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


@pipeline_view_bp.route('/api/prospect', methods=['POST'])
def add_prospect():
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


@pipeline_view_bp.route('/api/auto-score-all', methods=['POST'])
def api_auto_score_all():
    count = auto_score_all()
    return jsonify({'message': f'Auto-scored {count} prospects', 'updated': count})


@pipeline_view_bp.route('/api/auto-score/<int:prospect_id>', methods=['POST'])
def api_auto_score(prospect_id):
    prospect = db_session.query(Prospect).get(prospect_id)
    if not prospect:
        return jsonify({'error': 'Not found'}), 404
    auto_score_prospect(prospect)
    return jsonify(prospect.to_dict())


# ─── Import / Export ───

@pipeline_view_bp.route('/api/import-excel', methods=['POST'])
def api_import_excel():
    imported, skipped = import_from_excel()
    return jsonify({'message': f'Imported {imported} prospects ({skipped} skipped as duplicates)',
                    'imported': imported, 'skipped': skipped})


@pipeline_view_bp.route('/api/export/excel')
def api_export_excel():
    path = export_to_excel()
    return send_file(path, as_attachment=True,
                     download_name=os.path.basename(path),
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@pipeline_view_bp.route('/api/export/990-markdown')
def api_export_990_markdown():
    foundations = db_session.query(FoundationData).all()
    lines = ['# Foundation 990 Analysis\n']
    lines.append(f'Generated from WFM Corporate Fundraising Tool\n')
    lines.append(f'{len(foundations)} foundations analyzed\n\n---\n')
    for f in foundations:
        prospect = db_session.query(Prospect).get(f.prospect_id)
        company_name = prospect.company_name if prospect else 'Unknown'
        lines.append(f'\n## {f.foundation_name}\n')
        lines.append(f'**Company:** {company_name}')
        lines.append(f'**EIN:** {f.ein}')
        lines.append(f'**Tax Period:** {f.tax_period}')
        lines.append(f'**Total Assets:** ${f.total_assets:,.0f}' if f.total_assets else '**Total Assets:** N/A')
        lines.append(f'**Total Grants Paid:** ${f.total_grants_paid:,.0f}' if f.total_grants_paid else '**Total Grants Paid:** N/A')
        lines.append(f'**Fit Assessment:** {f.fit_assessment}')
        if f.pdf_url:
            lines.append(f'**990 PDF:** {f.pdf_url}')
        lines.append('\n---\n')
    content = '\n'.join(lines)
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               'foundation_990_analysis.md')
    with open(output_path, 'w') as fp:
        fp.write(content)
    return send_file(output_path, as_attachment=True, download_name='foundation_990_analysis.md',
                     mimetype='text/markdown')


@pipeline_view_bp.route('/api/export/emails-markdown')
def api_export_emails_markdown():
    emails = db_session.query(OutreachEmail).all()
    lines = ['# Outreach Emails\n']
    lines.append(f'{len(emails)} emails\n\n---\n')
    for e in emails:
        prospect = db_session.query(Prospect).get(e.prospect_id)
        company_name = prospect.company_name if prospect else 'Unknown'
        contact = prospect.contact_name if prospect else 'Community Affairs Team'
        lines.append(f'\n## {company_name}\n')
        lines.append(f'**Contact:** {contact or "Community Affairs Team"}')
        lines.append(f'**Status:** {e.status}')
        lines.append(f'**Subject:** {e.subject}\n')
        lines.append(f'```\n{e.body}\n```\n')
        if e.personalization_notes:
            lines.append(f'**Personalization notes:** {e.personalization_notes}\n')
        lines.append('\n---\n')
    content = '\n'.join(lines)
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               'outreach_emails.md')
    with open(output_path, 'w') as fp:
        fp.write(content)
    return send_file(output_path, as_attachment=True, download_name='outreach_emails.md',
                     mimetype='text/markdown')


@pipeline_view_bp.route('/api/reset-db', methods=['POST'])
def api_reset_db():
    Base.metadata.drop_all(bind=engine)
    init_db()
    imported, _ = import_from_excel()
    return jsonify({'message': f'Database reset. Re-imported {imported} prospects.'})
