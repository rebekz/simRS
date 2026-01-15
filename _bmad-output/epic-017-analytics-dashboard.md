# Epic 17: Analytics Dashboard - Hospital KPIs and Reports

**Epic ID**: EPIC-017
**Business Value**: Data-driven decision making, operational visibility, performance monitoring, strategic planning support
**Complexity**: High
**Estimated Duration**: 5-6 weeks

---

## Overview

Analytics Dashboard provides comprehensive business intelligence and data visualization capabilities for SIMRS, enabling hospital administrators, clinicians, and managers to make data-driven decisions through real-time dashboards, KPI tracking, and predictive analytics. This epic transforms operational data into actionable insights for improving patient care, operational efficiency, and financial performance.

**Key Business Benefits**:
- Real-time visibility into hospital operations and performance metrics
- Data-driven decision making for resource allocation and strategic planning
- Early warning system for operational bottlenecks and clinical quality issues
- Improved financial performance through revenue optimization and cost control
- Enhanced patient satisfaction through service quality monitoring
- Regulatory compliance reporting automation
- Predictive capabilities for capacity planning and demand forecasting

---

## Dependencies

### Prerequisite Epics (All must be completed)
- **Epic 1**: Foundation & Security Infrastructure (user authentication, RBAC, audit logging, data warehouse foundation)
- **Epic 2**: Patient Registration & Queue Management (patient flow data, queue metrics)
- **Epic 3**: Medical Records & Clinical Documentation (clinical data quality metrics, diagnosis data)
- **Epic 4**: Outpatient Management (outpatient volume, consultation metrics)
- **Epic 5**: Inpatient Management (bed occupancy, length of stay, discharge data)
- **Epic 6**: Pharmacy Management (drug utilization, inventory costs)
- **Epic 9**: Billing, Finance & Claims (revenue, costs, BPJS claim performance)
- **Epic 10**: BPJS Integration (claim analytics, eligibility data)
- **Epic 13**: Reporting & Analytics (basic reporting foundation)

### Technical Dependencies
- Data warehouse with ETL pipelines from all operational systems
- Time-series database for real-time metrics storage
- Business intelligence platform or custom visualization framework
- Materialized views for performance optimization
- Scheduled batch jobs for data aggregation
- Caching layer for dashboard performance

---

## Key User Stories

### 1. Executive Dashboard with Hospital-Wide KPIs
**As a hospital director/CEO**, I want a comprehensive executive dashboard showing key hospital-wide performance indicators so that I can monitor overall hospital health and make strategic decisions.

### 2. Departmental Performance Dashboards
**As a department head**, I want a customized dashboard showing my department's specific performance metrics so that I can identify areas for improvement and demonstrate my team's performance.

### 3. Real-Time Operational Metrics Dashboard
**As an operations manager**, I want real-time visibility into bed occupancy, queue lengths, and wait times so that I can allocate resources dynamically and prevent bottlenecks.

### 4. Financial Analytics Dashboard
**As a finance director**, I want detailed financial analytics including revenue trends, cost analysis, and BPJS claim performance so that I can optimize revenue and control costs.

### 5. Clinical Quality Metrics Dashboard
**As a quality assurance officer**, I want to track clinical quality indicators including readmission rates, complication rates, and mortality rates so that I can ensure care standards are met.

### 6. Patient Satisfaction Analytics Dashboard
**As a patient experience manager**, I want to analyze patient satisfaction scores and feedback trends so that I can identify service gaps and improve patient experience.

### 7. Resource Utilization Reports Dashboard
**As a resource planner**, I want to analyze staff, equipment, and facility utilization rates so that I can optimize resource allocation and reduce waste.

### 8. Predictive Analytics for Capacity Planning
**As a strategic planner**, I want predictive analytics for patient demand forecasting and capacity planning so that I can proactively prepare for demand surges and optimize resource allocation.

---

## Detailed Acceptance Criteria

### User Story 1: Executive Dashboard with Hospital-Wide KPIs

**Dashboard Layout & Navigation**:
- [ ] Single-page executive dashboard with at-a-glance hospital overview
- [ ] Responsive design (desktop, tablet, mobile)
- [ ] Customizable dashboard layout (drag-and-drop widgets)
- [ ] Dashboard templates for different executive roles (CEO, COO, CFO, CMO)
- [ ] Time period selectors (today, yesterday, last 7 days, last 30 days, custom range)
- [ ] Comparison views (current vs. previous period, current vs. target, current vs. benchmark)
- [ ] Drill-down capability from high-level metrics to detailed reports
- [ ] Export dashboard to PDF, image, or scheduled email
- [ ] Dashboard refresh controls (auto-refresh every 5/15/30 minutes, manual refresh)

**Hospital-Wide KPIs Displayed**:
- [ ] **Patient Volume Metrics**:
  - Daily patient visits (outpatient, inpatient admissions, emergency)
  - Month-to-date and year-to-date totals
  - Comparison with same period last year
  - Trend charts (7-day, 30-day, 12-month views)

- [ ] **Financial KPIs**:
  - Daily revenue (total, by payer type: BPJS, Asuransi, Umum)
  - Revenue per patient visit
  - Outstanding accounts receivable
  - BPJS claim submission rate and approval rate
  - Average claim payment time
  - Month-to-date financial performance vs. budget

- [ ] **Operational KPIs**:
  - Bed occupancy rate (overall, by ward, by room class)
  - Average length of stay (ALOS)
  - Emergency department wait times (door to triage, door to doctor)
  - Outpatient queue lengths and average wait times
  - Operating room utilization rate
  - Laboratory turnaround time (TAT)
  - Radiology report completion time

- [ ] **Quality & Safety KPIs**:
  - Patient satisfaction score (overall, by department)
  - Readmission rate (30-day unplanned readmissions)
  - Hospital-acquired infection rate
  - Medication error rate
  - Mortality rate (overall, case-mix adjusted)
  - Fall rate with injury
  - Pressure ulcer prevalence

- [ ] **Staff Productivity KPIs**:
  - Patient visits per doctor (by department)
  - Nurse-to-patient ratio (by ward)
  - Staff overtime hours
  - Staff absenteeism rate

**Alert & Exception Management**:
- [ ] KPI threshold configuration (set warning/critical levels)
- [ ] Visual indicators for KPIs (green/yellow/red status)
- [ ] Alert notifications for KPI breaches (email, SMS, in-app)
- [ ] Exception dashboard showing only underperforming metrics
- [ ] Trend analysis alerts (sudden changes, gradual degradation)
- [ ] Comparison alerts (below target, below benchmark)

