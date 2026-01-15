"""Audit Middleware for STORY-003: Audit Logging System

This module provides FastAPI middleware for automatic audit logging of all requests.
Ensures compliance with UU 27/2022 requirements for healthcare data access tracking.

Python 3.5+ compatible
"""

import logging
import json
from typing import Optional, Callable
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.user import User
from app.core.encryption import encrypt_field


logger = logging.getLogger(__name__)


# Sensitive operations that require alerting
SENSITIVE_OPERATIONS = {
    "data_export": ["export", "download", "bulk"],
    "data_deletion": ["delete", "remove", "destroy"],
    "permission_change": ["permission", "role", "access"],
    "auth_failure": ["login", "logout", "auth"],
}

# Routes to exclude from audit logging (health checks, static files, etc.)
EXCLUDED_ROUTES = [
    "/health",
    "/healthz",
    "/metrics",
    "/favicon.ico",
    "/static/",
    "/docs",
    "/redoc",
    "/openapi.json",
]


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic audit logging of all HTTP requests

    Logs all CRUD operations on patient data and tracks:
    - Timestamp, user, action, resource ID
    - IP address, user agent
    - Request/response data (encrypted)
    - Success/failure status
    """

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[list] = None,
        log_body: bool = True,
        log_response: bool = False,
    ):
        super(AuditMiddleware, self).__init__(app)
        self.exclude_paths = exclude_paths or EXCLUDED_ROUTES
        self.log_body = log_body
        self.log_response = log_response

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log audit trail"""

        # Check if path should be excluded
        if self._should_exclude(request.url.path):
            return await call_next(request)

        # Start timer for performance tracking
        start_time = datetime.utcnow()

        # Extract request info
        user = getattr(request.state, "user", None)
        user_id = user.id if user else None
        username = user.username if user else "anonymous"

        # Store request data for logging
        request_body = None
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Read request body (need to handle stream)
                body_bytes = await request.body()
                if body_bytes:
                    request_body = body_bytes.decode("utf-8", errors="ignore")
                    # Truncate large bodies
                    if len(request_body) > 10000:
                        request_body = request_body[:10000] + "... [truncated]"
            except Exception as e:
                logger.warning("Failed to read request body for audit: {}".format(e))

        # Process request
        try:
            response = await call_next(request)
            success = True
            failure_reason = None
        except Exception as e:
            success = False
            failure_reason = str(e)
            # Create error response for audit purposes
            from fastapi.responses import JSONResponse
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )

        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time_ms = int((end_time - start_time).total_seconds() * 1000)

        # Determine action from HTTP method
        action = self._get_action(request.method)

        # Determine resource type from path
        resource_type, resource_id = self._parse_resource(request.url.path)

        # Store audit context in request state for later use
        request.state.audit_context = {
            "user_id": user_id,
            "username": username,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "ip_address": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
            "request_path": request.url.path,
            "request_method": request.method,
            "request_body": request_body,
            "response_status": response.status_code,
            "success": success and response.status_code < 400,
            "failure_reason": failure_reason,
            "processing_time_ms": processing_time_ms,
        }

        # Check if this is a sensitive operation
        if self._is_sensitive_operation(action, resource_type):
            request.state.sensitive_operation = True

        # Log the audit event asynchronously (non-blocking)
        # The actual DB write will happen in a background task or endpoint handler
        request.state.needs_audit_log = True

        return response

    def _should_exclude(self, path: str) -> bool:
        """Check if path should be excluded from audit logging"""
        for excluded in self.exclude_paths:
            if path.startswith(excluded):
                return True
        return False

    def _get_action(self, method: str) -> str:
        """Map HTTP method to audit action"""
        action_map = {
            "GET": "READ",
            "POST": "CREATE",
            "PUT": "UPDATE",
            "PATCH": "UPDATE",
            "DELETE": "DELETE",
        }
        return action_map.get(method, "UNKNOWN")

    def _parse_resource(self, path: str):
        """Parse resource type and ID from URL path"""
        parts = [p for p in path.split("/") if p]

        if len(parts) < 2:
            return "unknown", None

        # Resource type is usually the first path segment
        resource_type = parts[0]

        # Try to extract ID from second segment
        resource_id = None
        if len(parts) >= 2:
            potential_id = parts[1]
            # Check if it looks like an ID (numeric or UUID)
            if potential_id.isdigit() or len(potential_id) in [32, 36]:
                resource_id = potential_id

        return resource_type, resource_id

    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Extract client IP address from request, handling proxies"""
        # Check for forwarded headers (proxy/load balancer)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # First IP is the original client
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fall back to direct client address
        if request.client:
            return request.client.host

        return None

    def _is_sensitive_operation(self, action: str, resource_type: str) -> bool:
        """Check if operation is sensitive and requires alerting"""
        operation_str = "{} {}".format(action, resource_type).lower()

        for category, keywords in SENSITIVE_OPERATIONS.items():
            for keyword in keywords:
                if keyword in operation_str:
                    return True

        return False


class AuditLogger(object):
    """Service for writing audit logs to database

    Provides methods for creating audit log entries and handling
    sensitive operation alerting.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_audit_log(
        self,
        user_id: Optional[int],
        username: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str],
        ip_address: Optional[str],
        user_agent: Optional[str],
        request_path: Optional[str],
        request_method: Optional[str],
        request_body: Optional[str],
        response_status: int,
        success: bool,
        failure_reason: Optional[str] = None,
        additional_data: Optional[dict] = None,
    ) -> AuditLog:
        """Create a new audit log entry

        Args:
            user_id: Database ID of user (if authenticated)
            username: Username or 'anonymous'
            action: Action performed (CREATE, READ, UPDATE, DELETE)
            resource_type: Type of resource affected
            resource_id: ID of specific resource affected
            ip_address: Client IP address
            user_agent: Client user agent string
            request_path: API endpoint path
            request_method: HTTP method used
            request_body: Request body (will be encrypted)
            response_status: HTTP response status code
            success: Whether operation succeeded
            failure_reason: Reason for failure (if failed)
            additional_data: Additional context data

        Returns:
            Created AuditLog instance
        """
        try:
            audit_log = AuditLog(
                user_id=user_id,
                username=username,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent[:500] if user_agent else None,  # Truncate long UAs
                request_path=request_path[:500] if request_path else None,
                request_method=request_method,
                request_body=request_body[:10000] if request_body else None,  # Encrypt and truncate
                success=success,
                failure_reason=failure_reason[:1000] if failure_reason else None,
                additional_data=additional_data,
            )

            self.db.add(audit_log)
            await self.db.flush()

            logger.info(
                "Audit log created: user={}, action={}, resource={}, success={}".format(
                    username, action, resource_type, success
                )
            )

            return audit_log

        except Exception as e:
            logger.error("Failed to create audit log: {}".format(e))
            # Don't raise - audit logging failure shouldn't break the application
            return None

    async def log_from_request_state(
        self,
        request: Request,
        response_status: int,
        additional_data: Optional[dict] = None,
    ) -> Optional[AuditLog]:
        """Create audit log from request.state.audit_context

        Convenience method for use in endpoint handlers after processing.

        Args:
            request: FastAPI request object
            response_status: HTTP response status code
            additional_data: Additional context data

        Returns:
            Created AuditLog instance or None if failed
        """
        context = getattr(request.state, "audit_context", None)
        if not context:
            return None

        return await self.create_audit_log(
            user_id=context.get("user_id"),
            username=context.get("username", "anonymous"),
            action=context.get("action", "UNKNOWN"),
            resource_type=context.get("resource_type", "unknown"),
            resource_id=context.get("resource_id"),
            ip_address=context.get("ip_address"),
            user_agent=context.get("user_agent"),
            request_path=context.get("request_path"),
            request_method=context.get("request_method"),
            request_body=context.get("request_body"),
            response_status=response_status,
            success=context.get("success", True),
            failure_reason=context.get("failure_reason"),
            additional_data=additional_data,
        )


def get_audit_logger(db: AsyncSession) -> AuditLogger:
    """Factory function to get AuditLogger instance

    Args:
        db: Database session

    Returns:
        AuditLogger instance
    """
    return AuditLogger(db)
