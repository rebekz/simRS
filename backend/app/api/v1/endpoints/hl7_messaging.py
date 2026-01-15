"""HL7 v2.x Integration API Endpoints for STORY-024-01

This module provides API endpoints for:
- HL7 message reception and parsing
- HL7 message status checking
- HL7 message history
- HL7 routing rules management

Python 3.5+ compatible
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user, get_current_admin_user
from app.services.hl7_messaging import get_hl7_messaging_service


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class HL7MessageReceiveRequest(BaseModel):
    """Request to receive HL7 message"""
    message: str = Field(..., description="Raw HL7 v2.x message")
    source_system: Optional[str] = Field(None, description="Source system identifier")


class HL7MessageResponse(BaseModel):
    """Response for HL7 message details"""
    message_id: int
    message_control_id: str
    message_type: str
    trigger_event: Optional[str] = None
    status: str
    sending_facility: Optional[str] = None
    sending_application: Optional[str] = None
    created_at: Optional[str] = None
    processed_at: Optional[str] = None
    acknowledgment: Optional[dict] = None
    errors: List[dict] = []


class HL7MessageListResponse(BaseModel):
    """Response for message list"""
    messages: List[HL7MessageResponse]
    total_count: int
    page: int
    per_page: int
    total_pages: int


class RoutingRuleCreateRequest(BaseModel):
    """Request to create routing rule"""
    name: str = Field(..., min_length=1, max_length=255, description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    message_type_filter: Optional[str] = Field(None, description="Filter by message type")
    sending_facility_filter: Optional[str] = Field(None, description="Filter by sending facility")
    sending_application_filter: Optional[str] = Field(None, description="Filter by sending application")
    action: str = Field(..., description="Routing action")
    target_system: Optional[str] = Field(None, description="Target system")
    target_endpoint: Optional[str] = Field(None, description="Target endpoint URL")
    priority: int = Field(0, description="Rule priority")


class RoutingRuleResponse(BaseModel):
    """Response for routing rule"""
    rule_id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    priority: int
    message_type_filter: Optional[str] = None
    action: str
    target_system: Optional[str] = None
    total_messages_processed: int
    successful_messages: int
    failed_messages: int
    created_at: Optional[str] = None


# =============================================================================
# HL7 Message Endpoints
# =============================================================================

@router.post("/messages", status_code=status.HTTP_202_ACCEPTED)
async def receive_hl7_message(
    request: HL7MessageReceiveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Receive and process incoming HL7 v2.x message"""
    try:
        service = get_hl7_messaging_service(db)

        result = await service.receive_message(
            raw_message=request.message,
            source_system=request.source_system
        )

        return {
            "message_id": result.get("message_id"),
            "message_control_id": result.get("message_control_id"),
            "status": result.get("status"),
            "acknowledgment": result.get("acknowledgment"),
            "routing_result": result.get("routing_result")
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error receiving HL7 message: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process HL7 message"
        )


@router.get("/messages/{message_id}", response_model=HL7MessageResponse)
async def get_hl7_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get HL7 message by ID"""
    try:
        service = get_hl7_messaging_service(db)

        result = await service.get_message(message_id)

        return HL7MessageResponse(**result)

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error getting HL7 message: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get message"
        )


@router.get("/messages", response_model=HL7MessageListResponse)
async def list_hl7_messages(
    status: Optional[str] = Query(None, description="Filter by status"),
    message_type: Optional[str] = Query(None, description="Filter by message type"),
    sending_facility: Optional[str] = Query(None, description="Filter by sending facility"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List HL7 messages with filtering"""
    try:
        service = get_hl7_messaging_service(db)

        result = await service.list_messages(
            status=status,
            message_type=message_type,
            sending_facility=sending_facility,
            page=page,
            per_page=per_page
        )

        return HL7MessageListResponse(
            messages=[HL7MessageResponse(**m) for m in result["messages"]],
            total_count=result["total_count"],
            page=page,
            per_page=per_page,
            total_pages=result["total_pages"]
        )

    except Exception as e:
        logger.error("Error listing HL7 messages: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list messages"
        )


