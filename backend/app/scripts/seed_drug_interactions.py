"""Drug Interaction Database Seeder Script for STORY-026

This script seeds the drug interaction database with common interactions.
Run with: python -m app.scripts.seed_drug_interactions
"""
import asyncio
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.medication import DrugInteraction
from app.models.inventory import Drug
from app.schemas.medication import InteractionType, InteractionSeverity
import json


# Common drug interactions for Indonesian hospitals
COMMON_INTERACTIONS = [
    # 1. ACE Inhibitors + Potassium Supplements
    {
        "drug_1_generic": "captopril",  # ACEI
        "drug_2_generic": "kalium klorida",  # Potassium chloride
        "interaction_type": InteractionType.DRUG_DRUG,
        "severity": InteractionSeverity.MODERATE,
        "description": "ACE inhibitor dapat meningkatkan kadar kalium serum. Penggunaan bersamaan dengan suplemen kalium dapat menyebabkan hiperkalemia.",
        "recommendation": "Monitor kadar kalium serum secara teratur. Pertimbangkan suplemen kalium hanya jika terdapat hipokalemia dan monitor sering.",
        "evidence_level": "B",
    },
    # 2. Warfarin + NSAIDs
    {
        "drug_1_generic": "warfarin",
        "drug_2_generic": "ibuprofen",  # NSAID
        "interaction_type": InteractionType.DRUG_DRUG,
        "severity": InteractionSeverity.SEVERE,
        "description": "NSAIDs dapat meningkatkan efek antikoagulan warfarin, meningkatkan risiko perdarahan.",
        "recommendation": "Hindari penggunaan bersama jika memungkinkan. Jika ko-administrasi diperlukan, monitor INR dan tanda perdarahan secara rapat.",
        "evidence_level": "A",
    },
    # 3. Digoxin + Verapamil
    {
        "drug_1_generic": "digoxin",
        "drug_2_generic": "verapamil",
        "interaction_type": InteractionType.DRUG_DRUG,
        "severity": InteractionSeverity.MODERATE,
        "description": "Verapamil dapat meningkatkan kadar digoxin serum dengan mengurangi clearance renal.",
        "recommendation": "Monitor kadar digoxin dan kurangi dosis digoxin sebesar 50% saat verapamil dimulai. Awasi toksisitas digoxin (mual, gangguan penglihatan).",
        "evidence_level": "A",
    },
    # 4. Beta-blockers + Calcium Channel Blockers
    {
        "drug_1_generic": "bisoprolol",  # Beta-blocker
        "drug_2_generic": "amlodipin",  # CCB
        "interaction_type": InteractionType.DRUG_DRUG,
        "severity": InteractionSeverity.MODERATE,
        "description": "Penggunaan bersamaan dapat menyebabkan bradikardia berlebih dan blok jantung.",
        "recommendation": "Monitor denyut jantung dan tekanan darah secara rapat. Pengurangan dosis mungkin diperlukan.",
        "evidence_level": "B",
    },
    # 5. SSRIs + MAOIs
    {
        "drug_1_generic": "fluoxetine",  # SSRI
        "drug_2_generic": "selegiline",  # MAOI
        "interaction_type": InteractionType.DRUG_DRUG,
        "severity": InteractionSeverity.CONTRAINDICATED,
        "description": "Penggunaan bersamaan dapat menyebabkan sindroma serotonin (hipertermia, rigidity, myoclonus, ketidakstabilan otonom).",
        "recommendation": "KONTRAINDIKASI. Berikan jeda minimal 2 minggu saat beralih dari MAOI ke SSRI.",
        "evidence_level": "A",
    },
    # 6. Quinolones + Antacids
    {
        "drug_1_generic": "ciprofloxacin",  # Quinolone
        "drug_2_generic": "antacid",  # Representing antacids
        "interaction_type": InteractionType.DRUG_FOOD,
        "severity": InteractionSeverity.MILD,
        "description": "Antasid yang mengandung magnesium atau aluminum dapat mengurangi absorpsi quinolon.",
        "recommendation": "Berikan quinolon minimal 2 jam sebelum atau 6 jam setelah antasid.",
        "evidence_level": "B",
    },
    # 7. Statins + Grapefruit
    {
        "drug_1_generic": "simvastatin",  # Statin
        "drug_2_generic": "jeruk",  # Grapefruit representation
        "interaction_type": InteractionType.DRUG_FOOD,
        "severity": InteractionSeverity.MODERATE,
        "description": "Jus jeruk menghambat CYP3A4, meningkatkan kadar statin dan risiko miopati.",
        "recommendation": "Nasihati pasien untuk menghindari jus jeruk saat minum statin, terutama simvastatin.",
        "evidence_level": "B",
    },
    # 8. ACE Inhibitors + Pregnancy
    {
        "drug_1_generic": "captopril",  # ACEI
        "disease_code": "O09",  # ICD-10 Pregnancy
        "disease_name": "Kehamilan",
        "interaction_type": InteractionType.DRUG_DISEASE,
        "severity": InteractionSeverity.CONTRAINDICATED,
        "description": "ACE inhibitor dapat menyebabkan gagal ginjal janin dan kematian selama kehamilan, terutama trimester kedua dan ketiga.",
        "recommendation": "Kontraindikasi selama kehamilan. Gunakan antihipertensi alternatif.",
        "evidence_level": "D",
    },
    # 9. NSAIDs + Peptic Ulcer
    {
        "drug_1_generic": "ibuprofen",  # NSAID
        "disease_code": "K25",  # ICD-10 Gastric ulcer
        "disease_name": "Tukak Lambung",
        "interaction_type": InteractionType.DRUG_DISEASE,
        "severity": InteractionSeverity.SEVERE,
        "description": "NSAIDs dapat meningkatkan risiko perdarahan gastrointestinal dan komplikasi ulkus.",
        "recommendation": "Gunakan dengan hati-hati pada pasien dengan riwayat PUD. Pertimbangkan ko-resep dengan PPI atau misoprostol. Hindari pada ulkus aktif.",
        "evidence_level": "A",
    },
    # 10. Beta-blockers + Asthma
    {
        "drug_1_generic": "propranolol",  # Non-selective beta-blocker
        "disease_code": "J45",  # ICD-10 Asthma
        "disease_name": "Asma",
        "interaction_type": InteractionType.DRUG_DISEASE,
        "severity": InteractionSeverity.MODERATE,
        "description": "Beta-blocker non-selektif dapat menginduksi bronkokonstriksi pada pasien asma.",
        "recommendation": "Gunakan beta-blocker kardioselektif (misal metoprolol, atenolol) dengan hati-hati. Hindari beta-blocker non-selektif pada asma berat.",
        "evidence_level": "B",
    },
]


