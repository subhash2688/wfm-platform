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

from flask import Flask, g, session, redirect, url_for, request
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

    # Inject module URLs into every template
    @app.context_processor
    def inject_module_urls():
        return {
            'CULTIVATE_URL': os.environ.get('CULTIVATE_URL', 'http://localhost:5001'),
            'RALLY_URL':     os.environ.get('RALLY_URL',     'http://localhost:5002'),
        }

    # Staff auth guard — protect all management routes
    @app.before_request
    def require_staff_login():
        public = ('/login', '/logout', '/static/')
        if any(request.path.startswith(p) for p in public):
            return None
        if not session.get('staff_id'):
            session['next_url'] = request.url
            return redirect(url_for('staff_auth.login'))
        from models.staff import Staff
        g.staff = db_session.query(Staff).get(session['staff_id'])
        if not g.staff or not g.staff.is_active:
            session.pop('staff_id', None)
            return redirect(url_for('staff_auth.login'))

    # Inject staff into templates
    @app.context_processor
    def inject_staff():
        return {'current_staff': getattr(g, 'staff', None)}

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

    # Seed default admin staff account if none exists
    from models.staff import Staff
    if db_session.query(Staff).count() == 0:
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@wfm.org')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'wfm2024')
        admin = Staff(name='Admin', email=admin_email, role='admin')
        admin.set_password(admin_password)
        db_session.add(admin)
        db_session.commit()
        print(f'  Created default admin: {admin_email} / {admin_password}')

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
