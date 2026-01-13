# SIMRS-Khanza Deep Analysis

## Executive Summary

SIMRS-Khanza is the most popular open-source Hospital Management Information System (SIMRS - Sistem Informasi Manajemen Rumah Sakit) in Indonesia. Developed by Khanza.Soft Media, it's a comprehensive desktop-based system built with Java that supports full hospital operations including BPJS Kesehatan integration, Indonesia's national health insurance system.

**License:** Aladdin Free Public License (AFPL) - Free to use, cannot be sold for profit without permission

**Repository:** https://github.com/mas-elkhanza/SIMRS-Khanza

**Codebase Stats:**
- Total Java Files: 2,033 files
- Total Database Tables: 1,116 tables
- PHP/Web Files: 2,129 files
- Database Schema Lines: 42,315 lines
- Source Code Directories: 32 major modules

---

## 1. Tech Stack

### Core Technology
- **Language:** Java 8 (JavaSE 1.8)
- **Build Tool:** Apache Ant (build.xml)
- **IDE:** NetBeans (nbproject structure)
- **GUI Framework:** Java Swing (UsuLibrary, SwingX)
- **Modern Look:** FlatLaf 2.6 (material design look & feel)
- **JavaFX:** Included for advanced UI components

### Database
- **Primary Database:** MySQL 5.1.47 (mysql-connector-java-5.1.47.jar)
- **Alternative Supported:** HSQLDB 1.8.0-10 (embedded option)
- **Character Set:** latin1 with latin1_swedish_ci collation
- **Storage Engine:** InnoDB (relational integrity with foreign keys)

### Key Dependencies & Libraries

**Reporting:**
- JasperReports 6.8.0 (primary reporting engine)
- iReport (visual report designer)
- JFreeChart 1.0.12 (charts/graphs)
- iText 2.1.7 & 5.5.9 (PDF generation)
- Apache POI 4.1.0 (Excel export)
- Batik 1.11/1.13 (SVG graphics)

**HTTP/API:**
- Apache HttpClient 4.5.1 & 5.2.1
- Spring Web 5.3.30
- Spring Security Crypto 3.1.2
- JSON libraries: Jackson 2.18.1, Gson 2.2.2, json-simple

**Security:**
- Bouncy Castle 1.54 (cryptography)
- Spring Security Crypto
- Custom encryption (KhanzaSecurity16bit.jar)

**Database/ORM:**
- Hibernate 3 (ORM framework)
- Hibernate Annotations
- Commons DBCP 1.2.2 (connection pooling)

**Utilities:**
- Joda Time 2.10.1 (date/time handling)
- Apache Commons (multiple utilities)
- Log4j 1.2.17 (logging)
- Groovy 2.4.7 (scripting support)

**Hardware Integration:**
- RXTXComm (serial communication for medical devices)
- Comm API (hardware integration)

---

## 2. Complete Feature Set

### 2.1 Administrative Modules
**Location:** `/src/setting/` (68 files)

**Features:**
- System configuration management
- User authentication & authorization
- Role-based access control
- Hospital profile settings
- Department/unit management
- Shift management
- Doctor scheduling
- Room/bed management
- Insurance company setup (penjab)
- Payment method configuration
- Bank account integration
- API credentials management (BPJS, SATUSEHAT, etc.)

### 2.2 Patient Registration (Pendaftaran)
**Location:** `/src/simrskhanza/Dlg*` files

**Features:**
- New patient registration (pasien barus)
- Old patient registration
- Online booking integration
- BPJS card validation
- NIK validation via Dukcapil integration
- General patient registration (reg_periksa table)
- Emergency registration (IGD)
- Patient queue management (antrian)
- Medical record number (RM) generation
- Family/patient responsible party tracking
- Insurance information capture

**Key Tables:**
- `pasien` - Master patient data
- `reg_periksa` - Visit registration
- `booking_registrasi` - Appointments
- `bridging_sep` - BPJS SEP (Surat Eligibilitas Peserta)

### 2.3 Medical Records (Rekam Medis)
**Location:** `/src/rekammedis/` (472 files)

**Features:**
- Medical record documentation
- Doctor progress notes
- Nurse notes (catatan_keperawatan_ralan/ranap)
- Vital signs tracking
- Medical history
- Allergy recording
- Diagnosis documentation (ICD-10)
- Procedure documentation (ICD-9-CM)
- Consultation notes
- Referral management
- Death certificates
- Medical summaries
- Resume Pasien (patient summary)
- Digital medical records (berkas_digital_perawatan)

**Specialized Assessments:**
- Initial nursing assessment (penilaian_awal_keperawatan)
- Geriatric assessment
- Pediatric assessment
- Psychiatric assessment
- Cardiac assessment
- Pre-anesthesia assessment
- Pain assessment
- Fall risk assessment
- Nutritional assessment
- Discharge planning

### 2.4 Outpatient Clinic (Rawat Jalan)
**Key Files:** DlgRawatJalan.java, DlgKasirRalan.java

**Features:**
- Polyclinic management
- Doctor consultation
- Prescription writing (resep_dokter)
- Treatment procedures
- Laboratory requests
- Radiology requests
- Referrals to specialists
- BPJS SEP creation
- Billing (kasir ralan)
- Queue management

**Polyclinics Supported:**
- General practice
- Specializations (internal medicine, surgery, pediatrics, obstetrics/gynecology, etc.)
- Dental clinic
- Eye clinic
- ENT clinic
- Psychiatry
- Physiotherapy
- Nutrition

### 2.5 Inpatient (Rawat Inap)
**Key Tables:**
- `kamar` - Room/bed management
- `bangsal` - Ward/unit
- `pasien_bangsal` - Room assignments
- `reg_periksa` with `stts`='Rawat Inap'

**Features:**
- Admission/discharge/transfer (ADT)
- Room/bed management
- Daily room charges
- Doctor visits (rounds)
- Inpatient procedures
- Surgery scheduling
- Medication administration
- Diet orders
- Nursing care plans
- Discharge planning
- Inpatient billing

### 2.6 Emergency Department (IGD - Instalasi Gawat Darurat)
**Key Tables:**
- `data_triase_igd*` - Triage system
- `catatan_observasi_igd` - Observation notes

