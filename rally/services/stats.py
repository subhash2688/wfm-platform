"""Stats service — compute volunteer totals, hours, reliability."""
from datetime import datetime, date, timedelta
from sqlalchemy import func
from models.database import db_session
from models.volunteer import Volunteer
from models.shift import Shift
from models.signup import Signup


def get_volunteer_stats(volunteer_id):
    """Return {total_shifts, total_hours, reliability_pct, last_active} for a volunteer."""
    signups = (db_session.query(Signup)
               .filter(Signup.volunteer_id == volunteer_id)
               .all())

    if not signups:
        return {
            'total_shifts': 0,
            'total_hours': 0,
            'reliability_pct': 100,
            'last_active': None,
        }

    completed = [s for s in signups if s.status == 'completed']
    no_shows = [s for s in signups if s.status == 'no_show']
    finished = len(completed) + len(no_shows)

    # Total hours from completed shifts
    total_hours = 0
    last_active = None
    for s in completed:
        shift = db_session.query(Shift).get(s.shift_id)
        if shift:
            total_hours += shift.duration_hours
            if shift.date and (last_active is None or shift.date > last_active):
                last_active = shift.date

    # Reliability: completed / (completed + no_shows)
    reliability_pct = round(len(completed) / finished * 100) if finished > 0 else 100

    return {
        'total_shifts': len(completed),
        'total_hours': round(total_hours, 1),
        'reliability_pct': reliability_pct,
        'last_active': last_active.isoformat() if last_active else None,
    }


def get_volunteer_streak(volunteer_id):
    """Return consecutive weeks with at least one completed shift, counting back from this week."""
    today = date.today()
    # Get all completed shift dates for this volunteer
    rows = (db_session.query(Shift.date)
            .join(Signup, Signup.shift_id == Shift.id)
            .filter(Signup.volunteer_id == volunteer_id,
                    Signup.status == 'completed')
            .all())
    if not rows:
        return 0

    # Build set of ISO week numbers (year, week)
    weeks_active = set()
    for (d,) in rows:
        iso = d.isocalendar()
        weeks_active.add((iso[0], iso[1]))

    # Count consecutive weeks going backwards from current week
    streak = 0
    current = today
    while True:
        iso = current.isocalendar()
        if (iso[0], iso[1]) in weeks_active:
            streak += 1
            current -= timedelta(weeks=1)
        else:
            break
    return streak


def get_shift_fill_count(shift_id):
    """Return number of active signups (not cancelled/no_show) for a shift."""
    return (db_session.query(Signup)
            .filter(Signup.shift_id == shift_id)
            .filter(Signup.status.in_(['signed_up', 'confirmed', 'checked_in', 'completed']))
            .count())


def get_dashboard_stats():
    """Return aggregate stats for the dashboard."""
    today = date.today()

    total_volunteers = db_session.query(Volunteer).count()
    active_volunteers = (db_session.query(Volunteer)
                         .filter(Volunteer.status == 'active')
                         .count())
    new_volunteers = (db_session.query(Volunteer)
                      .filter(Volunteer.status == 'new')
                      .count())

    total_shifts = db_session.query(Shift).count()
    upcoming_shifts = (db_session.query(Shift)
                       .filter(Shift.date >= today)
                       .filter(Shift.status == 'scheduled')
                       .count())
    completed_shifts = (db_session.query(Shift)
                        .filter(Shift.status == 'completed')
                        .count())

    total_signups = db_session.query(Signup).count()
    completed_signups = (db_session.query(Signup)
                         .filter(Signup.status == 'completed')
                         .count())

    # Total volunteer hours from completed signups
    total_hours = 0
    completed_signup_records = (db_session.query(Signup)
                                .filter(Signup.status == 'completed')
                                .all())
    for s in completed_signup_records:
        shift = db_session.query(Shift).get(s.shift_id)
        if shift:
            total_hours += shift.duration_hours

    # Gaps: upcoming shifts where filled < required
    upcoming = (db_session.query(Shift)
                .filter(Shift.date >= today)
                .filter(Shift.status == 'scheduled')
                .all())
    gaps = 0
    for shift in upcoming:
        filled = get_shift_fill_count(shift.id)
        if filled < shift.required_count:
            gaps += 1

    return {
        'total_volunteers': total_volunteers,
        'active_volunteers': active_volunteers,
        'new_volunteers': new_volunteers,
        'total_shifts': total_shifts,
        'upcoming_shifts': upcoming_shifts,
        'completed_shifts': completed_shifts,
        'total_signups': total_signups,
        'completed_signups': completed_signups,
        'total_hours': round(total_hours, 1),
        'gaps': gaps,
    }
