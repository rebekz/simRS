"""BPJS SEP API endpoints for STORY-019: BPJS SEP Generation

This module provides API endpoints for BPJS SEP (Surat Eligibilitas Peserta)
management, including creation, updating, cancellation, and history tracking.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.sep import (
    SEPCreate,
    SEPResponse,
    SEPUpdate,
    SEPUpdateResponse,
    SEPCancel,
    SEPCancelResponse,
    SEPInfo,
    SEPSummary,
    SEPListQuery,
    SEPListResponse,
    SEPValidationRequest,
    SEPValidationResponse,
    SEPHistory,
    SEPAutoPopulateRequest,
    SEPAutoPopulateResponse,
    SEPStatistics,
)
from app.crud import sep as crud_sep
from app.services.bpjs_vclaim import BPJSVClaimClient, BPJSVClaimError


router = APIRouter()


# =============================================================================
# SEP Creation Endpoints
# =============================================================================

@router.post("/sep/validate", response_model=SEPValidationResponse)
async def validate_sep_data(
    validation_data: SEPValidationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SEPValidationResponse:
    """Validate SEP data before creation."""
    validation = await crud_sep.validate_sep_data(db, validation_data)
    return validation


@router.get("/sep/auto-populate/{encounter_id}", response_model=SEPAutoPopulateResponse)
async def get_auto_populate_data(
    encounter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SEPAutoPopulateResponse:
    """
    Get auto-populated SEP data from encounter.

    Collects patient information, encounter details, doctor information,
    and diagnosis codes to pre-fill SEP creation form.
    """
    sep_data = await crud_sep.get_auto_populate_data(db, encounter_id)

    if not sep_data:
        raise HTTPException(status_code=404, detail="Encounter not found")

    # Validate the auto-populated data
    validation_request = SEPValidationRequest(
        bpjs_card_number=sep_data.bpjs_card_number,
        sep_date=sep_data.sep_date,
        service_type=sep_data.service_type,
        ppk_code=sep_data.ppk_code,
        initial_diagnosis_code=sep_data.initial_diagnosis_code or "",
        polyclinic_code=sep_data.polyclinic_code,
    )

    validation = await crud_sep.validate_sep_data(db, validation_request)

    # Check for missing fields
    missing_fields = []
    if not sep_data.ppk_code:
        missing_fields.append("ppk_code (hospital facility code)")
    if sep_data.service_type == "RJ" and not sep_data.polyclinic_code:
        missing_fields.append("polyclinic_code")
    if not sep_data.initial_diagnosis_code:
        missing_fields.append("initial_diagnosis_code")

    return SEPAutoPopulateResponse(
        sep_data=sep_data,
        validation=validation,
        can_create=validation.is_valid and len(missing_fields) == 0,
        missing_fields=missing_fields,
    )


@router.post("/sep", response_model=SEPResponse)
async def create_sep(
    sep_data: SEPCreate,
    submit_to_bpjs: bool = Query(default=True, description="Submit SEP to BPJS API"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SEPResponse:
    """
    Create a new SEP (Surat Eligibilitas Peserta).

    If submit_to_bpjs is True, the SEP will be submitted to BPJS VClaim API.
    Otherwise, it will be saved as a draft.
    """
    bpjs_response = None

    # Build BPJS SEP request data
    if submit_to_bpjs:
        bpjs_sep_data = {
            "request": {
                "t_sep": {
                    "noKartu": sep_data.bpjs_card_number,
                    "tglSEP": sep_data.sep_date.strftime("%Y-%m-%d"),
                    "ppkPelayanan": sep_data.ppk_code,
                    "jnsPelayanan": "RAWAT INAP" if sep_data.service_type == "RI" else "RAWAT JALAN",
                    "klsRawat": sep_data.treatment_class,
                    "noMR": sep_data.mrn,
                    "diagAwal": sep_data.initial_diagnosis_code,
                    "poliTujuan": sep_data.polyclinic_code,
                    "eksekutif": "1" if sep_data.is_executive else "0",
                    "cob": {"cob": "1" if sep_data.cob_flag else "0"} if sep_data.cob_flag else None,
                    "tujuanKun": sep_data.polyclinic_code,
                    "dpjp": {
                        "kodeDPJP": sep_data.doctor_code,
                        "namaDPJP": sep_data.doctor_name,
                    } if sep_data.doctor_code else None,
                    "noTelp": sep_data.patient_phone,
                    "catatan": sep_data.notes,
                },
                "user": sep_data.user,
            }
        }

        # Add referral if provided
        if sep_data.referral_number and sep_data.referral_ppk_code:
            bpjs_sep_data["request"]["t_sep"]["rujukan"] = {
                "noRujukan": sep_data.referral_number,
                "ppkRujukan": sep_data.referral_ppk_code,
            }

        try:
            async with BPJSVClaimClient() as bpjs_client:
                bpjs_response = await bpjs_client.create_sep(bpjs_sep_data)

                # Check for BPJS API errors
                if "metaData" in bpjs_response:
                    metadata = bpjs_response["metaData"]
                    code = metadata.get("code")
                    message = metadata.get("message")

                    if code != "200":
                        raise HTTPException(
                            status_code=400,
                            detail=f"BPJS API error: {message}"
                        )

        except BPJSVClaimError as e:
            raise HTTPException(
                status_code=500,
                detail=f"BPJS API request failed: {e.message}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create SEP: {str(e)}"
            )

    # Create SEP record in database
    sep = await crud_sep.create_sep(
        db=db,
        sep_data=sep_data,
        bpjs_response=bpjs_response,
        user_id=current_user.id,
    )

    return SEPResponse(
        sep_id=sep.id,
        sep_number=sep.sep_number,
        encounter_id=sep.encounter_id,
        patient_id=sep.patient_id,
        status=sep.status,
        sep_date=sep.sep_date,
        service_type=sep.service_type,
        bpjs_card_number=sep.bpjs_card_number,
        initial_diagnosis_code=sep.initial_diagnosis_code,
        initial_diagnosis_name=sep.initial_diagnosis_name,
        bpjs_response=sep.bpjs_response,
        created_at=sep.created_at,
    )


# =============================================================================
# SEP Information Endpoints
# =============================================================================

@router.get("/sep/{sep_id}", response_model=SEPInfo)
async def get_sep(
    sep_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SEPInfo:
    """Get SEP information by ID."""
    sep = await crud_sep.get_sep_by_id(db, sep_id)

    if not sep:
        raise HTTPException(status_code=404, detail="SEP not found")

    return SEPInfo(
        sep_id=sep.id,
        sep_number=sep.sep_number,
        encounter_id=sep.encounter_id,
        patient_id=sep.patient_id,
        patient_name=sep.patient_name,
        bpjs_card_number=sep.bpjs_card_number,
        sep_date=sep.sep_date,
        service_type=sep.service_type,
        ppk_code=sep.ppk_code,
        polyclinic_code=sep.polyclinic_code,
        treatment_class=sep.treatment_class,
        initial_diagnosis_code=sep.initial_diagnosis_code,
        initial_diagnosis_name=sep.initial_diagnosis_name,
        doctor_name=sep.doctor_name,
        referral_number=sep.referral_number,
        is_executive=sep.is_executive,
        cob_flag=sep.cob_flag,
        notes=sep.notes,
        status=sep.status,
        created_at=sep.created_at,
        updated_at=sep.updated_at,
    )


@router.get("/sep/number/{sep_number}", response_model=SEPInfo)
async def get_sep_by_number(
    sep_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SEPInfo:
    """Get SEP information by SEP number."""
    sep = await crud_sep.get_sep_by_number(db, sep_number)

    if not sep:
        raise HTTPException(status_code=404, detail="SEP not found")

    return SEPInfo(
        sep_id=sep.id,
        sep_number=sep.sep_number,
        encounter_id=sep.encounter_id,
        patient_id=sep.patient_id,
        patient_name=sep.patient_name,
        bpjs_card_number=sep.bpjs_card_number,
        sep_date=sep.sep_date,
        service_type=sep.service_type,
        ppk_code=sep.ppk_code,
        polyclinic_code=sep.polyclinic_code,
        treatment_class=sep.treatment_class,
        initial_diagnosis_code=sep.initial_diagnosis_code,
        initial_diagnosis_name=sep.initial_diagnosis_name,
        doctor_name=sep.doctor_name,
        referral_number=sep.referral_number,
        is_executive=sep.is_executive,
        cob_flag=sep.cob_flag,
        notes=sep.notes,
        status=sep.status,
        created_at=sep.created_at,
        updated_at=sep.updated_at,
    )


@router.get("/encounter/{encounter_id}/sep", response_model=SEPInfo)
async def get_sep_by_encounter(
    encounter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SEPInfo:
    """Get SEP information by encounter ID."""
    sep = await crud_sep.get_sep_by_encounter(db, encounter_id)

    if not sep:
        raise HTTPException(status_code=404, detail="SEP not found for this encounter")

    return SEPInfo(
        sep_id=sep.id,
        sep_number=sep.sep_number,
        encounter_id=sep.encounter_id,
        patient_id=sep.patient_id,
        patient_name=sep.patient_name,
        bpjs_card_number=sep.bpjs_card_number,
        sep_date=sep.sep_date,
        service_type=sep.service_type,
        ppk_code=sep.ppk_code,
        polyclinic_code=sep.polyclinic_code,
        treatment_class=sep.treatment_class,
        initial_diagnosis_code=sep.initial_diagnosis_code,
        initial_diagnosis_name=sep.initial_diagnosis_name,
        doctor_name=sep.doctor_name,
        referral_number=sep.referral_number,
        is_executive=sep.is_executive,
        cob_flag=sep.cob_flag,
        notes=sep.notes,
        status=sep.status,
        created_at=sep.created_at,
        updated_at=sep.updated_at,
    )


# =============================================================================
# SEP List Endpoints
# =============================================================================

@router.get("/sep", response_model=SEPListResponse)
async def list_seps(
    patient_id: Optional[int] = Query(None),
    encounter_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    service_type: Optional[str] = Query(None),
    sep_number: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SEPListResponse:
    """List SEPs with filtering and pagination."""
    from datetime import datetime

    query = SEPListQuery(
        patient_id=patient_id,
        encounter_id=encounter_id,
        status=status,
        service_type=service_type,
        sep_number=sep_number,
        date_from=datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else None,
        date_to=datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else None,
        page=page,
        page_size=page_size,
    )

    seps, total = await crud_sep.list_seps(db, query)

    total_pages = (total + page_size - 1) // page_size

    items = [
        SEPSummary(
            sep_id=sep.id,
            sep_number=sep.sep_number,
            patient_name=sep.patient_name,
            bpjs_card_number=sep.bpjs_card_number,
            sep_date=sep.sep_date,
            service_type=sep.service_type,
            initial_diagnosis=sep.initial_diagnosis_name,
            status=sep.status,
            created_at=sep.created_at,
        )
        for sep in seps
    ]

    return SEPListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=items,
    )


# =============================================================================
# SEP Update Endpoints
# =============================================================================

@router.put("/sep", response_model=SEPUpdateResponse)
async def update_sep(
    sep_update: SEPUpdate,
    submit_to_bpjs: bool = Query(default=True, description="Submit update to BPJS API"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SEPUpdateResponse:
    """
    Update an existing SEP.

    If submit_to_bpjs is True, the update will be submitted to BPJS VClaim API.
    """
    bpjs_response = None

    # Get current SEP
    sep = await crud_sep.get_sep_by_id(db, sep_update.sep_id)
    if not sep:
        raise HTTPException(status_code=404, detail="SEP not found")

    if not sep.sep_number:
        raise HTTPException(
            status_code=400,
            detail="Cannot update draft SEP. Submit to BPJS first."
        )

    # Build BPJS update request data
    if submit_to_bpjs:
        bpjs_update_data = {
            "request": {
                "t_sep": {
                    "noSEP": sep.sep_number,
                    "klsRawat": sep_update.treatment_class,
                    "poliTujuan": sep_update.polyclinic_code,
                    "dpjp": {
                        "kodeDPJP": sep_update.doctor_code,
                        "namaDPJP": sep_update.doctor_name,
                    } if sep_update.doctor_code else None,
                    "catatan": sep_update.notes,
                },
                "user": sep_update.user,
            }
        }

        try:
            async with BPJSVClaimClient() as bpjs_client:
                bpjs_response = await bpjs_client.update_sep(bpjs_update_data)

                # Check for BPJS API errors
                if "metaData" in bpjs_response:
                    metadata = bpjs_response["metaData"]
                    code = metadata.get("code")
                    message = metadata.get("message")

                    if code != "200":
                        raise HTTPException(
                            status_code=400,
                            detail=f"BPJS API error: {message}"
                        )

        except BPJSVClaimError as e:
            raise HTTPException(
                status_code=500,
                detail=f"BPJS API request failed: {e.message}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update SEP: {str(e)}"
            )

    # Update SEP record in database
    updated_sep = await crud_sep.update_sep(
        db=db,
        sep_update=sep_update,
        bpjs_response=bpjs_response,
        user_id=current_user.id,
    )

    if not updated_sep:
        raise HTTPException(status_code=404, detail="SEP not found")

    return SEPUpdateResponse(
        sep_id=updated_sep.id,
        sep_number=updated_sep.sep_number,
        previous_status=SEPStatus.SUBMITTED,  # TODO: Get from history
        new_status=updated_sep.status,
        message="SEP updated successfully",
        bpjs_response=updated_sep.bpjs_response,
        updated_at=updated_sep.updated_at,
    )


# =============================================================================
# SEP Cancellation Endpoints
# =============================================================================

@router.delete("/sep", response_model=SEPCancelResponse)
async def cancel_sep(
    sep_cancel: SEPCancel,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SEPCancelResponse:
    """
    Cancel (delete) an SEP.

    Submits cancellation request to BPJS VClaim API and soft-deletes the SEP.
    """
    # Verify SEP exists
    sep = await crud_sep.get_sep_by_id(db, sep_cancel.sep_id)
    if not sep:
        raise HTTPException(status_code=404, detail="SEP not found")

    if not sep.sep_number:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel draft SEP. SEP must be submitted to BPJS first."
        )

    bpjs_response = None

    try:
        async with BPJSVClaimClient() as bpjs_client:
            bpjs_response = await bpjs_client.delete_sep(
                sep_number=sep_cancel.sep_number,
                user=sep_cancel.user,
            )

            # Check for BPJS API errors
            if "metaData" in bpjs_response:
                metadata = bpjs_response["metaData"]
                code = metadata.get("code")
                message = metadata.get("message")

                if code != "200":
                    raise HTTPException(
                        status_code=400,
                        detail=f"BPJS API error: {message}"
                    )

    except BPJSVClaimError as e:
        raise HTTPException(
            status_code=500,
            detail=f"BPJS API request failed: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel SEP: {str(e)}"
        )

    # Cancel SEP record in database
    cancelled_sep = await crud_sep.cancel_sep(
        db=db,
        sep_cancel=sep_cancel,
        bpjs_response=bpjs_response,
        user_id=current_user.id,
    )

    if not cancelled_sep:
        raise HTTPException(status_code=404, detail="SEP not found")

    return SEPCancelResponse(
        sep_id=cancelled_sep.id,
        sep_number=cancelled_sep.sep_number,
        status=cancelled_sep.status,
        message="SEP cancelled successfully",
        bpjs_response=cancelled_sep.bpjs_response,
        cancelled_at=cancelled_sep.deleted_at or cancelled_sep.updated_at,
    )


# =============================================================================
# SEP History Endpoints
# =============================================================================

@router.get("/sep/{sep_id}/history", response_model=SEPHistory)
async def get_sep_history(
    sep_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SEPHistory:
    """Get SEP change history."""
    sep = await crud_sep.get_sep_by_id(db, sep_id)
    if not sep:
        raise HTTPException(status_code=404, detail="SEP not found")

    history = await crud_sep.get_sep_history(db, sep_id)

    history_entries = []
    for h in history:
        # Get user name
        user_name = None
        if h.changed_by:
            user_stmt = select(User).where(User.id == h.changed_by)
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            if user:
                user_name = user.full_name if hasattr(user, 'full_name') else user.email

        history_entries.append(
            SEPHistoryEntry(
                history_id=h.id,
                sep_id=h.sep_id,
                action=h.action,
                previous_status=h.previous_status,
                new_status=h.new_status,
                reason=h.reason,
                changed_by=h.changed_by,
                changed_by_name=user_name,
                changed_at=h.changed_at,
            )
        )

    return SEPHistory(
        sep_id=sep_id,
        sep_number=sep.sep_number,
        history=history_entries,
    )


# =============================================================================
# SEP Statistics Endpoints
# =============================================================================

@router.get("/sep/statistics", response_model=SEPStatistics)
async def get_sep_statistics(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SEPStatistics:
    """Get SEP statistics for dashboard."""
    from datetime import datetime

    date_from_parsed = datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else None
    date_to_parsed = datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else None

    stats = await crud_sep.get_sep_statistics(db, date_from_parsed, date_to_parsed)
    return stats


# Import SEPStatus for use in update response
from app.models.bpjs_sep import SEPStatus
