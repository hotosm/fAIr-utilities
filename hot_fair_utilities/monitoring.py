"""
Performance monitoring and logging utilities for fAIr-utilities.

This module provides comprehensive monitoring, logging, and performance
tracking capabilities for production deployments.
"""

import functools
import logging
import time
import traceback
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional

try:
    import psutil
except ImportError:
    psutil = None


class PerformanceMonitor:
    """
    Performance monitoring and metrics collection.
    """

    def __init__(self):
        self.metrics = {}
        self.start_times = {}

    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        self.start_times[operation] = time.time()

    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration."""
        if operation not in self.start_times:
            return 0.0

        duration = time.time() - self.start_times[operation]

        if operation not in self.metrics:
            self.metrics[operation] = []

        self.metrics[operation].append(duration)
        del self.start_times[operation]

        return duration

    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for an operation."""
        if operation not in self.metrics or not self.metrics[operation]:
            return {}

        times = self.metrics[operation]
        return {
            'count': len(times),
            'total': sum(times),
            'average': sum(times) / len(times),
            'min': min(times),
            'max': max(times)
        }

    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics."""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'available_memory_mb': psutil.virtual_memory().available / (1024 * 1024)
            }
        except Exception:
            return {}

    @contextmanager
    def timer(self, operation: str):
        """Context manager for timing operations."""
        self.start_timer(operation)
        try:
            yield
        finally:
            duration = self.end_timer(operation)
            logger.info(f"Operation '{operation}' completed in {duration:.2f}s")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up comprehensive logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        format_string: Custom format string

    Returns:
        Configured logger
    """
    if format_string is None:
        format_string = (
            '%(asctime)s - %(name)s - %(levelname)s - '
            '%(filename)s:%(lineno)d - %(message)s'
        )

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[]
    )

    logger = logging.getLogger('hot_fair_utilities')
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(format_string))
        logger.addHandler(file_handler)

    logger.setLevel(getattr(logging, level.upper()))

    return logger


def monitor_performance(operation_name: Optional[str] = None):
    """
    Decorator to monitor function performance.

    Args:
        operation_name: Custom operation name (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"

            # Log function call
            logger.debug(f"Starting {op_name}")

            # Monitor system resources before
            system_before = performance_monitor.get_system_stats()

            with performance_monitor.timer(op_name):
                try:
                    result = func(*args, **kwargs)

                    # Log success
                    stats = performance_monitor.get_stats(op_name)
                    if stats:
                        logger.info(
                            f"{op_name} completed successfully. "
                            f"Duration: {stats.get('average', 0):.2f}s"
                        )

                    return result

                except Exception as e:
                    # Log error with context
                    logger.error(
                        f"{op_name} failed: {e}\n"
                        f"Traceback: {traceback.format_exc()}"
                    )
                    raise
                finally:
                    # Log system resources after
                    system_after = performance_monitor.get_system_stats()
                    if system_before and system_after:
                        memory_diff = (
                            system_after.get('memory_percent', 0) -
                            system_before.get('memory_percent', 0)
                        )
                        if abs(memory_diff) > 5:  # Log significant memory changes
                            logger.warning(
                                f"{op_name} memory usage changed by {memory_diff:.1f}%"
                            )

        return wrapper
    return decorator


def monitor_async_performance(operation_name: Optional[str] = None):
    """
    Decorator to monitor async function performance.

    Args:
        operation_name: Custom operation name (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"

            # Log function call
            logger.debug(f"Starting async {op_name}")

            # Monitor system resources before
            system_before = performance_monitor.get_system_stats()

            with performance_monitor.timer(op_name):
                try:
                    result = await func(*args, **kwargs)

                    # Log success
                    stats = performance_monitor.get_stats(op_name)
                    if stats:
                        logger.info(
                            f"Async {op_name} completed successfully. "
                            f"Duration: {stats.get('average', 0):.2f}s"
                        )

                    return result

                except Exception as e:
                    # Log error with context
                    logger.error(
                        f"Async {op_name} failed: {e}\n"
                        f"Traceback: {traceback.format_exc()}"
                    )
                    raise
                finally:
                    # Log system resources after
                    system_after = performance_monitor.get_system_stats()
                    if system_before and system_after:
                        memory_diff = (
                            system_after.get('memory_percent', 0) -
                            system_before.get('memory_percent', 0)
                        )
                        if abs(memory_diff) > 5:  # Log significant memory changes
                            logger.warning(
                                f"Async {op_name} memory usage changed by {memory_diff:.1f}%"
                            )

        return wrapper
    return decorator


def log_system_info():
    """Log current system information."""
    try:
        import platform

        logger.info("System Information:")
        logger.info(f"  Platform: {platform.platform()}")
        logger.info(f"  Python: {platform.python_version()}")
        logger.info(f"  CPU Count: {psutil.cpu_count()}")
        logger.info(f"  Total Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB")
        logger.info(f"  Available Memory: {psutil.virtual_memory().available / (1024**3):.1f} GB")

    except Exception as e:
        logger.warning(f"Could not log system info: {e}")


def get_performance_report() -> Dict[str, Any]:
    """
    Get comprehensive performance report.

    Returns:
        Dictionary with performance metrics and system stats
    """
    report = {
        'timestamp': time.time(),
        'system_stats': performance_monitor.get_system_stats(),
        'operation_stats': {}
    }

    # Get stats for all monitored operations
    for operation in performance_monitor.metrics:
        report['operation_stats'][operation] = performance_monitor.get_stats(operation)

    return report


# Set up default logger
logger = setup_logging()


class ProgressTracker:
    """
    Progress tracking for long-running operations.
    """

    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.last_log_time = self.start_time

    def update(self, increment: int = 1):
        """Update progress."""
        self.current += increment
        current_time = time.time()

        # Log progress every 10 seconds or at completion
        if (current_time - self.last_log_time > 10) or (self.current >= self.total):
            self._log_progress()
            self.last_log_time = current_time

    def _log_progress(self):
        """Log current progress."""
        if self.total > 0:
            percentage = (self.current / self.total) * 100
            elapsed = time.time() - self.start_time

            if self.current > 0:
                eta = (elapsed / self.current) * (self.total - self.current)
                logger.info(
                    f"{self.description}: {self.current}/{self.total} "
                    f"({percentage:.1f}%) - ETA: {eta:.0f}s"
                )
            else:
                logger.info(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%)")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            logger.info(f"{self.description} completed successfully")
        else:
            logger.error(f"{self.description} failed: {exc_val}")


# Export monitoring decorators for easy use
__all__ = [
    'PerformanceMonitor',
    'performance_monitor',
    'setup_logging',
    'monitor_performance',
    'monitor_async_performance',
    'log_system_info',
    'get_performance_report',
    'ProgressTracker',
    'logger'
]
