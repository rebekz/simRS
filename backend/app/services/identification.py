"""Identification System Integration Service for STORY-024-09

This module provides services for:
- KTP-el (Electronic ID) verification
- BPJS card validation
- Face recognition verification
- Biometric data management

Python 3.5+ compatible
"""

import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.identification import (
    IDVerification, KTPData, BPJSCardValidation, FaceRecognition,
    BiometricData, BiometricVerification, IdentificationConfig,
    VerificationStatus, MatchScore
)


logger = logging.getLogger(__name__)


# =============================================================================
# Service Factory
# =============================================================================

_identification_service_instance = None


def get_identification_service(db: AsyncSession):
    """Get or create identification service instance"""
    global _identification_service_instance
    if _identification_service_instance is None:
        _identification_service_instance = IdentificationService(db)
    else:
        _identification_service_instance.db = db
    return _identification_service_instance


# =============================================================================
# KTP-el Verification Service
# =============================================================================

class KTPVerificationService(object):
    """KTP-el verification service

    Handles NIK verification through Dukcapil API.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def verify_nik(
        self,
        nik: str,
        full_name: str,
        date_of_birth: datetime,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Verify NIK through Dukcapil API

        Args:
            nik: 16-digit NIK
            full_name: Full name to verify
            date_of_birth: Date of birth to verify
            config: Optional configuration override

        Returns:
            Verification result with data and status
        """
        verification_id = "KTP-{}".format(datetime.utcnow().strftime("%Y%m%d%H%M%S"))

        try:
            # Validate NIK format
            if not self._validate_nik_format(nik):
                raise ValueError("Invalid NIK format. Must be 16 digits.")

            # Check cache first
            cached_data = await self._get_cached_ktp_data(nik)
            if cached_data:
                logger.info("Using cached KTP data for NIK: {}".format(nik))
                return self._build_verification_result(
                    verification_id,
                    cached_data,
                    from_cache=True
                )

            # Call Dukcapil API (mock implementation)
            api_response = await self._call_dukcapil_api(nik, config)

            # Parse response
            ktp_data = self._parse_dukcapil_response(api_response)

            # Verify matching data
            is_valid = self._verify_ktp_data(ktp_data, full_name, date_of_birth)

            # Store in cache
            await self._cache_ktp_data(ktp_data)

            # Create verification record
            await self._create_verification_record(
                verification_id,
                nik,
                ktp_data,
                is_valid
            )

            return self._build_verification_result(
                verification_id,
                ktp_data,
                is_valid=is_valid
            )

        except ValueError as e:
            logger.error("KTP verification failed: {}".format(e))
            raise
        except Exception as e:
            logger.error("KTP verification error: {}".format(e))
            # Create failed verification record
            await self._create_failed_verification_record(
                verification_id,
                nik,
                str(e)
            )
            raise

    def _validate_nik_format(self, nik: str) -> bool:
        """Validate NIK format (16 digits)"""
        return (
            nik is not None
            and len(nik) == 16
            and nik.isdigit()
        )

    async def _get_cached_ktp_data(self, nik: str) -> Optional[Dict[str, Any]]:
        """Get cached KTP data if available and not expired"""
        try:
            query = select(KTPData).where(
                and_(
                    KTPData.nik == nik,
                    KTPData.expires_at > datetime.utcnow()
                )
            )
            result = await self.db.execute(query)
            cached = result.scalar_one_or_none()

            if cached:
                return {
                    "nik": cached.nik,
                    "full_name": cached.full_name,
                    "place_of_birth": cached.place_of_birth,
                    "date_of_birth": cached.date_of_birth.isoformat() if cached.date_of_birth else None,
                    "gender": cached.gender,
                    "blood_type": cached.blood_type,
                    "address": cached.address,
                    "rt": cached.rt,
                    "rw": cached.rw,
                    "kelurahan": cached.kelurahan,
                    "kecamatan": cached.kecamatan,
                    "kabupaten_kota": cached.kabupaten_kota,
                    "province": cached.province,
                    "postal_code": cached.postal_code,
                    "marital_status": cached.marital_status,
                    "religion": cached.religion,
                    "occupation": cached.occupation,
                    "nationality": cached.nationality,
                    "is_valid": cached.is_valid,
                    "is_active": cached.is_active,
                    "kk_number": cached.kk_number,
                    "family_relationship": cached.family_relationship,
                    "family_members": cached.family_members,
                    "photo_url": cached.photo_url
                }
            return None

        except Exception as e:
            logger.error("Error getting cached KTP data: {}".format(e))
            return None

    async def _call_dukcapil_api(
        self,
        nik: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call Dukcapil API (mock implementation)

        In production, this would make an actual API call to Dukcapil.
        """
        # Mock response - in production, call actual API
        # This simulates a successful API response
        mock_response = {
            "nik": nik,
            "status": "success",
            "data": {
                "nik": nik,
                "nama": "WARGA NEGARA INDONESIA",
                "tempat_lahir": "JAKARTA",
                "tanggal_lahir": "1990-01-01",
                "jenis_kelamin": "LAKILAKI",
                "golongan_darah": "O",
                "alamat": "JL. CONTOH NO. 123",
                "rt": "001",
                "rw": "002",
                "kelurahan": "MENTENG",
                "kecamatan": "MENTENG",
                "kabupaten_kota": "JAKARTA PUSAT",
                "provinsi": "DKI JAKARTA",
                "kode_pos": "10310",
                "status_perkawinan": "BELUM KAWIN",
                "agama": "ISLAM",
                "pekerjaan": "KARYAWAN",
                "kewarganegaraan": "WNI",
                "berlaku_hingga": "SEUMUR HIDUP",
                "no_kk": "1234567890123456",
                "hubungan_keluarga": "KEPALA KELUARGA"
            }
        }

        # Simulate API delay
        import asyncio
        await asyncio.sleep(0.1)

        return mock_response

    def _parse_dukcapil_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Dukcapil API response"""
        if response.get("status") != "success":
            raise ValueError("Dukcapil API returned error: {}".format(
                response.get("message", "Unknown error")
            ))

        data = response.get("data", {})

        # Parse date of birth
        dob_str = data.get("tanggal_lahir")
        dob = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d")
            except ValueError:
                pass

        return {
            "nik": data.get("nik"),
            "full_name": data.get("nama"),
            "place_of_birth": data.get("tempat_lahir"),
            "date_of_birth": dob,
            "gender": data.get("jenis_kelamin"),
            "blood_type": data.get("golongan_darah"),
            "address": data.get("alamat"),
            "rt": data.get("rt"),
            "rw": data.get("rw"),
            "kelurahan": data.get("kelurahan"),
            "kecamatan": data.get("kecamatan"),
            "kabupaten_kota": data.get("kabupaten_kota"),
            "province": data.get("provinsi"),
            "postal_code": data.get("kode_pos"),
            "marital_status": data.get("status_perkawinan"),
            "religion": data.get("agama"),
            "occupation": data.get("pekerjaan"),
            "nationality": data.get("kewarganegaraan", "WNI"),
            "is_valid": True,
            "is_active": True,
            "kk_number": data.get("no_kk"),
            "family_relationship": data.get("hubungan_keluarga")
        }

    def _verify_ktp_data(
        self,
        ktp_data: Dict[str, Any],
        full_name: str,
        date_of_birth: datetime
    ) -> bool:
        """Verify KTP data matches provided information"""
        # Check name similarity (simple check - in production use fuzzy matching)
        ktp_name = ktp_data.get("full_name", "").upper().strip()
        provided_name = full_name.upper().strip()

        name_match = ktp_name == provided_name

        # Check date of birth
        ktp_dob = ktp_data.get("date_of_birth")
        dob_match = ktp_dob is not None and ktp_dob.date() == date_of_birth.date()

        return name_match and dob_match

    async def _cache_ktp_data(self, ktp_data: Dict[str, Any]) -> None:
        """Cache KTP data in database"""
        try:
            # Check if already exists
            query = select(KTPData).where(KTPData.nik == ktp_data["nik"])
            result = await self.db.execute(query)
            existing = result.scalar_one_or_none()

            cache_expiration = datetime.utcnow() + timedelta(days=30)

            if existing:
                # Update existing record
                existing.full_name = ktp_data.get("full_name")
                existing.place_of_birth = ktp_data.get("place_of_birth")
                existing.date_of_birth = ktp_data.get("date_of_birth")
                existing.gender = ktp_data.get("gender")
                existing.blood_type = ktp_data.get("blood_type")
                existing.address = ktp_data.get("address")
                existing.rt = ktp_data.get("rt")
                existing.rw = ktp_data.get("rw")
                existing.kelurahan = ktp_data.get("kelurahan")
                existing.kecamatan = ktp_data.get("kecamatan")
                existing.kabupaten_kota = ktp_data.get("kabupaten_kota")
                existing.province = ktp_data.get("province")
                existing.postal_code = ktp_data.get("postal_code")
                existing.marital_status = ktp_data.get("marital_status")
                existing.religion = ktp_data.get("religion")
                existing.occupation = ktp_data.get("occupation")
                existing.nationality = ktp_data.get("nationality", "WNI")
                existing.kk_number = ktp_data.get("kk_number")
                existing.family_relationship = ktp_data.get("family_relationship")
                existing.validation_date = datetime.utcnow()
                existing.expires_at = cache_expiration
                existing.updated_at = datetime.utcnow()
            else:
                # Create new record
                cached = KTPData(
                    nik=ktp_data["nik"],
                    full_name=ktp_data.get("full_name"),
                    place_of_birth=ktp_data.get("place_of_birth"),
                    date_of_birth=ktp_data.get("date_of_birth"),
                    gender=ktp_data.get("gender"),
                    blood_type=ktp_data.get("blood_type"),
                    address=ktp_data.get("address"),
                    rt=ktp_data.get("rt"),
                    rw=ktp_data.get("rw"),
                    kelurahan=ktp_data.get("kelurahan"),
                    kecamatan=ktp_data.get("kecamatan"),
                    kabupaten_kota=ktp_data.get("kabupaten_kota"),
                    province=ktp_data.get("province"),
                    postal_code=ktp_data.get("postal_code"),
                    marital_status=ktp_data.get("marital_status"),
                    religion=ktp_data.get("religion"),
                    occupation=ktp_data.get("occupation"),
                    nationality=ktp_data.get("nationality", "WNI"),
                    is_valid=ktp_data.get("is_valid", True),
                    is_active=ktp_data.get("is_active", True),
                    kk_number=ktp_data.get("kk_number"),
                    family_relationship=ktp_data.get("family_relationship"),
                    validation_date=datetime.utcnow(),
                    expires_at=cache_expiration,
                    data_source="dukcapil_api"
                )
                self.db.add(cached)

            await self.db.commit()

        except Exception as e:
            logger.error("Error caching KTP data: {}".format(e))
            await self.db.rollback()

    async def _create_verification_record(
        self,
        verification_id: str,
        nik: str,
        ktp_data: Dict[str, Any],
        is_valid: bool
    ) -> None:
        """Create verification record"""
        try:
            verification = IDVerification(
                verification_id=verification_id,
                verification_type="ktp_el",
                id_number=nik,
                id_name=ktp_data.get("full_name"),
                id_dob=ktp_data.get("date_of_birth"),
                id_gender=ktp_data.get("gender"),
                id_address=ktp_data.get("address"),
                verification_source="dukcapil",
                verification_method="api",
                status=VerificationStatus.VERIFIED if is_valid else VerificationStatus.NOT_VERIFIED,
                is_match=is_valid,
                verified_at=datetime.utcnow()
            )
            self.db.add(verification)
            await self.db.commit()

        except Exception as e:
            logger.error("Error creating verification record: {}".format(e))
            await self.db.rollback()

    async def _create_failed_verification_record(
        self,
        verification_id: str,
        nik: str,
        error_message: str
    ) -> None:
        """Create failed verification record"""
        try:
            verification = IDVerification(
                verification_id=verification_id,
                verification_type="ktp_el",
                id_number=nik,
                id_name="",
                verification_source="dukcapil",
                verification_method="api",
                status=VerificationStatus.FAILED,
                error_message=error_message
            )
            self.db.add(verification)
            await self.db.commit()

        except Exception as e:
            logger.error("Error creating failed verification record: {}".format(e))
            await self.db.rollback()

    def _build_verification_result(
        self,
        verification_id: str,
        ktp_data: Dict[str, Any],
        is_valid: bool = True,
        from_cache: bool = False
    ) -> Dict[str, Any]:
        """Build verification result response"""
        return {
            "verification_id": verification_id,
            "verification_type": "ktp_el",
            "status": "verified" if is_valid else "not_verified",
            "is_match": is_valid,
            "from_cache": from_cache,
            "data": ktp_data,
            "verified_at": datetime.utcnow().isoformat()
        }


# =============================================================================
# BPJS Card Validation Service
# =============================================================================

class BPJSValidationService(object):
    """BPJS card validation service

    Handles BPJS card validation through BPJS API.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate_bpjs_card(
        self,
        bpjs_card_number: str,
        nik: str,
        full_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate BPJS card

        Args:
            bpjs_card_number: 13-digit BPJS card number
            nik: NIK from BPJS card
            full_name: Full name from BPJS card
            config: Optional configuration override

        Returns:
            Validation result with membership details
        """
        validation_id = "BPJS-{}".format(datetime.utcnow().strftime("%Y%m%d%H%M%S"))

        try:
            # Validate BPJS card format
            if not self._validate_bpjs_format(bpjs_card_number):
                raise ValueError("Invalid BPJS card number. Must be 13 digits.")

            # Call BPJS API (mock implementation)
            api_response = await self._call_bpjs_api(bpjs_card_number, config)

            # Parse response
            bpjs_data = self._parse_bpjs_response(api_response)

            # Verify matching data
            is_valid = self._verify_bpjs_data(bpjs_data, nik, full_name)

            # Store validation record
            await self._create_validation_record(
                validation_id,
                bpjs_card_number,
                bpjs_data,
                is_valid
            )

            return self._build_validation_result(
                validation_id,
                bpjs_data,
                is_valid=is_valid
            )

        except ValueError as e:
            logger.error("BPJS validation failed: {}".format(e))
            raise
        except Exception as e:
            logger.error("BPJS validation error: {}".format(e))
            await self._create_failed_validation_record(
                validation_id,
                bpjs_card_number,
                str(e)
            )
            raise

    def _validate_bpjs_format(self, card_number: str) -> bool:
        """Validate BPJS card number format (13 digits)"""
        return (
            card_number is not None
            and len(card_number) == 13
            and card_number.isdigit()
        )

    async def _call_bpjs_api(
        self,
        card_number: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call BPJS API (mock implementation)"""
        # Mock response
        mock_response = {
            "status": "success",
            "data": {
                "nomor_kartu": card_number,
                "nama": "WARGA NEGARA INDONESIA",
                "nik": "1234567890123456",
                "peserta": {
                    "status_kepesertaan": "AKTIF",
                    "tgl_tmt": "2020-01-01",
                    "tgl_akhir": "2025-12-31",
                    "jenis_peserta": "PBI",
                    "kelas_rawat": "Kelas 3"
                },
                "faskes": {
                    "faskes_tk_1": "PUSKESMAS MENTENG",
                    "faskes_tk_2": "RS UMUM PUSAT",
                    "faskes_tk_3": "RS UMUM PUSAT"
                },
                "informasi": {
                    "no_kk": "1234567890123456",
                    "hubungan_keluarga": "KEPALA KELUARGA"
                }
            }
        }

        # Simulate API delay
        import asyncio
        await asyncio.sleep(0.1)

        return mock_response

    def _parse_bpjs_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse BPJS API response"""
        if response.get("status") != "success":
            raise ValueError("BPJS API returned error")

        data = response.get("data", {})
        peserta = data.get("peserta", {})
        faskes = data.get("faskes", {})
        informasi = data.get("informasi", {})

        # Parse dates
        tgl_tmt = self._parse_date(peserta.get("tgl_tmt"))
        tgl_akhir = self._parse_date(peserta.get("tgl_akhir"))

        return {
            "bpjs_card_number": data.get("nomor_kartu"),
            "bpjs_name": data.get("nama"),
            "nik": data.get("nik"),
            "membership_status": peserta.get("status_kepesertaan"),
            "membership_start_date": tgl_tmt,
            "membership_end_date": tgl_akhir,
            "membership_type": peserta.get("jenis_peserta"),
            "membership_tier": peserta.get("kelas_rawat"),
            "faskes_tier_1": faskes.get("faskes_tk_1"),
            "faskes_tier_2": faskes.get("faskes_tk_2"),
            "faskes_tier_3": faskes.get("faskes_tk_3"),
            "kk_number": informasi.get("no_kk"),
            "family_relationship": informasi.get("hubungan_keluarga"),
            "is_head_of_family": informasi.get("hubungan_keluarga") == "KEPALA KELUARGA"
        }

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None

    def _verify_bpjs_data(
        self,
        bpjs_data: Dict[str, Any],
        nik: str,
        full_name: str
    ) -> bool:
        """Verify BPJS data matches provided information"""
        # Check NIK
        nik_match = bpjs_data.get("nik") == nik

        # Check name (simple check - use fuzzy matching in production)
        bpjs_name = bpjs_data.get("bpjs_name", "").upper().strip()
        provided_name = full_name.upper().strip()
        name_match = bpjs_name == provided_name

        # Check membership status
        is_active = bpjs_data.get("membership_status") == "AKTIF"

        return nik_match and name_match and is_active

    async def _create_validation_record(
        self,
        validation_id: str,
        card_number: str,
        bpjs_data: Dict[str, Any],
        is_valid: bool
    ) -> None:
        """Create validation record"""
        try:
            validation = BPJSCardValidation(
                validation_id=validation_id,
                bpjs_card_number=card_number,
                bpjs_name=bpjs_data.get("bpjs_name"),
                nik=bpjs_data.get("nik"),
                membership_tier=bpjs_data.get("membership_tier"),
                membership_type=bpjs_data.get("membership_type"),
                membership_status=bpjs_data.get("membership_status"),
                membership_start_date=bpjs_data.get("membership_start_date"),
                membership_end_date=bpjs_data.get("membership_end_date"),
                is_head_of_family=bpjs_data.get("is_head_of_family", False),
                family_head_nik=bpjs_data.get("nik") if bpjs_data.get("is_head_of_family") else None,
                faskes_tier_1=bpjs_data.get("faskes_tier_1"),
                faskes_tier_2=bpjs_data.get("faskes_tier_2"),
                faskes_tier_3=bpjs_data.get("faskes_tier_3"),
                default_faskes=bpjs_data.get("faskes_tier_1"),
                is_verified=is_valid,
                verification_date=datetime.utcnow(),
                verification_source="bpjs_api"
            )
            self.db.add(validation)
            await self.db.commit()

        except Exception as e:
            logger.error("Error creating BPJS validation record: {}".format(e))
            await self.db.rollback()

    async def _create_failed_validation_record(
        self,
        validation_id: str,
        card_number: str,
        error_message: str
    ) -> None:
        """Create failed validation record"""
        try:
            validation = BPJSCardValidation(
                validation_id=validation_id,
                bpjs_card_number=card_number,
                bpjs_name="",
                nik="",
                membership_tier="",
                membership_status="FAILED",
                error_message=error_message
            )
            self.db.add(validation)
            await self.db.commit()

        except Exception as e:
            logger.error("Error creating failed BPJS validation record: {}".format(e))
            await self.db.rollback()

    def _build_validation_result(
        self,
        validation_id: str,
        bpjs_data: Dict[str, Any],
        is_valid: bool = True
    ) -> Dict[str, Any]:
        """Build validation result response"""
        return {
            "validation_id": validation_id,
            "validation_type": "bpjs_card",
            "status": "verified" if is_valid else "not_verified",
            "is_match": is_valid,
            "data": bpjs_data,
            "verified_at": datetime.utcnow().isoformat()
        }


# =============================================================================
# Face Recognition Service
# =============================================================================

class FaceRecognitionService(object):
    """Face recognition service

    Handles face verification using facial recognition.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def verify_face(
        self,
        source_image_data: str,
        captured_image_data: str,
        patient_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Verify face match between source and captured images

        Args:
            source_image_data: Base64 source image (from ID)
            captured_image_data: Base64 captured image
            patient_id: Optional patient ID

        Returns:
            Verification result with match score
        """
        verification_id = "FACE-{}".format(datetime.utcnow().strftime("%Y%m%d%H%M%S"))

        try:
            # Detect faces in images
            source_faces = await self._detect_faces(source_image_data)
            captured_faces = await self._detect_faces(captured_image_data)

            if len(source_faces) == 0:
                raise ValueError("No face detected in source image")
            if len(captured_faces) == 0:
                raise ValueError("No face detected in captured image")
            if len(source_faces) > 1:
                raise ValueError("Multiple faces detected in source image")
            if len(captured_faces) > 1:
                raise ValueError("Multiple faces detected in captured image")

            # Extract face embeddings
            source_embedding = await self._extract_face_embedding(source_image_data, source_faces[0])
            captured_embedding = await self._extract_face_embedding(captured_image_data, captured_faces[0])

            # Compare faces
            match_result = await self._compare_faces(source_embedding, captured_embedding)

            # Liveness detection
            liveness_result = await self._detect_liveness(captured_image_data)

            # Create verification record
            await self._create_face_verification_record(
                verification_id,
                source_image_data,
                captured_image_data,
                match_result,
                liveness_result,
                patient_id
            )

            return self._build_face_verification_result(
                verification_id,
                match_result,
                liveness_result
            )

        except Exception as e:
            logger.error("Face verification error: {}".format(e))
            raise

    async def _detect_faces(self, image_data: str) -> List[Dict[str, Any]]:
        """Detect faces in image (mock implementation)"""
        # Mock implementation - in production use face detection library
        import asyncio
        await asyncio.sleep(0.05)

        # Return mock face detection result
        return [{
            "bounding_box": {"x": 100, "y": 100, "width": 200, "height": 200},
            "landmarks": {},
            "confidence": 0.99
        }]

    async def _extract_face_embedding(
        self,
        image_data: str,
        face: Dict[str, Any]
    ) -> List[float]:
        """Extract face embedding (mock implementation)"""
        # Mock implementation - in production use face recognition library
        import asyncio
        await asyncio.sleep(0.05)

        # Return mock embedding (128-dimensional)
        return [0.1] * 128

    async def _compare_faces(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> Dict[str, Any]:
        """Compare two face embeddings"""
        # Mock implementation - calculate cosine similarity
        import asyncio
        await asyncio.sleep(0.02)

        # Simple mock comparison
        # In production, use actual cosine similarity or euclidean distance
        match_score = 0.92  # Mock score

        # Determine confidence level
        if match_score >= MatchScore.EXCELLENT:
            confidence = "excellent"
        elif match_score >= MatchScore.GOOD:
            confidence = "good"
        elif match_score >= MatchScore.FAIR:
            confidence = "fair"
        else:
            confidence = "poor"

        return {
            "match_score": match_score,
            "match_confidence": confidence,
            "is_match": match_score >= MatchScore.GOOD,
            "similarity_score": match_score
        }

    async def _detect_liveness(self, image_data: str) -> Dict[str, Any]:
        """Detect liveness (mock implementation)"""
        # Mock implementation
        import asyncio
        await asyncio.sleep(0.03)

        return {
            "liveness_check": True,
            "liveness_score": 0.95,
            "is_live": True,
            "spoof_detected": False
        }

    async def _create_face_verification_record(
        self,
        verification_id: str,
        source_image_data: str,
        captured_image_data: str,
        match_result: Dict[str, Any],
        liveness_result: Dict[str, Any],
        patient_id: Optional[int]
    ) -> None:
        """Create face verification record"""
        try:
            verification = FaceRecognition(
                verification_id=verification_id,
                patient_id=patient_id,
                source_image_data=source_image_data,
                captured_image_data=captured_image_data,
                face_detected=True,
                face_count=1,
                match_score=match_result.get("match_score"),
                match_confidence=match_result.get("match_confidence"),
                is_match=match_result.get("is_match"),
                similarity_score=match_result.get("similarity_score"),
                liveness_check=liveness_result.get("liveness_check", False),
                liveness_score=liveness_result.get("liveness_score"),
                is_live=liveness_result.get("is_live"),
                spoof_detection=liveness_result,
                verified_at=datetime.utcnow()
            )
            self.db.add(verification)
            await self.db.commit()

        except Exception as e:
            logger.error("Error creating face verification record: {}".format(e))
            await self.db.rollback()

    def _build_face_verification_result(
        self,
        verification_id: str,
        match_result: Dict[str, Any],
        liveness_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build face verification result"""
        return {
            "verification_id": verification_id,
            "verification_type": "face_recognition",
            "status": "verified" if match_result.get("is_match") else "not_verified",
            "is_match": match_result.get("is_match"),
            "match_score": match_result.get("match_score"),
            "match_confidence": match_result.get("match_confidence"),
            "liveness_check": liveness_result.get("liveness_check"),
            "is_live": liveness_result.get("is_live"),
            "verified_at": datetime.utcnow().isoformat()
        }


# =============================================================================
# Main Identification Service
# =============================================================================

class IdentificationService(object):
    """Main identification service

    Coordinates all identification verification services.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ktp_service = KTPVerificationService(db)
        self.bpjs_service = BPJSValidationService(db)
        self.face_service = FaceRecognitionService(db)

    async def verify_ktp(
        self,
        nik: str,
        full_name: str,
        date_of_birth: datetime,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Verify KTP through Dukcapil API"""
        return await self.ktp_service.verify_nik(nik, full_name, date_of_birth, config)

    async def verify_bpjs_card(
        self,
        bpjs_card_number: str,
        nik: str,
        full_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Verify BPJS card through BPJS API"""
        return await self.bpjs_service.validate_bpjs_card(bpjs_card_number, nik, full_name, config)

    async def verify_face(
        self,
        source_image_data: str,
        captured_image_data: str,
        patient_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Verify face match"""
        return await self.face_service.verify_face(source_image_data, captured_image_data, patient_id)

    async def get_verification_history(
        self,
        patient_id: Optional[int] = None,
        verification_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get verification history"""
        try:
            query = select(IDVerification)

            filters = []
            if patient_id:
                filters.append(IDVerification.patient_id == patient_id)
            if verification_type:
                filters.append(IDVerification.verification_type == verification_type)

            if filters:
                query = query.where(and_(*filters))

            query = query.order_by(IDVerification.created_at.desc()).limit(limit)

            result = await self.db.execute(query)
            verifications = result.scalars().all()

            return [
                {
                    "verification_id": v.verification_id,
                    "verification_type": v.verification_type,
                    "id_number": v.id_number,
                    "id_name": v.id_name,
                    "status": v.status,
                    "is_match": v.is_match,
                    "match_score": v.match_score,
                    "match_confidence": v.match_confidence,
                    "verified_at": v.verified_at.isoformat() if v.verified_at else None,
                    "created_at": v.created_at.isoformat()
                }
                for v in verifications
            ]

        except Exception as e:
            logger.error("Error getting verification history: {}".format(e))
            raise
