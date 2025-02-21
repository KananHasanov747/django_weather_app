import os
import sys
from loguru import logger

dirname = os.path.basename(os.path.dirname(__file__))


# TODO: setup_views logging doesn't work
def setup_views():
    # Sink for logs coming from modules ending with '.views'.
    logger.add(
        sys.stderr,
        colorize=True,
        format="<red>{time:YYYY-MM-D HH:mm:ss,SSS!UTC}Z</red> {level} {message} {extra}",
        filter=lambda record: record["module"].endswith(
            ".views"
        ),  # or record['module'] == 'views'
        backtrace=False,
        diagnose=False,
    )
