from ._base import *

DEBUG = True

# Uncomment if using http protocol in production
# CSRF_COOKIE_SECURE = False
# CSRF_COOKIE_HTTPONLY = False
# SESSION_COOKIE_SECURE = False
# SECURE_CROSS_ORIGIN_OPENER_POLICY = None
# USE_X_FORWARDED_HOST = True
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ServeStatic cache policy
SERVESTATIC_MAX_AGE = 31536000  # 1 year
