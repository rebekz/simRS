"""Bed sync service for BPJS Aplicare integration (STORY-032).

This module provides functions to sync bed availability data with BPJS Aplicare API,
converting internal bed data to BPJS format and handling real-time sync triggers.
"""
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.services.bpjs_aplicare import BPJSAplicareClient, BPJSAplicareError
from app.models.bed import Room, Bed
from app.schemas.bpjs import BPJSAplicareBedCreate, BPJSAplicareBedUpdate

logger = logging.getLogger(__name__)


# =============================================================================
# Room Class Mapping
# =============================================================================

# Map internal room class to BPJS Aplicare format
ROOM_CLASS_MAPPING = {
    "vvip": "VVIP",
    "vip": "VIP",
    "1": "1",
    "2": "2",
    "3": "3",
}


def map_room_class_to_bpjs(room_class: str) -> str:
    """
    Map internal room class to BPJS Aplicare format.

    Args:
        room_class: Internal room class (vvip, vip, 1, 2, 3)

    Returns:
        BPJS room class code (VVIP, VIP, 1, 2, 3)
    """
    return ROOM_CLASS_MAPPING.get(room_class, "3")  # Default to class 3


# =============================================================================
# Bed Data Conversion
# =============================================================================

async def get_bed_summary_for_room(
    db: AsyncSession,
    room_id: int
) -> Optional[Dict[str, Any]]:
    """
    Get bed summary statistics for a room.

    Args:
        db: Database session
        room_id: Room ID

    Returns:
        Dictionary with bed statistics or None if room not found
    """
    # Get room details
    room_result = await db.execute(select(Room).filter(Room.id == room_id))
    room = room_result.scalar_one_or_none()

    if not room:
        return None

    # Get bed statistics
    beds_result = await db.execute(
        select(Bed).filter(Bed.room_id == room_id)
    )
    beds = beds_result.scalars().all()

    # Count by status
    total_beds = len(beds)
    available_beds = sum(1 for b in beds if b.status == "available")
    occupied_beds = sum(1 for b in beds if b.status == "occupied")
    maintenance_beds = sum(1 for b in beds if b.status == "maintenance")
    reserved_beds = sum(1 for b in beds if b.status == "reserved")

    # Calculate by gender type (based on room's gender_type setting)
    if room.gender_type == "male":
        available_male = available_beds
        available_female = 0
        available_mixed = 0
    elif room.gender_type == "female":
        available_male = 0
        available_female = available_beds
        available_mixed = 0
    else:  # mixed
        # For mixed rooms, distribute evenly or use a specific ratio
        # For now, use a simple distribution
        available_mixed = available_beds
        available_male = 0
        available_female = 0

    return {
        "room_id": room.id,
        "room_number": room.room_number,
        "ward_id": room.ward_id,
        "room_class": room.room_class,
        "gender_type": room.gender_type,
        "total_beds": total_beds,
        "available_beds": available_beds,
        "available_male": available_male,
        "available_female": available_female,
        "available_mixed": available_mixed,
        "occupied_beds": occupied_beds,
        "maintenance_beds": maintenance_beds,
        "reserved_beds": reserved_beds,
    }


def convert_to_bpjs_bed_format(
    bed_summary: Dict[str, Any],
    room_code_prefix: str = "RM"
) -> Dict[str, Any]:
    """
    Convert internal bed summary to BPJS Aplicare format.

    Args:
        bed_summary: Internal bed summary data
        room_code_prefix: Prefix for room code generation

    Returns:
        Dictionary in BPJS Aplicare bed format
    """
    room_class = map_room_class_to_bpjs(bed_summary["room_class"])
    room_code = f"{room_code_prefix}{bed_summary['ward_id']}-{bed_summary['room_number']}"

    return {
        "kodekelas": room_class,
        "koderuang": room_code,
        "namaruang": f"Room {bed_summary['room_number']}",
        "kapasitas": bed_summary["total_beds"],
        "tersedia": bed_summary["available_beds"],
        "tersediapria": bed_summary["available_male"],
        "tersediawanita": bed_summary["available_female"],
        "tersediapriawanita": bed_summary["available_mixed"],
    }


# =============================================================================
# Bed Sync Operations
# =============================================================================

