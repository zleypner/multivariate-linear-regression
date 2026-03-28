"""
Data Pipeline Module for Campaign Analytics System.

This module provides production-ready components for data loading, validation,
and transformation in the campaign analytics pipeline.

Classes:
    CSVDataLoader: Loads and validates CSV files
    DataValidator: Validates data quality and schema compliance
    DataTransformer: Transforms data for ML consumption
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from scipy import stats

# Configure module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler if not already present
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@dataclass
class ValidationResult:
    """Container for validation results."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return self.is_valid

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)


class CSVDataLoader:
    """
    Loads and validates CSV files for campaign analytics.

    This class handles file reading, initial parsing, and basic validation
    of CSV data files. It supports schema validation and provides detailed
    error reporting.

    Attributes:
        schema_path: Path to the JSON schema file
        schema: Loaded schema dictionary

    Example:
        >>> loader = CSVDataLoader(schema_path="data/schema.json")
        >>> df = loader.load("data/sample_campaigns.csv")
        >>> print(f"Loaded {len(df)} records")
    """

    def __init__(self, schema_path: Optional[Union[str, Path]] = None):
        """
        Initialize the CSV data loader.

        Args:
            schema_path: Optional path to JSON schema file for validation
        """
        self.schema_path = Path(schema_path) if schema_path else None
        self.schema: Optional[Dict] = None

        if self.schema_path and self.schema_path.exists():
            self._load_schema()

    def _load_schema(self) -> None:
        """Load schema from JSON file."""
        try:
            with open(self.schema_path, 'r') as f:
                self.schema = json.load(f)
            logger.info(f"Schema loaded from {self.schema_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse schema JSON: {e}")
            raise ValueError(f"Invalid schema JSON: {e}")
        except IOError as e:
            logger.error(f"Failed to read schema file: {e}")
            raise

    def load(
        self,
        file_path: Union[str, Path],
        validate: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load CSV file into a pandas DataFrame.

        Args:
            file_path: Path to the CSV file
            validate: Whether to validate against schema
            **kwargs: Additional arguments passed to pd.read_csv

        Returns:
            Loaded DataFrame

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If validation fails
        """
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        logger.info(f"Loading CSV file: {file_path}")

        try:
            # Set default parameters for robust CSV reading
            default_params = {
                'encoding': 'utf-8',
                'on_bad_lines': 'warn',
                'low_memory': False
            }
            default_params.update(kwargs)

            df = pd.read_csv(file_path, **default_params)
            logger.info(f"Loaded {len(df)} records with {len(df.columns)} columns")

            if validate and self.schema:
                validation_result = self._validate_schema(df)
                if not validation_result.is_valid:
                    error_msg = "; ".join(validation_result.errors)
                    raise ValueError(f"Schema validation failed: {error_msg}")

                for warning in validation_result.warnings:
                    logger.warning(warning)

            return df

        except pd.errors.EmptyDataError:
            logger.error("CSV file is empty")
            raise ValueError("CSV file is empty")
        except pd.errors.ParserError as e:
            logger.error(f"CSV parsing error: {e}")
            raise ValueError(f"Failed to parse CSV: {e}")

    def _validate_schema(self, df: pd.DataFrame) -> ValidationResult:
        """
        Validate DataFrame against loaded schema.

        Args:
            df: DataFrame to validate

        Returns:
            ValidationResult with validation status and messages
        """
        result = ValidationResult(is_valid=True)

        if not self.schema:
            result.add_warning("No schema loaded, skipping validation")
            return result

        schema_columns = self.schema.get('columns', {})

        # Check required columns
        for col_name, col_spec in schema_columns.items():
            if col_spec.get('required', False) and col_name not in df.columns:
                result.add_error(f"Required column missing: {col_name}")

        # Check for unexpected columns
        expected_cols = set(schema_columns.keys())
        actual_cols = set(df.columns)
        unexpected = actual_cols - expected_cols

        if unexpected:
            result.add_warning(f"Unexpected columns found: {unexpected}")

        result.statistics['total_columns'] = len(df.columns)
        result.statistics['total_rows'] = len(df)

        return result

    def get_column_info(self) -> Dict[str, Dict]:
        """
        Get column information from schema.

        Returns:
            Dictionary of column specifications
        """
        if not self.schema:
            return {}
        return self.schema.get('columns', {})


class DataValidator:
    """
    Validates data quality and schema compliance.

    This class performs comprehensive data validation including:
    - Required column checks
    - Data type validation
    - Range and constraint validation
    - Categorical value validation

    Example:
        >>> validator = DataValidator(schema_path="data/schema.json")
        >>> result = validator.validate(df)
        >>> if not result.is_valid:
        ...     print(f"Validation errors: {result.errors}")
    """

    def __init__(self, schema_path: Optional[Union[str, Path]] = None):
        """
        Initialize the data validator.

        Args:
            schema_path: Optional path to JSON schema file
        """
        self.schema_path = Path(schema_path) if schema_path else None
        self.schema: Optional[Dict] = None

        if self.schema_path and self.schema_path.exists():
            self._load_schema()

    def _load_schema(self) -> None:
        """Load schema from JSON file."""
        try:
            with open(self.schema_path, 'r') as f:
                self.schema = json.load(f)
            logger.info(f"Validator schema loaded from {self.schema_path}")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load schema: {e}")
            raise

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """
        Perform comprehensive data validation.

        Args:
            df: DataFrame to validate

        Returns:
            ValidationResult with validation status and details
        """
        result = ValidationResult(is_valid=True)

        logger.info("Starting data validation...")

        # Check if DataFrame is empty
        if df.empty:
            result.add_error("DataFrame is empty")
            return result

        # Run all validation checks
        self._validate_required_columns(df, result)
        self._validate_data_types(df, result)
        self._validate_numeric_constraints(df, result)
        self._validate_categorical_values(df, result)
        self._validate_data_integrity(df, result)

        # Generate statistics
        result.statistics['row_count'] = len(df)
        result.statistics['column_count'] = len(df.columns)
        result.statistics['missing_cells'] = df.isnull().sum().sum()
        result.statistics['missing_percentage'] = (
            df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
        )

        if result.is_valid:
            logger.info("Data validation passed successfully")
        else:
            logger.error(f"Data validation failed with {len(result.errors)} errors")

        return result

    def _validate_required_columns(
        self, df: pd.DataFrame, result: ValidationResult
    ) -> None:
        """Check that all required columns exist."""
        if not self.schema:
            return

        columns = self.schema.get('columns', {})
        for col_name, col_spec in columns.items():
            if col_spec.get('required', False) and col_name not in df.columns:
                result.add_error(f"Required column '{col_name}' is missing")

    def _validate_data_types(
        self, df: pd.DataFrame, result: ValidationResult
    ) -> None:
        """Validate data types match schema expectations."""
        if not self.schema:
            return

        columns = self.schema.get('columns', {})
        type_mapping = {
            'integer': ['int64', 'int32', 'Int64', 'Int32'],
            'float': ['float64', 'float32', 'Float64', 'Float32', 'int64', 'int32'],
            'string': ['object', 'string'],
            'categorical': ['object', 'category', 'string']
        }

        for col_name, col_spec in columns.items():
            if col_name not in df.columns:
                continue

            expected_type = col_spec.get('type')
            if not expected_type:
                continue

            actual_type = str(df[col_name].dtype)
            allowed_types = type_mapping.get(expected_type, [expected_type])

            if actual_type not in allowed_types:
                # Try to infer if type is compatible
                if expected_type in ('integer', 'float'):
                    if not pd.api.types.is_numeric_dtype(df[col_name]):
                        result.add_warning(
                            f"Column '{col_name}' has type '{actual_type}', "
                            f"expected '{expected_type}'"
                        )

    def _validate_numeric_constraints(
        self, df: pd.DataFrame, result: ValidationResult
    ) -> None:
        """Validate numeric columns have no negative values and meet constraints."""
        if not self.schema:
            # Default validation: check common numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if col in ['budget', 'impressions', 'clicks', 'conversions',
                          'revenue', 'ctr', 'cpc', 'cpl', 'roas']:
                    negative_count = (df[col] < 0).sum()
                    if negative_count > 0:
                        result.add_error(
                            f"Column '{col}' contains {negative_count} negative values"
                        )
            return

        columns = self.schema.get('columns', {})
        for col_name, col_spec in columns.items():
            if col_name not in df.columns:
                continue

            if col_spec.get('type') not in ('integer', 'float'):
                continue

            constraints = col_spec.get('constraints', {})
            col_data = df[col_name].dropna()

            if 'min_value' in constraints:
                min_val = constraints['min_value']
                violations = (col_data < min_val).sum()
                if violations > 0:
                    result.add_error(
                        f"Column '{col_name}': {violations} values below minimum {min_val}"
                    )

            if 'max_value' in constraints:
                max_val = constraints['max_value']
                violations = (col_data > max_val).sum()
                if violations > 0:
                    result.add_error(
                        f"Column '{col_name}': {violations} values above maximum {max_val}"
                    )

    def _validate_categorical_values(
        self, df: pd.DataFrame, result: ValidationResult
    ) -> None:
        """Validate categorical columns have valid values."""
        if not self.schema:
            return

        columns = self.schema.get('columns', {})
        for col_name, col_spec in columns.items():
            if col_name not in df.columns:
                continue

            if col_spec.get('type') != 'categorical':
                continue

            constraints = col_spec.get('constraints', {})
            allowed_values = constraints.get('allowed_values')

            if allowed_values:
                actual_values = set(df[col_name].dropna().unique())
                invalid_values = actual_values - set(allowed_values)

                if invalid_values:
                    result.add_error(
                        f"Column '{col_name}' contains invalid values: {invalid_values}"
                    )

    def _validate_data_integrity(
        self, df: pd.DataFrame, result: ValidationResult
    ) -> None:
        """Validate data integrity constraints."""
        if not self.schema:
            return

        columns = self.schema.get('columns', {})

        # Check unique constraints
        for col_name, col_spec in columns.items():
            if col_name not in df.columns:
                continue

            constraints = col_spec.get('constraints', {})
            if constraints.get('unique', False):
                duplicates = df[col_name].duplicated().sum()
                if duplicates > 0:
                    result.add_error(
                        f"Column '{col_name}' has {duplicates} duplicate values"
                    )

        # Validate derived metrics consistency
        if all(col in df.columns for col in ['clicks', 'impressions', 'ctr']):
            calculated_ctr = (df['clicks'] / df['impressions'] * 100).round(1)
            actual_ctr = df['ctr'].round(1)
            mismatches = (calculated_ctr != actual_ctr).sum()
            if mismatches > 0:
                result.add_warning(
                    f"CTR inconsistency detected in {mismatches} records"
                )


class DataTransformer:
    """
    Transforms data for machine learning consumption.

    This class handles:
    - Missing value imputation
    - Outlier detection and handling
    - Feature engineering
    - Log transformations for skewed data
    - Data normalization and scaling

    Example:
        >>> transformer = DataTransformer()
        >>> df_transformed = transformer.fit_transform(df)
        >>> print(f"Features: {df_transformed.columns.tolist()}")
    """

    def __init__(
        self,
        outlier_method: str = 'zscore',
        outlier_threshold: float = 3.0,
        log_transform_threshold: float = 1.0
    ):
        """
        Initialize the data transformer.

        Args:
            outlier_method: Method for outlier detection ('zscore' or 'iqr')
            outlier_threshold: Threshold for outlier detection
            log_transform_threshold: Skewness threshold for log transformation
        """
        self.outlier_method = outlier_method
        self.outlier_threshold = outlier_threshold
        self.log_transform_threshold = log_transform_threshold

        # Fitted parameters
        self._fitted = False
        self._imputation_values: Dict[str, float] = {}
        self._outlier_bounds: Dict[str, Tuple[float, float]] = {}
        self._log_transformed_cols: List[str] = []
        self._numeric_columns: List[str] = []
        self._categorical_columns: List[str] = []

    def fit(self, df: pd.DataFrame) -> 'DataTransformer':
        """
        Fit the transformer to the data.

        Args:
            df: DataFrame to fit

        Returns:
            Self for method chaining
        """
        logger.info("Fitting data transformer...")

        # Identify column types
        self._numeric_columns = df.select_dtypes(
            include=[np.number]
        ).columns.tolist()
        self._categorical_columns = df.select_dtypes(
            include=['object', 'category']
        ).columns.tolist()

        # Calculate imputation values (median for numeric, mode for categorical)
        for col in self._numeric_columns:
            self._imputation_values[col] = df[col].median()

        for col in self._categorical_columns:
            mode_values = df[col].mode()
            if len(mode_values) > 0:
                self._imputation_values[col] = mode_values.iloc[0]

        # Calculate outlier bounds
        for col in self._numeric_columns:
            self._outlier_bounds[col] = self._calculate_outlier_bounds(
                df[col].dropna()
            )

        # Identify columns for log transformation
        for col in self._numeric_columns:
            if col in ['campaign_id']:  # Skip ID columns
                continue
            skewness = df[col].dropna().skew()
            if abs(skewness) > self.log_transform_threshold:
                self._log_transformed_cols.append(col)

        self._fitted = True
        logger.info(
            f"Transformer fitted: {len(self._numeric_columns)} numeric, "
            f"{len(self._categorical_columns)} categorical columns"
        )

        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the data.

        Args:
            df: DataFrame to transform

        Returns:
            Transformed DataFrame
        """
        if not self._fitted:
            raise ValueError("Transformer must be fitted before transform")

        logger.info("Transforming data...")
        df_transformed = df.copy()

        # Impute missing values
        df_transformed = self._impute_missing(df_transformed)

        # Handle outliers
        df_transformed = self._handle_outliers(df_transformed)

        # Apply log transformations
        df_transformed = self._apply_log_transform(df_transformed)

        # Engineer features
        df_transformed = self._engineer_features(df_transformed)

        logger.info(f"Transformation complete: {df_transformed.shape}")

        return df_transformed

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fit and transform in one step.

        Args:
            df: DataFrame to fit and transform

        Returns:
            Transformed DataFrame
        """
        return self.fit(df).transform(df)

    def _calculate_outlier_bounds(
        self, series: pd.Series
    ) -> Tuple[float, float]:
        """Calculate outlier bounds using specified method."""
        if self.outlier_method == 'zscore':
            mean = series.mean()
            std = series.std()
            lower = mean - self.outlier_threshold * std
            upper = mean + self.outlier_threshold * std
        elif self.outlier_method == 'iqr':
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - self.outlier_threshold * iqr
            upper = q3 + self.outlier_threshold * iqr
        else:
            raise ValueError(f"Unknown outlier method: {self.outlier_method}")

        return (lower, upper)

    def _impute_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Impute missing values."""
        for col, value in self._imputation_values.items():
            if col in df.columns:
                missing_count = df[col].isnull().sum()
                if missing_count > 0:
                    df[col] = df[col].fillna(value)
                    logger.debug(
                        f"Imputed {missing_count} missing values in '{col}'"
                    )

        return df

    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle outliers by clipping to bounds."""
        for col, (lower, upper) in self._outlier_bounds.items():
            if col in df.columns and col in self._numeric_columns:
                # Skip ID columns
                if 'id' in col.lower():
                    continue

                original = df[col].copy()
                df[col] = df[col].clip(lower=lower, upper=upper)

                clipped_count = (original != df[col]).sum()
                if clipped_count > 0:
                    logger.debug(
                        f"Clipped {clipped_count} outliers in '{col}'"
                    )

        return df

    def _apply_log_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply log transformation to skewed columns."""
        for col in self._log_transformed_cols:
            if col in df.columns:
                # Only apply to columns with positive values
                if (df[col] > 0).all():
                    new_col_name = f"{col}_log"
                    df[new_col_name] = np.log1p(df[col])
                    logger.debug(f"Created log-transformed column: {new_col_name}")

        return df

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer derived features."""
        # Engagement rate
        if all(col in df.columns for col in ['clicks', 'impressions']):
            df['engagement_rate'] = np.where(
                df['impressions'] > 0,
                df['clicks'] / df['impressions'],
                0
            )

        # Cost per impression
        if all(col in df.columns for col in ['budget', 'impressions']):
            df['cost_per_impression'] = np.where(
                df['impressions'] > 0,
                df['budget'] / df['impressions'],
                0
            )

        # Conversion rate
        if all(col in df.columns for col in ['conversions', 'clicks']):
            df['conversion_rate'] = np.where(
                df['clicks'] > 0,
                df['conversions'] / df['clicks'],
                0
            )

        # Efficiency score
        if all(col in df.columns for col in ['conversions', 'budget']):
            df['efficiency_score'] = np.where(
                df['budget'] > 0,
                df['conversions'] / df['budget'] * 1000,
                0
            )

        # Revenue per conversion
        if all(col in df.columns for col in ['revenue', 'conversions']):
            df['revenue_per_conversion'] = np.where(
                df['conversions'] > 0,
                df['revenue'] / df['conversions'],
                0
            )

        logger.debug("Feature engineering complete")

        return df

    def get_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get DataFrame of outlier records.

        Args:
            df: DataFrame to check

        Returns:
            DataFrame containing only outlier records
        """
        if not self._fitted:
            raise ValueError("Transformer must be fitted first")

        outlier_mask = pd.Series([False] * len(df), index=df.index)

        for col, (lower, upper) in self._outlier_bounds.items():
            if col in df.columns and col in self._numeric_columns:
                if 'id' in col.lower():
                    continue
                col_outliers = (df[col] < lower) | (df[col] > upper)
                outlier_mask = outlier_mask | col_outliers

        return df[outlier_mask]

    def get_transformation_report(self) -> Dict[str, Any]:
        """
        Get report of transformations applied.

        Returns:
            Dictionary with transformation details
        """
        return {
            'fitted': self._fitted,
            'numeric_columns': self._numeric_columns,
            'categorical_columns': self._categorical_columns,
            'imputation_values': self._imputation_values,
            'outlier_bounds': self._outlier_bounds,
            'log_transformed_columns': self._log_transformed_cols,
            'outlier_method': self.outlier_method,
            'outlier_threshold': self.outlier_threshold
        }


def create_pipeline(
    schema_path: Optional[str] = None
) -> Tuple[CSVDataLoader, DataValidator, DataTransformer]:
    """
    Factory function to create a complete data pipeline.

    Args:
        schema_path: Optional path to schema file

    Returns:
        Tuple of (loader, validator, transformer)

    Example:
        >>> loader, validator, transformer = create_pipeline("data/schema.json")
        >>> df = loader.load("data/sample_campaigns.csv")
        >>> result = validator.validate(df)
        >>> df_transformed = transformer.fit_transform(df)
    """
    loader = CSVDataLoader(schema_path=schema_path)
    validator = DataValidator(schema_path=schema_path)
    transformer = DataTransformer()

    return loader, validator, transformer


def run_pipeline(
    file_path: str,
    schema_path: Optional[str] = None,
    validate: bool = True,
    transform: bool = True
) -> Tuple[pd.DataFrame, ValidationResult, Optional[pd.DataFrame]]:
    """
    Run the complete data pipeline on a CSV file.

    Args:
        file_path: Path to CSV file
        schema_path: Optional path to schema file
        validate: Whether to perform validation
        transform: Whether to transform data

    Returns:
        Tuple of (raw_df, validation_result, transformed_df)

    Example:
        >>> raw_df, result, transformed_df = run_pipeline(
        ...     "data/sample_campaigns.csv",
        ...     "data/schema.json"
        ... )
    """
    loader, validator, transformer = create_pipeline(schema_path)

    # Load data
    raw_df = loader.load(file_path, validate=False)

    # Validate
    validation_result = ValidationResult(is_valid=True)
    if validate:
        validation_result = validator.validate(raw_df)

    # Transform
    transformed_df = None
    if transform:
        transformed_df = transformer.fit_transform(raw_df)

    return raw_df, validation_result, transformed_df


if __name__ == "__main__":
    # Example usage
    import sys

    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Get paths
    script_dir = Path(__file__).parent.parent
    data_path = script_dir / "data" / "sample_campaigns.csv"
    schema_path = script_dir / "data" / "schema.json"

    if not data_path.exists():
        print(f"Data file not found: {data_path}")
        sys.exit(1)

    # Run pipeline
    print("Running data pipeline...")
    raw_df, result, transformed_df = run_pipeline(
        str(data_path),
        str(schema_path) if schema_path.exists() else None
    )

    print(f"\n--- Pipeline Results ---")
    print(f"Raw data shape: {raw_df.shape}")
    print(f"Validation passed: {result.is_valid}")

    if result.errors:
        print(f"Errors: {result.errors}")
    if result.warnings:
        print(f"Warnings: {result.warnings}")

    if transformed_df is not None:
        print(f"Transformed data shape: {transformed_df.shape}")
        print(f"New features: {[c for c in transformed_df.columns if c not in raw_df.columns]}")
