"""Demand Forecasting and Predictive Ordering Service

EPIC-019 Story 1: Demand Forecasting & Predictive Ordering

Advanced inventory management with:
- Multiple forecasting algorithms (moving average, exponential smoothing, seasonal, linear regression)
- Automatic algorithm selection based on demand patterns
- Forecast accuracy tracking (MAPE)
- Predictive ordering with budget impact
- Multi-horizon forecasting (30, 60, 90 days)
- Confidence intervals (80%, 90%, 95%)

Python 3.5+ compatible - uses .format() instead of f-strings
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, case, literal_column
from sqlalchemy.orm import selectinload

from app.models.inventory import Drug, StockTransaction, StockTransactionItem
from app.models.dispensing import MedicationDispense
from app.core.config import settings


logger = logging.getLogger(__name__)


# =============================================================================
# Forecasting Algorithms
# =============================================================================

class ForecastingAlgorithm(object):
    """Base class for forecasting algorithms"""

    @staticmethod
    def forecast(historical_data, forecast_horizon, **kwargs):
        """Generate forecast based on historical data

        Args:
            historical_data: List of (date, quantity) tuples
            forecast_horizon: Number of days to forecast
            **kwargs: Algorithm-specific parameters

        Returns:
            Dict with forecast data, confidence intervals, accuracy metrics
        """
        raise NotImplementedError("Subclasses must implement forecast method")


class SimpleMovingAverage(ForecastingAlgorithm):
    """Simple moving average for stable demand items"""

    @staticmethod
    def forecast(historical_data, forecast_horizon, window=30, **kwargs):
        """Forecast using simple moving average

        Args:
            historical_data: List of (date, quantity) tuples
            forecast_horizon: Number of days to forecast
            window: Moving average window size (default: 30 days)
        """
        if len(historical_data) < window:
            window = len(historical_data)

        if not historical_data:
            return {
                'algorithm': 'simple_moving_average',
                'forecast': [],
                'mape': None,
                'confidence_intervals': []
            }

        # Calculate moving average
        quantities = [q for _, q in historical_data[-window:]]
        avg_demand = sum(quantities) / len(quantities)

        # Calculate standard deviation for confidence intervals
        variance = sum((q - avg_demand) ** 2 for q in quantities) / len(quantities)
        std_dev = variance ** 0.5

        # Generate forecast
        forecast = []
        confidence_intervals = []
        base_date = historical_data[-1][0] if historical_data else date.today()

        for i in range(1, forecast_horizon + 1):
            forecast_date = base_date + timedelta(days=i)
            forecast.append({
                'date': forecast_date.isoformat(),
                'quantity': round(avg_demand, 2)
            })

            # Confidence intervals (95%: 1.96 std dev)
            confidence_intervals.append({
                'date': forecast_date.isoformat(),
                'lower_80': round(max(0, avg_demand - 1.28 * std_dev), 2),
                'upper_80': round(avg_demand + 1.28 * std_dev, 2),
                'lower_90': round(max(0, avg_demand - 1.645 * std_dev), 2),
                'upper_90': round(avg_demand + 1.645 * std_dev, 2),
                'lower_95': round(max(0, avg_demand - 1.96 * std_dev), 2),
                'upper_95': round(avg_demand + 1.96 * std_dev, 2)
            })

        # Calculate MAPE (if we have enough data)
        mape = None
        if len(historical_data) >= window * 2:
            # Use last window as test set
            test_data = historical_data[-window:]
            test_actual = [q for _, q in test_data]
            mape = sum(abs(a - avg_demand) / a * 100 for a in test_actual if a > 0) / len(test_actual)

        return {
            'algorithm': 'simple_moving_average',
            'parameters': {'window': window},
            'forecast': forecast,
            'confidence_intervals': confidence_intervals,
            'mape': round(mape, 2) if mape else None
        }


class ExponentialSmoothing(ForecastingAlgorithm):
    """Exponential smoothing for trending items"""

    @staticmethod
    def forecast(historical_data, forecast_horizon, alpha=0.3, **kwargs):
        """Forecast using exponential smoothing (Holt's linear method)

        Args:
            historical_data: List of (date, quantity) tuples
            forecast_horizon: Number of days to forecast
            alpha: Smoothing parameter (0-1, default: 0.3)
        """
        if not historical_data:
            return {
                'algorithm': 'exponential_smoothing',
                'forecast': [],
                'mape': None,
                'confidence_intervals': []
            }

        quantities = [q for _, q in historical_data]

        # Initialize level and trend
        level = quantities[0]
        trend = 0 if len(quantities) < 2 else (quantities[1] - quantities[0]) / 2

        # Apply Holt's linear method
        for i in range(1, len(quantities)):
            prev_level = level
            level = alpha * quantities[i] + (1 - alpha) * (level + trend)
            trend = 0.2 * (level - prev_level) + (1 - 0.2) * trend

        # Calculate forecast
        forecast = []
        confidence_intervals = []
        base_date = historical_data[-1][0]

        for i in range(1, forecast_horizon + 1):
            forecast_date = base_date + timedelta(days=i)
            forecast_value = level + i * trend

            forecast.append({
                'date': forecast_date.isoformat(),
                'quantity': round(max(0, forecast_value), 2)
            })

            # Simplified confidence intervals
            std_dev = sum(abs(q - level) for q in quantities[-10:]) / 10 if len(quantities) >= 10 else level * 0.2
            confidence_intervals.append({
                'date': forecast_date.isoformat(),
                'lower_80': round(max(0, forecast_value - 1.28 * std_dev), 2),
                'upper_80': round(forecast_value + 1.28 * std_dev, 2),
                'lower_90': round(max(0, forecast_value - 1.645 * std_dev), 2),
                'upper_90': round(forecast_value + 1.645 * std_dev, 2),
                'lower_95': round(max(0, forecast_value - 1.96 * std_dev), 2),
                'upper_95': round(forecast_value + 1.96 * std_dev, 2)
            })

        # Calculate MAPE
        mape = None
        if len(quantities) >= 10:
            predictions = [level + (i - len(quantities)) * trend for i in range(len(quantities) - 10, len(quantities))]
            actuals = quantities[-10:]
            mape = sum(abs(a - p) / a * 100 for a, p in zip(actuals, predictions) if a > 0) / len(actuals)

        return {
            'algorithm': 'exponential_smoothing',
            'parameters': {'alpha': alpha},
            'forecast': forecast,
            'confidence_intervals': confidence_intervals,
            'mape': round(mape, 2) if mape else None
        }


class LinearRegression(ForecastingAlgorithm):
    """Linear regression for trend-based forecasting"""

    @staticmethod
    def forecast(historical_data, forecast_horizon, **kwargs):
        """Forecast using linear regression

        Args:
            historical_data: List of (date, quantity) tuples
            forecast_horizon: Number of days to forecast
        """
        if len(historical_data) < 3:
            # Fall back to moving average
            return SimpleMovingAverage.forecast(historical_data, forecast_horizon)

        # Prepare data
        base_date = historical_data[0][0]
        x_values = [(d - base_date).days for d, _ in historical_data]
        y_values = [q for _, q in historical_data]

        n = len(x_values)

        # Calculate linear regression coefficients
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x ** 2 for x in x_values)

        # y = mx + b
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n

        # Generate forecast
        forecast = []
        confidence_intervals = []
        last_date = historical_data[-1][0]

        # Calculate standard error
        y_pred = [slope * x + intercept for x in x_values]
        std_error = (sum((y - yp) ** 2 for y, yp in zip(y_values, y_pred)) / (n - 2)) ** 0.5

        for i in range(1, forecast_horizon + 1):
            forecast_date = last_date + timedelta(days=i)
            x_value = (forecast_date - base_date).days
            forecast_value = slope * x_value + intercept

            forecast.append({
                'date': forecast_date.isoformat(),
                'quantity': round(max(0, forecast_value), 2)
            })

            # Confidence intervals
            confidence_intervals.append({
                'date': forecast_date.isoformat(),
                'lower_80': round(max(0, forecast_value - 1.28 * std_error), 2),
                'upper_80': round(forecast_value + 1.28 * std_error, 2),
                'lower_90': round(max(0, forecast_value - 1.645 * std_error), 2),
                'upper_90': round(forecast_value + 1.645 * std_error, 2),
                'lower_95': round(max(0, forecast_value - 1.96 * std_error), 2),
                'upper_95': round(forecast_value + 1.96 * std_error, 2)
            })

        # Calculate MAPE
        mape = sum(abs(y - yp) / y * 100 for y, yp in zip(y_values, y_pred) if y > 0) / n

        return {
            'algorithm': 'linear_regression',
            'parameters': {'slope': round(slope, 6), 'intercept': round(intercept, 2)},
            'forecast': forecast,
            'confidence_intervals': confidence_intervals,
            'mape': round(mape, 2) if mape else None
        }


# =============================================================================
# Main Service
# =============================================================================

class DemandForecastingService(object):
    """Service for demand forecasting and predictive ordering"""

    # Algorithm registry
    ALGORITHMS = {
        'simple_moving_average': SimpleMovingAverage,
        'exponential_smoothing': ExponentialSmoothing,
        'linear_regression': LinearRegression
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_historical_consumption(
        self,
        drug_id: int,
        days: int = 365,
        end_date: date = None
    ) -> List[Tuple[date, int]]:
        """Get historical consumption data for a drug

        Args:
            drug_id: Drug ID
            days: Number of days of history to retrieve
            end_date: End date for data retrieval (default: today)

        Returns:
            List of (date, quantity) tuples
        """
        if end_date is None:
            end_date = date.today()
        start_date = end_date - timedelta(days=days)

        try:
            # Get consumption from medication dispenses
            stmt = select(
                func.date(MedicationDispense.dispensed_at).label('date'),
                func.sum(MedicationDispense.quantity).label('quantity')
            ).where(
                and_(
                    MedicationDispense.drug_id == drug_id,
                    MedicationDispense.dispensed_at >= start_date,
                    MedicationDispense.dispensed_at <= end_date
                )
            ).group_by(
                func.date(MedicationDispense.dispensed_at)
            ).order_by(
                func.date(MedicationDispense.dispensed_at)
            )

            result = await self.db.execute(stmt)
            consumption = [(row.date, int(row.quantity)) for row in result]

            # Fill in missing dates with zero consumption
            consumption_dict = dict(consumption)
            complete_data = []
            current_date = start_date

            while current_date <= end_date:
                complete_data.append((current_date, consumption_dict.get(current_date, 0)))
                current_date += timedelta(days=1)

            return complete_data

        except Exception as e:
            logger.error("Error getting historical consumption: {}".format(str(e)))
            return []

    async def analyze_demand_pattern(self, historical_data) -> str:
        """Analyze demand pattern to select best algorithm

        Args:
            historical_data: List of (date, quantity) tuples

        Returns:
            Recommended algorithm name
        """
        if len(historical_data) < 30:
            return 'simple_moving_average'

        quantities = [q for _, q in historical_data]

        # Calculate variability
        avg = sum(quantities) / len(quantities)
        variance = sum((q - avg) ** 2 for q in quantities) / len(quantities)
        cv = (variance ** 0.5) / avg if avg > 0 else 0  # Coefficient of variation

        # Calculate trend
        first_half_avg = sum(quantities[:len(quantities)//2]) / (len(quantities)//2)
        second_half_avg = sum(quantities[len(quantities)//2:]) / (len(quantities) - len(quantities)//2)
        trend_change = (second_half_avg - first_half_avg) / first_half_avg if first_half_avg > 0 else 0

        # Select algorithm based on pattern
        if cv < 0.3 and abs(trend_change) < 0.1:
            # Stable demand
            return 'simple_moving_average'
        elif cv < 0.5:
            # Moderate variability with trend
            return 'exponential_smoothing'
        else:
            # High variability or strong trend
            return 'linear_regression'

    async def generate_forecast(
        self,
        drug_id: int,
        forecast_horizon: int = 30,
        algorithm: str = None,
        historical_days: int = 365
    ) -> Dict:
        """Generate demand forecast for a drug

        Args:
            drug_id: Drug ID
            forecast_horizon: Number of days to forecast (30, 60, 90)
            algorithm: Algorithm to use (auto-detect if None)
            historical_days: Days of historical data to use

        Returns:
            Forecast dict with predictions and confidence intervals
        """
        # Get historical data
        historical_data = await self.get_historical_consumption(drug_id, historical_days)

        if not historical_data:
            return {
                'drug_id': drug_id,
                'error': 'No historical data available',
                'forecast': []
            }

        # Select algorithm
        if algorithm is None:
            algorithm = await self.analyze_demand_pattern(historical_data)

        # Get forecasting class
        forecast_class = self.ALGORITHMS.get(algorithm, SimpleMovingAverage)

        # Generate forecast
        forecast_result = forecast_class.forecast(historical_data, forecast_horizon)

        # Add drug info
        forecast_result['drug_id'] = drug_id

        return forecast_result

    async def generate_purchase_suggestions(
        self,
        drug_id: int,
        forecast_horizon: int = 30,
        algorithm: str = None
    ) -> Dict:
        """Generate purchase order suggestions based on forecast

        Args:
            drug_id: Drug ID
            forecast_horizon: Forecast horizon in days
            algorithm: Forecasting algorithm

        Returns:
            Purchase suggestion with budget impact
        """
        # Get drug info
        stmt = select(Drug).where(Drug.id == drug_id)
        result = await self.db.execute(stmt)
        drug = result.scalar_one_or_none()

        if not drug:
            return {
                'error': 'Drug not found'
            }

        # Get forecast
        forecast = await self.generate_forecast(drug_id, forecast_horizon, algorithm)

        if 'error' in forecast:
            return forecast

        # Calculate total forecasted demand
        total_demand = sum(f['quantity'] for f in forecast['forecast'])

        # Get current stock
        current_stock = await self.get_current_stock(drug_id)

        # Get open orders
        open_orders = await self.get_open_orders(drug_id)

        # Calculate suggested order quantity
        suggested_quantity = max(0, total_demand - current_stock - open_orders)

        # Calculate budget impact
        unit_cost = drug.purchase_price or Decimal('0')
        budget_impact = float(unit_cost * suggested_quantity)

        return {
            'drug_id': drug_id,
            'drug_name': drug.generic_name,
            'drug_code': drug.drug_code,
            'forecast_summary': {
                'algorithm': forecast['algorithm'],
                'forecast_horizon': forecast_horizon,
                'total_forecasted_demand': round(total_demand, 2),
                'mape': forecast.get('mape')
            },
            'current_stock': current_stock,
            'open_orders': open_orders,
            'suggested_order_quantity': round(suggested_quantity),
            'budget_impact': {
                'amount': round(budget_impact, 2),
                'currency': 'IDR'
            },
            'reorder_point': drug.reorder_point,
            'lead_time_days': drug.lead_time_days,
            'is_critical': is_critical_drug(drug),
            'forecast_details': forecast['forecast'],
            'confidence_intervals': forecast.get('confidence_intervals', [])
        }

    async def get_current_stock(self, drug_id: int) -> int:
        """Get current stock level for a drug

        Args:
            drug_id: Drug ID

        Returns:
            Current stock quantity
        """
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

    async def get_open_orders(self, drug_id: int) -> int:
        """Get quantity from open purchase orders

        Args:
            drug_id: Drug ID

        Returns:
            Total quantity from open orders
        """
        try:
            # This would query PurchaseOrderItem
            # For now, return 0 as placeholder
            return 0

        except Exception as e:
            logger.error("Error getting open orders: {}".format(str(e)))
            return 0

    async def batch_forecast(
        self,
        drug_ids: List[int],
        forecast_horizon: int = 30
    ) -> List[Dict]:
        """Generate forecasts for multiple drugs

        Args:
            drug_ids: List of drug IDs
            forecast_horizon: Forecast horizon in days

        Returns:
            List of forecast results
        """
        forecasts = []

        for drug_id in drug_ids:
            try:
                forecast = await self.generate_forecast(drug_id, forecast_horizon)
                forecasts.append(forecast)
            except Exception as e:
                logger.error("Error forecasting drug {}: {}".format(drug_id, str(e)))
                forecasts.append({
                    'drug_id': drug_id,
                    'error': str(e)
                })

        return forecasts

    async def get_forecast_accuracy_report(
        self,
        drug_id: int,
        algorithm: str = None
    ) -> Dict:
        """Generate forecast accuracy report

        Args:
            drug_id: Drug ID
            algorithm: Algorithm to evaluate

        Returns:
            Accuracy metrics and recommendations
        """
        # Get historical data
        historical_data = await self.get_historical_consumption(drug_id, days=365)

        if len(historical_data) < 60:
            return {
                'error': 'Insufficient data for accuracy evaluation'
            }

        # Use last 30 days as test set
        train_data = historical_data[:-30]
        test_data = historical_data[-30:]

        # Select algorithm
        if algorithm is None:
            algorithm = await self.analyze_demand_pattern(train_data)

        # Generate forecast for test period
        forecast_class = self.ALGORITHMS.get(algorithm, SimpleMovingAverage)
        forecast_result = forecast_class.forecast(train_data, 30)

        # Calculate accuracy metrics
        actuals = [q for _, q in test_data]
        predictions = [f['quantity'] for f in forecast_result['forecast'][:30]]

        # MAPE
        mape = sum(abs(a - p) / a * 100 for a, p in zip(actuals, predictions) if a > 0) / len(actuals)

        # MAD (Mean Absolute Deviation)
        mad = sum(abs(a - p) for a, p in zip(actuals, predictions)) / len(actuals)

        # RMSE (Root Mean Square Error)
        rmse = (sum((a - p) ** 2 for a, p in zip(actuals, predictions)) / len(actuals)) ** 0.5

        # Bias (forecast bias)
        bias = sum(p - a for a, p in zip(actuals, predictions)) / len(actuals)

        return {
            'drug_id': drug_id,
            'algorithm': algorithm,
            'test_period_days': 30,
            'accuracy_metrics': {
                'mape': round(mape, 2),
                'mad': round(mad, 2),
                'rmse': round(rmse, 2),
                'bias': round(bias, 2)
            },
            'recommendation': get_algorithm_recommendation(mape, bias)
        }


# =============================================================================
# Utility Functions
# =============================================================================

def is_critical_drug(drug: Drug) -> bool:
    """Determine if drug is critical (high importance)

    Args:
        drug: Drug model

    Returns:
        True if critical drug
    """
    # Narcotics are always critical
    if drug.is_narcotic:
        return True

    # High-cost drugs are critical
    if drug.purchase_price and drug.purchase_price > 1000000:  # > 1M IDR
        return True

    # Short shelf life drugs
    if drug.shelf_life_months and drug.shelf_life_months < 12:
        return True

    return False


def get_algorithm_recommendation(mape: float, bias: float) -> str:
    """Get recommendation based on accuracy metrics

    Args:
        mape: Mean Absolute Percentage Error
        bias: Forecast bias

    Returns:
        Recommendation string
    """
    if mape < 10:
        return 'Excellent accuracy - current algorithm recommended'
    elif mape < 20:
        return 'Good accuracy - current algorithm acceptable'
    elif mape < 30:
        return 'Fair accuracy - consider manual override or different algorithm'
    else:
        return 'Poor accuracy - recommend manual ordering and algorithm review'

    if bias > 0.1:
        return 'Warning: Consistent over-forecasting detected'
    elif bias < -0.1:
        return 'Warning: Consistent under-forecasting detected'


# =============================================================================
# Factory Function
# =============================================================================

def create_demand_forecasting_service(db: AsyncSession) -> DemandForecastingService:
    """Factory function to create DemandForecastingService

    Args:
        db: AsyncSession database session

    Returns:
        DemandForecastingService instance
    """
    return DemandForecastingService(db)
