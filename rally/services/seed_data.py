"""Seed data — 3 campuses, 20 volunteers, 15 shifts, ~40 signups, 3 recurring series."""
import json
from datetime import datetime, date, time, timedelta
from models.database import db_session
from models.campus import Campus
from models.volunteer import Volunteer
from models.shift import Shift
from models.signup import Signup
from models.recurring_series import RecurringSeries
from models.activity_log import ActivityLog
from config import DEFAULT_CAMPUSES


def seed_campuses():
    """Seed default campuses if none exist. Returns list of Campus objects."""
    existing = db_session.query(Campus).count()
    if existing > 0:
        return db_session.query(Campus).all()

    campuses = []
    for c in DEFAULT_CAMPUSES:
        campus = Campus(
            name=c['name'],
            city=c['city'],
            zip_code=c['zip_code'],
            region=c['region'],
            color=c['color'],
        )
        db_session.add(campus)
        campuses.append(campus)

    db_session.flush()
    return campuses


def seed_all():
    """Populate the database with realistic demo data."""
    seed_campuses()
    volunteers = _seed_volunteers()
    series = _seed_recurring_series()
    shifts = _seed_shifts(series)
    _seed_signups(volunteers, shifts)

    log = ActivityLog(
        action_type='seed',
        description=f'Seeded database: {len(volunteers)} volunteers, {len(shifts)} shifts',
    )
    db_session.add(log)
    db_session.commit()

    return len(volunteers), len(shifts)


