import logging
import sys

LOGGING_CONFIG = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "basic",
            "stream": sys.stdout,
        },
    },
    "formatters": {
        "basic": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}


logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger("user-management-service")