**Data Freshness & Performance**:
- [ ] Real-time data for operational KPIs (refreshed every 5 minutes)
- [ ] Near-real-time data for financial KPIs (refreshed every 15 minutes)
- [ ] Daily aggregated data for quality KPIs
- [ ] Dashboard load time <3 seconds
- [ ] Data query optimization (use materialized views, caching)
- [ ] Progressive loading (show high-level metrics first, then details)

---

### User Story 2: Departmental Performance Dashboards

**Department-Specific Dashboards**:
- [ ] **Outpatient Department Dashboard**:
  - Daily patient visits by poly (specialty clinic)
  - Average consultation time per doctor
  - Patient no-show rate
  - Doctor productivity (patients seen per day)
  - Queue length and wait time by poly
  - BPJS SEP generation rate
  - Prescription rate per consultation
  - Lab/radiology order rate
  - Patient satisfaction by poly
  - Revenue per patient visit by poly

- [ ] **Inpatient Department Dashboard**:
  - Bed occupancy by ward and room class
  - Admission/discharge/transfer metrics
  - Average length of stay (ALOS) by diagnosis
  - Bed turnover time
  - Readmission rate by department
  - Mortality rate by department
  - Pressure ulcer prevalence
  - Fall rate
  - Nursing hours per patient day
  - Patient satisfaction by ward

- [ ] **Emergency Department Dashboard**:
  - Patient arrivals per hour (trend over 24 hours)
  - Triage category distribution
  - Door-to-triage time
  - Door-to-doctor time by triage category
  - Length of stay in ED
  - Admission rate from ED
  - Left without being seen (LWBS) rate
  - ED mortality rate
  - Ambulance arrival metrics
  - Critical time metrics (door to needle, door to balloon)

- [ ] **Pharmacy Dashboard**:
  - Daily prescriptions filled
  - Average dispensing time
  - Prescription backlog
  - Drug inventory turns
  - Expired drug rate
  - Stockout rate (critical medications)
  - Purchasing metrics (order value, delivery time)
  - Dispensing error rate
  - Clinical intervention rate (pharmacist interventions)

- [ ] **Laboratory Dashboard**:
  - Daily test volume
  - Test turnaround time (TAT) by test type
  - TAT compliance percentage (tests completed within target time)
  - Critical value notification time
  - Test rejection rate
  - QC performance (Levey-Jennings, Westgard violations)
  - Instrument utilization rate
  - Revenue per test
  - Outlier detection (abnormal result rates)

- [ ] **Radiology Dashboard**:
  - Daily exam volume by modality (X-ray, CT, MRI, US)
  - Exam completion rate
  - Report turnaround time
  - Exam rejection rate (repeat exams)
  - Equipment utilization rate
  - Contrast media usage
  - Patient wait time for appointments
  - Report quality metrics (addendum rate)
  - Revenue per exam

**Dashboard Customization**:
- [ ] User-customizable dashboard layout
- [ ] Widget library (charts, KPI cards, tables, gauges)
- [ ] Drag-and-drop dashboard builder
- [ ] Save multiple dashboard configurations per user
- [ ] Share dashboards with other users
- [ ] Dashboard templates for common use cases
- [ ] Custom date range comparisons
- [ ] Filter by location, department, provider

**Performance Benchmarking**:
- [ ] Internal benchmarking (compare periods, departments)
- [ ] External benchmarking (compare to industry standards, KARS standards)
- [ ] Peer group comparison (similar-sized hospitals)
- [ ] National averages for key KPIs
- [ ] Best practice targets display
- [ ] Gap analysis (current vs. target)

---

### User Story 3: Real-Time Operational Metrics Dashboard

**Real-Time Bed Management**:
- [ ] **Bed Availability Display**:
  - Total beds by ward (occupied, available, maintenance, reserved)
  - Bed occupancy rate (overall, by ward, by room class, by specialty)
  - Clean vs. soiled beds
  - Isolation beds status
  - Ventilator availability
  - ICU/CCU bed status
  - Nursery bed occupancy
  - Real-time bed map with color-coded status
  - Bed assignment queue
  - Discharge predictions (beds becoming available)

- [ ] **Bed Demand Forecasting**:
  - Expected admissions (scheduled procedures, elective admissions)
  - ED admission probability
  - Bed demand prediction for next 24/48/72 hours
  - Overcapacity alerts (bed shortage warning)
  - Transfer recommendations (suggest wards with capacity)

**Real-Time Queue Management**:
- [ ] **Outpatient Queue Display**:
  - Current queue length by poly
  - Patients waiting vs. patients in consultation
  - Average wait time by poly
  - Longest wait time alert
  - Queue trend over time (chart showing queue growth/decline)
  - Doctor availability (doctors on duty, on break, unavailable)
  - Appointment schedule vs. walk-ins
  - Queue abandonment rate (patients who leave before being seen)

- [ ] **Multi-Department Queue Display**:
  - Pharmacy queue (prescriptions waiting, estimated wait time)
  - Laboratory queue (samples waiting, TAT status)
  - Radiology queue (exams waiting, appointment status)
  - Billing/ cashier queue (patients waiting, estimated wait time)
  - Centralized queue view (all departments in one screen)

- [ ] **Queue Analytics**:
  - Peak hours analysis (identify busy periods)
  - Average wait time by time of day
  - Service time distribution
  - Queue bottlenecks identification
  - Staff allocation recommendations (suggest adding doctors based on queue)

**Real-Time Wait Time Monitoring**:
- [ ] **Wait Time Thresholds**:
  - Define target wait times by department (poly registration, triage, doctor consultation, pharmacy, lab)
  - Visual indicators when wait times exceed targets
  - Wait time percentiles (50th, 75th, 90th, 95th)
  - Wait time trend over the day

- [ ] **Operational Bottleneck Detection**:
  - Identify longest wait times across all departments
  - Root cause analysis (doctor shortage, registration delays, lab delays)
  - Suggest interventions (add staff, redirect patients, open additional counters)
  - Track bottleneck resolution

**Real-Time Emergency Department Metrics**:
- [ ] ED census (patients in ED by triage category)
- [ ] ED boarding time (patients waiting for admission)
- [ ] ED bed capacity utilization
- [ ] Ambulance diversion status
- [ ] Critical time alerts (door to needle >60 min for stroke, door to balloon >90 min for STEMI)
- [ ] ED staff on duty (doctors, nurses, triage nurses)

