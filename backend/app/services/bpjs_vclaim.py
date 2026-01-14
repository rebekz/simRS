"""BPJS VClaim API Client Service.

This module provides an async client for interacting with the BPJS VClaim API,
handling authentication, request signing, and common API operations.

BPJS VClaim API Reference:
- Base URL: https://apijkn.bpjs-kesehatan.go.id/vclaim-rest
- Authentication: X-cons-id, X-signature, X-timestamp headers
- Signature: HMAC-SHA256(cons_id + timestamp, secret_key)

Key Endpoints:
- GET /Peserta/nokartu/{cardNumber}/tglSEP/{date} - Check eligibility by card number
- GET /Peserta/nik/{nik}/tglSEP/{date} - Check eligibility by NIK
- POST /SEP/create - Create SEP letter
- DELETE /SEP/{sepNumber} - Delete SEP
"""
import hashlib
import hmac
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin

import httpx

from app.core.config import settings
from app.schemas.bpjs import (
    BPJSConfig,
    BPJSEligibilityRequest,
    BPJSEligibilityResponse,
    BPJSSEPCreateRequest,
    BPJSSEPCreateResponse,
    BPJSSEPDeleteRequest,
    BPJSSEPDeleteResponse,
    BPJSErrorResponse,
    BPJSPesertaInfo,
    BPJSPoliclinicListResponse,
    BPJSFacilityListResponse,
    BPJSDiagnosisListResponse,
    BPJSDoctorListResponse,
)

logger = logging.getLogger(__name__)


