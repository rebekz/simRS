# Epic 19: Advanced Inventory Management

**Epic ID**: EPIC-019
**Business Value**: Cost control, stock optimization, regulatory compliance
**Complexity**: High
**Estimated Duration**: 5-6 weeks

---

## Overview

Advanced Inventory Management builds upon the foundational pharmacy inventory system (Epic 6) to provide sophisticated inventory tracking, predictive analytics, and automated procurement workflows. This epic focuses on reducing costs, minimizing stockouts and overstock situations, ensuring regulatory compliance, and optimizing the entire supply chain from procurement to dispensing.

**Key Business Benefits**:
- Reduce inventory carrying costs by 15-20% through optimized ordering
- Minimize stockouts of critical medications (target <0.5%)
- Reduce expired medication waste by 25% through proactive expiry management
- Improve procurement efficiency through automated supplier performance tracking
- Ensure regulatory compliance with POM and narcotics tracking
- Enable multi-location inventory visibility across hospital facilities

---

## Dependencies

### Prerequisite Epics
- **Epic 1**: Foundation & Security Infrastructure (user authentication, audit logging)
- **Epic 2**: Patient Registration (patient data for dispense tracking)
- **Epic 3**: Medical Records (allergy tracking, medication lists)
- **Epic 6**: Pharmacy Management (basic inventory, drug master file, dispensing workflows)

### Related Epics
- **Epic 9**: Billing & Finance (inventory valuation, cost accounting)
- **Epic 10**: BPJS Integration (formulary coverage, pricing)
- **Epic 15**: System Configuration (master data management)

---

## Key User Stories

### 1. Demand Forecasting & Predictive Ordering
**As a pharmacy manager**, I want the system to predict future drug demand based on historical usage patterns so that I can maintain optimal stock levels and avoid both stockouts and overstock situations.

### 2. Multi-Location Inventory Tracking
**As a hospital administrator**, I want to view and manage inventory across all locations (main pharmacy, ward satellites, operating rooms, ICU) so that I can optimize stock distribution and transfers between locations.

### 3. Automated Reorder Point Optimization
**As a procurement officer**, I want the system to automatically calculate and adjust optimal reorder points based on consumption patterns, lead times, and seasonality so that I never run out of essential medications.

### 4. Expiry Date Management & Automated Discounts
**As a pharmacist**, I want to receive alerts for soon-to-expire medications and have the system automatically calculate discount schedules so that I can sell them before expiry and minimize waste.

### 5. Supplier Performance Tracking & Scoring
**As a procurement manager**, I want to track supplier delivery performance, quality metrics, and pricing consistency so that I can make informed decisions about supplier selection and negotiation.

### 6. Inventory Valuation & Cost Analysis Reports
**As a finance manager**, I want detailed inventory valuation reports using multiple costing methods (FIFO, weighted average, standard cost) so that I can accurately track inventory value and cost of goods sold.

### 7. Physical Inventory Count with Barcode Scanning
**As a inventory controller**, I want to conduct physical inventory counts efficiently using barcode scanners and mobile devices so that I can reconcile system stock with actual stock quickly and accurately.

### 8. Return & Recall Management
**As a pharmacy manager**, I want to manage product returns to suppliers and track manufacturer recalls efficiently so that I can maintain compliance and recover costs.

---

## Detailed Acceptance Criteria

### User Story 1: Demand Forecasting & Predictive Ordering

**Forecasting Models**:
- [ ] Implement multiple forecasting algorithms:
  - Simple moving average (for stable demand items)
  - Exponential smoothing (for trending items)
  - Seasonal decomposition (for seasonal patterns)
  - Linear regression (for trend-based forecasting)
- [ ] Automatic algorithm selection based on demand pattern analysis
- [ ] Forecast accuracy tracking (MAPE - Mean Absolute Percentage Error)
- [ ] Forecast horizon: 30, 60, 90 days
- [ ] Confidence intervals for predictions (80%, 90%, 95%)
- [ ] Manual forecast override capability

**Data Inputs for Forecasting**:
- [ ] Historical consumption data (minimum 12 months)
- [ ] Seasonal factors (month, quarter, year)
- [ ] Special events (holidays, outbreaks, campaigns)
- [ ] Patient admission trends
- [ ] Doctor prescribing patterns
- [ ] BPJS formulary changes
- [ ] Disease outbreaks (flu season, dengue, etc.)

**Predictive Ordering**:
- [ ] Generate purchase suggestions based on forecasted demand
- [ ] Consider current stock levels, open orders, and lead times
- [ ] Prioritize critical medications and high-cost items
- [ ] Budget impact projection for suggested orders
- [ ] Approval workflow for purchase suggestions
- [ ] Auto-generate purchase orders (optional, with approval)