**Features:**
- Triage system (5 levels: skala1-5)
- Primary/secondary survey
- Observation tracking
- Emergency procedures
- Resuscitation documentation
- Rapid response team activation
- Emergency to inpatient admission
- Emergency BPJS SEP

### 2.7 Pharmacy (Farmasi)
**Location:** Multiple DlgApotek* files, webapps/farmasi

**Features:**
- Drug master file (databarang/jenisobat)
- Inventory management (stok_obat_bhp)
- Prescription processing
- Drug dispensing
- Compounding (obat_racikan)
- Drug interactions checking
- Stock management
- Expiry tracking
- Purchase orders (pemesanan)
- Goods received (terima_obat)
- Returns (retur)
- Batch number tracking
- Drug pricing (HPP, HNA)
- BPJS e-Claim integration for pharmacy
- Drug information (pelayanan_informasi_obat)
- Pharmaceutical care (konseling_farmasi)

**Key Tables:**
- `databarang` - Drug master
- `stok_obat_bhp` - Inventory
- `resep_dokter` - Prescriptions
- `detail_pemberian_obat` - Drug administration
- `pengeluaran_obat_bhp` - Stock dispensing
- `jns_perawatan` - Drug procedures for billing

### 2.8 Laboratory
**Location:** `/src/` DlgPeriksaLaboratorium*, DlgPeriksaLaboratoriumMB, DlgPeriksaLaboratoriumPA

**Features:**
- Test ordering (permintaan_pemeriksaan_lab)
- Sample tracking
- Worklist management
- Result entry (hasil_pemeriksaan_lab)
- Quality control
- Critical value alerts
- Pathology anatomy support (PA)
- Microbiology support
- Lab report printing
- Integration with lab equipment (bridging)
- BPJS e-Claim lab integration
- Reference ranges by age/gender
- Unit conversion

**Key Tables:**
- `jns_perawatan_lab` - Lab test catalog
- `permintaan_pemeriksaan_lab` - Test orders
- `permintaan_lab` - Lab requests
- `detail_periksa_lab` - Test results
- `template_laboratorium` - Result templates

**Sub-modules:**
- Clinical pathology (LabPK)
- Pathology anatomy (LabMB)
- Microbiology (LabPA)

### 2.9 Radiology
**Location:** DlgPeriksaRadiologi*, webapps/radiologi

**Features:**
- Examination ordering
- Modality worklist
- DICOM integration (Orthanc PACS)
- Image capture/storage
- Report generation
- X-ray, CT, MRI, USG support
- Result documentation
- Radiologist reporting
- Film printing
- CD burning
- BPJS e-Claim radiology integration
- Integration with CareStream, FUJI systems

**Key Tables:**
- `jns_perawatan_radiologi` - Procedure catalog
- `periksa_radiologi` - Examinations
- `hasil_radiologi` - Results
- `gambar_radiologi` - Image references
- `modality` - Equipment list

### 2.10 Surgery (OK - Operasi)
**Features:**
- Surgery scheduling (jadwal_operasi)
- Operating room management
- Pre-operative assessment (checklist_pre_operasi)
- Post-operative care (checklist_post_operasi)
- Anesthesia records
- Surgical team assignment
- Instrument counting
- Surgical safety checklist
- Time out/Sign out procedures
- Surgery billing (jns_perawatan_inap)

**Key Tables:**
- `booking_operasi` - Surgery schedule
- `pakai_ok` - OR resource usage
- `biaya_operasi` - OR costs
- `obatbhp_ok` - OR supplies

### 2.11 Finance & Billing (Keuangan)
**Location:** `/src/keuangan/` (335 files)

**Features:**
- Patient billing (billing)
- Itemized charges
- Payment processing
- Insurance billing (piutang)
- Accounts receivable
- Payment method management
- Bank integration
- Invoice generation
- Receipt printing
- Credit management
- Write-offs
- Refunds
- Deposit management
- Financial reporting

**Key Tables:**
- `billing` - Bill headers
- `detail_billing` - Bill line items
- `piutang_pasien` - Insurance claims
- `bayar_piutang` - Payment tracking
- `jurnal` - Financial journal
- `rekening` - Chart of accounts

### 2.12 Accounting
**Features:**
- Chart of accounts (rekening)
- Journal entries (jurnal)
- General ledger
- Trial balance
- Income statement
- Balance sheet
- Cash management
- Bank reconciliation
- Accounts payable
- Accounts receivable
- Fixed assets (inventaris)
- Inventory valuation
- Cost accounting
- Budget management

### 2.13 Inventory Management
**Location:** `/src/inventory/` (237 files)

**Features:**
- Item master (masterbarang)
- Purchase orders (pemesanan_non_medis)
- Goods received (terima_non_medis)
- Stock management
- Warehouse management
- Bin location tracking
- Expiry management
- Minimum stock levels
- Maximum stock levels
- Reorder points
- Stock transfers
- Stock adjustments
- Physical counts
- Supplier management
- Price lists
- Unit of measure conversion

### 2.14 Human Resources / Payroll (Kepegawaian)
**Location:** `/src/kepegawaian/` (148 files)

**Features:**
- Employee master (pegawai)
- Position management (jabatan)
- Department assignment
- Attendance tracking
- Shift scheduling
- Leave management
- Overtime tracking
- Payroll processing (penggajian)
- Salary calculation
- Deductions
- Benefits
- Performance evaluation (SKP)
- Training records
- Certification tracking
- Contract management
- Pension calculations

**Key Tables:**
- `pegawai` - Employee master
- `jabatan` - Positions
- `jadwal_pegawai` - Schedules
- `penggajian` - Payroll
- `kinerja_pegawai` - Performance

### 2.15 Medical Support Services

**Nutrition (Dapur/Gizi):**
- Diet ordering
- Meal planning
- Food production
- Patient meal delivery
- Nutritional assessment
- Diet education (asuhan_gizi)

**Medical Records (Rekam Medis):**
- Record filing
- Record retrieval
- Record tracking
- Loaner files
- Statistics (RL reports)
- ICD-10 coding
- ICD-9-CM procedure coding

**Laundry & Linen:**
- Linen inventory
- Soiled linen collection
- Clean linen distribution
- Laundry service tracking
- Linen sterilization

**Sterile Supply (CSSD):**
- Instrument sterilization
- Sterile storage
- Distribution
- Quality control
- Package tracking

