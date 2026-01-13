from app.db.session import Base as SQLBase

# Import all models here to ensure they are registered with SQLAlchemy
from app.models.user import User  # noqa: F401

Base = SQLBase