def _seed_volunteers():
    """Create 20 diverse Bay Area volunteers."""
    today = date.today()
    data = [
        # 14 active
        ('Priya', 'Sharma', '(408) 555-0101', 'priya.sharma@email.com', ['De Anza College'], 'active',
         {'Saturday': ['9:00-13:00'], 'Wednesday': ['14:00-17:00']}, today - timedelta(days=180)),
        ('Marcus', 'Johnson', '(510) 555-0102', 'marcus.j@email.com', ['Chabot College'], 'active',
         {'Saturday': ['9:00-13:00'], 'Thursday': ['10:00-14:00']}, today - timedelta(days=150)),
        ('Linh', 'Nguyen', '(650) 555-0103', 'linh.n@email.com', ['Foothill College', 'De Anza College'], 'active',
         {'Tuesday': ['11:00-15:00'], 'Saturday': ['9:00-13:00']}, today - timedelta(days=120)),
        ('Carlos', 'Ramirez', '(408) 555-0104', 'carlos.r@email.com', ['De Anza College'], 'active',
         {'Monday': ['9:00-12:00'], 'Friday': ['13:00-17:00']}, today - timedelta(days=200)),
        ('Aisha', 'Patel', '(510) 555-0105', 'aisha.p@email.com', ['Chabot College'], 'active',
         {'Wednesday': ['10:00-14:00'], 'Saturday': ['9:00-13:00']}, today - timedelta(days=90)),
        ('David', 'Kim', '(650) 555-0106', 'david.k@email.com', ['Foothill College'], 'active',
         {'Thursday': ['9:00-13:00'], 'Saturday': ['9:00-13:00']}, today - timedelta(days=160)),
        ('Sofia', 'Martinez', '(408) 555-0107', 'sofia.m@email.com', ['De Anza College', 'Foothill College'], 'active',
         {'Monday': ['10:00-14:00'], 'Wednesday': ['10:00-14:00']}, today - timedelta(days=75)),
        ('James', 'Chen', '(510) 555-0108', 'james.c@email.com', ['Chabot College'], 'active',
         {'Tuesday': ['9:00-13:00'], 'Saturday': ['9:00-13:00']}, today - timedelta(days=210)),
        ('Fatima', 'Hassan', '(408) 555-0109', 'fatima.h@email.com', ['De Anza College'], 'active',
         {'Wednesday': ['9:00-12:00'], 'Friday': ['9:00-12:00']}, today - timedelta(days=45)),
        ('Ryan', 'O\'Brien', '(650) 555-0110', 'ryan.ob@email.com', ['Foothill College', 'De Anza College'], 'active',
         {'Thursday': ['14:00-17:00'], 'Saturday': ['9:00-13:00']}, today - timedelta(days=130)),
        ('Maria', 'Santos', '(510) 555-0111', 'maria.s@email.com', ['Chabot College'], 'active',
         {'Monday': ['9:00-13:00'], 'Wednesday': ['9:00-13:00']}, today - timedelta(days=100)),
        ('Kevin', 'Washington', '(408) 555-0112', 'kevin.w@email.com', ['De Anza College'], 'active',
         {'Tuesday': ['10:00-14:00'], 'Saturday': ['9:00-13:00']}, today - timedelta(days=60)),
        ('Ananya', 'Desai', '(650) 555-0113', 'ananya.d@email.com', ['Foothill College'], 'active',
         {'Wednesday': ['11:00-15:00'], 'Friday': ['11:00-15:00']}, today - timedelta(days=85)),
        ('Tyler', 'Brooks', '(510) 555-0114', 'tyler.b@email.com', ['Chabot College', 'De Anza College'], 'active',
         {'Thursday': ['9:00-12:00'], 'Saturday': ['9:00-13:00']}, today - timedelta(days=140)),
        # 3 new
        ('Jasmine', 'Lee', '(408) 555-0115', 'jasmine.l@email.com', ['De Anza College'], 'new',
         {'Saturday': ['9:00-13:00']}, today - timedelta(days=5)),
        ('Omar', 'Ali', '(510) 555-0116', 'omar.a@email.com', ['Chabot College'], 'new',
         {'Wednesday': ['10:00-14:00'], 'Saturday': ['9:00-13:00']}, today - timedelta(days=3)),
        ('Emma', 'Taylor', '(650) 555-0117', 'emma.t@email.com', ['Foothill College'], 'new',
         {'Tuesday': ['9:00-13:00']}, today - timedelta(days=7)),
        # 3 inactive
        ('Daniel', 'Park', '(408) 555-0118', 'daniel.p@email.com', ['De Anza College'], 'inactive',
         {'Saturday': ['9:00-13:00']}, today - timedelta(days=300)),
        ('Sarah', 'Williams', '(510) 555-0119', 'sarah.w@email.com', ['Chabot College'], 'inactive',
         {'Monday': ['9:00-12:00']}, today - timedelta(days=250)),
        ('Alex', 'Rivera', '(650) 555-0120', 'alex.r@email.com', ['Foothill College'], 'inactive',
         {'Thursday': ['10:00-14:00']}, today - timedelta(days=280)),
        # Demo volunteer for mobile app testing
        ('Demo', 'Volunteer', '0000000000', 'demo@wfm.org',
         ['De Anza College', 'Foothill College', 'Chabot College'], 'active',
         {'Saturday': ['9:00-13:00'], 'Wednesday': ['10:00-14:00']}, today - timedelta(days=30)),
    ]

    volunteers = []
    for first, last, phone, email, campuses, status, avail, joined in data:
        v = Volunteer(
            first_name=first,
            last_name=last,
            phone=phone,
            email=email,
            preferred_campuses=json.dumps(campuses),
            availability=json.dumps(avail),
            status=status,
            joined_date=datetime.combine(joined, time(0, 0)),
        )
        db_session.add(v)
        volunteers.append(v)

    db_session.flush()
    return volunteers


def _seed_recurring_series():
    """Create 3 recurring series templates."""
    series = [
        RecurringSeries(
            campus='De Anza College',
            day_of_week='Saturday',
            start_time=time(9, 0),
            end_time=time(13, 0),
            shift_type='Serving',
            required_count=6,
            frequency='weekly',
            active=True,
        ),
        RecurringSeries(
            campus='Chabot College',
            day_of_week='Saturday',
            start_time=time(10, 0),
            end_time=time(14, 0),
            shift_type='Serving',
            required_count=5,
            frequency='weekly',
            active=True,
        ),
        RecurringSeries(
            campus='Foothill College',
            day_of_week='Wednesday',
            start_time=time(11, 0),
            end_time=time(15, 0),
            shift_type='Packing',
            required_count=3,
            frequency='biweekly',
            active=True,
        ),
    ]
    for s in series:
        db_session.add(s)
    db_session.flush()
    return series