# =============================================================================
# HL7 Statistics Endpoints
# =============================================================================

@router.get("/statistics")
async def get_hl7_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get HL7 integration statistics"""
    try:
        service = get_hl7_messaging_service(db)

        # Get message counts by status
        from app.models.hl7 import HL7Message, HL7MessageStatus
        from sqlalchemy import select, func

        status_query = select(
            HL7Message.status,
            func.count(HL7Message.id).label("count")
        ).group_by(HL7Message.status)

        status_result = await db.execute(status_query)
        status_counts = {row[0]: row[1] for row in status_result.all()}

        # Get total messages
        total_query = select(func.count(HL7Message.id))
        total_result = await db.execute(total_query)
        total_messages = total_result.scalar() or 0

        # Get message type counts
        type_query = select(
            HL7Message.message_type,
            func.count(HL7Message.id).label("count")
        ).group_by(HL7Message.message_type)

        type_result = await db.execute(type_query)
        type_counts = {row[0]: row[1] for row in type_result.all()}

        return {
            "total_messages": total_messages,
            "status_counts": status_counts,
            "message_type_counts": type_counts,
            "summary": {
                "pending": status_counts.get(HL7MessageStatus.PENDING, 0),
                "processing": status_counts.get(HL7MessageStatus.PROCESSING, 0),
                "processed": status_counts.get(HL7MessageStatus.PROCESSED, 0),
                "acknowledged": status_counts.get(HL7MessageStatus.ACKNOWLEDGED, 0),
                "failed": status_counts.get(HL7MessageStatus.FAILED, 0),
            }
        }

    except Exception as e:
        logger.error("Error getting HL7 statistics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )


# =============================================================================
# Routing Rules Endpoints (Admin)
# =============================================================================

@router.post("/routing-rules", response_model=RoutingRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_routing_rule(
    request: RoutingRuleCreateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create HL7 routing rule (admin only)"""
    try:
        from app.models.hl7 import HL7RoutingRule

        rule = HL7RoutingRule(
            name=request.name,
            description=request.description,
            message_type_filter=request.message_type_filter,
            sending_facility_filter=request.sending_facility_filter,
            sending_application_filter=request.sending_application_filter,
            action=request.action,
            target_system=request.target_system,
            target_endpoint=request.target_endpoint,
            priority=request.priority,
            created_by=current_user.id
        )

        db.add(rule)
        await db.commit()

        return RoutingRuleResponse(
            rule_id=rule.id,
            name=rule.name,
            description=rule.description,
            is_active=rule.is_active,
            priority=rule.priority,
            message_type_filter=rule.message_type_filter,
            action=rule.action,
            target_system=rule.target_system,
            total_messages_processed=0,
            successful_messages=0,
            failed_messages=0,
            created_at=rule.created_at.isoformat() if rule.created_at else None
        )

    except Exception as e:
        logger.error("Error creating routing rule: {}".format(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create routing rule"
        )


@router.get("/routing-rules")
async def list_routing_rules(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List HL7 routing rules (admin only)"""
    try:
        from app.models.hl7 import HL7RoutingRule
        from sqlalchemy import select

        query = select(HL7RoutingRule)

        if is_active is not None:
            query = query.where(HL7RoutingRule.is_active == is_active)

        query = query.order_by(HL7RoutingRule.priority.desc())

        result = await db.execute(query)
        rules = result.scalars().all()

        return [
            {
                "rule_id": r.id,
                "name": r.name,
                "description": r.description,
                "is_active": r.is_active,
                "priority": r.priority,
                "message_type_filter": r.message_type_filter,
                "sending_facility_filter": r.sending_facility_filter,
                "action": r.action,
                "target_system": r.target_system,
                "total_messages_processed": r.total_messages_processed,
                "successful_messages": r.successful_messages,
                "failed_messages": r.failed_messages,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rules
        ]

    except Exception as e:
        logger.error("Error listing routing rules: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list routing rules"
        )
