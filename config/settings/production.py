from ._base import *  # noqa

DEBUG = False

CSRF_TRUSTED_ORIGINS = env("DJANGO_CSRF_TRUSTED_HOSTS").split(",")  # noqa
# Uncomment if using http protocol in production
# CSRF_COOKIE_SECURE = False
# CSRF_COOKIE_HTTPONLY = False
# SESSION_COOKIE_SECURE = False
# SECURE_CROSS_ORIGIN_OPENER_POLICY = None
# USE_X_FORWARDED_HOST = True
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ServeStatic cache policy
SERVESTATIC_MAX_AGE = 31536000  # 1 year
