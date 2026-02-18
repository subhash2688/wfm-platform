"""Actions route — task checklist, grants, contacts, outreach, events."""
from datetime import date, datetime
from flask import Blueprint, render_template, request, jsonify
from models.database import db_session
from models.prospect import Prospect
from models.contact import Contact
from models.grant_deadline import GrantDeadline
from models.outreach import OutreachEmail
from models.action_item import ActionItem
from models.event import Event
from models.activity_log import ActivityLog
from config import PIPELINE_STAGES
from services.email_generator import generate_outreach_email, generate_top_emails

actions_bp = Blueprint('actions', __name__)


@actions_bp.route('/actions')
def actions():
    # Action items, sorted: in_progress first, then todo, then done
    status_order = {'in_progress': 0, 'todo': 1, 'done': 2}
    all_actions = db_session.query(ActionItem).all()
    all_actions.sort(key=lambda a: (status_order.get(a.status, 1), -(a.priority == 'high'), a.due_date or date(9999, 12, 31)))

    # Build prospect name lookup
    prospects = db_session.query(Prospect).all()
    prospect_map = {p.id: p.company_name for p in prospects}

    # Annotate actions with company name
    for a in all_actions:
        a._company = prospect_map.get(a.prospect_id, '')

    # Grants
    all_grants = db_session.query(GrantDeadline).all()
    high_grants = [g for g in all_grants if g.priority == 'High']
    med_grants = [g for g in all_grants if g.priority == 'Medium']
    low_grants = [g for g in all_grants if g.priority == 'Low']

    # Contacts
    contacts = db_session.query(Contact).all()
    for c in contacts:
        c._company = prospect_map.get(c.prospect_id, '')

    # Outreach emails
    emails_raw = db_session.query(OutreachEmail).all()
    emails = []
    for e in emails_raw:
        ed = e.to_dict()
        ed['company_name'] = prospect_map.get(e.prospect_id, 'Unknown')
        emails.append(type('Email', (), ed)())

    # Events
    events = db_session.query(Event).order_by(Event.date.asc()).all()

    # Stats
    action_stats = {
        'total': len(all_actions),
        'done': sum(1 for a in all_actions if a.status == 'done'),
        'todo': sum(1 for a in all_actions if a.status in ('todo', 'in_progress')),
    }

    return render_template('pages/actions.html',
                           active_page='actions',
                           actions=all_actions,
                           action_stats=action_stats,
                           grants=all_grants,
                           high_grants=high_grants,
                           med_grants=med_grants,
                           low_grants=low_grants,
                           contacts=contacts,
                           emails=emails,
                           events=events,
                           prospects=prospects,
                           stages=PIPELINE_STAGES,
                           today=date.today())


# ─── Action Items CRUD ───

@actions_bp.route('/api/action', methods=['POST'])
def add_action():
    data = request.json
    item = ActionItem(
        prospect_id=data.get('prospect_id') or None,
        description=data.get('description', ''),
        action_type=data.get('action_type', 'research'),
        priority=data.get('priority', 'medium'),
        status='todo',
        due_date=date.fromisoformat(data['due_date']) if data.get('due_date') else None,
        notes=data.get('notes'),
    )
    db_session.add(item)
    db_session.commit()
    return jsonify(item.to_dict()), 201


@actions_bp.route('/api/action/<int:action_id>', methods=['PATCH'])
def update_action(action_id):
    item = db_session.query(ActionItem).get(action_id)
    if not item:
        return jsonify({'error': 'Not found'}), 404

    data = request.json
    if 'status' in data:
        item.status = data['status']
        if data['status'] == 'done':
            item.completed_date = date.today()
        elif data['status'] in ('todo', 'in_progress'):
            item.completed_date = None
    if 'description' in data:
        item.description = data['description']
    if 'priority' in data:
        item.priority = data['priority']
    if 'action_type' in data:
        item.action_type = data['action_type']
    if 'due_date' in data:
        item.due_date = date.fromisoformat(data['due_date']) if data['due_date'] else None
    if 'notes' in data:
        item.notes = data['notes']

    db_session.commit()
    return jsonify(item.to_dict())


@actions_bp.route('/api/action/<int:action_id>', methods=['DELETE'])
def delete_action(action_id):
    item = db_session.query(ActionItem).get(action_id)
    if not item:
        return jsonify({'error': 'Not found'}), 404
    db_session.delete(item)
    db_session.commit()
    return jsonify({'ok': True})


# ─── Contacts CRUD ───

@actions_bp.route('/api/contact', methods=['POST'])
def add_contact():
    data = request.json
    contact = Contact(
        prospect_id=data.get('prospect_id'),
        name=data.get('name'),
        title=data.get('title'),
        email=data.get('email'),
        linkedin_url=data.get('linkedin_url'),
        is_primary=data.get('is_primary', False),
        source=data.get('source'),
    )
    db_session.add(contact)
    db_session.commit()
    return jsonify(contact.to_dict()), 201


@actions_bp.route('/api/contact/<int:contact_id>', methods=['PATCH'])
def update_contact(contact_id):
    contact = db_session.query(Contact).get(contact_id)
    if not contact:
        return jsonify({'error': 'Not found'}), 404
    data = request.json
    for field in ('name', 'title', 'email', 'linkedin_url', 'source', 'is_primary'):
        if field in data:
            setattr(contact, field, data[field])
    db_session.commit()
    return jsonify(contact.to_dict())


