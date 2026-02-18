from .home import home_bp
from .intelligence import intelligence_bp
from .actions import actions_bp
from .pipeline_view import pipeline_view_bp
from .progress import progress_bp
from .company import company_bp
from .settings import settings_bp
from .staff_auth import staff_auth_bp

all_blueprints = [
    staff_auth_bp,
    home_bp,
    intelligence_bp,
    actions_bp,
    pipeline_view_bp,
    progress_bp,
    company_bp,
    settings_bp,
]
