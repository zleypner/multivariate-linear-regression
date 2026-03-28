"""
Utility functions for the campaign analytics ML module.

This module provides model serialization, results formatting,
and validation functions.
"""

from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json
from datetime import datetime
import numpy as np
import pandas as pd
import joblib


def save_model(
    model: Any,
    filepath: Union[str, Path],
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Save a model to disk using joblib.

    Args:
        model: The model object to save.
        filepath: Path where the model will be saved.
        metadata: Optional metadata to save alongside the model.

    Returns:
        The path where the model was saved.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Create a model bundle with metadata
    bundle = {
        'model': model,
        'metadata': metadata or {},
        'saved_at': datetime.now().isoformat(),
        'version': '1.0.0'
    }

    joblib.dump(bundle, filepath)
    return str(filepath)


def load_model(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Load a model from disk.

    Args:
        filepath: Path to the saved model file.

    Returns:
        Dictionary containing the model and metadata.

    Raises:
        FileNotFoundError: If the model file does not exist.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Model file not found: {filepath}")

    bundle = joblib.load(filepath)
    return bundle


def get_model(filepath: Union[str, Path]) -> Any:
    """
    Load and return just the model object.

    Args:
        filepath: Path to the saved model file.

    Returns:
        The model object.
    """
    bundle = load_model(filepath)
    return bundle['model']


def format_metrics(metrics: Dict[str, float], precision: int = 4) -> Dict[str, str]:
    """
    Format metric values for display.

    Args:
        metrics: Dictionary of metric names to values.
        precision: Number of decimal places.

    Returns:
        Dictionary of formatted metric strings.
    """
    formatted = {}
    for name, value in metrics.items():
        if isinstance(value, (int, float)):
            if abs(value) >= 1000:
                formatted[name] = f"{value:,.{precision}f}"
            else:
                formatted[name] = f"{value:.{precision}f}"
        else:
            formatted[name] = str(value)
    return formatted


def format_feature_importance(
    feature_names: List[str],
    importance_values: np.ndarray,
    top_n: Optional[int] = None,
    sort_descending: bool = True
) -> List[Dict[str, Any]]:
    """
    Format feature importance results.

    Args:
        feature_names: List of feature names.
        importance_values: Array of importance values.
        top_n: Number of top features to return (None for all).
        sort_descending: Whether to sort by importance descending.

    Returns:
        List of dictionaries with feature name, importance, and rank.
    """
    # Create DataFrame for easy sorting
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importance_values,
        'abs_importance': np.abs(importance_values)
    })

    # Sort by absolute importance
    importance_df = importance_df.sort_values(
        'abs_importance',
        ascending=not sort_descending
    )

    # Add rank
    importance_df['rank'] = range(1, len(importance_df) + 1)

    # Limit to top_n if specified
    if top_n is not None:
        importance_df = importance_df.head(top_n)

    # Convert to list of dicts
    results = []
    for _, row in importance_df.iterrows():
        results.append({
            'feature': row['feature'],
            'importance': float(row['importance']),
            'abs_importance': float(row['abs_importance']),
            'rank': int(row['rank'])
        })

    return results


def format_prediction_results(
    predictions: np.ndarray,
    confidence_intervals: Optional[np.ndarray] = None,
    feature_contributions: Optional[Dict[str, np.ndarray]] = None
) -> List[Dict[str, Any]]:
    """
    Format prediction results for API response.

    Args:
        predictions: Array of predicted values.
        confidence_intervals: Optional array of [lower, upper] bounds.
        feature_contributions: Optional dict mapping features to contribution arrays.

    Returns:
        List of prediction result dictionaries.
    """
    results = []

    for i, pred in enumerate(predictions):
        result = {
            'prediction': float(pred),
            'index': i
        }

        if confidence_intervals is not None:
            result['confidence_interval'] = {
                'lower': float(confidence_intervals[i, 0]),
                'upper': float(confidence_intervals[i, 1])
            }

        if feature_contributions is not None:
            result['feature_contributions'] = {
                feature: float(values[i])
                for feature, values in feature_contributions.items()
            }

        results.append(result)

    return results