**Operational Alerting**:
- [ ] Threshold-based alerts (queue length >X, wait time >Y minutes)
- [ ] Trend-based alerts (wait time increasing rapidly)
- [ ] Capacity alerts (bed occupancy >90%, ICU beds full)
- [ ] Staff shortage alerts (doctor count below required)
- [ ] Equipment downtime alerts (CT/MRI down, lab analyzer down)
- [ ] Multi-channel alert delivery (dashboard, email, SMS, push notification)

---

### User Story 4: Financial Analytics Dashboard

**Revenue Analytics**:
- [ ] **Revenue Trends**:
  - Daily, weekly, monthly, yearly revenue
  - Revenue by department (outpatient, inpatient, emergency, pharmacy, lab, radiology)
  - Revenue by payer type (BPJS, Asuransi, Umum/Pasien Umum)
  - Revenue by service type (consultations, procedures, drugs, lab, radiology, room charges)
  - Revenue per patient visit
  - Revenue trends (growth rate, seasonal patterns)
  - Year-over-year comparison
  - Actual vs. budget comparison

- [ ] **Payer Mix Analysis**:
  - Payer distribution (BPJS % vs. Asuransi % vs. Umum %)
  - Payer mix trends over time
  - Revenue contribution by payer
  - Average revenue per patient by payer
  - Patient volume by payer
  - Collection rate by payer

- [ ] **Revenue Cycle Metrics**:
  - Days in Accounts Receivable (DAR)
  - Net collection rate
  - Denial rate (BPJS claim rejections)
  - Clean claim rate (first-pass approval rate)
  - Average time to payment
  - Aging analysis (0-30, 31-60, 61-90, 90+ days)
  - Bad debt rate

**BPJS Claims Analytics**:
- [ ] **Claim Submission Metrics**:
  - Total claims submitted (daily, monthly, yearly)
  - Claim submission rate (claims submitted / eligible claims)
  - Claim submission timeliness (% submitted within 21 days)
  - Claim backlog (claims not yet submitted)

- [ ] **Claim Approval & Rejection Analytics**:
  - Claim approval rate (approved claims / submitted claims)
  - Claim rejection rate (rejected claims / submitted claims)
  - Top rejection reasons (missing data, invalid SEP, diagnosis mismatch, etc.)
  - Rejection trend analysis (improving or worsening)
  - Rejection rate by department, by doctor
  - Financial impact of rejections (lost revenue)

- [ ] **Claim Payment Analytics**:
  - Average payment time (days from submission to payment)
  - Payment aging (claims awaiting payment: 0-30, 31-60, 61-90, 90+ days)
  - Total outstanding BPJS receivables
  - Payment accuracy rate (paid amount vs. claimed amount)
  - Underpayment analysis (claims paid less than claimed)
  - Verifikasi status tracking (pending, approved, rejected, paid)

- [ ] **INA-CBG Package Analytics**:
  - Most common INA-CBG packages
  - Average package rate by diagnosis/procedure
  - Package profitability (revenue vs. cost)
  - LOS compliance (actual LOS vs. package LOS)
  - Upgrade case rate (upgraded to higher class)
  - Downgrade case rate (downgraded to lower class)

**Cost Analytics**:
- [ ] **Expense Tracking**:
  - Total expenses by category (personnel, medicines, supplies, equipment, utilities)
  - Expense trends over time
  - Expense per patient visit
  - Expense per inpatient day
  - Actual vs. budget comparison
  - Variance analysis (favorable vs. unfavorable)

- [ ] **Cost-Volume-Profit Analysis**:
  - Break-even analysis (patient volume needed to cover costs)
  - Contribution margin by service
  - Fixed vs. variable cost breakdown
  - Cost allocation by department
  - Overhead allocation

- [ ] **Pharmacy Cost Analytics**:
  - Drug cost per patient
  - High-cost drug utilization
  - Generic vs. brand prescribing rate
  - Drug wastage rate (expired drugs, unused drugs)
  - Inventory carrying cost
  - Purchase price variance (actual vs. standard cost)

- [ ] **Labor Cost Analytics**:
  - Total labor cost by department
  - Overtime cost analysis
  - Staff productivity cost (revenue per FTE)
  - Labor cost per patient visit
  - Staffing ratio vs. industry benchmark

**Profitability Analysis**:
- [ ] **Department Profit/Loss**:
  - Revenue by department
  - Direct costs by department
  - Allocated overhead costs
  - Department profit/loss
  - Profit margin by department
  - Trend analysis (improving or declining)

- [ ] **Service Line Profitability**:
  - Profitability by procedure/service
  - High-margin services identification
  - Loss-making services identification
  - Profitability by payer (BPJS vs. Asuransi vs. Umum)
  - Contribution margin analysis

**Financial Ratios & KPIs**:
- [ ] Current ratio, quick ratio (liquidity)
- [ ] Days cash on hand
- [ ] Operating margin
- [ ] Net patient revenue per adjusted discharge
- [ ] Operating revenue per adjusted patient day
- [ ] Salary expense as % of operating revenue
- [ ] Supply expense as % of operating revenue

---

### User Story 5: Clinical Quality Metrics Dashboard

**Outcome Quality Metrics**:
- [ ] **Readmission Analytics**:
  - 30-day unplanned readmission rate (overall, by department, by diagnosis)
  - 7-day readmission rate
  - Readmission reasons analysis
  - Readmission cost impact
  - High-readmission diagnoses identification
  - Readmission trend over time
  - Comparison to national benchmark

- [ ] **Mortality Analytics**:
  - Hospital mortality rate (overall, by department)
  - Case-mix adjusted mortality rate (risk-adjusted)
  - Mortality by diagnosis (DRG-specific mortality)
  - Mortality trend over time
  - Early mortality (deaths within 48 hours)
  - Mortality review tracking
  - Comparison to national benchmark

- [ ] **Complication Rates**:
  - Surgical site infection rate
  - Hospital-acquired infection rate (HAI)
  - Catheter-associated urinary tract infection (CAUTI) rate
  - Central line-associated bloodstream infection (CLABSI) rate
  - Ventilator-associated pneumonia (VAP) rate
  - Pressure ulcer prevalence (overall, by ward)
  - Falls with injury rate
  - Adverse drug reaction rate
  - Transfusion reaction rate
  - Return to OR rate

