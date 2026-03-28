"""
Data preprocessing for campaign analytics multivariate regression.
"""

from typing import Any
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder


class CampaignDataPreprocessor:
    """Preprocessor for campaign data with encoding and scaling."""

    # Default feature columns for campaign data
    CATEGORICAL_FEATURES = ["audience_type", "creative_type", "channel"]
    NUMERICAL_FEATURES = ["budget", "impressions", "clicks", "ctr", "cpc"]
    DEFAULT_TARGET = "revenue"

    def __init__(self) -> None:
        self.label_encoders: dict[str, LabelEncoder] = {}
        self.scaler: StandardScaler = StandardScaler()
        self.feature_names: list[str] = []
        self.is_fitted: bool = False

    def fit(
        self,
        df: pd.DataFrame,
        categorical_features: list[str] | None = None,
        numerical_features: list[str] | None = None,
    ) -> "CampaignDataPreprocessor":
        """
        Fit the preprocessor on training data.

        Args:
            df: Input DataFrame
            categorical_features: List of categorical column names
            numerical_features: List of numerical column names

        Returns:
            self for method chaining
        """
        categorical_features = categorical_features or self.CATEGORICAL_FEATURES
        numerical_features = numerical_features or self.NUMERICAL_FEATURES

        # Filter to only existing columns
        categorical_features = [c for c in categorical_features if c in df.columns]
        numerical_features = [n for n in numerical_features if n in df.columns]

        # Fit label encoders for categorical features
        for col in categorical_features:
            le = LabelEncoder()
            le.fit(df[col].astype(str))
            self.label_encoders[col] = le

        # Build feature names list
        self.feature_names = numerical_features + categorical_features

        # Fit scaler on all features
        X = self._encode_features(df, categorical_features, numerical_features)
        self.scaler.fit(X)

        self.is_fitted = True
        return self

    def transform(
        self,
        df: pd.DataFrame,
        categorical_features: list[str] | None = None,
        numerical_features: list[str] | None = None,
    ) -> np.ndarray:
        """
        Transform data using fitted preprocessor.

        Args:
            df: Input DataFrame
            categorical_features: List of categorical column names
            numerical_features: List of numerical column names

        Returns:
            Scaled feature array
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transform")

        categorical_features = categorical_features or self.CATEGORICAL_FEATURES
        numerical_features = numerical_features or self.NUMERICAL_FEATURES

        # Filter to only existing columns
        categorical_features = [c for c in categorical_features if c in df.columns]
        numerical_features = [n for n in numerical_features if n in df.columns]

        X = self._encode_features(df, categorical_features, numerical_features)
        return self.scaler.transform(X)

    def fit_transform(
        self,
        df: pd.DataFrame,
        categorical_features: list[str] | None = None,
        numerical_features: list[str] | None = None,
    ) -> np.ndarray:
        """
        Fit and transform data in one step.

        Args:
            df: Input DataFrame
            categorical_features: List of categorical column names
            numerical_features: List of numerical column names

        Returns:
            Scaled feature array
        """
        self.fit(df, categorical_features, numerical_features)
        return self.transform(df, categorical_features, numerical_features)

    def _encode_features(
        self,
        df: pd.DataFrame,
        categorical_features: list[str],
        numerical_features: list[str],
    ) -> np.ndarray:
        """
        Encode categorical and combine with numerical features.

        Args:
            df: Input DataFrame
            categorical_features: List of categorical column names
            numerical_features: List of numerical column names

        Returns:
            Combined feature array
        """
        # Get numerical features
        X_numerical = df[numerical_features].values.astype(float)

        # Encode categorical features
        X_categorical_list = []
        for col in categorical_features:
            le = self.label_encoders.get(col)
            if le is not None:
                # Handle unseen categories by using a default value
                encoded = []
                for val in df[col].astype(str):
                    if val in le.classes_:
                        encoded.append(le.transform([val])[0])
                    else:
                        encoded.append(-1)  # Unknown category
                X_categorical_list.append(np.array(encoded).reshape(-1, 1))

        if X_categorical_list:
            X_categorical = np.hstack(X_categorical_list)
            return np.hstack([X_numerical, X_categorical])
        return X_numerical

    def get_feature_names(self) -> list[str]:
        """Return list of feature names in order."""
        return self.feature_names.copy()

    def get_category_mapping(self, column: str) -> dict[str, int]:
        """Get the mapping of category values to encoded integers."""
        if column not in self.label_encoders:
            raise ValueError(f"Column {column} not found in encoders")
        le = self.label_encoders[column]
        return {cls: idx for idx, cls in enumerate(le.classes_)}
