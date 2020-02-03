import logging
import sys

import structlog

DEFAULT_LIBRARY_LOGGING_LEVEL = logging.WARN


def setup_logging(
    log_level=logging.WARN, log_verbose=False, log_json=False, log_file=None
):
    if isinstance(log_level, str):
        log_level = logging.getLevelName(log_level)

    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.processors.UnicodeDecoder(),
        structlog.processors.format_exc_info,
        structlog.processors.StackInfoRenderer(),
    ]

    structlog.configure(
        processors=(
            shared_processors
            + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter]
        ),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    processor = structlog.dev.ConsoleRenderer(colors=True)
    if log_json:
        processor = structlog.processors.JSONRenderer()

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=processor, foreign_pre_chain=shared_processors
    )

    if log_file:
        handler = logging.FileHandler(log_file, encoding="utf-8")
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    if not log_verbose:
        lib_log_level = DEFAULT_LIBRARY_LOGGING_LEVEL
        if log_level > lib_log_level:
            lib_log_level = log_level

        logging.getLogger("aio_pika").setLevel(lib_log_level)
        logging.getLogger("asyncio").setLevel(lib_log_level)
        logging.getLogger("heatspreader").setLevel(lib_log_level)
        logging.getLogger("keystoneauth").setLevel(lib_log_level)
        logging.getLogger("openstack").setLevel(lib_log_level)
        logging.getLogger("stevedore").setLevel(lib_log_level)
        logging.getLogger("urllib3").setLevel(lib_log_level)

    sys.excepthook = lambda ex_type, ex_value, tb: structlog.get_logger(
        "sys.excepthook"
    ).critical(event="uncaught_exception", exc_info=(ex_type, ex_value, tb))
