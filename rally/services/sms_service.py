"""SMS service — OTP generation, verification, phone normalization, and shift reminders."""
import random
import re
from datetime import datetime, timedelta, date
from models.database import db_session
from models.sms_code import SmsCode
from config import SMS_DEV_MODE, OTP_EXPIRY_MINUTES, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER


def normalize_phone(phone):
    """Strip non-digit characters for consistent matching."""
    return re.sub(r'\D', '', phone or '')


def generate_otp():
    """Return a random 6-digit string."""
    return f'{random.randint(0, 999999):06d}'


def send_otp(phone):
    """Invalidate old codes, create new OTP, return result dict."""
    phone_digits = normalize_phone(phone)

    # Invalidate any existing unused codes for this phone
    db_session.query(SmsCode).filter(
        SmsCode.phone == phone_digits,
        SmsCode.used == False,
    ).update({'used': True})

    code = generate_otp()
    sms = SmsCode(
        phone=phone_digits,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )
    db_session.add(sms)
    db_session.commit()

    result = {'success': True}
    if SMS_DEV_MODE:
        result['dev_code'] = code
    return result


def verify_otp(phone, code):
    """Check if code is valid, unexpired, and unused. Mark used if valid."""
    phone_digits = normalize_phone(phone)
    now = datetime.utcnow()

    sms = (db_session.query(SmsCode)
           .filter(SmsCode.phone == phone_digits,
                   SmsCode.code == code,
                   SmsCode.used == False,
                   SmsCode.expires_at > now)
           .first())

    if sms:
        sms.used = True
        db_session.commit()
        return True
    return False


# ── Outbound SMS ──────────────────────────────────────────────────────────────

def send_sms(to_phone, message):
    """Send an SMS message. Uses Twilio if configured, logs to console in dev mode."""
    digits = normalize_phone(to_phone)
    if len(digits) == 10:
        digits = '1' + digits
    if not digits:
        return False

    if SMS_DEV_MODE or not TWILIO_ACCOUNT_SID:
        print(f'[SMS DEV] To +{digits}: {message}')
        return True

    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(body=message, from_=TWILIO_FROM_NUMBER, to=f'+{digits}')
        return True
    except Exception as e:
        print(f'[SMS ERROR] {e}')
        return False


def send_shift_reminders():
    """Send reminder SMS to all volunteers with shifts tomorrow. Called nightly."""
    from models.shift import Shift
    from models.signup import Signup
    from models.volunteer import Volunteer
    from models.activity_log import ActivityLog

    tomorrow = date.today() + timedelta(days=1)
    shifts = (db_session.query(Shift)
              .filter(Shift.date == tomorrow, Shift.status == 'scheduled')
              .all())

    sent = 0
    for shift in shifts:
        signups = (db_session.query(Signup)
                   .filter(Signup.shift_id == shift.id,
                           Signup.status.in_(['signed_up', 'confirmed']))
                   .all())
        campus_short = shift.campus.split(' College')[0]
        for su in signups:
            vol = db_session.query(Volunteer).get(su.volunteer_id)
            if not vol or not vol.phone:
                continue
            msg = (
                f"Hi {vol.first_name}! Reminder: your {shift.shift_type} shift at "
                f"{campus_short} is tomorrow at {shift.start_time.strftime('%-I:%M %p')}. "
                f"Thank you for volunteering with WFM!"
            )
            if send_sms(vol.phone, msg):
                sent += 1
                db_session.add(ActivityLog(
                    action_type='sms',
                    description=f'Shift reminder sent to {vol.full_name}',
                    volunteer_id=vol.id,
                    shift_id=shift.id,
                ))

    if sent > 0:
        db_session.commit()
    print(f'[Reminders] {sent} reminder(s) sent for {tomorrow}')
    return sent
