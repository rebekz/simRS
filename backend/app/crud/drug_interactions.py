"""Drug Interaction Database CRUD Operations for STORY-026

This module provides CRUD operations for:
- Drug interaction management
- Custom interaction rules
- Interaction database seeding
"""
from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import json

from app.models.medication import DrugInteraction, CustomInteractionRule
from app.models.inventory import Drug
from app.schemas.medication import InteractionType, InteractionSeverity


# =============================================================================
# Drug Interaction CRUD
# =============================================================================

async def get_drug_interaction(
    db: AsyncSession,
    interaction_id: int,
) -> Optional[DrugInteraction]:
    """Get drug interaction by ID"""
    stmt = (
        select(DrugInteraction)
        .options(selectinload(DrugInteraction.drug_1), selectinload(DrugInteraction.drug_2))
        .where(DrugInteraction.id == interaction_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_drug_interactions(
    db: AsyncSession,
    interaction_type: Optional[InteractionType] = None,
    severity: Optional[InteractionSeverity] = None,
    drug_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[DrugInteraction], int]:
    """List drug interactions with filtering"""
    conditions = []

    if interaction_type:
        conditions.append(DrugInteraction.interaction_type == interaction_type)
    if severity:
        conditions.append(DrugInteraction.severity == severity)
    if drug_id:
        conditions.append(
            or_(
                DrugInteraction.drug_1_id == drug_id,
                DrugInteraction.drug_2_id == drug_id,
            )
        )

    # Build query
    stmt = select(DrugInteraction)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Get total count
    count_stmt = select(DrugInteraction.id)
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total = len(count_result.all())

    # Apply pagination and ordering
    stmt = stmt.options(selectinload(DrugInteraction.drug_1), selectinload(DrugInteraction.drug_2))
    stmt = stmt.order_by(DrugInteraction.severity.desc(), DrugInteraction.drug_1_name)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    interactions = result.scalars().all()

    return list(interactions), total


async def create_drug_interaction(
    db: AsyncSession,
    interaction_type: InteractionType,
    severity: InteractionSeverity,
    drug_1_id: int,
    drug_2_id: Optional[int],
    description: str,
    recommendation: str,
    disease_code: Optional[str] = None,
    disease_name: Optional[str] = None,
    references: Optional[List[str]] = None,
    requires_override: bool = True,
    evidence_level: Optional[str] = None,
) -> DrugInteraction:
    """Create a new drug interaction"""
    # Get drug names
    drug_1_stmt = select(Drug).where(Drug.id == drug_1_id)
    drug_1_result = await db.execute(drug_1_stmt)
    drug_1 = drug_1_result.scalar_one_or_none()
    drug_1_name = drug_1.generic_name if drug_1 else f"Drug {drug_1_id}"

    drug_2_name = None
    if drug_2_id:
        drug_2_stmt = select(Drug).where(Drug.id == drug_2_id)
        drug_2_result = await db.execute(drug_2_stmt)
        drug_2 = drug_2_result.scalar_one_or_none()
        drug_2_name = drug_2.generic_name if drug_2 else f"Drug {drug_2_id}"

    interaction = DrugInteraction(
        interaction_type=interaction_type,
        severity=severity,
        drug_1_id=drug_1_id,
        drug_1_name=drug_1_name,
        drug_2_id=drug_2_id,
        drug_2_name=drug_2_name,
        disease_code=disease_code,
        disease_name=disease_name,
        description=description,
        recommendation=recommendation,
        references=json.dumps(references) if references else None,
        requires_override=requires_override,
        evidence_level=evidence_level,
    )

    db.add(interaction)
    await db.commit()
    await db.refresh(interaction)

    return interaction


async def update_drug_interaction(
    db: AsyncSession,
    interaction_id: int,
    severity: Optional[InteractionSeverity] = None,
    description: Optional[str] = None,
    recommendation: Optional[str] = None,
    references: Optional[List[str]] = None,
    requires_override: Optional[bool] = None,
    evidence_level: Optional[str] = None,
) -> Optional[DrugInteraction]:
    """Update drug interaction"""
    interaction = await get_drug_interaction(db, interaction_id)
    if not interaction:
        return None

    if severity is not None:
        interaction.severity = severity
    if description is not None:
        interaction.description = description
    if recommendation is not None:
        interaction.recommendation = recommendation
    if references is not None:
        interaction.references = json.dumps(references)
    if requires_override is not None:
        interaction.requires_override = requires_override
    if evidence_level is not None:
        interaction.evidence_level = evidence_level

    await db.commit()
    await db.refresh(interaction)

    return interaction


async def delete_drug_interaction(
    db: AsyncSession,
    interaction_id: int,
) -> bool:
    """Delete a drug interaction"""
    interaction = await get_drug_interaction(db, interaction_id)
    if not interaction:
        return False

    await db.delete(interaction)
    await db.commit()

    return True


async def check_interaction_exists(
    db: AsyncSession,
    drug_1_id: int,
    drug_2_id: Optional[int],
    interaction_type: InteractionType,
) -> bool:
    """Check if an interaction already exists"""
    conditions = [
        DrugInteraction.drug_1_id == drug_1_id,
        DrugInteraction.interaction_type == interaction_type,
    ]

    if drug_2_id:
        conditions.append(DrugInteraction.drug_2_id == drug_2_id)
    else:
        conditions.append(DrugInteraction.drug_2_id.is_(None))

    stmt = select(DrugInteraction).where(and_(*conditions))
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


# =============================================================================
# Custom Interaction Rule CRUD
# =============================================================================

async def get_custom_rule(
    db: AsyncSession,
    rule_id: int,
) -> Optional[CustomInteractionRule]:
    """Get custom interaction rule by ID"""
    stmt = select(CustomInteractionRule).where(CustomInteractionRule.id == rule_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_custom_rules(
    db: AsyncSession,
    is_active: Optional[bool] = None,
    rule_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[CustomInteractionRule], int]:
    """List custom interaction rules"""
    conditions = []

    if is_active is not None:
        conditions.append(CustomInteractionRule.is_active == is_active)
    if rule_type:
        conditions.append(CustomInteractionRule.rule_type == rule_type)

    # Build query
    stmt = select(CustomInteractionRule)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Get total count
    count_stmt = select(CustomInteractionRule.id)
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total = len(count_result.all())

    # Apply pagination and ordering
    stmt = stmt.order_by(CustomInteractionRule.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    rules = result.scalars().all()

    return list(rules), total


async def create_custom_rule(
    db: AsyncSession,
    name: str,
    description: str,
    rule_type: str,
    drug_ids: List[int],
    severity: InteractionSeverity,
    action_required: Optional[str] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    renal_dose_adjustment: bool = False,
    hepatic_dose_adjustment: bool = False,
    pregnancy_contraindication: bool = False,
    breastfeeding_contraindication: bool = False,
    created_by: int = None,
) -> CustomInteractionRule:
    """Create a custom interaction rule"""
    # Get drug names
    drug_names = []
    for drug_id in drug_ids:
        drug_stmt = select(Drug).where(Drug.id == drug_id)
        drug_result = await db.execute(drug_stmt)
        drug = drug_result.scalar_one_or_none()
        if drug:
            drug_names.append(drug.generic_name)

    rule = CustomInteractionRule(
        name=name,
        description=description,
        rule_type=rule_type,
        drug_ids=json.dumps(drug_ids),
        drug_names=json.dumps(drug_names) if drug_names else None,
        age_min=age_min,
        age_max=age_max,
        renal_dose_adjustment=renal_dose_adjustment,
        hepatic_dose_adjustment=hepatic_dose_adjustment,
        pregnancy_contraindication=pregnancy_contraindication,
        breastfeeding_contraindication=breastfeeding_contraindication,
        severity=severity,
        action_required=action_required,
        created_by=created_by,
    )

    db.add(rule)
    await db.commit()
    await db.refresh(rule)

    return rule


async def update_custom_rule(
    db: AsyncSession,
    rule_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    severity: Optional[InteractionSeverity] = None,
    action_required: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Optional[CustomInteractionRule]:
    """Update custom interaction rule"""
    rule = await get_custom_rule(db, rule_id)
    if not rule:
        return None

    if name is not None:
        rule.name = name
    if description is not None:
        rule.description = description
    if severity is not None:
        rule.severity = severity
    if action_required is not None:
        rule.action_required = action_required
    if is_active is not None:
        rule.is_active = is_active

    await db.commit()
    await db.refresh(rule)

    return rule


async def delete_custom_rule(
    db: AsyncSession,
    rule_id: int,
) -> bool:
    """Delete a custom interaction rule"""
    rule = await get_custom_rule(db, rule_id)
    if not rule:
        return False

    await db.delete(rule)
    await db.commit()

    return True


# =============================================================================
# Interaction Statistics
# =============================================================================

async def get_interaction_statistics(
    db: AsyncSession,
) -> dict:
    """Get statistics about drug interactions in database"""
    # Count by type
    type_counts = {}
    for interaction_type in InteractionType:
        stmt = select(DrugInteraction).where(DrugInteraction.interaction_type == interaction_type)
        result = await db.execute(stmt)
        count = len(result.all())
        type_counts[interaction_type.value] = count

    # Count by severity
    severity_counts = {}
    for severity in InteractionSeverity:
        stmt = select(DrugInteraction).where(DrugInteraction.severity == severity)
        result = await db.execute(stmt)
        count = len(result.all())
        severity_counts[severity.value] = count

    # Total count
    total_stmt = select(DrugInteraction)
    total_result = await db.execute(total_stmt)
    total = len(total_result.all())

    # Custom rules count
    custom_stmt = select(CustomInteractionRule).where(CustomInteractionRule.is_active == True)
    custom_result = await db.execute(custom_stmt)
    custom_total = len(custom_result.all())

    return {
        "total_interactions": total,
        "by_type": type_counts,
        "by_severity": severity_counts,
        "active_custom_rules": custom_total,
    }


# =============================================================================
# Common Drug Interactions (Initial Data)
# =============================================================================

COMMON_INTERACTIONS = [
    # ACE Inhibitors + Potassium Supplements → Hyperkalemia
    {
        "interaction_type": InteractionType.DRUG_DRUG,
        "severity": InteractionSeverity.MODERATE,
        "drug_1_code": "ACEI",  # Will be mapped to actual drug IDs
        "drug_2_code": "POTASSIUM",
        "description": "ACE inhibitors may increase serum potassium levels. Concurrent use with potassium supplements may cause hyperkalemia.",
        "recommendation": "Monitor serum potassium regularly. Consider potassium supplementation only if hypokalemia is present and monitor frequently.",
        "evidence_level": "B",
    },
    # Warfarin + NSAIDs → Increased bleeding risk
    {
        "interaction_type": InteractionType.DRUG_DRUG,
        "severity": InteractionSeverity.SEVERE,
        "drug_1_code": "WARFARIN",
        "drug_2_code": "NSAID",
        "description": "NSAIDs may enhance the anticoagulant effect of warfarin, increasing bleeding risk.",
        "recommendation": "Avoid concurrent use if possible. If co-administration is necessary, monitor INR and bleeding signs closely.",
        "evidence_level": "A",
    },
    # Digoxin + Verapamil → Increased digoxin levels
    {
        "interaction_type": InteractionType.DRUG_DRUG,
        "severity": InteractionSeverity.MODERATE,
        "drug_1_code": "DIGOXIN",
        "drug_2_code": "VERAPAMIL",
        "description": "Verapamil may increase serum digoxin levels by reducing renal clearance.",
        "recommendation": "Monitor digoxin levels and reduce digoxin dose by 50% when verapamil is started. Watch for digoxin toxicity (nausea, visual disturbances).",
        "evidence_level": "A",
    },
    # Beta-blockers + Calcium Channel Blockers → Bradycardia
    {
        "interaction_type": InteractionType.DRUG_DRUG,
        "severity": InteractionSeverity.MODERATE,
        "drug_1_code": "BETABLOCKER",
        "drug_2_code": "CCB",
        "description": "Combined use may cause excessive bradycardia and heart block.",
        "recommendation": "Monitor heart rate and blood pressure closely. Dose reduction may be necessary.",
        "evidence_level": "B",
    },
    # SSRIs + MAOIs → Serotonin Syndrome
    {
        "interaction_type": InteractionType.DRUG_DRUG,
        "severity": InteractionSeverity.CONTRAINDICATED,
        "drug_1_code": "SSRI",
        "drug_2_code": "MAOI",
        "description": "Concurrent use may cause serotonin syndrome (hyperthermia, rigidity, myoclonus, autonomic instability).",
        "recommendation": "CONTRAINDICATED. Allow at least 2 weeks washout period when switching from MAOIs to SSRIs.",
        "evidence_level": "A",
    },
    # Quinolones + Antacids → Reduced absorption
    {
        "interaction_type": InteractionType.DRUG_FOOD,
        "severity": InteractionSeverity.MILD,
        "drug_1_code": "QUINOLONE",
        "drug_2_code": "ANTACID",
        "description": "Antacids containing magnesium or aluminum may reduce quinolone absorption.",
        "recommendation": "Administer quinolones at least 2 hours before or 6 hours after antacids.",
        "evidence_level": "B",
    },
    # Statins + Grapefruit juice → Increased statin levels
    {
        "interaction_type": InteractionType.DRUG_FOOD,
        "severity": InteractionSeverity.MODERATE,
        "drug_1_code": "STATIN",
        "drug_2_code": "GRAPEFRUIT",
        "description": "Grapefruit juice inhibits CYP3A4, increasing statin levels and risk of myopathy.",
        "recommendation": "Advise patients to avoid grapefruit juice while taking statins, especially simvastatin.",
        "evidence_level": "B",
    },
    # ACE Inhibitors + Pregnancy → Contraindicated
    {
        "interaction_type": InteractionType.DRUG_DISEASE,
        "severity": InteractionSeverity.CONTRAINDICATED,
        "drug_1_code": "ACEI",
        "disease_code": "O09",  # Pregnancy (ICD-10)
        "disease_name": "Pregnancy",
        "description": "ACE inhibitors may cause fetal renal failure and death during pregnancy, especially in second and third trimesters.",
        "recommendation": "Contraindicated in pregnancy. Use alternative antihypertensives.",
        "evidence_level": "D",
    },
    # NSAIDs + Peptic Ulcer Disease → Increased bleeding risk
    {
        "interaction_type": InteractionType.DRUG_DISEASE,
        "severity": InteractionSeverity.SEVERE,
        "drug_1_code": "NSAID",
        "disease_code": "K25",  # Gastric ulcer (ICD-10)
        "disease_name": "Peptic Ulcer Disease",
        "description": "NSAIDs may increase risk of gastrointestinal bleeding and ulcer complications.",
        "recommendation": "Use with caution in patients with history of PUD. Consider co-prescription with PPI or misoprostol. Avoid in active ulcer.",
        "evidence_level": "A",
    },
    # Beta-blockers + Asthma → Bronchoconstriction
    {
        "interaction_type": InteractionType.DRUG_DISEASE,
        "severity": InteractionSeverity.MODERATE,
        "drug_1_code": "BETABLOCKER",
        "disease_code": "J45",  # Asthma (ICD-10)
        "disease_name": "Asthma",
        "description": "Non-selective beta-blockers may induce bronchoconstriction in asthmatic patients.",
        "recommendation": "Use cardioselective beta-blockers (e.g., metoprolol, atenolol) with caution. Avoid non-selective beta-blockers in severe asthma.",
        "evidence_level": "B",
    },
]


async def seed_common_interactions(db: AsyncSession) -> dict:
    """Seed database with common drug interactions
    Note: This is a simplified version that would need drug ID mapping
    """
    results = {
        "created": 0,
        "skipped": 0,
        "errors": []
    }

    # In production, this would map drug codes to actual drug IDs
    # For now, we'll create placeholder interactions that can be updated
    for interaction_data in COMMON_INTERACTIONS:
        try:
            # Check if interaction already exists
            exists = await check_interaction_exists(
                db,
                drug_1_id=1,  # Placeholder - would map to actual drug ID
                drug_2_id=2,  # Placeholder
                interaction_type=interaction_data["interaction_type"],
            )

            if exists:
                results["skipped"] += 1
                continue

            # Create interaction with placeholder drug IDs
            await create_drug_interaction(
                db=db,
                interaction_type=interaction_data["interaction_type"],
                severity=interaction_data["severity"],
                drug_1_id=1,  # Placeholder
                drug_2_id=2,  # Placeholder
                description=interaction_data["description"],
                recommendation=interaction_data["recommendation"],
                evidence_level=interaction_data["evidence_level"],
            )
            results["created"] += 1

        except Exception as e:
            results["errors"].append(str(e))

    return results
