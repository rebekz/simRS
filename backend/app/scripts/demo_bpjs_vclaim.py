"""BPJS VClaim API Client Demonstration Script.

This script demonstrates how to use the BPJS VClaim client to interact
with the BPJS API for checking eligibility and managing SEP (Surat Eligibilitas Peserta).

NOTE: This is a demonstration script. Set your BPJS credentials in environment variables:
- BPJS_CONSUMER_ID: Your BPJS consumer ID
- BPJS_CONSUMER_SECRET: Your BPJS secret key
- BPJS_USER_KEY: Your BPJS user key (optional)

Usage:
    python app/scripts/demo_bpjs_vclaim.py
"""
import asyncio
import sys
from datetime import date, datetime
from pathlib import Path

# Add the parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.bpjs_vclaim import BPJSVClaimClient, BPJSVClaimError
from app.core.config import settings


async def demo_check_credentials():
    """Check if BPJS credentials are configured."""
    print("\n" + "="*60)
    print("BPJS VClaim Configuration Check")
    print("="*60)

    if not settings.BPJS_CONSUMER_ID or not settings.BPJS_CONSUMER_SECRET:
        print("\n⚠️  WARNING: BPJS credentials not configured!")
        print("\nPlease set the following environment variables:")
        print("  - BPJS_CONSUMER_ID")
        print("  - BPJS_CONSUMER_SECRET")
        print("  - BPJS_USER_KEY (optional)")
        return False

    print(f"\n✓ BPJS Consumer ID: {settings.BPJS_CONSUMER_ID}")
    print(f"✓ BPJS Secret Key: {'*' * len(settings.BPJS_CONSUMER_SECRET)}")
    print(f"✓ BPJS User Key: {settings.BPJS_USER_KEY or 'Not set'}")
    print(f"✓ BPJS API URL: {settings.BPJS_API_URL}")
    return True


async def demo_check_eligibility_by_card(client: BPJSVClaimClient):
    """Demonstrate checking eligibility by card number."""
    print("\n" + "="*60)
    print("Demo: Check Eligibility by Card Number")
    print("="*60)

    # Example card number (replace with real BPJS card number)
    card_number = "0001234567890"  # 13-digit BPJS card number
    sep_date = date.today().strftime("%Y-%m-%d")

    print(f"\nChecking eligibility for card: {card_number}")
    print(f"SEP Date: {sep_date}")

    try:
        result = await client.check_eligibility_by_card(card_number, sep_date)
        print("\n✓ Eligibility check successful!")
        print(f"Response: {result}")
    except BPJSVClaimError as e:
        print(f"\n✗ Error: {e.message}")
        if e.code:
            print(f"Code: {e.code}")


async def demo_check_eligibility_by_nik(client: BPJSVClaimClient):
    """Demonstrate checking eligibility by NIK."""
    print("\n" + "="*60)
    print("Demo: Check Eligibility by NIK")
    print("="*60)

    # Example NIK (replace with real Indonesian ID number)
    nik = "1234567890123456"  # 16-digit Indonesian ID number
    sep_date = date.today().strftime("%Y-%m-%d")

    print(f"\nChecking eligibility for NIK: {nik}")
    print(f"SEP Date: {sep_date}")

    try:
        result = await client.check_eligibility_by_nik(nik, sep_date)
        print("\n✓ Eligibility check successful!")
        print(f"Response: {result}")
    except BPJSVClaimError as e:
        print(f"\n✗ Error: {e.message}")
        if e.code:
            print(f"Code: {e.code}")


