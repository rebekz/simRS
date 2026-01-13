"""
Audit logging middleware for FastAPI.

Intercepts all requests to patient data endpoints and logs CRUD operations
for compliance with Indonesian regulations (UU 27/2022).
"""
import json
import time
from typing import Callable, Optional, Set, List
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.encryption import encrypt_field
from app.db.session import get_db_context


# Sensitive field patterns to exclude from logs
SENSITIVE_PATTERNS = [
    "password", "secret", "token", "api_key", "credit_card", "ssn", "nik"
]

# Endpoints that require audit logging
AUDIT_ENDPOINTS = {
    # Patient data
    "POST:/api/v1/patients": ("CREATE", "Patient"),
    "GET:/api/v1/patients/{id}": ("READ", "Patient"),
    "PUT:/api/v1/patients/{id}": ("UPDATE", "Patient"),
    "DELETE:/api/v1/patients/{id}": ("DELETE", "Patient"),

    # User management
    "POST:/api/v1/users": ("CREATE", "User"),
    "PUT:/api/v1/users/{id}": ("UPDATE", "User"),
    "DELETE:/api/v1/users/{id}": ("DELETE", "User"),
    "PUT:/api/v1/users/{id}/permissions": ("UPDATE", "UserPermission"),

    # Encounters
    "POST:/api/v1/encounters": ("CREATE", "Encounter"),
    "GET:/api/v1/encounters/{id}": ("READ", "Encounter"),
    "PUT:/api/v1/encounters/{id}": ("UPDATE", "Encounter"),

    # Prescriptions
    "POST:/api/v1/prescriptions": ("CREATE", "Prescription"),
    "PUT:/api/v1/prescriptions/{id}": ("UPDATE", "Prescription"),

    # Diagnoses
    "POST:/api/v1/diagnoses": ("CREATE", "Diagnosis"),

    # Export (sensitive)
    "POST:/api/v1/export/*": ("EXPORT", "DataExport"),
    "GET:/api/v1/export/*": ("EXPORT", "DataExport"),
}

# Sensitive operations that trigger alerts
SENSITIVE_OPERATIONS = {
    "EXPORT:DataExport",
    "UPDATE:UserPermission",
    "DELETE:Patient",
    "DELETE:User",
}


