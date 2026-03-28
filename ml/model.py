"""
Multiple Linear Regression model for campaign analytics.

This module provides a comprehensive regression model for predicting
campaign performance metrics with multicollinearity detection,
feature importance analysis, and robust evaluation metrics.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score
)
from sklearn.model_selection import cross_val_score, KFold
from statsmodels.stats.outliers_influence import variance_inflation_factor

from .preprocessing import CampaignDataPreprocessor
from .utils import (
    save_model,
    load_model,
    format_feature_importance,
    format_metrics,
    validate_dataframe,
    create_model_summary
)


class CampaignRegressionModel:
    """
    Multiple Linear Regression model for campaign performance prediction.

    This model predicts campaign outcomes (e.g., conversions) based on
    campaign features including budget, impressions, CTR, CPC, and
    categorical variables like audience type, creative type, and channel.

    Attributes:
        target_variable: Name of the target variable to predict.
        numeric_features: List of numeric feature column names.
        categorical_features: List of categorical feature column names.
        model: The fitted sklearn LinearRegression model.
        preprocessor: The fitted CampaignDataPreprocessor.
        metrics: Dictionary of evaluation metrics.
        feature_importance: List of feature importance dictionaries.
        vif_results: Variance Inflation Factor results for multicollinearity.
    """

    DEFAULT_NUMERIC_FEATURES = ['budget', 'impressions', 'clicks', 'ctr', 'cpc']
    DEFAULT_CATEGORICAL_FEATURES = ['audience_type', 'creative_type', 'channel']
    DEFAULT_TARGET = 'conversions'

    def __init__(
        self,
        target_variable: str = DEFAULT_TARGET,
        numeric_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None
    ):
        """
        Initialize the regression model.

        Args:
            target_variable: Name of the target variable to predict.
            numeric_features: List of numeric features. Defaults to standard campaign metrics.
            categorical_features: List of categorical features. Defaults to standard categories.
        """
        self.target_variable = target_variable
        self.numeric_features = numeric_features or self.DEFAULT_NUMERIC_FEATURES.copy()
        self.categorical_features = categorical_features or self.DEFAULT_CATEGORICAL_FEATURES.copy()

        self.model: Optional[LinearRegression] = None
        self.preprocessor: Optional[CampaignDataPreprocessor] = None
        self.metrics: Dict[str, float] = {}
        self.feature_importance: List[Dict[str, Any]] = []
        self.vif_results: List[Dict[str, Any]] = []
        self._is_fitted: bool = False
        self._n_features: int = 0
        self._n_samples_train: int = 0

    def _get_all_features(self) -> List[str]:
        """Get combined list of all features."""
        return self.numeric_features + self.categorical_features

    def fit(
        self,
        df: pd.DataFrame,
        compute_vif: bool = True,
        cv_folds: int = 5
    ) -> 'CampaignRegressionModel':
        """
        Fit the regression model on training data.

        Args:
            df: DataFrame containing features and target variable.
            compute_vif: Whether to compute Variance Inflation Factors.
            cv_folds: Number of cross-validation folds for evaluation.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If required columns are missing from the DataFrame.
        """
        # Validate input data
        required_cols = self._get_all_features() + [self.target_variable]
        validation = validate_dataframe(
            df,
            required_columns=required_cols,
            numeric_columns=self.numeric_features + [self.target_variable]
        )

        if not validation['is_valid']:
            raise ValueError(f"Invalid input data: {validation['errors']}")

        # Extract features and target
        X = df[self._get_all_features()].copy()
        y = df[self.target_variable].copy()

        # Initialize and fit preprocessor
        self.preprocessor = CampaignDataPreprocessor(
            numeric_features=self.numeric_features,
            categorical_features=self.categorical_features
        )

        # Transform features
        X_transformed = self.preprocessor.fit_transform(X)
        self._n_features = X_transformed.shape[1]
        self._n_samples_train = len(y)

        # Compute VIF for multicollinearity detection
        if compute_vif:
            self._compute_vif(X_transformed)

        # Fit the model
        self.model = LinearRegression()
        self.model.fit(X_transformed, y)

        # Compute metrics with cross-validation
        self._compute_metrics(X_transformed, y, cv_folds)

        # Compute feature importance
        self._compute_feature_importance()

        self._is_fitted = True
        return self

    def _compute_vif(self, X: np.ndarray) -> None:
        """
        Compute Variance Inflation Factors for multicollinearity detection.

        Args:
            X: Transformed feature matrix.
        """
        feature_names = self.preprocessor.get_feature_names()
        self.vif_results = []

        # Add constant for VIF calculation
        X_with_const = np.column_stack([np.ones(X.shape[0]), X])

        for i in range(1, X_with_const.shape[1]):
            try:
                vif = variance_inflation_factor(X_with_const, i)
                feature_name = feature_names[i - 1] if i - 1 < len(feature_names) else f"feature_{i}"
                self.vif_results.append({
                    'feature': feature_name,
                    'vif': float(vif) if not np.isinf(vif) else float('inf'),
                    'has_multicollinearity': vif > 10 if not np.isinf(vif) else True
                })
            except Exception:
                # Handle numerical issues
                feature_name = feature_names[i - 1] if i - 1 < len(feature_names) else f"feature_{i}"
                self.vif_results.append({
                    'feature': feature_name,
                    'vif': None,
                    'has_multicollinearity': None
                })

    def _compute_metrics(
        self,
        X: np.ndarray,
        y: pd.Series,
        cv_folds: int
    ) -> None:
        """
        Compute evaluation metrics including cross-validation scores.

        Args:
            X: Transformed feature matrix.
            y: Target values.
            cv_folds: Number of cross-validation folds.
        """
        # Predictions on training data
        y_pred = self.model.predict(X)

        # Basic metrics
        mse = mean_squared_error(y, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y, y_pred)
        r2 = r2_score(y, y_pred)

        # Adjusted R-squared
        n = len(y)
        p = X.shape[1]
        adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1) if n > p + 1 else r2

        # Cross-validation scores
        cv = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
        cv_scores = cross_val_score(self.model, X, y, cv=cv, scoring='r2')

        self.metrics = {
            'r_squared': float(r2),
            'adjusted_r_squared': float(adj_r2),
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'cv_r2_mean': float(cv_scores.mean()),
            'cv_r2_std': float(cv_scores.std()),
            'cv_r2_scores': [float(s) for s in cv_scores],
            'n_samples': int(n),
            'n_features': int(p)
        }

    def _compute_feature_importance(self) -> None:
        """Compute and store feature importance based on coefficients."""
        feature_names = self.preprocessor.get_feature_names()
        coefficients = self.model.coef_

        self.feature_importance = format_feature_importance(
            feature_names=feature_names,
            importance_values=coefficients,
            sort_descending=True
        )

    def predict(
        self,
        df: pd.DataFrame,
        return_confidence: bool = False
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Make predictions for new campaign data.

        Args:
            df: DataFrame containing feature columns.
            return_confidence: Whether to return prediction intervals.

        Returns:
            Predicted values, or tuple of (predictions, intervals) if return_confidence=True.

        Raises:
            ValueError: If model has not been fitted.
        """
        if not self._is_fitted:
            raise ValueError("Model has not been fitted. Call fit() first.")

        # Transform input features
        X = df[self._get_all_features()].copy()
        X_transformed = self.preprocessor.transform(X)

        # Make predictions
        predictions = self.model.predict(X_transformed)

        if return_confidence:
            # Simple prediction interval based on RMSE
            rmse = self.metrics.get('rmse', 0)
            intervals = np.column_stack([
                predictions - 1.96 * rmse,
                predictions + 1.96 * rmse
            ])
            return predictions, intervals

        return predictions

    def predict_single(self, **kwargs) -> Dict[str, Any]:
        """
        Make a prediction for a single campaign.

        Args:
            **kwargs: Feature values as keyword arguments.

        Returns:
            Dictionary with prediction and confidence interval.

        Example:
            >>> model.predict_single(
            ...     budget=5000,
            ...     impressions=150000,
            ...     clicks=4500,
            ...     ctr=3.0,
            ...     cpc=1.11,
            ...     audience_type='lookalike',
            ...     creative_type='video',
            ...     channel='facebook'
            ... )
        """
        # Create DataFrame from kwargs
        df = pd.DataFrame([kwargs])

        # Get prediction with confidence
        prediction, intervals = self.predict(df, return_confidence=True)

        return {
            'prediction': float(prediction[0]),
            'confidence_interval': {
                'lower': float(intervals[0, 0]),
                'upper': float(intervals[0, 1])
            },
            'input_features': kwargs
        }

    def evaluate(
        self,
        df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Evaluate model on a test dataset.

        Args:
            df: DataFrame containing features and target variable.

        Returns:
            Dictionary of evaluation metrics.
        """
        if not self._is_fitted:
            raise ValueError("Model has not been fitted. Call fit() first.")

        X = df[self._get_all_features()].copy()
        y = df[self.target_variable].copy()

        X_transformed = self.preprocessor.transform(X)
        y_pred = self.model.predict(X_transformed)

        mse = mean_squared_error(y, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y, y_pred)
        r2 = r2_score(y, y_pred)

        n = len(y)
        p = X_transformed.shape[1]
        adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1) if n > p + 1 else r2

        return {
            'r_squared': float(r2),
            'adjusted_r_squared': float(adj_r2),
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'n_samples': int(n)
        }

    def get_feature_importance(
        self,
        top_n: Optional[int] = None,
        include_zero: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get feature importance rankings.

        Args:
            top_n: Number of top features to return (None for all).
            include_zero: Whether to include features with zero importance.

        Returns:
            List of feature importance dictionaries.
        """
        if not self._is_fitted:
            raise ValueError("Model has not been fitted. Call fit() first.")

        importance = self.feature_importance.copy()

        if not include_zero:
            importance = [f for f in importance if f['abs_importance'] > 0]

        if top_n is not None:
            importance = importance[:top_n]

        return importance

    def get_vif_report(
        self,
        threshold: float = 10.0
    ) -> Dict[str, Any]:
        """
        Get multicollinearity report based on VIF.

        Args:
            threshold: VIF threshold for flagging multicollinearity.

        Returns:
            Dictionary with VIF results and recommendations.
        """
        if not self.vif_results:
            return {
                'status': 'not_computed',
                'message': 'VIF was not computed during model fitting.'
            }

        problematic_features = [
            vif for vif in self.vif_results
            if vif['vif'] is not None and vif['vif'] > threshold
        ]

        return {
            'status': 'completed',
            'threshold': threshold,
            'all_results': self.vif_results,
            'problematic_features': problematic_features,
            'has_multicollinearity': len(problematic_features) > 0,
            'recommendation': (
                f"Consider removing or combining features: "
                f"{[f['feature'] for f in problematic_features]}"
                if problematic_features else "No significant multicollinearity detected."
            )
        }

    def get_model_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive model summary.

        Returns:
            Dictionary containing model summary information.
        """
        if not self._is_fitted:
            raise ValueError("Model has not been fitted. Call fit() first.")

        return create_model_summary(
            model_name='CampaignRegressionModel',
            metrics=self.metrics,
            feature_importance=self.feature_importance,
            training_info={
                'target_variable': self.target_variable,
                'numeric_features': self.numeric_features,
                'categorical_features': self.categorical_features,
                'n_features_transformed': self._n_features,
                'n_samples_train': self._n_samples_train,
                'intercept': float(self.model.intercept_) if self.model else None
            }
        )

    def get_coefficients(self) -> Dict[str, float]:
        """
        Get model coefficients with feature names.

        Returns:
            Dictionary mapping feature names to coefficients.
        """
        if not self._is_fitted:
            raise ValueError("Model has not been fitted. Call fit() first.")

        feature_names = self.preprocessor.get_feature_names()
        coefficients = self.model.coef_

        return {
            name: float(coef)
            for name, coef in zip(feature_names, coefficients)
        }

    def get_intercept(self) -> float:
        """
        Get model intercept.

        Returns:
            The intercept value.
        """
        if not self._is_fitted:
            raise ValueError("Model has not been fitted. Call fit() first.")
        return float(self.model.intercept_)

    def save(self, filepath: str) -> str:
        """
        Save the model to disk.

        Args:
            filepath: Path where the model will be saved.

        Returns:
            The path where the model was saved.
        """
        if not self._is_fitted:
            raise ValueError("Model has not been fitted. Call fit() first.")

        model_data = {
            'sklearn_model': self.model,
            'preprocessor': self.preprocessor,
            'target_variable': self.target_variable,
            'numeric_features': self.numeric_features,
            'categorical_features': self.categorical_features,
            'metrics': self.metrics,
            'feature_importance': self.feature_importance,
            'vif_results': self.vif_results,
            'n_features': self._n_features,
            'n_samples_train': self._n_samples_train
        }

        return save_model(model_data, filepath, metadata={
            'model_type': 'CampaignRegressionModel',
            'target': self.target_variable
        })

    @classmethod
    def load(cls, filepath: str) -> 'CampaignRegressionModel':
        """
        Load a saved model from disk.

        Args:
            filepath: Path to the saved model file.

        Returns:
            Loaded CampaignRegressionModel instance.
        """
        bundle = load_model(filepath)
        model_data = bundle['model']

        instance = cls(
            target_variable=model_data['target_variable'],
            numeric_features=model_data['numeric_features'],
            categorical_features=model_data['categorical_features']
        )

        instance.model = model_data['sklearn_model']
        instance.preprocessor = model_data['preprocessor']
        instance.metrics = model_data['metrics']
        instance.feature_importance = model_data['feature_importance']
        instance.vif_results = model_data['vif_results']
        instance._n_features = model_data['n_features']
        instance._n_samples_train = model_data['n_samples_train']
        instance._is_fitted = True

        return instance

    @property
    def is_fitted(self) -> bool:
        """Check if model has been fitted."""
        return self._is_fitted

    def __repr__(self) -> str:
        """String representation of the model."""
        status = "fitted" if self._is_fitted else "not fitted"
        return (
            f"CampaignRegressionModel(target='{self.target_variable}', "
            f"status='{status}', features={self._n_features if self._is_fitted else 'N/A'})"
        )


def train_campaign_model(
    data_path: str,
    target_variable: str = 'conversions',
    test_size: float = 0.2,
    save_path: Optional[str] = None
) -> Tuple[CampaignRegressionModel, Dict[str, Any]]:
    """
    Convenience function to train a campaign regression model.

    Args:
        data_path: Path to the CSV file containing campaign data.
        target_variable: Name of the target variable.
        test_size: Proportion of data for testing.
        save_path: Optional path to save the trained model.

    Returns:
        Tuple of (trained model, evaluation results dictionary).
    """
    from sklearn.model_selection import train_test_split

    # Load data
    df = pd.read_csv(data_path)

    # Split data
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=42
    )

    # Initialize and train model
    model = CampaignRegressionModel(target_variable=target_variable)
    model.fit(train_df)

    # Evaluate on test set
    test_metrics = model.evaluate(test_df)

    results = {
        'training_metrics': model.metrics,
        'test_metrics': test_metrics,
        'feature_importance': model.get_feature_importance(),
        'vif_report': model.get_vif_report(),
        'model_summary': model.get_model_summary()
    }

    # Save model if path provided
    if save_path:
        model.save(save_path)
        results['saved_to'] = save_path

    return model, results
