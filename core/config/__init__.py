from .common import Common
from .production import Production  # noqa

# Attempt to import Local; fallback if it doesn't exist
try:
    from .local import Local  # noqa
except ImportError:
    # Provide a basic Local class so "DJANGO_CONFIGURATION=Local" won't break if local.py is missing.
    class Local(Common):
        DEBUG = True
        # Add any local overrides you need. Or leave as pass.
        pass

# core package init
