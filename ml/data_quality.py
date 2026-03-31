"""
Data Quality Module for Campaign Analytics System.

This module provides comprehensive data quality checking, summary statistics
generation, and data profiling capabilities for campaign analytics data.

Classes:
    DataQualityChecker: Performs quality checks on data
    StatisticsGenerator: Generates summary statistics
    DataProfiler: Creates comprehensive data profiles
"""

import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

# Configure module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@dataclass
class QualityCheckResult:
    """Container for a single quality check result."""
    check_name: str
    passed: bool
    severity: str  # 'error', 'warning', 'info'
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    affected_rows: int = 0
    affected_percentage: float = 0.0


@dataclass
class DataQualityReport:
    """Container for complete data quality report."""
    timestamp: str
    total_rows: int
    total_columns: int
    checks_passed: int = 0
    checks_failed: int = 0
    checks_warned: int = 0
    overall_score: float = 100.0
    check_results: List[QualityCheckResult] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

    def add_check(self, result: QualityCheckResult) -> None:
        """Add a check result to the report."""
        self.check_results.append(result)

        if result.passed:
            self.checks_passed += 1
        elif result.severity == 'error':
            self.checks_failed += 1
        else:
            self.checks_warned += 1

    def calculate_score(self) -> float:
        """Calculate overall data quality score."""
        total_checks = len(self.check_results)
        if total_checks == 0:
            return 100.0

        # Weight by severity
        error_weight = 10
        warning_weight = 3

        deductions = 0
        for check in self.check_results:
            if not check.passed:
                if check.severity == 'error':
                    deductions += error_weight
                else:
                    deductions += warning_weight

        max_deductions = total_checks * error_weight
        score = max(0, 100 - (deductions / max_deductions * 100))
        self.overall_score = round(score, 2)

        return self.overall_score

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            'timestamp': self.timestamp,
            'total_rows': self.total_rows,
            'total_columns': self.total_columns,
            'checks_passed': self.checks_passed,
            'checks_failed': self.checks_failed,
            'checks_warned': self.checks_warned,
            'overall_score': self.overall_score,
            'check_results': [
                {
                    'check_name': r.check_name,
                    'passed': r.passed,
                    'severity': r.severity,
                    'message': r.message,
                    'details': r.details,
                    'affected_rows': r.affected_rows,
                    'affected_percentage': r.affected_percentage
                }
                for r in self.check_results
            ],
            'summary': self.summary
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert report to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)


