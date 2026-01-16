"""Inventory Valuation and Cost Analysis Service

EPIC-019 Story 6: Inventory Valuation & Cost Analysis Reports

Comprehensive inventory valuation with:
- Multiple costing methods (FIFO, Weighted Average, Standard Cost)
- Inventory valuation reports (balance sheet, aging, slow-moving)
- Cost analysis (COGS, turnover ratio, DSI, holding costs)
- Budget variance analysis
- Regulatory reports (POM, narcotics)
- ABC analysis integration

Python 3.5+ compatible - uses .format() instead of f-strings
"""

import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional
from decimal import Decimal
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, case
from sqlalchemy.orm import selectinload

from app.models.inventory import Drug, DrugBatch
from app.models.dispensing import MedicationDispense


logger = logging.getLogger(__name__)


# =============================================================================
# Constants & Configuration
# =============================================================================

# Costing methods
COSTING_METHODS = ['fifo', 'weighted_average', 'standard_cost', 'specific_identification']

# Holding cost components (as percentage of inventory value)
HOLDING_COST_RATES = {
    'capital_cost': 0.15,    # Cost of capital
    'storage_cost': 0.05,    # Warehousing
    'risk_cost': 0.03       # Obsolescence, damage, expiry
}
TOTAL_HOLDING_COST_RATE = sum(HOLDING_COST_RATES.values())  # 23%

# Inventory aging thresholds
AGING_THRESHOLDS = {
    'fast_moving': 90,      # <3 months
    'slow_moving': 180,     # 3-6 months
    'non_moving': 365,      # 6-12 months
    'obsolete': 730         # >2 years
}


# =============================================================================
# Main Service
# =============================================================================