**Process Quality Metrics**:
- [ ] **Care Process Compliance**:
  - Medical record completion rate (>95% target)
  - Diagnosis coding rate (percentage of visits with ICD-10 codes)
  - Medication reconciliation on admission rate
  - Discharge summary completion rate
  - Informed consent documentation rate
  - Timeout procedure compliance for surgeries
  - Vital signs documentation completeness

- [ ] **Evidence-Based Care Measures**:
  - Antibiotic prophylaxis for surgical patients
  - DVT prophylaxis for at-risk patients
  - Aspirin for acute MI
  - Beta-blocker for heart failure
  - Stroke unit admission for stroke patients
  - Smoking cessation counseling

**Patient Safety Metrics**:
- [ ] **Medication Safety**:
  - Medication error rate (overall, by type, by severity)
  - Near-miss medication errors
  - High-alert medication errors
  - Drug interaction alerts overridden rate
  - Barcode scanning compliance rate (5 rights verification)
  - Adverse drug events rate

- [ ] **Diagnostic Safety**:
  - Critical test result notification time
  - Critical value alert acknowledgment rate
  - Radiology report addendum rate (significant errors)
  - Lab specimen rejection rate
  - Wrong patient incidents
  - Wrong site procedures (near misses and actual)

**Effectiveness & Efficiency Metrics**:
- [ ] **Length of Stay Analytics**:
  - Average length of stay (ALOS) overall
  - ALOS by diagnosis (DRG-specific ALOS)
  - ALOS by department
  - Actual LOS vs. expected LOS (case-mix adjusted)
  - Outlier identification (patients with prolonged LOS)
  - Short-stay outliers (possible premature discharge)
  - LOS trend over time

- [ ] **Appropriateness of Care**:
  - Unnecessary emergency department visits
  - Avoidable admissions
  - Readmission hotspots (high-readmission diagnoses)
  - High-cost variation by diagnosis (identify unwarranted variation)
  - Antibiotic utilization rate (by department, by diagnosis)
  - Imaging utilization rate (CT/MRI per 1000 visits)
  - Lab test utilization rate (tests per patient)
  - Blood transfusion rate

**Patient-Reported Outcome Measures (PROMs)**:
- [ ] Patient-reported pain scores
- [ ] Functional status improvement
- [ ] Patient-reported quality of life
- [ ] Patient experience scores (HCAHPS-style if applicable)

**Clinical Quality Benchmarking**:
- [ ] Internal benchmarking (compare departments, doctors)
- [ ] External benchmarking (compare to national standards)
- [ ] KARS accreditation standards compliance tracking
- [ ] Ministry of Health reporting requirements
- [ ] International benchmarking (WHO, OECD indicators)

**Quality Improvement Tools**:
- [ ] Run charts (show trends over time)
- [ ] Control charts (UCL, LCL, identify special cause variation)
- [ ] Pareto charts (identify vital few issues)
- [ ] Scatter plots (identify correlations)
- [ ] Drill-down to individual cases for review
- [ ] Export data for quality improvement projects

---

### User Story 6: Patient Satisfaction Analytics Dashboard

**Patient Satisfaction Surveys**:
- [ ] **Survey Management**:
  - Survey distribution (SMS, email, in-app, paper)
  - Survey response rate
  - Survey completion time
  - Survey reminders
  - Survey invitation tracking

- [ ] **Overall Satisfaction Metrics**:
  - Overall satisfaction score (mean, distribution)
  - Net Promoter Score (NPS) - "Would you recommend this hospital?"
  - Patient satisfaction trend over time
  - Satisfaction by department
  - Satisfaction by service type (outpatient, inpatient, emergency)
  - Satisfaction by payer type (BPJS, Asuransi, Umum)

**Satisfaction by Dimension**:
- [ ] **Access & Waiting Times**:
  - Satisfaction with wait times (registration, consultation, pharmacy)
  - Ease of appointment booking
  - Wait time perception vs. actual wait time
  - Queue management satisfaction

- [ ] **Quality of Care**:
  - Doctor communication quality
  - Nurse care quality
  - Explanation of diagnosis and treatment
  - Involvement in decision-making
  - Perceived clinical competence

- [ ] **Facilities & Environment**:
  - Cleanliness satisfaction
  - Comfort of facilities (waiting areas, rooms)
  - Noise levels
  - Food quality (for inpatients)
  - Parking availability

- [ ] **Billing & Administrative Processes**:
  - Clarity of billing information
  - Ease of payment process
  - Staff helpfulness (registration, billing, information)
  - Administrative efficiency

- [ ] **Continuity & Coordination**:
  - Care coordination between departments
  - Discharge instructions clarity
  - Follow-up appointment scheduling
  - Medication explanation at discharge

**Text Analytics & Feedback**:
- [ ] **Open-Ended Comments Analysis**:
  - Word cloud (frequent terms in patient comments)
  - Sentiment analysis (positive, neutral, negative comments)
  - Topic modeling (identify common themes: long wait, rude staff, clean facility, etc.)
  - Comment categorization (staff, facility, process, clinical)
  - Complaint tracking and resolution
  - Compliment recognition (staff recognition)

- [ ] **Complaint Management**:
  - Complaint categorization
  - Complaint severity level
  - Complaint response time
  - Complaint resolution rate
  - Recurring complaint identification

**Benchmarking & Targets**:
- [ ] Internal benchmarking (compare departments)
- [ ] External benchmarking (compare to other hospitals)
- [ ] Target satisfaction scores
- [ ] Improvement trajectory tracking

**Staff Performance Recognition**:
- [ ] Top-rated doctors and nurses
- [ ] Most mentioned staff in positive comments
- [ ] Department satisfaction rankings
- [ ] Recognition alerts for highly-rated staff

---

### User Story 7: Resource Utilization Reports Dashboard

**Human Resource Utilization**:
- [ ] **Staff Productivity Metrics**:
  - Patient visits per doctor (by department, by doctor)
  - Consultations per doctor per day
  - Procedures performed per doctor
  - Nursing hours per patient day
  - Nurse-to-patient ratio (by ward)
  - Staffed hours vs. scheduled hours
  - Overtime hours (total, by department, by staff)
  - On-call hours
  - Productivity trend over time

- [ ] **Workload Distribution**:
  - Workload balance among doctors (fair distribution analysis)
  - Nurse assignment distribution
  - Shift coverage analysis (gaps in staffing)
  - Weekend/holiday staffing analysis
  - On-call burden distribution

