"""Outreach route — GET /outreach — email drafts."""
from flask import Blueprint, render_template, request, jsonify
from models.database import db_session
from models.prospect import Prospect
from models.outreach import OutreachEmail
from models.activity_log import ActivityLog
from services.email_generator import generate_outreach_email, generate_top_emails

outreach_bp = Blueprint('outreach', __name__)


@outreach_bp.route('/outreach')
def outreach():
    # Join with prospect to get company names
    emails_raw = db_session.query(OutreachEmail).all()
    emails = []
    for e in emails_raw:
        prospect = db_session.query(Prospect).get(e.prospect_id)
        email_dict = e.to_dict()
        email_dict['company_name'] = prospect.company_name if prospect else 'Unknown'
        email_dict['prospect_id'] = e.prospect_id
        emails.append(type('Email', (), email_dict)())

    return render_template('pages/outreach.html',
                           active_page='outreach',
                           emails=emails)


@outreach_bp.route('/api/generate-email/<int:prospect_id>', methods=['POST'])
def api_generate_email(prospect_id):
    """Generate outreach email for a prospect."""
    result = generate_outreach_email(prospect_id)
    if result is None:
        return jsonify({'error': 'Prospect not found'}), 404
    return jsonify(result)


@outreach_bp.route('/api/generate-top-emails', methods=['POST'])
def api_generate_top_emails():
    """Generate emails for top 15 prospects."""
    n = request.json.get('n', 15) if request.json else 15
    results = generate_top_emails(n)
    return jsonify({'message': f'Generated {len(results)} emails', 'count': len(results)})


@outreach_bp.route('/api/email/<int:email_id>', methods=['PATCH'])
def api_update_email(email_id):
    """Update an email (edit body, change status)."""
    email = db_session.query(OutreachEmail).get(email_id)
    if not email:
        return jsonify({'error': 'Not found'}), 404

    data = request.json
    if 'subject' in data:
        email.subject = data['subject']
    if 'body' in data:
        email.body = data['body']
        email.word_count = len(data['body'].split())
    if 'status' in data:
        old_status = email.status
        email.status = data['status']
        prospect = db_session.query(Prospect).get(email.prospect_id)
        if prospect and data['status'] == 'sent':
            prospect.pipeline_stage = '3-Outreach Sent'
        log = ActivityLog(
            prospect_id=email.prospect_id,
            action_type='email_status',
            description=f'Email status changed: {old_status}→{data["status"]}',
        )
        db_session.add(log)

    db_session.commit()
    return jsonify(email.to_dict())


@outreach_bp.route('/api/email/<int:email_id>/body', methods=['GET'])
def api_get_email_body(email_id):
    """Get email body text for clipboard copy."""
    email = db_session.query(OutreachEmail).get(email_id)
    if not email:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({'subject': email.subject, 'body': email.body})
