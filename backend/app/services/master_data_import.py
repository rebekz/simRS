"""
Master Data Import Service

This module provides utilities for importing master data from various sources
including ICD-10, LOINC, and other reference data.
"""

import csv
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.master_data import (
    ICD10Code,
    LOINCCode,
    DrugFormulary,
    ProcedureCode,
)
from backend.app.schemas.master_data import (
    DataImportRequest,
    DataImportResponse,
)


class MasterDataImportError(Exception):
    """Custom exception for master data import errors."""
    pass


class MasterDataImporter:
    """
    Master data importer with batch processing and error handling.
    """

    def __init__(self, db: AsyncSession, batch_size: int = 100):
        """
        Initialize importer.

        Args:
            db: Database session
            batch_size: Number of records to process per batch
        """
        self.db = db
        self.batch_size = batch_size
        self.errors = []
        self.success_count = 0
        self.failed_count = 0

    async def import_icd10_codes(
        self,
        data: List[Dict[str, Any]],
        overwrite: bool = False,
    ) -> DataImportResponse:
        """
        Import ICD-10 codes from data list.

        Args:
            data: List of ICD-10 code dictionaries
            overwrite: Whether to overwrite existing codes

        Returns:
            Import response with statistics
        """
        start_time = time.time()
        total_records = len(data)

        for i, record in enumerate(data):
            try:
                # Check if code already exists
                existing = await self.db.execute(
                    select(ICD10Code).where(ICD10Code.code == record.get("code"))
                )
                existing_code = existing.scalar_one_or_none()

                if existing_code:
                    if overwrite:
                        # Update existing record
                        for key, value in record.items():
                            if hasattr(existing_code, key):
                                setattr(existing_code, key, value)
                        self.success_count += 1
                    else:
                        # Skip existing record
                        continue
                else:
                    # Create new record
                    db_code = ICD10Code(**record)
                    self.db.add(db_code)
                    self.success_count += 1

                # Commit batch
                if (i + 1) % self.batch_size == 0:
                    await self.db.commit()

            except Exception as e:
                self.failed_count += 1
                self.errors.append("Record {}: {}".format(i, str(e)))

        # Final commit
        await self.db.commit()

        return DataImportResponse(
            data_type="icd10",
            total_records=total_records,
            success_count=self.success_count,
            failed_count=self.failed_count,
            errors=self.errors,
            import_time_seconds=time.time() - start_time,
        )

    async def import_icd10_from_csv(
        self,
        file_path: str,
        overwrite: bool = False,
    ) -> DataImportResponse:
        """
        Import ICD-10 codes from CSV file.

        Expected CSV format:
        code,code_full,chapter,block,description_indonesian,description_english,severity,notes,is_common

        Args:
            file_path: Path to CSV file
            overwrite: Whether to overwrite existing codes

        Returns:
            Import response with statistics
        """
        data = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert boolean fields
                if "is_common" in row:
                    row["is_common"] = row["is_common"].lower() in ("true", "1", "yes")
                data.append(row)

        return await self.import_icd10_codes(data, overwrite)

    async def import_loinc_codes(
        self,
        data: List[Dict[str, Any]],
        overwrite: bool = False,
    ) -> DataImportResponse:
        """
        Import LOINC codes from data list.

        Args:
            data: List of LOINC code dictionaries
            overwrite: Whether to overwrite existing codes

        Returns:
            Import response with statistics
        """
        start_time = time.time()
        total_records = len(data)

        for i, record in enumerate(data):
            try:
                # Check if code already exists
                existing = await self.db.execute(
                    select(LOINCCode).where(LOINCCode.loinc_num == record.get("loinc_num"))
                )
                existing_code = existing.scalar_one_or_none()

                if existing_code:
                    if overwrite:
                        # Update existing record
                        for key, value in record.items():
                            if hasattr(existing_code, key):
                                setattr(existing_code, key, value)
                        self.success_count += 1
                    else:
                        # Skip existing record
                        continue
                else:
                    # Create new record
                    db_code = LOINCCode(**record)
                    self.db.add(db_code)
                    self.success_count += 1

                # Commit batch
                if (i + 1) % self.batch_size == 0:
                    await self.db.commit()

            except Exception as e:
                self.failed_count += 1
                self.errors.append("Record {}: {}".format(i, str(e)))

        # Final commit
        await self.db.commit()

        return DataImportResponse(
            data_type="loinc",
            total_records=total_records,
            success_count=self.success_count,
            failed_count=self.failed_count,
            errors=self.errors,
            import_time_seconds=time.time() - start_time,
        )

    async def import_loinc_from_csv(
        self,
        file_path: str,
        overwrite: bool = False,
    ) -> DataImportResponse:
        """
        Import LOINC codes from CSV file.

        Expected CSV format:
        loinc_num,component,property,time_aspect,system,scale_type,method_type,
        class_name,status,short_name,long_common_name,example_units,is_common

        Args:
            file_path: Path to CSV file
            overwrite: Whether to overwrite existing codes

        Returns:
            Import response with statistics
        """
        data = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert boolean fields
                if "is_common" in row:
                    row["is_common"] = row["is_common"].lower() in ("true", "1", "yes")
                data.append(row)

        return await self.import_loinc_codes(data, overwrite)

    async def import_drugs(
        self,
        data: List[Dict[str, Any]],
        overwrite: bool = False,
    ) -> DataImportResponse:
        """
        Import drug formulary from data list.

        Args:
            data: List of drug dictionaries
            overwrite: Whether to overwrite existing drugs

        Returns:
            Import response with statistics
        """
        start_time = time.time()
        total_records = len(data)

        for i, record in enumerate(data):
            try:
                # Check if drug already exists by generic name and strength
                existing = await self.db.execute(
                    select(DrugFormulary).where(
                        DrugFormulary.generic_name == record.get("generic_name"),
                        DrugFormulary.strength == record.get("strength"),
                    )
                )
                existing_drug = existing.scalar_one_or_none()

                if existing_drug:
                    if overwrite:
                        # Update existing record
                        for key, value in record.items():
                            if hasattr(existing_drug, key):
                                setattr(existing_drug, key, value)
                        self.success_count += 1
                    else:
                        # Skip existing record
                        continue
                else:
                    # Create new record
                    db_drug = DrugFormulary(**record)
                    self.db.add(db_drug)
                    self.success_count += 1

                # Commit batch
                if (i + 1) % self.batch_size == 0:
                    await self.db.commit()

            except Exception as e:
                self.failed_count += 1
                self.errors.append("Record {}: {}".format(i, str(e)))

        # Final commit
        await self.db.commit()

        return DataImportResponse(
            data_type="drugs",
            total_records=total_records,
            success_count=self.success_count,
            failed_count=self.failed_count,
            errors=self.errors,
            import_time_seconds=time.time() - start_time,
        )

    async def import_procedures(
        self,
        data: List[Dict[str, Any]],
        overwrite: bool = False,
    ) -> DataImportResponse:
        """
        Import procedure codes from data list.

        Args:
            data: List of procedure code dictionaries
            overwrite: Whether to overwrite existing procedures

        Returns:
            Import response with statistics
        """
        start_time = time.time()
        total_records = len(data)

        for i, record in enumerate(data):
            try:
                # Check if procedure already exists
                existing = await self.db.execute(
                    select(ProcedureCode).where(ProcedureCode.code == record.get("code"))
                )
                existing_procedure = existing.scalar_one_or_none()

                if existing_procedure:
                    if overwrite:
                        # Update existing record
                        for key, value in record.items():
                            if hasattr(existing_procedure, key):
                                setattr(existing_procedure, key, value)
                        self.success_count += 1
                    else:
                        # Skip existing record
                        continue
                else:
                    # Create new record
                    db_procedure = ProcedureCode(**record)
                    self.db.add(db_procedure)
                    self.success_count += 1

                # Commit batch
                if (i + 1) % self.batch_size == 0:
                    await self.db.commit()

            except Exception as e:
                self.failed_count += 1
                self.errors.append("Record {}: {}".format(i, str(e)))

        # Final commit
        await self.db.commit()

        return DataImportResponse(
            data_type="procedures",
            total_records=total_records,
            success_count=self.success_count,
            failed_count=self.failed_count,
            errors=self.errors,
            import_time_seconds=time.time() - start_time,
        )

    async def import_from_json(
        self,
        file_path: str,
        data_type: str,
        overwrite: bool = False,
    ) -> DataImportResponse:
        """
        Import master data from JSON file.

        Args:
            file_path: Path to JSON file
            data_type: Type of data (icd10, loinc, drugs, procedures)
            overwrite: Whether to overwrite existing data

        Returns:
            Import response with statistics
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise MasterDataImportError("JSON file must contain a list of records")

        if data_type == "icd10":
            return await self.import_icd10_codes(data, overwrite)
        elif data_type == "loinc":
            return await self.import_loinc_codes(data, overwrite)
        elif data_type == "drugs":
            return await self.import_drugs(data, overwrite)
        elif data_type == "procedures":
            return await self.import_procedures(data, overwrite)
        else:
            raise MasterDataImportError("Unknown data type: {}".format(data_type))


async def import_master_data(
    db: AsyncSession,
    data_type: str,
    data: Optional[List[Dict[str, Any]]] = None,
    source_file: Optional[str] = None,
    overwrite: bool = False,
    batch_size: int = 100,
) -> DataImportResponse:
    """
    Import master data from various sources.

    Args:
        db: Database session
        data_type: Type of data to import (icd10, loinc, drugs, procedures)
        data: Inline data to import
        source_file: Path to source file (CSV or JSON)
        overwrite: Whether to overwrite existing data
        batch_size: Batch size for processing

    Returns:
        Import response with statistics

    Raises:
        MasterDataImportError: If import fails
    """
    importer = MasterDataImporter(db, batch_size)

    if source_file:
        if source_file.endswith(".csv"):
            if data_type == "icd10":
                return await importer.import_icd10_from_csv(source_file, overwrite)
            elif data_type == "loinc":
                return await importer.import_loinc_from_csv(source_file, overwrite)
            else:
                raise MasterDataImportError("CSV import not supported for data type: {}".format(data_type))
        elif source_file.endswith(".json"):
            return await importer.import_from_json(source_file, data_type, overwrite)
        else:
            raise MasterDataImportError("Unsupported file format. Use CSV or JSON.")

    elif data:
        if data_type == "icd10":
            return await importer.import_icd10_codes(data, overwrite)
        elif data_type == "loinc":
            return await importer.import_loinc_codes(data, overwrite)
        elif data_type == "drugs":
            return await importer.import_drugs(data, overwrite)
        elif data_type == "procedures":
            return await importer.import_procedures(data, overwrite)
        else:
            raise MasterDataImportError("Unknown data type: {}".format(data_type))

    else:
        raise MasterDataImportError("Either data or source_file must be provided")