- [ ] **Staff Attendance & Availability**:
  - Absenteeism rate (overall, by department)
  - Leave utilization (annual leave, sick leave)
  - Staff turnover rate
  - Staff on duty vs. staff scheduled
  - Replacement staff usage (locum, overtime)

**Equipment Utilization**:
- [ ] **Medical Equipment Utilization**:
  - CT scanner utilization rate (hours used / available hours)
  - MRI scanner utilization rate
  - X-ray machine utilization rate
  - Ultrasound machine utilization rate
  - Operating room utilization rate
  - Laboratory analyzer utilization rate
  - Ventilator utilization rate
  - Patient monitor utilization rate
  - Equipment idle time analysis
  - Peak usage hours

- [ ] **Equipment Maintenance & Downtime**:
  - Equipment downtime tracking
  - Maintenance schedule compliance
  - Breakdown frequency
  - Mean time between failures (MTBF)
  - Mean time to repair (MTTR)
  - Equipment replacement planning

**Facility Utilization**:
- [ ] **Bed Utilization**:
  - Overall bed occupancy rate
  - Bed occupancy by ward
  - Bed occupancy by room class (VVIP, VIP, Class 1, 2, 3)
  - Average length of stay by bed type
  - Bed turnover time (time between discharge and next admission)
  - Bed utilization trend over time
  - Seasonal bed utilization patterns

- [ ] **Facility Space Utilization**:
  - Outpatient clinic utilization (patient visits per clinic hour)
  - Operating room utilization (hours used / available hours)
  - Emergency department bed utilization
  - Pharmacy counter utilization
  - Laboratory workstation utilization
  - Waiting area usage patterns

**Supply & Inventory Utilization**:
- [ ] **Medicine Utilization**:
  - Drug consumption rate (by drug, by department)
  - High-cost drug utilization monitoring
  - Antibiotic utilization rate (DDD per 1000 patient days)
  - Narcotic/controlled drug utilization
  - Drug wastage rate (expired, spoiled, unused)
  - Inventory turnover rate
  - Stockout rate (frequency and duration)

- [ ] **Supply Utilization**:
  - Medical supply consumption (by category, by department)
  - Surgical supply utilization
  - Lab reagent consumption
  - Supply cost per patient
  - Supply wastage tracking
  - Supply utilization benchmarking

**Resource Optimization Recommendations**:
- [ ] Staff reallocation suggestions (move staff from underutilized to overutilized areas)
- [ ] Equipment sharing opportunities
- [ ] Bed assignment optimization
- [ ] Operating room scheduling optimization
- [ ] Clinic appointment optimization
- [ ] Resource cost-saving opportunities
- [ ] Capacity planning recommendations (expand/reduce resources)

---

### User Story 8: Predictive Analytics for Capacity Planning

**Patient Demand Forecasting**:
- [ ] **Outpatient Visit Forecasting**:
  - Forecast outpatient visits for next 7/14/30 days (by poly)
  - Forecast accuracy tracking (MAPE - Mean Absolute Percentage Error)
  - Seasonal pattern identification
  - Holiday and special event impact analysis
  - Appointment vs. walk-in forecasting
  - Doctor scheduling optimization based on forecast

- [ ] **Inpatient Admission Forecasting**:
  - Forecast daily admissions for next 7/14/30 days (by ward, by specialty)
  - Forecast emergency admissions
  - Forecast elective admissions (scheduled procedures)
  - Length of stay prediction (by diagnosis, by patient)
  - Discharge prediction (likelihood of discharge tomorrow)
  - Bed demand forecast (total beds needed by ward)
  - Overcapacity risk prediction

- [ ] **Emergency Department Demand Forecasting**:
  - Forecast ED arrivals for next 24/48/72 hours (by hour)
  - Forecast ED admissions
  - Forecast triage category distribution
  - Seasonal and daily pattern analysis
  - Impact of external factors (weather, events, outbreaks)
  - Staffing requirement prediction

**Capacity Planning Scenarios**:
- [ ] **What-If Analysis**:
  - Scenario 1: 10% increase in patient volume
  - Scenario 2: 20% increase in emergency admissions
  - Scenario 3: Flu season surge
  - Scenario 4: New ward/unit opening
  - Scenario 5: Ward closure for renovation
  - Scenario impact on bed occupancy, staff needs, costs

- [ ] **Resource Requirement Planning**:
  - Required bed capacity for forecasted demand
  - Required staff (doctors, nurses) for forecasted demand
  - Required equipment (CT, MRI, OR time) for forecasted demand
  - Gap analysis (capacity vs. demand)
  - Resource allocation optimization

**Predictive Models**:
- [ ] **Length of Stay Prediction**:
  - Predict LOS at admission (based on diagnosis, age, comorbidities)
  - Update LOS prediction daily during stay
  - Identify outliers (prolonged LOS)
  - Early discharge prediction
  - LOS prediction by DRG

- [ ] **Readmission Risk Prediction**:
  - Predict 30-day readmission risk at discharge
  - Risk factors identification
  - High-risk patient flagging
  - Intervention recommendations (follow-up planning)
  - Readmission prevention programs targeting

- [ ] **No-Show Prediction**:
  - Predict appointment no-show probability
  - Risk factors (history, appointment time, weather)
  - Overbooking optimization
  - Reminder strategy optimization

- [ ] **Deterioration Risk Prediction**:
  - Predict clinical deterioration (sepsis, cardiac arrest)
  - Early warning score (EWS) tracking
  - Rapid response team activation prediction
  - ICU transfer risk prediction

**Demand Drivers Analysis**:
- [ ] Seasonal demand patterns (monthly, quarterly, yearly)
- [ ] Day-of-week patterns (weekday vs. weekend)
- [ ] Time-of-day patterns (peak hours)
- [ ] Holiday and special event impact
- [ ] Disease outbreak impact (flu, dengue, COVID-19)
- [ ] Community factors impact (weather, pollution)
- [ ] Referral patterns impact

**Capacity Planning Reports**:
- [ ] Monthly capacity planning report (forecast vs. actual)
- [ ] Quarterly capacity review (trends, recommendations)
- [ ] Annual capacity planning (strategic resource planning)
- [ ] Scenario analysis reports (what-if results)
- [ ] Capital expenditure planning (equipment, facility expansion)
- [ ] Staffing plan development (hiring needs)

