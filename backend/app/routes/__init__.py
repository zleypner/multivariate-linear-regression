"""
API route modules.
"""

from .upload import router as upload_router
from .train import router as train_router
from .predict import router as predict_router
from .results import router as results_router

__all__ = [
    "upload_router",
    "train_router",
    "predict_router",
    "results_router",
]