async def sync_room_to_bpjs(
    db: AsyncSession,
    room_id: int,
    bpjs_client: BPJSAplicareClient,
    force_update: bool = False
) -> Dict[str, Any]:
    """
    Sync a single room's bed data to BPJS Aplicare.

    Args:
        db: Database session
        room_id: Room ID to sync
        bpjs_client: BPJS Aplicare API client
        force_update: Force update even if data unchanged

    Returns:
        Sync result dictionary
    """
    try:
        # Get bed summary
        bed_summary = await get_bed_summary_for_room(db, room_id)
        if not bed_summary:
            return {
                "success": False,
                "message": f"Room {room_id} not found",
                "room_id": room_id,
            }

        # Convert to BPJS format
        bpjs_bed_data = convert_to_bpjs_bed_format(bed_summary)

        # Try to update first (assuming room exists)
        try:
            result = await bpjs_client.update_bed(**bpjs_bed_data)
            logger.info(f"Updated BPJS bed data for room {room_id}")
            return {
                "success": True,
                "message": "Bed data updated successfully",
                "room_id": room_id,
                "bpjs_response": result,
                "action": "update",
            }
        except BPJSAplicareError as e:
            # If update fails with "not found", try create instead
            if "not found" in str(e.message).lower() or "404" in str(e.code):
                try:
                    result = await bpjs_client.create_bed(**bpjs_bed_data)
                    logger.info(f"Created BPJS bed data for room {room_id}")
                    return {
                        "success": True,
                        "message": "Bed data created successfully",
                        "room_id": room_id,
                        "bpjs_response": result,
                        "action": "create",
                    }
                except BPJSAplicareError as create_error:
                    logger.error(f"Failed to create BPJS bed data for room {room_id}: {create_error}")
                    return {
                        "success": False,
                        "message": f"Failed to create bed data: {create_error.message}",
                        "room_id": room_id,
                        "error": str(create_error),
                    }
            else:
                logger.error(f"Failed to update BPJS bed data for room {room_id}: {e}")
                return {
                    "success": False,
                    "message": f"Failed to update bed data: {e.message}",
                    "room_id": room_id,
                    "error": str(e),
                }

    except Exception as e:
        logger.exception(f"Unexpected error syncing room {room_id} to BPJS")
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "room_id": room_id,
            "error": str(e),
        }


async def sync_all_rooms_to_bpjs(
    db: AsyncSession,
    bpjs_client: BPJSAplicareClient,
    ward_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Sync all rooms (or rooms in a ward) to BPJS Aplicare.

    Args:
        db: Database session
        bpjs_client: BPJS Aplicare API client
        ward_id: Optional ward ID to filter rooms

    Returns:
        Sync result summary
    """
    # Get all rooms to sync
    query = select(Room)
    if ward_id:
        query = query.filter(Room.ward_id == ward_id)

    rooms_result = await db.execute(query)
    rooms = rooms_result.scalars().all()

    success_count = 0
    failure_count = 0
    results = []

    for room in rooms:
        result = await sync_room_to_bpjs(db, room.id, bpjs_client)
        results.append(result)
        if result["success"]:
            success_count += 1
        else:
            failure_count += 1

    return {
        "total_rooms": len(rooms),
        "success_count": success_count,
        "failure_count": failure_count,
        "results": results,
    }


async def delete_room_from_bpjs(
    bpjs_client: BPJSAplicareClient,
    room_id: int,
    room_class: str,
    room_code: str
) -> Dict[str, Any]:
    """
    Delete a room from BPJS Aplicare.

    Args:
        bpjs_client: BPJS Aplicare API client
        room_id: Room ID
        room_class: Internal room class
        room_code: Room code in BPJS format

    Returns:
        Delete result dictionary
    """
    try:
        bpjs_room_class = map_room_class_to_bpjs(room_class)
        result = await bpjs_client.delete_bed(
            kodekelas=bpjs_room_class,
            koderuang=room_code,
        )

        logger.info(f"Deleted room {room_id} from BPJS Aplicare")
        return {
            "success": True,
            "message": "Room deleted successfully from BPJS",
            "room_id": room_id,
            "bpjs_response": result,
        }

    except BPJSAplicareError as e:
        logger.error(f"Failed to delete room {room_id} from BPJS: {e}")
        return {
            "success": False,
            "message": f"Failed to delete room: {e.message}",
            "room_id": room_id,
            "error": str(e),
        }
    except Exception as e:
        logger.exception(f"Unexpected error deleting room {room_id} from BPJS")
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "room_id": room_id,
            "error": str(e),
        }


# =============================================================================
# Real-time Sync Triggers
# =============================================================================

async def trigger_bed_sync_on_status_change(
    db: AsyncSession,
    bed_id: int,
    old_status: str,
    new_status: str
) -> Optional[Dict[str, Any]]:
    """
    Trigger BPJS sync when bed status changes.

    This should be called after a bed's status changes to automatically
    sync the new availability to BPJS Aplicare.

    Args:
        db: Database session
        bed_id: Bed ID that changed
        old_status: Previous bed status
        new_status: New bed status

    Returns:
        Sync result or None if sync failed
    """
    try:
        # Get the bed to find its room
        bed_result = await db.execute(select(Bed).filter(Bed.id == bed_id))
        bed = bed_result.scalar_one_or_none()

        if not bed or not bed.room_id:
            logger.warning(f"Bed {bed_id} not found or has no room_id")
            return None

        # Sync the room to BPJS
        async with BPJSAplicareClient() as client:
            return await sync_room_to_bpjs(db, bed.room_id, client)

    except Exception as e:
        logger.exception(f"Failed to trigger bed sync for bed {bed_id}")
        return None


async def trigger_bed_sync_on_assignment_change(
    db: AsyncSession,
    room_id: int
) -> Optional[Dict[str, Any]]:
    """
    Trigger BPJS sync when a bed assignment changes.

    This should be called after a patient is assigned to or discharged from a bed.

    Args:
        db: Database session
        room_id: Room ID that needs syncing

    Returns:
        Sync result or None if sync failed
    """
    try:
        # Sync the room to BPJS
        async with BPJSAplicareClient() as client:
            return await sync_room_to_bpjs(db, room_id, client)

    except Exception as e:
        logger.exception(f"Failed to trigger bed sync for room {room_id}")
        return None
