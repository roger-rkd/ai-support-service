"""
Prometheus metrics for AI Support Service.

This module defines and manages Prometheus metrics for monitoring
application performance and health.
"""

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from typing import Callable
import time
import logging

logger = logging.getLogger(__name__)

# Define metrics
request_count = Counter(
    'ai_support_requests_total',
    'Total number of requests to the AI support service',
    ['endpoint', 'method', 'status']
)

request_failures = Counter(
    'ai_support_request_failures_total',
    'Total number of failed requests',
    ['endpoint', 'error_type']
)

request_latency_seconds = Histogram(
    'ai_support_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, float('inf'))
)

# RAG-specific metrics
rag_pipeline_latency = Histogram(
    'ai_support_rag_pipeline_latency_seconds',
    'RAG pipeline processing latency in seconds',
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, float('inf'))
)

rag_retrieval_latency = Histogram(
    'ai_support_rag_retrieval_latency_seconds',
    'Document retrieval latency in seconds',
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, float('inf'))
)

rag_generation_latency = Histogram(
    'ai_support_rag_generation_latency_seconds',
    'Answer generation latency in seconds',
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0, float('inf'))
)

documents_retrieved = Histogram(
    'ai_support_documents_retrieved',
    'Number of documents retrieved per query',
    buckets=(1, 2, 3, 4, 5, 10, 20, 50, float('inf'))
)


class MetricsTimer:
    """Context manager for timing operations."""

    def __init__(self, histogram: Histogram, labels: dict = None):
        """
        Initialize timer.

        Args:
            histogram: Prometheus Histogram to record to
            labels: Optional labels for the metric
        """
        self.histogram = histogram
        self.labels = labels or {}
        self.start_time = None

    def __enter__(self):
        """Start the timer."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Record the elapsed time."""
        if self.start_time is not None:
            elapsed = time.time() - self.start_time
            if self.labels:
                self.histogram.labels(**self.labels).observe(elapsed)
            else:
                self.histogram.observe(elapsed)
        return False


def record_request(endpoint: str, method: str = "POST", status: str = "success"):
    """
    Record a request to the service.

    Args:
        endpoint: The endpoint that was called
        method: HTTP method
        status: Status of the request (success/error)
    """
    request_count.labels(endpoint=endpoint, method=method, status=status).inc()


def record_failure(endpoint: str, error_type: str):
    """
    Record a failed request.

    Args:
        endpoint: The endpoint that failed
        error_type: Type of error that occurred
    """
    request_failures.labels(endpoint=endpoint, error_type=error_type).inc()
    logger.warning(f"Request failure recorded - endpoint: {endpoint}, error: {error_type}")


def record_documents_retrieved(count: int):
    """
    Record the number of documents retrieved.

    Args:
        count: Number of documents retrieved
    """
    documents_retrieved.observe(count)


def get_metrics() -> tuple[bytes, str]:
    """
    Get current metrics in Prometheus format.

    Returns:
        Tuple of (metrics_data, content_type)
    """
    return generate_latest(), CONTENT_TYPE_LATEST


def instrument_function(metric_name: str, histogram: Histogram = None):
    """
    Decorator to instrument a function with metrics.

    Args:
        metric_name: Name identifier for the metric labels
        histogram: Histogram to use (defaults to request_latency_seconds)

    Returns:
        Decorator function
    """
    if histogram is None:
        histogram = request_latency_seconds

    def decorator(func: Callable) -> Callable:
        async def async_wrapper(*args, **kwargs):
            with MetricsTimer(histogram, {"endpoint": metric_name}):
                return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            with MetricsTimer(histogram, {"endpoint": metric_name}):
                return func(*args, **kwargs)

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
