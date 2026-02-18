"""WFM Rally — Volunteer Management App — Entry Point.

Usage:
    cd rally/
    python run.py
    → Open http://localhost:5002
"""
import sys
import os
import threading
from time import sleep
from datetime import datetime, timedelta

# Ensure rally directory is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models.database import db_session, init_db
from models.volunteer import Volunteer
from routes import all_blueprints
from services.seed_data import seed_all, seed_campuses
from config import UPLOAD_FOLDER, REMINDER_HOUR


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'wfm-rally-volunteer-2024')

    # Register all blueprints
    for bp in all_blueprints:
        app.register_blueprint(bp)

    # Teardown: remove DB session at end of each request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app


def _start_reminder_scheduler(app):
    """Daemon thread: send shift reminders once daily at REMINDER_HOUR."""
    def run():
        while True:
            now = datetime.now()
            target = now.replace(hour=REMINDER_HOUR, minute=0, second=0, microsecond=0)
            if now >= target:
                target += timedelta(days=1)
            sleep_secs = (target - now).total_seconds()
            sleep(sleep_secs)
            try:
                with app.app_context():
                    from services.sms_service import send_shift_reminders
                    send_shift_reminders()
            except Exception as e:
                print(f'[Reminder Error] {e}')

    t = threading.Thread(target=run, daemon=True, name='sms-reminder')
    t.start()
    print(f'  Shift reminder scheduler started (runs daily at {REMINDER_HOUR}:00)')


def main():
    # Ensure upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Initialize database
    init_db()

    # Ensure default campuses exist
    seed_campuses()
    db_session.commit()

    # Auto-seed on first run (if DB is empty)
    count = db_session.query(Volunteer).count()
    if count == 0:
        vol_count, shift_count = seed_all()
        print(f'  Seeded {vol_count} volunteers and {shift_count} shifts')
    else:
        print(f'  Database has {count} volunteers')

    app = create_app()

    # Start nightly SMS reminder scheduler
    _start_reminder_scheduler(app)

    print()
    print('  WFM Rally — Volunteer Management')
    print('  ──────────────────────────────────')
    print('  http://localhost:5002')
    print()

    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    main()
