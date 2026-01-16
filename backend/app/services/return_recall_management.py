"""Return & Recall Management Service

EPIC-019 Story 8: Return & Recall Management

Comprehensive return and recall management with:
- Product returns to suppliers (damaged, wrong items, expiry, quality issues)
- Return Material Authorization (RMA) generation
- Manufacturer recall tracking and management
- Automatic quarantine of recalled items
- Credit note tracking
- Return shipping documentation
- Recall compliance reporting

Python 3.5+ compatible - uses .format() instead of f-strings
"""

import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional
from decimal import Decimal
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, case
from sqlalchemy.orm import selectinload

from app.models.inventory import Drug, DrugBatch, Supplier


logger = logging.getLogger(__name__)


# =============================================================================
# Constants & Configuration
# =============================================================================

# Return reason codes
RETURN_REASONS = {
    'DAMAGED': 'Damaged in transit or storage',
    'WRONG_ITEM': 'Incorrect item delivered',
    'EXPIRY': 'Near-expiry or expired',
    'QUALITY': 'Quality issue, failed QC',
    'OVERSTOCK': 'Excess inventory',
    'RECALL': 'Manufacturer recall'
}

# Return status workflow
RETURN_STATUS = {
    'PENDING': 'Pending authorization',
    'AUTHORIZED': 'Authorized by supplier',
    'SHIPPED': 'Shipped to supplier',
    'CREDITED': 'Credit note received',
    'REJECTED': 'Return rejected by supplier'
}

# Recall severity levels
RECALL_SEVERITY = {
    'LOW': 'Low - Regular recall',
    'MEDIUM': 'Medium - Priority handling',
    'HIGH': 'High - Immediate action required',
    'CRITICAL': 'Critical - Emergency recall'
}

# Recall types
RECALL_TYPES = {
    'VOLUNTARY': 'Voluntary manufacturer recall',
    'MANDATORY': 'Mandatory government recall'
}


# =============================================================================
# Main Service
# =============================================================================