**Forecasting Model Performance**:
- [ ] Forecast accuracy tracking (MAPE, MAD, bias)
- [ ] Model retraining (regularly update with new data)
- [ ] Model comparison (test multiple algorithms)
- [ ] Forecast error analysis (identify systematic errors)
- [ ] Continuous improvement

---

## Technical Notes

### Data Architecture

**Data Warehouse Design**:
- **Star Schema**: Fact tables for events (visits, admissions, prescriptions, lab tests) with dimension tables (patients, providers, departments, time)
- **Data Marts**: Separate data marts for different domains (clinical, financial, operational, quality)
- **Slowly Changing Dimensions (SCD)**: Type 2 for tracking historical changes (doctor department transfers, bed class changes)
- **Conformed Dimensions**: Shared dimensions across data marts for consistent reporting
- **Fact Tables**:
  - fact_patient_visit (outpatient visits)
  - fact_admission (inpatient stays)
  - fact_emergency_visit (ED visits)
  - fact_lab_order (lab tests)
  - fact_radiology_order (radiology exams)
  - fact_prescription (medications prescribed)
  - fact_dispense (medications dispensed)
  - fact_billing_transaction (charges and payments)
  - fact_bpjs_claim (BPJS claims)
  - fact_inventory_transaction (stock movements)

**ETL/ELT Pipelines**:
- **Extraction**: Change Data Capture (CDC) from operational databases (PostgreSQL WAL, timestamp-based incremental extraction)
- **Transformation**: Data cleaning, validation, enrichment, aggregation using SQL, dbt, or Python
- **Loading**: Batch loading (nightly for historical data), streaming for real-time data
- **Scheduling**: Apache Airflow or dbt Cloud for orchestrating ETL jobs
- **Data Quality**: Automated data quality checks (completeness, accuracy, consistency, timeliness)
- **Data Lineage**: Track data flow from source to warehouse to dashboard

**Data Storage**:
- **Operational Data Store (ODS)**: Near-real-time copy of operational data (15-minute refresh)
- **Data Warehouse**: Historical data archive (10+ years), optimized for analytics (columnar storage)
- **Data Lake**: Raw data storage for future analytics (Parquet files in S3-compatible storage)
- **Time-Series Database**: InfluxDB or TimescaleDB for real-time metrics (bed occupancy, queue lengths)
- **Caching Layer**: Redis for frequently accessed data (dashboard KPIs, user sessions)

### Business Intelligence Stack

**Option 1: Open Source Stack**:
- **Metabase**: Business intelligence platform (SQL-based dashboards, easy to use)
- **Apache Superset**: Advanced BI platform (rich visualizations, SQL Lab)
- **Grafana**: Real-time monitoring dashboards (time-series data)
- **Redash**: Query and visualization tool (SQL-based)

**Option 2: Commercial Stack**:
- **Tableau**: Advanced visualization, drag-and-drop dashboard builder
- **Power BI**: Microsoft BI platform, good Excel integration
- **Looker**: Modern BI platform, LookML for data modeling
- **Qlik Sense**: Associative analytics engine

**Option 3: Custom Dashboard**:
- **Frontend Framework**: React with TypeScript
- **Visualization Library**: Recharts, D3.js, Victory, Plotly.js
- **Real-Time Updates**: WebSocket connections for live data
- **API Backend**: FastAPI with SQL endpoints
- **Query Builder**: GUI-based query builder for non-technical users

### Performance Optimization

**Materialized Views**:
- Pre-compute expensive aggregations (daily revenue by department, monthly bed occupancy)
- Refresh materialized views on schedule (nightly, hourly)
- Use materialized views for dashboard KPIs

**Indexing Strategy**:
- Create indexes on frequently filtered columns (date, department, patient_id)
- Create composite indexes for common query patterns
- Create covering indexes for dashboard queries
- Regular index maintenance (vacuum, analyze)

**Query Optimization**:
- Use query optimization techniques (avoid N+1 queries, use joins efficiently)
- Limit result sets (pagination, top N queries)
- Use window functions for ranking and percentile calculations
- Cache query results (Redis cache with TTL)

**Dashboard Performance**:
- Lazy loading (load data on demand, not all at once)
- Progressive rendering (show high-level metrics first, then details)
- Data pagination (large tables with server-side pagination)
- Debouncing (avoid excessive API calls during user interactions)
- Background refresh (update data in background, show cached data immediately)

### Real-Time Data Processing

**Streaming Architecture**:
- **Message Queue**: Apache Kafka or Redis Streams for event streaming
- **Stream Processing**: Apache Flink or Spark Streaming for real-time aggregation
- **Change Data Capture**: Debezium for streaming database changes
- **Real-Time Metrics**: Compute bed occupancy, queue lengths in real-time

**Real-Time Data Sources**:
- Bed status changes (admission, discharge, transfer)
- Queue updates (patient queue-in, queue-out)
- Vital signs monitoring (ICU patient data)
- Lab critical values (trigger immediate notification)
- ED arrivals (real-time ED census)

### Data Security & Privacy

**Access Control**:
- Role-Based Access Control (RBAC) for dashboards
- Row-level security (users see data for their departments only)
- Column-level security (sensitive fields hidden for non-admin users)
- Audit logging for dashboard access and data exports

**Data Anonymization**:
- Patient data anonymization in non-clinical dashboards (age ranges instead of DOB)
- Aggregation only (no individual patient data in executive dashboards)
- Data masking for sensitive fields (names, NIK, addresses)

**Compliance**:
- HIPAA-style protections for patient data
- Indonesian Personal Data Protection Act (PDP Law) compliance
- Data retention policies (analytics data: 10 years, audit logs: 6 years)
- Patient data access logging (who accessed what patient data)

### Scalability Considerations

**Horizontal Scaling**:
- Deploy BI platform on multiple servers (load balancing)
- Database read replicas (direct read queries to replicas)
- Distributed computing for heavy analytics (Spark cluster)
- CDN for static assets (dashboard UI, JavaScript libraries)

**Vertical Scaling**:
- Optimize database server (more RAM, faster SSD, more CPU cores)
- Optimize BI server (more memory for caching)
- Partition large tables (by date, by department)

**Caching Strategy**:
- Cache dashboard KPIs (TTL: 5-15 minutes)
- Cache frequently accessed data (reference data, user permissions)
- Cache expensive queries (aggregations, complex joins)
- Cache invalidation on data updates

