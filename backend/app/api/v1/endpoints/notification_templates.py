"""Notification Template API Endpoints

STORY-071: Notification Template Management System
API endpoints for notification template management.

Python 3.5+ compatible
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user
from app.services.notification_templates import get_notification_template_service


logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models
class TemplateCreateRequest(BaseModel):
    """Request to create a template"""
    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    category: str = Field(..., max_length=100, description="Template category")
    channel: str = Field(..., max_length=50, description="Notification channel")
    subject: Optional[str] = Field(None, max_length=500, description="Message subject")
    body: str = Field(..., min_length=1, description="Message body with variables")
    language: str = Field("id", max_length=10, description="Language code")
    variables: Optional[List[str]] = Field(None, description="Variables used in template")
    description: Optional[str] = Field(None, description="Template description")
    is_default: bool = Field(False, description="Whether this is default template")
    is_active: bool = Field(True, description="Whether template is active")


class TemplateUpdateRequest(BaseModel):
    """Request to update a template"""
    subject: Optional[str] = Field(None, max_length=500, description="New subject")
    body: Optional[str] = Field(None, min_length=1, description="New body")
    variables: Optional[List[str]] = Field(None, description="New variables")
    description: Optional[str] = Field(None, description="New description")
    is_active: Optional[bool] = Field(None, description="New active status")
    change_reason: Optional[str] = Field(None, max_length=500, description="Reason for change")


class TemplateResponse(BaseModel):
    """Response for template details"""
    template_id: int
    name: str
    category: str
    channel: str
    language: str
    subject: Optional[str] = None
    body: str
    variables: Optional[dict] = None
    is_active: bool
    is_default: bool
    version: int
    description: Optional[str] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class TemplateListResponse(BaseModel):
    """Response for template list"""
    templates: List[TemplateResponse]
    total_count: int
    page: int
    per_page: int
    total_pages: int


class TemplatePreviewRequest(BaseModel):
    """Request for template preview"""
    sample_data: dict = Field(..., description="Sample data for variables")


class TemplatePreviewResponse(BaseModel):
    """Response for template preview"""
    template_id: int
    subject: str
    body: str
    variables: Optional[dict] = None


class TemplateVersionResponse(BaseModel):
    """Response for template version"""
    version_id: int
    version_number: int
    subject: Optional[str] = None
    body: str
    variables: Optional[dict] = None
    change_reason: Optional[str] = None
    changed_by: Optional[int] = None
    changed_at: Optional[str] = None


@router.post("/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    request: TemplateCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new notification template"""
    try:
        service = get_notification_template_service(db)

        result = await service.create_template(
            name=request.name,
            category=request.category,
            channel=request.channel,
            subject=request.subject,
            body=request.body,
            language=request.language,
            variables=request.variables,
            description=request.description,
            created_by=current_user.id,
            is_default=request.is_default,
            is_active=request.is_active
        )

        # Get full template details
        template_details = await service.get_template(result["template_id"])

        return TemplateResponse(**template_details)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error creating template: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create template"
        )


@router.get("/templates", response_model=TemplateListResponse)
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    channel: Optional[str] = Query(None, description="Filter by channel"),
    language: Optional[str] = Query(None, description="Filter by language"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List notification templates with filtering"""
    try:
        service = get_notification_template_service(db)

        result = await service.list_templates(
            category=category,
            channel=channel,
            language=language,
            is_active=is_active,
            page=page,
            per_page=per_page
        )

        return TemplateListResponse(
            templates=[TemplateResponse(**t) for t in result["templates"]],
            total_count=result["total_count"],
            page=page,
            per_page=per_page,
            total_pages=result["total_pages"]
        )

    except Exception as e:
        logger.error("Error listing templates: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list templates"
        )


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get template by ID"""
    try:
        service = get_notification_template_service(db)

        result = await service.get_template(template_id)

        return TemplateResponse(**result)

    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error getting template: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get template"
        )


@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    request: TemplateUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a notification template"""
    try:
        service = get_notification_template_service(db)

        result = await service.update_template(
            template_id=template_id,
            subject=request.subject,
            body=request.body,
            variables=request.variables,
            description=request.description,
            updated_by=current_user.id,
            is_active=request.is_active,
            change_reason=request.change_reason
        )

        # Get updated template details
        template_details = await service.get_template(template_id)

        return TemplateResponse(**template_details)

    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error updating template: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update template"
        )


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a notification template"""
    try:
        service = get_notification_template_service(db)

        result = await service.delete_template(template_id)

        return result

    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error deleting template: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete template"
        )


@router.post("/templates/{template_id}/preview", response_model=TemplatePreviewResponse)
async def preview_template(
    template_id: int,
    request: TemplatePreviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Preview template with sample data"""
    try:
        service = get_notification_template_service(db)

        result = await service.preview_template(
            template_id=template_id,
            sample_data=request.sample_data
        )

        return TemplatePreviewResponse(**result)

    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error previewing template: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to preview template"
        )


@router.get("/templates/{template_id}/versions")
async def get_template_versions(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get version history for a template"""
    try:
        service = get_notification_template_service(db)

        versions = await service.get_template_versions(template_id)

        return {
            "template_id": template_id,
            "versions": [TemplateVersionResponse(**v) for v in versions],
            "total": len(versions)
        }

    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error getting template versions: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get template versions"
        )


@router.post("/templates/{template_id}/rollback", response_model=TemplateResponse)
async def rollback_template(
    template_id: int,
    target_version: int = Query(..., description="Target version number"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Rollback template to a previous version"""
    try:
        service = get_notification_template_service(db)

        result = await service.rollback_template(
            template_id=template_id,
            target_version=target_version,
            updated_by=current_user.id
        )

        # Get updated template details
        template_details = await service.get_template(template_id)

        return TemplateResponse(**template_details)

    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error rolling back template: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rollback template"
        )
