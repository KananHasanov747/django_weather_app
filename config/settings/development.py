from ._base import *  # noqa

# Django debug toolbar

if not TESTING:  # noqa
    INSTALLED_APPS = [
        *INSTALLED_APPS,  # noqa
        "debug_toolbar",
    ]
    MIDDLEWARE = [
        *MIDDLEWARE,  # noqa
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