class DataQualityChecker:
    """
    Performs comprehensive data quality checks.

    This class implements various quality checks including:
    - Completeness checks (missing values)
    - Validity checks (data type, range, format)
    - Consistency checks (business rules)
    - Uniqueness checks (duplicates)
    - Accuracy checks (statistical anomalies)

    Example:
        >>> checker = DataQualityChecker(schema_path="data/schema.json")
        >>> report = checker.run_checks(df)
        >>> print(f"Quality score: {report.overall_score}%")
    """

    def __init__(
        self,
        schema_path: Optional[Union[str, Path]] = None,
        missing_threshold: float = 0.05,
        outlier_threshold: float = 3.0
    ):
        """
        Initialize the data quality checker.

        Args:
            schema_path: Optional path to JSON schema file
            missing_threshold: Maximum allowed missing value ratio
            outlier_threshold: Z-score threshold for outlier detection
        """
        self.schema_path = Path(schema_path) if schema_path else None
        self.schema: Optional[Dict] = None
        self.missing_threshold = missing_threshold
        self.outlier_threshold = outlier_threshold

        if self.schema_path and self.schema_path.exists():
            self._load_schema()

    def _load_schema(self) -> None:
        """Load schema from JSON file."""
        try:
            with open(self.schema_path, 'r') as f:
                self.schema = json.load(f)
            logger.info(f"Schema loaded for quality checks: {self.schema_path}")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load schema: {e}")

    def run_checks(self, df: pd.DataFrame) -> DataQualityReport:
        """
        Run all data quality checks.

        Args:
            df: DataFrame to check

        Returns:
            DataQualityReport with all check results
        """
        logger.info("Starting data quality checks...")

        report = DataQualityReport(
            timestamp=datetime.now().isoformat(),
            total_rows=len(df),
            total_columns=len(df.columns)
        )

        # Run all check categories
        self._check_completeness(df, report)
        self._check_validity(df, report)
        self._check_consistency(df, report)
        self._check_uniqueness(df, report)
        self._check_accuracy(df, report)

        # Calculate overall score
        report.calculate_score()

        # Generate summary
        report.summary = {
            'total_checks': len(report.check_results),
            'passed': report.checks_passed,
            'failed': report.checks_failed,
            'warnings': report.checks_warned,
            'score': report.overall_score
        }

        logger.info(
            f"Quality checks complete. Score: {report.overall_score}% "
            f"({report.checks_passed}/{len(report.check_results)} passed)"
        )

        return report

    def _check_completeness(
        self, df: pd.DataFrame, report: DataQualityReport
    ) -> None:
        """Check for missing values."""
        # Overall missing value check
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        missing_ratio = missing_cells / total_cells if total_cells > 0 else 0

        report.add_check(QualityCheckResult(
            check_name='overall_completeness',
            passed=missing_ratio <= self.missing_threshold,
            severity='error' if missing_ratio > self.missing_threshold else 'info',
            message=f"Missing value ratio: {missing_ratio:.2%}",
            details={'missing_cells': int(missing_cells), 'total_cells': total_cells},
            affected_rows=int(df.isnull().any(axis=1).sum()),
            affected_percentage=round(missing_ratio * 100, 2)
        ))

        # Per-column missing value check
        for col in df.columns:
            col_missing = df[col].isnull().sum()
            col_missing_ratio = col_missing / len(df) if len(df) > 0 else 0

            # Check required columns more strictly
            is_required = False
            if self.schema:
                col_schema = self.schema.get('columns', {}).get(col, {})
                is_required = col_schema.get('required', False)

            threshold = 0 if is_required else self.missing_threshold

            if col_missing_ratio > threshold:
                report.add_check(QualityCheckResult(
                    check_name=f'completeness_{col}',
                    passed=False,
                    severity='error' if is_required else 'warning',
                    message=f"Column '{col}' has {col_missing_ratio:.2%} missing values",
                    details={'column': col, 'missing_count': int(col_missing)},
                    affected_rows=int(col_missing),
                    affected_percentage=round(col_missing_ratio * 100, 2)
                ))

    def _check_validity(
        self, df: pd.DataFrame, report: DataQualityReport
    ) -> None:
        """Check data validity against schema constraints."""
        if not self.schema:
            return

        columns = self.schema.get('columns', {})

        for col_name, col_spec in columns.items():
            if col_name not in df.columns:
                continue

            constraints = col_spec.get('constraints', {})
            col_data = df[col_name].dropna()

            # Check min/max constraints for numeric columns
            if 'min_value' in constraints:
                min_val = constraints['min_value']
                violations = (col_data < min_val).sum()

                report.add_check(QualityCheckResult(
                    check_name=f'validity_min_{col_name}',
                    passed=violations == 0,
                    severity='error',
                    message=f"Column '{col_name}': {violations} values below minimum {min_val}",
                    details={'column': col_name, 'min_value': min_val},
                    affected_rows=int(violations),
                    affected_percentage=round(violations / len(df) * 100, 2)
                ))

            if 'max_value' in constraints:
                max_val = constraints['max_value']
                violations = (col_data > max_val).sum()

                report.add_check(QualityCheckResult(
                    check_name=f'validity_max_{col_name}',
                    passed=violations == 0,
                    severity='error',
                    message=f"Column '{col_name}': {violations} values above maximum {max_val}",
                    details={'column': col_name, 'max_value': max_val},
                    affected_rows=int(violations),
                    affected_percentage=round(violations / len(df) * 100, 2)
                ))

            # Check categorical constraints
            if 'allowed_values' in constraints:
                allowed = set(constraints['allowed_values'])
                actual = set(col_data.unique())
                invalid = actual - allowed

                report.add_check(QualityCheckResult(
                    check_name=f'validity_categorical_{col_name}',
                    passed=len(invalid) == 0,
                    severity='error',
                    message=f"Column '{col_name}': invalid values {invalid}" if invalid else f"Column '{col_name}': all values valid",
                    details={'column': col_name, 'invalid_values': list(invalid)},
                    affected_rows=int(df[col_name].isin(invalid).sum()) if invalid else 0,
                    affected_percentage=round(df[col_name].isin(invalid).sum() / len(df) * 100, 2) if invalid else 0
                ))

    def _check_consistency(
        self, df: pd.DataFrame, report: DataQualityReport
    ) -> None:
        """Check data consistency and business rules."""
        # Check that clicks <= impressions
        if all(col in df.columns for col in ['clicks', 'impressions']):
            violations = (df['clicks'] > df['impressions']).sum()

            report.add_check(QualityCheckResult(
                check_name='consistency_clicks_impressions',
                passed=violations == 0,
                severity='error',
                message=f"Clicks exceed impressions in {violations} rows",
                details={'rule': 'clicks <= impressions'},
                affected_rows=int(violations),
                affected_percentage=round(violations / len(df) * 100, 2)
            ))

        # Check that conversions <= clicks
        if all(col in df.columns for col in ['conversions', 'clicks']):
            violations = (df['conversions'] > df['clicks']).sum()

            report.add_check(QualityCheckResult(
                check_name='consistency_conversions_clicks',
                passed=violations == 0,
                severity='error',
                message=f"Conversions exceed clicks in {violations} rows",
                details={'rule': 'conversions <= clicks'},
                affected_rows=int(violations),
                affected_percentage=round(violations / len(df) * 100, 2)
            ))

        # Check CTR consistency
        if all(col in df.columns for col in ['clicks', 'impressions', 'ctr']):
            # Protect against division by zero
            calculated_ctr = np.where(
                df['impressions'] > 0,
                df['clicks'] / df['impressions'] * 100,
                0.0
            )
            tolerance = 0.5  # Allow 0.5% tolerance
            # Only check where impressions > 0
            valid_mask = df['impressions'] > 0
            inconsistent = np.zeros(len(df), dtype=bool)
            inconsistent[valid_mask] = abs(calculated_ctr[valid_mask] - df.loc[valid_mask, 'ctr']) > tolerance
            violations = inconsistent.sum()

            report.add_check(QualityCheckResult(
                check_name='consistency_ctr_calculation',
                passed=violations == 0,
                severity='warning',
                message=f"CTR inconsistent with clicks/impressions in {violations} rows",
                details={'rule': 'ctr = clicks/impressions * 100', 'tolerance': tolerance},
                affected_rows=int(violations),
                affected_percentage=round(violations / len(df) * 100, 2)
            ))

        # Check ROAS consistency
        if all(col in df.columns for col in ['revenue', 'budget', 'roas']):
            # Protect against division by zero
            calculated_roas = np.where(
                df['budget'] > 0,
                df['revenue'] / df['budget'],
                0.0
            )
            tolerance = 0.05  # Allow 5% tolerance
            # Only check where budget > 0
            valid_mask = df['budget'] > 0
            inconsistent = np.zeros(len(df), dtype=bool)
            inconsistent[valid_mask] = abs(calculated_roas[valid_mask] - df.loc[valid_mask, 'roas']) > tolerance
            violations = inconsistent.sum()

            report.add_check(QualityCheckResult(
                check_name='consistency_roas_calculation',
                passed=violations == 0,
                severity='warning',
                message=f"ROAS inconsistent with revenue/budget in {violations} rows",
                details={'rule': 'roas = revenue/budget', 'tolerance': tolerance},
                affected_rows=int(violations),
                affected_percentage=round(violations / len(df) * 100, 2)
            ))

    def _check_uniqueness(
        self, df: pd.DataFrame, report: DataQualityReport
    ) -> None:
        """Check for duplicate records and unique constraints."""
        # Check for complete duplicate rows
        duplicates = df.duplicated().sum()

        report.add_check(QualityCheckResult(
            check_name='uniqueness_duplicate_rows',
            passed=duplicates == 0,
            severity='warning',
            message=f"Found {duplicates} duplicate rows",
            details={'duplicate_count': int(duplicates)},
            affected_rows=int(duplicates),
            affected_percentage=round(duplicates / len(df) * 100, 2)
        ))

        # Check unique constraints from schema
        if self.schema:
            columns = self.schema.get('columns', {})

            for col_name, col_spec in columns.items():
                if col_name not in df.columns:
                    continue

                constraints = col_spec.get('constraints', {})

                if constraints.get('unique', False):
                    duplicates = df[col_name].duplicated().sum()

                    report.add_check(QualityCheckResult(
                        check_name=f'uniqueness_{col_name}',
                        passed=duplicates == 0,
                        severity='error',
                        message=f"Column '{col_name}' has {duplicates} duplicate values",
                        details={'column': col_name},
                        affected_rows=int(duplicates),
                        affected_percentage=round(duplicates / len(df) * 100, 2)
                    ))

    def _check_accuracy(
        self, df: pd.DataFrame, report: DataQualityReport
    ) -> None:
        """Check for statistical anomalies and outliers."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            if col in ['campaign_id'] or 'id' in col.lower():
                continue

            col_data = df[col].dropna()

            if len(col_data) < 3:
                continue

            # Calculate z-scores
            mean = col_data.mean()
            std = col_data.std()

            if std == 0:
                continue

            z_scores = np.abs((col_data - mean) / std)
            outliers = (z_scores > self.outlier_threshold).sum()

            report.add_check(QualityCheckResult(
                check_name=f'accuracy_outliers_{col}',
                passed=outliers / len(col_data) < 0.05,  # Allow up to 5% outliers
                severity='warning',
                message=f"Column '{col}' has {outliers} outliers (z-score > {self.outlier_threshold})",
                details={
                    'column': col,
                    'mean': round(mean, 2),
                    'std': round(std, 2),
                    'threshold': self.outlier_threshold
                },
                affected_rows=int(outliers),
                affected_percentage=round(outliers / len(df) * 100, 2)
            ))


class StatisticsGenerator:
    """
    Generates comprehensive summary statistics for datasets.

    This class provides:
    - Descriptive statistics for numeric columns
    - Frequency distributions for categorical columns
    - Distribution analysis
    - Percentile calculations

    Example:
        >>> stats_gen = StatisticsGenerator()
        >>> stats = stats_gen.generate(df)
        >>> print(stats['numeric_summary'])
    """

    def __init__(
        self,
        percentiles: List[float] = None,
        include_correlations: bool = True
    ):
        """
        Initialize the statistics generator.

        Args:
            percentiles: List of percentiles to calculate
            include_correlations: Whether to include correlation matrix
        """
        self.percentiles = percentiles or [0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
        self.include_correlations = include_correlations

    def generate(
        self,
        df: pd.DataFrame,
        target_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive statistics.

        Args:
            df: DataFrame to analyze
            target_column: Optional target column for additional analysis

        Returns:
            Dictionary with all statistics
        """
        logger.info("Generating summary statistics...")

        stats = {
            'overview': self._generate_overview(df),
            'numeric_summary': self._generate_numeric_summary(df),
            'categorical_summary': self._generate_categorical_summary(df),
            'missing_values': self._analyze_missing_values(df),
            'distributions': self._analyze_distributions(df)
        }

        if self.include_correlations:
            stats['correlations'] = self._generate_correlations(df)

        if target_column and target_column in df.columns:
            stats['target_analysis'] = self._analyze_target(df, target_column)

        logger.info("Statistics generation complete")

        return stats

    def _generate_overview(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate dataset overview."""
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
            'categorical_columns': len(df.select_dtypes(include=['object', 'category']).columns),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            'duplicate_rows': int(df.duplicated().sum()),
            'complete_rows': int((~df.isnull().any(axis=1)).sum())
        }

    def _generate_numeric_summary(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Generate summary statistics for numeric columns."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        summary = {}

        for col in numeric_cols:
            col_data = df[col].dropna()

            if len(col_data) == 0:
                continue

            summary[col] = {
                'count': int(len(col_data)),
                'mean': round(float(col_data.mean()), 4),
                'std': round(float(col_data.std()), 4),
                'min': round(float(col_data.min()), 4),
                'max': round(float(col_data.max()), 4),
                'median': round(float(col_data.median()), 4),
                'skewness': round(float(col_data.skew()), 4),
                'kurtosis': round(float(col_data.kurtosis()), 4),
                'percentiles': {
                    f'p{int(p*100)}': round(float(col_data.quantile(p)), 4)
                    for p in self.percentiles
                },
                'zeros': int((col_data == 0).sum()),
                'negatives': int((col_data < 0).sum())
            }

        return summary

    def _generate_categorical_summary(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Generate summary for categorical columns."""
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        summary = {}

        for col in cat_cols:
            value_counts = df[col].value_counts()

            summary[col] = {
                'count': int(df[col].notna().sum()),
                'unique_values': int(df[col].nunique()),
                'most_common': value_counts.index[0] if len(value_counts) > 0 else None,
                'most_common_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                'least_common': value_counts.index[-1] if len(value_counts) > 0 else None,
                'least_common_count': int(value_counts.iloc[-1]) if len(value_counts) > 0 else 0,
                'value_distribution': {
                    str(k): int(v) for k, v in value_counts.head(10).items()
                }
            }

        return summary

    def _analyze_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze missing values in detail."""
        missing_counts = df.isnull().sum()
        missing_pcts = (df.isnull().sum() / len(df) * 100).round(2)

        return {
            'total_missing_cells': int(df.isnull().sum().sum()),
            'total_cells': len(df) * len(df.columns),
            'missing_percentage': round(
                df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100, 2
            ),
            'columns_with_missing': {
                col: {
                    'count': int(missing_counts[col]),
                    'percentage': float(missing_pcts[col])
                }
                for col in df.columns if missing_counts[col] > 0
            },
            'rows_with_any_missing': int(df.isnull().any(axis=1).sum()),
            'complete_rows_percentage': round(
                (1 - df.isnull().any(axis=1).sum() / len(df)) * 100, 2
            )
        }

    def _analyze_distributions(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Analyze distributions of numeric columns."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        distributions = {}

        for col in numeric_cols:
            col_data = df[col].dropna()

            if len(col_data) < 8:  # Need enough data for distribution tests
                continue

            # Normality test (Shapiro-Wilk for small samples, D'Agostino for larger)
            try:
                if len(col_data) <= 5000:
                    # Use sample for large datasets
                    sample = col_data.sample(min(len(col_data), 5000), random_state=42)
                    stat, p_value = stats.shapiro(sample)
                    test_name = 'shapiro'
                else:
                    stat, p_value = stats.normaltest(col_data)
                    test_name = 'dagostino'

                is_normal = p_value > 0.05
            except Exception:
                stat, p_value = None, None
                is_normal = None
                test_name = None

            distributions[col] = {
                'normality_test': test_name,
                'normality_statistic': round(stat, 4) if stat else None,
                'normality_pvalue': round(p_value, 4) if p_value else None,
                'is_normal': is_normal,
                'skewness': round(float(col_data.skew()), 4),
                'skew_direction': 'right' if col_data.skew() > 0 else 'left',
                'is_skewed': abs(col_data.skew()) > 1.0
            }

        return distributions

    def _generate_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate correlation analysis."""
        numeric_df = df.select_dtypes(include=[np.number])

        if len(numeric_df.columns) < 2:
            return {}

        corr_matrix = numeric_df.corr()

        # Find high correlations
        high_corrs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    high_corrs.append({
                        'feature1': corr_matrix.columns[i],
                        'feature2': corr_matrix.columns[j],
                        'correlation': round(corr_val, 4)
                    })

        # Sort by absolute correlation
        high_corrs.sort(key=lambda x: abs(x['correlation']), reverse=True)

        return {
            'correlation_matrix': corr_matrix.round(4).to_dict(),
            'high_correlations': high_corrs[:10],
            'most_correlated_pairs': high_corrs[:5]
        }

    def _analyze_target(
        self, df: pd.DataFrame, target_column: str
    ) -> Dict[str, Any]:
        """Analyze target variable and its relationships."""
        target_data = df[target_column].dropna()

        analysis = {
            'column': target_column,
            'count': int(len(target_data)),
            'mean': round(float(target_data.mean()), 4),
            'std': round(float(target_data.std()), 4),
            'min': round(float(target_data.min()), 4),
            'max': round(float(target_data.max()), 4)
        }

        # Calculate correlations with target
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        correlations = {}

        for col in numeric_cols:
            if col != target_column:
                corr = df[col].corr(df[target_column])
                correlations[col] = round(corr, 4)

        # Sort by absolute correlation
        sorted_corrs = sorted(
            correlations.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )

        analysis['feature_correlations'] = dict(sorted_corrs)
        analysis['top_predictors'] = [c[0] for c in sorted_corrs[:5]]

        return analysis


class DataProfiler:
    """
    Creates comprehensive data profiles for campaign analytics data.

    This class combines quality checks, statistics, and visualizations
    to create a complete data profile report.

    Example:
        >>> profiler = DataProfiler(schema_path="data/schema.json")
        >>> profile = profiler.create_profile(df)
        >>> profiler.save_profile(profile, "reports/data_profile.json")
    """

    def __init__(
        self,
        schema_path: Optional[Union[str, Path]] = None
    ):
        """
        Initialize the data profiler.

        Args:
            schema_path: Optional path to JSON schema file
        """
        self.schema_path = schema_path
        self.quality_checker = DataQualityChecker(schema_path=schema_path)
        self.stats_generator = StatisticsGenerator()

    def create_profile(
        self,
        df: pd.DataFrame,
        name: str = "Campaign Analytics Data",
        target_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive data profile.

        Args:
            df: DataFrame to profile
            name: Name for the profile
            target_column: Optional target column for ML analysis

        Returns:
            Dictionary containing complete data profile
        """
        logger.info(f"Creating data profile for '{name}'...")

        profile = {
            'profile_name': name,
            'created_at': datetime.now().isoformat(),
            'data_shape': {
                'rows': len(df),
                'columns': len(df.columns)
            },
            'column_info': self._get_column_info(df),
            'quality_report': self.quality_checker.run_checks(df).to_dict(),
            'statistics': self.stats_generator.generate(df, target_column),
            'recommendations': self._generate_recommendations(df)
        }

        logger.info("Data profile creation complete")

        return profile

    def _get_column_info(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Get detailed information about each column."""
        column_info = []

        for col in df.columns:
            info = {
                'name': col,
                'dtype': str(df[col].dtype),
                'non_null_count': int(df[col].notna().sum()),
                'null_count': int(df[col].isnull().sum()),
                'null_percentage': round(df[col].isnull().sum() / len(df) * 100, 2),
                'unique_values': int(df[col].nunique())
            }

            # Add type-specific info
            if pd.api.types.is_numeric_dtype(df[col]):
                info['is_numeric'] = True
                info['min'] = float(df[col].min()) if df[col].notna().any() else None
                info['max'] = float(df[col].max()) if df[col].notna().any() else None
                info['mean'] = float(df[col].mean()) if df[col].notna().any() else None
            else:
                info['is_numeric'] = False
                info['sample_values'] = df[col].dropna().head(5).tolist()

            column_info.append(info)

        return column_info

    def _generate_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Generate data preparation recommendations."""
        recommendations = []

        # Check for missing values
        missing_cols = df.columns[df.isnull().any()].tolist()
        if missing_cols:
            recommendations.append(
                f"Handle missing values in columns: {missing_cols}"
            )

        # Check for high cardinality categorical columns
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in cat_cols:
            if df[col].nunique() > 50:
                recommendations.append(
                    f"Column '{col}' has high cardinality ({df[col].nunique()} unique values). "
                    "Consider grouping or encoding."
                )

        # Check for skewed distributions
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            skewness = df[col].skew()
            if abs(skewness) > 2:
                recommendations.append(
                    f"Column '{col}' is highly skewed (skewness: {skewness:.2f}). "
                    "Consider log transformation."
                )

        # Check data size
        if len(df) < 100:
            recommendations.append(
                f"Dataset has only {len(df)} rows. Consider collecting more data "
                "for robust model training."
            )

        if not recommendations:
            recommendations.append(
                "Data appears to be in good shape for modeling."
            )

        return recommendations

    def save_profile(
        self,
        profile: Dict[str, Any],
        filepath: Union[str, Path]
    ) -> None:
        """
        Save profile to JSON file.

        Args:
            profile: Profile dictionary to save
            filepath: Output file path
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(profile, f, indent=2, default=str)

        logger.info(f"Profile saved to {filepath}")

    def print_summary(self, profile: Dict[str, Any]) -> None:
        """Print a human-readable summary of the profile."""
        print("\n" + "=" * 60)
        print(f"DATA PROFILE: {profile['profile_name']}")
        print("=" * 60)

        print(f"\nCreated: {profile['created_at']}")
        print(f"Shape: {profile['data_shape']['rows']} rows x {profile['data_shape']['columns']} columns")

        # Quality summary
        quality = profile['quality_report']
        print(f"\nQuality Score: {quality['overall_score']}%")
        print(f"Checks: {quality['checks_passed']} passed, {quality['checks_failed']} failed, {quality['checks_warned']} warnings")

        # Statistics summary
        stats = profile['statistics']
        print(f"\nNumeric columns: {stats['overview']['numeric_columns']}")
        print(f"Categorical columns: {stats['overview']['categorical_columns']}")
        print(f"Memory usage: {stats['overview']['memory_usage_mb']} MB")

        # Recommendations
        print("\nRecommendations:")
        for rec in profile['recommendations']:
            print(f"  - {rec}")

        print("\n" + "=" * 60)


def run_data_quality_checks(
    file_path: Union[str, Path],
    schema_path: Optional[Union[str, Path]] = None
) -> DataQualityReport:
    """
    Convenience function to run quality checks on a CSV file.

    Args:
        file_path: Path to CSV file
        schema_path: Optional path to schema file

    Returns:
        DataQualityReport with all check results

    Example:
        >>> report = run_data_quality_checks("data/campaigns.csv", "data/schema.json")
        >>> print(f"Quality score: {report.overall_score}%")
    """
    df = pd.read_csv(file_path)
    checker = DataQualityChecker(schema_path=schema_path)
    return checker.run_checks(df)


def generate_data_profile(
    file_path: Union[str, Path],
    schema_path: Optional[Union[str, Path]] = None,
    output_path: Optional[Union[str, Path]] = None,
    target_column: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to generate a complete data profile.

    Args:
        file_path: Path to CSV file
        schema_path: Optional path to schema file
        output_path: Optional path to save profile JSON
        target_column: Optional target column for ML analysis

    Returns:
        Dictionary containing complete data profile

    Example:
        >>> profile = generate_data_profile(
        ...     "data/campaigns.csv",
        ...     schema_path="data/schema.json",
        ...     output_path="reports/profile.json",
        ...     target_column="roas"
        ... )
    """
    df = pd.read_csv(file_path)
    profiler = DataProfiler(schema_path=schema_path)

    profile = profiler.create_profile(
        df,
        name=Path(file_path).stem,
        target_column=target_column
    )

    if output_path:
        profiler.save_profile(profile, output_path)

    return profile


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    script_dir = Path(__file__).parent.parent
    data_path = script_dir / "data" / "sample_campaigns.csv"
    schema_path = script_dir / "data" / "schema.json"

    if data_path.exists():
        print("=== Data Quality Analysis ===\n")

        # Load data
        df = pd.read_csv(data_path)

        # Run quality checks
        checker = DataQualityChecker(
            schema_path=str(schema_path) if schema_path.exists() else None
        )
        report = checker.run_checks(df)

        print(f"Quality Score: {report.overall_score}%")
        print(f"Checks: {report.checks_passed} passed, {report.checks_failed} failed")

        print("\nFailed checks:")
        for check in report.check_results:
            if not check.passed and check.severity == 'error':
                print(f"  - {check.check_name}: {check.message}")

        print("\nWarnings:")
        for check in report.check_results:
            if not check.passed and check.severity == 'warning':
                print(f"  - {check.check_name}: {check.message}")

        # Generate statistics
        print("\n=== Summary Statistics ===\n")

        stats_gen = StatisticsGenerator()
        stats = stats_gen.generate(df, target_column='roas')

        print(f"Dataset overview:")
        for key, value in stats['overview'].items():
            print(f"  {key}: {value}")

        # Create full profile
        print("\n=== Full Data Profile ===\n")

        profiler = DataProfiler(
            schema_path=str(schema_path) if schema_path.exists() else None
        )
        profile = profiler.create_profile(df, target_column='roas')
        profiler.print_summary(profile)
    else:
        print(f"Sample data not found at {data_path}")
