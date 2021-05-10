from logging import (
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    Formatter,
    StreamHandler,
    getLogger,
)

FORMATTER = Formatter('''
| %(levelname)s - %(asctime)s | %(name)s | %(processName)s %(threadName)s
| %(module)s.%(funcName)s [%(pathname)s:%(lineno)d]
%(message)s
'''.lstrip())

LOG_LEVELS = {
    'debug': DEBUG,
    'error': ERROR,
    'info': INFO,
    'warn': WARNING,
    'warning': WARNING,
}


def setup_logging(level_name):
    root_logger = getLogger()
    root_logger.setLevel(DEBUG)

    level = LOG_LEVELS.get(level_name, DEBUG)

    stream = StreamHandler(stream=None)
    stream.setFormatter(FORMATTER)
    stream.setLevel(level)

    root_logger.addHandler(stream)
