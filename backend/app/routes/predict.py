"""
Prediction endpoints.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status
import structlog

from ..services.ml_service import ml_service
from ..models.schemas import (
    PredictionRequest,
    PredictionResponse,
    SinglePrediction,
    ErrorResponse,
)
from ..middleware.error_handler import ModelError

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api", tags=["prediction"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        422: {"model": ErrorResponse, "description": "Prediction failed"},
    },
    summary="Make predictions",
    description="Make predictions for new campaign data using the trained model.",
)
async def predict(request: PredictionRequest) -> PredictionResponse:
    """
    Make predictions for new campaign data.

    Requires a trained model (call /api/train first).

    Input should include the same features used during training:
    - **budget**: Campaign budget
    - **impressions**: Number of impressions
    - **clicks**: Number of clicks
    - **ctr**: Click-through rate
    - **cpc**: Cost per click
    - **audience_type**: Target audience type
    - **creative_type**: Type of creative asset
    - **channel**: Marketing channel

    Returns predictions with optional confidence intervals.
    """
    logger.info("Prediction request received", count=len(request.campaigns))

    # Check if model is trained
    if not ml_service.is_model_trained():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "no_trained_model",
                "message": "No trained model available. Please train a model first using /api/train",
            },
        )

    try:
        # Make predictions
        predictions = ml_service.predict(request.campaigns)

        # Build response
        prediction_results = [
            SinglePrediction(
                input_data=pred["input_data"],
                predicted_value=pred["predicted_value"],
                confidence_interval=pred.get("confidence_interval"),
            )
            for pred in predictions
        ]

        model_info = ml_service.get_model_info()

        logger.info(
            "Predictions generated",
            count=len(predictions),
        )

        return PredictionResponse(
            success=True,
            target_column=model_info.get("target_column", "unknown"),
            predictions=prediction_results,
            model_info=model_info,
            predicted_at=datetime.utcnow(),
        )

    except ModelError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "prediction_failed",
                "message": str(e.message),
                "details": e.details,
            },
        )


@router.post(
    "/predict/single",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Make single prediction",
    description="Make a prediction for a single campaign.",
)
async def predict_single(campaign: dict[str, Any]) -> dict:
    """
    Make a prediction for a single campaign.

    Convenience endpoint for making a single prediction without
    wrapping in an array.
    """
    if not ml_service.is_model_trained():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "no_trained_model",
                "message": "No trained model available. Please train a model first.",
            },
        )

    try:
        predictions = ml_service.predict([campaign])
        prediction = predictions[0]

        return {
            "success": True,
            "prediction": prediction["predicted_value"],
            "confidence_interval": prediction.get("confidence_interval"),
            "input": campaign,
            "target_column": ml_service.get_model_info().get("target_column"),
        }

    except ModelError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "prediction_failed",
                "message": str(e.message),
            },
        )
