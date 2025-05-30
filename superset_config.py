import os

from flask_appbuilder.security.manager import AUTH_DB

# Database configuration
SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://puzzle_user:puzzle_password@postgres:5432/puzzle_swap"
)

# Security configuration
SECRET_KEY = os.environ.get(
    "SUPERSET_SECRET_KEY", "your-secret-key-change-this-in-production"
)

# Authentication type
AUTH_TYPE = AUTH_DB

# Enable CSRF protection
WTF_CSRF_ENABLED = True

# Cache configuration
CACHE_CONFIG = {
    "CACHE_TYPE": "simple",
}

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_RBAC": True,
    "EMBEDDED_SUPERSET": True,
}

# Row limit for SQL queries
ROW_LIMIT = 5000
VIZ_ROW_LIMIT = 10000

# Enable SQL Lab
SUPERSET_WEBSERVER_PORT = 8088

# Time zone
DEFAULT_TIMEZONE = "UTC"

# Enable public role for dashboards
PUBLIC_ROLE_LIKE_GAMMA = True

# Custom CSS
CUSTOM_CSS = """
.navbar-brand {
    color: #1f77b4 !important;
}
"""

# Email configuration (optional)
SMTP_HOST = "localhost"
SMTP_STARTTLS = True
SMTP_SSL = False
SMTP_USER = "superset"
SMTP_PORT = 25
SMTP_PASSWORD = ""
SMTP_MAIL_FROM = "superset@puzzle-swap.com"

# Async query configuration
RESULTS_BACKEND = None

# Enable CORS for API access
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "resources": ["*"],
    "origins": ["*"],
}

# Logging configuration
ENABLE_TIME_ROTATE = True
TIME_ROTATE_LOG_LEVEL = "INFO"
FILENAME = os.path.join(os.path.expanduser("~"), "superset.log")

# Database connection pool settings
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_timeout": 20,
    "max_overflow": 0,
}
