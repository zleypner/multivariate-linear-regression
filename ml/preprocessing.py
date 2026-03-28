"""
Data preprocessing module for campaign analytics ML.

This module provides utilities for data cleaning, feature scaling,
categorical encoding, and train/test splitting.
"""

from typing import Tuple, List, Optional, Dict, Any
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer


class CampaignDataPreprocessor:
    """
    Preprocessor for campaign analytics data.

    Handles missing values, scales numeric features, and encodes categorical features.

    Attributes:
        numeric_features: List of numeric feature column names.
        categorical_features: List of categorical feature column names.
        preprocessor: Fitted ColumnTransformer for data transformation.
        feature_names_out: List of feature names after transformation.
    """

    def __init__(
        self,
        numeric_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None
    ):
        """
        Initialize the preprocessor.

        Args:
            numeric_features: List of numeric column names. Defaults to standard campaign features.
            categorical_features: List of categorical column names. Defaults to standard categories.
        """
        self.numeric_features = numeric_features or [
            'budget', 'impressions', 'clicks', 'ctr', 'cpc'
        ]
        self.categorical_features = categorical_features or [
            'audience_type', 'creative_type', 'channel'
        ]
        self.preprocessor: Optional[ColumnTransformer] = None
        self.feature_names_out: List[str] = []
        self._is_fitted: bool = False

    def _create_preprocessor(self) -> ColumnTransformer:
        """
        Create the column transformer for preprocessing.

        Returns:
            Configured ColumnTransformer with numeric scaling and categorical encoding.
        """
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.numeric_features),
                ('cat', categorical_transformer, self.categorical_features)
            ],
            remainder='drop'
        )

        return preprocessor

    def fit(self, X: pd.DataFrame) -> 'CampaignDataPreprocessor':
        """
        Fit the preprocessor to the data.

        Args:
            X: DataFrame containing features to fit on.

        Returns:
            Self for method chaining.
        """
        self.preprocessor = self._create_preprocessor()
        self.preprocessor.fit(X)
        self._extract_feature_names()
        self._is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Transform the data using the fitted preprocessor.

        Args:
            X: DataFrame containing features to transform.

        Returns:
            Transformed numpy array.

        Raises:
            ValueError: If preprocessor has not been fitted.
        """
        if not self._is_fitted:
            raise ValueError("Preprocessor has not been fitted. Call fit() first.")
        return self.preprocessor.transform(X)

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Fit the preprocessor and transform data in one step.

        Args:
            X: DataFrame containing features to fit and transform.

        Returns:
            Transformed numpy array.
        """
        self.fit(X)
        return self.transform(X)

    def _extract_feature_names(self) -> None:
        """Extract feature names after transformation."""
        feature_names = []

        # Add numeric feature names (unchanged)
        feature_names.extend(self.numeric_features)

        # Add one-hot encoded feature names
        if hasattr(self.preprocessor, 'named_transformers_'):
            cat_encoder = self.preprocessor.named_transformers_['cat'].named_steps['encoder']
            if hasattr(cat_encoder, 'get_feature_names_out'):
                cat_feature_names = cat_encoder.get_feature_names_out(self.categorical_features)
                feature_names.extend(cat_feature_names)

        self.feature_names_out = list(feature_names)

    def get_feature_names(self) -> List[str]:
        """
        Get the feature names after transformation.

        Returns:
            List of feature names.
        """
        return self.feature_names_out.copy()

    @property
    def is_fitted(self) -> bool:
        """Check if preprocessor has been fitted."""
        return self._is_fitted