def _filter_sensitive_data(data: dict) -> dict:
    """
    Remove sensitive fields from request/response data.

    Args:
        data: Dictionary to filter

    Returns:
        Filtered dictionary with sensitive values masked
    """
    if not data:
        return {}

    filtered = {}
    for key, value in data.items():
        key_lower = key.lower()
        if any(pattern in key_lower for pattern in SENSITIVE_PATTERNS):
            filtered[key] = "***REDACTED***"
        elif isinstance(value, dict):
            filtered[key] = _filter_sensitive_data(value)
        elif isinstance(value, list):
            filtered[key] = [
                _filter_sensitive_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            filtered[key] = value
    return filtered


def _extract_resource_id(path: str, path_params: dict) -> Optional[str]:
    """
    Extract resource ID from request path.

    Args:
        path: Request path
        path_params: Path parameters from route

    Returns:
        Resource ID or None
    """
    # Try to get ID from path parameters
    if "id" in path_params:
        return str(path_params["id"])

    # Try to extract from path pattern
    parts = path.split("/")
    for i, part in enumerate(parts):
        if part.isdigit() and i > 0:
            return part

    return None


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic audit logging of all requests.

    Logs are written asynchronously to minimize performance impact.
    Target overhead: <50ms per request.
    """

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[Set[str]] = None,
        exclude_methods: Optional[Set[str]] = None,
    ):
        """
        Initialize audit logging middleware.

        Args:
            app: ASGI application
            exclude_paths: Paths to exclude from logging
            exclude_methods: HTTP methods to exclude from logging
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or {
            "/health", "/health/detailed", "/health/live", "/health/ready",
            "/docs", "/redoc", "/openapi.json"
        }
        self.exclude_methods = exclude_methods or {"OPTIONS", "HEAD"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log to audit trail.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response from route handler
        """
        # Skip excluded paths and methods
        if (
            request.url.path in self.exclude_paths or
            request.method in self.exclude_methods
        ):
            return await call_next(request)

        # Start timing
        start_time = time.time()

        # Extract request info
        method = request.method
        path = request.url.path

        # Get user info if authenticated
        user_id = None
        username = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # Extract user from JWT token
            try:
                from app.core.security import decode_token
                token = auth_header[7:]
                payload = decode_token(token)
                if payload:
                    user_id = payload.get("sub")
                    # Note: We'd need to fetch username from DB if needed
            except Exception:
                pass  # Continue without user info

        # Get client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Read request body if present
        request_body = None
        if method in ("POST", "PUT", "PATCH"):
            try:
                body = await request.body()
                if body:
                    request_body = json.loads(body.decode())
                    request_body = _filter_sensitive_data(request_body)
            except Exception:
                pass

        # Capture response
        response = await call_next(request)

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # ms

        # Determine action and resource type
        endpoint_key = f"{method}:{path}"
        action, resource_type = self._get_action_resource(endpoint_key)

        if action and resource_type:
            # Queue async audit log (non-blocking)
            self._queue_audit_log(
                user_id=user_id,
                username=username,
                action=action,
                resource_type=resource_type,
                resource_id=_extract_resource_id(path, request.path_params),
                ip_address=ip_address,
                user_agent=user_agent,
                request_path=path,
                request_method=method,
                success=response.status_code < 400,
                status_code=response.status_code,
                request_body=request_body,
            )

        return response

    def _get_action_resource(self, endpoint_key: str) -> tuple:
        """
        Determine action and resource type from endpoint.

        Args:
            endpoint_key: Method:path endpoint key

        Returns:
            Tuple of (action, resource_type) or (None, None)
        """
        # Direct match
        if endpoint_key in AUDIT_ENDPOINTS:
            return AUDIT_ENDPOINTS[endpoint_key]

        # Wildcard match for export
        for pattern, (action, resource) in AUDIT_ENDPOINTS.items():
            if "*" in pattern:
                method, path_pattern = pattern.split(":")
                if endpoint_key.startswith(f"{method}:{path_pattern.rstrip('*')}"):
                    return (action, resource)

        return (None, None)

    def _queue_audit_log(
        self,
        user_id: Optional[int],
        username: Optional[str],
        action: str,
        resource_type: str,
        resource_id: Optional[str],
        ip_address: Optional[str],
        user_agent: Optional[str],
        request_path: str,
        request_method: str,
        success: bool,
        status_code: int,
        request_body: Optional[dict],
    ):
        """
        Queue audit log entry for async writing.

        Args:
            user_id: User ID if authenticated
            username: Username
            action: CRUD action performed
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            ip_address: Client IP address
            user_agent: Client user agent
            request_path: Request path
            request_method: HTTP method
            success: Whether operation succeeded
            status_code: HTTP status code
            request_body: Filtered request body
        """
        # Import here to avoid circular dependency
        import asyncio
        from app.crud.audit_log import create_audit_log

        async def _write_log():
            """Write audit log in background."""
            try:
                async with get_db_context() as db:
                    # Encrypt request body
                    encrypted_body = None
                    if request_body:
                        encrypted_body = encrypt_field(json.dumps(request_body))

                    await create_audit_log(
                        db=db,
                        action=action,
                        resource_type=resource_type,
                        user_id=int(user_id) if user_id else None,
                        username=username,
                        resource_id=resource_id,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        request_path=request_path,
                        request_method=request_method,
                        success=success,
                        failure_reason=None if success else f"HTTP {status_code}",
                        additional_data={
                            "status_code": status_code,
                            "request_body_encrypted": encrypted_body,
                        } if encrypted_body else {"status_code": status_code},
                    )

                    # Check if this is a sensitive operation that needs alerting
                    operation_key = f"{action}:{resource_type}"
                    if operation_key in SENSITIVE_OPERATIONS and success:
                        self._trigger_alert(
                            db=db,
                            user_id=user_id,
                            username=username,
                            action=action,
                            resource_type=resource_type,
                            resource_id=resource_id,
                            ip_address=ip_address,
                        )

            except Exception as e:
                # Log to stderr but don't fail the request
                import sys
                print(f"Audit log write failed: {str(e)}", file=sys.stderr)

        # Schedule background task
        try:
            asyncio.create_task(_write_log())
        except RuntimeError:
            # No event loop - run synchronously (shouldn't happen in FastAPI)
            import asyncio
            loop = asyncio.get_event_loop()
            loop.run_until_complete(_write_log())

    def _trigger_alert(
        self,
        db: AsyncSession,
        user_id: Optional[int],
        username: Optional[str],
        action: str,
        resource_type: str,
        resource_id: Optional[str],
        ip_address: Optional[str],
    ):
        """
        Trigger alert for sensitive operation.

        Args:
            db: Database session
            user_id: User who performed action
            username: Username
            action: Action performed
            resource_type: Type of resource
            resource_id: Resource ID
            ip_address: Client IP
        """
        # TODO: Implement real alerting (WebSocket, email, etc.)
        # For now, just log to stdout
        alert_msg = (
            f"[AUDIT ALERT] Sensitive operation: {action} {resource_type}"
            f" by {username} ({user_id}) from {ip_address}"
        )
        if resource_id:
            alert_msg += f" on resource {resource_id}"
        print(alert_msg)
