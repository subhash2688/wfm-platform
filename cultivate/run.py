"""WFM Corporate Fundraising App — Entry Point.

Usage:
    cd app/
    python run.py
    → Open http://localhost:5000
"""
import sys
import os

# Ensure app directory is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models.database import db_session, init_db
from models.prospect import Prospect
from routes import all_blueprints
from services.import_excel import import_from_excel
from config import EXCEL_PATH


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'wfm-corporate-giving-2024')

    # Register all blueprints
    for bp in all_blueprints:
        app.register_blueprint(bp)

    # Teardown: remove DB session at end of each request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app


def main():
    # Initialize database
    init_db()

    # Auto-import from Excel on first run (if DB is empty)
    count = db_session.query(Prospect).count()
    if count == 0 and os.path.exists(EXCEL_PATH):
        imported, skipped = import_from_excel()
        print(f'  Imported {imported} prospects from Excel ({skipped} skipped)')
    else:
        print(f'  Database has {count} prospects')

    app = create_app()

    print()
    print('  WFM Corporate Fundraising')
    print('  ─────────────────────────')
    print('  http://localhost:5001')
    print()

    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    main()