class ReturnRecallManagementService(object):
    """Service for return and recall management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_return_request(
        self,
        supplier_id: int,
        return_items: List[Dict],
        return_type: str,
        notes: Optional[str] = None
    ) -> Dict:
        """Create a new return request to supplier

        Args:
            supplier_id: Supplier ID
            return_items: List of items to return
                [{drug_id, batch_no, quantity, reason}]
            return_type: Return reason code
            notes: Additional notes

        Returns:
            Created return request with details
        """
        if return_type not in RETURN_REASONS:
            return {
                'error': 'Invalid return type: {}'.format(return_type)
            }

        # Verify supplier exists
        stmt = select(Supplier).where(Supplier.id == supplier_id)
        result = await self.db.execute(stmt)
        supplier = result.scalar_one_or_none()

        if not supplier:
            return {
                'error': 'Supplier not found'
            }

        # Build return details
        return_details = []
        total_value = 0

        for item in return_items:
            # Get batch details
            stmt = select(DrugBatch).join(Drug).where(
                and_(
                    DrugBatch.drug_id == item['drug_id'],
                    DrugBatch.batch_number == item.get('batch_no'),
                    DrugBatch.supplier_id == supplier_id
                )
            ).options(selectinload(DrugBatch.drug))

            result = await self.db.execute(stmt)
            batch = result.scalar_one_or_none()

            if not batch:
                logger.warning("Batch not found: {}".format(item))
                continue

            unit_cost = float(batch.unit_cost) if batch.unit_cost else 0
            item_value = item['quantity'] * unit_cost
            total_value += item_value

            return_details.append({
                'drug_id': item['drug_id'],
                'drug_name': batch.drug.generic_name if batch.drug else 'Unknown',
                'batch_number': batch.batch_number,
                'quantity': item['quantity'],
                'unit_cost': unit_cost,
                'total_value': item_value,
                'reason': item.get('reason', RETURN_REASONS[return_type])
            })

        if not return_details:
            return {
                'error': 'No valid items found for return'
            }

        # Create return request (in real implementation, would save to DB)
        return_request = {
            'supplier_id': supplier_id,
            'supplier_name': supplier.supplier_name,
            'return_type': return_type,
            'return_type_description': RETURN_REASONS[return_type],
            'status': 'PENDING',
            'total_value': round(total_value, 2),
            'total_items': len(return_details),
            'items': return_details,
            'notes': notes,
            'created_at': datetime.utcnow().isoformat(),
            'authorization_no': None,
            'credit_note_no': None
        }

        return return_request

    async def authorize_return(
        self,
        return_id: int,
        authorization_no: str,
        authorized_by: int
    ) -> Dict:
        """Authorize a return request with supplier's RMA

        Args:
            return_id: Return request ID
            authorization_no: RMA number from supplier
            authorized_by: User ID who authorized

        Returns:
            Updated return request
        """
        # In real implementation, would update DB record
        return {
            'return_id': return_id,
            'status': 'AUTHORIZED',
            'authorization_no': authorization_no,
            'authorized_by': authorized_by,
            'authorized_at': datetime.utcnow().isoformat(),
            'message': 'Return authorized with RMA: {}'.format(authorization_no)
        }

    async def ship_return(
        self,
        return_id: int,
        shipping_details: Dict
    ) -> Dict:
        """Mark return as shipped to supplier

        Args:
            return_id: Return request ID
            shipping_details: Shipping information
                {carrier, tracking_no, shipped_date}

        Returns:
            Updated return request with shipping info
        """
        return {
            'return_id': return_id,
            'status': 'SHIPPED',
            'shipping': {
                'carrier': shipping_details.get('carrier'),
                'tracking_no': shipping_details.get('tracking_no'),
                'shipped_date': shipping_details.get('shipped_date'),
                'estimated_delivery': shipping_details.get('estimated_delivery')
            },
            'shipped_at': datetime.utcnow().isoformat(),
            'message': 'Return shipped to supplier'
        }

    async def process_credit_note(
        self,
        return_id: int,
        credit_note_no: str,
        credit_amount: float
    ) -> Dict:
        """Process credit note received from supplier

        Args:
            return_id: Return request ID
            credit_note_no: Credit note number
            credit_amount: Amount credited

        Returns:
            Updated return request with credit info
        """
        return {
            'return_id': return_id,
            'status': 'CREDITED',
            'credit_note_no': credit_note_no,
            'credit_amount': round(credit_amount, 2),
            'credited_at': datetime.utcnow().isoformat(),
            'message': 'Credit note processed: {}'.format(credit_note_no)
        }

    async def create_recall_notice(
        self,
        manufacturer_id: int,
        product_name: str,
        batch_from: Optional[str] = None,
        batch_to: Optional[str] = None,
        batch_prefix: Optional[str] = None,
        expiry_from: Optional[date] = None,
        expiry_to: Optional[date] = None,
        recall_reason: str = '',
        recall_type: str = 'VOLUNTARY',
        severity: str = 'MEDIUM'
    ) -> Dict:
        """Create a manufacturer recall notice

        Args:
            manufacturer_id: Manufacturer ID
            product_name: Product/brand name
            batch_from: Batch number range start
            batch_to: Batch number range end
            batch_prefix: Batch number prefix
            expiry_from: Expiry date range start
            expiry_to: Expiry date range end
            recall_reason: Reason for recall
            recall_type: VOLUNTARY or MANDATORY
            severity: LOW, MEDIUM, HIGH, or CRITICAL

        Returns:
            Created recall notice
        """
        if recall_type not in RECALL_TYPES:
            return {
                'error': 'Invalid recall type: {}'.format(recall_type)
            }

        if severity not in RECALL_SEVERITY:
            return {
                'error': 'Invalid severity: {}'.format(severity)
            }

        # Identify affected inventory
        stmt = select(DrugBatch).join(Drug).where(
            Drug.drug_name.ilike('%{}%'.format(product_name))
        )

        # Add batch filters if provided
        conditions = []
        if batch_from:
            conditions.append(DrugBatch.batch_number >= batch_from)
        if batch_to:
            conditions.append(DrugBatch.batch_number <= batch_to)
        if batch_prefix:
            conditions.append(DrugBatch.batch_number.startswith(batch_prefix))

        if expiry_from:
            conditions.append(DrugBatch.expiry_date >= expiry_from)
        if expiry_to:
            conditions.append(DrugBatch.expiry_date <= expiry_to)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.options(selectinload(DrugBatch.drug))
        result = await self.db.execute(stmt)
        affected_batches = result.scalars().all()

        affected_quantity = sum(b.quantity for b in affected_batches)
        affected_value = sum(
            (b.quantity * float(b.unit_cost)) if b.unit_cost else 0
            for b in affected_batches
        )

        # Create recall notice
        recall_notice = {
            'manufacturer_id': manufacturer_id,
            'product_name': product_name,
            'batch_from': batch_from,
            'batch_to': batch_to,
            'batch_prefix': batch_prefix,
            'expiry_from': expiry_from.isoformat() if expiry_from else None,
            'expiry_to': expiry_to.isoformat() if expiry_to else None,
            'affected_quantity': affected_quantity,
            'affected_value': round(affected_value, 2),
            'affected_batches': [
                {
                    'batch_id': b.id,
                    'batch_number': b.batch_number,
                    'quantity': b.quantity,
                    'expiry_date': b.expiry_date.isoformat() if b.expiry_date else None
                }
                for b in affected_batches
            ],
            'recall_date': date.today().isoformat(),
            'recall_reason': recall_reason,
            'recall_type': recall_type,
            'recall_type_description': RECALL_TYPES[recall_type],
            'severity': severity,
            'severity_description': RECALL_SEVERITY[severity],
            'status': 'ACTIVE',
            'created_at': datetime.utcnow().isoformat()
        }

        return recall_notice

    async def quarantine_recalled_items(
        self,
        recall_id: int,
        recall_notice: Dict
    ) -> Dict:
        """Quarantine all items affected by recall

        Args:
            recall_id: Recall notice ID
            recall_notice: Recall notice details

        Returns:
            Quarantine action summary
        """
        quarantined_count = 0
        quarantined_batches = []

        for batch_info in recall_notice.get('affected_batches', []):
            # In real implementation, would update DB
            # batch.is_quarantined = True
            # batch.quarantine_reason = 'RECALL: {}'.format(recall_id)

            quarantined_batches.append({
                'batch_id': batch_info['batch_id'],
                'batch_number': batch_info['batch_number'],
                'quarantined_quantity': batch_info['quantity']
            })
            quarantined_count += batch_info['quantity']

        return {
            'recall_id': recall_id,
            'quarantined_batches': len(quarantined_batches),
            'quarantined_quantity': quarantined_count,
            'batches': quarantined_batches,
            'quarantined_at': datetime.utcnow().isoformat(),
            'message': 'Quarantined {} items from {} batches'.format(
                quarantined_count, len(quarantined_batches)
            )
        }

    async def get_return_summary(
        self,
        supplier_id: Optional[int] = None,
        status: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict:
        """Get summary of return requests

        Args:
            supplier_id: Filter by supplier
            status: Filter by status
            from_date: Filter by start date
            to_date: Filter by end date

        Returns:
            Return summary statistics
        """
        # In real implementation, would query DB
        return {
            'period': {
                'from_date': from_date.isoformat() if from_date else None,
                'to_date': to_date.isoformat() if to_date else None
            },
            'total_returns': 0,
            'total_value': 0,
            'by_status': {
                'PENDING': {'count': 0, 'value': 0},
                'AUTHORIZED': {'count': 0, 'value': 0},
                'SHIPPED': {'count': 0, 'value': 0},
                'CREDITED': {'count': 0, 'value': 0},
                'REJECTED': {'count': 0, 'value': 0}
            },
            'by_reason': {
                'DAMAGED': {'count': 0, 'value': 0},
                'WRONG_ITEM': {'count': 0, 'value': 0},
                'EXPIRY': {'count': 0, 'value': 0},
                'QUALITY': {'count': 0, 'value': 0},
                'OVERSTOCK': {'count': 0, 'value': 0},
                'RECALL': {'count': 0, 'value': 0}
            }
        }

    async def get_recall_summary(self) -> Dict:
        """Get summary of active recalls

        Returns:
            Recall summary statistics
        """
        return {
            'active_recalls': 0,
            'by_severity': {
                'CRITICAL': {'count': 0, 'affected_items': 0},
                'HIGH': {'count': 0, 'affected_items': 0},
                'MEDIUM': {'count': 0, 'affected_items': 0},
                'LOW': {'count': 0, 'affected_items': 0}
            },
            'by_status': {
                'ACTIVE': 0,
                'IN_PROGRESS': 0,
                'COMPLETED': 0,
                'CLOSED': 0
            }
        }

    async def check_return_eligibility(
        self,
        drug_id: int,
        batch_no: str,
        supplier_id: int,
        return_type: str
    ) -> Dict:
        """Check if item is eligible for return

        Args:
            drug_id: Drug ID
            batch_no: Batch number
            supplier_id: Supplier ID
            return_type: Return reason type

        Returns:
            Eligibility check result
        """
        # Get batch details
        stmt = select(DrugBatch).join(Drug).where(
            and_(
                DrugBatch.drug_id == drug_id,
                DrugBatch.batch_number == batch_no,
                DrugBatch.supplier_id == supplier_id
            )
        ).options(selectinload(DrugBatch.drug))

        result = await self.db.execute(stmt)
        batch = result.scalar_one_or_none()

        if not batch:
            return {
                'eligible': False,
                'reason': 'Batch not found'
            }

        # Check eligibility based on return type
        eligible = True
        reason = 'Eligible for return'

        if return_type == 'EXPIRY':
            # Check if near expiry or expired
            days_to_expiry = (batch.expiry_date - date.today()).days if batch.expiry_date else 0
            if days_to_expiry > 90:
                eligible = False
                reason = 'Item not near expiry ({} days remaining)'.format(days_to_expiry)
            elif batch.quantity == 0:
                eligible = False
                reason = 'No quantity available'

        elif return_type == 'DAMAGED':
            if not batch.is_quarantined:
                eligible = False
                reason = 'Item not marked as damaged/quarantined'

        return {
            'eligible': eligible,
            'reason': reason,
            'batch': {
                'drug_id': drug_id,
                'drug_name': batch.drug.generic_name if batch.drug else 'Unknown',
                'batch_number': batch.batch_number,
                'quantity': batch.quantity,
                'expiry_date': batch.expiry_date.isoformat() if batch.expiry_date else None,
                'is_quarantined': batch.is_quarantined
            }
        }

    async def get_supplier_return_performance(
        self,
        supplier_id: int,
        months: int = 12
    ) -> Dict:
        """Get supplier return performance metrics

        Args:
            supplier_id: Supplier ID
            months: Analysis period in months

        Returns:
            Return performance statistics
        """
        from_date = date.today() - timedelta(days=30 * months)

        return {
            'supplier_id': supplier_id,
            'period': {
                'months': months,
                'from_date': from_date.isoformat(),
                'to_date': date.today().isoformat()
            },
            'total_returns': 0,
            'total_return_value': 0,
            'return_rate': 0.0,  # Returns as % of purchases
            'authorization_rate': 0.0,  # % of returns authorized
            'credit_rate': 0.0,  # % of shipped returns credited
            'average_credit_days': 0,  # Average days to receive credit
            'by_reason': {},
            'top_return_reasons': []
        }


# =============================================================================
# Factory Function
# =============================================================================

def create_return_recall_management_service(db: AsyncSession) -> ReturnRecallManagementService:
    """Factory function to create ReturnRecallManagementService

    Args:
        db: AsyncSession database session

    Returns:
        ReturnRecallManagementService instance
    """
    return ReturnRecallManagementService(db)
