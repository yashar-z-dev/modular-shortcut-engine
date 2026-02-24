# 100/100

from typing import Optional
import logging
from logging import LogRecord
import sys
import inspect


class RootLogger:
    """
    RootLogger sets up a central logging system for the application.

    Features:
    - Single root logger configuration
    - Logs to console and optionally to a file
    - Automatically detects calling class and function or module and function
    - Allows all modules to use logging.info(), logging.error(), etc. without defining a logger
    """

    @staticmethod
    def setup(log_file: Optional[str] = None, level: int = logging.INFO):
        """
        Initialize the root logger.

        Parameters:
        - log_file (str, optional): Path to a file where logs will be saved. Defaults to None (console only).
        - level (int, optional): Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to logging.INFO.
        """

        logger = logging.getLogger()
        logger.setLevel(level)
        logger.handlers.clear()

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(caller)s - %(message)s'
        )

        class CallerFilter(logging.Filter):
            """Filter that adds caller information (Class.Method or Module.Function)."""

            def filter(self, record: LogRecord):
                # Inspect call stack
                stack = inspect.stack()
                record.caller = "<unknown>"

                # Iterate over stack frames to find the first external caller
                for frame_info in stack[1:]:
                    frame = frame_info.frame
                    func_name = frame.f_code.co_name
                    module_name = frame.f_globals.get('__name__', '')

                    # Skip frames inside logging module
                    if module_name.startswith('logging'):
                        continue

                    # Check if it's a method of a class
                    if 'self' in frame.f_locals:
                        cls_name = frame.f_locals['self'].__class__.__name__
                        record.caller = f"{cls_name}.{func_name}"
                        break

                    # Check for standalone function
                    elif func_name != '<module>':
                        record.caller = f"{module_name}.{func_name}"
                        break

                return True

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        ch.addFilter(CallerFilter())
        logger.addHandler(ch)

        # Optional file handler
        if log_file:
            fh = logging.FileHandler(log_file, encoding='utf-8')
            fh.setFormatter(formatter)
            fh.addFilter(CallerFilter())
            logger.addHandler(fh)
