"""BPJS Antrean API Client Service.

This module provides an async client for interacting with the BPJS Antrean API,
handling authentication, request signing, and Mobile JKN queue management operations.

BPJS Antrean API Reference:
- Base URL: https://apijkn.bpjs-kesehatan.go.id/antreanrest
- Authentication: X-cons-id, X-signature, X-timestamp headers
- Signature: HMAC-SHA256(cons_id + timestamp, secret_key)

Key Endpoints:
- POST /antrean/perbarui - Update queue status
- POST /antrean/sisa - Get remaining queue
- GET /antrean/list - Get queue list
- POST /antrean/batal - Cancel booking
- POST /antrean/checkin - Patient check-in
- POST /antrean/kesimpulan - Complete service
"""
import asyncio
import hashlib
import hmac
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from urllib.parse import urljoin

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class BPJSAntreanError(Exception):
    """Custom exception for BPJS Antrean API errors."""

    def __init__(self, message: str, code: Optional[str] = None, details: Optional[str] = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class BPJSAntreanClient:
    """
    Async client for BPJS Antrean API integration.

    Handles authentication, request signing, and Mobile JKN queue management operations.
    """

    def __init__(
        self,
        cons_id: Optional[str] = None,
        secret_key: Optional[str] = None,
        user_key: Optional[str] = None,
        api_url: Optional[str] = None,
    ):
        """
        Initialize BPJS Antrean client.

        Args:
            cons_id: BPJS Consumer ID (defaults to settings.BPJS_CONSUMER_ID)
            secret_key: BPJS Secret Key (defaults to settings.BPJS_CONSUMER_SECRET)
            user_key: BPJS User Key (defaults to settings.BPJS_USER_KEY)
            api_url: BPJS Antrean API URL (defaults to Antrean base URL)
        """
        self.cons_id = cons_id or settings.BPJS_CONSUMER_ID
        self.secret_key = secret_key or settings.BPJS_CONSUMER_SECRET
        self.user_key = user_key or settings.BPJS_USER_KEY or ""
        self.api_url = api_url or "https://apijkn.bpjs-kesehatan.go.id/antreanrest"

        if not self.cons_id or not self.secret_key:
            logger.warning(
                "Kredensial BPJS tidak dikonfigurasi. "
                "Set BPJS_CONSUMER_ID dan BPJS_CONSUMER_SECRET di environment."
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
        Generate timestamp untuk autentikasi BPJS API.

        Returns:
            Timestamp string dalam format UTC
        """
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def _generate_signature(self, timestamp: str) -> str:
        """
        Generate HMAC-SHA256 signature untuk autentikasi BPJS API.

        Rumus signature: HMAC-SHA256(cons_id + timestamp, secret_key)

        Args:
            timestamp: Timestamp string

        Returns:
            Signature string dalam format hex-encoded
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
        Generate header autentikasi untuk request BPJS API.

        Returns:
            Dictionary dari headers
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

        # Tambahkan header user_key jika tersedia
        if self.user_key:
            headers["X-user-key"] = self.user_key

        return headers

    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL untuk endpoint API.

        Args:
            endpoint: API endpoint path

        Returns:
            Full URL string
        """
        return urljoin(self.api_url + "/", endpoint)

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle HTTP response dari BPJS API.

        Args:
            response: httpx Response object

        Returns:
            Data JSON response yang telah diparsing

        Raises:
            BPJSAntreanError: Jika API mengembalikan error
        """
        try:
            data = response.json()

            # Cek struktur error BPJS API
            if "metaData" in data:
                metadata = data["metaData"]
                code = metadata.get("code", "")
                message = metadata.get("message", "")

                # BPJS mengembalikan code "200" untuk sukses
                if code != "200":
                    logger.error(f"Error BPJS API: {code} - {message}")
                    raise BPJSAntreanError(
                        message=message,
                        code=code,
                        details=str(data.get("response", {}))
                    )

            return data

        except ValueError as e:
            logger.error(f"Gagal parsing response BPJS API: {e}")
            raise BPJSAntreanError(
                message="Respons JSON tidak valid dari BPJS API",
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
        Buat HTTP request ke BPJS API.

        Args:
            method: HTTP method (GET, POST, DELETE, dll)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON body data

        Returns:
            JSON response yang telah diparsing

        Raises:
            BPJSAntreanError: Jika request gagal
        """
        if not self.cons_id or not self.secret_key:
            raise BPJSAntreanError(
                "Kredensial BPJS tidak dikonfigurasi. "
                "Mohon set BPJS_CONSUMER_ID dan BPJS_CONSUMER_SECRET."
            )

        client = await self.get_client()
        url = self._build_url(endpoint)
        headers = self._get_headers()

        logger.info(f"Request BPJS API: {method} {url}")

        if json_data:
            logger.debug(f"Request body: {json_data}")

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
                raise BPJSAntreanError(f"HTTP method tidak didukung: {method}")

            # Log status response
            logger.info(f"Response BPJS API: {response.status_code}")

            # Handle HTTP errors
            if response.status_code >= 400:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Error HTTP BPJS API: {error_msg}")
                raise BPJSAntreanError(message=error_msg)

            return await self._handle_response(response)

        except httpx.TimeoutException as e:
            logger.error(f"Timeout BPJS API: {e}")
            raise BPJSAntreanError(
                message="Request ke BPJS API timeout",
                details=str(e)
            )
        except httpx.RequestError as e:
            logger.error(f"Error request BPJS API: {e}")
            raise BPJSAntreanError(
                message="Gagal terhubung ke BPJS API",
                details=str(e)
            )
        except BPJSAntreanError:
            raise
        except Exception as e:
            logger.error(f"Error tak terduga saat request BPJS API: {e}")
            raise BPJSAntreanError(
                message=f"Error tak terduga: {str(e)}",
                details=str(e)
            )

    async def update_queue_status(
        self,
        queue_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update status antrian (Perbarui Antrian).

        Args:
            queue_data: Dictionary berisi data update antrian:
                - kodebooking: Kode booking (string, wajib)
                - jenisantrean: Jenis antrian (string, wajib)
                - estimasidilayani: Estimasi waktu layanan (integer, wajib)
                - namapoli: Nama poli (string, opsional)
                - namadokter: Nama dokter (string, opsional)

        Returns:
            Dictionary berisi response update antrian

        Raises:
            BPJSAntreanError: Jika request gagal

        Contoh:
            client.update_queue_status({
                "kodebooking": "123456",
                "jenisantrean": "2",
                "estimasidilayani": 1609459200000
            })
        """
        endpoint = "antrean/perbarui"
        return await self._request("POST", endpoint, json_data=queue_data)

    async def get_remaining_queue(
        self,
        queue_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Dapatkan sisa antrian (Sisa Antrian).

        Args:
            queue_data: Dictionary berisi data query sisa antrian:
                - kodebooking: Kode booking (string, wajib)
                - polieksekusi: Kode poli eksekusi (string, wajib)
                - tanggalperiksa: Tanggal periksa (string, wajib)

        Returns:
            Dictionary berisi informasi sisa antrian

        Raises:
            BPJSAntreanError: Jika request gagal

        Contoh:
            client.get_remaining_queue({
                "kodebooking": "123456",
                "polieksekusi": "INT",
                "tanggalperiksa": "2024-01-15"
            })
        """
        endpoint = "antrean/sisa"
        return await self._request("POST", endpoint, json_data=queue_data)

    async def get_queue_list(
        self,
        date: str,
        poly_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Dapatkan daftar antrian (List Antrian).

        Args:
            date: Tanggal periksa (format: YYYY-MM-DD)
            poly_code: Kode poli (opsional)

        Returns:
            Dictionary berisi daftar antrian

        Raises:
            BPJSAntreanError: Jika request gagal

        Contoh:
            client.get_queue_list("2024-01-15", "INT")
        """
        endpoint = f"antrean/list"
        params = {"tanggalperiksa": date}

        if poly_code:
            params["kodepoli"] = poly_code

        return await self._request("GET", endpoint, params=params)

    async def cancel_booking(
        self,
        cancellation_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Batalkan booking antrian (Batal Antrian).

        Args:
            cancellation_data: Dictionary berisi data pembatalan:
                - kodebooking: Kode booking (string, wajib)
                - keterangan: Alasan pembatalan (string, wajib)

        Returns:
            Dictionary berisi response pembatalan

        Raises:
            BPJSAntreanError: Jika request gagal

        Contoh:
            client.cancel_booking({
                "kodebooking": "123456",
                "keterangan": "Pasien membatalkan karena ada urusan mendadak"
            })
        """
        endpoint = "antrean/batal"
        return await self._request("POST", endpoint, json_data=cancellation_data)

    async def checkin_patient(
        self,
        checkin_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Check-in pasien (Check-in Antrian).

        Args:
            checkin_data: Dictionary berisi data check-in:
                - kodebooking: Kode booking (string, wajib)
                - waktu: Waktu check-in dalam milliseconds (integer, wajib)
                - jenisantrean: Jenis antrian (string, wajib)

        Returns:
            Dictionary berisi response check-in

        Raises:
            BPJSAntreanError: Jika request gagal

        Contoh:
            client.checkin_patient({
                "kodebooking": "123456",
                "waktu": 1609459200000,
                "jenisantrean": "2"
            })
        """
        endpoint = "antrean/checkin"
        return await self._request("POST", endpoint, json_data=checkin_data)

    async def complete_service(
        self,
        completion_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Selesaikan layanan pasien (Kesimpulan Antrian).

        Args:
            completion_data: Dictionary berisi data penyelesaian:
                - kodebooking: Kode booking (string, wajib)
                - hasilpelayanan: Hasil pelayanan (string, wajib)
                - keterangan: Keterangan tambahan (string, opsional)

        Returns:
            Dictionary berisi response penyelesaian

        Raises:
            BPJSAntreanError: Jika request gagal

        Contoh:
            client.complete_service({
                "kodebooking": "123456",
                "hasilpelayanan": "Selesai",
                "keterangan": "Pasien已完成治疗"
            })
        """
        endpoint = "antrean/kesimpulan"
        return await self._request("POST", endpoint, json_data=completion_data)

    async def get_current_queue(
        self,
        poly_code: str,
        date: str,
    ) -> Dict[str, Any]:
        """
        Dapatkan nomor antrian saat ini.

        Args:
            poly_code: Kode poli
            date: Tanggal periksa (format: YYYY-MM-DD)

        Returns:
            Dictionary berisi informasi antrian saat ini

        Raises:
            BPJSAntreanError: Jika request gagal

        Contoh:
            client.get_current_queue("INT", "2024-01-15")
        """
        endpoint = f"antrean/getcurrent"
        params = {
            "kodepoli": poly_code,
            "tanggalperiksa": date,
        }
        return await self._request("GET", endpoint, params=params)

    async def get_available_slots(
        self,
        poly_code: str,
        date: str,
    ) -> Dict[str, Any]:
        """
        Dapatkan slot antrian yang tersedia.

        Args:
            poly_code: Kode poli
            date: Tanggal periksa (format: YYYY-MM-DD)

        Returns:
            Dictionary berisi informasi slot tersedia

        Raises:
            BPJSAntreanError: Jika request gagal

        Contoh:
            client.get_available_slots("INT", "2024-01-15")
        """
        endpoint = f"antrean/slot"
        params = {
            "kodepoli": poly_code,
            "tanggalperiksa": date,
        }
        return await self._request("GET", endpoint, params=params)

    async def get_doctor_schedule(
        self,
        poly_code: str,
        date: str,
    ) -> Dict[str, Any]:
        """
        Dapatkan jadwal dokter poli.

        Args:
            poly_code: Kode poli
            date: Tanggal periksa (format: YYYY-MM-DD)

        Returns:
            Dictionary berisi jadwal dokter

        Raises:
            BPJSAntreanError: Jika request gagal

        Contoh:
            client.get_doctor_schedule("INT", "2024-01-15")
        """
        endpoint = f"antrean/jadwal"
        params = {
            "kodepoli": poly_code,
            "tanggalperiksa": date,
        }
        return await self._request("GET", endpoint, params=params)

    async def close(self):
        """Tutup HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


class BPJSAntreanClientWithRetry(BPJSAntreanClient):
    """
    BPJS Antrean Client dengan retry logic otomatis dan exponential backoff.

    Extends BPJSAntreanClient untuk menambahkan kemampuan retry untuk kegagalan transient.
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_backoff: float = 1.0,
        max_backoff: float = 10.0,
        **kwargs
    ):
        """
        Initialize BPJS Antrean client dengan retry logic.

        Args:
            max_retries: Jumlah maksimum percobaan retry
            initial_backoff: Waktu backoff awal dalam detik
            max_backoff: Waktu backoff maksimum dalam detik
            **kwargs: Arguments yang diteruskan ke BPJSAntreanClient
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
        Buat HTTP request ke BPJS API dengan retry logic.

        Args:
            method: HTTP method (GET, POST, DELETE, dll)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON body data
            retry_count: Percobaan retry saat ini

        Returns:
            JSON response yang telah diparsing

        Raises:
            BPJSAntreanError: Jika semua percobaan retry gagal
        """
        try:
            return await self._request(method, endpoint, params=params, json_data=json_data)

        except (httpx.TimeoutException, httpx.RequestError) as e:
            if retry_count < self.max_retries:
                # Hitung exponential backoff delay
                backoff_delay = min(
                    self.initial_backoff * (2 ** retry_count),
                    self.max_backoff
                )

                logger.warning(
                    f"Request BPJS API gagal (percobaan {retry_count + 1}/{self.max_retries}): {e}. "
                    f"Retry dalam {backoff_delay} detik..."
                )

                # Tunggu sebelum retry
                await asyncio.sleep(backoff_delay)

                # Retry request
                return await self._request_with_retry(
                    method, endpoint, params, json_data, retry_count + 1
                )
            else:
                logger.error(f"Request BPJS API gagal setelah {self.max_retries} retry: {e}")
                raise BPJSAntreanError(
                    message=f"Request gagal setelah {self.max_retries} percobaan",
                    details=str(e)
                )

        except BPJSAntreanError as e:
            # Cek jika ini adalah error transient (5xx status codes)
            if e.code and e.code.startswith("5") and retry_count < self.max_retries:
                backoff_delay = min(
                    self.initial_backoff * (2 ** retry_count),
                    self.max_backoff
                )

                logger.warning(
                    f"BPJS API mengembalikan error transient (percobaan {retry_count + 1}/{self.max_retries}): {e.message}. "
                    f"Retry dalam {backoff_delay} detik..."
                )

                await asyncio.sleep(backoff_delay)

                return await self._request_with_retry(
                    method, endpoint, params, json_data, retry_count + 1
                )
            else:
                # Tidak bisa di-retry atau max retries tercapai
                raise

    # Override semua endpoint methods untuk menggunakan _request_with_retry
    async def update_queue_status(self, queue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update status antrian dengan retry."""
        endpoint = "antrean/perbarui"
        return await self._request_with_retry("POST", endpoint, json_data=queue_data)

    async def get_remaining_queue(self, queue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dapatkan sisa antrian dengan retry."""
        endpoint = "antrean/sisa"
        return await self._request_with_retry("POST", endpoint, json_data=queue_data)

    async def get_queue_list(self, date: str, poly_code: Optional[str] = None) -> Dict[str, Any]:
        """Dapatkan daftar antrian dengan retry."""
        endpoint = "antrean/list"
        params = {"tanggalperiksa": date}
        if poly_code:
            params["kodepoli"] = poly_code
        return await self._request_with_retry("GET", endpoint, params=params)

    async def cancel_booking(self, cancellation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Batalkan booking dengan retry."""
        endpoint = "antrean/batal"
        return await self._request_with_retry("POST", endpoint, json_data=cancellation_data)

    async def checkin_patient(self, checkin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check-in pasien dengan retry."""
        endpoint = "antrean/checkin"
        return await self._request_with_retry("POST", endpoint, json_data=checkin_data)

    async def complete_service(self, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Selesaikan layanan dengan retry."""
        endpoint = "antrean/kesimpulan"
        return await self._request_with_retry("POST", endpoint, json_data=completion_data)

    async def get_current_queue(self, poly_code: str, date: str) -> Dict[str, Any]:
        """Dapatkan antrian saat ini dengan retry."""
        endpoint = f"antrean/getcurrent"
        params = {"kodepoli": poly_code, "tanggalperiksa": date}
        return await self._request_with_retry("GET", endpoint, params=params)

    async def get_available_slots(self, poly_code: str, date: str) -> Dict[str, Any]:
        """Dapatkan slot tersedia dengan retry."""
        endpoint = f"antrean/slot"
        params = {"kodepoli": poly_code, "tanggalperiksa": date}
        return await self._request_with_retry("GET", endpoint, params=params)

    async def get_doctor_schedule(self, poly_code: str, date: str) -> Dict[str, Any]:
        """Dapatkan jadwal dokter dengan retry."""
        endpoint = f"antrean/jadwal"
        params = {"kodepoli": poly_code, "tanggalperiksa": date}
        return await self._request_with_retry("GET", endpoint, params=params)


# Fungsi convenience untuk membuat instance client
async def get_bpjs_antrean_client() -> BPJSAntreanClient:
    """
    Dapatkan instance BPJS Antrean client yang sudah terkonfigurasi.

    Returns:
        BPJSAntreanClient instance
    """
    client = BPJSAntreanClient()
    await client.get_client()  # Initialize HTTP client
    return client


async def get_bpjs_antrean_client_with_retry() -> BPJSAntreanClientWithRetry:
    """
    Dapatkan instance BPJS Antrean client dengan retry logic.

    Returns:
        BPJSAntreanClientWithRetry instance
    """
    client = BPJSAntreanClientWithRetry()
    await client.get_client()  # Initialize HTTP client
    return client
