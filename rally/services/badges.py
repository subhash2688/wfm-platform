"""Badge service — milestone badges based on completed shifts."""
from config import BADGE_THRESHOLDS


def get_earned_badges(total_shifts):
    """Return list of earned badge dicts from BADGE_THRESHOLDS."""
    earned = []
    for threshold, name, icon in BADGE_THRESHOLDS:
        if total_shifts >= threshold:
            earned.append({'threshold': threshold, 'name': name, 'icon': icon})
    return earned
