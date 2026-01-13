"""
Prometheus metrics middleware for FastAPI.

This middleware automatically tracks HTTP request metrics
and exposes the /metrics endpoint.
"""
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match
import time
import logging

from app.core.metrics import (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress,
    errors_total
)

logger = logging.getLogger(__name__)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to track HTTP request metrics."""

    async def dispatch(self, request: Request, call_next):
        # Get endpoint name
        endpoint = self._get_endpoint_name(request)

        # Track in-progress requests
        http_requests_in_progress.labels(
            method=request.method,
            endpoint=endpoint
        ).inc()

        # Record start time
        start_time = time.time()

        try:
            # Process request
            response: Response = await call_next(request)
            status = response.status_code

            # Record metrics
            http_requests_total.labels(
                method=request.method,
                endpoint=endpoint,
                status=status
            ).inc()

            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)

            return response

        except Exception as e:
            # Record error
            logger.error(f"Request error: {e}", exc_info=True)

            http_requests_total.labels(
                method=request.method,
                endpoint=endpoint,
                status=500
            ).inc()

            errors_total.labels(
                type='request_handler',
                severity='error'
            ).inc()

            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)

            raise

        finally:
            # Decrease in-progress counter
            http_requests_in_progress.labels(
                method=request.method,
                endpoint=endpoint
            ).dec()

    def _get_endpoint_name(self, request: Request) -> str:
        """Extract endpoint name from request."""
        # Try to match route
        for route in request.app.routes:
            match, child_scope = route.matches(request.scope)
            if match == Match.FULL:
                # Return route path (e.g., /api/v1/auth/login)
                return route.path_regex.pattern.replace('\\', '').replace('<', ':').replace('>', '')
            elif match == Match.PARTIAL:
                return route.path

        # Fallback to request path
        return request.url.path


def setup_metrics(app):
    """
    Set up Prometheus metrics collection.

    This configures both the custom middleware and the
    prometheus-fastapi-instrumentator for comprehensive metrics.
    """
    # Add custom middleware
    app.add_middleware(PrometheusMiddleware)

    # Configure instrumentator for additional metrics
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_group_untemplated=True,
        should_instrument_requests_inprogress=True,
        should_instrument_requests_duration=True,
        excluded_handlers=["/metrics"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="simrs_http_requests_in_progress_instrumentator",
        inprogress_labels=True,
    )

    # Instrument the app
    instrumentator.instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=False,
        tags=["monitoring"]
    )

    logger.info("Prometheus metrics middleware configured")
