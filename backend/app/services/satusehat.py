"""SATUSEHAT FHIR R4 API client for STORY-033: Organization Registration.

This module provides the OAuth 2.0 authenticated client for SATUSEHAT integration,
including token management, facility registration, and FHIR resource operations.
"""
import logging
import json
import hashlib
import hmac
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from httpx import AsyncClient, HTTPStatusError, TimeoutException
from app.core.config import settings

logger = logging.getLogger(__name__)


class SATUSEHATError(Exception):
    """Base exception for SATUSEHAT API errors."""

    def __init__(self, message: str, code: Optional[str] = None, details: Optional[str] = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class SATUSEHATAuthError(SATUSEHATError):
    """Exception for SATUSEHAT authentication errors."""

    pass


class SATUSEHATClient:
    """
    Async client for SATUSEHAT FHIR R4 API integration.

    This client handles:
    - OAuth 2.0 client credentials authentication
    - Automatic token refresh
    - Organization registration and management
    - FHIR resource operations (Patient, Encounter, Condition, etc.)
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        auth_url: Optional[str] = None,
        api_url: Optional[str] = None,
    ):
        """
        Initialize SATUSEHAT client.

        Args:
            client_id: OAuth client ID (from SATUSEHAT portal)
            client_secret: OAuth client secret (from SATUSEHAT portal)
            auth_url: OAuth authorization server URL
            api_url: FHIR API base URL
        """
        self.client_id = client_id or settings.SATUSEHAT_CLIENT_ID
        self.client_secret = client_secret or settings.SATUSEHAT_CLIENT_SECRET
        self.auth_url = auth_url or settings.SATUSEHAT_AUTH_URL
        self.api_url = api_url or settings.SATUSEHAT_API_URL

        # Token cache
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

        # HTTP client
        self._client: Optional[AsyncClient] = None

    async def __aenter__(self):
        """Enter async context manager."""
        self._client = AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()

    # =============================================================================
    # OAuth 2.0 Authentication
    # =============================================================================

    async def _get_valid_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.

        Returns:
            Valid access token

        Raises:
            SATUSEHATAuthError: If token acquisition fails
        """
        # Check if we have a valid token
        if self._access_token and self._token_expires_at:
            # Add 5-minute buffer to avoid using expired tokens
            if datetime.now() + timedelta(minutes=5) < self._token_expires_at:
                return self._access_token

        # Need to refresh token
        return await self._refresh_token()

    async def _refresh_token(self) -> str:
        """
        Refresh access token using client credentials grant.

        Returns:
            New access token

        Raises:
            SATUSEHATAuthError: If token refresh fails
        """
        if not self._client:
            raise SATUSEHATError("Client not initialized. Use async context manager.")

        try:
            # Prepare token request
            token_url = f"{self.auth_url}/accesstoken"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            # Build request body
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            }

            logger.info(f"Requesting access token from {token_url}")

            # Make token request
            response = await self._client.post(token_url, headers=headers, data=data)
            response.raise_for_status()

            token_data = response.json()

            # Extract token and expiration
            self._access_token = token_data.get("access_token")
            if not self._access_token:
                raise SATUSEHATAuthError("No access token in response")

            # Calculate expiration (expires_in is in seconds)
            expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)

            logger.info(f"Access token obtained, expires at {self._token_expires_at}")

            return self._access_token

        except HTTPStatusError as e:
            error_msg = f"HTTP error refreshing token: {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f" - {error_detail.get('error', 'Unknown error')}"
            except:
                pass
            logger.error(error_msg)
            raise SATUSEHATAuthError(error_msg, code=str(e.response.status_code))

        except Exception as e:
            error_msg = f"Failed to refresh access token: {str(e)}"
            logger.error(error_msg)
            raise SATUSEHATAuthError(error_msg)

    # =============================================================================
    # FHIR Resource Operations
    # =============================================================================

    async def _make_fhir_request(
        self,
        method: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make authenticated FHIR API request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            resource_type: FHIR resource type (Patient, Organization, etc.)
            resource_id: Resource ID for PUT/DELETE operations
            data: Request body data
            params: Query parameters

        Returns:
            FHIR response data

        Raises:
            SATUSEHATError: If request fails
        """
        if not self._client:
            raise SATUSEHATError("Client not initialized. Use async context manager.")

        # Get valid access token
        token = await self._get_valid_token()

        # Build URL
        url = f"{self.api_url}/{resource_type}"
        if resource_id:
            url += f"/{resource_id}"

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/fhir+json",
        }

        try:
            # Make request
            if method.upper() == "GET":
                response = await self._client.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = await self._client.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = await self._client.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = await self._client.delete(url, headers=headers)
            else:
                raise SATUSEHATError(f"Unsupported HTTP method: {method}")

            # Check for errors
            try:
                response.raise_for_status()
            except HTTPStatusError as e:
                # Parse FHIR OperationOutcome for error details
                try:
                    error_data = e.response.json()
                    if "resourceType" in error_data and error_data["resourceType"] == "OperationOutcome":
                        issues = error_data.get("issue", [])
                        if issues:
                            error_msg = issues[0].get("diagnostics", issues[0].get("text", "Unknown error"))
                            raise SATUSEHATError(
                                error_msg,
                                code=str(e.response.status_code),
                                details=json.dumps(issues),
                            )
                except:
                    pass
                raise

            return response.json()

        except HTTPStatusError as e:
            logger.error(f"HTTP error in FHIR request: {e.response.status_code}")
            raise SATUSEHATError(
                f"HTTP {e.response.status_code}: {e.response.text}",
                code=str(e.response.status_code),
            )

        except TimeoutException:
            logger.error("Timeout in FHIR request")
            raise SATUSEHATError("Request timeout")

        except SATUSEHATError:
            raise

        except Exception as e:
            logger.exception("Unexpected error in FHIR request")
            raise SATUSEHATError(f"Unexpected error: {str(e)}")

    # =============================================================================
    # Organization Management (STORY-033)
    # =============================================================================

    async def create_organization(
        self,
        identifier: str,
        name: str,
        org_type: List[str],
        telecom: Optional[List[Dict[str, Any]]] = None,
        address: Optional[Dict[str, Any]] = None,
        part_of: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register a healthcare organization/facility with SATUSEHAT.

        Args:
            identifier: Facility identifier (e.g., hospital code)
            name: Facility name
            org_type: List of organization type codes
            telecom: Contact information (phone, email)
            address: Facility address
            part_of: Parent organization ID (if part of larger network)

        Returns:
            Created FHIR Organization resource

        Raises:
            SATUSEHATError: If creation fails
        """
        # Build FHIR Organization resource
        organization = {
            "resourceType": "Organization",
            "identifier": [
                {
                    "use": "official",
                    "system": "https://fhir.kemkes.go.id/id/satusehat-kode-fasyankes",
                    "value": identifier,
                }
            ],
            "active": True,
            "type": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/organization-type", "code": t}]} for t in org_type],
            "name": name,
        }

        if telecom:
            organization["telecom"] = telecom

        if address:
            organization["address"] = [address]

        if part_of:
            organization["partOf"] = {"reference": f"Organization/{part_of}"}

        logger.info(f"Creating Organization: {name} (ID: {identifier})")

        result = await self._make_fhir_request("POST", "Organization", data=organization)

        logger.info(f"Organization created with ID: {result.get('id')}")

        return result

    async def update_organization(
        self,
        organization_id: str,
        identifier: Optional[str] = None,
        name: Optional[str] = None,
        org_type: Optional[List[str]] = None,
        telecom: Optional[List[Dict[str, Any]]] = None,
        address: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing organization in SATUSEHAT.

        Args:
            organization_id: FHIR Organization resource ID
            identifier: Facility identifier
            name: Facility name
            org_type: List of organization type codes
            telecom: Contact information
            address: Facility address

        Returns:
            Updated FHIR Organization resource

        Raises:
            SATUSEHATError: If update fails
        """
        # Build minimal update resource
        organization = {
            "resourceType": "Organization",
            "id": organization_id,
            "active": True,
        }

        if identifier:
            organization["identifier"] = [
                {
                    "use": "official",
                    "system": "https://fhir.kemkes.go.id/id/satusehat-kode-fasyankes",
                    "value": identifier,
                }
            ]

        if name:
            organization["name"] = name

        if org_type:
            organization["type"] = [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/organization-type", "code": t}]} for t in org_type]

        if telecom:
            organization["telecom"] = telecom

        if address:
            organization["address"] = [address]

        logger.info(f"Updating Organization: {organization_id}")

        result = await self._make_fhir_request("PUT", "Organization", resource_id=organization_id, data=organization)

        logger.info(f"Organization updated: {organization_id}")

        return result

    async def get_organization(self, organization_id: str) -> Dict[str, Any]:
        """
        Retrieve an organization from SATUSEHAT.

        Args:
            organization_id: FHIR Organization resource ID

        Returns:
            FHIR Organization resource

        Raises:
            SATUSEHATError: If retrieval fails
        """
        logger.info(f"Retrieving Organization: {organization_id}")

        result = await self._make_fhir_request("GET", "Organization", resource_id=organization_id)

        return result

    async def search_organization_by_identifier(self, identifier: str) -> Dict[str, Any]:
        """
        Search for organization by facility identifier.

        Args:
            identifier: Facility identifier (e.g., hospital code)

        Returns:
            FHIR Bundle with search results

        Raises:
            SATUSEHATError: If search fails
        """
        params = {"identifier": f"https://fhir.kemkes.go.id/id/satusehat-kode-fasyankes|{identifier}"}

        logger.info(f"Searching Organization by identifier: {identifier}")

        result = await self._make_fhir_request("GET", "Organization", params=params)

        return result

    # =============================================================================
    # Connectivity Testing
    # =============================================================================

    async def test_connectivity(self) -> Dict[str, Any]:
        """
        Test basic connectivity to SATUSEHAT services.

        Returns:
            Test results including auth and API status

        Raises:
            SATUSEHATError: If connectivity test fails
        """
        results = {
            "auth_url": self.auth_url,
            "api_url": self.api_url,
            "authenticated": False,
            "api_accessible": False,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # Test authentication by getting a token
            token = await self._get_valid_token()
            results["authenticated"] = True
            results["token_expires_at"] = self._token_expires_at.isoformat()

            # Test API by making a simple search
            try:
                # Search for organizations (should return at least empty bundle)
                search_result = await self._make_fhir_request("GET", "Organization", params={"_count": "1"})
                results["api_accessible"] = True
                results["resource_type"] = search_result.get("resourceType")

            except SATUSEHATError as e:
                results["api_error"] = str(e)

        except SATUSEHATAuthError as e:
            results["auth_error"] = str(e)

        return results


# =============================================================================
# Client Factory
# =============================================================================

async def get_satusehat_client() -> SATUSEHATClient:
    """
    Get a configured SATUSEHAT client instance.

    Returns:
        Initialized SATUSEHAT client

    Raises:
        SATUSEHATError: If client credentials not configured
    """
    if not settings.SATUSEHAT_CLIENT_ID or not settings.SATUSEHAT_CLIENT_SECRET:
        raise SATUSEHATError(
            "SATUSEHAT credentials not configured. "
            "Set SATUSEHAT_CLIENT_ID and SATUSEHAT_CLIENT_SECRET in environment or config."
        )

    client = SATUSEHATClient()
    await client.__aenter__()
    return client
