"""Supabase Storage service for persistent document storage."""

from supabase import create_client

from app.config import settings


class StorageService:
    """Handle document uploads, downloads, and deletion."""

    def __init__(self):
        """Initialize the Supabase Storage client."""
        self.client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )

        self.bucket = settings.supabase_storage_bucket

    def upload_file(
        self,
        file_data: bytes,
        storage_path: str,
        content_type: str = "application/pdf",
    ) -> str:
        """Upload file bytes to Supabase Storage.

        Args:
            file_data: File contents.
            storage_path: Destination path inside the bucket.
            content_type: MIME type of the file.

        Returns:
            Storage path of the uploaded file.
        """
        self.client.storage.from_(self.bucket).upload(
            path=storage_path,
            file=file_data,
            file_options={
                "content-type": content_type,
                "upsert": "false",
            },
        )

        return storage_path

    def download_file(
        self,
        storage_path: str,
        destination_path: str,
    ) -> str:
        """Download a file from Supabase Storage.

        Args:
            storage_path: Path inside the storage bucket.
            destination_path: Local destination path.

        Returns:
            Local path of the downloaded file.
        """
        data = self.client.storage.from_(self.bucket).download(
            storage_path
        )

        with open(destination_path, "wb") as file:
            file.write(data)

        return destination_path

    def delete_file(self, storage_path: str) -> None:
        """Delete a file from Supabase Storage.

        Args:
            storage_path: Path inside the storage bucket.
        """
        self.client.storage.from_(self.bucket).remove(
            [storage_path]
        )


storage_service = StorageService()