**Blood Bank (UTD - Unit Transfusi Darah):**
- Donor registration
- Blood collection
- Blood typing
- Cross-matching
- Component preparation
- Blood issuance
- Transfusion monitoring
- Adverse reaction tracking
- Blood inventory

**Morgue:**
- Body storage
- Family identification
- Autopsy coordination
- Body release
- Death documentation

### 2.16 Facilities Management

**Parking (Parkir):**
- Vehicle entry/exit
- Parking fees
- Parking attendant management
- Parking space tracking

**Library (Perpustakaan):**
- Book catalog
- Borrowing/lending
- Overdue tracking
- Reservation system

**Asset Management (Inventaris):**
- Asset registration
- Asset tracking
- Depreciation
- Maintenance scheduling
- Asset disposal

**Storehouse (Gudang):**
- General inventory
- Non-medical supplies
- Office supplies
- Equipment maintenance

### 2.17 Additional Features

**Patient Education:**
- Education materials
- Education tracking
- Family education

**Complaint Management:**
- Patient complaints
- Feedback tracking
- Resolution tracking
- Analysis

**Telemedicine:**
- (Basic support for remote consultations)

**Research:**
- Clinical research data collection
- Research subject tracking

**Quality Improvement:**
- Audit modules (multiple audit tables)
- Performance indicators
- Quality dashboards

---

## 3. Database Schema

### 3.1 Schema Overview
- **Total Tables:** 1,116 tables
- **Primary Engine:** InnoDB (relational integrity)
- **Character Set:** latin1 with latin1_swedish_ci
- **Schema Size:** 42,315 lines of SQL

### 3.2 Key Master Tables

**Patient Master (`pasien`):**
```sql
no_rkm_medis (PK) - Medical record number
nm_pasien - Patient name
no_ktp - National ID
jk - Gender (L/P)
tmp_lahir, tgl_lahir - Birth place/date
nm_ibu - Mother's name (for verification)
alamat - Address
gol_darah - Blood type (A,B,O,AB,-)
pekerjaan - Occupation
stts_nikah - Marital status
agama - Religion
no_tlp - Phone
umur - Age (calculated field)
pnd - Education (TS-S3)
kd_pj (FK) - Insurance payment method
no_peserta - BPJS card number
kd_kel, kd_kec, kd_kab, kd_prop - Geographic codes
email - Email
nip - For employees
suku_bangsa, bahasa_pasien, cacat_fisik - Demographics
```

**Doctor Master (`dokter`):**
```sql
kd_dokter (PK)
nm_dokter
jk
tmp_lahir
tgl_lahir
gol_drh
agama
alamat
no_tlp
kd_sps (FK) - Specialty
status - Active/inactive
stts_nikah
nm_ister
almt_ister
no_tlp_ister
kerja_ister
status_ister
```

**Polyclinic Master (`poliklinik`):**
```sql
kd_poli (PK)
nm_poli
status
registrasi
registrasi_lama
```

**Room Master (`kamar`):**
```sql
kd_kamar (PK)
bangsal (FK)
nama_kamar
trf_kamar - Room rate
status - Available/Occuped
kelas - Class (1,2,3,VVIP)
```

### 3.3 Transaction Tables

**Registration (`reg_periksa`):**
```sql
no_reg - Registration number
no_rawat (PK) - Visit number
tgl_registrasi
jam_reg
kd_dokter (FK)
no_rkm_medis (FK)
kd_poli (FK)
p_jawab - Responsible party
biaya_reg - Registration fee
stts - Status (Batal, Lama, Baru)
stts_daftar - Where registered
status_lanjut - Outpatient/Inpatient
```

**SEP Table (`bridging_sep`):**
```sql
no_sep (PK)
no_rawat (FK)
tglsep
no_rujukan - Referral number
kdppkrujukan - Referring facility
jnspelayanan - Service type (1=Inpatient, 2=Outpatient)
diagawal - Initial diagnosis (ICD-10)
kdpolitujuan - Target poly
klsrawat - Room class
lakalantas - Accident indicator (0-3)
penunjang - Support services
asesmenpelayanan - Assessment level
```

### 3.4 Indonesia-Specific Fields

**BPJS Kesehatan Integration:**
- `no_peserta` - BPJS membership number
- `kd_pj` = 'BPJ' for BPJS patients
- `bridging_sep` table stores all SEP data
- `no_sep` links visits to BPJS claims
- Diagnosis maps to ICD-10 (Indonesian adaptation)
- `kdpolitujuan` uses BPJS poly codes

**Geographic Structure:**
- `propinsi` (Province) - 34 provinces
- `kabupaten` (Regency/City) - 514 regencies
- `kecamatan` (District) - 7,000+ districts
- `kelurahan` (Village) - 83,000+ villages
- All use official BPS (Statistics Indonesia) codes

**Medical Coding:**
- ICD-10-CM (Indonesian version)
- ICD-9-CM procedures
- Local procedure codes (jns_perawatan)
- DRG codes (INA-CBG) for BPJS

**Language & Demographics:**
- `suku_bangsa` - Ethnic groups (1,300+ tribes)
- `bahasa_pasien` - Local languages (700+ languages)
- `cacat_fisik` - Disability types
- Marital status includes local categories (Janda, Duda)

**Date Format:**
- Standard Indonesian: DD-MM-YYYY
- Display format: Java SimpleDateFormat
- Storage: ISO format (YYYY-MM-DD)

**Currency (IDR - Rupiah):**
- Stored as DOUBLE/DECIMAL
- No decimal places (rupiah has no sen)
- Formatting: Rp 1.000.000 (dots as thousands separator)

---

## 4. BPJS Kesehatan Integration

### 4.1 BPJS Architecture

BPJS Kesehatan is Indonesia's national health insurance (JKN - Jaminan Kesehatan Nasional). SIMRS-Khanza has comprehensive integration.

### 4.2 BPJS API Endpoints

**VClaim API (Primary):**
```
URL: https://apijkn.bpjs-kesehatan.go.id/vclaim-rest
Cons ID: Configurable
Secret Key: Configurable
```

**Key VClaim Services:**
1. **SEP (Surat Eligibilitas Peserta) Management:**
   - Create SEP
   - Update SEP
   - Delete SEP
   - Search SEP by number
   - Search SEP by patient data

2. **Patient Eligibility Checking:**
   - Check membership status (Peserta)
   - Check eligibility by NO.KARTU
   - Check eligibility by NIK