**User Interface**:
- [ ] Forecast visualization dashboard
- [ ] Compare forecast vs actual consumption
- [ ] Forecast accuracy reports
- [ ] Override reason tracking
- [ ] Forecast parameter configuration (lead times, safety stock levels)

**Technical Notes**:
```
Forecasting Algorithms:
- Moving Average: MA(n) = (Sum of last n periods) / n
- Exponential Smoothing: F(t+1) = α × A(t) + (1-α) × F(t)
- Seasonal Decomposition: Y(t) = T(t) × S(t) × E(t)
- Safety Stock = Z × σd × √(Lead Time)

Parameters:
- α (smoothing factor): 0.1 to 0.9 (default 0.3)
- Z (service level): 1.65 for 95%, 2.33 for 99%
- Review period: Weekly, monthly, quarterly
```

---

### User Story 2: Multi-Location Inventory Tracking

**Location Management**:
- [ ] Define multiple inventory locations:
  - Main pharmacy store
  - Ward satellites (per ward/unit)
  - Operating room pharmacies
  - ICU pharmacies
  - Emergency department pharmacy
  - Outpatient pharmacy
  - Satellite clinics
- [ ] Location hierarchy (parent-child relationships)
- [ ] Location capacity limits
- [ ] Location types (bulk storage, picking area, ward stock)

**Real-Time Visibility**:
- [ ] View stock levels across all locations
- [ ] Drill-down from hospital-wide to location-level
- [ ] Color-coded stock status (green, yellow, red)
- [ ] Total hospital inventory position
- [ ] Inter-location transfers
- [ ] Transfer approval workflow
- [ ] Transfer history tracking

**Automated Replenishment**:
- [ ] Set par levels per location
- [ ] Automatic replenishment requests from main pharmacy
- [ ] Ward stock replenishment schedules
- [ ] Emergency transfer requests
- [ ] Priority-based allocation during shortages

**Stock Movement Tracking**:
- [ ] Complete audit trail of all stock movements
- [ ] Track: receipt, dispensing, transfer, adjustment, expiry, damage, loss
- [ ] Movement reason codes
- [ ] User attribution for all movements
- [ ] DateTime stamps for all transactions

**Reporting**:
- [ ] Inventory position by location
- [ ] Transfer volume reports
- [ ] Location utilization analysis
- [ ] Ward consumption patterns
- [ ] Stock velocity by location

**Technical Notes**:
```
Location Schema:
- location_id, parent_location_id, location_name, location_type
- capacity_limit, current_stock, par_level
- is_active, created_at, updated_at

Transfer Workflow:
1. Request created by requesting location
2. Auto-check availability in source location
3. Approval by source location manager
4. Picking and packing
5. Transfer confirmation by receiving location
6. System updates both locations' inventory

Data Structure:
- Each inventory item tracked by: item_id + batch_no + location_id
- Unique key for stock tracking
```

---

### User Story 3: Automated Reorder Point Optimization

**Reorder Point Calculation**:
- [ ] Calculate optimal reorder points based on:
  - Average daily usage (ADU)
  - Lead time variability
  - Demand variability
  - Service level targets
  - Review period
- [ ] Separate reorder points for each location
- [ ] ABC analysis-based ordering:
  - A items (high value, low volume): tight control
  - B items (medium value, medium volume): moderate control
  - C items (low value, high volume): loose control

**Dynamic Adjustments**:
- [ ] Auto-adjust reorder points based on:
  - Consumption pattern changes (>20% variation)
  - Seasonal adjustments
  - Lead time changes
  - Service level modifications
- [ ] Adjustment notification to pharmacy manager
- [ ] Adjustment history tracking
- [ ] Manual override capability

**Reorder Triggers**:
- [ ] Automatic reorder point monitoring
- [ ] Alert when stock reaches reorder point
- [ ] Generate purchase requisition automatically
- [ ] Expedited ordering for critical items
- [ ] Consolidate ordering to maximize bulk discounts
- [ ] Consider supplier minimum order quantities

**Order Optimization**:
- [ ] Economic Order Quantity (EOQ) calculation
- [ ] Consider:
  - Ordering costs
  - Holding costs
  - Stockout costs
  - Quantity discounts
  - Storage constraints
- [ ] Order consolidation across suppliers
- [ ] Group items by supplier for efficiency

**User Interface**:
- [ ] Reorder point configuration per item
- [ ] Service level settings (95%, 99%, 99.9%)
- [ ] Lead time configuration per supplier
- [ ] Safety stock level visualization
- [ ] Days stock on hand (DSO) calculation
- [ ] Reorder point analysis reports

