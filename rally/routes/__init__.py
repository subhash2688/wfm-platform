from .home import home_bp
from .shifts import shifts_bp
from .shift_detail import shift_detail_bp
from .volunteers import volunteers_bp
from .volunteer_detail import volunteer_detail_bp
from .gaps import gaps_bp
from .settings import settings_bp
from .volunteer_app import volunteer_bp
from .staff_auth import staff_auth_bp

all_blueprints = [
    staff_auth_bp,
    home_bp,
    shifts_bp,
    shift_detail_bp,
    volunteers_bp,
    volunteer_detail_bp,
    gaps_bp,
    settings_bp,
    volunteer_bp,
]
