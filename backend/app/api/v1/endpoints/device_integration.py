"""Device/Instrument Integration API Endpoints for STORY-024-05

This module provides API endpoints for:
- Medical device registration and management
- Device data capture and retrieval
- Device alert management
- Device calibration tracking

Python 3.5+ compatible
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user, get_current_admin_user
from app.services.device_integration import get_device_integration_service


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class DeviceRegisterRequest(BaseModel):
    """Request to register device"""
    device_name: str = Field(..., description="Device name")
    device_type: str = Field(..., description="Device type")
    serial_number: str = Field(..., description="Device serial number")
    protocol: str = Field(..., description="Communication protocol (HL7, ASTM, TCP_IP, etc.)")
    manufacturer: Optional[str] = Field(None, description="Manufacturer")
    model: Optional[str] = Field(None, description="Model number")
    firmware_version: Optional[str] = Field(None, description="Firmware version")
    location: Optional[str] = Field(None, description="Device location")
    department: Optional[str] = Field(None, description="Department")
    station: Optional[str] = Field(None, description="Station/Room")
    endpoint_url: Optional[str] = Field(None, description="Device endpoint URL")
    auth_type: Optional[str] = Field(None, description="Authentication type")
    auto_capture: bool = Field(False, description="Enable automatic data capture")
    capture_interval_seconds: Optional[int] = Field(None, description="Data capture interval")
    data_format: str = Field("json", description="Data format (json, hl7, csv)")


class DeviceDataCaptureRequest(BaseModel):
    """Request to capture device data"""
    device_id: str = Field(..., description="Device ID")
    raw_data: str = Field(..., description="Raw data from device")
    patient_id: Optional[int] = Field(None, description="Patient ID")
    encounter_id: Optional[int] = Field(None, description="Encounter ID")


class DeviceAlertCreateRequest(BaseModel):
    """Request to create device alert"""
    device_id: str = Field(..., description="Device ID")
    alert_type: str = Field(..., description="Alert type")
    alert_severity: str = Field(..., description="Alert severity (low, medium, high, critical)")
    alert_message: str = Field(..., description="Alert message")
    patient_id: Optional[int] = Field(None, description="Patient ID")
    alert_data: Optional[dict] = Field(None, description="Additional alert data")


# =============================================================================
# Device Management Endpoints
# =============================================================================

@router.post("/devices", status_code=status.HTTP_201_CREATED)
async def register_device(
    request: DeviceRegisterRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Register a new medical device (admin only)"""
    try:
        service = get_device_integration_service(db)

        result = await service.register_device(
            device_name=request.device_name,
            device_type=request.device_type,
            serial_number=request.serial_number,
            protocol=request.protocol,
            manufacturer=request.manufacturer,
            model=request.model,
            firmware_version=request.firmware_version,
            location=request.location,
            department=request.department,
            station=request.station,
            endpoint_url=request.endpoint_url,
            auth_type=request.auth_type,
            auto_capture=request.auto_capture,
            capture_interval_seconds=request.capture_interval_seconds,
            data_format=request.data_format,
            connection_params={
                "endpoint_url": request.endpoint_url
            }
        )

        return result

    except ValueError as e:
        if "not found" in str(e).lower() or "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error registering device: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register device"
        )


