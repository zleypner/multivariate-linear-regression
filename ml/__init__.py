"""
Campaign Analytics ML Module.

This module provides machine learning capabilities for campaign performance
prediction and analysis using multiple linear regression.

Main Components:
    - CampaignRegressionModel: Enhanced regression model with VIF analysis
    - MultivariateCampaignRegressor: Original regression model (legacy)
    - CampaignDataPreprocessor: Data preprocessing utilities
    - Utility functions for model serialization and results formatting

Data Engineering Components:
    - CSVDataLoader: Load and validate CSV data files
    - DataValidator: Validate data quality and schema compliance
    - DataTransformer: Transform data for ML consumption
    - FeatureEngineer: Create derived features
    - FeatureSelector: Select optimal features
    - CorrelationAnalyzer: Analyze feature correlations
    - DataQualityChecker: Run comprehensive quality checks
    - DataProfiler: Generate data profiles

Example Usage:
    >>> from ml import CampaignRegressionModel, train_campaign_model
    >>>
    >>> # Train a model
    >>> model = CampaignRegressionModel(target_variable='conversions')
    >>> model.fit(training_data)
    >>>
    >>> # Make predictions
    >>> predictions = model.predict(new_campaigns)
    >>>
    >>> # Or use convenience function
    >>> model, results = train_campaign_model('data/campaigns.csv')
    >>>
    >>> # Data engineering pipeline
    >>> from ml import run_pipeline, engineer_campaign_features
    >>> raw_df, validation, transformed_df = run_pipeline(
    ...     "data/campaigns.csv", "data/schema.json"
    ... )
    >>> df_features, engineer = engineer_campaign_features(transformed_df)
"""

# New enhanced model
from .model import (
    CampaignRegressionModel,
    train_campaign_model
)

# Legacy support
from .regression import MultivariateCampaignRegressor
from .preprocessor import CampaignDataPreprocessor as LegacyPreprocessor

# Enhanced preprocessing
from .preprocessing import (
    CampaignDataPreprocessor,
    handle_missing_values,
    create_train_test_split,
    detect_missing_patterns,
    encode_categorical_features,
    scale_numeric_features
)

# Utilities
from .utils import (
    save_model,
    load_model,
    get_model,
    format_metrics,
    format_feature_importance,
    format_prediction_results,
    validate_dataframe,
    validate_model_input,
    create_model_summary,
    results_to_json,
    calculate_percentage_change
)

# Data Engineering Pipeline
from .pipeline import (
    CSVDataLoader,
    DataValidator,
    DataTransformer,
    ValidationResult,
    create_pipeline,
    run_pipeline
)

# Feature Engineering
from .feature_engineering import (
    FeatureEngineer,
    FeatureSelector,
    CorrelationAnalyzer,
    FeatureDefinition,
    CorrelationReport,
    engineer_campaign_features,
    select_best_features
)

# Data Quality
from .data_quality import (
    DataQualityChecker,
    StatisticsGenerator,
    DataProfiler,
    DataQualityReport,
    QualityCheckResult,
    run_data_quality_checks,
    generate_data_profile
)

__version__ = '1.0.0'
__author__ = 'Campaign Analytics Team'

__all__ = [
    # Main model class (enhanced)
    'CampaignRegressionModel',
    'train_campaign_model',

    # Legacy model
    'MultivariateCampaignRegressor',
    'LegacyPreprocessor',

    # Preprocessing
    'CampaignDataPreprocessor',
    'handle_missing_values',
    'create_train_test_split',
    'detect_missing_patterns',
    'encode_categorical_features',
    'scale_numeric_features',

    # Utilities
    'save_model',
    'load_model',
    'get_model',
    'format_metrics',
    'format_feature_importance',
    'format_prediction_results',
    'validate_dataframe',
    'validate_model_input',
    'create_model_summary',
    'results_to_json',
    'calculate_percentage_change',

    # Data Engineering Pipeline
    'CSVDataLoader',
    'DataValidator',
    'DataTransformer',
    'ValidationResult',
    'create_pipeline',
    'run_pipeline',

    # Feature Engineering
    'FeatureEngineer',
    'FeatureSelector',
    'CorrelationAnalyzer',
    'FeatureDefinition',
    'CorrelationReport',
    'engineer_campaign_features',
    'select_best_features',

    # Data Quality
    'DataQualityChecker',
    'StatisticsGenerator',
    'DataProfiler',
    'DataQualityReport',
    'QualityCheckResult',
    'run_data_quality_checks',
    'generate_data_profile'
]
