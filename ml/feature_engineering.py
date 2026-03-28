"""
Feature Engineering Module for Campaign Analytics System.

This module provides utilities for creating derived features, feature selection,
and correlation analysis for campaign analytics machine learning models.

Classes:
    FeatureEngineer: Creates derived features from raw campaign data
    FeatureSelector: Selects optimal features based on various criteria
    CorrelationAnalyzer: Analyzes feature correlations and multicollinearity
"""

import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from scipy import stats
from collections import OrderedDict

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
class FeatureDefinition:
    """Definition of a derived feature."""
    name: str
    formula: str
    description: str
    dependencies: List[str]
    transform_func: callable = None


@dataclass
class CorrelationReport:
    """Container for correlation analysis results."""
    correlation_matrix: pd.DataFrame = None
    high_correlations: List[Tuple[str, str, float]] = field(default_factory=list)
    vif_scores: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class FeatureEngineer:
    """
    Creates derived features from raw campaign data.

    This class generates calculated metrics and features that are useful
    for predictive modeling of campaign performance.

    Features created:
    - cost_per_impression: budget / impressions
    - conversion_rate: conversions / clicks
    - efficiency_score: conversions / budget * 1000
    - engagement_rate: clicks / impressions
    - revenue_per_conversion: revenue / conversions
    - cost_efficiency_ratio: revenue / budget (same as ROAS)
    - click_value: revenue / clicks

    Example:
        >>> engineer = FeatureEngineer()
        >>> df_features = engineer.create_features(df)
        >>> print(engineer.get_feature_names())
    """

    # Feature definitions with formulas and dependencies
    FEATURE_DEFINITIONS = OrderedDict([
        ('cost_per_impression', FeatureDefinition(
            name='cost_per_impression',
            formula='budget / impressions',
            description='Cost per single impression (CPM basis)',
            dependencies=['budget', 'impressions']
        )),
        ('conversion_rate', FeatureDefinition(
            name='conversion_rate',
            formula='conversions / clicks',
            description='Percentage of clicks that convert',
            dependencies=['conversions', 'clicks']
        )),
        ('efficiency_score', FeatureDefinition(
            name='efficiency_score',
            formula='conversions / budget * 1000',
            description='Conversions per $1000 spent',
            dependencies=['conversions', 'budget']
        )),
        ('engagement_rate', FeatureDefinition(
            name='engagement_rate',
            formula='clicks / impressions',
            description='Click-through rate as decimal',
            dependencies=['clicks', 'impressions']
        )),
        ('revenue_per_conversion', FeatureDefinition(
            name='revenue_per_conversion',
            formula='revenue / conversions',
            description='Average revenue per conversion',
            dependencies=['revenue', 'conversions']
        )),
        ('click_value', FeatureDefinition(
            name='click_value',
            formula='revenue / clicks',
            description='Average revenue per click',
            dependencies=['revenue', 'clicks']
        )),
        ('impression_efficiency', FeatureDefinition(
            name='impression_efficiency',
            formula='conversions / impressions * 1000',
            description='Conversions per 1000 impressions',
            dependencies=['conversions', 'impressions']
        )),
        ('budget_utilization', FeatureDefinition(
            name='budget_utilization',
            formula='(clicks * cpc) / budget',
            description='How much of budget was spent on clicks',
            dependencies=['clicks', 'cpc', 'budget']
        )),
        ('profit_margin', FeatureDefinition(
            name='profit_margin',
            formula='(revenue - budget) / revenue',
            description='Profit as percentage of revenue',
            dependencies=['revenue', 'budget']
        ))
    ])

    def __init__(
        self,
        include_log_features: bool = True,
        include_interaction_features: bool = False,
        custom_features: Optional[List[FeatureDefinition]] = None
    ):
        """
        Initialize the feature engineer.

        Args:
            include_log_features: Whether to create log-transformed features
            include_interaction_features: Whether to create interaction features
            custom_features: Optional list of custom feature definitions
        """
        self.include_log_features = include_log_features
        self.include_interaction_features = include_interaction_features
        self.custom_features = custom_features or []

        self._created_features: List[str] = []
        self._feature_metadata: Dict[str, Dict] = {}

    def create_features(
        self,
        df: pd.DataFrame,
        target_column: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Create all derived features.

        Args:
            df: Input DataFrame with raw features
            target_column: Optional target column to exclude from transformations

        Returns:
            DataFrame with original and derived features
        """
        logger.info("Starting feature engineering...")
        df_result = df.copy()
        self._created_features = []
        self._feature_metadata = {}

        # Create standard derived features
        for feature_name, feature_def in self.FEATURE_DEFINITIONS.items():
            df_result = self._create_single_feature(
                df_result, feature_def
            )

        # Create custom features
        for custom_feature in self.custom_features:
            df_result = self._create_single_feature(
                df_result, custom_feature
            )

        # Create log-transformed features
        if self.include_log_features:
            df_result = self._create_log_features(df_result, target_column)

        # Create interaction features
        if self.include_interaction_features:
            df_result = self._create_interaction_features(
                df_result, target_column
            )

        logger.info(
            f"Feature engineering complete. Created {len(self._created_features)} "
            f"new features"
        )

        return df_result

    def _create_single_feature(
        self,
        df: pd.DataFrame,
        feature_def: FeatureDefinition
    ) -> pd.DataFrame:
        """Create a single derived feature."""
        # Check if dependencies are available
        missing_deps = [
            dep for dep in feature_def.dependencies
            if dep not in df.columns
        ]

        if missing_deps:
            logger.debug(
                f"Skipping feature '{feature_def.name}': "
                f"missing dependencies {missing_deps}"
            )
            return df

        try:
            # Use custom transform function if provided
            if feature_def.transform_func:
                df[feature_def.name] = feature_def.transform_func(df)
            else:
                # Create feature based on formula pattern
                df = self._apply_formula(df, feature_def)

            self._created_features.append(feature_def.name)
            self._feature_metadata[feature_def.name] = {
                'formula': feature_def.formula,
                'description': feature_def.description,
                'dependencies': feature_def.dependencies
            }

            logger.debug(f"Created feature: {feature_def.name}")

        except Exception as e:
            logger.warning(
                f"Failed to create feature '{feature_def.name}': {e}"
            )

        return df

    def _apply_formula(
        self,
        df: pd.DataFrame,
        feature_def: FeatureDefinition
    ) -> pd.DataFrame:
        """Apply formula to create feature."""
        name = feature_def.name
        deps = feature_def.dependencies

        # Handle division-based formulas with zero protection
        if name == 'cost_per_impression':
            df[name] = np.where(
                df['impressions'] > 0,
                df['budget'] / df['impressions'],
                0
            )
        elif name == 'conversion_rate':
            df[name] = np.where(
                df['clicks'] > 0,
                df['conversions'] / df['clicks'],
                0
            )
        elif name == 'efficiency_score':
            df[name] = np.where(
                df['budget'] > 0,
                df['conversions'] / df['budget'] * 1000,
                0
            )
        elif name == 'engagement_rate':
            df[name] = np.where(
                df['impressions'] > 0,
                df['clicks'] / df['impressions'],
                0
            )
        elif name == 'revenue_per_conversion':
            df[name] = np.where(
                df['conversions'] > 0,
                df['revenue'] / df['conversions'],
                0
            )
        elif name == 'click_value':
            df[name] = np.where(
                df['clicks'] > 0,
                df['revenue'] / df['clicks'],
                0
            )
        elif name == 'impression_efficiency':
            df[name] = np.where(
                df['impressions'] > 0,
                df['conversions'] / df['impressions'] * 1000,
                0
            )
        elif name == 'budget_utilization':
            df[name] = np.where(
                df['budget'] > 0,
                (df['clicks'] * df['cpc']) / df['budget'],
                0
            )
        elif name == 'profit_margin':
            df[name] = np.where(
                df['revenue'] > 0,
                (df['revenue'] - df['budget']) / df['revenue'],
                0
            )
        else:
            # Generic formula evaluation (use with caution)
            logger.warning(
                f"Unknown formula for '{name}', skipping"
            )

        return df

    def _create_log_features(
        self,
        df: pd.DataFrame,
        target_column: Optional[str] = None
    ) -> pd.DataFrame:
        """Create log-transformed features for skewed numeric columns."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        # Columns that typically benefit from log transformation
        log_candidates = [
            'budget', 'impressions', 'clicks', 'conversions',
            'revenue', 'cost_per_impression'
        ]

        for col in log_candidates:
            if col not in df.columns:
                continue
            if col == target_column:
                continue

            # Check if all values are positive
            if (df[col] > 0).all():
                log_col_name = f"{col}_log"
                df[log_col_name] = np.log1p(df[col])
                self._created_features.append(log_col_name)
                self._feature_metadata[log_col_name] = {
                    'formula': f'log1p({col})',
                    'description': f'Log-transformed {col}',
                    'dependencies': [col]
                }

        return df

    def _create_interaction_features(
        self,
        df: pd.DataFrame,
        target_column: Optional[str] = None
    ) -> pd.DataFrame:
        """Create interaction features between key numeric columns."""
        # Define interaction pairs
        interaction_pairs = [
            ('budget', 'ctr'),
            ('impressions', 'conversion_rate'),
            ('clicks', 'cpc')
        ]

        for col1, col2 in interaction_pairs:
            if col1 not in df.columns or col2 not in df.columns:
                continue

            interaction_name = f"{col1}_x_{col2}"
            df[interaction_name] = df[col1] * df[col2]
            self._created_features.append(interaction_name)
            self._feature_metadata[interaction_name] = {
                'formula': f'{col1} * {col2}',
                'description': f'Interaction between {col1} and {col2}',
                'dependencies': [col1, col2]
            }

        return df

    def get_feature_names(self) -> List[str]:
        """Get list of created feature names."""
        return self._created_features.copy()

    def get_feature_metadata(self) -> Dict[str, Dict]:
        """Get metadata for all created features."""
        return self._feature_metadata.copy()

    def get_feature_info(self, feature_name: str) -> Optional[Dict]:
        """Get information about a specific feature."""
        return self._feature_metadata.get(feature_name)


class FeatureSelector:
    """
    Selects optimal features based on various criteria.

    This class provides methods for selecting features based on:
    - Correlation with target variable
    - Variance threshold
    - Mutual information
    - Feature importance from models

    Example:
        >>> selector = FeatureSelector()
        >>> selected_features = selector.select_by_correlation(
        ...     df, target='roas', threshold=0.1
        ... )
    """

    def __init__(
        self,
        correlation_threshold: float = 0.1,
        variance_threshold: float = 0.01,
        multicollinearity_threshold: float = 0.95
    ):
        """
        Initialize the feature selector.

        Args:
            correlation_threshold: Minimum correlation with target
            variance_threshold: Minimum variance for feature selection
            multicollinearity_threshold: Maximum inter-feature correlation
        """
        self.correlation_threshold = correlation_threshold
        self.variance_threshold = variance_threshold
        self.multicollinearity_threshold = multicollinearity_threshold

        self._selected_features: List[str] = []
        self._selection_scores: Dict[str, float] = {}

    def select_by_correlation(
        self,
        df: pd.DataFrame,
        target: str,
        threshold: Optional[float] = None
    ) -> List[str]:
        """
        Select features based on correlation with target.

        Args:
            df: DataFrame with features
            target: Name of target column
            threshold: Optional override for correlation threshold

        Returns:
            List of selected feature names
        """
        threshold = threshold or self.correlation_threshold

        if target not in df.columns:
            raise ValueError(f"Target column '{target}' not found")

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        numeric_cols = [c for c in numeric_cols if c != target]

        selected = []
        self._selection_scores = {}

        for col in numeric_cols:
            correlation = abs(df[col].corr(df[target]))
            self._selection_scores[col] = correlation

            if correlation >= threshold:
                selected.append(col)

        # Sort by correlation strength
        selected.sort(key=lambda x: self._selection_scores[x], reverse=True)
        self._selected_features = selected

        logger.info(
            f"Selected {len(selected)}/{len(numeric_cols)} features "
            f"with correlation >= {threshold}"
        )

        return selected

    def select_by_variance(
        self,
        df: pd.DataFrame,
        threshold: Optional[float] = None
    ) -> List[str]:
        """
        Select features based on variance threshold.

        Args:
            df: DataFrame with features
            threshold: Optional override for variance threshold

        Returns:
            List of selected feature names
        """
        threshold = threshold or self.variance_threshold

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        selected = []
        self._selection_scores = {}

        for col in numeric_cols:
            # Normalize variance by mean to get coefficient of variation
            variance = df[col].var()
            mean = df[col].mean()

            if mean != 0:
                cv = variance / (mean ** 2)  # Squared CV
            else:
                cv = variance

            self._selection_scores[col] = cv

            if cv >= threshold:
                selected.append(col)

        self._selected_features = selected

        logger.info(
            f"Selected {len(selected)}/{len(numeric_cols)} features "
            f"with variance >= {threshold}"
        )

        return selected

    def remove_multicollinear(
        self,
        df: pd.DataFrame,
        features: Optional[List[str]] = None,
        threshold: Optional[float] = None
    ) -> List[str]:
        """
        Remove highly correlated features to reduce multicollinearity.

        Args:
            df: DataFrame with features
            features: Optional list of features to consider
            threshold: Optional override for correlation threshold

        Returns:
            List of features with multicollinearity removed
        """
        threshold = threshold or self.multicollinearity_threshold

        if features is None:
            features = df.select_dtypes(include=[np.number]).columns.tolist()

        # Calculate correlation matrix
        corr_matrix = df[features].corr().abs()

        # Find pairs with high correlation
        to_remove = set()

        for i in range(len(features)):
            for j in range(i + 1, len(features)):
                if corr_matrix.iloc[i, j] >= threshold:
                    # Remove the feature with lower variance
                    var_i = df[features[i]].var()
                    var_j = df[features[j]].var()

                    if var_i < var_j:
                        to_remove.add(features[i])
                    else:
                        to_remove.add(features[j])

                    logger.debug(
                        f"High correlation ({corr_matrix.iloc[i, j]:.3f}) "
                        f"between '{features[i]}' and '{features[j]}'"
                    )

        selected = [f for f in features if f not in to_remove]
        self._selected_features = selected

        logger.info(
            f"Removed {len(to_remove)} multicollinear features, "
            f"{len(selected)} remaining"
        )

        return selected

    def get_feature_rankings(self) -> List[Tuple[str, float]]:
        """
        Get ranked list of features by selection score.

        Returns:
            List of (feature_name, score) tuples sorted by score
        """
        return sorted(
            self._selection_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

    def get_selected_features(self) -> List[str]:
        """Get list of selected features."""
        return self._selected_features.copy()


class CorrelationAnalyzer:
    """
    Analyzes feature correlations and multicollinearity.

    This class provides comprehensive correlation analysis including:
    - Correlation matrix computation
    - High correlation pair detection
    - Variance Inflation Factor (VIF) calculation
    - Multicollinearity diagnostics

    Example:
        >>> analyzer = CorrelationAnalyzer()
        >>> report = analyzer.analyze(df, target='roas')
        >>> print(report.recommendations)
    """

    def __init__(
        self,
        high_correlation_threshold: float = 0.8,
        vif_threshold: float = 10.0
    ):
        """
        Initialize the correlation analyzer.

        Args:
            high_correlation_threshold: Threshold for flagging high correlations
            vif_threshold: Threshold for VIF-based multicollinearity
        """
        self.high_correlation_threshold = high_correlation_threshold
        self.vif_threshold = vif_threshold

    def analyze(
        self,
        df: pd.DataFrame,
        target: Optional[str] = None,
        features: Optional[List[str]] = None
    ) -> CorrelationReport:
        """
        Perform comprehensive correlation analysis.

        Args:
            df: DataFrame with features
            target: Optional target column for target correlations
            features: Optional list of features to analyze

        Returns:
            CorrelationReport with analysis results
        """
        logger.info("Starting correlation analysis...")

        report = CorrelationReport()

        if features is None:
            features = df.select_dtypes(include=[np.number]).columns.tolist()

        # Compute correlation matrix
        report.correlation_matrix = df[features].corr()

        # Find high correlation pairs
        report.high_correlations = self._find_high_correlations(
            report.correlation_matrix
        )

        # Calculate VIF scores
        report.vif_scores = self._calculate_vif(df, features)

        # Generate recommendations
        report.recommendations = self._generate_recommendations(report, target)

        logger.info(
            f"Correlation analysis complete. Found "
            f"{len(report.high_correlations)} high correlation pairs"
        )

        return report

    def _find_high_correlations(
        self,
        corr_matrix: pd.DataFrame
    ) -> List[Tuple[str, str, float]]:
        """Find pairs of features with high correlation."""
        high_corr = []

        features = corr_matrix.columns.tolist()

        for i in range(len(features)):
            for j in range(i + 1, len(features)):
                corr_value = abs(corr_matrix.iloc[i, j])

                if corr_value >= self.high_correlation_threshold:
                    high_corr.append((
                        features[i],
                        features[j],
                        round(corr_matrix.iloc[i, j], 4)
                    ))

        # Sort by absolute correlation
        high_corr.sort(key=lambda x: abs(x[2]), reverse=True)

        return high_corr

    def _calculate_vif(
        self,
        df: pd.DataFrame,
        features: List[str]
    ) -> Dict[str, float]:
        """Calculate Variance Inflation Factor for each feature."""
        vif_scores = {}

        # Need at least 2 features for VIF
        if len(features) < 2:
            return vif_scores

        df_subset = df[features].dropna()

        if len(df_subset) < len(features) + 1:
            logger.warning("Not enough samples to calculate VIF")
            return vif_scores

        for i, feature in enumerate(features):
            try:
                # Get other features as predictors
                other_features = [f for f in features if f != feature]

                if not other_features:
                    continue

                X = df_subset[other_features].values
                y = df_subset[feature].values

                # Add constant term
                X = np.column_stack([np.ones(len(X)), X])

                # Calculate R-squared
                try:
                    coeffs, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
                    y_pred = X @ coeffs
                    ss_res = np.sum((y - y_pred) ** 2)
                    ss_tot = np.sum((y - np.mean(y)) ** 2)

                    if ss_tot > 0:
                        r_squared = 1 - (ss_res / ss_tot)
                        r_squared = max(0, min(r_squared, 0.9999))  # Clip to avoid division by zero
                        vif = 1 / (1 - r_squared)
                        vif_scores[feature] = round(vif, 2)
                except np.linalg.LinAlgError:
                    vif_scores[feature] = np.inf

            except Exception as e:
                logger.warning(f"VIF calculation failed for '{feature}': {e}")

        return vif_scores

    def _generate_recommendations(
        self,
        report: CorrelationReport,
        target: Optional[str] = None
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # High correlation recommendations
        if report.high_correlations:
            recommendations.append(
                f"Found {len(report.high_correlations)} highly correlated "
                f"feature pairs (>= {self.high_correlation_threshold}). "
                "Consider removing redundant features."
            )

            # Specific recommendations for top pairs
            for feat1, feat2, corr in report.high_correlations[:3]:
                recommendations.append(
                    f"  - Consider removing either '{feat1}' or '{feat2}' "
                    f"(correlation: {corr:.3f})"
                )

        # VIF recommendations
        high_vif_features = [
            f for f, v in report.vif_scores.items()
            if v > self.vif_threshold
        ]

        if high_vif_features:
            recommendations.append(
                f"Features with high VIF (> {self.vif_threshold}): "
                f"{high_vif_features}. These may cause multicollinearity issues."
            )

        # Target correlation recommendations
        if target and report.correlation_matrix is not None:
            if target in report.correlation_matrix.columns:
                target_corrs = report.correlation_matrix[target].drop(target)
                low_corr_features = target_corrs[abs(target_corrs) < 0.1].index.tolist()

                if low_corr_features:
                    recommendations.append(
                        f"Features with low correlation to target '{target}': "
                        f"{low_corr_features[:5]}. Consider removing if not important."
                    )

        if not recommendations:
            recommendations.append(
                "No significant correlation issues detected."
            )

        return recommendations

    def get_target_correlations(
        self,
        df: pd.DataFrame,
        target: str,
        features: Optional[List[str]] = None
    ) -> pd.Series:
        """
        Get correlations of all features with target variable.

        Args:
            df: DataFrame with features
            target: Target column name
            features: Optional list of features to include

        Returns:
            Series of correlations sorted by absolute value
        """
        if target not in df.columns:
            raise ValueError(f"Target column '{target}' not found")

        if features is None:
            features = df.select_dtypes(include=[np.number]).columns.tolist()
            features = [f for f in features if f != target]

        correlations = {}
        for feature in features:
            correlations[feature] = df[feature].corr(df[target])

        corr_series = pd.Series(correlations)
        corr_series = corr_series.reindex(
            corr_series.abs().sort_values(ascending=False).index
        )

        return corr_series

    def plot_correlation_matrix(
        self,
        corr_matrix: pd.DataFrame,
        figsize: Tuple[int, int] = (12, 10)
    ) -> None:
        """
        Plot correlation matrix as heatmap.

        Args:
            corr_matrix: Correlation matrix DataFrame
            figsize: Figure size tuple

        Note:
            Requires matplotlib and seaborn for visualization.
        """
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns

            plt.figure(figsize=figsize)
            sns.heatmap(
                corr_matrix,
                annot=True,
                fmt='.2f',
                cmap='coolwarm',
                center=0,
                square=True,
                linewidths=0.5
            )
            plt.title('Feature Correlation Matrix')
            plt.tight_layout()
            plt.show()

        except ImportError:
            logger.warning(
                "matplotlib and seaborn required for plotting. "
                "Install with: pip install matplotlib seaborn"
            )


def engineer_campaign_features(
    df: pd.DataFrame,
    target: Optional[str] = None,
    include_log: bool = True,
    include_interactions: bool = False
) -> Tuple[pd.DataFrame, FeatureEngineer]:
    """
    Convenience function to engineer all campaign features.

    Args:
        df: Raw campaign DataFrame
        target: Optional target column
        include_log: Include log-transformed features
        include_interactions: Include interaction features

    Returns:
        Tuple of (engineered DataFrame, FeatureEngineer instance)

    Example:
        >>> df_features, engineer = engineer_campaign_features(
        ...     df, target='roas'
        ... )
        >>> print(engineer.get_feature_names())
    """
    engineer = FeatureEngineer(
        include_log_features=include_log,
        include_interaction_features=include_interactions
    )

    df_result = engineer.create_features(df, target_column=target)

    return df_result, engineer


def select_best_features(
    df: pd.DataFrame,
    target: str,
    max_features: int = 10,
    correlation_threshold: float = 0.1
) -> List[str]:
    """
    Convenience function to select best features for modeling.

    Args:
        df: DataFrame with features
        target: Target column name
        max_features: Maximum number of features to select
        correlation_threshold: Minimum correlation with target

    Returns:
        List of selected feature names

    Example:
        >>> features = select_best_features(df, 'roas', max_features=8)
    """
    selector = FeatureSelector(correlation_threshold=correlation_threshold)

    # Select by correlation
    correlated_features = selector.select_by_correlation(df, target)

    # Remove multicollinear features
    selected = selector.remove_multicollinear(df, correlated_features)

    # Limit to max features
    return selected[:max_features]


if __name__ == "__main__":
    # Example usage
    from pathlib import Path

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Load sample data
    script_dir = Path(__file__).parent.parent
    data_path = script_dir / "data" / "sample_campaigns.csv"

    if data_path.exists():
        df = pd.read_csv(data_path)

        print("=== Feature Engineering Demo ===\n")

        # Engineer features
        df_features, engineer = engineer_campaign_features(df, target='roas')

        print(f"Original columns: {len(df.columns)}")
        print(f"After engineering: {len(df_features.columns)}")
        print(f"\nNew features created:")
        for feature in engineer.get_feature_names():
            print(f"  - {feature}")

        # Analyze correlations
        print("\n=== Correlation Analysis ===\n")

        analyzer = CorrelationAnalyzer()
        report = analyzer.analyze(df_features, target='roas')

        print("High correlation pairs:")
        for f1, f2, corr in report.high_correlations[:5]:
            print(f"  {f1} <-> {f2}: {corr:.3f}")

        print("\nRecommendations:")
        for rec in report.recommendations:
            print(f"  {rec}")

        # Select best features
        print("\n=== Feature Selection ===\n")

        best_features = select_best_features(df_features, 'roas')
        print(f"Selected features: {best_features}")
    else:
        print(f"Sample data not found at {data_path}")
