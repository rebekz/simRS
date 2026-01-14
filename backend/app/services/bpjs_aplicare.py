"""BPJS Aplicare API Client Service.

This module provides an async client for interacting with the BPJS Aplicare API,
handling authentication, request signing, and bed availability reporting.

BPJS Aplicare API Reference:
- Base URL: https://apijkn.bpjs-kesehatan.go.id/aplicarews
- Authentication: X-cons-id, X-signature, X-timestamp headers
- Signature: HMAC-SHA256(cons_id + timestamp, secret_key)

Key Endpoints:
- POST /bed/create - Add new bed data
- POST /bed/update - Update existing bed data
- POST /bed/delete - Delete bed data
- GET /bed/list - Get list of beds
- GET /bed/{kodekelas}/gettotalbed - Get total bed count by room class
"""
import hashlib
import hmac
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class BPJSAplicareError(Exception):
    """Custom exception for BPJS Aplicare API errors."""

    def __init__(self, message: str, code: Optional[str] = None, details: Optional[str] = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class BPJSAplicareClient:
    """
    Async client for BPJS Aplicare API integration.

    Handles authentication, request signing, and bed availability reporting.
    """

    def __init__(
        self,
        cons_id: Optional[str] = None,
        secret_key: Optional[str] = None,
        user_key: Optional[str] = None,
        api_url: Optional[str] = None,
    ):
        """
        Initialize BPJS Aplicare client.

        Args:
            cons_id: BPJS Consumer ID (defaults to settings.BPJS_CONSUMER_ID)
            secret_key: BPJS Secret Key (defaults to settings.BPJS_CONSUMER_SECRET)
            user_key: BPJS User Key (defaults to settings.BPJS_USER_KEY)
            api_url: BPJS Aplicare API URL (defaults to settings.BPJS_APLICARE_URL)
        """
        self.cons_id = cons_id or settings.BPJS_CONSUMER_ID
        self.secret_key = secret_key or settings.BPJS_CONSUMER_SECRET
        self.user_key = user_key or settings.BPJS_USER_KEY or ""
        self.api_url = api_url or getattr(settings, 'BPJS_APLICARE_URL', 'https://apijkn.bpjs-kesehatan.go.id/aplicarews')

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
            Dictionary of HTTP headers
        """
        timestamp = self._generate_timestamp()
        signature = self._generate_signature(timestamp)

        headers = {
            "X-cons-id": self.cons_id,
            "X-timestamp": timestamp,
            "X-signature": signature,
            "Content-Type": "application/json",
        }

        if self.user_key:
            headers["X-user-key"] = self.user_key

        return headers

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to BPJS Aplicare API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            json_data: Request body for POST/PUT requests

        Returns:
            Response data as dictionary

        Raises:
            BPJSAplicareError: If API request fails
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()

        client = await self.get_client()

        try:
            logger.info(f"BPJS Aplicare API Request: {method} {url}")

            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=json_data)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=headers, json=json_data)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers, params=params)
            else:
                raise BPJSAplicareError(f"Unsupported HTTP method: {method}")

            # Log response status
            logger.info(f"BPJS Aplicare API Response: {response.status_code}")

            # Parse response
            response.raise_for_status()
            data = response.json()

            # Check for BPJS API errors
            if not self._is_response_success(data):
                error_code = data.get("code") or data.get("metaData", {}).get("code")
                error_message = data.get("message") or data.get("metaData", {}).get("message")
                raise BPJSAplicareError(
                    message=error_message or "BPJS API returned an error",
                    code=error_code,
                    details=str(data)
                )

            return data

        except httpx.TimeoutException as e:
            logger.error(f"BPJS Aplicare API timeout: {e}")
            raise BPJSAplicareError(
                message="BPJS API request timed out",
                details=str(e)
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"BPJS Aplicare API HTTP error: {e.response.status_code} - {e.response.text}")
            raise BPJSAplicareError(
                message=f"BPJS API returned HTTP {e.response.status_code}",
                code=str(e.response.status_code),
                details=e.response.text
            )
        except httpx.RequestError as e:
            logger.error(f"BPJS Aplicare API request error: {e}")
            raise BPJSAplicareError(
                message="Failed to connect to BPJS API",
                details=str(e)
            )
        except Exception as e:
            logger.error(f"BPJS Aplicare API unexpected error: {e}")
            raise BPJSAplicareError(
                message="Unexpected error during BPJS API request",
                details=str(e)
            )

    def _is_response_success(self, data: Dict[str, Any]) -> bool:
        """
        Check if BPJS API response indicates success.

        Args:
            data: Response data

        Returns:
            True if response indicates success
        """
        # Check for common success patterns
        if "metaData" in data:
            return data.get("metaData", {}).get("code") == "200"
        if "code" in data:
            return str(data.get("code")) == "200"
        if "response" in data:
            return True
        return False

    # =============================================================================
    # Bed Availability Endpoints
    # =============================================================================

    async def create_bed(
        self,
        kodekelas: str,
        koderuang: str,
        namaruang: str,
        kapasitas: int,
        tersedia: int,
        tersediapria: int,
        tersediawanita: int,
        tersediapriawanita: int,
    ) -> Dict[str, Any]:
        """
        Add new bed data to BPJS Aplicare.

        Args:
            kodekelas: Room class code (1, 2, 3, VVIP, VIP)
            koderuang: Room code
            namaruang: Room name
            kapasitas: Total bed capacity
            tersedia: Available beds
            tersediapria: Available male beds
            tersediawanita: Available female beds
            tersediapriawanita: Available mixed gender beds

        Returns:
            Response data from BPJS API
        """
        endpoint = "bed/create"
        payload = {
            "kodekelas": kodekelas,
            "koderuang": koderuang,
            "namaruang": namaruang,
            "kapasitas": kapasitas,
            "tersedia": tersedia,
            "tersediapria": tersediapria,
            "tersediawanita": tersediawanita,
            "tersediapriawanita": tersediapriawanita,
        }

        return await self._request("POST", endpoint, json_data=payload)

    async def update_bed(
        self,
        kodekelas: str,
        koderuang: str,
        namaruang: str,
        kapasitas: int,
        tersedia: int,
        tersediapria: int,
        tersediawanita: int,
        tersediapriawanita: int,
    ) -> Dict[str, Any]:
        """
        Update existing bed data in BPJS Aplicare.

        Args:
            kodekelas: Room class code (1, 2, 3, VVIP, VIP)
            koderuang: Room code
            namaruang: Room name
            kapasitas: Total bed capacity
            tersedia: Available beds
            tersediapria: Available male beds
            tersediawanita: Available female beds
            tersediapriawanita: Available mixed gender beds

        Returns:
            Response data from BPJS API
        """
        endpoint = "bed/update"
        payload = {
            "kodekelas": kodekelas,
            "koderuang": koderuang,
            "namaruang": namaruang,
            "kapasitas": kapasitas,
            "tersedia": tersedia,
            "tersediapria": tersediapria,
            "tersediawanita": tersediawanita,
            "tersediapriawanita": tersediapriawanita,
        }

        return await self._request("POST", endpoint, json_data=payload)

    async def delete_bed(
        self,
        kodekelas: str,
        koderuang: str,
    ) -> Dict[str, Any]:
        """
        Delete bed data from BPJS Aplicare.

        Args:
            kodekelas: Room class code
            koderuang: Room code

        Returns:
            Response data from BPJS API
        """
        endpoint = "bed/delete"
        payload = {
            "kodekelas": kodekelas,
            "koderuang": koderuang,
        }

        return await self._request("POST", endpoint, json_data=payload)

    async def get_bed_list(
        self,
        start: int = 0,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Get list of beds from BPJS Aplicare.

        Args:
            start: Start index for pagination
            limit: Number of records to return

        Returns:
            Response data with bed list
        """
        endpoint = f"bed/list/{start}/{limit}"
        return await self._request("GET", endpoint)

    async def get_bed_count_by_class(
        self,
        kodekelas: str,
    ) -> Dict[str, Any]:
        """
        Get total bed count by room class.

        Args:
            kodekelas: Room class code (1, 2, 3, VVIP, VIP)

        Returns:
            Response data with bed count
        """
        endpoint = f"bed/{kodekelas}/gettotalbed"
        return await self._request("GET", endpoint)


# =============================================================================
# Convenience Functions
# =============================================================================

async def get_bpjs_aplicare_client() -> BPJSAplicareClient:
    """
    Get configured BPJS Aplicare client instance.

    Returns:
        BPJSAplicareClient instance
    """
    client = BPJSAplicareClient()
    await client.get_client()  # Initialize HTTP client
    return client