class BPJSVClaimError(Exception):
    """Custom exception for BPJS VClaim API errors."""

    def __init__(self, message: str, code: Optional[str] = None, details: Optional[str] = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class BPJSVClaimClient:
    """
    Async client for BPJS VClaim API integration.

    Handles authentication, request signing, and common BPJS VClaim operations.
    """

    def __init__(
        self,
        cons_id: Optional[str] = None,
        secret_key: Optional[str] = None,
        user_key: Optional[str] = None,
        api_url: Optional[str] = None,
    ):
        """
        Initialize BPJS VClaim client.

        Args:
            cons_id: BPJS Consumer ID (defaults to settings.BPJS_CONSUMER_ID)
            secret_key: BPJS Secret Key (defaults to settings.BPJS_CONSUMER_SECRET)
            user_key: BPJS User Key (defaults to settings.BPJS_USER_KEY)
            api_url: BPJS API URL (defaults to settings.BPJS_API_URL)
        """
        self.cons_id = cons_id or settings.BPJS_CONSUMER_ID
        self.secret_key = secret_key or settings.BPJS_CONSUMER_SECRET
        self.user_key = user_key or settings.BPJS_USER_KEY or ""
        self.api_url = api_url or settings.BPJS_API_URL

        if not self.cons_id or not self.secret_key:
            logger.warning(
                "BPJS credentials not configured. "
                "Set BPJS_CONSUMER_ID and BPJS_CONSUMER_SECRET in environment."
            )

        self._client = None  # type: Optional[httpx.AsyncClient]

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    async def get_client(self) -> httpx.AsyncClient:
        """
        Get or create HTTP client.

        Returns:
            httpx.AsyncClient instance
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=10.0),
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            )
        return self._client

    def _generate_timestamp(self) -> str:
        """
        Generate timestamp for BPJS API authentication.

        Returns:
            Timestamp string in UTC format
        """
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def _generate_signature(self, timestamp: str) -> str:
        """
        Generate HMAC-SHA256 signature for BPJS API authentication.

        Signature formula: HMAC-SHA256(cons_id + timestamp, secret_key)

        Args:
            timestamp: Timestamp string

        Returns:
            Hex-encoded signature string
        """
        string_to_sign = f"{self.cons_id}{timestamp}"
        signature = hmac.new(
            self.secret_key.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _get_headers(self) -> Dict[str, str]:
        """
        Generate authentication headers for BPJS API requests.

        Returns:
            Dictionary of headers
        """
        timestamp = self._generate_timestamp()
        signature = self._generate_signature(timestamp)

        headers = {
            "X-cons-id": self.cons_id,
            "X-timestamp": timestamp,
            "X-signature": signature,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # Add user_key header if provided (new API requirement)
        if self.user_key:
            headers["X-user-key"] = self.user_key

        return headers

    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL for API endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            Full URL string
        """
        return urljoin(self.api_url + "/", endpoint)

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle HTTP response from BPJS API.

        Args:
            response: httpx Response object

        Returns:
            Parsed JSON response data

        Raises:
            BPJSVClaimError: If API returns an error
        """
        try:
            data = response.json()

            # Check for BPJS API error structure
            if "metaData" in data:
                metadata = data["metaData"]
                code = metadata.get("code", "")
                message = metadata.get("message", "")

                # BPJS returns code "200" for success
                if code != "200":
                    logger.error(f"BPJS API error: {code} - {message}")
                    raise BPJSVClaimError(
                        message=message,
                        code=code,
                        details=str(data.get("response", {}))
                    )

            return data

        except ValueError as e:
            logger.error(f"Failed to parse BPJS API response: {e}")
            raise BPJSVClaimError(
                message="Invalid JSON response from BPJS API",
                details=str(e)
            )

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to BPJS API.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON body data

        Returns:
            Parsed JSON response

        Raises:
            BPJSVClaimError: If request fails
        """
        if not self.cons_id or not self.secret_key:
            raise BPJSVClaimError(
                "BPJS credentials not configured. "
                "Please set BPJS_CONSUMER_ID and BPJS_CONSUMER_SECRET."
            )

        client = await self.get_client()
        url = self._build_url(endpoint)
        headers = self._get_headers()

        logger.info(f"BPJS API request: {method} {url}")

        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=json_data)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=headers, json=json_data)
            else:
                raise BPJSVClaimError(f"Unsupported HTTP method: {method}")

            # Log response status
            logger.info(f"BPJS API response: {response.status_code}")

            # Handle HTTP errors
            if response.status_code >= 400:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"BPJS API HTTP error: {error_msg}")
                raise BPJSVClaimError(message=error_msg)

            return await self._handle_response(response)

        except httpx.TimeoutException as e:
            logger.error(f"BPJS API timeout: {e}")
            raise BPJSVClaimError(
                message="Request to BPJS API timed out",
                details=str(e)
            )
        except httpx.RequestError as e:
            logger.error(f"BPJS API request error: {e}")
            raise BPJSVClaimError(
                message="Failed to connect to BPJS API",
                details=str(e)
            )
        except BPJSVClaimError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during BPJS API request: {e}")
            raise BPJSVClaimError(
                message=f"Unexpected error: {str(e)}",
                details=str(e)
            )

    async def check_eligibility_by_card(
        self,
        card_number: str,
        sep_date: str,
    ) -> Dict[str, Any]:
        """
        Check BPJS member eligibility by card number.

        Args:
            card_number: 13-digit BPJS card number
            sep_date: SEP date (format: YYYY-MM-DD)

        Returns:
            Dictionary containing participant information

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"Peserta/nokartu/{card_number}/tglSEP/{sep_date}"
        return await self._request("GET", endpoint)

    async def check_eligibility_by_nik(
        self,
        nik: str,
        sep_date: str,
    ) -> Dict[str, Any]:
        """
        Check BPJS member eligibility by NIK (Indonesian ID number).

        Args:
            nik: 16-digit Indonesian ID number
            sep_date: SEP date (format: YYYY-MM-DD)

        Returns:
            Dictionary containing participant information

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"Peserta/nik/{nik}/tglSEP/{sep_date}"
        return await self._request("GET", endpoint)

    async def create_sep(self, sep_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new SEP (Surat Eligibilitas Peserta).

        Args:
            sep_data: Dictionary containing SEP creation data

        Returns:
            Dictionary containing created SEP information

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = "SEP/create"
        return await self._request("POST", endpoint, json_data=sep_data)

    async def delete_sep(
        self,
        sep_number: str,
        user: str,
    ) -> Dict[str, Any]:
        """
        Delete an existing SEP.

        Args:
            sep_number: SEP number to delete
            user: User requesting the deletion

        Returns:
            Dictionary containing deletion response

        Raises:
            BPJSVClaimError: If request fails
        """
        query_params = {"user": user}
        endpoint = f"SEP/{sep_number}"
        return await self._request("DELETE", endpoint, params=query_params)

    async def update_sep(self, sep_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing SEP.

        Args:
            sep_data: Dictionary containing SEP update data

        Returns:
            Dictionary containing updated SEP information

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = "SEP/2.0/update"
        return await self._request("PUT", endpoint, json_data=sep_data)

    async def get_sep_by_number(self, sep_number: str) -> Dict[str, Any]:
        """
        Retrieve SEP information by SEP number.

        Args:
            sep_number: SEP number

        Returns:
            Dictionary containing SEP information

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"SEP/{sep_number}"
        return await self._request("GET", endpoint)

    async def get_polyclinic_list(
        self,
        start: int = 0,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Get list of polyclinics.

        Args:
            start: Starting index
            limit: Number of records to return

        Returns:
            Dictionary containing polyclinic list

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"referensi/poli/{start}/{limit}"
        return await self._request("GET", endpoint)

    async def get_facility_list(
        self,
        start: int = 0,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Get list of healthcare facilities (PPK).

        Args:
            start: Starting index
            limit: Number of records to return

        Returns:
            Dictionary containing facility list

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"referensi/faskes/{start}/{limit}"
        return await self._request("GET", endpoint)

    async def get_diagnosis_list(
        self,
        start: int = 0,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Get list of diagnoses (ICD-10).

        Args:
            start: Starting index
            limit: Number of records to return

        Returns:
            Dictionary containing diagnosis list

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"referensi/diagnosa/{start}/{limit}"
        return await self._request("GET", endpoint)

    async def get_diagnosis_by_code(self, diagnosis_code: str) -> Dict[str, Any]:
        """
        Get diagnosis information by code.

        Args:
            diagnosis_code: ICD-10 diagnosis code

        Returns:
            Dictionary containing diagnosis information

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"referensi/diagnosa/{diagnosis_code}"
        return await self._request("GET", endpoint)

    async def get_polyclinic_by_code(self, polyclinic_code: str) -> Dict[str, Any]:
        """
        Get polyclinic information by code.

        Args:
            polyclinic_code: Polyclinic code

        Returns:
            Dictionary containing polyclinic information

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"referensi/poli/{polyclinic_code}"
        return await self._request("GET", endpoint)

    async def get_facility_by_code(self, facility_code: str) -> Dict[str, Any]:
        """
        Get facility information by code.

        Args:
            facility_code: Healthcare facility code

        Returns:
            Dictionary containing facility information

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"referensi/faskes/{facility_code}"
        return await self._request("GET", endpoint)

    async def get_doctor_list(
        self,
        ppk_code: str,
        polyclinic_code: str,
        start: int = 0,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Get list of doctors by facility and polyclinic.

        Args:
            ppk_code: Healthcare facility code
            polyclinic_code: Polyclinic code
            start: Starting index
            limit: Number of records to return

        Returns:
            Dictionary containing doctor list

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"referensi/dokter/{ppk_code}/{polyclinic_code}/{start}/{limit}"
        return await self._request("GET", endpoint)

    async def get_room_class_list(self) -> Dict[str, Any]:
        """
        Get list of room classes.

        Returns:
            Dictionary containing room class list

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = "referensi/kelasrawat"
        return await self._request("GET", endpoint)

    async def get_facility_room_list(
        self,
        ppk_code: str,
        start: int = 0,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Get list of rooms in a facility.

        Args:
            ppk_code: Healthcare facility code
            start: Starting index
            limit: Number of records to return

        Returns:
            Dictionary containing room list

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"referensi/kamar/{ppk_code}/{start}/{limit}"
        return await self._request("GET", endpoint)

    async def get_referral_list(
        self,
        card_number: str,
        start_date: str,
        end_date: str,
    ) -> Dict[str, Any]:
        """
        Get referral (rujukan) list for a patient.

        Args:
            card_number: BPJS card number
            start_date: Start date (format: YYYY-MM-DD)
            end_date: End date (format: YYYY-MM-DD)

        Returns:
            Dictionary containing referral list

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"Rujukan/List/Peserta/{card_number}/{start_date}/{end_date}"
        return await self._request("GET", endpoint)

    async def get_referral_by_number(
        self,
        referral_number: str,
    ) -> Dict[str, Any]:
        """
        Get referral information by referral number.

        Args:
            referral_number: Referral number

        Returns:
            Dictionary containing referral information

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"Rujukan/{referral_number}"
        return await self._request("GET", endpoint)

    async def get_claim_status(
        self,
        claim_number: str,
        sep_date: str,
    ) -> Dict[str, Any]:
        """
        Get claim status for monitoring.

        Args:
            claim_number: Claim number (NOSEP)
            sep_date: SEP date (format: YYYY-MM-DD)

        Returns:
            Dictionary containing claim status information

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"Klaim/Status/{claim_number}/tglSEP/{sep_date}"
        return await self._request("GET", endpoint)

    async def get_claim_data(
        self,
        claim_number: str,
        sep_date: str,
    ) -> Dict[str, Any]:
        """
        Get claim data for Summary of Bill (SRB).

        Args:
            claim_number: Claim number (NOSEP)
            sep_date: SEP date (format: YYYY-MM-DD)

        Returns:
            Dictionary containing claim data

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"Klaim/Data/{claim_number}/tglSEP/{sep_date}"
        return await self._request("GET", endpoint)

    async def get_patient_history(
        self,
        card_number: str,
        start_date: str,
        end_date: str,
    ) -> Dict[str, Any]:
        """
        Get patient claim history.

        Args:
            card_number: BPJS card number
            start_date: Start date (format: YYYY-MM-DD)
            end_date: End date (format: YYYY-MM-DD)

        Returns:
            Dictionary containing patient history

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"histori/{card_number}/{start_date}/{end_date}"
        return await self._request("GET", endpoint)

    async def get_diagnosis_group(
        self,
        group_id: str,
    ) -> Dict[str, Any]:
        """
        Get diagnosis group information.

        Args:
            group_id: Diagnosis group ID

        Returns:
            Dictionary containing diagnosis group

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"referensi/icdgroup/{group_id}"
        return await self._request("GET", endpoint)

    async def get_procedure_list(
        self,
        start: int = 0,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Get procedure list (ICD-9-CM).

        Args:
            start: Starting index
            limit: Number of records to return

        Returns:
            Dictionary containing procedure list

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"referensi/prosedur/{start}/{limit}"
        return await self._request("GET", endpoint)

    async def get_procedure_by_code(
        self,
        procedure_code: str,
    ) -> Dict[str, Any]:
        """
        Get procedure information by code.

        Args:
            procedure_code: ICD-9-CM procedure code

        Returns:
            Dictionary containing procedure information

        Raises:
            BPJSVClaimError: If request fails
        """
        endpoint = f"referensi/prosedur/{procedure_code}"
        return await self._request("GET", endpoint)

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


class BPJSVClaimClientWithRetry(BPJSVClaimClient):
    """
    BPJS VClaim Client with automatic retry logic and exponential backoff.

    Extends BPJSVClaimClient to add retry capability for transient failures.
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_backoff: float = 1.0,
        max_backoff: float = 10.0,
        **kwargs
    ):
        """
        Initialize BPJS VClaim client with retry logic.

        Args:
            max_retries: Maximum number of retry attempts
            initial_backoff: Initial backoff time in seconds
            max_backoff: Maximum backoff time in seconds
            **kwargs: Arguments passed to BPJSVClaimClient
        """
        super().__init__(**kwargs)
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff

    async def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to BPJS API with retry logic.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON body data
            retry_count: Current retry attempt

        Returns:
            Parsed JSON response

        Raises:
            BPJSVClaimError: If all retry attempts fail
        """
        try:
            return await self._request(method, endpoint, params=params, json_data=json_data)

        except (httpx.TimeoutException, httpx.RequestError) as e:
            if retry_count < self.max_retries:
                # Calculate exponential backoff delay
                backoff_delay = min(
                    self.initial_backoff * (2 ** retry_count),
                    self.max_backoff
                )

                logger.warning(
                    f"BPJS API request failed (attempt {retry_count + 1}/{self.max_retries}): {e}. "
                    f"Retrying in {backoff_delay} seconds..."
                )

                # Wait before retry
                import asyncio
                await asyncio.sleep(backoff_delay)

                # Retry the request
                return await self._request_with_retry(
                    method, endpoint, params, json_data, retry_count + 1
                )
            else:
                logger.error(f"BPJS API request failed after {self.max_retries} retries: {e}")
                raise BPJSVClaimError(
                    message=f"Request failed after {self.max_retries} retries",
                    details=str(e)
                )

        except BPJSVClaimError as e:
            # Check if this is a transient error (5xx status codes)
            if e.code and e.code.startswith("5") and retry_count < self.max_retries:
                backoff_delay = min(
                    self.initial_backoff * (2 ** retry_count),
                    self.max_backoff
                )

                logger.warning(
                    f"BPJS API returned transient error (attempt {retry_count + 1}/{self.max_retries}): {e.message}. "
                    f"Retrying in {backoff_delay} seconds..."
                )

                import asyncio
                await asyncio.sleep(backoff_delay)

                return await self._request_with_retry(
                    method, endpoint, params, json_data, retry_count + 1
                )
            else:
                # Not retryable or max retries reached
                raise


# Convenience function for creating client instance
async def get_bpjs_client() -> BPJSVClaimClient:
    """
    Get configured BPJS VClaim client instance.

    Returns:
        BPJSVClaimClient instance
    """
    client = BPJSVClaimClient()
    await client.get_client()  # Initialize HTTP client
    return client


async def get_bpjs_client_with_retry() -> BPJSVClaimClientWithRetry:
    """
    Get configured BPJS VClaim client instance with retry logic.

    Returns:
        BPJSVClaimClientWithRetry instance
    """
    client = BPJSVClaimClientWithRetry()
    await client.get_client()  # Initialize HTTP client
    return client
