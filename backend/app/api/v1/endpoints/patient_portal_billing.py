"""Patient Portal Billing & Payments Endpoints

API endpoints for patients to view and pay their bills.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.deps import get_db, get_current_portal_patient
from app.models.patient_portal import PatientPortalUser
from app.schemas.patient_portal.billing import (
    InvoiceListResponse,
    InvoiceDetail,
    PaymentInitiationRequest,
    PaymentInitiationResponse,
    PaymentMethodConfig,
)

router = APIRouter()


@router.get("/billing/invoices", response_model=InvoiceListResponse)
async def get_invoices(
    status: Optional[str] = Query(None, description="Filter by status: unpaid, overdue, or all"),
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Get patient's invoices

    Returns all invoices with optional filtering:
    - status=unpaid: Only unpaid invoices
    - status=overdue: Only overdue invoices
    - No filter: All invoices
    """
    from app.services.patient_portal.billing_service import BillingService

    service = BillingService(db)
    invoices = await service.get_invoices(current_user.patient_id, status)
    return invoices


@router.get("/billing/invoices/{invoice_id}", response_model=InvoiceDetail)
async def get_invoice_detail(
    invoice_id: int,
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed invoice information

    Returns invoice details including:
    - Line items with descriptions
    - Tax and discount breakdown
    - Payment history
    - Outstanding balance
    """
    from app.services.patient_portal.billing_service import BillingService

    service = BillingService(db)
    invoice = await service.get_invoice_detail(current_user.patient_id, invoice_id)

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    return invoice


@router.get("/billing/payment-methods", response_model=list[PaymentMethodConfig])
async def get_payment_methods(
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Get available payment methods

    Returns all payment methods with their configurations:
    - Fees
    - Min/max amounts
    - Availability
    """
    from app.services.patient_portal.billing_service import BillingService

    service = BillingService(db)
    methods = await service.get_payment_methods()
    return methods


@router.post("/billing/payments/initiate", response_model=PaymentInitiationResponse, status_code=status.HTTP_201_CREATED)
async def initiate_payment(
    request: PaymentInitiationRequest,
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Initiate payment for an invoice

    Creates a payment transaction and returns payment details:
    - For QRIS: Returns QR code string
    - For Virtual Account: Returns VA number
    - For Credit Card/E-Wallet: Returns payment URL

    Payment gateway integration is simulated - would integrate with
    Midtrans, Xendit, or similar in production.
    """
    from app.services.patient_portal.billing_service import BillingService

    service = BillingService(db)

    try:
        response = await service.initiate_payment(current_user.patient_id, request)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate payment: {str(e)}",
        )
