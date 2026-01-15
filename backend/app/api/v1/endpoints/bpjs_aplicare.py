"""BPJS Aplicare API endpoints for STORY-032: Bed Availability Reporting

This module provides REST API endpoints for:
- Manual bed sync triggers
- Real-time bed availability updates to BPJS Aplicare
- Room class information
- Automatic synchronization monitoring
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.bpjs import (
    BPJSAplicareSyncRequest,
    BPJSAplicareSyncResponse,
    BPJSAplicareBedListResponse,
    BPJSAplicareBedCountResponse,
    BPJSAplicareBedInfo,
)
from app.services.bed_sync import (
    sync_room_to_bpjs,
    sync_all_rooms_to_bpjs,
    delete_room_from_bpjs,
    get_bed_summary_for_room,
    convert_to_bpjs_bed_format,
)
from app.services.bpjs_aplicare import (
    BPJSAplicareClient,
    BPJSAplicareError,
    get_bpjs_aplicare_client,
)


router = APIRouter()


# =============================================================================
# Bed Sync Endpoints
# =============================================================================

@router.post("/beds/sync/room/{room_id}", response_model=BPJSAplicareSyncResponse)
async def sync_room_bed_availability(
    room_id: int,
    force_update: bool = Query(default=False, description="Force update even if data unchanged"),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync a single room's bed availability to BPJS Aplicare.

    This endpoint manually triggers a sync of bed data for a specific room
    to BPJS Aplicare for real-time availability reporting.

    Args:
        room_id: Room ID to sync
        force_update: Force update even if data unchanged
        background_tasks: FastAPI background tasks
        current_user: Authenticated user
        db: Database session

    Returns:
        Sync result

    Raises:
        HTTPException 404: If room not found
        HTTPException 502: If BPJS API error
    """
    # Verify user has permission
    if current_user.role not in ["admin", "nurse", "doctor"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin, nurse, and doctor roles can sync bed data"
        )

    # Verify room exists
    bed_summary = await get_bed_summary_for_room(db, room_id)
    if not bed_summary:
        raise HTTPException(
            status_code=404,
            detail=f"Room {room_id} not found"
        )

    # Perform sync
    try:
        async with BPJSAplicareClient() as client:
            result = await sync_room_to_bpjs(db, room_id, client, force_update)

        return BPJSAplicareSyncResponse(
            success=result["success"],
            message=result["message"],
            room_id=room_id,
            bpjs_response=result.get("bpjs_response"),
            synced_at=datetime.now() if result["success"] else None,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync room: {str(e)}"
        )


@router.post("/beds/sync/all", response_model=dict)
async def sync_all_bed_availability(
    ward_id: Optional[int] = Query(None, description="Filter by ward ID"),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync all rooms' bed availability to BPJS Aplicare.

    This endpoint triggers a sync of all rooms (or rooms in a specific ward)
    to BPJS Aplicare for real-time availability reporting.

    Args:
        ward_id: Optional ward ID to filter rooms
        background_tasks: FastAPI background tasks
        current_user: Authenticated user
        db: Database session

    Returns:
        Sync result summary

    Raises:
        HTTPException 403: If user lacks permission
        HTTPException 502: If BPJS API error
    """
    # Verify user has permission (admin only)
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can sync all bed data"
        )

    try:
        async with BPJSAplicareClient() as client:
            result = await sync_all_rooms_to_bpjs(db, client, ward_id)

        return {
            "message": f"Synced {result['success_count']}/{result['total_rooms']} rooms successfully",
            "total_rooms": result["total_rooms"],
            "success_count": result["success_count"],
            "failure_count": result["failure_count"],
            "results": result["results"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync all rooms: {str(e)}"
        )


@router.delete("/beds/sync/room/{room_id}", response_model=dict)
async def delete_room_from_bpjs_sync(
    room_id: int,
    room_code: str = Query(..., description="Room code in BPJS format"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a room from BPJS Aplicare sync.

    This endpoint removes a room from BPJS Aplicare bed availability reporting.

    Args:
        room_id: Room ID
        room_code: Room code in BPJS format (e.g., "RM1-101")
        current_user: Authenticated user
        db: Database session

    Returns:
        Delete result

    Raises:
        HTTPException 403: If user lacks permission
        HTTPException 502: If BPJS API error
    """
    # Verify user has permission (admin only)
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can delete rooms from BPJS"
        )

    # Get room to verify existence and get room_class
    from app.models.bed import Room
    from sqlalchemy import select

    room_result = await db.execute(select(Room).filter(Room.id == room_id))
    room = room_result.scalar_one_or_none()

    if not room:
        raise HTTPException(
            status_code=404,
            detail=f"Room {room_id} not found"
        )

    try:
        async with BPJSAplicareClient() as client:
            result = await delete_room_from_bpjs(
                client,
                room_id,
                room.room_class,
                room_code
            )

        if not result["success"]:
            raise HTTPException(
                status_code=502,
                detail=result.get("message", "Failed to delete from BPJS")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete room from BPJS: {str(e)}"
        )


# =============================================================================
# BPJS Aplicare Query Endpoints
# =============================================================================

@router.get("/beds/bpjs/list", response_model=BPJSAplicareBedListResponse)
async def get_bpjs_bed_list(
    start: int = Query(0, description="Start index for pagination"),
    limit: int = Query(10, description="Number of records to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get bed list from BPJS Aplicare.

    This endpoint queries BPJS Aplicare to retrieve the current bed list
    that has been reported to BPJS.

    Args:
        start: Start index for pagination
        limit: Number of records to return
        current_user: Authenticated user
        db: Database session

    Returns:
        BPJS bed list

    Raises:
        HTTPException 502: If BPJS API error
    """
    try:
        client = await get_bpjs_aplicare_client()
        result = await client.get_bed_list(start=start, limit=limit)

        # Parse response
        beds = []
        if "list" in result.get("response", {}):
            for bed_data in result["response"]["list"]:
                beds.append(BPJSAplicareBedInfo(**bed_data))

        return BPJSAplicareBedListResponse(
            metaInfo=result.get("metaInfo"),
            list=beds,
        )

    except BPJSAplicareError as e:
        raise HTTPException(
            status_code=502,
            detail=f"BPJS API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get bed list: {str(e)}"
        )


@router.get("/beds/bpjs/count/{room_class}", response_model=BPJSAplicareBedCountResponse)
async def get_bpjs_bed_count_by_class(
    room_class: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get total bed count by room class from BPJS Aplicare.

    This endpoint queries BPJS Aplicare to retrieve the total bed count
    for a specific room class.

    Args:
        room_class: Room class code (1, 2, 3, VVIP, VIP)
        current_user: Authenticated user
        db: Database session

    Returns:
        BPJS bed count

    Raises:
        HTTPException 400: If invalid room class
        HTTPException 502: If BPJS API error
    """
    # Validate room class
    valid_classes = ['1', '2', '3', 'VVIP', 'VIP']
    if room_class.upper() not in valid_classes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid room class. Must be one of: {', '.join(valid_classes)}"
        )

    try:
        client = await get_bpjs_aplicare_client()
        result = await client.get_bed_count_by_class(kodekelas=room_class.upper())

        return BPJSAplicareBedCountResponse(
            metaInfo=result.get("metaInfo"),
            totalbed=result.get("response", {}).get("bed") or result.get("totalbed"),
            kodekelas=room_class.upper(),
        )

    except BPJSAplicareError as e:
        raise HTTPException(
            status_code=502,
            detail=f"BPJS API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get bed count: {str(e)}"
        )


# =============================================================================
# Bed Summary Endpoints
# =============================================================================

@router.get("/beds/summary/room/{room_id}", response_model=dict)
async def get_room_bed_summary(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get bed summary for a room (internal data).

    This endpoint returns the current bed availability summary for a room
    from the internal database, before BPJS sync.

    Args:
        room_id: Room ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Bed summary statistics

    Raises:
        HTTPException 404: If room not found
    """
    bed_summary = await get_bed_summary_for_room(db, room_id)

    if not bed_summary:
        raise HTTPException(
            status_code=404,
            detail=f"Room {room_id} not found"
        )

    return bed_summary


@router.get("/beds/summary/room/{room_id}/bpjs-format", response_model=dict)
async def get_room_bed_summary_bpjs_format(
    room_id: int,
    room_code_prefix: str = Query("RM", description="Prefix for room code generation"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get bed summary for a room in BPJS Aplicare format.

    This endpoint returns the bed data formatted for BPJS Aplicare sync,
    useful for previewing what data will be sent to BPJS.

    Args:
        room_id: Room ID
        room_code_prefix: Prefix for room code generation
        current_user: Authenticated user
        db: Database session

    Returns:
        Bed data in BPJS format

    Raises:
        HTTPException 404: If room not found
    """
    bed_summary = await get_bed_summary_for_room(db, room_id)

    if not bed_summary:
        raise HTTPException(
            status_code=404,
            detail=f"Room {room_id} not found"
        )

    bpjs_format = convert_to_bpjs_bed_format(bed_summary, room_code_prefix)

    return {
        "internal_data": bed_summary,
        "bpjs_format": bpjs_format,
    }