3. **Referral (Rujukan):**
   - Get referral from FKTP (primary clinic)
   - Get referral from hospital (specialist)
   - Get referral history
   - Create referral (PCare)

4. **Diagnosis & Procedure:**
   - ICD-10 lookup
   - ICD-9-CM lookup
   - Search by code or name

5. **Facility & Provider:**
   - Hospital info
   - Poly/mapping
   - Room class mapping
   - Doctor mapping (DPJP)

6. **Claims Monitoring:**
   - Check claim status
   - Get claim history
   - Claim data inquiry

**Aplicare API (Bed Availability):**
```
URL: https://new-api.bpjs-kesehatan.go.id/aplicaresws
Purpose: Real-time bed reporting
```

**Mobile JKN API (Appointment Integration):**
```
URL: https://apijkn-dev.bpjs-kesehatan.go.id/antreanrs_dev
Purpose: Appointment queue management
```

**Mobile JKN FKTP:**
```
URL: https://apijkn-dev.bpjs-kesehatan.go.id/antreanfktp_dev
Purpose: Primary care queue integration
```

**Apotek API:**
```
URL: https://dev-soa.bpjs-kesehatan.go.id/apotek-rest
Purpose: Pharmacy e-Claim
```

**PCare API (Primary Care):**
```
URL: https://apijkn-dev.bpjs-kesehatan.go.id/pcare-rest-dev
Purpose: FKTP (primary clinic) integration
```

**iCare API (Integration Hub):**
```
URL: https://apijkn-dev.bpjs-kesehatan.go.id/ihs_dev/api/rs
Purpose: Interoperability with SATUSEHAT platform
```

### 4.3 BPJS Data Flow

```
Patient Registration
       ↓
Check BPJS Eligibility (NIK/No. Kartu)
       ↓
Create SEP (Surat Eligibilitas Peserta)
       ↓
Provide Medical Services
       ↓
Create e-Claim Data File
       ↓
Submit Claim (21 days after discharge)
       ↓
Receive Payment (via virtual account)
```

### 4.4 BPJS-Specific Data Structures

**Mapping Tables:**
- `maping_poli_bpjs` - Poly clinic mapping
- `maping_dokter_pcare` - Doctor mapping
- `maping_tindakan_pcare` - Procedure mapping
- `maping_obat_apotek_bpjs` - Drug mapping
- `maping_obat_pcare` - PCare drug mapping

**Bridging Tables:**
- `bridging_sep` - Main SEP data
- `bridging_sep_internal` - Internal SEP tracking
- `bridging_rujukan_bpjs` - Referral data
- `bridging_srb_bpjs` - Summary of bill (SRB)
- `bridging_resep_apotek_bpjs` - Pharmacy claims
- `bridging_surat_kontrol_bpjs` - Control letters
- `bridging_surat_pri_bpjs - PRI (Peresepan Isi Pasien)

**PCare Integration:**
- `pcare_pendaftaran` - PCare registration
- `pcare_kunjungan_umum` - General visits
- `pcare_kegiatan_kelompok` - Group activities
- `pcare_obat_diberikan` - Medication given

### 4.5 BPJS Authentication

**HMAC-SHA256 Signature:**
```java
String timestamp = Long.toString(GetUTCdatetimeAsString());
String data = consId + "&" + timestamp;
String signature = generateHmacSHA256Signature(data, secretKey);
```

**Headers:**
```
X-cons-id: {consId}
X-timestamp: {timestamp}
X-signature: {signature}
X-authorization: Basic {base64(username:password)}
```

**Decryption:**
- AES-128-CBC encryption
- Key: ConsId + SecretKey + Timestamp
- LZString decompression
- JSON parsing

### 4.6 e-Claim Process

**Step 1: Generate Claim File**
- Combine all bill items
- Group by diagnosis/procedure
- Calculate INA-CBG rate
- Generate JSON file

**Step 2: Validate Claim**
- Check data completeness
- Validate against BPJS rules
- Verify INA-CBG grouper result

**Step 3: Submit Claim**
- Upload through BPJS gateway
- Get claim submission ID
- Track status

**Step 4: Claim Verification**
- BPJS verifies claim
- May request clarification
- Submit additional documents if needed

**Step 5: Receive Payment**
- Credit to hospital account
- Reconcile with internal records
- Update patient accounts

### 4.7 INACBG (Indonesia Case Base Groups)

**What is INA-CBG?**
- Indonesia's DRG-like system
- Groups hospitalizations into packages
- Determines reimbursement rates
- Based on severity, procedure, age

**Implementation:**
- External INA-CBG grouper software
- Generates grouping code (e.g., A-1-23-A)
- Determines package price
- Adjusts for ICU, ventilator, etc.

**Key Tables:**
- `masterbangsal` - Ward reference
- `kamar_inap` - Room data
- `jns_perawatan_inap` - Inpatient procedures

---

## 5. Architecture Patterns

### 5.1 Overall Architecture

**Type:** Monolithic Desktop Application with Hybrid Web Components

```
┌─────────────────────────────────────────────────────────┐
│                   SIMRS-Khanza Client                   │
│                   (Java Desktop App)                    │
│  ┌──────────────┬──────────────┬──────────────────────┐ │
│  │   Swing UI   │   Business   │    Data Access      │ │
│  │  (Dlg*.java) │   Logic      │    (MySQL DB)        │ │
│  └──────────────┴──────────────┴──────────────────────┘ │
└─────────────────────────────────────────────────────────┘
         ↕ REST API (Spring Web + HttpClient)
┌─────────────────────────────────────────────────────────┐
│                   External Systems                      │
│  BPJS APIs | SATUSEHAT | Kemenkes | Other Systems       │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Module Communication

**Direct Database Access:**
- All modules connect directly to MySQL
- No ORM layer (mostly direct SQL)
- Connection pooling via Commons DBCP
- Connection parameters in `database.xml` (encrypted)

**Inter-Module Data Flow:**
```
Registration Module
    ↓ INSERT into reg_periksa
Medical Records Module
    ↓ UPDATE reg_periksa, INSERT into diagnosa_pasien
Billing Module
    ↓ INSERT into billing, detail_billing
Pharmacy Module
    ↓ INSERT into resep_dokter, pengeluaran_obat_bhp
Lab/Radiology Modules
    ↓ INSERT into respective request/result tables
```

