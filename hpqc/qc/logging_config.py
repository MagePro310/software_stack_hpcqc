"""Centralized logging configuration for HPQC Quantum Server."""

import logging
import os
import sys

# Standard ANSI escape codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

LEVEL_COLORS = {
    logging.DEBUG: DIM + WHITE,
    logging.INFO: GREEN,
    logging.WARNING: YELLOW,
    logging.ERROR: RED,
    logging.CRITICAL: BOLD + RED,
}

STAGE_COLORS = {
    "[STARTUP]": BOLD + GREEN,
    "[SERVER]": BOLD + CYAN,
    "[REQUEST]": CYAN,
    "[QUEUE]": BLUE,
    "[EXEC]": MAGENTA,
    "[SUCCESS]": BOLD + GREEN,
    "[ERROR]": BOLD + RED,
    "[SHUTDOWN]": YELLOW,
}

NOISY_LOGGERS = [
    "qiskit",
    "qiskit.passmanager",
    "qiskit.passmanager.base_tasks",
    "qiskit.compiler",
    "qiskit.compiler.transpiler",
    "qiskit.transpiler",
    "qiskit_aer",
    "stevedore",
    "stevedore.extension",
    "urllib3",
    "grpc",
]


class QCLogFormatter(logging.Formatter):
    """Custom formatter with clean timestamps, level alignment, and optional ANSI colors."""

    def __init__(self, use_color: bool = True):
        super().__init__(datefmt="%Y-%m-%d %H:%M:%S")
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, self.datefmt)
        levelname = record.levelname
        msg = record.getMessage()

        if self.use_color:
            level_color = LEVEL_COLORS.get(record.levelno, "")
            # Colorize stage tags like [REQUEST], [SUCCESS], etc.
            for tag, color in STAGE_COLORS.items():
                if tag in msg:
                    msg = msg.replace(tag, f"{color}{tag}{RESET}")

            formatted = f"{DIM}{timestamp}{RESET} [{level_color}{levelname:<5}{RESET}] {msg}"
        else:
            formatted = f"{timestamp} [{levelname:<5}] {msg}"

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
            if record.exc_text:
                formatted = f"{formatted}\n{record.exc_text}"

        return formatted


def setup_qc_logging(
    log_level: str | int | None = None,
    enable_color: bool | None = None,
    debug_qiskit: bool | None = None,
) -> logging.Logger:
    """Configures server logging with clean terminal output and silenced Qiskit noise.

    Args:
        log_level: Desired log level (e.g., "DEBUG", "INFO", "WARNING", "ERROR").
                   Defaults to env var HPQC_LOG_LEVEL or INFO.
        enable_color: Force enable/disable colors. Defaults to auto-detection (TTY / HPQC_LOG_COLOR).
        debug_qiskit: Whether to allow verbose Qiskit transpiler passes (default False).
    """
    if log_level is None:
        log_level = os.getenv("HPQC_LOG_LEVEL", "INFO").upper()

    if isinstance(log_level, str):
        level_value = getattr(logging, log_level.upper(), logging.INFO)
    else:
        level_value = log_level

    if enable_color is None:
        env_color = os.getenv("HPQC_LOG_COLOR", "").lower()
        if env_color in ("1", "true", "yes"):
            enable_color = True
        elif env_color in ("0", "false", "no"):
            enable_color = False
        elif "NO_COLOR" in os.environ:
            enable_color = False
        else:
            enable_color = sys.stdout.isatty() or os.getenv("PYTHONUNBUFFERED") == "1"

    if debug_qiskit is None:
        debug_qiskit = os.getenv("HPQC_DEBUG_QISKIT", "0").lower() in ("1", "true", "yes")

    root_logger = logging.getLogger()
    root_logger.setLevel(level_value)

    # Remove non-testing handlers to avoid duplicate output in console
    for handler in list(root_logger.handlers):
        if not handler.__class__.__name__.startswith("LogCapture"):
            root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level_value)
    console_handler.setFormatter(QCLogFormatter(use_color=enable_color))
    root_logger.addHandler(console_handler)

    # Configure noise reduction for third-party libraries (especially Qiskit passmanager)
    third_party_level = logging.INFO if debug_qiskit else logging.WARNING
    for noisy_name in NOISY_LOGGERS:
        noisy_logger = logging.getLogger(noisy_name)
        noisy_logger.setLevel(third_party_level)
        noisy_logger.propagate = True

    return logging.getLogger("hpqc.qc")

