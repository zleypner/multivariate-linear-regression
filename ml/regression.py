"""
Multivariate Linear Regression model for campaign analytics.
"""

from typing import Any
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

from .preprocessor import CampaignDataPreprocessor


class MultivariateCampaignRegressor:
    """
    Multivariate linear regression model for predicting campaign metrics.

    Supports multiple regression types: OLS, Ridge, and Lasso.
    """

    SUPPORTED_MODELS = {"ols": LinearRegression, "ridge": Ridge, "lasso": Lasso}

    def __init__(
        self,
        model_type: str = "ols",
        alpha: float = 1.0,
        random_state: int = 42,
    ) -> None:
        """
        Initialize the regressor.

        Args:
            model_type: Type of regression ('ols', 'ridge', 'lasso')
            alpha: Regularization strength for Ridge/Lasso
            random_state: Random seed for reproducibility
        """
        if model_type not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"model_type must be one of {list(self.SUPPORTED_MODELS.keys())}"
            )

        self.model_type = model_type
        self.alpha = alpha
        self.random_state = random_state

        # Initialize model
        if model_type == "ols":
            self.model = LinearRegression()
        elif model_type == "ridge":
            self.model = Ridge(alpha=alpha, random_state=random_state)
        else:
            self.model = Lasso(alpha=alpha, random_state=random_state)

        self.preprocessor = CampaignDataPreprocessor()
        self.is_trained: bool = False
        self.target_column: str = ""
        self.training_metrics: dict[str, Any] = {}
        self.feature_importance: dict[str, float] = {}

    def train(
        self,
        df: pd.DataFrame,
        target_column: str = "revenue",
        categorical_features: list[str] | None = None,
        numerical_features: list[str] | None = None,
        test_size: float = 0.2,
        cv_folds: int = 5,
    ) -> dict[str, Any]:
        """
        Train the regression model on campaign data.

        Args:
            df: Training DataFrame
            target_column: Name of target variable column
            categorical_features: List of categorical feature columns
            numerical_features: List of numerical feature columns
            test_size: Proportion of data for test set
            cv_folds: Number of cross-validation folds

        Returns:
            Dictionary with training metrics and results
        """
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in data")

        self.target_column = target_column

        # Prepare features
        X = self.preprocessor.fit_transform(
            df,
            categorical_features=categorical_features,
            numerical_features=numerical_features,
        )
        y = df[target_column].values

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state
        )

        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Predictions
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)

        # Calculate metrics
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)

        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X, y, cv=cv_folds, scoring="r2"
        )

        # Feature importance (coefficients)
        feature_names = self.preprocessor.get_feature_names()
        coefficients = self.model.coef_

        self.feature_importance = {
            name: float(coef)
            for name, coef in zip(feature_names, coefficients)
        }

        # Sort by absolute importance
        sorted_importance = dict(
            sorted(
                self.feature_importance.items(),
                key=lambda x: abs(x[1]),
                reverse=True,
            )
        )

        self.training_metrics = {
            "model_type": self.model_type,
            "target_column": target_column,
            "n_samples": len(df),
            "n_features": len(feature_names),
            "train_r2": float(train_r2),
            "test_r2": float(test_r2),
            "train_rmse": float(train_rmse),
            "test_rmse": float(test_rmse),
            "train_mae": float(train_mae),
            "test_mae": float(test_mae),
            "cv_r2_mean": float(cv_scores.mean()),
            "cv_r2_std": float(cv_scores.std()),
            "intercept": float(self.model.intercept_),
            "coefficients": self.feature_importance.copy(),
            "feature_importance": sorted_importance,
            "feature_names": feature_names,
        }

        return self.training_metrics

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Make predictions on new data.

        Args:
            df: DataFrame with same feature columns as training data

        Returns:
            Array of predictions
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        X = self.preprocessor.transform(df)
        return self.model.predict(X)

    def predict_single(self, data: dict[str, Any]) -> float:
        """
        Make prediction for a single campaign.

        Args:
            data: Dictionary with feature values

        Returns:
            Single prediction value
        """
        df = pd.DataFrame([data])
        predictions = self.predict(df)
        return float(predictions[0])

    def get_metrics(self) -> dict[str, Any]:
        """Return training metrics."""
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        return self.training_metrics.copy()

    def get_coefficients(self) -> dict[str, float]:
        """Return model coefficients."""
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        return self.feature_importance.copy()

    def evaluate(self, df: pd.DataFrame) -> dict[str, float]:
        """
        Evaluate model on new data.

        Args:
            df: DataFrame with features and target column

        Returns:
            Dictionary with evaluation metrics
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")

        if self.target_column not in df.columns:
            raise ValueError(f"Target column '{self.target_column}' not in data")

        X = self.preprocessor.transform(df)
        y_true = df[self.target_column].values
        y_pred = self.model.predict(X)

        return {
            "r2": float(r2_score(y_true, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "mae": float(mean_absolute_error(y_true, y_pred)),
        }