**Technical Notes**:
```
Reorder Point (ROP) Formula:
ROP = (ADU × Average Lead Time) + Safety Stock

Safety Stock Formula:
Safety Stock = Z × σd × √(Average Lead Time)

Where:
- Z = Service level factor (1.65 for 95%, 2.33 for 99%)
- σd = Standard deviation of daily demand
- Lead Time = Time from order to receipt (in days)

Economic Order Quantity (EOQ):
EOQ = √((2 × D × S) / H)

Where:
- D = Annual demand
- S = Ordering cost per order
- H = Holding cost per unit per year

Service Level Targets:
- Critical medications: 99.9% (Z = 3.09)
- High-value items: 99% (Z = 2.33)
- Standard items: 95% (Z = 1.65)
- Low-cost items: 90% (Z = 1.28)

Review Frequency:
- A items: Weekly review
- B items: Monthly review
- C items: Quarterly review
```

---

### User Story 4: Expiry Date Management & Automated Discounts

**Expiry Tracking**:
- [ ] Track expiry dates by batch number
- [ ] FEFO (First Expire, First Out) dispensing logic
- [ ] Expiry alerts at multiple thresholds:
  - 6 months: Plan for rotation
  - 3 months: Priority dispensing
  - 2 months: Initiate discounting
  - 1 month: Critical alert
  - Expired: Block from dispensing
- [ ] Batch-level expiry management
- [ ] Quarantine expired items automatically
- [ ] Prevent dispensing expired medications

**Expiry Reports**:
- [ ] Expiry forecast report (by month, by quarter)
- [ ] Near-expiry items list (filterable by time range)
- [ ] Expired items report
- [ ] Expiry write-off reports
- [ ] Supplier-wise expiry analysis
- [ ] Department-wise expiry consumption

**Automated Discount Schedules**:
- [ ] Define discount rules based on remaining shelf life:
  - 6-8 months remaining: 10% discount
  - 4-6 months remaining: 20% discount
  - 2-4 months remaining: 30% discount
  - 1-2 months remaining: 50% discount
- [ ] Discount approval workflow
- [ ] Apply discounts automatically to sales
- [ ] Track discounted sales vs write-offs
- [ ] ROI analysis: discount vs waste
- [ ] Patient notification of discounted items (optional)

**Returns to Suppliers**:
- [ ] Generate return requests for near-expiry items
- [ ] Check supplier return policies
- [ ] Track return authorizations
- [ ] Monitor return credits
- [ ] Supplier return performance

**Expiry Prevention**:
- [ ] Purchase quantity optimization
- [ ] Avoid overstocking of slow-moving items
- [ ] Supplier negotiation for shorter expiry items
- [ ] Expiry-based supplier selection

**Technical Notes**:
```
Expiry Management Logic:

1. FEFO Algorithm:
   SELECT * FROM inventory_batches
   WHERE item_id = [item_id]
     AND expiry_date > CURRENT_DATE
     AND quantity > 0
   ORDER BY expiry_date ASC
   LIMIT 1

2. Days to Expiry Calculation:
   days_to_expiry = expiry_date - current_date

3. Discount Application:
   IF days_to_expiry <= 60 AND days_to_expiry > 30:
       discount = 0.30
   ELSE IF days_to_expiry <= 90 AND days_to_expiry > 60:
       discount = 0.20
   ELSE IF days_to_expiry <= 120 AND days_to_expiry > 90:
       discount = 0.10

4. Expiry Rate Calculation:
   expiry_rate = (expired_items / total_items) × 100
   Target: <2% for high-cost items, <5% overall

5. Cost Avoidance Calculation:
   avoided_cost = (discounted_quantity × discount_percentage)
                 - (expired_quantity × full_cost)
```

---

### User Story 5: Supplier Performance Tracking & Scoring

**Supplier Master Data**:
- [ ] Comprehensive supplier profile:
  - Supplier name, code, contact details
  - Product categories supplied
  - Payment terms and conditions
  - Minimum order quantities
  - Lead time commitments
  - Quality certifications
  - BPJS/E-Katalog registration status
- [ ] Multiple contact persons per supplier
- [ ] Bank account details
- [ ] Tax information (NPWP)

**Performance Metrics**:
- [ ] Track delivery performance:
  - On-time delivery rate
  - Complete delivery rate (full order fulfillment)
  - Average lead time vs committed lead time
  - Emergency order response time
- [ ] Track quality metrics:
  - Damaged goods rate
  - Wrong item rate
  - Near-expiry delivery rate
  - Returns and rejection rate
  - Documentation completeness
- [ ] Track pricing:
  - Price consistency
  - Price competitive analysis
  - Volume discount achievement
  - Payment term compliance

**Supplier Scoring System**:
- [ ] Calculate composite score (0-100):
  - Delivery performance: 40% weight
  - Quality performance: 30% weight
  - Pricing competitiveness: 20% weight
  - Service & support: 10% weight
- [ ] Score categories:
  - Excellent: 90-100
  - Good: 75-89
  - Acceptable: 60-74
  - Poor: 40-59
  - Unacceptable: <40
- [ ] Trend analysis (improving vs declining)
- [ ] Periodic score recalculations (monthly)
- [ ] Score history tracking