async def find_drug_by_generic(db: AsyncSession, generic_name: str) -> Optional[int]:
    """Find drug ID by generic name"""
    from sqlalchemy import select

    stmt = select(Drug).where(Drug.generic_name.ilike(f"%{generic_name}%"))
    result = await db.execute(stmt)
    drug = result.scalar_one_or_none()
    return drug.id if drug else None


async def seed_interactions(db: AsyncSession) -> dict:
    """Seed drug interactions"""
    results = {
        "created": 0,
        "skipped": 0,
        "not_found": [],
        "errors": []
    }

    for interaction_data in COMMON_INTERACTIONS:
        try:
            # Find drug IDs
            if "drug_2_generic" in interaction_data:
                drug_1_id = await find_drug_by_generic(db, interaction_data["drug_1_generic"])
                drug_2_id = await find_drug_by_generic(db, interaction_data["drug_2_generic"])
            else:
                drug_1_id = await find_drug_by_generic(db, interaction_data["drug_1_generic"])
                drug_2_id = None

            # Skip if drugs not found
            if not drug_1_id or (interaction_data.get("drug_2_generic") and not drug_2_id):
                results["not_found"].append(interaction_data["drug_1_generic"])
                continue

            # Check for duplicate
            from app.crud.drug_interactions import check_interaction_exists

            exists = await check_interaction_exists(
                db=db,
                drug_1_id=drug_1_id,
                drug_2_id=drug_2_id,
                interaction_type=interaction_data["interaction_type"],
            )

            if exists:
                results["skipped"] += 1
                continue

            # Create interaction
            from app.crud.drug_interactions import create_drug_interaction

            await create_drug_interaction(
                db=db,
                interaction_type=interaction_data["interaction_type"],
                severity=interaction_data["severity"],
                drug_1_id=drug_1_id,
                drug_2_id=drug_2_id,
                description=interaction_data["description"],
                recommendation=interaction_data["recommendation"],
                disease_code=interaction_data.get("disease_code"),
                disease_name=interaction_data.get("disease_name"),
                requires_override=True,
                evidence_level=interaction_data["evidence_level"],
            )
            results["created"] += 1

        except Exception as e:
            results["errors"].append(f"{interaction_data['drug_1_generic']}: {str(e)}")

    return results


async def main():
    """Main seeding function"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as session:
        print("🌱 Seeding drug interaction database...")
        print("=" * 50)

        results = await seed_interactions(session)

        print(f"\n✅ Seeding completed!")
        print(f"   Created: {results['created']} interactions")
        print(f"   Skipped: {results['skipped']} (already exists)")
        print(f"   Not Found: {len(results['not_found'])} drugs")

        if results["not_found"]:
            print(f"\n⚠️  Drugs not found in database:")
            for drug in results["not_found"]:
                print(f"   - {drug}")

        if results["errors"]:
            print(f"\n❌ Errors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"   - {error}")

        print("\n" + "=" * 50)
        print("Seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
