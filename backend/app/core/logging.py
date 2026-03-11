import logging
import sys

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def configure_logging(log_level: str = LOG_LEVEL, log_format: str = LOG_FORMAT):
    logging.basicConfig(
        stream=sys.stdout,
        format=log_format,
        level=getattr(logging, log_level.upper(), "INFO"),
    )
    # Silence 'uvicorn.access' unless in debug
    logging.getLogger("uvicorn.access").setLevel(logging.ERROR)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


# Usage (do this in app.main before anything else, or as a startup event):
# from app.core.logging import configure_logging
# configure_logging()
