"""Staff authentication routes — login and logout."""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, g
from models.database import db_session
from models.staff import Staff

staff_auth_bp = Blueprint('staff_auth', __name__)


@staff_auth_bp.route('/login', methods=['GET'])
def login():
    if session.get('staff_id'):
        return redirect(url_for('home.index'))
    return render_template('staff_login.html')


@staff_auth_bp.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    staff = db_session.query(Staff).filter_by(email=email, is_active=True).first()

    if not staff or not staff.check_password(password):
        return render_template('staff_login.html', error='Incorrect email or password.')

    staff.last_login = datetime.utcnow()
    db_session.commit()

    session['staff_id'] = staff.id
    next_url = session.pop('next_url', '/')
    return redirect(next_url)


@staff_auth_bp.route('/logout')
def logout():
    session.pop('staff_id', None)
    return redirect(url_for('staff_auth.login'))