**E-Katalog Integration**:
- [ ] Real-time E-Katalog price comparison
- [ ] Display E-Katalog prices vs negotiated prices
- [ ] Price variance alerts
- [ ] E-Katalog product availability
- [ ] Government procurement price references
- [ ] Update prices from E-Katalog automatically

**Supplier Management**:
- [ ] Preferred supplier designation
- [ ] Supplier performance reports
- [ ] Supplier performance reviews (quarterly)
- [ ] Supplier approval workflow
- [ ] Supplier suspension/deactivation
- [ ] Alternate supplier identification

**Technical Notes**:
```
Supplier Scoring Algorithm:

Score = (Delivery_Score × 0.40) + (Quality_Score × 0.30)
      + (Price_Score × 0.20) + (Service_Score × 0.10)

Delivery_Score Components:
- On-time Delivery Rate: 60%
- Complete Fulfillment Rate: 30%
- Lead Time Adherence: 10%

Quality_Score Components:
- Damage Rate: 40%
- Wrong Item Rate: 30%
- Expiry Rate: 20%
- Documentation: 10%

Price_Score Components:
- Price vs E-Katalog: 60%
- Price Stability: 20%
- Volume Discounts: 20%

Scoring Examples:
Delivery_Score = (0.95 × 0.60) + (0.90 × 0.30) + (0.85 × 0.10) = 92.5

Data Collection:
- Auto-collect from purchase orders and goods receipts
- Manual entry for qualitative metrics
- Periodic surveys for service evaluation
```

---

### User Story 6: Inventory Valuation & Cost Analysis Reports

**Valuation Methods**:
- [ ] Support multiple costing methods:
  - FIFO (First In, First Out)
  - Weighted Average Cost
  - Standard Cost
  - Specific Identification (for high-value items)
- [ ] Configure costing method per item class
- [ ] Switch between costing methods (with proper cut-off)
- [ ] Maintain cost layers for FIFO

**Inventory Valuation Reports**:
- [ ] Balance sheet inventory valuation:
  - Raw materials
  - Work-in-progress (compound medications)
  - Finished goods
  - Total inventory value
- [ ] Inventory aging analysis
- [ ] Slow-moving inventory report
  - No movement in 6+ months
  - No movement in 12+ months
  - Obsolete items
- [ ] Fast-moving inventory report (ABC analysis)
- [ ] Gross margin analysis by item

**Cost Analysis**:
- [ ] Cost of Goods Sold (COGS) reports
- [ ] Inventory turnover ratio
  - By item
  - By category
  - By department
- [ ] Days Sales of Inventory (DSI)
- [ ] Holding cost analysis
- [ ] Stockout cost analysis
- [ ] Carrying cost calculation

**Budget & Variance Analysis**:
- [ ] Purchase budget tracking
- [ ] Actual vs budgeted spend
- [ ] Price variance analysis
- [ ] Quantity variance analysis
- [ ] Usage variance analysis
- [ ] Period-over-period comparisons

**Regulatory Reports**:
- [ ] POM (Psychotropic & Narcotic) stock reports
- [ ] Narcotics consumption tracking
- [ ] Regulated substance reconciliation
- [ ] Monthly POM reporting to authorities
- [ ] Audit trail for regulated items

**Technical Notes**:
```
Valuation Formulas:

1. FIFO Cost:
   Track each batch with its purchase cost
   COGS = Sum of oldest batches consumed
   Ending Inventory = Sum of remaining batches

2. Weighted Average Cost:
   WAC = (Total Cost of Goods Available) / (Total Units Available)
   Updated after each purchase

3. Inventory Turnover:
   Turnover = COGS / Average Inventory
   Average Inventory = (Beginning + Ending) / 2

4. Days Sales of Inventory:
   DSI = (Average Inventory / COGS) × 365

5. Holding Cost:
   Holding Cost = (Capital Cost + Storage Cost + Risk Cost)
   Capital Cost = 15% (cost of capital)
   Storage Cost = 5% (warehousing)
   Risk Cost = 3% (obsolescence, damage, expiry)
   Total Holding Cost ≈ 23% of inventory value

Data Structure:
- inventory_layer: layer_id, item_id, batch_no, quantity, unit_cost, acquisition_date
- Cost calculation triggers: purchase receipt, issue, adjustment, valuation
```

---

### User Story 7: Physical Inventory Count with Barcode Scanning

**Count Planning**:
- [ ] Schedule physical counts:
  - Full inventory counts (annual)
  - Cycle counts (rotating by ABC category)
  - Spot counts (random verification)
  - Category-specific counts
- [ ] Define count frequency:
  - A items: Monthly
  - B items: Quarterly
  - C items: Semi-annually
- [ ] Assign count teams and locations
- [ ] Generate count sheets (by location, category)
- [ ] Freeze inventory during count (optional)

