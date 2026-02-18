"""Personalized outreach email generator."""
import random
from models.database import db_session
from models.prospect import Prospect
from models.foundation import FoundationData
from models.outreach import OutreachEmail
from models.activity_log import ActivityLog


# Subject line templates — varied per company attributes
SUBJECT_TEMPLATES = [
    "Addressing student hunger near {company}'s {city} campus",
    "1 in 3 community college students near {city} faces food insecurity",
    "{company} + World Food Movement: Fighting student hunger in the Bay Area",
    "Students at {campus} need our help — partnership opportunity",
    "Community impact opportunity near {company}'s headquarters",
    "Partnering to end food insecurity at {campus}",
    "{company}'s commitment to {focus} — a local connection",
    "Bay Area students are going hungry — how {company} can help",
]


def generate_outreach_email(prospect_id):
    """Generate a personalized outreach email for a prospect."""
    prospect = db_session.query(Prospect).get(prospect_id)
    if not prospect:
        return None

    foundation = db_session.query(FoundationData).filter_by(prospect_id=prospect.id).first()

    # Pick campus reference
    campus = prospect.nearest_campus or 'our Bay Area campuses'
    campus_city = _campus_city(campus)

    # Build focus reference
    focus = prospect.focus_areas or 'community investment'
    focus_short = focus.split(',')[0].strip() if focus else 'community impact'

    # Pick a subject line
    subject = _pick_subject(prospect, campus, focus_short)

    # Contact greeting
    if prospect.contact_name:
        greeting = f"Dear {prospect.contact_name.split()[0]}"
    else:
        greeting = "Dear Community Team"

    # Build body
    body_parts = []

    # Line 1: Why reaching out (reference their giving focus)
    if foundation and foundation.mission_statement:
        body_parts.append(
            f"{greeting},\n\n"
            f"I'm reaching out because {prospect.company_name}'s commitment to "
            f"{focus_short.lower()} aligns closely with our mission to end student food insecurity "
            f"in the Bay Area."
        )
    elif prospect.has_foundation and prospect.foundation_name:
        body_parts.append(
            f"{greeting},\n\n"
            f"I'm reaching out because the {prospect.foundation_name}'s focus on "
            f"{focus_short.lower()} directly connects to a critical need in your community."
        )
    else:
        body_parts.append(
            f"{greeting},\n\n"
            f"I'm reaching out because {prospect.company_name}'s investment in "
            f"{focus_short.lower()} aligns with an urgent need right in your backyard."
        )

    # Line 2-3: Who WFM is + campus reference
    body_parts.append(
        f"World Food Movement operates food pantries and meal programs at {campus} "
        f"in {campus_city}, serving hundreds of students who struggle to afford their next meal "
        f"while pursuing their education."
    )

    # Line 3: Data point
    body_parts.append(
        "One in three California community college students experiences food insecurity — "
        "and the students we serve are among the most affected."
    )

    # Line 4: The ask (meeting, not money)
    body_parts.append(
        "I'd welcome 20 minutes to share how a partnership could create meaningful impact "
        "for students in your community."
    )

    # Line 5: Thank them
    body_parts.append(
        f"Thank you for {prospect.company_name}'s commitment to strengthening "
        f"local communities."
    )

    # Signature
    body_parts.append(
        "\nBest regards,\n"
        "[Name]\n"
        "Funding & Partnerships Lead\n"
        "World Food Movement, California Chapter"
    )

    body = '\n\n'.join(body_parts)
    word_count = len(body.split())

    # Personalization notes
    notes = _build_personalization_notes(prospect, foundation)

    # Save to database
    existing = db_session.query(OutreachEmail).filter_by(prospect_id=prospect.id).first()
    if existing:
        email = existing
    else:
        email = OutreachEmail(prospect_id=prospect.id)
        db_session.add(email)

    email.subject = subject
    email.body = body
    email.word_count = word_count
    email.personalization_notes = notes
    email.status = 'draft'

    log = ActivityLog(
        prospect_id=prospect.id,
        action_type='email_draft',
        description=f'Generated outreach email draft for {prospect.company_name} ({word_count} words)',
    )
    db_session.add(log)
    db_session.commit()

    return email.to_dict()


def generate_top_emails(n=15):
    """Generate emails for the top N prospects by score."""
    prospects = (db_session.query(Prospect)
                 .order_by(Prospect.total_score.desc())
                 .limit(n)
                 .all())
    results = []
    for p in prospects:
        result = generate_outreach_email(p.id)
        if result:
            results.append(result)
    return results


def _pick_subject(prospect, campus, focus_short):
    """Pick and populate a subject line template."""
    template = random.choice(SUBJECT_TEMPLATES)
    return template.format(
        company=prospect.company_name,
        city=prospect.hq_city or 'the Bay Area',
        campus=campus,
        focus=focus_short,
    )


def _campus_city(campus_name):
    """Get the city for a campus."""
    mapping = {
        'De Anza College': 'Cupertino',
        'Foothill College': 'Los Altos Hills',
        'Chabot College': 'Hayward',
        'All Campuses': 'the Bay Area',
    }
    return mapping.get(campus_name, 'the Bay Area')


def _build_personalization_notes(prospect, foundation):
    """Build notes on what to verify/personalize before sending."""
    notes = []
    if not prospect.contact_name:
        notes.append("Find specific contact name via LinkedIn or Apollo")
    if not prospect.contact_email:
        notes.append("Find contact email address")
    notes.append("Insert exact number of students served at nearest campus last semester")
    notes.append("Verify company's current CSR priorities haven't changed")
    if foundation:
        if foundation.fit_assessment == 'Strong fit':
            notes.append("Strong 990 fit — consider mentioning specific similar grantees")
        notes.append(f"Foundation grants ${foundation.total_grants_paid:,.0f}/year — calibrate ask accordingly")
    if not prospect.csr_page_url:
        notes.append("Find and verify company's CSR/giving page URL")
    return ' | '.join(notes)
