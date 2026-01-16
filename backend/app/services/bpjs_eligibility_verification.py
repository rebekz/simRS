"""BPJS Eligibility Verification Service for STORY-008: BPJS Eligibility Verification

This module provides services for:
- BPJS eligibility verification with VClaim API integration
- Eligibility result caching for performance
- Eligibility history tracking
- Manual override workflow
- Error handling and retry logic
- Indonesian error messages

Python 3.5+ compatible
"""

import logging
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.models.bpjs_eligibility import BPJSEligibilityCheck
from app.models.patient import Patient
from app.models.user import User
from app.models.audit_log import AuditLog
from app.services.bpjs_vclaim import BPJSVClaimClient, BPJSVClaimError
from app.core.redis import redis_client


logger = logging.getLogger(__name__)


class EligibilityCheckError(Exception):
    """Eligibility check error"""
    pass


class BPJSEligibilityService(object):
    """Service for BPJS eligibility verification operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def verify_eligibility_by_card(
        self,
        card_number: str,
        sep_date: date,
        patient_id: Optional[int] = None,
        use_cache: bool = True,
        verified_by: Optional[int] = None,
    ) -> Dict[str, any]:
        """Verify BPJS eligibility by card number

        Args:
            card_number: BPJS card number (13 digits)
            sep_date: SEP date (YYYY-MM-DD)
            patient_id: Patient ID (optional, for history tracking)
            use_cache: Whether to use cached results
            verified_by: User ID performing verification

        Returns:
            Eligibility verification result

        Raises:
            EligibilityCheckError: If verification fails
        """
        # Validate card number format
        if not card_number or len(card_number) != 13:
            raise EligibilityCheckError("Nomor kartu BPJS harus 13 digit")

        # Check cache first
        if use_cache:
            cached = await self._get_cached_eligibility(card_number, sep_date)
            if cached:
                logger.info("Using cached eligibility for card {}".format(card_number))
                return self._build_eligibility_response(cached, is_cached=True)

        # Call BPJS API
        bpjs_client = BPJSVClaimClient()

        try:
            api_result = await bpjs_client.check_eligibility_by_card(
                card_number=card_number,
                sep_date=sep_date
            )

            # Save to database
            check_record = await self._save_eligibility_check(
                patient_id=patient_id,
                search_type="card",
                search_value=card_number,
                sep_date=sep_date,
                api_result=api_result,
                verified_by=verified_by,
                verification_method="api",
            )

            # Cache the result
            await self._cache_eligibility(card_number, sep_date, api_result)

            return self._build_eligibility_response(check_record, is_cached=False)

        except BPJSVClaimError as e:
            # Create error record
            error_record = await self._save_eligibility_error(
                patient_id=patient_id,
                search_type="card",
                search_value=card_number,
                error=e,
                verified_by=verified_by,
            )

            logger.error("BPJS API error: {}".format(e.message))

            raise EligibilityCheckError(
                "Gagal memverifikasi eligibility: {}".format(e.message)
            )

    async def verify_eligibility_by_nik(
        self,
        nik: str,
        sep_date: date,
        patient_id: Optional[int] = None,
        use_cache: bool = True,
        verified_by: Optional[int] = None,
    ) -> Dict[str, any]:
        """Verify BPJS eligibility by NIK

        Args:
            nik: NIK (16 digits)
            sep_date: SEP date (YYYY-MM-DD)
            patient_id: Patient ID (optional, for history tracking)
            use_cache: Whether to use cached results
            verified_by: User ID performing verification

        Returns:
            Eligibility verification result

        Raises:
            EligibilityCheckError: If verification fails
        """
        # Validate NIK format
        if not nik or len(nik) != 16 or not nik.isdigit():
            raise EligibilityCheckError("NIK harus 16 digit angka")

        # Check cache first
        if use_cache:
            cached = await self._get_cached_eligibility(nik, sep_date)
            if cached:
                logger.info("Using cached eligibility for NIK {}".format(nik))
                return self._build_eligibility_response(cached, is_cached=True)

        # Call BPJS API
        bpjs_client = BPJSVClaimClient()

        try:
            api_result = await bpjs_client.check_eligibility_by_nik(
                nik=nik,
                sep_date=sep_date
            )

            # Save to database
            check_record = await self._save_eligibility_check(
                patient_id=patient_id,
                search_type="nik",
                search_value=nik,
                sep_date=sep_date,
                api_result=api_result,
                verified_by=verified_by,
                verification_method="api",
            )

            # Cache the result
            await self._cache_eligibility(nik, sep_date, api_result)

            return self._build_eligibility_response(check_record, is_cached=False)

        except BPJSVClaimError as e:
            # Create error record
            error_record = await self._save_eligibility_error(
                patient_id=patient_id,
                search_type="nik",
                search_value=nik,
                error=e,
                verified_by=verified_by,
            )

            logger.error("BPJS API error: {}".format(e.message))

            raise EligibilityCheckError(
                "Gagal memverifikasi eligibility: {}".format(e.message)
            )

    async def create_manual_override(
        self,
        patient_id: int,
        card_number: Optional[str] = None,
        nik: Optional[str] = None,
        is_eligible: bool = True,
        reason: str = None,
        override_by: int = None,
        approved_by: int = None,
    ) -> Dict[str, any]:
        """Create manual eligibility verification override

        Args:
            patient_id: Patient ID
            card_number: BPJS card number
            nik: NIK
            is_eligible: Eligibility status
            reason: Override reason
            override_by: User ID requesting override
            approved_by: User ID approving override

        Returns:
            Override record

        Raises:
            EligibilityCheckError: If validation fails
        """
        # Validate
        if not card_number and not nik:
            raise EligibilityCheckError("Nomor kartu atau NIK harus diisi")

        if not reason:
            raise EligibilityCheckError("Alasan override harus diisi")

        # Create override record
        override_record = BPJSEligibilityCheck(
            patient_id=patient_id,
            search_type="card" if card_number else "nik",
            search_value=card_number or nik,
            is_eligible=is_eligible,
            response_code="MANUAL",
            response_message="Manual override",
            verification_method="override",
            is_manual_override=True,
            override_reason=reason,
            override_approved_by=approved_by,
            override_approved_at=datetime.utcnow(),
            verified_by=override_by,
        )

        self.db.add(override_record)
        await self.db.flush()

        # Create audit log
        await self._create_override_audit_log(
            patient_id,
            card_number or nik,
            is_eligible,
            reason,
            approved_by,
        )

        logger.info(
            "Manual override created for patient {} by user {}".format(
                patient_id,
                approved_by
            )
        )

        return {
            "id": override_record.id,
            "patient_id": patient_id,
            "is_eligible": is_eligible,
            "search_type": override_record.search_type,
            "search_value": override_record.search_value,
            "reason": reason,
            "approved_by": approved_by,
            "approved_at": override_record.override_approved_at.isoformat() if override_record.override_approved_at else None,
        }

    async def get_eligibility_history(
        self,
        patient_id: int,
        limit: int = 20,
    ) -> List[Dict[str, any]]:
        """Get eligibility verification history for patient

        Args:
            patient_id: Patient ID
            limit: Maximum records to return

        Returns:
            List of eligibility checks
        """
        query = select(BPJSEligibilityCheck).where(
            BPJSEligibilityCheck.patient_id == patient_id
        ).order_by(
            desc(BPJSEligibilityCheck.verified_at)
        ).limit(limit)

        result = await self.db.execute(query)
        checks = result.scalars().all()

        return [
            {
                "id": c.id,
                "search_type": c.search_type,
                "search_value": c.search_value,
                "is_eligible": c.is_eligible,
                "response_code": c.response_code,
                "response_message": c.response_message,
                "verification_method": c.verification_method,
                "is_manual_override": c.is_manual_override,
                "verified_at": c.verified_at.isoformat() if c.verified_at else None,
                "participant_info": c.participant_info,
            }
            for c in checks
        ]

    async def get_eligibility_status(
        self,
        card_number: str = None,
        nik: str = None,
    ) -> Dict[str, any]:
        """Get current eligibility status from recent checks

        Args:
            card_number: BPJS card number
            nik: NIK

        Returns:
            Current eligibility status

        Raises:
            EligibilityCheckError: If neither card nor NIK provided
        """
        if not card_number and not nik:
            raise EligibilityCheckError("Nomor kartu atau NIK harus diisi")

        search_value = card_number or nik
        search_type = "card" if card_number else "nik"

        # Get most recent check
        query = select(BPJSEligibilityCheck).where(
            and_(
                BPJSEligibilityCheck.search_type == search_type,
                BPJSEligibilityCheck.search_value == search_value,
            )
        ).order_by(
            desc(BPJSEligibilityCheck.verified_at)
        )

        result = await self.db.execute(query)
        check = result.scalar_one_or_none()

        if not check:
            return {
                "has_verification": False,
                "is_eligible": None,
                "last_verified": None,
                "verification_method": None,
            }

        # Check if result is still valid (24 hours)
        is_valid = False
        if check.verified_at:
            expiry_time = check.verified_at + timedelta(hours=24)
            is_valid = datetime.utcnow() < expiry_time

        return {
            "has_verification": True,
            "is_eligible": check.is_eligible,
            "is_valid": is_valid,
            "last_verified": check.verified_at.isoformat() if check.verified_at else None,
            "verification_method": check.verification_method,
            "is_manual_override": check.is_manual_override,
            "participant_info": check.participant_info,
        }

    async def get_eligibility_statistics(
        self,
        start_date: date = None,
        end_date: date = None,
    ) -> Dict[str, any]:
        """Get eligibility verification statistics

        Args:
            start_date: Start date (default: today)
            end_date: End date (default: today)

        Returns:
            Eligibility statistics
        """
        if not start_date:
            start_date = date.today()
        if not end_date:
            end_date = date.today()

        # Total checks
        total_query = select(func.count()).select_from(BPJSEligibilityCheck).where(
            and_(
                BPJSEligibilityCheck.verified_at >= start_date,
                BPJSEligibilityCheck.verified_at < end_date + timedelta(days=1),
            )
        )

        total_result = await self.db.execute(total_query)
        total_checks = total_result.scalar() or 0

        # Eligible checks
        eligible_query = select(func.count()).select_from(BPJSEligibilityCheck).where(
            and_(
                BPJSEligibilityCheck.verified_at >= start_date,
                BPJSEligibilityCheck.verified_at < end_date + timedelta(days=1),
                BPJSEligibilityCheck.is_eligible == True,
            )
        )

        eligible_result = await self.db.execute(eligible_query)
        eligible_checks = eligible_result.scalar() or 0

        # Ineligible checks
        ineligible_checks = total_checks - eligible_checks

        # Manual overrides
        override_query = select(func.count()).select_from(BPJSEligibilityCheck).where(
            and_(
                BPJSEligibilityCheck.verified_at >= start_date,
                BPJSEligibilityCheck.verified_at < end_date + timedelta(days=1),
                BPJSEligibilityCheck.is_manual_override == True,
            )
        )

        override_result = await self.db.execute(override_query)
        override_count = override_result.scalar() or 0

        # API errors
        error_query = select(func.count()).select_from(BPJSEligibilityCheck).where(
            and_(
                BPJSEligibilityCheck.verified_at >= start_date,
                BPJSEligibilityCheck.verified_at < end_date + timedelta(days=1),
                BPJSEligibilityCheck.api_error.isnot(None),
            )
        )

        error_result = await self.db.execute(error_query)
        error_count = error_result.scalar() or 0

        return {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_checks": total_checks,
            "eligible_checks": eligible_checks,
            "ineligible_checks": ineligible_checks,
            "manual_overrides": override_count,
            "api_errors": error_count,
            "success_rate": round(float(eligible_checks) / total_checks * 100, 2) if total_checks > 0 else 0,
        }

    # ==============================================================================
    # Private Helper Methods
    # ==============================================================================

    async def _get_cached_eligibility(
        self,
        search_value: str,
        sep_date: date,
    ) -> Optional[Dict[str, any]]:
        """Get cached eligibility result

        Args:
            search_value: Card number or NIK
            sep_date: SEP date

        Returns:
            Cached result or None
        """
        cache_key = "bpjs:eligibility:{}:{}".format(search_value, sep_date.isoformat())

        try:
            cached_data = redis_client.get(cache_key)

            if cached_data:
                import json
                return json.loads(cached_data)

        except Exception as e:
            logger.warning("Error getting cached eligibility: {}".format(e))

        return None

    async def _cache_eligibility(
        self,
        search_value: str,
        sep_date: date,
        api_result: Dict[str, any],
    ):
        """Cache eligibility result

        Args:
            search_value: Card number or NIK
            sep_date: SEP date
            api_result: API result to cache
        """
        cache_key = "bpjs:eligibility:{}:{}".format(search_value, sep_date.isoformat())
        cache_ttl = 24 * 60 * 60  # 24 hours

        try:
            import json
            redis_client.setex(
                cache_key,
                cache_ttl,
                json.dumps(api_result)
            )

            logger.info("Cached eligibility result for {}".format(search_value))

        except Exception as e:
            logger.warning("Error caching eligibility: {}".format(e))

    async def _save_eligibility_check(
        self,
        patient_id: Optional[int],
        search_type: str,
        search_value: str,
        sep_date: date,
        api_result: Dict[str, any],
        verified_by: Optional[int],
        verification_method: str,
    ) -> BPJSEligibilityCheck:
        """Save eligibility check to database

        Args:
            patient_id: Patient ID
            search_type: Search type (card or nik)
            search_value: Card number or NIK
            sep_date: SEP date
            api_result: API result
            verified_by: User ID
            verification_method: Verification method

        Returns:
            Created BPJSEligibilityCheck record
        """
        check_record = BPJSEligibilityCheck(
            patient_id=patient_id,
            search_type=search_type,
            search_value=search_value,
            is_eligible=api_result.get("is_eligible", False),
            response_code=api_result.get("code"),
            response_message=api_result.get("message"),
            participant_info=api_result.get("participant_info"),
            verification_method=verification_method,
            verified_by=verified_by,
        )

        self.db.add(check_record)
        await self.db.flush()

        logger.info(
            "Eligibility check saved: {} - {}".format(
                search_type,
                search_value
            )
        )

        return check_record

    async def _save_eligibility_error(
        self,
        patient_id: Optional[int],
        search_type: str,
        search_value: str,
        error: BPJSVClaimError,
        verified_by: Optional[int],
    ) -> BPJSEligibilityCheck:
        """Save eligibility check error to database

        Args:
            patient_id: Patient ID
            search_type: Search type (card or nik)
            search_value: Card number or NIK
            error: BPJS API error
            verified_by: User ID

        Returns:
            Created BPJSEligibilityCheck record
        """
        check_record = BPJSEligibilityCheck(
            patient_id=patient_id,
            search_type=search_type,
            search_value=search_value,
            is_eligible=False,
            response_code=error.code,
            response_message=error.message,
            verification_method="api",
            verified_by=verified_by,
            api_error=error.details or error.message,
            api_error_code=error.code,
        )

        self.db.add(check_record)
        await self.db.flush()

        return check_record

    def _build_eligibility_response(
        self,
        check: BPJSEligibilityCheck,
        is_cached: bool,
    ) -> Dict[str, any]:
        """Build eligibility response from check record

        Args:
            check: Eligibility check record
            is_cached: Whether result was from cache

        Returns:
            Formatted response
        """
        participant_info = check.participant_info or {}

        return {
            "is_eligible": check.is_eligible,
            "response_code": check.response_code,
            "response_message": check.response_message,
            "participant_info": {
                "nama": participant_info.get("nama"),
                "no_kartu": participant_info.get("no_kartu"),
                "nik": participant_info.get("nik"),
                "faskes_tingkat_1": participant_info.get("faskes_tingkat_1"),
                "faskes_rujukan": participant_info.get("faskes_rujukan"),
                "kelas_rawat": participant_info.get("kelas_rawat"),
                "status_kepesertaan": participant_info.get("status_kepesertaan"),
                "tgl_cetak_kartu": participant_info.get("tgl_cetak_kartu"),
                "tgl_tat": participant_info.get("tgl_tat"),
                "tgl_aktif": participant_info.get("tgl_aktif"),
            },
            "verification_method": check.verification_method,
            "is_manual_override": check.is_manual_override,
            "verified_at": check.verified_at.isoformat() if check.verified_at else None,
            "is_cached": is_cached,
            "check_id": check.id,
        }

    async def _create_override_audit_log(
        self,
        patient_id: int,
        search_value: str,
        is_eligible: bool,
        reason: str,
        approved_by: int,
    ):
        """Create audit log for manual override

        Args:
            patient_id: Patient ID
            search_value: Card number or NIK
            is_eligible: Eligibility status
            reason: Override reason
            approved_by: User ID who approved
        """
        # Get user info
        query = select(User).where(User.id == approved_by)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        username = user.username if user else "system"

        audit_log = AuditLog(
            user_id=approved_by,
            username=username,
            action="OVERRIDE",
            resource_type="BPJSEligibility",
            resource_id=search_value,
            request_path="/bpjs-verification/override",
            request_method="POST",
            success=True,
            additional_data={
                "patient_id": patient_id,
                "is_eligible": is_eligible,
                "reason": reason,
            },
        )

        self.db.add(audit_log)
        await self.db.flush()


# Factory function
def get_bpjs_eligibility_service(db: AsyncSession) -> BPJSEligibilityService:
    """Get BPJS eligibility service"""
    return BPJSEligibilityService(db)
