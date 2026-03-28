"""
Results and metrics endpoints.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, status
import structlog

from ..services.ml_service import ml_service
from ..models.schemas import TrainingResult, ErrorResponse
from ..middleware.error_handler import NotFoundError

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api", tags=["results"])


@router.get(
    "/results",
    response_model=TrainingResult,
    responses={
        404: {"model": ErrorResponse, "description": "No results available"},
    },
    summary="Get latest training results",
    description="Get the results and metrics from the most recent model training.",
)
async def get_latest_results() -> TrainingResult:
    """
    Get the latest training results.

    Returns comprehensive metrics including:
    - R-squared scores (train and test)
    - RMSE and MAE
    - Cross-validation results
    - Feature coefficients and importance rankings
    """
    try:
        result = ml_service.get_latest_result()
        return result
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "no_results",
                "message": "No training results available. Please train a model first.",
            },
        )


@router.get(
    "/results/summary",
    summary="Get results summary",
    description="Get a summary of the latest training results.",
)
async def get_results_summary() -> dict[str, Any]:
    """
    Get a summary of the latest training results.

    Returns key metrics in a simplified format.
    """
    try:
        result = ml_service.get_latest_result()

        # Get top features by importance
        sorted_importance = sorted(
            result.feature_importance.items(),
            key=lambda x: abs(x[1]),
            reverse=True,
        )
        top_features = sorted_importance[:5]

        return {
            "training_id": result.training_id,
            "model_type": result.model_type,
            "target_column": result.target_column,
            "metrics": {
                "r_squared": result.train_r2,
                "cv_r2_mean": result.cv_r2_mean,
                "rmse": result.train_rmse,
                "mae": result.train_mae,
            },
            "top_features": [
                {"feature": name, "coefficient": coef}
                for name, coef in top_features
            ],
            "trained_at": result.trained_at.isoformat(),
        }

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "no_results",
                "message": "No training results available.",
            },
        )


@router.get(
    "/results/coefficients",
    summary="Get model coefficients",
    description="Get the coefficients for all features in the trained model.",
)
async def get_coefficients() -> dict[str, Any]:
    """
    Get model coefficients.

    Returns the intercept and all feature coefficients.
    """
    try:
        result = ml_service.get_latest_result()
        return {
            "intercept": result.intercept,
            "coefficients": result.coefficients,
            "feature_names": result.feature_names,
        }
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "no_results",
                "message": "No training results available.",
            },
        )


@router.get(
    "/results/feature-importance",
    summary="Get feature importance",
    description="Get ranked feature importance from the trained model.",
)
async def get_feature_importance() -> dict[str, Any]:
    """
    Get feature importance rankings.

    Returns features sorted by absolute importance (coefficient magnitude).
    """
    try:
        result = ml_service.get_latest_result()

        # Sort by absolute value
        sorted_importance = sorted(
            result.feature_importance.items(),
            key=lambda x: abs(x[1]),
            reverse=True,
        )

        importance_list = [
            {
                "rank": idx + 1,
                "feature": name,
                "coefficient": coef,
                "abs_importance": abs(coef),
                "direction": "positive" if coef > 0 else "negative",
            }
            for idx, (name, coef) in enumerate(sorted_importance)
        ]

        return {
            "feature_importance": importance_list,
            "n_features": len(importance_list),
            "target_column": result.target_column,
        }

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "no_results",
                "message": "No training results available.",
            },
        )


@router.get(
    "/results/vif",
    summary="Get VIF report",
    description="Get Variance Inflation Factor report for multicollinearity analysis.",
)
async def get_vif_report() -> dict[str, Any]:
    """
    Get VIF (Variance Inflation Factor) report.

    VIF helps detect multicollinearity among features:
    - VIF = 1: No correlation
    - VIF < 5: Moderate correlation (acceptable)
    - VIF > 10: High correlation (problematic)
    """
    try:
        return ml_service.get_vif_report()
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "no_results",
                "message": "No trained model available.",
            },
        )


@router.get(
    "/model/info",
    summary="Get model information",
    description="Get information about the currently trained model.",
)
async def get_model_info() -> dict[str, Any]:
    """Get current model information."""
    info = ml_service.get_model_info()
    return info