@router.get("/devices/{device_id}")
async def get_device_status(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get device status by device ID"""
    try:
        service = get_device_integration_service(db)

        result = await service.get_device_status(device_id)

        return result

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
        logger.error("Error getting device status: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get device status"
        )


@router.get("/devices")
async def list_devices(
    device_type: Optional[str] = Query(None, description="Filter by device type"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List medical devices with filtering"""
    try:
        from app.models.device_integration import Device
        from sqlalchemy import select, func, and_

        # Build filters
        filters = [Device.is_active == True]

        if device_type:
            filters.append(Device.device_type == device_type)
        if department:
            filters.append(Device.department == department)
        if status:
            filters.append(Device.status == status)

        # Get total count
        count_query = select(func.count(Device.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Get devices with pagination
        offset = (page - 1) * per_page
        query = select(Device)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(Device.device_name).limit(per_page).offset(offset)

        result = await db.execute(query)
        devices = result.scalars().all()

        # Build response
        device_list = [
            {
                "device_id": d.device_id,
                "device_name": d.device_name,
                "device_type": d.device_type,
                "serial_number": d.serial_number,
                "manufacturer": d.manufacturer,
                "model": d.model,
                "location": d.location,
                "department": d.department,
                "status": d.status,
                "protocol": d.protocol,
                "last_communication_at": d.last_communication_at.isoformat() if d.last_communication_at else None,
                "auto_capture": d.auto_capture
            }
            for d in devices
        ]

        return {
            "devices": device_list,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page if per_page > 0 else 0
        }

    except Exception as e:
        logger.error("Error listing devices: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list devices"
        )


# =============================================================================
# Data Capture Endpoints
# =============================================================================

@router.post("/data/capture", status_code=status.HTTP_201_CREATED)
async def capture_device_data(
    request: DeviceDataCaptureRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Capture data from medical device"""
    try:
        service = get_device_integration_service(db)

        result = await service.capture_device_data(
            device_id=request.device_id,
            raw_data=request.raw_data,
            patient_id=request.patient_id,
            encounter_id=request.encounter_id
        )

        return result

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
        logger.error("Error capturing device data: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to capture device data"
        )


@router.get("/data")
async def list_device_data(
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    data_type: Optional[str] = Query(None, description="Filter by data type"),
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List device data records with filtering"""
    try:
        from app.models.device_integration import DeviceData
        from sqlalchemy import select, func, and_

        # Build filters
        filters = []

        if device_id:
            filters.append(DeviceData.device_id == int(device_id))
        if patient_id:
            filters.append(DeviceData.patient_id == patient_id)
        if data_type:
            filters.append(DeviceData.data_type == data_type)
        if start_date:
            filters.append(DeviceData.created_at >= start_date)
        if end_date:
            filters.append(DeviceData.created_at <= end_date)

        # Get total count
        count_query = select(func.count(DeviceData.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Get data with pagination
        offset = (page - 1) * per_page
        query = select(DeviceData)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(DeviceData.created_at.desc()).limit(per_page).offset(offset)

        result = await db.execute(query)
        data_records = result.scalars().all()

        # Build response
        data_list = []
        for record in data_records:
            data_item = {
                "record_id": record.record_id,
                "device_id": record.device_id,
                "patient_id": record.patient_id,
                "data_type": record.data_type,
                "measured_at": record.measured_at.isoformat() if record.measured_at else None,
                "received_at": record.received_at.isoformat(),
                "is_imported": record.is_imported
            }

            # Add vitals if present
            if record.heart_rate:
                data_item["heart_rate"] = record.heart_rate
            if record.blood_pressure_systolic:
                data_item["blood_pressure_systolic"] = record.blood_pressure_systolic
            if record.blood_pressure_diastolic:
                data_item["blood_pressure_diastolic"] = record.blood_pressure_diastolic
            if record.temperature:
                data_item["temperature"] = record.temperature
            if record.spo2:
                data_item["spo2"] = record.spo2
            if record.blood_glucose:
                data_item["blood_glucose"] = record.blood_glucose

            data_list.append(data_item)

        return {
            "data": data_list,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page if per_page > 0 else 0
        }

    except Exception as e:
        logger.error("Error listing device data: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list device data"
        )


# =============================================================================
# Alert Endpoints
# =============================================================================

@router.post("/alerts", status_code=status.HTTP_201_CREATED)
async def create_device_alert(
    request: DeviceAlertCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create device alert"""
    try:
        service = get_device_integration_service(db)

        result = await service.create_device_alert(
            device_id=request.device_id,
            alert_type=request.alert_type,
            alert_severity=request.alert_severity,
            alert_message=request.alert_message,
            patient_id=request.patient_id,
            alert_data=request.alert_data
        )

        return result

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
        logger.error("Error creating device alert: {}".format(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create device alert"
        )


@router.get("/alerts")
async def list_device_alerts(
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    is_resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List device alerts with filtering"""
    try:
        from app.models.device_integration import DeviceAlert
        from sqlalchemy import select, func, and_

        # Build filters
        filters = []

        if device_id:
            filters.append(DeviceAlert.device_id == int(device_id))
        if severity:
            filters.append(DeviceAlert.alert_severity == severity)
        if is_resolved is not None:
            filters.append(DeviceAlert.is_resolved == is_resolved)

        # Get total count
        count_query = select(func.count(DeviceAlert.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Get alerts with pagination
        offset = (page - 1) * per_page
        query = select(DeviceAlert)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(DeviceAlert.created_at.desc()).limit(per_page).offset(offset)

        result = await db.execute(query)
        alerts = result.scalars().all()

        # Build response
        alert_list = [
            {
                "alert_id": a.alert_id,
                "device_id": a.device_id,
                "alert_type": a.alert_type,
                "alert_severity": a.alert_severity,
                "alert_message": a.alert_message,
                "is_resolved": a.is_resolved,
                "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
                "created_at": a.created_at.isoformat()
            }
            for a in alerts
        ]

        return {
            "alerts": alert_list,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page if per_page > 0 else 0
        }

    except Exception as e:
        logger.error("Error listing device alerts: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list device alerts"
        )


# =============================================================================
# Statistics Endpoints
# =============================================================================

@router.get("/statistics")
async def get_device_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get device integration statistics"""
    try:
        from app.models.device_integration import Device, DeviceData, DeviceAlert, DeviceStatus
        from sqlalchemy import select, func

        # Get device counts by status
        status_query = select(
            Device.status,
            func.count(Device.id).label("count")
        ).group_by(Device.status)

        status_result = await db.execute(status_query)
        status_counts = {row[0]: row[1] for row in status_result.all()}

        # Get total devices
        total_query = select(func.count(Device.id))
        total_result = await db.execute(total_query)
        total_devices = total_result.scalar() or 0

        # Get total data records
        data_query = select(func.count(DeviceData.id))
        data_result = await db.execute(data_query)
        total_data_records = data_result.scalar() or 0

        # Get unresolved alerts
        alert_query = select(func.count(DeviceAlert.id)).where(
            DeviceAlert.is_resolved == False
        )
        alert_result = await db.execute(alert_query)
        unresolved_alerts = alert_result.scalar() or 0

        # Get device type breakdown
        type_query = select(
            Device.device_type,
            func.count(Device.id).label("count")
        ).group_by(Device.device_type)

        type_result = await db.execute(type_query)
        type_counts = {row[0]: row[1] for row in type_result.all()}

        return {
            "total_devices": total_devices,
            "total_data_records": total_data_records,
            "unresolved_alerts": unresolved_alerts,
            "status_counts": status_counts,
            "type_counts": type_counts,
            "summary": {
                "online": status_counts.get(DeviceStatus.ONLINE, 0),
                "offline": status_counts.get(DeviceStatus.OFFLINE, 0),
                "error": status_counts.get(DeviceStatus.ERROR, 0),
                "maintenance": status_counts.get(DeviceStatus.MAINTENANCE, 0),
            }
        }

    except Exception as e:
        logger.error("Error getting device statistics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )
