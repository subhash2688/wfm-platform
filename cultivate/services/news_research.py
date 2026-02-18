"""Research notes service — CRUD for prospect research notes."""
from models.database import db_session
from models.research_note import ResearchNote


def add_research_note(prospect_id, note_type, title, content, source_url=None, published_date=None):
    """Create a new research note for a prospect."""
    note = ResearchNote(
        prospect_id=prospect_id,
        note_type=note_type,
        title=title,
        content=content,
        source_url=source_url,
        published_date=published_date,
    )
    db_session.add(note)
    db_session.commit()
    return note.to_dict()


def get_research_notes(prospect_id):
    """Get all research notes for a prospect, newest first."""
    notes = (db_session.query(ResearchNote)
             .filter_by(prospect_id=prospect_id)
             .order_by(ResearchNote.created_at.desc())
             .all())
    return [n.to_dict() for n in notes]


def delete_research_note(note_id):
    """Delete a research note by ID."""
    note = db_session.query(ResearchNote).get(note_id)
    if not note:
        return {'error': 'Note not found'}
    db_session.delete(note)
    db_session.commit()
    return {'success': True}
