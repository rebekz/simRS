"""Expiry Date Management Service

EPIC-019 Story 4: Expiry Date Management & Automated Discounts

Advanced expiry tracking with:
- FEFO (First Expire, First Out) dispensing logic
- Multi-threshold expiry alerts (6m, 3m, 2m, 1m, expired)
- Automated discount schedules
- Expiry forecasting reports
- Supplier return management
- Cost avoidance tracking

Python 3.5+ compatible - uses .format() instead of f-strings
"""

import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple
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

# Expiry alert thresholds (in days)
EXPIRY_THRESHOLDS = {
    'critical': 30,      # 1 month - critical alert
    'urgent': 60,        # 2 months - initiate discounting
    'warning': 90,       # 3 months - priority dispensing
    'notice': 180,       # 6 months - plan for rotation
}

# Discount schedule based on remaining shelf life (in days)
DISCOUNT_SCHEDULE = {
    (30, 60): 0.50,      # 1-2 months: 50% discount
    (60, 90): 0.30,      # 2-3 months: 30% discount
    (90, 120): 0.20,     # 3-4 months: 20% discount
    (120, 180): 0.10,    # 4-6 months: 10% discount
}

# Expiry rate targets
EXPIRY_RATE_TARGETS = {
    'high_cost': 0.02,   # <2% for high-cost items
    'standard': 0.05,    # <5% overall
}


# =============================================================================
# Main Service
# =============================================================================