**Mobile Counting with Barcode Scanning**:
- [ ] Mobile-optimized count interface
- [ ] Barcode/QR code scanning:
  - Scan item barcode
  - Scan batch barcode
  - Scan location barcode
- [ ] Enter quantity
- [ ] Photo capture (optional for verification)
- [ ] Offline counting capability
- [ ] Auto-sync when online
- [ ] Duplicate scan prevention

**Count Variance Management**:
- [ ] Compare system stock vs counted stock
- [ ] Calculate variance quantity and value
- [ ] Variance threshold alerts:
  - Quantity variance >5%: Investigate
  - Value variance >IDR 1,000,000: Investigate
  - Regulated items: Any variance requires investigation
- [ ] Variance approval workflow
- [ ] System stock adjustment after approval
- [ ] Variance analysis and reporting

**Reconciliation**:
- [ ] Approval workflow for stock adjustments
- [ ] Multi-level approval based on variance amount
- [ ] Document variance reasons
- [ ] Adjust system inventory
- [ ] Generate adjustment journal entries
- [ ] Notify finance department

**Count Reports**:
- [ ] Count completion status
- [ ] Variance summary report
- [ ] Count accuracy by location
- [ ] Count accuracy by item
- [ ] Trend analysis (improving vs declining accuracy)
- [ ] Staff performance metrics

**Technical Notes**:
```
Count Workflow:
1. Planning → Create count event, assign teams
2. Preparation → Freeze system stock (optional), generate count sheets
3. Counting → Scan items, enter quantities, sync data
4. Verification → Compare system vs counted, calculate variances
5. Investigation → Review variances, document reasons
6. Approval → Approve adjustments (multi-level based on amount)
7. Reconciliation → Adjust system stock, generate journal entries
8. Reporting → Analyze accuracy, identify trends

Variance Calculation:
variance_qty = counted_qty - system_qty
variance_value = variance_qty × unit_cost
variance_pct = (variance_qty / system_qty) × 100

Approval Thresholds:
- <IDR 100,000: Pharmacy manager approval
- IDR 100,000 - 1,000,000: Pharmacy manager + Finance manager
- >IDR 1,000,000: Director approval
- Regulated items: Compliance officer + Pharmacy manager

Count Accuracy Metrics:
accuracy_rate = (correct_counts / total_counts) × 100
Target: >98% for A items, >95% overall
```

---

### User Story 8: Return & Recall Management

**Product Returns to Suppliers**:
- [ ] Initiate return requests:
  - Damaged goods
  - Wrong items delivered
  - Near-expiry items (per supplier agreement)
  - Overstock items
  - Quality issues
- [ ] Generate Return Material Authorization (RMA)
- [ ] Check supplier return policies
- [ ] Calculate return value
- [ ] Track return shipping
- [ ] Monitor credit notes
- [ ] Reconcile returns with supplier credits

**Manufacturer Recalls**:
- [ ] Receive recall notifications:
  - Manual entry
  - API integration with regulatory bodies
  - Email parsing
- [ ] Identify affected inventory:
  - By brand
  - By batch number
  - By expiry date range
  - By manufacturer
- [ ] Quarantine recalled items immediately
- [ ] Notify all locations holding recalled items
- [ ] Generate recall report
- [ ] Track recall completion
- [ ] Return recalled items to supplier
- [ ] Document recall actions for regulatory compliance

**Return Workflow**:
- [ ] Return request creation
- [ ] Reason code selection
- [ ] Attach supporting documentation
- [ ] Approval workflow
- [ ] Supplier notification
- [ ] Shipping documentation
- [ ] Credit tracking
- [ ] Close return when credited

**Reporting**:
- [ ] Returns by supplier
- [ ] Returns by reason
- [ ] Return value analysis
- [ ] Credit note tracking
- [ ] Recall compliance reports
- [ ] Supplier return performance

**Technical Notes**:
```
Return Process Flow:
1. Identify returnable items
2. Create return request with reason codes
3. Attach documentation (photos, quality reports)
4. Obtain supplier authorization (RMA)
5. Ship items with tracking
6. Receive credit note
7. Reconcile credit with accounts

Reason Codes:
- DAMAGED: Damaged in transit or storage
- WRONG_ITEM: Incorrect item delivered
- EXPIRY: Near-expiry or expired
- QUALITY: Quality issue, failed QC
- OVERSTOCK: Excess inventory
- RECALL: Manufacturer recall

Recall Management:
- Hot List: Maintain real-time list of active recalls
- Auto-Quarantine: Block recalled items from dispensing
- Notification: Alert all relevant departments
- Reporting: Generate regulatory reports (BPJS, Kemenkes)

Data Model:
- return_request: request_id, supplier_id, item_id, batch_no, quantity, reason,
                 status, created_by, approved_by, credit_note_id
- recall_notice: notice_id, manufacturer_id, product_name, batch_range,
                affected_quantity, recall_date, recall_reason, status
```