### 5.3 Service Architecture

**Standalone Services (Java Applications):**
1. **KhanzaHMSServiceAplicare** - Bed availability reporting
2. **KhanzaHMSServiceMobileJKN** - Appointment queue sync
3. **KhanzaHMSServiceMobileJKNERM** - ER appointment queue
4. **KhanzaHMSServiceMobileJKNFKTP** - FKTP queue
5. **KhanzaHMSServicePCare** - Primary care integration
6. **KhanzaHMSServiceSIRSYankes** - Kemenkes reporting
7. **KhanzaHMSServiceSPDGT** - Specialized reporting
8. **KhanzaHMSServiceSatuSehat** - FHIR integration
9. **KhanzaHMSServiceMandiri** - Bank Mandiri payment gateway

**Queue/Antrian Applications:**
- KhanzaAntrianLoket - Reception queue
- KhanzaAntrianPoli - Poly queue
- KhanzaAntrianApotek - Pharmacy queue
- KhanzaCetakAntrianLoket - Queue ticket printing

**Supporting Applications:**
- KhanzaHMSResume - Patient summary generator
- KhanzaHMSAutoVerify - Automatic verification
- KhanzaHMSAnjungan - Patient kiosk
- KhanzaHMSAnjunganFingerPrint - Biometric kiosk
- KhanzaUpdater - Automatic update system
- KhanzaSecurity16bit - License/encryption module

### 5.4 Data Access Pattern

**Typical Data Access Flow:**
```java
// 1. Get database connection
Connection conn = koneksiDB.condb();

// 2. Create statement
Statement st = conn.createStatement();

// 3. Execute query
ResultSet rs = st.executeQuery("SELECT * FROM pasien WHERE no_rkm_medis = ?");

// 4. Process results
while(rs.next()) {
    // Extract data
}

// 5. Close resources
rs.close();
st.close();
conn.close();
```

**Connection Pooling:**
```xml
<Resource
    name="jdbc/simrs"
    auth="Container"
    type="javax.sql.DataSource"
    maxActive="100"
    maxIdle="30"
    maxWait="10000"
    username="simrs"
    password="password"
    driverClassName="com.mysql.jdbc.Driver"
    url="jdbc:mysql://localhost:3306/simrs"/>
```

### 5.5 Reporting Architecture

**JasperReports Integration:**
```
Java Application
    ↓ Parameters + Data
JasperReports Engine
    ↓ JRXML template (.jrxml)
Compiled Report (.jasper)
    ↓ Output
PDF/Excel/HTML/Print
```

**Report Storage:**
- `/report/` - JRXML and JASPER files
- Compiled during build process
- Runtime parameter binding
- Dynamic SQL based on parameters

### 5.6 Security Architecture

**Authentication:**
- Username/password stored in database
- Password hashing (bcrypt/spring-security)
- Session management
- Role-based access control

**Authorization:**
- Module-level access
- Feature-level permissions
- Data-level restrictions (e.g., only own department)

**Data Encryption:**
- Database credentials encrypted (AES)
- API credentials encrypted
- BPJS signature (HMAC-SHA256)
- Custom encryption library (KhanzaSecurity16bit)

**Audit Trail:**
- Login/logout tracking
- Data modification logging
- Financial transaction audit
- Database triggers for critical tables

### 5.7 Deployment Model

**Single-User/Small Clinic:**
- Standalone desktop application
- Local MySQL server
- Single computer

**Multi-User/Hospital:**
- Client-server architecture
- Central MySQL server
- Multiple client workstations
- Shared network resources (printers, etc.)

**Web Components:**
- Apache Tomcat for PHP/webapps
- MySQL database (shared with desktop)
- REST API endpoints
- Kiosk applications
- Mobile-friendly interfaces

**Enterprise Setup:**
```
┌────────────────────────────────────────────┐
│          Database Server (MySQL)           │
│  - simrs database (production)             │
│  - backup/replikasi (if any)              │
└────────────────────────────────────────────┘
                    ↕
┌────────────────────────────────────────────┐
│         Application Server (Tomcat)        │
│  - webapps (PHP applications)              │
│  - API endpoints                           │
│  - File storage (reports, images)          │
└────────────────────────────────────────────┘
                    ↕
┌────────────────────────────────────────────┐
│         Client Workstations                │
│  - SIMRS-Khanza.jar (desktop app)          │
│  - Shared printers                         │
│  - Barcode scanners, card readers          │
└────────────────────────────────────────────┘
```

---

## 6. Localization (Indonesian Context)

### 6.1 Language

**Primary Language:** Indonesian (Bahasa Indonesia)

**UI Language:**
- All menu items in Indonesian
- Database column names use Indonesian abbreviations
- Error messages in Indonesian
- Reports in Indonesian

**Examples:**
- `pasien` (patient)
- `periksa` (examine)
- `rawat inap` (inpatient care)
- `poli` (polyclinic)
- `obat` (medicine)
- `bangsal` (ward)

**Key Indonesian Abbreviations:**
- `ralan` = Rawat Jalan (outpatient)
- `ranap` = Rawat Inap (inpatient)
- `igd` = Instalasi Gawat Darurat (emergency)
- `pj` = Penjamin (guarantor/insurance)
- `rkm` = Rekam Medis (medical record)

### 6.2 Currency (IDR - Rupiah)

**Format:** Rp 1.000.000 (dots as thousands separator)

**Database Storage:**
- Data type: DOUBLE or DECIMAL
- No decimal places (sen no longer used)
- Example: 1000000 (not 1000000.00)

**Display Formatting:**
```java
NumberFormat nf = NumberFormat.getInstance(Locale.of("id", "ID"));
String formatted = "Rp " + nf.format(amount);
// Output: Rp 1.000.000
```

**Financial Tables:**
- `billing` - Bills
- `jurnal` - Journal entries
- `piutang` - Accounts receivable
- `rekening` - Chart of accounts

### 6.3 Date Format

**Indonesian Format:** DD-MM-YYYY
- Example: 12-01-2026 (January 12, 2026)

**Database Storage:** YYYY-MM-DD (ISO format)
- Example: 2026-01-12

**Display Format Options:**
- Short: 12-01-2026
- Long: 12 Januari 2026
- Full: Senin, 12 Januari 2026

