"""Auto-scoring engine for Alignment, Proximity, and Capacity."""
from models.database import db_session
from models.prospect import Prospect
from models.foundation import FoundationData
from models.activity_log import ActivityLog
from config import PROXIMITY_SCORES, ALIGNMENT_KEYWORDS


def auto_score_prospect(prospect, commit=True):
    """Calculate and update scores for a single prospect. Skips if score_override is True."""
    if prospect.score_override:
        return prospect

    changes = []

    # Proximity score
    new_prox = _calc_proximity(prospect.hq_city)
    if new_prox != prospect.proximity_score:
        changes.append(f'Proximity: {prospect.proximity_score}→{new_prox}')
        prospect.proximity_score = new_prox

    # Alignment score
    new_align = _calc_alignment(prospect.focus_areas)
    if new_align != prospect.alignment_score:
        changes.append(f'Alignment: {prospect.alignment_score}→{new_align}')
        prospect.alignment_score = new_align

    # Capacity score (from 990 data if available, else keep existing)
    foundation = db_session.query(FoundationData).filter_by(prospect_id=prospect.id).first()
    if foundation and foundation.total_grants_paid:
        new_cap = _calc_capacity_from_990(foundation.total_grants_paid)
        if new_cap != prospect.capacity_score:
            changes.append(f'Capacity: {prospect.capacity_score}→{new_cap}')
            prospect.capacity_score = new_cap

    prospect.recalculate_total()

    if changes and commit:
        log = ActivityLog(
            prospect_id=prospect.id,
            action_type='score',
            description=f'Auto-scored {prospect.company_name}: {", ".join(changes)} → Total: {prospect.total_score}',
        )
        db_session.add(log)
        db_session.commit()

    return prospect


def auto_score_all():
    """Score all prospects. Returns count of updated records."""
    prospects = db_session.query(Prospect).all()
    count = 0
    for p in prospects:
        old_total = p.total_score
        auto_score_prospect(p, commit=False)
        if p.total_score != old_total:
            count += 1

    if count > 0:
        log = ActivityLog(
            action_type='score',
            description=f'Batch auto-scored all prospects: {count} updated out of {len(prospects)}',
        )
        db_session.add(log)
        db_session.commit()

    return count


def _calc_proximity(hq_city):
    """Look up city in proximity table."""
    if not hq_city:
        return 1
    city_lower = hq_city.strip().lower()
    return PROXIMITY_SCORES.get(city_lower, 1)


def _calc_alignment(focus_areas):
    """Score alignment based on keyword matching in focus areas."""
    if not focus_areas:
        return 1
    text = focus_areas.lower()
    for score in [5, 4, 3, 2]:
        for keyword in ALIGNMENT_KEYWORDS[score]:
            if keyword in text:
                return score
    return 1


def _calc_capacity_from_990(total_grants_paid):
    """Score capacity based on foundation grant amounts."""
    if total_grants_paid >= 10_000_000:
        return 5
    elif total_grants_paid >= 1_000_000:
        return 4
    elif total_grants_paid >= 100_000:
        return 3
    elif total_grants_paid >= 10_000:
        return 2
    return 1