---

## Cross-Cutting Concerns

### Security & Compliance
- [ ] Role-based access control (RBAC)
- [ ] Audit logging for all inventory transactions
- [ ] POM and narcotics tracking with enhanced security
- [ ] Compliance with Indonesian pharmacy regulations
- [ ] BPJS reporting requirements

### Integration Points
- **Epic 6 (Pharmacy)**: Share drug master file, dispense data
- **Epic 9 (Billing)**: Inventory valuation for financial reports
- **Epic 10 (BPJS)**: Formulary pricing, coverage status
- **Epic 15 (Master Data)**: Supplier data, location data

### Performance Considerations
- Real-time stock updates across all locations
- Efficient batch tracking algorithms
- Optimized queries for high-volume transactions
- Background processing for forecasting calculations
- Caching for frequently accessed data

---

## Technical Implementation Notes

### Database Schema Extensions

```sql
-- New tables for advanced inventory

CREATE TABLE inventory_locations (
    location_id SERIAL PRIMARY KEY,
    parent_location_id INTEGER REFERENCES inventory_locations(location_id),
    location_name VARCHAR(100) NOT NULL,
    location_type VARCHAR(50) NOT NULL, -- 'MAIN', 'WARD', 'OR', 'ICU', 'SATELLITE'
    capacity_limit INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory_batches (
    batch_id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES drug_master(item_id),
    location_id INTEGER REFERENCES inventory_locations(location_id),
    batch_no VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_cost DECIMAL(12,2) NOT NULL,
    expiry_date DATE NOT NULL,
    manufacturing_date DATE,
    supplier_id INTEGER REFERENCES suppliers(supplier_id),
    received_date DATE NOT NULL,
    is_quarantined BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(item_id, batch_no, location_id)
);

CREATE TABLE stock_movements (
    movement_id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES drug_master(item_id),
    batch_id INTEGER REFERENCES inventory_batches(batch_id),
    from_location_id INTEGER REFERENCES inventory_locations(location_id),
    to_location_id INTEGER REFERENCES inventory_locations(location_id),
    movement_type VARCHAR(50) NOT NULL, -- 'RECEIPT', 'DISPENSE', 'TRANSFER', 'ADJUSTMENT', 'EXPIRY', 'DAMAGE'
    quantity INTEGER NOT NULL,
    unit_cost DECIMAL(12,2),
    reason_code VARCHAR(50),
    reference_id INTEGER, -- PO ID, dispense ID, etc.
    performed_by INTEGER REFERENCES users(user_id),
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE TABLE forecast_models (
    forecast_id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES drug_master(item_id),
    location_id INTEGER REFERENCES inventory_locations(location_id),
    model_type VARCHAR(50) NOT NULL, -- 'MOVING_AVG', 'EXP_SMOOTHING', 'SEASONAL', 'LINEAR_REG'
    forecast_horizon INTEGER NOT NULL, -- days
    forecast_date DATE NOT NULL,
    parameters JSONB, -- model-specific parameters
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE forecast_data (
    forecast_data_id SERIAL PRIMARY KEY,
    forecast_id INTEGER REFERENCES forecast_models(forecast_id),
    forecast_date DATE NOT NULL,
    predicted_quantity INTEGER NOT NULL,
    lower_bound INTEGER, -- confidence interval
    upper_bound INTEGER,
    actual_quantity INTEGER, -- filled after actual consumption
    accuracy_pct DECIMAL(5,2), -- calculated after actuals known
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reorder_points (
    rp_id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES drug_master(item_id),
    location_id INTEGER REFERENCES inventory_locations(location_id),
    reorder_point INTEGER NOT NULL,
    safety_stock INTEGER NOT NULL,
    economic_order_qty INTEGER,
    service_level_pct DECIMAL(5,2) NOT NULL,
    lead_time_days INTEGER NOT NULL,
    last_reviewed_date DATE,
    auto_adjust BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(item_id, location_id)
);

CREATE TABLE supplier_performance (
    performance_id SERIAL PRIMARY KEY,
    supplier_id INTEGER REFERENCES suppliers(supplier_id),
    evaluation_period_start DATE NOT NULL,
    evaluation_period_end DATE NOT NULL,
    on_time_delivery_rate DECIMAL(5,2),
    complete_fulfillment_rate DECIMAL(5,2),
    avg_lead_time_days DECIMAL(5,2),
    damage_rate DECIMAL(5,2),
    wrong_item_rate DECIMAL(5,2),
    price_competitive_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),
    score_category VARCHAR(20), -- 'EXCELLENT', 'GOOD', 'ACCEPTABLE', 'POOR', 'UNACCEPTABLE'
    evaluated_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE physical_counts (
    count_id SERIAL PRIMARY KEY,
    count_name VARCHAR(100) NOT NULL,
    count_type VARCHAR(50) NOT NULL, -- 'FULL', 'CYCLE', 'SPOT', 'CATEGORY'
    location_id INTEGER REFERENCES inventory_locations(location_id),
    scheduled_date DATE NOT NULL,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    status VARCHAR(20) NOT NULL, -- 'PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'
    performed_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE physical_count_details (
    count_detail_id SERIAL PRIMARY KEY,
    count_id INTEGER REFERENCES physical_counts(count_id),
    item_id INTEGER REFERENCES drug_master(item_id),
    batch_no VARCHAR(50),
    location_id INTEGER REFERENCES inventory_locations(location_id),
    system_qty INTEGER NOT NULL,
    counted_qty INTEGER NOT NULL,
    variance_qty INTEGER NOT NULL,
    variance_value DECIMAL(12,2),
    unit_cost DECIMAL(12,2),
    counted_by INTEGER REFERENCES users(user_id),
    counted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified BOOLEAN DEFAULT FALSE,
    verified_by INTEGER REFERENCES users(user_id),
    notes TEXT
);

CREATE TABLE return_requests (
    return_id SERIAL PRIMARY KEY,
    supplier_id INTEGER REFERENCES suppliers(supplier_id),
    return_type VARCHAR(50) NOT NULL, -- 'DAMAGED', 'WRONG_ITEM', 'EXPIRY', 'QUALITY', 'OVERSTOCK', 'RECALL'
    request_date DATE NOT NULL,
    total_value DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'PENDING', 'AUTHORIZED', 'SHIPPED', 'CREDITED', 'REJECTED'
    authorization_no VARCHAR(50),
    credit_note_no VARCHAR(50),
    approved_by INTEGER REFERENCES users(user_id),
    approved_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE return_request_details (
    return_detail_id SERIAL PRIMARY KEY,
    return_id INTEGER REFERENCES return_requests(return_id),
    item_id INTEGER REFERENCES drug_master(item_id),
    batch_no VARCHAR(50),
    quantity INTEGER NOT NULL,
    unit_cost DECIMAL(12,2) NOT NULL,
    total_value DECIMAL(12,2) NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recall_notices (
    recall_id SERIAL PRIMARY KEY,
    manufacturer_id INTEGER REFERENCES manufacturers(manufacturer_id),
    product_name VARCHAR(200) NOT NULL,
    brand_name VARCHAR(200),
    batch_prefix VARCHAR(50),
    batch_from VARCHAR(50),
    batch_to VARCHAR(50),
    expiry_from DATE,
    expiry_to DATE,
    affected_quantity INTEGER,
    recall_date DATE NOT NULL,
    recall_reason TEXT NOT NULL,
    recall_type VARCHAR(50) NOT NULL, -- 'VOLUNTARY', 'MANDATORY'
    severity VARCHAR(20) NOT NULL, -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    status VARCHAR(20) NOT NULL, -- 'ACTIVE', 'IN_PROGRESS', 'COMPLETED', 'CLOSED'
    notification_source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE expiry_discounts (
    discount_id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES drug_master(item_id),
    days_to_expiry_from INTEGER NOT NULL,
    days_to_expiry_to INTEGER NOT NULL,
    discount_pct DECIMAL(5,2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    effective_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_inventory_batches_item ON inventory_batches(item_id);
CREATE INDEX idx_inventory_batches_location ON inventory_batches(location_id);
CREATE INDEX idx_inventory_batches_expiry ON inventory_batches(expiry_date);
CREATE INDEX idx_stock_movements_item ON stock_movements(item_id);
CREATE INDEX idx_stock_movements_date ON stock_movements(performed_at);
CREATE INDEX idx_physical_counts_status ON physical_counts(status);
CREATE INDEX idx_recall_notices_status ON recall_notices(status);
```

