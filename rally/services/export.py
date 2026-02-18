"""Export service — CSV export of volunteer roster with stats."""
import csv
import io
from models.database import db_session
from models.volunteer import Volunteer
from services.stats import get_volunteer_stats


def export_volunteers_csv():
    """Generate CSV string of volunteer roster with stats."""
    volunteers = (db_session.query(Volunteer)
                  .order_by(Volunteer.last_name)
                  .all())

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'Name', 'Phone', 'Email', 'Status',
        'Preferred Campuses', 'Total Shifts', 'Total Hours',
        'Reliability %', 'Last Active', 'Joined',
    ])

    for vol in volunteers:
        stats = get_volunteer_stats(vol.id)
        campuses = ', '.join(vol.get_campuses())
        writer.writerow([
            vol.full_name,
            vol.phone,
            vol.email or '',
            vol.status,
            campuses,
            stats['total_shifts'],
            stats['total_hours'],
            stats['reliability_pct'],
            stats['last_active'] or '',
            vol.joined_date.strftime('%Y-%m-%d') if vol.joined_date else '',
        ])

    return output.getvalue()