class ExpiryManagementService(object):
    """Service for expiry date management and automated discounts"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_batches_fefo(
        self,
        drug_id: int,
        quantity_needed: int
    ) -> List[Dict]:
        """Get batches using FEFO (First Expire, First Out) logic

        Args:
            drug_id: Drug ID
            quantity_needed: Total quantity needed

        Returns:
            List of batches sorted by expiry date with quantities to dispense
        """
        # Get non-quarantined, non-expired batches sorted by expiry
        stmt = select(DrugBatch).where(
            and_(
                DrugBatch.drug_id == drug_id,
                DrugBatch.is_quarantined == False,
                DrugBatch.expiry_date > date.today(),
                DrugBatch.quantity > 0
            )
        ).order_by(DrugBatch.expiry_date.asc())

        result = await self.db.execute(stmt)
        batches = result.scalars().all()

        allocated = []
        remaining_needed = quantity_needed

        for batch in batches:
            if remaining_needed <= 0:
                break

            # Allocate from this batch
            allocate_qty = min(batch.quantity, remaining_needed)

            allocated.append({
                'batch_id': batch.id,
                'batch_number': batch.batch_number,
                'expiry_date': batch.expiry_date.isoformat(),
                'quantity': allocate_qty,
                'remaining_quantity': batch.quantity - allocate_qty,
                'days_to_expiry': (batch.expiry_date - date.today()).days,
                'unit_cost': float(batch.unit_cost) if batch.unit_cost else 0
            })

            remaining_needed -= allocate_qty

        return allocated

    async def get_expiry_alerts(
        self,
        threshold: Optional[str] = None,
        drug_id: Optional[int] = None
    ) -> List[Dict]:
        """Get expiry alerts based on thresholds

        Args:
            threshold: Alert threshold ('critical', 'urgent', 'warning', 'notice')
            drug_id: Filter by drug ID

        Returns:
            List of batches approaching expiry
        """
        today = date.today()

        # Build query
        stmt = select(DrugBatch).join(Drug).where(
            and_(
                DrugBatch.is_quarantined == False,
                DrugBatch.expiry_date > today
            )
        )

        # Apply drug filter
        if drug_id:
            stmt = stmt.where(DrugBatch.drug_id == drug_id)

        # Apply threshold filter
        if threshold:
            days_threshold = EXPIRY_THRESHOLDS.get(threshold, 180)
            threshold_date = today + timedelta(days=days_threshold)
            stmt = stmt.where(DrugBatch.expiry_date <= threshold_date)
        else:
            # Get all batches expiring within 6 months
            threshold_date = today + timedelta(days=180)
            stmt = stmt.where(DrugBatch.expiry_date <= threshold_date)

        stmt = stmt.options(selectinload(DrugBatch.drug))

        result = await self.db.execute(stmt)
        batches = result.scalars().all()

        # Build alerts
        alerts = []
        for batch in batches:
            days_to_expiry = (batch.expiry_date - today).days

            # Determine alert level
            if days_to_expiry <= EXPIRY_THRESHOLDS['critical']:
                alert_level = 'critical'
                action = 'CRITICAL: Near expiry - dispense immediately or return to supplier'
            elif days_to_expiry <= EXPIRY_THRESHOLDS['urgent']:
                alert_level = 'urgent'
                action = 'Initiate discounting and priority dispensing'
            elif days_to_expiry <= EXPIRY_THRESHOLDS['warning']:
                alert_level = 'warning'
                action = 'Priority dispensing - avoid stockpiling'
            elif days_to_expiry <= EXPIRY_THRESHOLDS['notice']:
                alert_level = 'notice'
                action = 'Plan for rotation - monitor closely'
            else:
                alert_level = 'info'
                action = 'Monitor expiry dates'

            # Calculate discount
            discount = self._calculate_discount(days_to_expiry)

            alerts.append({
                'batch_id': batch.id,
                'drug_id': batch.drug_id,
                'drug_name': batch.drug.generic_name,
                'drug_code': batch.drug.drug_code,
                'batch_number': batch.batch_number,
                'expiry_date': batch.expiry_date.isoformat(),
                'days_to_expiry': days_to_expiry,
                'quantity': batch.quantity,
                'unit_cost': float(batch.unit_cost) if batch.unit_cost else 0,
                'total_value': float(batch.quantity * batch.unit_cost) if batch.unit_cost else 0,
                'alert_level': alert_level,
                'recommended_action': action,
                'discount_percentage': discount,
                'discounted_value': float(batch.quantity * batch.unit_cost * (1 - discount)) if batch.unit_cost else 0
            })

        # Sort by days to expiry
        alerts.sort(key=lambda x: x['days_to_expiry'])

        return alerts

    async def get_expiry_forecast(
        self,
        months_ahead: int = 12
    ) -> Dict:
        """Generate expiry forecast report

        Args:
            months_ahead: Number of months to forecast

        Returns:
            Expiry forecast grouped by month
        """
        today = date.today()
        end_date = today + timedelta(days=months_ahead * 30)

        # Get all batches expiring in forecast period
        stmt = select(DrugBatch).join(Drug).where(
            and_(
                DrugBatch.is_quarantined == False,
                DrugBatch.expiry_date > today,
                DrugBatch.expiry_date <= end_date
            )
        ).options(selectinload(DrugBatch.drug))

        result = await self.db.execute(stmt)
        batches = result.scalars().all()

        # Group by month
        forecast = defaultdict(lambda: {
            'count': 0,
            'total_quantity': 0,
            'total_value': 0,
            'batches': []
        })

        for batch in batches:
            # Determine month key
            month_key = batch.expiry_date.strftime('%Y-%m')
            month_name = batch.expiry_date.strftime('%B %Y')

            total_value = float(batch.quantity * batch.unit_cost) if batch.unit_cost else 0

            forecast[month_key]['count'] += 1
            forecast[month_key]['total_quantity'] += batch.quantity
            forecast[month_key]['total_value'] += total_value
            forecast[month_key]['month_name'] = month_name
            forecast[month_key]['batches'].append({
                'drug_name': batch.drug.generic_name,
                'batch_number': batch.batch_number,
                'expiry_date': batch.expiry_date.isoformat(),
                'quantity': batch.quantity,
                'value': total_value
            })

        # Calculate totals
        total_value = sum(f['total_value'] for f in forecast.values())

        return {
            'forecast_period_months': months_ahead,
            'total_expiring_value': total_value,
            'months': dict(forecast)
        }

    async def get_expiry_report(
        self,
        report_type: str = 'near_expiry'
    ) -> Dict:
        """Generate various expiry reports

        Args:
            report_type: Type of report ('near_expiry', 'expired', 'supplier_analysis')

        Returns:
            Report data based on type
        """
        if report_type == 'near_expiry':
            return await self._near_expiry_report()
        elif report_type == 'expired':
            return await self._expired_report()
        elif report_type == 'supplier_analysis':
            return await self._supplier_analysis_report()
        else:
            return {
                'error': 'Unknown report type: {}'.format(report_type)
            }

    async def _near_expiry_report(self) -> Dict:
        """Generate near-expiry items report"""
        today = date.today()
        threshold_date = today + timedelta(days=180)  # 6 months

        stmt = select(DrugBatch).join(Drug).where(
            and_(
                DrugBatch.is_quarantined == False,
                DrugBatch.expiry_date > today,
                DrugBatch.expiry_date <= threshold_date
            )
        ).options(selectinload(DrugBatch.drug))

        result = await self.db.execute(stmt)
        batches = result.scalars().all()

        # Group by urgency
        by_urgency = defaultdict(lambda: {'count': 0, 'quantity': 0, 'value': 0})

        for batch in batches:
            days_to_expiry = (batch.expiry_date - today).days
            value = float(batch.quantity * batch.unit_cost) if batch.unit_cost else 0

            if days_to_expiry <= 30:
                urgency = 'critical_1_month'
            elif days_to_expiry <= 60:
                urgency = 'urgent_2_months'
            elif days_to_expiry <= 90:
                urgency = 'warning_3_months'
            else:
                urgency = 'notice_4_6_months'

            by_urgency[urgency]['count'] += 1
            by_urgency[urgency]['quantity'] += batch.quantity
            by_urgency[urgency]['value'] += value

        return {
            'report_type': 'near_expiry',
            'generated_at': datetime.utcnow().isoformat(),
            'summary': {
                'total_batches': len(batches),
                'total_quantity': sum(b.quantity for b in batches),
                'total_value': sum(float(b.quantity * b.unit_cost) if b.unit_cost else 0 for b in batches)
            },
            'by_urgency': dict(by_urgency)
        }

    async def _expired_report(self) -> Dict:
        """Generate expired items report"""
        stmt = select(DrugBatch).join(Drug).where(
            DrugBatch.expiry_date <= date.today()
        ).options(selectinload(DrugBatch.drug))

        result = await self.db.execute(stmt)
        batches = result.scalars().all()

        # Calculate write-off value
        write_off_value = sum(
            float(b.quantity * b.unit_cost) if b.unit_cost else 0
            for b in batches
        )

        return {
            'report_type': 'expired',
            'generated_at': datetime.utcnow().isoformat(),
            'total_expired_batches': len(batches),
            'total_write_off_value': write_off_value,
            'batches': [
                {
                    'drug_name': b.drug.generic_name,
                    'batch_number': b.batch_number,
                    'expiry_date': b.expiry_date.isoformat(),
                    'quantity': b.quantity,
                    'value': float(b.quantity * b.unit_cost) if b.unit_cost else 0,
                    'quarantined': b.is_quarantined
                }
                for b in batches
            ]
        }

    async def _supplier_analysis_report(self) -> Dict:
        """Generate supplier-wise expiry analysis"""
        stmt = select(DrugBatch, Supplier, Drug).join(
            Drug, DrugBatch.drug_id == Drug.id
        ).join(
            Supplier, DrugBatch.supplier_id == Supplier.id
        ).where(
            DrugBatch.expiry_date <= date.today() + timedelta(days=180)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        # Group by supplier
        by_supplier = defaultdict(lambda: {
            'total_batches': 0,
            'expired_batches': 0,
            'total_value': 0,
            'expired_value': 0
        })

        for batch, supplier, drug in rows:
            value = float(batch.quantity * batch.unit_cost) if batch.unit_cost else 0
            is_expired = batch.expiry_date <= date.today()

            by_supplier[supplier.id]['supplier_name'] = supplier.supplier_name
            by_supplier[supplier.id]['total_batches'] += 1
            by_supplier[supplier.id]['total_value'] += value

            if is_expired:
                by_supplier[supplier.id]['expired_batches'] += 1
                by_supplier[supplier.id]['expired_value'] += value

        # Calculate expiry rates
        for supplier_id, data in by_supplier.items():
            if data['total_batches'] > 0:
                data['expiry_rate'] = (data['expired_batches'] / data['total_batches']) * 100
            else:
                data['expiry_rate'] = 0

        return {
            'report_type': 'supplier_analysis',
            'generated_at': datetime.utcnow().isoformat(),
            'suppliers': dict(by_supplier)
        }

    async def apply_discounts(self, batch_ids: List[int]) -> Dict:
        """Apply automatic discounts to near-expiry batches

        Args:
            batch_ids: List of batch IDs to apply discounts

        Returns:
            Summary of applied discounts
        """
        today = date.today()
        results = []

        for batch_id in batch_ids:
            # Get batch
            stmt = select(DrugBatch).where(DrugBatch.id == batch_id)
            result = await self.db.execute(stmt)
            batch = result.scalar_one_or_none()

            if not batch:
                results.append({
                    'batch_id': batch_id,
                    'error': 'Batch not found'
                })
                continue

            # Calculate discount
            days_to_expiry = (batch.expiry_date - today).days
            discount = self._calculate_discount(days_to_expiry)

            if discount > 0:
                original_price = float(batch.unit_cost) if batch.unit_cost else 0
                discounted_price = original_price * (1 - discount)

                results.append({
                    'batch_id': batch_id,
                    'drug_name': batch.drug.generic_name if batch.drug else 'Unknown',
                    'batch_number': batch.batch_number,
                    'days_to_expiry': days_to_expiry,
                    'original_price': original_price,
                    'discount_percentage': discount * 100,
                    'discounted_price': discounted_price,
                    'savings': original_price - discounted_price
                })
            else:
                results.append({
                    'batch_id': batch_id,
                    'drug_name': batch.drug.generic_name if batch.drug else 'Unknown',
                    'message': 'No discount applicable (too far from expiry)'
                })

        return {
            'processed': len(results),
            'discounts_applied': sum(1 for r in results if 'savings' in r),
            'total_savings': sum(r.get('savings', 0) for r in results),
            'results': results
        }

    async def calculate_cost_avoidance(
        self,
        days: int = 90
    ) -> Dict:
        """Calculate cost avoidance through discounts vs write-offs

        Args:
            days: Number of days to analyze

        Returns:
            Cost avoidance metrics
        """
        # Get batches that expired or were discounted
        from_date = date.today() - timedelta(days=days)

        # This would query discount and write-off transactions
        # For now, return placeholder

        return {
            'period_days': days,
            'from_date': from_date.isoformat(),
            'to_date': date.today().isoformat(),
            'total_discounted_quantity': 0,
            'total_written_off_quantity': 0,
            'cost_avoidance': 0,
            'roi_percentage': 0,
            'message': 'Cost avoidance tracking requires discount transaction logging'
        }

    def _calculate_discount(self, days_to_expiry: int) -> float:
        """Calculate discount percentage based on days to expiry

        Args:
            days_to_expiry: Days until expiry

        Returns:
            Discount percentage (0.0 to 1.0)
        """
        for (min_days, max_days), discount in DISCOUNT_SCHEDULE.items():
            if min_days <= days_to_expiry < max_days:
                return discount

        return 0.0

    async def generate_return_requests(
        self,
        supplier_id: int = None,
        days_to_expiry: int = 60
    ) -> List[Dict]:
        """Generate return requests for near-expiry items

        Args:
            supplier_id: Filter by supplier
            days_to_expiry: Maximum days to expiry for returns

        Returns:
            List of items eligible for return
        """
        threshold_date = date.today() + timedelta(days=days_to_expiry)

        stmt = select(DrugBatch, Drug, Supplier).join(
            Drug, DrugBatch.drug_id == Drug.id
        ).join(
            Supplier, DrugBatch.supplier_id == Supplier.id
        ).where(
            and_(
                DrugBatch.is_quarantined == False,
                DrugBatch.expiry_date > date.today(),
                DrugBatch.expiry_date <= threshold_date
            )
        )

        if supplier_id:
            stmt = stmt.where(DrugBatch.supplier_id == supplier_id)

        result = await self.db.execute(stmt)
        rows = result.all()

        returns = []
        for batch, drug, supplier in rows:
            returns.append({
                'batch_id': batch.id,
                'drug_id': drug.id,
                'drug_name': drug.generic_name,
                'drug_code': drug.drug_code,
                'batch_number': batch.batch_number,
                'expiry_date': batch.expiry_date.isoformat(),
                'days_to_expiry': (batch.expiry_date - date.today()).days,
                'quantity': batch.quantity,
                'unit_cost': float(batch.unit_cost) if batch.unit_cost else 0,
                'total_value': float(batch.quantity * batch.unit_cost) if batch.unit_cost else 0,
                'supplier_id': supplier.id,
                'supplier_name': supplier.supplier_name,
                'return_eligible': self._check_return_eligibility(supplier, batch)
            })

        return returns

    def _check_return_eligibility(self, supplier: Supplier, batch: DrugBatch) -> bool:
        """Check if batch is eligible for return to supplier

        Args:
            supplier: Supplier model
            batch: DrugBatch model

        Returns:
            True if eligible for return
        """
        # Check if supplier allows returns (this would be based on supplier policy)
        # For now, assume all suppliers accept returns >30 days before expiry
        days_to_expiry = (batch.expiry_date - date.today()).days
        return days_to_expiry >= 30


# =============================================================================
# Factory Function
# =============================================================================

def create_expiry_management_service(db: AsyncSession) -> ExpiryManagementService:
    """Factory function to create ExpiryManagementService

    Args:
        db: AsyncSession database session

    Returns:
        ExpiryManagementService instance
    """
    return ExpiryManagementService(db)
