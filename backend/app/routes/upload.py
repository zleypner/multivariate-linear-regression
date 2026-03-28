"""
CSV file upload endpoints.
"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, File, UploadFile, HTTPException, status
import structlog

from ..config import settings
from ..services.file_service import file_service
from ..models.schemas import UploadResponse, ErrorResponse

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file"},
        413: {"model": ErrorResponse, "description": "File too large"},
    },
    summary="Upload CSV file",
    description="Upload a CSV file containing campaign data for analysis.",
)
async def upload_csv(
    file: Annotated[UploadFile, File(description="CSV file to upload")],
) -> UploadResponse:
    """
    Upload a CSV file for campaign analytics.

    The file must be a valid CSV with campaign data including:
    - Budget, impressions, clicks, CTR, CPC
    - Audience type, creative type, channel
    - Target metrics (conversions, revenue, etc.)

    Returns a preview of the data and a file_id for subsequent operations.
    """
    # Validate content type
    if file.content_type not in ["text/csv", "application/csv", "application/vnd.ms-excel"]:
        # Allow any content type but warn about extension
        if not file.filename or not file.filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "invalid_file_type",
                    "message": "Only CSV files are allowed",
                    "content_type": file.content_type,
                },
            )

    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        logger.error("Failed to read uploaded file", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "file_read_error",
                "message": f"Failed to read file: {str(e)}",
            },
        )

    # Validate file size
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "file_too_large",
                "message": f"File size exceeds maximum of {settings.max_upload_size_mb}MB",
                "max_size_mb": settings.max_upload_size_mb,
            },
        )

    # Check for empty file
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "empty_file",
                "message": "Uploaded file is empty",
            },
        )

    # Save file
    file_id, file_path = await file_service.save_upload(
        content=content,
        filename=file.filename or "upload.csv",
    )

    # Validate and parse CSV
    df = file_service.validate_csv(file_path)

    # Create preview
    preview = file_service.create_preview(df)

    # Store dataframe for later use
    file_service.store_dataframe(file_id, df, file.filename or "upload.csv")

    logger.info(
        "File uploaded successfully",
        file_id=file_id,
        filename=file.filename,
        rows=len(df),
        columns=len(df.columns),
    )

    return UploadResponse(
        success=True,
        filename=file.filename or "upload.csv",
        file_id=file_id,
        preview=preview,
        message=f"Successfully uploaded {len(df)} rows with {len(df.columns)} columns",
        uploaded_at=datetime.utcnow(),
    )


@router.get(
    "/files",
    summary="List uploaded files",
    description="Get a list of all uploaded files.",
)
async def list_files() -> dict:
    """List all uploaded files with their metadata."""
    files = file_service.list_uploaded_files()
    return {
        "files": files,
        "count": len(files),
    }


@router.delete(
    "/files/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete uploaded file",
    description="Delete an uploaded file by its ID.",
)
async def delete_file(file_id: str) -> None:
    """Delete an uploaded file."""
    deleted = await file_service.delete_file(file_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "not_found",
                "message": f"File with ID '{file_id}' not found",
            },
        )
    logger.info("File deleted", file_id=file_id)