**Java Date Handling:**
```java
SimpleDateFormat indoFormat = new SimpleDateFormat("dd-MM-yyyy");
SimpleDateFormat dbFormat = new SimpleDateFormat("yyyy-MM-dd");
```

### 6.4 Medical Coding Systems

**Diagnosis Coding (ICD-10-CM):**
- International Classification of Diseases
- Indonesian adaptation
- 3-character codes (A00-Z99)
- Used in `diagnosa_pasien` table

**Procedure Coding (ICD-9-CM):**
- International Classification of Procedures
- Indonesian adaptation
- Used for medical procedures
- Maps to `jns_perawatan` table

**INA-CBG Coding:**
- Indonesia Case Base Groups
- DRG-like system for BPJS
- Package codes (e.g., A-1-23-A)
- Determines reimbursement

**Local Procedure Codes:**
- Hospital-specific codes
- `jns_perawatan` table
- Maps to billing codes
- Prices per class (1, 2, 3, VVIP)

### 6.5 Geographic Structure

**Indonesian Administrative Divisions:**

1. **Provinsi** (Province) - 34 provinces
   - Code: 2 digits (01-34, 11-94 for special regions)
   - Table: `propinsi`

2. **Kabupaten/Kota** (Regency/City) - 514 total
   - Code: 4 digits (first 2 = province)
   - Table: `kabupaten`
   - Types: Kabupaten (regency) or Kota (city)

3. **Kecamatan** (District) - 7,000+
   - Code: 6 digits (first 4 = regency)
   - Table: `kecamatan`

4. **Kelurahan** (Village) - 83,000+
   - Code: 10 digits (first 6 = district)
   - Table: `kelurahan`

**Usage:**
- Patient address (`pasien` table)
- Hospital location
- BPJS reporting
- SATUSEHAT integration
- Statistics reporting

### 6.6 Demographics & Cultural Considerations

**Ethnic Groups (`suku_bangsa`):**
- 1,300+ ethnic groups in Indonesia
- Major groups: Javanese, Sundanese, Malay, Batak, etc.
- Important for cultural sensitivity in care

**Languages (`bahasa_pasien`):**
- 700+ local languages
- Official: Bahasa Indonesia
- Regional languages important for communication
- Affects informed consent process

**Religion (`agama`):**
- Official religions in Indonesia:
  - Islam
  - Kristen (Protestant)
  - Katolik (Catholic)
  - Hindu
  - Buddha
  - Konghucu (Confucianism)
- Affects dietary requirements, burial practices

**Marital Status (`stts_nikah`):**
- BELUM MENIKAH (Never married)
- MENIKAH (Married)
- JANDA (Widow)
- DUDA (Widower)
- JOMBLO (Single/Unmarried - informal)
- Affects decision-making, insurance

**Education (`pnd` - Pendidikan):**
- TS (Tidak Sekolah - No school)
- TK (Taman Kanak-kanak - Kindergarten)
- SD (Primary school)
- SMP (Junior high)
- SMA (Senior high)
- SLTA/SEDERAJAT (High school equivalent)
- D1-D4 (Diploma)
- S1-S3 (Bachelor-Master-Doctorate)
- Affects health literacy

### 6.7 Indonesia-Specific Medical Practices

**Traditional Medicine:**
- Integration with traditional practices
- Documentation of herbal medicines
- Cultural healing practices

**Family Involvement:**
- Family decision-makers (`keluarga`)
- Family presence during care
- Family as caregivers

**Referral Patterns:**
- Puskesmas (primary health center)
- FKTP (Primary care clinic)
- RS Type D (small hospital)
- RS Type C (medium)
- RS Type B (large)
- RS Type A (teaching hospital)
- Referral chain: Puskesmas → RS Tipe C → RS Tipe B → RS Tipe A

### 6.8 Regulatory Compliance

**Kemenkes (Ministry of Health) Reporting:**
- SIRS (Sistem Informasi Rumah Sakit Terpadu)
- SISRUTE (Sistem Rujukan Terintegrasi)
- SITT (Sistem Informasi Tuberkulosis Terpadu)
- COVID-19 reporting

**BPJS Kesehatan Requirements:**
- SEP creation rules
- e-Claim submission
- Bed reporting (Aplicare)
- Mobile JKN integration
- SATUSEHAT FHIR integration

**Medical Records Standards:**
- Medical record completeness
- Retention periods (25+ years)
- Privacy regulations
- Information release procedures

**Price Regulation:**
- INA-CBG package rates
- Maximum prices for services
- Professional fee standards
- Drug price transparency

---

## 7. SATUSEHAT Integration (FHIR)

### 7.1 Overview

SATUSEHAT is Indonesia's national health data exchange platform based on FHIR (Fast Healthcare Interoperability Resources).

**API Endpoints:**
```
Auth: https://api-satusehat-dev.dto.kemkes.go.id/oauth2/v1
FHIR: https://api-satusehat-dev.dto.kemkes.go.id/fhir-r4/v1
```

### 7.2 FHIR Resources Implemented

**Patient Resource:**
- Create/update patient records
- NIK as identifier
- Demographic data synchronization

**Encounter Resource:**
- Hospital visit documentation
- Outpatient encounters
- Inpatient admissions
- Emergency visits

**Condition Resource:**
- Diagnosis documentation
- Problem list
- Health concerns

**Observation Resource:**
- Lab results
- Vital signs
- Clinical observations
- Lab PK (pathology klinis)
- Radiology results

**MedicationRequest Resource:**
- Prescription data
- Medication orders
- Dispensing records

**DiagnosticReport Resource:**
- Lab reports
- Radiology reports
- Consultation reports

**Immunization Resource:**
- Vaccination records
- COVID-19 vaccines
- Routine immunizations

**Organization Resource:**
- Hospital/facility data
- Department information
- Provider organizations

### 7.3 SATUSEHAT Tables

**Mapping Tables:**
- `DataSatuSehatCondition` - Condition mapping
- `DataSatuSehatEncounter` - Encounter mapping
- `DataSatuSehatDiagnosticReportLabPK` - Lab reports
- `DataSatuSehatImunisasi` - Immunization mapping
- `DataSatuSehatClinicalImpression` - Clinical impressions

**Location Coding:**
- PROPINSISATUSEHAT: Province code
- KABUPATENSATUSEHAT: Regency code
- KECAMATANSATUSEHAT: District code
- KELURAHANSATUSEHAT: Village code
- KODEPOSSATUSEHAT: Postal code

