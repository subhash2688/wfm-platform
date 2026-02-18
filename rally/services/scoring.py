"""Scoring service — rank volunteers for gap-filling."""
from datetime import date
from models.database import db_session
from models.volunteer import Volunteer
from models.shift import Shift
from models.signup import Signup
from services.stats import get_volunteer_stats, get_shift_fill_count


def score_volunteers_for_shift(shift_id):
    """Rank active volunteers for a shift. Returns list of {volunteer, score, breakdown}."""
    shift = db_session.query(Shift).get(shift_id)
    if not shift:
        return []

    # Get volunteers already signed up for this shift
    existing_ids = {s.volunteer_id for s in
                    db_session.query(Signup)
                    .filter(Signup.shift_id == shift_id)
                    .filter(Signup.status.in_(['signed_up', 'confirmed', 'checked_in']))
                    .all()}

    # Score all active volunteers not already signed up
    volunteers = (db_session.query(Volunteer)
                  .filter(Volunteer.status.in_(['active', 'new']))
                  .all())

    scored = []
    day_name = shift.date.strftime('%A') if shift.date else None

    for vol in volunteers:
        if vol.id in existing_ids:
            continue

        score = 0
        breakdown = {}

        # Campus match (30 points)
        campuses = vol.get_campuses()
        if shift.campus in campuses:
            campus_score = 30
        elif campuses:
            campus_score = 10
        else:
            campus_score = 15  # No preference = flexible
        breakdown['campus'] = campus_score
        score += campus_score

        # Availability match (25 points)
        avail = vol.get_availability()
        avail_score = 0
        if day_name and day_name in avail:
            # Check if shift time overlaps with availability
            avail_score = 25
        elif not avail:
            avail_score = 12  # No availability set = might be flexible
        breakdown['availability'] = avail_score
        score += avail_score

        # Reliability (25 points)
        stats = get_volunteer_stats(vol.id)
        rel_pct = stats['reliability_pct']
        rel_score = round(rel_pct / 100 * 25)
        breakdown['reliability'] = rel_score
        score += rel_score

        # Recency — more recent activity = higher score (20 points)
        if stats['last_active']:
            last = date.fromisoformat(stats['last_active'])
            days_ago = (date.today() - last).days
            if days_ago <= 7:
                recency_score = 20
            elif days_ago <= 14:
                recency_score = 15
            elif days_ago <= 30:
                recency_score = 10
            elif days_ago <= 60:
                recency_score = 5
            else:
                recency_score = 2
        else:
            recency_score = 8 if vol.status == 'new' else 0
        breakdown['recency'] = recency_score
        score += recency_score

        scored.append({
            'volunteer': vol.to_dict(),
            'score': score,
            'breakdown': breakdown,
        })

    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored
