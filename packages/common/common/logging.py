import sys

import structlog

shared_processors = [
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.UnicodeDecoder(),
    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
]
if sys.stderr.isatty():
    # Pretty printing when we run in a terminal session.
    # Automatically prints pretty tracebacks when "rich" is installed
    processors = shared_processors + [
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
        structlog.dev.ConsoleRenderer(
            exception_formatter=structlog.dev.RichTracebackFormatter(
                show_locals=True,
            ),
        ),
    ]
else:
    # Print JSON when we run, e.g., in a Docker container.
    # Also print structured tracebacks.
    processors = shared_processors + [
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer(),
    ]

structlog.configure(processors)


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """
    Get a logger with the specified name.
    """
    return structlog.get_logger(context=name)


if __name__ == "__main__":
    logger = get_logger(__name__)
    logger.info("Logging system initialized", service="common", version="1.0.0")
    # Example log message
    logger.info("This is an example log message", status="success")
    # You can add more log messages as needed
    logger.info("Another log message", status="info")
    logger.error("An error occurred", error="Sample error message")
    logger.warning("This is a warning", details="Sample warning details")
    logger.debug("Debugging information", debug_info="Sample debug info")
    logger.critical(
        "Critical issue encountered",
        details="Sample critical details",
    )
    logger.info("Logging system shutdown", service="common", version="1.0.0")
    logger.info("Logging system shutdown", service="common", version="1.0.0")
    try:
        raise ZeroDivisionError("This is a test exception")
    except ZeroDivisionError as e:
        logger.exception("An exception occurred", exc_info=e)