### Key Algorithms

1. **FEFO Dispensing**:
   - Always select batches with nearest expiry date
   - Consider current quantity and expiry date
   - Block expired batches

2. **Demand Forecasting**:
   - Auto-select best algorithm based on demand patterns
   - Track forecast accuracy
   - Adjust parameters based on performance

3. **Reorder Point Calculation**:
   - Consider daily usage, lead time, service level
   - Auto-adjust based on consumption patterns
   - Account for seasonality

4. **Supplier Scoring**:
   - Composite score with weighted components
   - Periodic recalculation
   - Trend analysis

---

## Dependencies on External Systems

### E-Katalog Integration
- **Endpoint**: E-Katalog API (LPSE)
- **Authentication**: API key + digital certificate
- **Data Sync**:
  - Product catalog updates (daily)
  - Price updates (weekly)
  - Order submission
  - Delivery tracking

### Supplier Integrations
- Electronic ordering (email, EDI, supplier portal)
- Order status updates
- Invoice processing
- Credit note management

### Regulatory Systems
- BPJS formulary updates
- Kemenkes POM reporting
- Drug regulatory authority (POM) notifications
- Recall notifications

---

## Testing Requirements

### Unit Tests
- Forecasting algorithm accuracy
- Reorder point calculations
- FEFO dispensing logic
- Supplier scoring calculations
- Valuation method calculations

