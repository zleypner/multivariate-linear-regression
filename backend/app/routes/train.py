"""
Model training endpoints.
"""

from fastapi import APIRouter, HTTPException, status
import structlog

from ..services.file_service import file_service
from ..services.ml_service import ml_service
from ..models.schemas import TrainingConfig, TrainingResult, ErrorResponse
from ..middleware.error_handler import NotFoundError, ModelError

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api", tags=["training"])


@router.post(
    "/train",
    response_model=TrainingResult,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "File not found"},
        422: {"model": ErrorResponse, "description": "Training failed"},
    },
    summary="Train regression model",
    description="Train a multivariate regression model on uploaded campaign data.",
)
async def train_model(config: TrainingConfig) -> TrainingResult:
    """
    Train a multivariate linear regression model.

    Requires a previously uploaded CSV file (identified by file_id).

    Supports different model types:
    - **ols**: Ordinary Least Squares (default)
    - **ridge**: Ridge regression with L2 regularization
    - **lasso**: Lasso regression with L1 regularization

    Returns comprehensive training metrics including:
    - R-squared (train and test)
    - RMSE, MAE
    - Cross-validation scores
    - Feature coefficients and importance
    """
    logger.info(
        "Training request received",
        file_id=config.file_id,
        target=config.target_column,
        model_type=config.model_type,
    )

    # Get the uploaded dataframe
    try:
        df = file_service.get_dataframe(config.file_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "file_not_found",
                "message": f"No uploaded file found with ID '{config.file_id}'",
                "file_id": config.file_id,
            },
        )

    # Validate target column exists
    if config.target_column not in df.columns:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "invalid_target",
                "message": f"Target column '{config.target_column}' not found in data",
                "available_columns": list(df.columns),
            },
        )

    # Train the model
    try:
        result = ml_service.train_model(df, config)
        logger.info(
            "Model training completed",
            training_id=result.training_id,
            r2=result.train_r2,
        )
        return result
    except ModelError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "training_failed",
                "message": str(e.message),
                "details": e.details,
            },
        )


@router.get(
    "/train/runs",
    summary="List training runs",
    description="Get a list of all training runs with summary metrics.",
)
async def list_training_runs() -> dict:
    """List all training runs."""
    runs = ml_service.list_training_runs()
    return {
        "runs": runs,
        "count": len(runs),
    }


@router.get(
    "/train/{training_id}",
    response_model=TrainingResult,
    responses={
        404: {"model": ErrorResponse, "description": "Training run not found"},
    },
    summary="Get training result",
    description="Get detailed results for a specific training run.",
)
async def get_training_result(training_id: str) -> TrainingResult:
    """Get training result by ID."""
    try:
        return ml_service.get_result_by_id(training_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "not_found",
                "message": f"Training run '{training_id}' not found",
            },
        )
