import os
import sys
from loguru import logger

dirname = os.path.basename(os.path.dirname(__file__))  # client


# TODO: setup_views logging doesn't work correctly
def setup_views():
    # Sink for logs coming from modules ending with '.views'.
    logger.add(
        sys.stderr,
        colorize=True,
        format="<red>{time:YYYY-MM-D HH:mm:ss,SSS!UTC}Z</red> {level} {file}:{line} {message} {extra}",
        # filter=lambda record: record["module"].endswith(
        #     ".views"
        # ),  # or record['module'] == 'views'
        filter=lambda record: record["name"] == f"{dirname}.views",
        backtrace=False,
        diagnose=False,
    )
