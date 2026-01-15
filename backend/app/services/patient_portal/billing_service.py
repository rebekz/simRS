"""Billing & Payments Service for Patient Portal

Service for patients to view and pay their bills through patient portal.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, desc, or_
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
import secrets

from app.models.billing import Invoice, InvoiceItem, Payment, InvoiceStatus
from app.models.user import User
from app.schemas.patient_portal.billing import (
    InvoiceDetail,
    InvoiceListItem,
    InvoiceListResponse,
    PaymentInitiationRequest,
    PaymentInitiationResponse,
    PaymentRecord,
    PaymentMethodConfig,
    PaymentMethod,
)


class BillingService:
    """Service for handling billing and payments for patients"""

    # Payment method configurations (simulated - would come from payment gateway)
    PAYMENT_METHODS = {
        PaymentMethod.CREDIT_CARD: {
            "name": "Credit/Debit Card",
            "is_available": True,
            "fee_percentage": Decimal("0.025"),  # 2.5% fee
            "min_amount": Decimal("10000"),
            "max_amount": Decimal("50000000"),
            "description": "Visa, Mastercard, JCB",
        },
        PaymentMethod.TRANSFER: {
            "name": "Bank Transfer",
            "is_available": True,
            "fee_percentage": Decimal("0"),
            "min_amount": Decimal("10000"),
            "max_amount": Decimal("100000000"),
            "description": "Transfer to virtual account",
        },
        PaymentMethod.VIRTUAL_ACCOUNT: {
            "name": "Virtual Account",
            "is_available": True,
            "fee_percentage": Decimal("0"),
            "min_amount": Decimal("10000"),
            "max_amount": Decimal("100000000"),
            "description": "Mandiri, BCA, BNI, BRI",
        },
        PaymentMethod.EWALLET: {
            "name": "E-Wallet",
            "is_available": True,
            "fee_percentage": Decimal("0.015"),  # 1.5% fee
            "min_amount": Decimal("10000"),
            "max_amount": Decimal("20000000"),
            "description": "GoPay, OVO, Dana, LinkAja",
        },
        PaymentMethod.QRIS: {
            "name": "QRIS",
            "is_available": True,
            "fee_percentage": Decimal("0.007"),  # 0.7% fee
            "min_amount": Decimal("1000"),
            "max_amount": Decimal("10000000"),
            "description": "Scan QR code to pay",
        },
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_invoices(
        self, patient_id: int, status_filter: Optional[str] = None
    ) -> InvoiceListResponse:
        """Get patient's invoices

        Args:
            patient_id: Patient ID
            status_filter: Optional filter by status (unpaid, overdue, all)

        Returns:
            InvoiceListResponse with invoices and summary
        """
        # Build query
        query = (
            select(Invoice)
            .options(selectinload(Invoice.items))
            .where(Invoice.patient_id == patient_id)
            .where(Invoice.status.in_([InvoiceStatus.APPROVED, InvoiceStatus.PAID, InvoiceStatus.PARTIAL_PAID]))
        )

        # Apply status filter
        if status_filter == "unpaid":
            query = query.where(Invoice.balance_due > 0)
        elif status_filter == "overdue":
            query = query.where(
                and_(
                    Invoice.balance_due > 0,
                    Invoice.due_date < date.today()
                )
            )

        query = query.order_by(desc(Invoice.invoice_date))

        result = await self.db.execute(query)
        invoices = result.scalars().all()

        # Calculate totals
        outstanding_balance = Decimal("0")
        overdue_count = 0
        overdue_amount = Decimal("0")
        today = date.today()

        invoice_items = []
        for invoice in invoices:
            is_overdue = invoice.due_date and invoice.due_date < today and invoice.balance_due > 0

            if is_overdue:
                overdue_count += 1
                overdue_amount += invoice.balance_due

            outstanding_balance += invoice.balance_due

            invoice_items.append(
                InvoiceListItem(
                    id=invoice.id,
                    invoice_number=invoice.invoice_number,
                    invoice_date=invoice.invoice_date,
                    invoice_type=invoice.invoice_type,
                    status=invoice.status,
                    total_amount=invoice.total_amount,
                    paid_amount=invoice.paid_amount,
                    balance_due=invoice.balance_due,
                    due_date=invoice.due_date,
                    is_overdue=is_overdue,
                    payer_type=invoice.payer_type,
                )
            )

        return InvoiceListResponse(
            invoices=invoice_items,
            total=len(invoice_items),
            outstanding_balance=outstanding_balance,
            overdue_count=overdue_count,
            overdue_amount=overdue_amount,
        )

    async def get_invoice_detail(self, patient_id: int, invoice_id: int) -> Optional[InvoiceDetail]:
        """Get detailed invoice information

        Args:
            patient_id: Patient ID
            invoice_id: Invoice ID

        Returns:
            InvoiceDetail with items and payment history
        """
        # Get invoice with items and payments
        result = await self.db.execute(
            select(Invoice)
            .options(
                selectinload(Invoice.items),
                selectinload(Invoice.payments),
            )
            .where(
                and_(
                    Invoice.id == invoice_id,
                    Invoice.patient_id == patient_id,
                )
            )
        )
        invoice = result.scalar_one_or_none()

        if not invoice:
            return None

        # Build payment history
        payment_history = [
            PaymentRecord(
                id=payment.id,
                payment_date=payment.payment_date,
                payment_method=payment.payment_method,
                amount=payment.amount,
                reference_number=payment.reference_number,
                bank_name=payment.bank_name,
            )
            for payment in invoice.payments
        ]

        # Build invoice items with doctor names
        items = []
        for item in invoice.items:
            # Get doctor name if doctor_id exists
            doctor_name = None
            if item.doctor_id:
                doctor_result = await self.db.execute(
                    select(User.full_name).where(User.id == item.doctor_id)
                )
                doctor_name = doctor_result.scalar_one_or_none()

            items.append(
                InvoiceItem(
                    id=item.id,
                    item_type=item.item_type,
                    item_code=item.item_code,
                    item_name=item.item_name,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=item.subtotal,
                    tax_amount=item.tax_amount,
                    discount_amount=item.discount_amount,
                    total=item.total,
                    doctor_name=doctor_name,
                    service_date=item.service_date,
                    is_bpjs_covered=item.is_bpjs_covered,
                )
            )

        return InvoiceDetail(
            id=invoice.id,
            invoice_number=invoice.invoice_number,
            invoice_date=invoice.invoice_date,
            invoice_type=invoice.invoice_type,
            status=invoice.status,
            due_date=invoice.due_date,
            payer_type=invoice.payer_type,
            insurance_company=invoice.insurance_company,
            policy_number=invoice.policy_number,
            bpjs_membership_number=invoice.bpjs_membership_number,
            subtotal=invoice.subtotal,
            tax_amount=invoice.tax_amount,
            discount_amount=invoice.discount_amount,
            total_amount=invoice.total_amount,
            paid_amount=invoice.paid_amount,
            balance_due=invoice.balance_due,
            items=items,
            payment_history=payment_history,
            outstanding_balance=invoice.balance_due,
            created_at=invoice.created_at,
            approved_at=invoice.approved_at,
        )

    async def initiate_payment(
        self, patient_id: int, request: PaymentInitiationRequest
    ) -> PaymentInitiationResponse:
        """Initiate payment for an invoice

        Args:
            patient_id: Patient ID
            request: Payment initiation request

        Returns:
            PaymentInitiationResponse with payment details
        """
        # Validate invoice exists and belongs to patient
        invoice_result = await self.db.execute(
            select(Invoice).where(
                and_(
                    Invoice.id == request.invoice_id,
                    Invoice.patient_id == patient_id,
                    Invoice.balance_due > 0,
                )
            )
        )
        invoice = invoice_result.scalar_one_or_none()

        if not invoice:
            raise ValueError("Invoice not found or already paid")

        # Validate amount
        if request.amount > invoice.balance_due:
            raise ValueError("Payment amount exceeds outstanding balance")

        # Get payment method config
        method_config = self.PAYMENT_METHODS.get(request.payment_method)
        if not method_config or not method_config["is_available"]:
            raise ValueError("Payment method not available")

        # Calculate fee
        fee = request.amount * method_config["fee_percentage"]
        total_amount = request.amount + fee

        # Generate payment ID
        payment_id = f"PAY-{datetime.utcnow().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"

        # In production, this would integrate with payment gateway (Midtrans, Xendit, etc.)
        # For now, return simulated response
        payment_response = PaymentInitiationResponse(
            payment_id=payment_id,
            amount=total_amount,
            message="Payment initiated successfully",
        )

        # Add method-specific details
        if request.payment_method == PaymentMethod.QRIS:
            # Simulate QR code
            payment_response.qr_code = f"QRIS-{payment_id}"
        elif request.payment_method == PaymentMethod.VIRTUAL_ACCOUNT:
            # Simulate virtual account number
            bank_code = "8800"  # Example bank code
            payment_response.virtual_account_number = f"{bank_code}{invoice.id:010d}"
        elif request.payment_method in [PaymentMethod.CREDIT_CARD, PaymentMethod.EWALLET]:
            # Simulate payment URL
            payment_response.payment_url = f"https://payment.simrs.id/pay/{payment_id}"

        return payment_response

    async def get_payment_methods(self) -> List[PaymentMethodConfig]:
        """Get available payment methods

        Returns:
            List of payment method configurations
        """
        methods = []
        for method, config in self.PAYMENT_METHODS.items():
            methods.append(
                PaymentMethodConfig(
                    method=method,
                    name=config["name"],
                    is_available=config["is_available"],
                    fee_percentage=config["fee_percentage"],
                    min_amount=config["min_amount"],
                    max_amount=config["max_amount"],
                    description=config["description"],
                )
            )
        return methods
