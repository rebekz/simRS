# BPJS VClaim API Integration

This module provides integration with the BPJS (Badan Penyelenggara Jaminan Sosial) VClaim API for Indonesian national health insurance.

## Overview

BPJS VClaim API allows healthcare providers to:
- Check patient eligibility by card number or NIK
- Create and manage SEP (Surat Eligibilitas Peserta) letters
- Access reference data (polyclinics, facilities, diagnoses, doctors)
- Verify patient insurance status

## Configuration

Add the following environment variables to your `.env` file:

```bash
# BPJS VClaim API Credentials
BPJS_CONSUMER_ID=your_consumer_id_here
BPJS_CONSUMER_SECRET=your_secret_key_here
BPJS_USER_KEY=your_user_key_here  # Optional, for new API
BPJS_SERVICE_NAME=SIMRS  # Optional, defaults to SIMRS

# BPJS API URLs (configured by default)
BPJS_API_URL=https://apijkn.bpjs-kesehatan.go.id/vclaim-rest
```

## File Structure

```
backend/app/
├── services/
│   ├── __init__.py              # Services module initialization
│   └── bpjs_vclaim.py           # BPJS VClaim API client (603 lines)
├── schemas/
│   └── bpjs.py                  # BPJS API schemas (242 lines)
├── core/
│   └── config.py                # Updated with BPJS settings
└── scripts/
    └── demo_bpjs_vclaim.py      # Demonstration script
```

## Usage

### Basic Usage

```python
from app.services.bpjs_vclaim import BPJSVClaimClient

async with BPJSVClaimClient() as client:
    # Check eligibility by card number
    result = await client.check_eligibility_by_card(
        card_number="0001234567890",
        sep_date="2026-01-14"
    )
    print(result)
```

### Check Eligibility

```python
# By BPJS card number
await client.check_eligibility_by_card(
    card_number="0001234567890",
    sep_date="2026-01-14"
)

# By NIK (Indonesian ID number)
await client.check_eligibility_by_nik(
    nik="1234567890123456",
    sep_date="2026-01-14"
)
```

### Create SEP (Surat Eligibilitas Peserta)

```python
sep_data = {
    "noKartu": "0001234567890",
    "tglSEP": "2026-01-14",
    "ppkPelayanan": "0123456",
    "jnsPelayanan": "RJ",  # RJ = Rawat Jalan, RI = Rawat Inap
    "klsRawat": "3",
    "noMR": "MR-2026-00001",
    "diagAwal": "A00",  # ICD-10 code
    "poliTujuan": "INT",
    "user": "admin"
}

result = await client.create_sep(sep_data)
```

### Get Reference Data

```python
# Get polyclinic list
await client.get_polyclinic_list(start=0, limit=10)

# Get diagnosis by code
await client.get_diagnosis_by_code("A00")

# Get facility by code
await client.get_facility_by_code("0123456")

# Get doctor list
await client.get_doctor_list(
    ppk_code="0123456",
    polyclinic_code="INT",
    start=0,
    limit=10
)
```

### Delete SEP

```python
await client.delete_sep(
    sep_number="0001R0010016V000001",
    user="admin"
)
```

## Authentication

The BPJS VClaim API uses HMAC-SHA256 signature-based authentication:

1. **X-cons-id**: Consumer ID
2. **X-timestamp**: Current timestamp in UTC
3. **X-signature**: HMAC-SHA256(cons_id + timestamp, secret_key)
4. **X-user-key**: User key (optional, for new API)

The client handles authentication automatically. You can inspect generated headers:

```python
client = BPJSVClaimClient()
timestamp = client._generate_timestamp()
signature = client._generate_signature(timestamp)
```

## Error Handling

All API methods raise `BPJSVClaimError` on failure:

```python
from app.services.bpjs_vclaim import BPJSVClaimClient, BPJSVClaimError

try:
    result = await client.check_eligibility_by_card("0001234567890", "2026-01-14")
except BPJSVClaimError as e:
    print(f"Error: {e.message}")
    print(f"Code: {e.code}")
    print(f"Details: {e.details}")
```

## API Endpoints

The client supports the following BPJS VClaim endpoints:

### Eligibility
- `GET /Peserta/nokartu/{cardNumber}/tglSEP/{date}` - Check by card number
- `GET /Peserta/nik/{nik}/tglSEP/{date}` - Check by NIK

### SEP Management
- `POST /SEP/create` - Create new SEP
- `DELETE /SEP/{sepNumber}` - Delete SEP
- `PUT /SEP/2.0/update` - Update SEP
- `GET /SEP/{sepNumber}` - Get SEP by number

### Reference Data
- `GET /referensi/poli/{start}/{limit}` - List polyclinics
- `GET /referensi/poli/{code}` - Get polyclinic by code
- `GET /referensi/faskes/{start}/{limit}` - List facilities
- `GET /referensi/faskes/{code}` - Get facility by code
- `GET /referensi/diagnosa/{start}/{limit}` - List diagnoses
- `GET /referensi/diagnosa/{code}` - Get diagnosis by code
- `GET /referensi/dokter/{ppk}/{poli}/{start}/{limit}` - List doctors
- `GET /referensi/kelasrawat` - List room classes
- `GET /referensi/kamar/{ppk}/{start}/{limit}` - List facility rooms

## Testing

Run the demonstration script to see the client in action:

```bash
cd backend
python app/scripts/demo_bpjs_vclaim.py
```

Note: The demo will fail without valid BPJS credentials, but shows the API call patterns.

## Dependencies

- `httpx>=0.25.2` - Async HTTP client
- `pydantic>=2.5.2` - Data validation
- `python-dateutil` - Date handling

## Schemas

The following Pydantic schemas are defined in `app/schemas/bpjs.py`:

### Configuration
- `BPJSConfig` - BPJS API configuration

### Eligibility
- `BPJSEligibilityRequest` - Eligibility check request
- `BPJSEligibilityResponse` - Eligibility check response
- `BPJSPesertaInfo` - Participant information

### SEP
- `BPJSSEPCreateRequest` - SEP creation request
- `BPJSSEPCreateResponse` - SEP creation response
- `BPJSSEPDeleteRequest` - SEP deletion request
- `BPJSSEPDeleteResponse` - SEP deletion response

### Reference Data
- `BPJSPoliclinicListResponse` - Polyclinic list response
- `BPJSFacilityListResponse` - Facility list response
- `BPJSDiagnosisListResponse` - Diagnosis list response
- `BPJSDoctorListResponse` - Doctor list response

### Error Handling
- `BPJSErrorResponse` - API error response

## Best Practices

1. **Use async context manager**: Always use `async with BPJSVClaimClient() as client:` to ensure proper resource cleanup

2. **Handle errors**: Wrap API calls in try-except blocks to handle `BPJSVClaimError`

3. **Validate dates**: Ensure SEP dates are in the correct format (YYYY-MM-DD) and not in the future

4. **Cache reference data**: Reference data (polyclinics, diagnoses, etc.) rarely changes - cache appropriately

5. **Log API calls**: The client includes logging for debugging and monitoring

6. **Set timeouts**: Default timeout is 30 seconds, configurable via httpx.Timeout

## API Documentation

Official BPJS VClaim API documentation:
- Production: https://apijkn.bpjs-kesehatan.go.id/vclaim-rest
- Documentation: Available from BPJS Kesehatan developer portal

## Support

For issues related to:
- **BPJS API**: Contact BPJS Kesehatan support
- **This integration**: Check the demo script and source code documentation
