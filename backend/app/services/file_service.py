"""
File handling service for CSV uploads.
"""

import uuid
import aiofiles
from pathlib import Path
from typing import Any

import pandas as pd
import structlog

from ..config import settings
from ..middleware.error_handler import FileUploadError, NotFoundError
from ..models.schemas import ColumnInfo, DataPreview

logger = structlog.get_logger(__name__)


class FileService:
    """Service for handling file uploads and storage."""

    # In-memory storage for uploaded files metadata
    # In production, use Redis or database
    _uploaded_files: dict[str, dict[str, Any]] = {}
    _dataframes: dict[str, pd.DataFrame] = {}

    def __init__(self) -> None:
        """Initialize file service."""
        self.upload_dir = settings.upload_path
        self.max_size = settings.max_upload_size_bytes
        self.allowed_extensions = settings.allowed_extensions

    async def save_upload(
        self,
        content: bytes,
        filename: str,
    ) -> tuple[str, Path]:
        """
        Save uploaded file content.

        Args:
            content: File content as bytes
            filename: Original filename

        Returns:
            Tuple of (file_id, file_path)

        Raises:
            FileUploadError: If file validation fails
        """
        # Validate file size
        if len(content) > self.max_size:
            raise FileUploadError(
                f"File size exceeds maximum allowed size of {settings.max_upload_size_mb}MB",
                details={"max_size_mb": settings.max_upload_size_mb},
            )

        # Validate file extension
        extension = Path(filename).suffix.lower()
        if extension not in self.allowed_extensions:
            raise FileUploadError(
                f"File type '{extension}' not allowed. Allowed types: {self.allowed_extensions}",
                details={"allowed_extensions": self.allowed_extensions},
            )

        # Generate unique file ID
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}{extension}"
        file_path = self.upload_dir / safe_filename

        # Save file
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        logger.info(
            "File saved",
            file_id=file_id,
            filename=filename,
            size=len(content),
        )

        return file_id, file_path

    def validate_csv(self, file_path: Path) -> pd.DataFrame:
        """
        Validate and parse CSV file.

        Args:
            file_path: Path to CSV file

        Returns:
            Parsed DataFrame

        Raises:
            FileUploadError: If CSV validation fails
        """
        try:
            df = pd.read_csv(file_path)

            if df.empty:
                raise FileUploadError("CSV file is empty")

            if len(df.columns) < 2:
                raise FileUploadError(
                    "CSV file must have at least 2 columns",
                    details={"columns_found": len(df.columns)},
                )

            logger.info(
                "CSV validated",
                rows=len(df),
                columns=len(df.columns),
            )

            return df

        except pd.errors.EmptyDataError:
            raise FileUploadError("CSV file is empty or has no valid data")
        except pd.errors.ParserError as e:
            raise FileUploadError(
                f"Failed to parse CSV file: {str(e)}",
                details={"parser_error": str(e)},
            )
        except Exception as e:
            if isinstance(e, FileUploadError):
                raise
            raise FileUploadError(
                f"Error reading CSV file: {str(e)}",
                details={"error": str(e)},
            )

    def create_preview(
        self,
        df: pd.DataFrame,
        preview_rows: int = 5,
    ) -> DataPreview:
        """
        Create a preview of the DataFrame.

        Args:
            df: DataFrame to preview
            preview_rows: Number of rows to include in preview

        Returns:
            DataPreview object
        """
        # Get sample rows
        sample_df = df.head(preview_rows)
        rows = sample_df.to_dict(orient="records")

        # Get column info
        columns = []
        for col in df.columns:
            col_info = ColumnInfo(
                name=col,
                dtype=str(df[col].dtype),
                non_null_count=int(df[col].notna().sum()),
                unique_count=int(df[col].nunique()),
                sample_values=df[col].dropna().head(3).tolist(),
            )
            columns.append(col_info)

        return DataPreview(
            rows=rows,
            columns=columns,
            total_rows=len(df),
            total_columns=len(df.columns),
        )

    def store_dataframe(self, file_id: str, df: pd.DataFrame, filename: str) -> None:
        """
        Store DataFrame in memory for later use.

        Args:
            file_id: Unique file identifier
            df: DataFrame to store
            filename: Original filename
        """
        self._dataframes[file_id] = df
        self._uploaded_files[file_id] = {
            "filename": filename,
            "rows": len(df),
            "columns": list(df.columns),
        }
        logger.info("DataFrame stored", file_id=file_id)

    def get_dataframe(self, file_id: str) -> pd.DataFrame:
        """
        Retrieve stored DataFrame.

        Args:
            file_id: Unique file identifier

        Returns:
            Stored DataFrame

        Raises:
            NotFoundError: If file_id not found
        """
        if file_id not in self._dataframes:
            raise NotFoundError(
                f"File with ID '{file_id}' not found",
                details={"file_id": file_id},
            )
        return self._dataframes[file_id]

    def get_file_info(self, file_id: str) -> dict[str, Any]:
        """
        Get metadata about an uploaded file.

        Args:
            file_id: Unique file identifier

        Returns:
            File metadata

        Raises:
            NotFoundError: If file_id not found
        """
        if file_id not in self._uploaded_files:
            raise NotFoundError(
                f"File with ID '{file_id}' not found",
                details={"file_id": file_id},
            )
        return self._uploaded_files[file_id]

    def list_uploaded_files(self) -> list[dict[str, Any]]:
        """List all uploaded files."""
        return [
            {"file_id": fid, **info}
            for fid, info in self._uploaded_files.items()
        ]

    async def delete_file(self, file_id: str) -> bool:
        """
        Delete an uploaded file.

        Args:
            file_id: Unique file identifier

        Returns:
            True if deleted successfully
        """
        if file_id in self._dataframes:
            del self._dataframes[file_id]
        if file_id in self._uploaded_files:
            del self._uploaded_files[file_id]

        # Delete physical file if exists
        for ext in self.allowed_extensions:
            file_path = self.upload_dir / f"{file_id}{ext}"
            if file_path.exists():
                file_path.unlink()
                logger.info("File deleted", file_id=file_id)
                return True

        return False


# Singleton instance
file_service = FileService()