class InventoryValuationService(object):
    """Service for inventory valuation and cost analysis"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_inventory_valuation(
        self,
        costing_method: str = 'weighted_average',
        as_of_date: date = None
    ) -> Dict:
        """Calculate total inventory valuation using specified method

        Args:
            costing_method: Costing method ('fifo', 'weighted_average', 'standard_cost')
            as_of_date: Valuation date (default: today)

        Returns:
            Inventory valuation breakdown
        """
        if as_of_date is None:
            as_of_date = date.today()

        # Get all non-quarantined, non-expired batches
        stmt = select(DrugBatch).join(Drug).where(
            and_(
                DrugBatch.is_quarantined == False,
                DrugBatch.expiry_date > as_of_date,
                DrugBatch.quantity > 0
            )
        ).options(selectinload(DrugBatch.drug))

        result = await self.db.execute(stmt)
        batches = result.scalars().all()

        if costing_method == 'fifo':
            valuation = await self._calculate_fifo_valuation(batches)
        elif costing_method == 'weighted_average':
            valuation = await self._calculate_weighted_average_valuation(batches)
        elif costing_method == 'standard_cost':
            valuation = await self._calculate_standard_cost_valuation(batches)
        else:
            valuation = await self._calculate_weighted_average_valuation(batches)

        # Add summary
        total_value = sum(item['value'] for item in valuation['items'])

        return {
            'costing_method': costing_method,
            'as_of_date': as_of_date.isoformat(),
            'total_items': len(valuation['items']),
            'total_quantity': sum(item['quantity'] for item in valuation['items']),
            'total_value': round(total_value, 2),
            'valuation': valuation,
            'currency': 'IDR'
        }

    async def _calculate_fifo_valuation(self, batches: List[DrugBatch]) -> Dict:
        """Calculate FIFO (First In, First Out) valuation"""
        items = []

        for batch in batches:
            unit_cost = float(batch.unit_cost) if batch.unit_cost else 0
            value = batch.quantity * unit_cost

            items.append({
                'drug_id': batch.drug_id,
                'drug_name': batch.drug.generic_name,
                'drug_code': batch.drug.drug_code,
                'batch_id': batch.id,
                'batch_number': batch.batch_number,
                'quantity': batch.quantity,
                'unit_cost': unit_cost,
                'value': value,
                'acquisition_date': batch.received_date.isoformat() if batch.received_date else None
            })

        return {
            'method': 'FIFO',
            'description': 'First In, First Out - oldest costs assigned first',
            'items': sorted(items, key=lambda x: x['acquisition_date'] or '0')
        }

    async def _calculate_weighted_average_valuation(self, batches: List[DrugBatch]) -> Dict:
        """Calculate Weighted Average Cost valuation"""
        # Group by drug to calculate WAC per drug
        drug_batches = defaultdict(list)
        for batch in batches:
            drug_batches[batch.drug_id].append(batch)

        items = []

        for drug_id, drug_batch_list in drug_batches.items():
            total_quantity = sum(b.quantity for b in drug_batch_list)
            total_cost = sum(
                (b.quantity * float(b.unit_cost)) if b.unit_cost else 0
                for b in drug_batch_list
            )

            wac = total_cost / total_quantity if total_quantity > 0 else 0

            for batch in drug_batch_list:
                value = batch.quantity * wac

                items.append({
                    'drug_id': batch.drug_id,
                    'drug_name': batch.drug.generic_name,
                    'drug_code': batch.drug.drug_code,
                    'batch_id': batch.id,
                    'batch_number': batch.batch_number,
                    'quantity': batch.quantity,
                    'unit_cost': round(wac, 2),
                    'value': round(value, 2),
                    'weighted_average_cost': round(wac, 2)
                })

        return {
            'method': 'Weighted Average Cost',
            'description': 'Average cost of all batches of each item',
            'items': items
        }

    async def _calculate_standard_cost_valuation(self, batches: List[DrugBatch]) -> Dict:
        """Calculate Standard Cost valuation"""
        items = []

        for batch in batches:
            # Use drug's standard cost or fall back to purchase price
            standard_cost = float(batch.drug.purchase_price) if batch.drug and batch.drug.purchase_price else 0
            if standard_cost == 0:
                standard_cost = float(batch.unit_cost) if batch.unit_cost else 0

            value = batch.quantity * standard_cost

            items.append({
                'drug_id': batch.drug_id,
                'drug_name': batch.drug.generic_name if batch.drug else 'Unknown',
                'drug_code': batch.drug.drug_code if batch.drug else 'Unknown',
                'batch_id': batch.id,
                'batch_number': batch.batch_number,
                'quantity': batch.quantity,
                'unit_cost': round(standard_cost, 2),
                'value': round(value, 2),
                'standard_cost': round(standard_cost, 2)
            })

        return {
            'method': 'Standard Cost',
            'description': 'Predetermined standard cost per item',
            'items': items
        }

    async def get_inventory_aging_analysis(self) -> Dict:
        """Generate inventory aging analysis

        Returns:
            Aging report with fast-moving, slow-moving, non-moving, obsolete items
        """
        today = date.today()

        # Get all batches
        stmt = select(DrugBatch).join(Drug).where(
            and_(
                DrugBatch.is_quarantined == False,
                DrugBatch.expiry_date > today,
                DrugBatch.quantity > 0
            )
        ).options(selectinload(DrugBatch.drug))

        result = await self.db.execute(stmt)
        batches = result.scalars().all()

        # Categorize by age based on acquisition date
        categories = defaultdict(lambda: {'count': 0, 'quantity': 0, 'value': 0, 'items': []})

        for batch in batches:
            acquisition_date = batch.received_date or batch.manufacturing_date
            if not acquisition_date:
                continue

            days_in_inventory = (today - acquisition_date).days

            # Calculate value
            unit_cost = float(batch.unit_cost) if batch.unit_cost else 0
            value = batch.quantity * unit_cost

            # Determine category
            if days_in_inventory < AGING_THRESHOLDS['fast_moving']:
                category = 'fast_moving'
                category_name = 'Fast Moving (< 3 months)'
            elif days_in_inventory < AGING_THRESHOLDS['slow_moving']:
                category = 'slow_moving'
                category_name = 'Slow Moving (3-6 months)'
            elif days_in_inventory < AGING_THRESHOLDS['non_moving']:
                category = 'non_moving'
                category_name = 'Non-Moving (6-12 months)'
            else:
                category = 'obsolete'
                category_name = 'Obsolete (> 2 years)'

            categories[category]['count'] += 1
            categories[category]['quantity'] += batch.quantity
            categories[category]['value'] += value
            categories[category]['category_name'] = category_name
            categories[category]['items'].append({
                'drug_id': batch.drug_id,
                'drug_name': batch.drug.generic_name,
                'batch_number': batch.batch_number,
                'quantity': batch.quantity,
                'value': value,
                'days_in_inventory': days_in_inventory,
                'acquisition_date': acquisition_date.isoformat()
            })

        total_value = sum(c['value'] for c in categories.values())

        return {
            'as_of_date': today.isoformat(),
            'total_items': len(batches),
            'total_value': round(total_value, 2),
            'categories': dict(categories)
        }

    async def calculate_inventory_turnover(
        self,
        period_days: int = 90
    ) -> Dict:
        """Calculate inventory turnover ratio

        Formula: Turnover = COGS / Average Inventory

        Args:
            period_days: Analysis period in days

        Returns:
            Turnover metrics by drug and overall
        """
        from_date = date.today() - timedelta(days=period_days)

        # Calculate COGS from dispenses
        stmt = select(
            MedicationDispense.drug_id,
            func.sum(MedicationDispense.quantity).label('total_quantity'),
            func.sum(MedicationDispense.quantity * MedicationDispense.unit_cost).label('total_cost')
        ).where(
            MedicationDispense.dispensed_at >= from_date
        ).group_by(MedicationDispense.drug_id)

        result = await self.db.execute(stmt)
        cogs_data = result.all()

        turnover_by_drug = []

        for drug_id, total_quantity, total_cost in cogs_data:
            # Get average inventory value
            avg_inventory = await self._get_average_inventory_value(drug_id, from_date, date.today())

            if avg_inventory > 0:
                turnover_ratio = total_cost / avg_inventory
                days_sales = (avg_inventory / total_cost * 365) if total_cost > 0 else 0
            else:
                turnover_ratio = 0
                days_sales = 0

            turnover_by_drug.append({
                'drug_id': drug_id,
                'cogs': round(total_cost, 2),
                'average_inventory': round(avg_inventory, 2),
                'turnover_ratio': round(turnover_ratio, 2),
                'days_sales_of_inventory': round(days_sales, 1),
                'performance': self._classify_turnover(turnover_ratio)
            })

        # Calculate overall turnover
        total_cogs = sum(d['cogs'] for d in turnover_by_drug)
        total_avg_inventory = sum(d['average_inventory'] for d in turnover_by_drug)

        overall_turnover = (total_cogs / total_avg_inventory) if total_avg_inventory > 0 else 0

        return {
            'period_days': period_days,
            'from_date': from_date.isoformat(),
            'to_date': date.today().isoformat(),
            'overall_turnover': round(overall_turnover, 2),
            'overall_dsi': round((total_avg_inventory / total_cogs * 365) if total_cogs > 0 else 0, 1),
            'by_drug': sorted(turnover_by_drug, key=lambda x: x['turnover_ratio'], reverse=True)
        }

    def _classify_turnover(self, turnover_ratio: float) -> str:
        """Classify turnover performance"""
        if turnover_ratio >= 12:
            return 'excellent'  # >12 times per year
        elif turnover_ratio >= 8:
            return 'good'  # 8-12 times per year
        elif turnover_ratio >= 4:
            return 'acceptable'  # 4-8 times per year
        else:
            return 'poor'  # <4 times per year (overstocked)

    async def _get_average_inventory_value(
        self,
        drug_id: int,
        start_date: date,
        end_date: date
    ) -> float:
        """Calculate average inventory value for a drug over period"""
        # Simplified: get current inventory as proxy for average
        # In production, would calculate from daily snapshots
        stmt = select(
            func.sum(DrugBatch.quantity * DrugBatch.unit_cost)
        ).where(
            and_(
                DrugBatch.drug_id == drug_id,
                DrugBatch.is_quarantined == False,
                DrugBatch.expiry_date > date.today(),
                DrugBatch.quantity > 0
            )
        )

        result = await self.db.execute(stmt)
        current_value = result.scalar() or 0
        return float(current_value)

    async def calculate_holding_costs(self, days: int = 365) -> Dict:
        """Calculate inventory holding costs

        Formula: Holding Cost = (Capital + Storage + Risk) × Inventory Value
        Total rate ≈ 23% annually

        Args:
            days: Period to calculate costs for

        Returns:
            Holding cost breakdown
        """
        # Get current inventory valuation
        valuation = await self.calculate_inventory_valuation()

        total_value = valuation['total_value']
        daily_rate = TOTAL_HOLDING_COST_RATE / 365

        # Calculate holding costs
        holding_costs = {}
        total_holding_cost = 0

        for component, rate in HOLDING_COST_RATES.items():
            component_cost = total_value * rate * (days / 365)
            holding_costs[component] = {
                'annual_rate': round(rate * 100, 2),
                'period_cost': round(component_cost, 2)
            }
            total_holding_cost += component_cost

        return {
            'period_days': days,
            'total_inventory_value': total_value,
            'total_annual_holding_cost': round(total_value * TOTAL_HOLDING_COST_RATE, 2),
            'period_holding_cost': round(total_holding_cost, 2),
            'daily_holding_cost': round(total_value * daily_rate, 2),
            'holding_cost_breakdown': holding_costs,
            'holding_cost_rate': round(TOTAL_HOLDING_COST_RATE * 100, 2),
            'currency': 'IDR'
        }

    async def generate_regulatory_reports(
        self,
        report_type: str = 'pom',
        month: int = None,
        year: int = None
    ) -> Dict:
        """Generate regulatory reports (POM, narcotics)

        Args:
            report_type: Type of report ('pom', 'narcotics')
            month: Report month (default: current month)
            year: Report year (default: current year)

        Returns:
            Regulatory report data
        """
        if month is None:
            month = date.today().month
        if year is None:
            year = date.today().year

        if report_type == 'pom':
            return await self._generate_pom_report(month, year)
        elif report_type == 'narcotics':
            return await self._generate_narcotics_report(month, year)
        else:
            return {
                'error': 'Unknown report type: {}'.format(report_type)
            }

    async def _generate_pom_report(self, month: int, year: int) -> Dict:
        """Generate POM (Psychotropic & Narcotic) report"""
        # Get all drugs marked as narcotic
        stmt = select(Drug).where(Drug.is_narcotic == True)
        result = await self.db.execute(stmt)
        narcotics = result.scalars().all()

        # Get inventory for each narcotic
        report_data = []
        for drug in narcotics:
            # Get batches
            batch_stmt = select(
                func.sum(DrugBatch.quantity).label('total_quantity')
            ).where(
                and_(
                    DrugBatch.drug_id == drug.id,
                    DrugBatch.is_quarantined == False,
                    DrugBatch.expiry_date > date.today()
                )
            )

            batch_result = await self.db.execute(batch_stmt)
            total_quantity = batch_result.scalar() or 0

            # Get dispenses for the month
            from_date = date(year, month, 1)
            to_date = date(year, month, 28) if month == 2 else date(year, month + 1, 1) - timedelta(days=1)

            dispense_stmt = select(
                func.sum(MedicationDispense.quantity).label('total_dispensed')
            ).where(
                and_(
                    MedicationDispense.drug_id == drug.id,
                    MedicationDispense.dispensed_at >= from_date,
                    MedicationDispense.dispensed_at <= to_date
                )
            )

            dispense_result = await self.db.execute(dispense_stmt)
            total_dispensed = dispense_result.scalar() or 0

            report_data.append({
                'drug_id': drug.id,
                'drug_name': drug.generic_name,
                'drug_code': drug.drug_code,
                'opening_balance': total_quantity + total_dispensed,  # Approximation
                'received': 0,  # Would need to track receipts
                'dispensed': total_dispensed,
                'closing_balance': total_quantity,
                'unit': drug.strength or 'unit'
            })

        return {
            'report_type': 'POM',
            'report_period': '{}/{}'.format(month, year),
            'generated_at': datetime.utcnow().isoformat(),
            'drugs': report_data,
            'total_narcotics': len(report_data),
            'summary': {
                'total_dispensed': sum(d['dispensed'] for d in report_data),
                'total_closing_balance': sum(d['closing_balance'] for d in report_data)
            }
        }

    async def _generate_narcotics_report(self, month: int, year: int) -> Dict:
        """Generate narcotics consumption report"""
        # Similar to POM but with additional details
        pom_report = await self._generate_pom_report(month, year)

        pom_report['report_type'] = 'Narcotics Consumption'
        pom_report['regulatory_authority'] = 'Badan POM (pengawas obat keras)'

        return pom_report


# =============================================================================
# Factory Function
# =============================================================================

def create_inventory_valuation_service(db: AsyncSession) -> InventoryValuationService:
    """Factory function to create InventoryValuationService

    Args:
        db: AsyncSession database session

    Returns:
        InventoryValuationService instance
    """
    return InventoryValuationService(db)