def validate_dataframe(
    df: pd.DataFrame,
    required_columns: List[str],
    numeric_columns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Validate a DataFrame for model input.

    Args:
        df: DataFrame to validate.
        required_columns: List of required column names.
        numeric_columns: List of columns that must be numeric.

    Returns:
        Dictionary with validation results.
    """
    errors = []
    warnings = []

    # Check required columns
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        errors.append(f"Missing required columns: {list(missing_columns)}")

    # Check for empty DataFrame
    if len(df) == 0:
        errors.append("DataFrame is empty")

    # Check numeric columns
    if numeric_columns:
        for col in numeric_columns:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    errors.append(f"Column '{col}' must be numeric")

    # Check for missing values
    missing_counts = df[required_columns].isnull().sum() if not missing_columns else pd.Series()
    columns_with_missing = missing_counts[missing_counts > 0]
    if len(columns_with_missing) > 0:
        warnings.append(
            f"Columns with missing values: {columns_with_missing.to_dict()}"
        )

    # Check for infinite values in numeric columns
    if numeric_columns:
        for col in numeric_columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                inf_count = np.isinf(df[col]).sum()
                if inf_count > 0:
                    warnings.append(f"Column '{col}' contains {inf_count} infinite values")

    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'row_count': len(df),
        'column_count': len(df.columns)
    }


def validate_model_input(
    X: Union[pd.DataFrame, np.ndarray],
    expected_features: int
) -> Dict[str, Any]:
    """
    Validate input data for model prediction.

    Args:
        X: Input features.
        expected_features: Expected number of features.

    Returns:
        Dictionary with validation results.
    """
    errors = []

    if isinstance(X, pd.DataFrame):
        actual_features = X.shape[1]
    elif isinstance(X, np.ndarray):
        actual_features = X.shape[1] if X.ndim > 1 else X.shape[0]
    else:
        errors.append(f"Invalid input type: {type(X)}")
        return {'is_valid': False, 'errors': errors}

    if actual_features != expected_features:
        errors.append(
            f"Expected {expected_features} features, got {actual_features}"
        )

    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'actual_features': actual_features,
        'expected_features': expected_features
    }


def create_model_summary(
    model_name: str,
    metrics: Dict[str, float],
    feature_importance: List[Dict[str, Any]],
    training_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a comprehensive model summary.

    Args:
        model_name: Name of the model.
        metrics: Dictionary of evaluation metrics.
        feature_importance: List of feature importance dictionaries.
        training_info: Optional training information.

    Returns:
        Dictionary containing the model summary.
    """
    return {
        'model_name': model_name,
        'created_at': datetime.now().isoformat(),
        'metrics': metrics,
        'feature_importance': feature_importance,
        'training_info': training_info or {},
        'top_features': [f['feature'] for f in feature_importance[:5]],
        'summary_stats': {
            'r_squared': metrics.get('r_squared', metrics.get('r2', None)),
            'rmse': metrics.get('rmse', None),
            'total_features': len(feature_importance)
        }
    }


def results_to_json(results: Dict[str, Any], filepath: Optional[Union[str, Path]] = None) -> str:
    """
    Convert results to JSON string and optionally save to file.

    Args:
        results: Dictionary of results.
        filepath: Optional path to save JSON file.

    Returns:
        JSON string representation.
    """
    # Custom encoder for numpy types
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            return super().default(obj)

    json_str = json.dumps(results, indent=2, cls=NumpyEncoder)

    if filepath:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(json_str)

    return json_str


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values.

    Args:
        old_value: Original value.
        new_value: New value.

    Returns:
        Percentage change.
    """
    if old_value == 0:
        return float('inf') if new_value != 0 else 0.0
    return ((new_value - old_value) / abs(old_value)) * 100
