import logging.config

from dms import settings


def setup():
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s.%(msecs)03d][%(name)s][%(filename)s:%(funcName)s:%(lineno)d][%(levelname)s]: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "default": {"class": "logging.StreamHandler", "formatter": "default"}
            },
            "root": {
                "level": ["INFO", "DEBUG"][settings.DEBUG],
                "handlers": ["default"],
                "propagate": True,
            },
        }
    )
