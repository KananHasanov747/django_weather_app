from ._base import *  # noqa


CONN_MAX_AGE = 600  # 10 minutes
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Apply to subdomains
SECURE_HSTS_PRELOAD = True  # Allow preloading in browsers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ServeStatic cache policy
SERVESTATIC_MAX_AGE = 31536000  # 1 year
