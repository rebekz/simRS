"""Middleware package for SIMRS."""
from app.middleware.audit import AuditLoggingMiddleware

__all__ = ["AuditLoggingMiddleware"]