def handle_missing_values(
    df: pd.DataFrame,
    numeric_strategy: str = 'median',
    categorical_strategy: str = 'most_frequent'
) -> pd.DataFrame:
    """
    Handle missing values in a DataFrame.

    Args:
        df: Input DataFrame.
        numeric_strategy: Strategy for numeric columns ('mean', 'median', 'most_frequent').
        categorical_strategy: Strategy for categorical columns ('most_frequent', 'constant').

    Returns:
        DataFrame with missing values handled.
    """
    df_clean = df.copy()

    # Handle numeric columns
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        numeric_imputer = SimpleImputer(strategy=numeric_strategy)
        df_clean[numeric_cols] = numeric_imputer.fit_transform(df_clean[numeric_cols])

    # Handle categorical columns
    categorical_cols = df_clean.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        categorical_imputer = SimpleImputer(strategy=categorical_strategy)
        df_clean[categorical_cols] = categorical_imputer.fit_transform(df_clean[categorical_cols])

    return df_clean


def create_train_test_split(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    random_state: int = 42,
    stratify: Optional[pd.Series] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split data into training and testing sets.

    Args:
        X: Feature DataFrame.
        y: Target Series.
        test_size: Proportion of data for testing (0.0 to 1.0).
        random_state: Random seed for reproducibility.
        stratify: Optional series for stratified splitting.

    Returns:
        Tuple of (X_train, X_test, y_train, y_test).
    """
    return train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify
    )


def detect_missing_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze missing data patterns in a DataFrame.

    Args:
        df: Input DataFrame.

    Returns:
        Dictionary containing missing data statistics.
    """
    total_cells = df.size
    missing_cells = df.isnull().sum().sum()

    missing_by_column = df.isnull().sum()
    missing_pct_by_column = (missing_by_column / len(df)) * 100

    return {
        'total_missing': int(missing_cells),
        'total_cells': int(total_cells),
        'missing_percentage': float(missing_cells / total_cells * 100) if total_cells > 0 else 0.0,
        'missing_by_column': missing_by_column.to_dict(),
        'missing_pct_by_column': missing_pct_by_column.to_dict(),
        'columns_with_missing': list(missing_by_column[missing_by_column > 0].index)
    }


def encode_categorical_features(
    df: pd.DataFrame,
    categorical_columns: List[str],
    drop_first: bool = False
) -> Tuple[pd.DataFrame, Dict[str, List[str]]]:
    """
    One-hot encode categorical features.

    Args:
        df: Input DataFrame.
        categorical_columns: List of columns to encode.
        drop_first: Whether to drop first category to avoid multicollinearity.

    Returns:
        Tuple of (encoded DataFrame, mapping of original to new column names).
    """
    encoder = OneHotEncoder(drop='first' if drop_first else None, sparse_output=False)

    # Fit and transform categorical columns
    encoded_data = encoder.fit_transform(df[categorical_columns])
    encoded_feature_names = encoder.get_feature_names_out(categorical_columns)

    # Create DataFrame with encoded features
    encoded_df = pd.DataFrame(
        encoded_data,
        columns=encoded_feature_names,
        index=df.index
    )

    # Combine with non-categorical columns
    non_categorical_cols = [col for col in df.columns if col not in categorical_columns]
    result_df = pd.concat([df[non_categorical_cols], encoded_df], axis=1)

    # Create mapping
    column_mapping = {}
    for col in categorical_columns:
        column_mapping[col] = [
            name for name in encoded_feature_names if name.startswith(f"{col}_")
        ]

    return result_df, column_mapping


def scale_numeric_features(
    df: pd.DataFrame,
    numeric_columns: List[str],
    scaler: Optional[StandardScaler] = None
) -> Tuple[pd.DataFrame, StandardScaler]:
    """
    Scale numeric features using StandardScaler.

    Args:
        df: Input DataFrame.
        numeric_columns: List of numeric columns to scale.
        scaler: Optional pre-fitted scaler to use.

    Returns:
        Tuple of (scaled DataFrame, fitted scaler).
    """
    df_scaled = df.copy()

    if scaler is None:
        scaler = StandardScaler()
        df_scaled[numeric_columns] = scaler.fit_transform(df[numeric_columns])
    else:
        df_scaled[numeric_columns] = scaler.transform(df[numeric_columns])

    return df_scaled, scaler
