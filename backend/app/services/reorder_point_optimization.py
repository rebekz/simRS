"""Reorder Point Optimization Service

EPIC-019 Story 3: Automated Reorder Point Optimization

Advanced inventory optimization with:
- Reorder Point (ROP) calculation based on demand variability
- Safety Stock calculation with service levels
- Economic Order Quantity (EOQ) optimization
- ABC analysis for inventory classification
- Dynamic reorder point adjustments
- Automatic reorder triggers
- Order consolidation and optimization

Python 3.5+ compatible - uses .format() instead of f-strings
"""

import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, case
from sqlalchemy.orm import selectinload

from app.models.inventory import Drug, DrugBatch, Supplier
from app.services.demand_forecasting import DemandForecastingService


logger = logging.getLogger(__name__)


# =============================================================================
# Constants & Configuration
# =============================================================================

# Service level factors (Z-values)
SERVICE_LEVELS = {
    0.90: 1.28,   # 90% service level
    0.95: 1.645,  # 95% service level
    0.99: 2.33,   # 99% service level
    0.999: 3.09   # 99.9% service level
}

# ABC classification thresholds
ABC_THRESHOLDS = {
    'A': {'value_max': 0.80, 'volume_min': 0},   # High value, low volume
    'B': {'value_max': 0.95, 'volume_min': 0.20}, # Medium value, medium volume
    'C': {'value_max': 1.0, 'volume_min': 0.80}   # Low value, high volume
}

# Review frequencies (in days)
ABC_REVIEW_FREQUENCY = {
    'A': 7,    # Weekly
    'B': 30,   # Monthly
    'C': 90    # Quarterly
}


# =============================================================================
# Main Service
# =============================================================================