---

## Data Warehouse Requirements

### Data Models

**Dimension Tables**:
- **dim_patient**: Patient demographics (name, DOB, gender, address, phone, blood type, religion)
- **dim_provider**: Healthcare providers (doctors, nurses) with details (name, specialization, department)
- **dim_department**: Hospital departments (poly, wards, ICU, pharmacy, lab, radiology)
- **dim_location**: Physical locations (wards, rooms, beds, clinics)
- **dim_diagnosis**: ICD-10 codes (code, description, category, chapter)
- **dim_procedure**: Procedure codes (ICD-9-PCS, CPT codes)
- **dim_drug**: Drug master data (generic name, brand names, dosage forms, BPJS codes)
- **dim_insurance**: Insurance companies and BPJS details
- **dim_time**: Date/time dimensions (date, month, quarter, year, day of week, holiday flag)
- **dim_bed**: Bed details (ward, room, bed number, bed class, status)

**Fact Tables**:
- **fact_outpatient_visit**: Outpatient visit facts (visit_id, patient_id, provider_id, department_id, date, diagnosis_id, revenue, queue_time, consultation_time)
- **fact_inpatient_stay**: Inpatient stay facts (admission_id, patient_id, department_id, bed_id, admission_date, discharge_date, los, diagnosis_id, revenue, cost)
- **fact_emergency_visit**: ED visit facts (visit_id, patient_id, triage_category, arrival_time, doctor_time, disposition)
- **fact_lab_order**: Lab test facts (order_id, patient_id, test_id, order_time, result_time, tat, critical_flag)
- **fact_radiology_order**: Radiology exam facts (order_id, patient_id, exam_type, order_time, report_time, contrast_flag)
- **fact_prescription**: Prescription facts (prescription_id, patient_id, drug_id, prescription_date, dispensed_flag)
- **fact_dispense**: Dispensing facts (dispense_id, patient_id, drug_id, dispense_date, quantity, cost)
- **fact_billing_transaction**: Billing facts (transaction_id, patient_id, charge_code, amount, date, payer_type)
- **fact_bpjs_claim**: BPJS claim facts (claim_id, sep_no, submission_date, approval_date, status, amount_claimed, amount_paid)
- **fact_inventory_transaction**: Inventory facts (transaction_id, drug_id, transaction_type, quantity, date)
- **fact_patient_satisfaction**: Survey facts (survey_id, patient_id, survey_date, satisfaction_score, comments)
- **fact_quality_event**: Quality events (event_id, patient_id, event_type, event_date, severity, description)

### Data Integration Points

**Source Systems**:
- **SIMRS Operational Database (PostgreSQL)**: Patient registration, medical records, admissions, billing
- **BPJS Integration Data**: Claims data, eligibility data, SEP data
- **SATUSEHAT Integration Data**: FHIR resources (Patient, Encounter, Condition)
- **External Systems**: Pharmacy inventory, lab instruments, radiology PACS

**Integration Frequency**:
- **Real-Time**: Bed status, queue updates, critical lab values (streaming)
- **Near Real-Time**: Patient registration, admissions, discharges (every 5-15 minutes)
- **Batch**: Financial data, claims data, quality data (nightly)
- **Historical Load**: Initial data warehouse load (full historical extraction)

### Data Quality Checks

**Completeness Checks**:
- Required fields present (patient_id, date, amount)
- Foreign key integrity (all references valid)
- No null values in critical fields

**Accuracy Checks**:
- Numerical ranges (age between 0-150, LOS >0)
- Date consistency (admission_date <= discharge_date)
- Logic checks (discharged patients must have discharge disposition)

**Consistency Checks**:
- Consistent coding (ICD-10 codes valid, LOINC codes valid)
- Consistent units (mg vs. g, mL vs. L)
- Consistent categorization (department mappings)

**Timeliness Checks**:
- Data freshness (last update time)
- Delay detection (data not loaded within expected window)
- Lag monitoring (operational to warehouse latency)

**Uniqueness Checks**:
- Primary key uniqueness
- No duplicate records (same patient visit counted twice)

### Data Retention & Archival

**Retention Policies**:
- **Operational Data Store (ODS)**: 90 days (recent operational data)
- **Data Warehouse**: 10+ years (historical analytics)
- **Raw Data Archive**: 25+ years (medical records legal requirement)
- **Audit Logs**: 6 years (regulatory requirement)
- **Dashboard Query Logs**: 1 year (usage analytics)

**Archival Strategy**:
- Partition tables by year/month
- Archive old partitions to cold storage (S3 Glacier, tape)
- Compress archived data
- Maintain indexes on recent partitions only

### Data Governance

**Data Stewardship**:
- Assign data stewards for each data domain (clinical, financial, operational)
- Data quality ownership (stewards responsible for data quality in their domain)
- Data dictionary (business definitions for all metrics)
- Metadata management (data lineage, data source, transformation logic)

**Data Access Governance**:
- Data access request workflow (users request access to dashboards)
- Access approval (department heads approve access for their staff)
- Access review (quarterly review of dashboard access)
- Revocation of access (when staff leave or change roles)

**Data Usage Policies**:
- Acceptable use policy (no patient data export for personal use)
- Data export logging (all data exports logged and reviewed)
- Dashboard usage monitoring (track which dashboards are used, by whom)
- Performance monitoring (identify slow dashboards, optimize queries)

---

## Success Criteria

### Technical Success
- [ ] Data warehouse operational with 99.9% uptime
- [ ] ETL pipelines complete with <1 hour latency for batch data
- [ ] Real-time metrics refreshed every 5 minutes
- [ ] Dashboard load time <3 seconds
- [ ] Query performance <5 seconds for 95% of queries
- [ ] Data accuracy >99% (validated against source systems)
- [ ] Dashboard adoption >80% of management staff
- [ ] Mobile-responsive dashboards
- [ ] Export functionality working (PDF, Excel, CSV)

### Business Success
- [ ] 100% of executive staff use dashboards weekly
- [ ] Data-driven decisions documented (improvements attributed to analytics)
- [ ] Reduction in time to generate reports (from days to minutes)
- [ ] Improved financial performance (revenue increase, cost reduction)
- [ ] Improved operational efficiency (reduced wait times, better resource utilization)
- [ ] Improved clinical quality (reduced readmissions, reduced complications)
- [ ] Improved patient satisfaction (higher satisfaction scores)
- [ ] Earlier detection of issues (proactive vs. reactive management)

