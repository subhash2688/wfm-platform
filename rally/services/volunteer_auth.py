"""Volunteer auth — session helpers and login_required decorator."""
from functools import wraps
from flask import session, redirect, url_for, request, g
from models.database import db_session
from models.volunteer import Volunteer


def get_current_volunteer():
    """Return the logged-in Volunteer or None."""
    vid = session.get('volunteer_id')
    if vid:
        return db_session.query(Volunteer).get(vid)
    return None


def volunteer_login_required(f):
    """Redirect to /v/login if no volunteer session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        volunteer = get_current_volunteer()
        if not volunteer:
            session['next_url'] = request.path
            return redirect(url_for('volunteer.login'))
        g.volunteer = volunteer
        return f(*args, **kwargs)
    return decorated
