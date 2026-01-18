from app.db.session import Base as SQLBase

# Import all models here to ensure they are registered with SQLAlchemy
# Note: This file must NOT import from models that use Base from base_class
# to avoid circular imports. Models using Base from app.db.session are safe.
from app.models.user import User  # noqa: F401

Base = SQLBase
