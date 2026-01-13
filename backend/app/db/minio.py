from minio import Minio
from typing import Optional
from app.core.config import settings

_minio_client: Optional[Minio] = None


def get_minio_client() -> Minio:
    """
    Get or create MinIO client instance.
    """
    global _minio_client

    if _minio_client is None:
        _minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )

        # Create bucket if it doesn't exist
        try:
            if not _minio_client.bucket_exists(settings.MINIO_BUCKET):
                _minio_client.make_bucket(settings.MINIO_BUCKET)
        except Exception as e:
            print(f"Warning: Could not create MinIO bucket: {e}")

    return _minio_client