### Integration Tests
- E-Katalog API integration
- Supplier API integrations
- Multi-location stock synchronization
- Physical count mobile workflow

### Performance Tests
- Real-time stock updates (target: <100ms)
- Forecast calculations (target: <5 seconds for 1000 items)
- Multi-location inventory queries (target: <2 seconds)
- Barcode scanning response (target: <500ms)

### User Acceptance Tests
- Pharmacy manager: Demand forecasting workflow
- Procurement officer: Automated ordering workflow
- Inventory controller: Physical count workflow
- Finance manager: Inventory valuation reports

---

## Success Metrics

### Operational Metrics
- **Stockout Rate**: <0.5% for critical medications
- **Inventory Turnover**: >4 times per year
- **Expiry Rate**: <2% for high-cost items, <5% overall
- **Forecast Accuracy**: MAPE <20%
- **Physical Count Accuracy**: >98%
- **Order Fulfillment Time**: <48 hours for urgent items

### Financial Metrics
- **Inventory Carrying Cost**: Reduce by 15-20%
- **Cost Avoidance**: Track discounts vs write-offs
- **Supplier On-Time Delivery**: >95%
- **Purchase Price Variance**: <5% vs budget

### User Satisfaction
- Pharmacy manager satisfaction: >85%
- Procurement efficiency improvement: >30%
- Training completion: >90%

---

## Risks & Mitigations

### High Risk
1. **Forecast Inaccuracy**: Could lead to stockouts or overstock
   - *Mitigation*: Start with conservative safety stocks, gradual implementation

2. **Multi-Location Complexity**: Data synchronization issues
   - *Mitigation*: Robust transaction management, real-time sync monitoring

3. **E-Katalog Integration**: External API dependency
   - *Mitigation*: Fallback to manual processes, regular testing

### Medium Risk
1. **User Adoption**: Complex workflows may resist adoption
   - *Mitigation*: Comprehensive training, phased rollout, quick wins

2. **Performance**: Large inventory data may impact performance
   - *Mitigation*: Database optimization, caching, background processing

3. **Regulatory Changes**: POM regulations may change
   - *Mitigation*: Flexible configuration, regular compliance reviews

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- Database schema implementation
- Multi-location inventory tracking
- Basic stock movement tracking
- Location management UI

### Phase 2: Forecasting & Ordering (Week 2-4)
- Demand forecasting algorithms
- Reorder point optimization
- Automated ordering suggestions
- Forecast dashboards

### Phase 3: Expiry & Supplier Management (Week 3-5)
- Expiry date management
- Automated discount schedules
- Supplier performance tracking
- Supplier scoring system
- E-Katalog integration

### Phase 4: Physical Counting & Returns (Week 4-5)
- Physical inventory count workflow
- Mobile barcode scanning
- Count variance management
- Return & recall management

### Phase 5: Reporting & Analytics (Week 5-6)
- Inventory valuation reports
- Cost analysis reports
- Supplier performance reports
- Forecast accuracy reports
- Executive dashboards

### Phase 6: Testing & Deployment (Week 6)
- Integration testing
- Performance testing
- User acceptance testing
- Training materials
- Go-live support

---

## Documentation Requirements

### User Documentation
- Pharmacy Manager Guide
- Procurement Officer Guide
- Inventory Controller Guide
- Training Manuals
- Video Tutorials

### Technical Documentation
- API Documentation
- Database Schema Documentation
- Integration Guides (E-Katalog, Suppliers)
- Algorithm Documentation
- Performance Tuning Guide

### Regulatory Documentation
- POM Compliance Guide
- BPJS Reporting Guide
- Audit Trail Documentation
- Recall Management SOP

---

## Open Questions & Assumptions

### Open Questions
1. Should we support multiple costing methods simultaneously or enforce one method hospital-wide?
2. What is the minimum acceptable forecast accuracy before go-live?
3. Should physical counts freeze system stock or allow parallel operations?
4. What is the maximum acceptable delay for multi-location stock synchronization?

### Assumptions
1. Basic pharmacy inventory (Epic 6) is already implemented
2. Hospital has barcode scanners available for physical counts
3. Suppliers can accept electronic orders via email or web portal
4. E-Katalog API is accessible and stable
5. Mobile devices/tablets are available for bedside counting
6. Internet connectivity is reliable for real-time sync

---

**Document Version**: 1.0
**Created**: 2026-01-15
**Status**: Draft - Ready for Review
**Next Review**: After Architecture Approval
