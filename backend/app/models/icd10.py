"""ICD-10 codes database model for STORY-012: ICD-10 Problem List

This module defines the database model for ICD-10-CM Indonesia codes.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from app.db.session import Base


class ICD10Code(Base):
    """ICD-10-CM Indonesia code reference."""
    __tablename__ = "icd10_codes"

    id = Column(Integer, primary_key=True, index=True)

    # ICD-10 code structure
    code = Column(String(10), nullable=False, unique=True, index=True)
    code_full = Column(String(20), nullable=False)  # Full code with decimal
    chapter = Column(String(10), nullable=False, index=True)  # Chapter (I-XXII)
    block = Column(String(10), nullable=False, index=True)  # Block category

    # Descriptions
    description_indonesian = Column(Text, nullable=False)
    description_english = Column(Text, nullable=True)

    # Classification
    is_chapter = Column(Boolean, server_default="false", nullable=False)
    is_block = Column(Boolean, server_default="false", nullable=False)
    is_category = Column(Boolean, server_default="false", nullable=False)  # 3-char code
    severity = Column(String(20), nullable=True)  # mild, moderate, severe

    # Additional metadata
    inclusion_terms = Column(JSONB, nullable=True)  # Included conditions
    exclusion_terms = Column(JSONB, nullable=True)  # Excluded conditions
    notes = Column(Text, nullable=True)

    # Usage tracking
    usage_count = Column(Integer, server_default="0", nullable=False)
    is_common = Column(Boolean, server_default="false", nullable=False, index=True)

    # System fields
    created_at = Column("created_at", String(50), nullable=False)
    updated_at = Column("updated_at", String(50), nullable=False)


class ICD10UserFavorite(Base):
    """User's favorite ICD-10 codes."""
    __tablename__ = "icd10_user_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    icd10_code_id = Column(Integer, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(String(50), nullable=False)
