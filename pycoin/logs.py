import logging
import logging.config


BLACK = "\u001b[30m"
RED = "\u001b[31m"
GREEN = "\u001b[32m"
YELLOW = "\u001b[33m"
BLUE = "\u001b[34m"
MAGENTA = "\u001b[35m"
CYAN = "\u001b[36m"
WHITE = "\u001b[37m"
RESET = "\u001b[0m"


class ColoredFormatter(logging.Formatter):
    LEVEL_FMT = {
        logging.DEBUG: f'[{BLUE}%(levelname)s{RESET}] %(message)s',
        logging.INFO: f'[{YELLOW}%(levelname)s{RESET}] %(message)s',
        logging.WARNING: f'[{MAGENTA}%(levelname)s{RESET}] %(message)s',
        logging.ERROR: f'[{RED}%(levelname)s{RESET}] %(message)s',
        logging.CRITICAL: f'[{RED}%(levelname)s{RESET}] %(message)s',
        logging.FATAL: f'[{RED}%(levelname)s{RESET}] %(message)s',
    }

    def format(self, record: logging.LogRecord) -> str:
        fmt = self.LEVEL_FMT[record.levelno]
        formatter = logging.Formatter(fmt)
        return formatter.format(record)


log_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'colored': {
            '()': ColoredFormatter
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
        },
    },
    'loggers': {
        'pycoin': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

logging.config.dictConfig(log_config)
logger = logging.getLogger('pycoin')
