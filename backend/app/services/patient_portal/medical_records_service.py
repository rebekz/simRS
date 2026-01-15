"""Medical Records Service for Patient Portal

Service for patients to access, manage, and share their medical documents
and records. Includes document upload, download, sharing, and audit logging.
STORY-047: Medical Records & Documents Access
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import secrets
import uuid

from app.models.patient import Patient
from app.schemas.patient_portal.medical_records import (
    MedicalDocument,
    MedicalDocumentsList,
    DocumentCategory,
    DocumentType,
    DocumentStatus,
    DocumentUploadRequest,
    DocumentUploadResponse,
    DocumentAccessLog,
    DocumentShareRequest,
    DocumentShareResponse,
)


class MedicalRecordsService:
    """Service for handling medical records and documents access"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_medical_documents(
        self,
        patient_id: int,
        category: Optional[DocumentCategory] = None,
        status: Optional[DocumentStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> MedicalDocumentsList:
        """List patient's medical documents with pagination and filtering

        Args:
            patient_id: Patient ID
            category: Filter by document category
            status: Filter by document status
            page: Page number (1-indexed)
            page_size: Number of documents per page

        Returns:
            MedicalDocumentsList with paginated documents

        Raises:
            ValueError: If patient not found
        """
        # Verify patient exists
        patient = await self._get_patient(patient_id)
        if not patient:
            raise ValueError("Patient not found")

        # Mock documents list - in production would query database
        documents = []
        total = 0

        # Calculate pagination
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1

        return MedicalDocumentsList(
            documents=documents,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )

    async def get_document_detail(
        self,
        patient_id: int,
        document_id: int,
    ) -> Optional[MedicalDocument]:
        """Get detailed information about a specific document with access logging

        Args:
            patient_id: Patient ID
            document_id: Document ID

        Returns:
            MedicalDocument with full details

        Raises:
            ValueError: If document not found or access denied
        """
        # Get document
        document = await self._get_document_by_id(document_id)

        if not document:
            raise ValueError("Document not found")

        # Verify ownership (in production, would check patient_id matches)
        # Log document access
        await self.log_document_access(
            document_id=document_id,
            patient_id=patient_id,
            access_type="view",
        )

        return document

    async def upload_document(
        self,
        patient_id: int,
        document_data: DocumentUploadRequest,
        file_filename: str,
        file_content_type: str,
        file_size: int,
    ) -> DocumentUploadResponse:
        """Handle document upload (mock file storage)

        Args:
            patient_id: Patient ID
            document_data: Document metadata from request
            file_filename: Uploaded file name
            file_content_type: File MIME type
            file_size: File size in bytes

        Returns:
            DocumentUploadResponse with created document details

        Raises:
            ValueError: If patient not found or invalid data
        """
        # Verify patient exists
        patient = await self._get_patient(patient_id)
        if not patient:
            raise ValueError("Patient not found")

        # Validate file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if file_size > max_size:
            raise ValueError("File size exceeds maximum allowed size of 50MB")

        # Generate mock document ID and URLs
        document_id = 1  # Mock ID - in production would get from DB insert
        upload_date = datetime.utcnow()

        # Generate secure file URL (mock)
        fileUUID = str(uuid.uuid4())
        file_url = "https://storage.example.com/medical_records/{}/{}".format(patient_id, fileUUID)

        # Generate access code for shared documents (mock)
        access_code = None
        if document_data.is_confidential:
            access_code = secrets.token_urlsafe(16)

        # Create mock document record
        document = MedicalDocument(
            id=document_id,
            title=document_data.title,
            category=document_data.category,
            document_type=document_data.document_type,
            status=DocumentStatus.AVAILABLE,
            file_url=file_url,
            file_size=file_size,
            upload_date=upload_date,
            encounter_id=document_data.encounter_id,
            uploaded_by="Patient",  # In production would get from user context
            description=document_data.description,
            tags=document_data.tags,
            access_count=0,
            last_accessed=None,
            expires_at=None,
            is_confidential=document_data.is_confidential,
        )

        # Log upload activity
        await self.log_document_access(
            document_id=document_id,
            patient_id=patient_id,
            access_type="view",
        )

        return DocumentUploadResponse(
            document_id=document_id,
            message="Dokumen berhasil diunggah",  # Indonesian: "Document successfully uploaded"
            file_url=file_url,
            access_code=access_code,
            upload_date=upload_date,
            expires_at=None,
        )

    async def delete_document(
        self,
        patient_id: int,
        document_id: int,
    ) -> Dict[str, Any]:
        """Soft delete/archive a document

        Args:
            patient_id: Patient ID
            document_id: Document ID

        Returns:
            Dict with success status and message

        Raises:
            ValueError: If document not found or access denied
        """
        # Get document
        document = await self._get_document_by_id(document_id)

        if not document:
            raise ValueError("Document not found")

        # Verify ownership (in production, would check patient_id matches)
        # Soft delete by changing status to archived
        # In production, would update database record
        document.status = DocumentStatus.ARCHIVED

        # Log deletion
        await self.log_document_access(
            document_id=document_id,
            patient_id=patient_id,
            access_type="view",
        )

        return {
            "success": True,
            "message": "Dokumen berhasil dihapus",  # Indonesian: "Document successfully deleted"
            "document_id": document_id,
        }

    async def share_document(
        self,
        patient_id: int,
        share_request: DocumentShareRequest,
    ) -> DocumentShareResponse:
        """Generate shareable link for document (mock)

        Args:
            patient_id: Patient ID
            share_request: Share request with recipient details

        Returns:
            DocumentShareResponse with share link details

        Raises:
            ValueError: If document not found or access denied
        """
        # Get document
        document = await self._get_document_by_id(share_request.document_id)

        if not document:
            raise ValueError("Document not found")

        # Verify ownership (in production, would check patient_id matches)
        # Generate share token and URL
        share_id = str(uuid.uuid4())
        access_url = "https://portal.example.com/shared/{}".format(share_id)

        # Calculate expiration
        expires_at = datetime.utcnow()
        if share_request.access_duration:
            expires_at = expires_at + timedelta(hours=share_request.access_duration)
        else:
            # Default 7 days
            expires_at = expires_at + timedelta(days=7)

        # Generate access code if confidential
        access_code = None
        if document.is_confidential:
            access_code = secrets.token_urlsafe(16)

        share_created = datetime.utcnow()

        # Log sharing activity
        await self.log_document_access(
            document_id=share_request.document_id,
            patient_id=patient_id,
            access_type="share",
        )

        return DocumentShareResponse(
            share_id=share_id,
            document_id=share_request.document_id,
            access_url=access_url,
            access_code=access_code,
            expires_at=expires_at,
            message="Dokumen berhasil dibagikan",  # Indonesian: "Document successfully shared"
            recipient_email=share_request.recipient_email,
            share_created=share_created,
        )

    async def get_document_stats(
        self,
        patient_id: int,
    ) -> Dict[str, Any]:
        """Get statistics on document counts by category

        Args:
            patient_id: Patient ID

        Returns:
            Dict with counts by category and type

        Raises:
            ValueError: If patient not found
        """
        # Verify patient exists
        patient = await self._get_patient(patient_id)
        if not patient:
            raise ValueError("Patient not found")

        # Mock statistics - in production would query database
        stats = {
            "total_documents": 0,
            "by_category": {
                "clinical_notes": 0,
                "lab_results": 0,
                "radiology_reports": 0,
                "prescriptions": 0,
                "referral_letters": 0,
                "medical_certificates": 0,
                "insurance_documents": 0,
                "id_documents": 0,
                "other": 0,
            },
            "by_type": {
                "pdf": 0,
                "jpg": 0,
                "png": 0,
                "dicom": 0,
                "txt": 0,
                "docx": 0,
            },
            "recent_count": 0,  # Last 30 days
            "total_storage_mb": 0.0,
        }

        return stats

    async def log_document_access(
        self,
        document_id: int,
        patient_id: int,
        access_type: str,
    ) -> DocumentAccessLog:
        """Record document access for audit trail

        Args:
            document_id: Document ID
            patient_id: Patient ID
            access_type: Type of access (view, download, share)

        Returns:
            DocumentAccessLog with recorded access

        Raises:
            ValueError: If document not found
        """
        # Get document for title
        document = await self._get_document_by_id(document_id)
        if not document:
            raise ValueError("Document not found")

        # Create access log (mock - in production would save to database)
        access_log = DocumentAccessLog(
            id=1,  # Mock ID
            document_id=document_id,
            document_title=document.title,
            accessed_by="Patient",  # In production would get from user context
            access_type=access_type,  # type: ignore
            access_date=datetime.utcnow(),
            ip_address=None,  # Would be extracted from request
            user_agent=None,  # Would be extracted from request
            purpose=None,
        )

        return access_log

    # Private helper methods

    async def _get_patient(
        self, patient_id: int
    ) -> Optional[Patient]:
        """Get patient by ID"""
        result = await self.db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        return result.scalar_one_or_none()

    async def _get_document_by_id(
        self, document_id: int
    ) -> Optional[MedicalDocument]:
        """Get document by ID (mock implementation)"""
        # Mock implementation - in production, query database
        # For now, return None as placeholder
        return None