def _seed_shifts(series):
    """Create 15 shifts: 5 past completed, 7 next-2-weeks, 3 further out."""
    today = date.today()
    shifts = []

    # 5 past completed shifts (campus, date, start, end, activity_type, service_type, required, status, series_id)
    past_data = [
        ('De Anza College', today - timedelta(days=21), time(9, 0), time(13, 0), 'Serving', 'Catered Meal', 6, 'completed', series[0].id),
        ('Chabot College', today - timedelta(days=14), time(10, 0), time(14, 0), 'Serving', 'Pre-packed Meal', 5, 'completed', series[1].id),
        ('Foothill College', today - timedelta(days=10), time(11, 0), time(15, 0), 'Packing', 'Pre-packed Meal', 3, 'completed', series[2].id),
        ('De Anza College', today - timedelta(days=7), time(9, 0), time(13, 0), 'Serving', 'Catered Meal', 6, 'completed', series[0].id),
        ('Chabot College', today - timedelta(days=7), time(10, 0), time(14, 0), 'Delivery', 'Pre-packed Meal', 5, 'completed', series[1].id),
    ]

    for campus, d, st, et, stype, svtype, req, status, sid in past_data:
        s = Shift(campus=campus, date=d, start_time=st, end_time=et,
                  shift_type=stype, service_type=svtype, required_count=req,
                  status=status, recurring_series_id=sid)
        db_session.add(s)
        shifts.append(s)

    # 7 upcoming (next 2 weeks) — some will have gaps
    upcoming_data = [
        ('De Anza College', today + timedelta(days=1), time(9, 0), time(13, 0), 'Serving', 'Catered Meal', 6, 'scheduled', series[0].id),
        ('Chabot College', today + timedelta(days=2), time(10, 0), time(14, 0), 'Serving', 'Pre-packed Meal', 5, 'scheduled', series[1].id),
        ('Foothill College', today + timedelta(days=3), time(11, 0), time(15, 0), 'Packing', 'Pre-packed Meal', 3, 'scheduled', series[2].id),
        ('De Anza College', today + timedelta(days=5), time(14, 0), time(17, 0), 'Meal Prep', 'Catered Meal', 4, 'scheduled', None),
        ('Chabot College', today + timedelta(days=7), time(9, 0), time(12, 0), 'Administrative', 'Catered Meal', 3, 'scheduled', None),
        ('De Anza College', today + timedelta(days=8), time(9, 0), time(13, 0), 'Serving', 'Catered Meal', 6, 'scheduled', series[0].id),
        ('Foothill College', today + timedelta(days=10), time(10, 0), time(14, 0), 'Delivery', 'Pre-packed Meal', 5, 'scheduled', None),
    ]

    for campus, d, st, et, stype, svtype, req, status, sid in upcoming_data:
        s = Shift(campus=campus, date=d, start_time=st, end_time=et,
                  shift_type=stype, service_type=svtype, required_count=req,
                  status=status, recurring_series_id=sid)
        db_session.add(s)
        shifts.append(s)

    # 3 further out (3-4 weeks)
    far_data = [
        ('De Anza College', today + timedelta(days=15), time(9, 0), time(13, 0), 'Serving', 'Catered Meal', 6, 'scheduled', series[0].id),
        ('Chabot College', today + timedelta(days=21), time(10, 0), time(14, 0), 'Packing', 'Pre-packed Meal', 5, 'scheduled', series[1].id),
        ('Foothill College', today + timedelta(days=24), time(11, 0), time(15, 0), 'Packing', 'Pre-packed Meal', 3, 'scheduled', series[2].id),
    ]

    for campus, d, st, et, stype, svtype, req, status, sid in far_data:
        s = Shift(campus=campus, date=d, start_time=st, end_time=et,
                  shift_type=stype, service_type=svtype, required_count=req,
                  status=status, recurring_series_id=sid)
        db_session.add(s)
        shifts.append(s)

    db_session.flush()
    return shifts


