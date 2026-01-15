"""Patient Portal Medical Records & Documents Endpoints

API endpoints for accessing medical documents and records.
STORY-047: Medical Records & Documents Access
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.db.session import get_db
from app.models.patient_portal import PatientPortalUser
from app.api.v1.endpoints.patient_portal_auth import get_current_portal_user

router = APIRouter()


@router.get(
    "/documents/medical",
    operation_id="list_medical_documents",
    summary="List medical documents",
    description="List medical documents with optional filtering by document type, date range, and pagination support",
)
async def list_medical_documents(
    document_type: Optional[str] = Query(
        None,
        description="Filter by document type (e.g., 'lab_report', 'radiology', 'discharge_summary', 'prescription', 'other')"
    ),
    date_from: Optional[str] = Query(
        None,
        description="Filter documents from this date (YYYY-MM-DD format)"
    ),
    date_to: Optional[str] = Query(
        None,
        description="Filter documents until this date (YYYY-MM-DD format)"
    ),
    limit: int = Query(
        100,
        ge=1,
        le=100,
        description="Maximum number of records to return"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of records to skip for pagination"
    ),
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """List medical documents with optional filtering

    Returns paginated list of medical documents associated with the patient.

    Query Parameters:
        document_type: Optional filter for document type
        date_from: Optional start date filter (YYYY-MM-DD format)
        date_to: Optional end date filter (YYYY-MM-DD format)
        limit: Maximum number of records to return (1-100, default 100)
        offset: Number of records to skip for pagination (default 0)

    Raises:
        HTTPException 400: If no patient record is linked to the account
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    from app.services.patient_portal.medical_records_service import MedicalRecordsService

    service = MedicalRecordsService(db)

    # Parse date filters if provided
    date_from_parsed = None
    date_to_parsed = None
    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format. Use YYYY-MM-DD format"
            )
    if date_to:
        try:
            date_to_parsed = datetime.strptime(date_to, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_to format. Use YYYY-MM-DD format"
            )

    return await service.list_documents(
        patient_id=current_user.patient_id,
        document_type=document_type,
        date_from=date_from_parsed,
        date_to=date_to_parsed,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/documents/medical/{document_id}",
    operation_id="get_medical_document_detail",
    summary="Get medical document details",
    description="Get detailed information about a specific medical document including metadata and download URL",
)
async def get_medical_document_detail(
    document_id: int,
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about specific medical document

    Returns detailed document record including metadata, access information, and download URL.

    Path Parameters:
        document_id: Unique identifier of the medical document

    Raises:
        HTTPException 400: If no patient record is linked to the account
        HTTPException 404: If document is not found
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    from app.services.patient_portal.medical_records_service import MedicalRecordsService

    service = MedicalRecordsService(db)
    try:
        detail = await service.get_document_detail(
            patient_id=current_user.patient_id,
            document_id=document_id,
        )
        return detail
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/documents/medical/upload",
    operation_id="upload_medical_document",
    summary="Upload medical document",
    description="Upload a new medical document to the patient's record. Supports PDF, images, and other common document formats.",
)
async def upload_medical_document(
    document_type: str = Query(
        ...,
        description="Type of document (e.g., 'lab_report', 'radiology', 'discharge_summary', 'prescription', 'other')"
    ),
    title: str = Query(
        ...,
        description="Document title or name"
    ),
    description: Optional[str] = Query(
        None,
        description="Optional description of the document"
    ),
    encounter_id: Optional[int] = Query(
        None,
        description="Optional link to a specific encounter"
    ),
    file: UploadFile = File(...),
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a new medical document

    Uploads a document file and associates it with the patient's medical record.

    Query Parameters:
        document_type: Type/category of the document
        title: Document title
        description: Optional document description
        encounter_id: Optional encounter ID to link the document to

    Form Data:
        file: The document file to upload (supports PDF, images, etc.)

    Returns:
        Created document record with metadata and download information

    Raises:
        HTTPException 400: If no patient record is linked to the account
        HTTPException 400: If file format is not supported
        HTTPException 413: If file size exceeds maximum allowed
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    from app.services.patient_portal.medical_records_service import MedicalRecordsService

    service = MedicalRecordsService(db)
    try:
        document = await service.upload_document(
            patient_id=current_user.patient_id,
            file=file,
            document_type=document_type,
            title=title,
            description=description,
            encounter_id=encounter_id,
            uploaded_by_portal_user_id=current_user.id,
        )
        return document
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise


@router.delete(
    "/documents/medical/{document_id}",
    operation_id="delete_medical_document",
    summary="Archive/delete medical document",
    description="Archive or permanently delete a medical document from the patient's record",
)
async def delete_medical_document(
    document_id: int,
    permanent: bool = Query(
        False,
        description="If true, permanently delete. If false, archive (soft delete)."
    ),
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Archive or delete a medical document

    Archives (soft delete) or permanently deletes a document from the patient's record.
    By default, documents are archived rather than permanently deleted.

    Path Parameters:
        document_id: Unique identifier of the medical document

    Query Parameters:
        permanent: If true, permanently delete. Default false (archive).

    Raises:
        HTTPException 400: If no patient record is linked to the account
        HTTPException 404: If document is not found
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    from app.services.patient_portal.medical_records_service import MedicalRecordsService

    service = MedicalRecordsService(db)
    try:
        await service.delete_document(
            patient_id=current_user.patient_id,
            document_id=document_id,
            permanent=permanent,
        )
        return {
            "message": "Document permanently deleted" if permanent else "Document archived",
            "document_id": document_id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/documents/medical/{document_id}/share",
    operation_id="share_medical_document",
    summary="Generate document share link",
    description="Generate a secure, time-limited share link for a medical document. Useful for sharing with healthcare providers.",
)
async def share_medical_document(
    document_id: int,
    expires_in_hours: int = Query(
        24,
        ge=1,
        le=168,
        description="Share link expiration time in hours (1-168, default 24)"
    ),
    access_count_limit: Optional[int] = Query(
        None,
        ge=1,
        le=50,
        description="Optional limit on number of times the link can be accessed"
    ),
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a secure share link for a medical document

    Creates a time-limited, secure URL that can be shared with healthcare providers
    or other authorized parties to access the document.

    Path Parameters:
        document_id: Unique identifier of the medical document

    Query Parameters:
        expires_in_hours: Number of hours until the link expires (1-168, default 24)
        access_count_limit: Optional maximum number of times the link can be accessed

    Returns:
        Share link URL with expiration information

    Raises:
        HTTPException 400: If no patient record is linked to the account
        HTTPException 404: If document is not found
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    from app.services.patient_portal.medical_records_service import MedicalRecordsService

    service = MedicalRecordsService(db)
    try:
        share_info = await service.generate_share_link(
            patient_id=current_user.patient_id,
            document_id=document_id,
            expires_in_hours=expires_in_hours,
            access_count_limit=access_count_limit,
            created_by_portal_user_id=current_user.id,
        )
        return share_info
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/documents/medical/stats",
    operation_id="get_medical_document_statistics",
    summary="Get document statistics",
    description="Get statistical information about medical documents including counts by type, storage usage, and recent activity",
)
async def get_medical_document_statistics(
    current_user: PatientPortalUser = Depends(get_current_portal_user),
    db: AsyncSession = Depends(get_db),
):
    """Get medical document statistics

    Returns comprehensive statistics about the patient's medical documents including:
    - Total count of documents
    - Count by document type
    - Total storage used
    - Most recent document
    - Documents uploaded in last 30 days

    Raises:
        HTTPException 400: If no patient record is linked to the account
    """
    if not current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No patient record linked to this account",
        )

    from app.services.patient_portal.medical_records_service import MedicalRecordsService

    service = MedicalRecordsService(db)
    stats = await service.get_document_statistics(current_user.patient_id)
    return stats