@actions_bp.route('/api/contact/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    contact = db_session.query(Contact).get(contact_id)
    if not contact:
        return jsonify({'error': 'Not found'}), 404
    db_session.delete(contact)
    db_session.commit()
    return jsonify({'ok': True})


# ─── Events CRUD ───

@actions_bp.route('/api/event', methods=['POST'])
def add_event():
    data = request.json
    event = Event(
        name=data.get('name', ''),
        event_type=data.get('event_type', 'networking'),
        date=date.fromisoformat(data['date']) if data.get('date') else None,
        end_date=date.fromisoformat(data['end_date']) if data.get('end_date') else None,
        location=data.get('location'),
        url=data.get('url'),
        description=data.get('description'),
        relevance=data.get('relevance'),
        status='upcoming',
    )
    db_session.add(event)
    db_session.commit()
    return jsonify(event.to_dict()), 201


@actions_bp.route('/api/event/<int:event_id>', methods=['PATCH'])
def update_event(event_id):
    event = db_session.query(Event).get(event_id)
    if not event:
        return jsonify({'error': 'Not found'}), 404
    data = request.json
    for field in ('name', 'event_type', 'location', 'url', 'description', 'relevance', 'status'):
        if field in data:
            setattr(event, field, data[field])
    if 'date' in data:
        event.date = date.fromisoformat(data['date']) if data['date'] else None
    if 'end_date' in data:
        event.end_date = date.fromisoformat(data['end_date']) if data['end_date'] else None
    db_session.commit()
    return jsonify(event.to_dict())


@actions_bp.route('/api/event/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = db_session.query(Event).get(event_id)
    if not event:
        return jsonify({'error': 'Not found'}), 404
    db_session.delete(event)
    db_session.commit()
    return jsonify({'ok': True})


# ─── Outreach emails (moved from old outreach route) ───

@actions_bp.route('/api/generate-email/<int:prospect_id>', methods=['POST'])
def api_generate_email(prospect_id):
    result = generate_outreach_email(prospect_id)
    if result is None:
        return jsonify({'error': 'Prospect not found'}), 404
    return jsonify(result)


@actions_bp.route('/api/generate-top-emails', methods=['POST'])
def api_generate_top_emails():
    n = request.json.get('n', 15) if request.json else 15
    results = generate_top_emails(n)
    return jsonify({'message': f'Generated {len(results)} emails', 'count': len(results)})


@actions_bp.route('/api/email/<int:email_id>', methods=['PATCH'])
def api_update_email(email_id):
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
            description=f'Email status changed: {old_status} -> {data["status"]}',
        )
        db_session.add(log)
    db_session.commit()
    return jsonify(email.to_dict())


@actions_bp.route('/api/email/<int:email_id>/body', methods=['GET'])
def api_get_email_body(email_id):
    email = db_session.query(OutreachEmail).get(email_id)
    if not email:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({'subject': email.subject, 'body': email.body})


# ─── Grant deadlines (moved from old deadlines route) ───

@actions_bp.route('/api/deadline', methods=['POST'])
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


@actions_bp.route('/api/deadline/<int:deadline_id>', methods=['PATCH'])
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


@actions_bp.route('/api/deadline/<int:deadline_id>', methods=['DELETE'])
def delete_deadline(deadline_id):
    dl = db_session.query(GrantDeadline).get(deadline_id)
    if not dl:
        return jsonify({'error': 'Not found'}), 404
    db_session.delete(dl)
    db_session.commit()
    return jsonify({'ok': True})


# ─── Seed initial action items from existing data ───

@actions_bp.route('/api/seed-actions', methods=['POST'])
def seed_actions():
    """Create action items from existing prospects, grants, and outreach emails."""
    created = 0

    # Skip if we already have actions
    existing_count = db_session.query(ActionItem).count()
    if existing_count > 0:
        return jsonify({'message': f'Already have {existing_count} action items', 'created': 0})

    # Prospects with contacts → "Email [contact] at [company]"
    prospects = db_session.query(Prospect).all()
    for p in prospects:
        if p.contact_name and p.pipeline_stage in ('1-Research', '2-Contact Identified'):
            item = ActionItem(
                prospect_id=p.id,
                description=f'Email {p.contact_name} at {p.company_name}',
                action_type='email',
                priority='high' if (p.total_score or 0) >= 12 else 'medium',
            )
            db_session.add(item)
            created += 1

    # Grant deadlines with status 'Not Started' → "Research [program]"
    grants = db_session.query(GrantDeadline).filter_by(status='Not Started').all()
    for g in grants:
        item = ActionItem(
            prospect_id=g.prospect_id,
            description=f'Research {g.program_name} grant ({g.company_name})',
            action_type='apply',
            priority='high' if g.priority == 'High' else 'medium',
        )
        db_session.add(item)
        created += 1

    # Outreach emails with status 'draft' → "Review and send email to [company]"
    emails = db_session.query(OutreachEmail).filter_by(status='draft').all()
    for e in emails:
        p = db_session.query(Prospect).get(e.prospect_id)
        if p:
            item = ActionItem(
                prospect_id=p.id,
                description=f'Review and send outreach email to {p.company_name}',
                action_type='email',
                priority='high' if (p.total_score or 0) >= 12 else 'medium',
            )
            db_session.add(item)
            created += 1

    db_session.commit()
    return jsonify({'message': f'Created {created} action items', 'created': created})