---

## 8. Key Insights for New SIMRS Development

### 8.1 Strengths of SIMRS-Khanza

1. **Comprehensive Coverage:**
   - Covers all hospital departments
   - BPJS integration is mature
   - Handles Indonesia-specific requirements

2. **Battle-Tested:**
   - Used in hundreds of Indonesian hospitals
   - Handles real-world edge cases
   - Proven BPJS integration

3. **Rich Feature Set:**
   - Medical records depth
   - Financial system completeness
   - Support services coverage

4. **Active Development:**
   - Regular updates
   - New integrations (SATUSEHAT)
   - Community support

### 8.2 Limitations & Challenges

1. **Technology Stack:**
   - Java Swing is dated
   - Desktop-only primary interface
   - Limited mobile support
   - Monolithic architecture

2. **Code Quality:**
   - Direct SQL (no ORM abstraction)
   - Mixed concerns (UI + business + data)
   - Large dialog classes
   - Limited test coverage

3. **Database Schema:**
   - 1,116 tables (very complex)
   - Some redundancy
   - Inconsistent naming
   - latin1 charset (limited for multi-language)

4. **Deployment:**
   - Client-server model (not cloud-native)
   - Requires local installation
   - Update management complexity
   - Hardware dependencies

### 8.3 Lessons for New Implementation

**Architecture:**
- Consider modern web/mobile architecture
- Microservices for scalability
- API-first design
- Cloud-native deployment

**Database Design:**
- Simplify schema (fewer tables)
- Use UTF-8 for international support
- Consistent naming conventions
- Proper indexing strategy
- Partitioning for large tables

**Technology Stack:**
- Modern web framework (React/Vue/Angular)
- REST/GraphQL APIs
- Mobile app (React Native/Flutter)
- Container deployment (Docker/Kubernetes)
- PostgreSQL or MySQL 8.0+

**BPJS Integration:**
- Reuse authentication patterns
- Implement all BPJS APIs
- Robust error handling
- Async claim submission
- Comprehensive logging

**User Experience:**
- Modern, intuitive UI
- Responsive design
- Accessibility features
- Offline capabilities
- Performance optimization

---

## 9. Module Reference

### 9.1 Complete Module List

| Module | Directory | Purpose |
|--------|-----------|---------|
| simrskhanza | /src/simrskhanza/ | Main application (137 files) |
| rekammedis | /src/rekammedis/ | Medical records (472 files) |
| keuangan | /src/keuangan/ | Finance & billing (335 files) |
| kepegawaian | /src/kepegawaian/ | HR & payroll (148 files) |
| laporan | /src/laporan/ | Reports (216 files) |
| inventory | /src/inventory/ | Inventory management (237 files) |
| bridging | /src/bridging/ | External integrations (463 files) |
| setting | /src/setting/ | System configuration (68 files) |
| fungsi | /src/fungsi/ | Utilities & helpers (20 files) |
| dapur | /src/dapur/ | Nutrition/kitchen (73 files) |
| ipsrs | /src/ipsrs/ | Sterile supply/CSSD (89 files) |
| grafikanalisa | /src/grafikanalisa/ | Analytics dashboards (263 files) |
| informasi | /src/informasi/ | Information display (24 files) |
| inventaris | /src/inventaris/ | Fixed assets (72 files) |
| parkir | /src/parkir/ | Parking management (8 files) |
| perpustakaan | /src/perpustakaan/ | Library (34 files) |
| permintaan | /src/permintaan/ | Request management (34 files) |
| picture | /src/picture/ | Imaging/photo (232 files) |
| surat | /src/surat/ | Letter/document (80 files) |
| toko | /src/toko/ | Retail/shop (71 files) |
| tranfusidarah | /src/tranfusidarah/ | Blood bank (22 files) |
| viabarcode | /src/viabarcode/ | Barcode operations (50 files) |
| widget | /src/widget/ | UI widgets (37 files) |
| smsui | /src/smsui/ | SMS interface (13 files) |
| smsservice | /src/smsservice/ | SMS service (3 files) |
| smsobj | /src/smsobj/ | SMS objects (3 files) |
| smsimage | /src/smsimage/ | SMS images (15 files) |
| ziscsr | /src/ziscsr/ | CSR/CSR (32 files) |
| restore | /src/restore/ | Data restore (38 files) |

### 9.2 Web Applications (webapps/)

**Antrian (Queue) Systems:**
- antrian.php - Main queue display
- antrianfarmasi.php - Pharmacy queue
- antrianlaborat.php - Lab queue
- antrianradiologi.php - Radiology queue
- antrianmobilejkn.php - BPJS queue

**Medical Result Display:**
- hasilpemeriksaanecho/ - Echocardiography
- hasilpemeriksaanekg/ - ECG
- hasilpemeriksaanusg/ - Ultrasound
- hasilpemeriksaanendoskopifaringlaring/ - ENT endoscopy
- hasilpemeriksaanoct/ - OCT (ophthalmology)
- hasilpemeriksaanslitlamp/ - Slit lamp
- hasilpemeriksaantreadmill/ - Treadmill test

**Specialized Modules:**
- billing - Billing portal
- medrec - Medical record portal
- radiologi - Radiology images/reports
- inacbg - DRG grouper interface
- ebook - Digital library
- phpqrcode - QR code generation

**Consent Forms & Documents:**
- pernyataanumum - General consent
- persetujuanrawatinap - Admission consent
- persetujuantindakan - Procedure consent
- pernyataanmemilihdpjp - Doctor choice
- penolakananjuranmedis - Refusal of treatment
- penundaanpelayanan - Delayed care
- pelaksanaanedukasi - Patient education
- pengkajianrestrain - Restraint assessment
- perencanaanpemulangan - Discharge planning

### 9.3 Service Applications