### User Satisfaction
- [ ] User satisfaction score >4.0/5.0 for dashboards
- [ ] Dashboard usage >3 times per week per active user
- [ ] <5% of users report data accuracy issues
- [ ] <10% of users report performance issues

---

## Risks & Mitigation

### Technical Risks

**Risk 1: Data Quality Issues**
- **Impact**: High - Poor decisions based on bad data
- **Mitigation**: Comprehensive data quality checks, data stewardship program, regular data audits, automated validation

**Risk 2: Poor Dashboard Performance**
- **Impact**: Medium - Low user adoption due to slow dashboards
- **Mitigation**: Materialized views, caching, query optimization, database indexing, lazy loading, progressive rendering

**Risk 3: Data Warehouse Scalability Issues**
- **Impact**: Medium - System cannot handle data volume growth
- **Mitigation**: Partitioning, archival, read replicas, horizontal scaling, cloud-based data warehouse (Snowflake, BigQuery)

**Risk 4: Integration Failures**
- **Impact**: High - Data not loading from source systems
- **Mitigation**: Robust ETL error handling, retry logic, alerting for failed jobs, fallback to manual data entry

### Organizational Risks

**Risk 1: Low User Adoption**
- **Impact**: High - Dashboards not used, no ROI
- **Mitigation**: User-centered design, training program, dashboard champions (power users), continuous improvement based on feedback

**Risk 2: Resistance to Data-Driven Culture**
- **Impact**: Medium - Managers rely on intuition, not data
- **Mitigation**: Executive sponsorship, success stories, quick wins, training on data literacy

**Risk 3: Data Silos**
- **Impact**: Medium - Departments don't share data
- **Mitigation**: Centralized data warehouse, cross-departmental dashboards, data governance council

**Risk 4: Privacy Concerns**
- **Impact**: High - Patient data privacy violations
- **Mitigation**: Anonymization, access control, audit logging, compliance with regulations, data minimization

### Implementation Risks

**Risk 1: Scope Creep**
- **Impact**: Medium - Project timeline extends, budget overruns
- **Mitigation**: Phased implementation (MVP dashboards first, then advanced analytics), clear priorities, change control process

**Risk 2: Insufficient Resources**
- **Impact**: High - Lack of data engineers, BI developers
- **Mitigation**: Hire dedicated data team, train existing staff, use external consultants for initial setup, use managed services (cloud BI platforms)

**Risk 3: Changing Requirements**
- **Impact**: Medium - Requirements evolve during development
- **Mitigation**: Agile development, iterative prototyping, user feedback sessions, flexible architecture

---

## Post-Launch Considerations

### Phase 2 Enhancements (Future Capabilities)

**Advanced Analytics**:
- [ ] Machine learning models for more accurate predictions
- [ ] Anomaly detection (unusual patterns in operations, clinical outcomes)
- [ ] Root cause analysis (identify factors contributing to outcomes)
- [ ] Prescriptive analytics (recommend actions, not just insights)
- [ ] Natural language queries (ask questions in plain language)

**Population Health Analytics**:
- [ ] Disease registry analytics (diabetes, hypertension, heart disease)
- [ ] Epidemiological reporting (outbreak detection, disease surveillance)
- [ ] Social determinants of health analysis
- [ ] Health equity analytics (disparities by demographics)

**AI-Powered Insights**:
- [ ] Automated insight generation (identify trends, anomalies, opportunities)
- [ ] Natural language summaries of dashboards
- [ ] Intelligent alerting (reduce alert fatigue with smart prioritization)
- [ ] Predictive maintenance for equipment

**Self-Service Analytics**:
- [ ] Drag-and-drop dashboard builder for non-technical users
- [ ] Natural language query interface
- [ ] Data exploration tools (drill-down, slice-and-dice)
- [ ] Collaborative analytics (share dashboards, annotate insights)

**External Data Integration**:
- [ ] Weather data integration (impact on patient volume)
- [ ] Social media integration (patient sentiment analysis)
- [ ] Government health data integration (national benchmarks)
- [ ] Public health data integration (Kemenkes, WHO data)

### Maintenance & Support

**Ongoing Maintenance**:
- Monitor data pipeline performance
- Update dashboards based on user feedback
- Add new metrics and KPIs as business needs evolve
- Maintain data quality through continuous validation
- Optimize queries and dashboards for performance
- Update BI platform software (security patches, new features)

**User Support**:
- Dashboard user training (onboarding for new users)
- User guides and documentation
- Help desk support for dashboard issues
- Dashboard customization service (create custom dashboards for departments)
- User feedback mechanism (suggest improvements, report issues)

**Continuous Improvement**:
- Regular dashboard reviews (quarterly business reviews)
- Usage analytics (which dashboards are used, which are ignored)
- Performance metrics tracking (dashboard load times, query performance)
- User satisfaction surveys (identify pain points)
- Benchmark against industry best practices

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-3)
- Set up data warehouse infrastructure
- Design and implement core data models (fact and dimension tables)
- Build ETL pipelines for high-priority data sources
- Set up BI platform (Metabase/Superset or custom)
- Create basic authentication and RBAC

### Phase 2: Core Dashboards (Weeks 4-8)
- Executive Dashboard (hospital-wide KPIs)
- Departmental Dashboards (outpatient, inpatient, emergency)
- Real-Time Operational Metrics Dashboard
- Financial Analytics Dashboard
- User acceptance testing and feedback

### Phase 3: Advanced Analytics (Weeks 9-12)
- Clinical Quality Metrics Dashboard
- Patient Satisfaction Analytics Dashboard
- Resource Utilization Dashboard
- Predictive Analytics for Capacity Planning
- Performance optimization (query tuning, caching)

### Phase 4: Deployment & Training (Weeks 13-15)
- User training for all dashboard users
- Dashboard champions program (power users in each department)
- Go-live and hypercare support
- Feedback collection and iterative improvements
- Documentation and knowledge transfer

### Phase 5: Optimization & Expansion (Weeks 16-20)
- Performance optimization based on usage patterns
- Add additional metrics and KPIs based on user feedback
- Expand to more departments and users
- Advanced analytics (machine learning models)
- Continuous improvement

---

**Document Version:** 1.0
**Created:** 2026-01-15
**Status:** Draft - Ready for Review
**Epic ID:** EPIC-017
**Phase:** Phase 2-3 (Months 8-12 from project start, after core operational epics completed)