async def demo_create_sep(client: BPJSVClaimClient):
    """Demonstrate creating a SEP."""
    print("\n" + "="*60)
    print("Demo: Create SEP (Surat Eligibilitas Peserta)")
    print("="*60)

    sep_data = {
        "noKartu": "0001234567890",
        "tglSEP": date.today().strftime("%Y-%m-%d"),
        "ppkPelayanan": "0123456",  # Healthcare facility code
        "jnsPelayanan": "RJ",  # RJ = Rawat Jalan (Outpatient)
        "klsRawat": "3",  # Class 3
        "noMR": "MR-2026-00001",  # Medical record number
        "diagAwal": "A00",  # ICD-10 diagnosis code
        "poliTujuan": "INT",  # Polyclinic code (Internal Medicine)
        "eksekutif": "0",  # Not executive
        "user": "admin",
    }

    print(f"\nCreating SEP with data:")
    for key, value in sep_data.items():
        print(f"  {key}: {value}")

    try:
        result = await client.create_sep(sep_data)
        print("\n✓ SEP creation successful!")
        print(f"Response: {result}")
    except BPJSVClaimError as e:
        print(f"\n✗ Error: {e.message}")
        if e.code:
            print(f"Code: {e.code}")


async def demo_get_polyclinic_list(client: BPJSVClaimClient):
    """Demonstrate getting polyclinic list."""
    print("\n" + "="*60)
    print("Demo: Get Polyclinic List")
    print("="*60)

    print(f"\nFetching polyclinic list (first 10)...")

    try:
        result = await client.get_polyclinic_list(start=0, limit=10)
        print("\n✓ Polyclinic list retrieved successfully!")
        print(f"Response: {result}")
    except BPJSVClaimError as e:
        print(f"\n✗ Error: {e.message}")
        if e.code:
            print(f"Code: {e.code}")


async def demo_get_diagnosis_by_code(client: BPJSVClaimClient):
    """Demonstrate getting diagnosis by code."""
    print("\n" + "="*60)
    print("Demo: Get Diagnosis by Code")
    print("="*60)

    diagnosis_code = "A00"  # Cholera
    print(f"\nFetching diagnosis for code: {diagnosis_code}")

    try:
        result = await client.get_diagnosis_by_code(diagnosis_code)
        print("\n✓ Diagnosis retrieved successfully!")
        print(f"Response: {result}")
    except BPJSVClaimError as e:
        print(f"\n✗ Error: {e.message}")
        if e.code:
            print(f"Code: {e.code}")


async def demo_signature_generation(client: BPJSVClaimClient):
    """Demonstrate signature generation."""
    print("\n" + "="*60)
    print("Demo: Authentication Signature Generation")
    print("="*60)

    timestamp = client._generate_timestamp()
    signature = client._generate_signature(timestamp)

    print(f"\nConsumer ID: {client.cons_id}")
    print(f"Timestamp: {timestamp}")
    print(f"Signature: {signature}")
    print("\nThese values are used in HTTP headers:")
    print(f"  X-cons-id: {client.cons_id}")
    print(f"  X-timestamp: {timestamp}")
    print(f"  X-signature: {signature}")
    if client.user_key:
        print(f"  X-user-key: {client.user_key}")


async def main():
    """Run all demonstrations."""
    print("\n" + "="*60)
    print("BPJS VClaim API Client - Demonstration")
    print("="*60)

    # Check credentials
    has_credentials = await demo_check_credentials()
    if not has_credentials:
        print("\n⚠️  Cannot run API demos without credentials.")
        print("\nHowever, you can still see how signature generation works:")
        client = BPJSVClaimClient(
            cons_id="demo_cons_id",
            secret_key="demo_secret_key",
        )
        await demo_signature_generation(client)
        return

    # Initialize client
    print("\n" + "="*60)
    print("Initializing BPJS VClaim Client")
    print("="*60)

    async with BPJSVClaimClient() as client:
        # Show signature generation
        await demo_signature_generation(client)

        # Run API demos
        # Note: These will fail with demo credentials, but show the API call patterns

        await demo_check_eligibility_by_card(client)
        await demo_check_eligibility_by_nik(client)
        await demo_create_sep(client)
        await demo_get_polyclinic_list(client)
        await demo_get_diagnosis_by_code(client)

    print("\n" + "="*60)
    print("Demonstration Complete")
    print("="*60)
    print("\nNote: API calls may fail with demo credentials.")
    print("Update your .env file with real BPJS credentials for actual usage.")


if __name__ == "__main__":
    asyncio.run(main())