| Service | Purpose |
|---------|---------|
| KhanzaHMSServiceAplicare | Bed reporting to BPJS |
| KhanzaHMSServiceMobileJKN | Appointment queue sync |
| KhanzaHMSServiceMobileJKNERM | ER queue |
| KhanzaHMSServiceMobileJKNFKTP | Primary care queue |
| KhanzaHMSServicePCare | Primary care integration |
| KhanzaHMSServiceSIRSYankes | Kemenkes reporting |
| KhanzaHMSServiceSPDGT | Special reporting |
| KhanzaHMSServiceSatuSehat | FHIR/SATUSEHAT |
| KhanzaHMSServiceMandiri | Bank payment gateway |
| KhanzaAntrianLoket | Reception queue |
| KhanzaAntrianPoli | Poly queue |
| KhanzaAntrianApotek | Pharmacy queue |
| KhanzaCetakAntrianLoket | Queue tickets |
| KhanzaHMSResume | Patient summaries |
| KhanzaHMSAutoVerify | Auto-verification |
| KhanzaHMSAnjungan | Patient kiosk |
| KhanzaHMSAnjunganFingerPrint | Biometric kiosk |
| KhanzaUpdater | Auto-update system |
| KhanzaSecurity16bit | License/encryption |

---

## 10. Database Entity Relationships

### 10.1 Core Registration Flow

```
pasien (patient)
    ↓ 1:N
reg_periksa (visit registration)
    ↓ 1:N
├── diagnosa_pasien (diagnoses)
├── proceduresrawat (procedures)
├── resep_dokter (prescriptions)
├── permintaan_pemeriksaan_lab (lab orders)
├── permintaan_radiologi (radiology orders)
└── billing (bills)
    ↓ 1:N
    detail_billing (bill items)
```

### 10.2 BPJS Integration Flow

```
pasien (with no_peserta)
    ↓
reg_periksa (with kd_pj='BPJ')
    ↓
bridging_sep (SEP data)
    ↓ 1:N
├── bridging_rujukan_bpjs (referrals)
├── bridging_srb_bpjs (summary of bill)
├── bridging_resep_apotek_bpjs (pharmacy)
└── pcare_* (primary care data)
```

### 10.3 Inpatient Flow

```
reg_periksa (with status_lanjut='Ranap')
    ↓ 1:N
pasien_bangsal (room assignments)
    ↓ N:1
kamar (bed/room)
    ↓ N:1
bangsal (ward/unit)
    ↓ 1:N
billing (room charges, services)
```

---

## 11. Conclusion & Recommendations

### 11.1 Summary

SIMRS-Khanza is a mature, comprehensive Hospital Management Information System specifically designed for Indonesian healthcare facilities. Its greatest strength lies in its deep integration with BPJS Kesehatan and coverage of Indonesia-specific healthcare requirements.

**Key Statistics:**
- 2,033 Java source files
- 1,116 database tables
- 32 major functional modules
- 11 BPJS/Kemenkes API integrations
- 2,129 web application files
- Full Indonesian localization

### 11.2 Strengths

1. **Domain Expertise:** Deep understanding of Indonesian healthcare
2. **BPJS Mastery:** Comprehensive BPJS integration across all APIs
3. **Completeness:** Covers all hospital departments comprehensively
4. **Proven:** Battle-tested in real Indonesian hospitals
5. **Active:** Regular updates and new integrations

### 11.3 Areas for Modernization

1. **Architecture:** Move from desktop-first to web/mobile-first
2. **Technology:** Modernize tech stack (current: Java Swing, Java 8)
3. **Database:** Simplify schema, improve indexing, use UTF-8
4. **UX/UI:** Modern, responsive user interface
5. **DevOps:** Containerization, CI/CD, cloud deployment
6. **Testing:** Add automated testing
7. **Documentation:** API documentation, deployment guides

### 11.4 Recommendations for New Implementation

**Keep:**
- BPJS integration patterns (battle-tested)
- Database structure concepts (not exact schema)
- Medical workflows (Indonesian standards)
- Feature completeness
- Localization approach

**Modernize:**
- Use web/mobile technologies
- API-first architecture
- Microservices for scalability
- Modern database design principles
- DevOps best practices
- Security best practices

**Add:**
- Mobile apps for patients/staff
- Telemedicine capabilities
- AI/ML for decision support
- Advanced analytics
- Interoperability standards (HL7 FHIR)
- Cloud deployment options

### 11.5 Final Notes

SIMRS-Khanza serves as an excellent reference implementation for Indonesian hospital systems. Its deep BPJS integration and comprehensive feature coverage provide valuable insights for building a modern SIMRS. However, a new implementation should leverage modern technologies and architectural patterns while maintaining the domain expertise and BPJS integration patterns proven by SIMRS-Khanza.

---

## Appendix A: Key File Locations

**Main Application:**
- `/tmp/SIMRS-Khanza/src/simrskhanza/SIMRSKhanza.java` - Entry point
- `/tmp/SIMRS-Khanza/src/simrskhanza/frmUtama.java` - Main form
- `/tmp/SIMRS-Khanza/build.xml` - Build script

**Database:**
- `/tmp/SIMRS-Khanza/sik.sql` - Complete schema (42,315 lines)

**Configuration:**
- `/tmp/SIMRS-Khanza/setting/database.xml` - Database & API config

**BPJS Integration:**
- `/tmp/SIMRS-Khanza/src/bridging/ApiBPJS.java` - BPJS API client
- `/tmp/SIMRS-Khanza/src/bridging/` - All bridging modules

**Web Apps:**
- `/tmp/SIMRS-Khanza/webapps/` - PHP applications

---

## Appendix B: External API References

**BPJS APIs:**
- VClaim: https://apijkn.bpjs-kesehatan.go.id/vclaim-rest
- Aplicare: https://new-api.bpjs-kesehatan.go.id/aplicaresws
- Mobile JKN: https://apijkn.bpjs-kesehatan.go.id/antreanrs
- PCare: https://apijkn.bpjs-kesehatan.go.id/pcare-rest
- e-Claim: https://dvlp.bpjs-kesehatan.go.id/eRekamMedis

**Kemenkes APIs:**
- SISRUTE: https://api.sisrute.kemkes.go.id
- SIRS: https://sirs.kemkes.go.id
- SITT: http://sirs.yankes.kemkes.go.id/sirsservice

**SATUSEHAT:**
- Auth: https://api-satusehat-dev.dto.kemkes.go.id/oauth2/v1
- FHIR: https://api-satusehat-dev.dto.kemkes.go.id/fhir-r4/v1

---

**Document Version:** 1.0
**Analysis Date:** January 12, 2026
**Source:** SIMRS-Khanza Repository (https://github.com/mas-elkhanza/SIMRS-Khanza)
**Analyzed By:** Claude Code Research Agent