class ReorderPointOptimizationService(object):
    """Service for automated reorder point optimization"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_reorder_point(
        self,
        drug_id: int,
        service_level: float = 0.95,
        lead_time_days: int = None,
        review_period_days: int = 30
    ) -> Dict:
        """Calculate optimal reorder point for a drug

        Args:
            drug_id: Drug ID
            service_level: Target service level (0.90, 0.95, 0.99, 0.999)
            lead_time_days: Supplier lead time (default from drug record)
            review_period_days: Review period in days

        Returns:
            Dict with ROP, safety stock, EOQ, and metrics
        """
        # Get drug info
        stmt = select(Drug).where(Drug.id == drug_id)
        result = await self.db.execute(stmt)
        drug = result.scalar_one_or_none()

        if not drug:
            return {
                'error': 'Drug not found'
            }

        # Use provided lead time or default from drug
        if lead_time_days is None:
            lead_time_days = drug.lead_time_days or 7

        # Get forecasting service
        forecast_service = DemandForecastingService(self.db)

        # Get historical consumption
        historical_data = await forecast_service.get_historical_consumption(
            drug_id=drug_id,
            days=90  # Use 90 days for calculation
        )

        if not historical_data:
            return {
                'error': 'Insufficient historical data'
            }

        # Calculate Average Daily Usage (ADU)
        quantities = [q for _, q in historical_data]
        adu = sum(quantities) / len(quantities)

        # Calculate demand standard deviation
        variance = sum((q - adu) ** 2 for q in quantities) / len(quantities)
        std_dev_demand = variance ** 0.5

        # Get service level Z-factor
        z_factor = SERVICE_LEVELS.get(service_level, 1.645)

        # Calculate Safety Stock
        # SS = Z × σd × √(Lead Time)
        safety_stock = z_factor * std_dev_demand * (lead_time_days ** 0.5)

        # Calculate Reorder Point
        # ROP = (ADU × Lead Time) + Safety Stock
        reorder_point = (adu * lead_time_days) + safety_stock

        # Calculate Economic Order Quantity (EOQ)
        # EOQ = √((2 × D × S) / H)
        annual_demand = adu * 365
        ordering_cost = Decimal('50000')  # 50,000 IDR per order
        holding_cost_rate = Decimal('0.25')  # 25% annual holding cost
        unit_cost = drug.purchase_price or Decimal('1000')
        holding_cost = float(unit_cost * holding_cost_rate)

        eoq = ((2 * annual_demand * float(ordering_cost)) / holding_cost) ** 0.5

        # Calculate Days Stock on Hand (DSO)
        current_stock = await self._get_current_stock(drug_id)
        dso = current_stock / adu if adu > 0 else 0

        # Determine ABC classification
        abc_class = await self._calculate_abc_classification(drug, annual_demand)

        return {
            'drug_id': drug_id,
            'drug_name': drug.generic_name,
            'drug_code': drug.drug_code,
            'parameters': {
                'average_daily_usage': round(adu, 2),
                'demand_std_dev': round(std_dev_demand, 2),
                'lead_time_days': lead_time_days,
                'service_level': service_level,
                'review_period_days': review_period_days
            },
            'reorder_point': {
                'calculated_rop': round(reorder_point),
                'safety_stock': round(safety_stock),
                'demand_during_lead_time': round(adu * lead_time_days)
            },
            'economic_order_quantity': {
                'eoq': round(eoq),
                'annual_demand': round(annual_demand),
                'ordering_cost': float(ordering_cost),
                'holding_cost_per_unit': round(holding_cost, 2)
            },
            'current_status': {
                'current_stock': current_stock,
                'days_stock_on_hand': round(dso, 1),
                'should_reorder': current_stock <= reorder_point,
                'suggested_order_quantity': round(max(0, eoq - (current_stock - reorder_point))),
                'abc_classification': abc_class
            },
            'recommendations': self._generate_recommendations(
                current_stock, reorder_point, safety_stock, adu, abc_class
            )
        }

    async def batch_calculate_reorder_points(
        self,
        drug_ids: List[int],
        service_level: float = 0.95
    ) -> List[Dict]:
        """Calculate reorder points for multiple drugs

        Args:
            drug_ids: List of drug IDs
            service_level: Target service level

        Returns:
            List of reorder point calculations
        """
        results = []

        for drug_id in drug_ids:
            try:
                result = await self.calculate_reorder_point(
                    drug_id=drug_id,
                    service_level=service_level
                )
                results.append(result)
            except Exception as e:
                logger.error("Error calculating ROP for drug {}: {}".format(drug_id, str(e)))
                results.append({
                    'drug_id': drug_id,
                    'error': str(e)
                })

        return results

    async def get_reorder_alerts(
        self,
        location_id: int = None
    ) -> List[Dict]:
        """Get drugs that need reordering

        Args:
            location_id: Filter by location (None = all locations)

        Returns:
            List of drugs at or below reorder point
        """
        # Get all active drugs
        stmt = select(Drug).where(Drug.is_active == True)
        result = await self.db.execute(stmt)
        drugs = result.scalars().all()

        alerts = []

        for drug in drugs:
            # Calculate ROP
            rop_result = await self.calculate_reorder_point(drug.id)

            if 'error' in rop_result:
                continue

            current_status = rop_result['current_status']

            # Check if should reorder
            if current_status['should_reorder']:
                alerts.append({
                    'drug_id': drug.id,
                    'drug_name': drug.generic_name,
                    'drug_code': drug.drug_code,
                    'current_stock': current_status['current_stock'],
                    'reorder_point': rop_result['reorder_point']['calculated_rop'],
                    'safety_stock': rop_result['reorder_point']['safety_stock'],
                    'suggested_order_quantity': current_status['suggested_order_quantity'],
                    'days_stock_on_hand': current_status['days_stock_on_hand'],
                    'is_critical': self._is_critical_drug(drug),
                    'abc_classification': current_status['abc_classification'],
                    'priority': self._calculate_reorder_priority(rop_result)
                })

        # Sort by priority
        alerts.sort(key=lambda x: x['priority'], reverse=True)

        return alerts

    async def optimize_order_consolidation(
        self,
        supplier_id: int = None
    ) -> Dict:
        """Optimize and consolidate purchase orders

        Args:
            supplier_id: Filter by supplier (None = all suppliers)

        Returns:
            Optimized order groups by supplier
        """
        # Get drugs that need reordering
        alerts = await self.get_reorder_alerts()

        # Group by supplier
        supplier_groups = defaultdict(list)

        for alert in alerts:
            # Get supplier for this drug
            stmt = select(Supplier).join(
                DrugBatch, Supplier.id == DrugBatch.supplier_id
            ).where(
                DrugBatch.drug_id == alert['drug_id']
            ).distinct()

            if supplier_id:
                stmt = stmt.where(Supplier.id == supplier_id)

            result = await self.db.execute(stmt)
            suppliers = result.scalars().all()

            # Use primary supplier or first available
            if suppliers:
                primary_supplier = suppliers[0]
                supplier_groups[primary_supplier.id].append({
                    **alert,
                    'supplier_name': primary_supplier.supplier_name
                })

        # Calculate order summaries
        order_groups = []

        for supplier_id, items in supplier_groups.items():
            # Get supplier info
            stmt = select(Supplier).where(Supplier.id == supplier_id)
            result = await self.db.execute(stmt)
            supplier = result.scalar_one_or_none()

            total_quantity = sum(item['suggested_order_quantity'] for item in items)
            total_value = sum(
                item['suggested_order_quantity'] * 1000  # Placeholder for unit cost
                for item in items
            )

            order_groups.append({
                'supplier_id': supplier_id,
                'supplier_name': supplier.supplier_name if supplier else 'Unknown',
                'items': items,
                'summary': {
                    'total_items': len(items),
                    'total_quantity': total_quantity,
                    'estimated_value': total_value,
                    'critical_items': sum(1 for item in items if item['is_critical']),
                    'high_priority_items': sum(1 for item in items if item['priority'] >= 80)
                }
            })

        return {
            'order_groups': sorted(order_groups, key=lambda x: x['summary']['estimated_value'], reverse=True),
            'total_suppliers': len(order_groups),
            'total_items': sum(g['summary']['total_items'] for g in order_groups)
        }

    async def adjust_reorder_points_dynamically(
        self,
        variation_threshold: float = 0.20
    ) -> List[Dict]:
        """Auto-adjust reorder points based on consumption changes

        Args:
            variation_threshold: Threshold for adjustment (20%)

        Returns:
            List of adjustments made
        """
        # Get all active drugs
        stmt = select(Drug).where(Drug.is_active == True)
        result = await self.db.execute(stmt)
        drugs = result.scalars().all()

        adjustments = []

        for drug in drugs:
            # Get current and historical consumption
            forecast_service = DemandForecastingService(self.db)

            # Recent consumption (last 30 days)
            recent_data = await forecast_service.get_historical_consumption(
                drug.id, days=30
            )
            recent_adu = sum(q for _, q in recent_data) / len(recent_data) if recent_data else 0

            # Previous period consumption (30-60 days ago)
            previous_data = await forecast_service.get_historical_consumption(
                drug.id, days=30, end_date=date.today() - timedelta(days=30)
            )
            previous_adu = sum(q for _, q in previous_data) / len(previous_data) if previous_data else 0

            # Calculate variation
            if previous_adu > 0:
                variation = (recent_adu - previous_adu) / previous_adu

                # Check if variation exceeds threshold
                if abs(variation) > variation_threshold:
                    # Calculate new ROP
                    new_rop_result = await self.calculate_reorder_point(drug.id)

                    if 'error' not in new_rop_result:
                        old_rop = drug.reorder_point
                        new_rop = new_rop_result['reorder_point']['calculated_rop']

                        # Only adjust if significant change
                        if abs(new_rop - old_rop) > 5:
                            adjustments.append({
                                'drug_id': drug.id,
                                'drug_name': drug.generic_name,
                                'old_reorder_point': old_rop,
                                'new_reorder_point': int(new_rop),
                                'variation_percent': round(variation * 100, 1),
                                'reason': 'Consumption pattern change',
                                'recommended_action': 'update' if variation > 0 else 'reduce'
                            })

        return adjustments

    # =========================================================================
    # Helper Methods
    # =========================================================================

    async def _get_current_stock(self, drug_id: int) -> int:
        """Get current stock level"""
        try:
            stmt = select(
                func.sum(DrugBatch.quantity)
            ).where(
                and_(
                    DrugBatch.drug_id == drug_id,
                    DrugBatch.is_quarantined == False,
                    DrugBatch.expiry_date > date.today()
                )
            )

            result = await self.db.execute(stmt)
            stock = result.scalar() or 0
            return int(stock)

        except Exception as e:
            logger.error("Error getting current stock: {}".format(str(e)))
            return 0

    async def _calculate_abc_classification(self, drug: Drug, annual_demand: float) -> str:
        """Calculate ABC classification based on value and volume

        Args:
            drug: Drug model
            annual_demand: Annual demand quantity

        Returns:
            ABC class (A, B, or C)
        """
        # Calculate annual value
        unit_cost = drug.purchase_price or Decimal('1000')
        annual_value = float(unit_cost * annual_demand)

        # This is simplified - real ABC would rank all drugs
        # For now, use drug cost as proxy
        if drug.is_narcotic or (drug.purchase_price and drug.purchase_price > 500000):
            return 'A'  # High value
        elif drug.purchase_price and drug.purchase_price > 100000:
            return 'B'  # Medium value
        else:
            return 'C'  # Low value

    def _is_critical_drug(self, drug: Drug) -> bool:
        """Determine if drug is critical"""
        return drug.is_narcotic or drug.is_antibiotic

    def _calculate_reorder_priority(self, rop_result: Dict) -> int:
        """Calculate reorder priority score (0-100)

        Args:
            rop_result: Reorder point calculation result

        Returns:
            Priority score
        """
        current_status = rop_result['current_status']
        dso = current_status['days_stock_on_hand']
        is_critical = self._is_critical_drug_type(rop_result)

        # Base priority
        priority = 50

        # Adjust based on days of stock
        if dso <= 3:
            priority += 40  # Critical - less than 3 days
        elif dso <= 7:
            priority += 30  # Urgent - less than 1 week
        elif dso <= 14:
            priority += 20  # Important - less than 2 weeks

        # Adjust for critical drugs
        if is_critical:
            priority += 20

        # Adjust for ABC classification
        abc_class = current_status['abc_classification']
        if abc_class == 'A':
            priority += 10
        elif abc_class == 'B':
            priority += 5

        return min(100, priority)

    def _is_critical_drug_type(self, rop_result: Dict) -> bool:
        """Check if drug is critical type"""
        # This would check from drug properties
        return False  # Placeholder

    def _generate_recommendations(
        self,
        current_stock: int,
        reorder_point: float,
        safety_stock: float,
        adu: float,
        abc_class: str
    ) -> List[str]:
        """Generate recommendations based on analysis

        Args:
            current_stock: Current stock level
            reorder_point: Calculated reorder point
            safety_stock: Safety stock level
            adu: Average daily usage
            abc_class: ABC classification

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Stock level recommendations
        if current_stock < safety_stock:
            recommendations.append(
                "CRITICAL: Stock below safety stock. Immediate order required."
            )
        elif current_stock < reorder_point:
            recommendations.append(
                "WARNING: Stock at or below reorder point. Order recommended."
            )
        elif current_stock < reorder_point * 1.2:
            recommendations.append(
                "INFO: Stock approaching reorder point. Plan order within {} days.".format(
                    int((current_stock - reorder_point) / adu)
                )
            )

        # ABC-specific recommendations
        if abc_class == 'A':
            recommendations.append(
                "High-value item: Tight control recommended. Review weekly."
            )
        elif abc_class == 'C':
            recommendations.append(
                "Low-value item: Consider ordering in larger batches to reduce ordering costs."
            )

        # General recommendations
        if adu == 0:
            recommendations.append(
                "No recent consumption: Review if item should be discontinued."
            )

        return recommendations


# =============================================================================
# Factory Function
# =============================================================================

def create_reorder_point_service(db: AsyncSession) -> ReorderPointOptimizationService:
    """Factory function to create ReorderPointOptimizationService

    Args:
        db: AsyncSession database session

    Returns:
        ReorderPointOptimizationService instance
    """
    return ReorderPointOptimizationService(db)
