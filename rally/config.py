"""Configuration for Rally — WFM Volunteer Management App."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WFM_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'wfm_rally.db')
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'

# Default campuses (seeded into DB on first run)
DEFAULT_CAMPUSES = [
    {'name': 'De Anza College', 'city': 'Cupertino', 'zip_code': '95014', 'region': 'South Bay', 'color': 'blue'},
    {'name': 'Foothill College', 'city': 'Los Altos Hills', 'zip_code': '94022', 'region': 'South Bay', 'color': 'orange'},
    {'name': 'Chabot College', 'city': 'Hayward', 'zip_code': '94545', 'region': 'East Bay', 'color': 'purple'},
]

# Available colors for campuses
COLOR_PALETTE = ['blue', 'orange', 'purple', 'green', 'rose']

# Activity / shift types
SHIFT_TYPES = [
    'Meal Prep',
    'Packing',
    'Delivery',
    'Serving',
    'Media & Marketing',
    'Administrative',
    'Other',
]

# Service types — determines volunteer mix
SERVICE_TYPES = [
    'Pre-packed Meal',
    'Catered Meal',
]

# Shift statuses
SHIFT_STATUSES = [
    'scheduled',
    'in_progress',
    'completed',
    'cancelled',
]

# Volunteer statuses
VOLUNTEER_STATUSES = [
    'active',
    'new',
    'inactive',
    'on_leave',
]

# Signup statuses
SIGNUP_STATUSES = [
    'signed_up',
    'confirmed',
    'checked_in',
    'completed',
    'no_show',
    'cancelled',
]

# Recurring frequencies
FREQUENCIES = [
    'weekly',
    'biweekly',
    'monthly',
]

# Days of week
DAYS_OF_WEEK = [
    'Monday', 'Tuesday', 'Wednesday', 'Thursday',
    'Friday', 'Saturday', 'Sunday',
]

# --- Volunteer Mobile App ---
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'volunteers')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5 MB

SMS_DEV_MODE = True          # Show OTP on screen instead of sending SMS
OTP_EXPIRY_MINUTES = 10
MEALS_PER_SHIFT = 80         # Estimated meals served per shift

# Twilio (set as environment variables in production; leave blank for dev/log mode)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN  = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER', '')
REMINDER_HOUR = 20           # Hour (24h) to send nightly shift reminders

# Availability time slots (used on volunteer profile)
AVAILABILITY_SLOTS = ['Morning', 'Afternoon', 'Evening']

SHIFT_TYPE_INFO = {
    'Meal Prep': {
        'what': 'Preparing and portioning food — chopping, measuring, and assembling ingredients for packed meals.',
        'wear': 'Comfortable clothes, closed-toe shoes. Aprons and gloves provided.',
        'note': 'Fast-paced and team-based. Great if you like hands-on, kitchen-style work.',
    },
    'Packing': {
        'what': 'Assembling and packing meal bags or boxes for student pickup and distribution.',
        'wear': 'Comfortable clothes, closed-toe shoes.',
        'note': 'Assembly-line style. You\'ll move quickly — the team finds a good rhythm fast.',
    },
    'Delivery': {
        'what': 'Transporting packed meals or supplies to distribution points around campus.',
        'wear': 'Casual and comfortable. Expect some walking and light lifting.',
        'note': 'Good fit if you prefer staying active and moving around rather than standing in one place.',
    },
    'Serving': {
        'what': 'Distributing food directly to students at the pantry or meal station.',
        'wear': 'Comfortable, professional-casual. Gloves provided.',
        'note': 'You\'ll interact with students face to face. This is where the mission feels most real.',
    },
    'Media & Marketing': {
        'what': 'Documenting impact through photos or video, creating content, or supporting outreach.',
        'wear': 'Whatever you\'re comfortable in.',
        'note': 'Creative and flexible. Bring your phone or camera. Great if you want to tell WFM\'s story.',
    },
    'Administrative': {
        'what': 'Supporting coordination, data entry, logistics, or communications.',
        'wear': 'Casual.',
        'note': 'Helps the whole operation run smoothly. Important work that often goes unseen.',
    },
    'Other': {
        'what': 'Check the shift notes for specific details on what you\'ll be doing.',
        'wear': 'Comfortable clothes, closed-toe shoes recommended.',
        'note': 'Ask your shift coordinator if you have questions before arriving.',
    },
}

BADGE_THRESHOLDS = [
    (1,  'First Step',   '\U0001F331'),  # Seedling
    (5,  'Growing',      '\U0001F33F'),  # Herb
    (10, 'Dedicated',    '\u2B50'),      # Star
    (25, 'Champion',     '\U0001F3C6'),  # Trophy
    (50, 'Legend',       '\U0001F525'),  # Fire
]