def _seed_signups(volunteers, shifts):
    """Create ~40 signups with realistic status distribution."""
    now = datetime.utcnow()
    signups = []

    # Past shifts — completed signups (shifts 0-4)
    past_assignments = [
        # Shift 0 (past De Anza): 5 completed, 1 no_show
        (0, 0, 'completed'), (0, 3, 'completed'), (0, 6, 'completed'),
        (0, 8, 'completed'), (0, 11, 'completed'), (0, 17, 'no_show'),
        # Shift 1 (past Chabot): 4 completed, 1 no_show
        (1, 1, 'completed'), (1, 4, 'completed'), (1, 7, 'completed'),
        (1, 10, 'completed'), (1, 18, 'no_show'),
        # Shift 2 (past Foothill): 3 completed
        (2, 2, 'completed'), (2, 5, 'completed'), (2, 9, 'completed'),
        # Shift 3 (past De Anza): 5 completed
        (3, 0, 'completed'), (3, 3, 'completed'), (3, 6, 'completed'),
        (3, 8, 'completed'), (3, 11, 'completed'),
        # Shift 4 (past Chabot): 4 completed, 1 no_show
        (4, 1, 'completed'), (4, 4, 'completed'), (4, 7, 'completed'),
        (4, 13, 'completed'), (4, 19, 'no_show'),
    ]

    for shift_idx, vol_idx, status in past_assignments:
        s = Signup(
            volunteer_id=volunteers[vol_idx].id,
            shift_id=shifts[shift_idx].id,
            status=status,
            signed_up_at=now - timedelta(days=30),
            confirmed_at=now - timedelta(days=28) if status != 'no_show' else None,
            checked_in_at=now - timedelta(days=21) if status == 'completed' else None,
            completed_at=now - timedelta(days=21) if status == 'completed' else None,
        )
        db_session.add(s)
        signups.append(s)

    # Upcoming shifts — mix of signed_up and confirmed (shifts 5-11)
    upcoming_assignments = [
        # Shift 5 (tomorrow De Anza, need 6): only 3 signed up — gap!
        (5, 0, 'confirmed'), (5, 3, 'confirmed'), (5, 6, 'signed_up'),
        # Shift 6 (day after tomorrow Chabot, need 5): 4 signed up — gap!
        (6, 1, 'confirmed'), (6, 4, 'confirmed'), (6, 7, 'signed_up'), (6, 10, 'signed_up'),
        # Shift 7 (Foothill, need 3): 3 confirmed — full!
        (7, 2, 'confirmed'), (7, 5, 'confirmed'), (7, 9, 'confirmed'),
        # Shift 8 (De Anza meal prep, need 4): 2 signed up — gap!
        (8, 8, 'signed_up'), (8, 11, 'signed_up'),
        # Shift 9 (Chabot administrative, need 3): 1 signed up — big gap!
        (9, 13, 'signed_up'),
        # Shift 10 (De Anza, need 6): 4 confirmed — gap!
        (10, 0, 'confirmed'), (10, 3, 'confirmed'), (10, 6, 'confirmed'), (10, 11, 'signed_up'),
        # Shift 11 (Foothill delivery, need 5): 2 signed up — gap!
        (11, 2, 'signed_up'), (11, 12, 'signed_up'),
    ]

    for shift_idx, vol_idx, status in upcoming_assignments:
        s = Signup(
            volunteer_id=volunteers[vol_idx].id,
            shift_id=shifts[shift_idx].id,
            status=status,
            signed_up_at=now - timedelta(days=3),
            confirmed_at=now - timedelta(days=1) if status == 'confirmed' else None,
        )
        db_session.add(s)
        signups.append(s)

    db_session.flush()
    return signups
