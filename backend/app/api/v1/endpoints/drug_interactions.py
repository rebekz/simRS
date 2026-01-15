"""Drug Interaction Database Management API endpoints for STORY-026

This module provides admin API endpoints for:
- Drug interaction management (CRUD)
- Custom interaction rule management
- Interaction database statistics
- Database seeding with common interactions
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_admin_user, get_db
from app.models.user import User
from app.schemas.medication import (
    DrugInteraction as DrugInteractionResponse,
    InteractionType, InteractionSeverity,
)
from app.crud import drug_interactions as crud


router = APIRouter()


# =============================================================================
# Drug Interaction Management Endpoints (Admin)
# =============================================================================

@router.post("/drug-interactions", response_model=DrugInteractionResponse)
async def create_drug_interaction(
    interaction_type: InteractionType,
    severity: InteractionSeverity,
    drug_1_id: int,
    drug_2_id: Optional[int] = None,
    description: str = Query(...),
    recommendation: str = Query(...),
    disease_code: Optional[str] = None,
    disease_name: Optional[str] = None,
    references: Optional[str] = Query(None),  # JSON string
    requires_override: bool = True,
    evidence_level: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Create a new drug interaction (admin only)"""
    import json

    refs_list = json.loads(references) if references else None

    # Check for duplicate
    exists = await crud.check_interaction_exists(
        db=db,
        drug_1_id=drug_1_id,
        drug_2_id=drug_2_id,
        interaction_type=interaction_type,
    )

    if exists:
        raise HTTPException(status_code=400, detail="Interaction already exists")

    interaction = await crud.create_drug_interaction(
        db=db,
        interaction_type=interaction_type,
        severity=severity,
        drug_1_id=drug_1_id,
        drug_2_id=drug_2_id,
        description=description,
        recommendation=recommendation,
        disease_code=disease_code,
        disease_name=disease_name,
        references=refs_list,
        requires_override=requires_override,
        evidence_level=evidence_level,
    )

    return DrugInteractionResponse(
        id=interaction.id,
        interaction_type=interaction.interaction_type,
        severity=interaction.severity,
        drug_1_id=interaction.drug_1_id,
        drug_1_name=interaction.drug_1_name,
        drug_2_id=interaction.drug_2_id,
        drug_2_name=interaction.drug_2_name,
        description=interaction.description,
        recommendation=interaction.recommendation,
        references=json.loads(interaction.references) if interaction.references else None,
        requires_override=interaction.requires_override,
    )


@router.get("/drug-interactions")
async def list_drug_interactions(
    interaction_type: Optional[InteractionType] = Query(None),
    severity: Optional[InteractionSeverity] = Query(None),
    drug_id: Optional[int] = Query(None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """List drug interactions with filtering (admin only)"""
    import json

    interactions, total = await crud.list_drug_interactions(
        db=db,
        interaction_type=interaction_type,
        severity=severity,
        drug_id=drug_id,
        page=page,
        page_size=page_size,
    )

    response_data = []
    for interaction in interactions:
        response_data.append(DrugInteractionResponse(
            id=interaction.id,
            interaction_type=interaction.interaction_type,
            severity=interaction.severity,
            drug_1_id=interaction.drug_1_id,
            drug_1_name=interaction.drug_1_name,
            drug_2_id=interaction.drug_2_id,
            drug_2_name=interaction.drug_2_name,
            description=interaction.description,
            recommendation=interaction.recommendation,
            references=json.loads(interaction.references) if interaction.references else None,
            requires_override=interaction.requires_override,
        ))

    return {
        "interactions": response_data,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/drug-interactions/statistics")
async def get_interaction_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get interaction database statistics (admin only)"""
    stats = await crud.get_interaction_statistics(db=db)
    return stats


@router.post("/drug-interactions/seed")
async def seed_drug_interactions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Seed database with common drug interactions (admin only)"""
    result = await crud.seed_common_interactions(db=db)
    return {
        "message": "Drug interaction seeding completed",
        "created": result["created"],
        "skipped": result["skipped"],
        "errors": result["errors"],
    }


# =============================================================================
# Custom Interaction Rule Management Endpoints (Admin)
# =============================================================================

@router.get("/custom-interaction-rules")
async def list_custom_rules(
    is_active: Optional[bool] = Query(None),
    rule_type: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """List custom interaction rules (admin only)"""
    import json

    rules, total = await crud.list_custom_rules(
        db=db,
        is_active=is_active,
        rule_type=rule_type,
        page=page,
        page_size=page_size,
    )

    response_data = []
    for rule in rules:
        response_data.append({
            "id": rule.id,
            "name": rule.name,
            "description": rule.description,
            "rule_type": rule.rule_type,
            "drug_ids": json.loads(rule.drug_ids) if rule.drug_ids else [],
            "drug_names": json.loads(rule.drug_names) if rule.drug_names else [],
            "age_min": rule.age_min,
            "age_max": rule.age_max,
            "renal_dose_adjustment": rule.renal_dose_adjustment,
            "hepatic_dose_adjustment": rule.hepatic_dose_adjustment,
            "pregnancy_contraindication": rule.pregnancy_contraindication,
            "breastfeeding_contraindication": rule.breastfeeding_contraindication,
            "severity": rule.severity,
            "action_required": rule.action_required,
            "is_active": rule.is_active,
            "created_by": rule.created_by,
            "created_at": rule.created_at,
            "updated_at": rule.updated_at,
        })

    return {
        "rules": response_data,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
