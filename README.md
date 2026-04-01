# Campaign Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=flat&logo=next.js&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A full-stack machine learning platform for marketing campaign performance analysis. Upload campaign data, train predictive regression models, detect multicollinearity issues, and forecast conversions with confidence intervals.

## Overview

This platform enables marketing teams and data analysts to:

- **Predict Campaign Performance** - Estimate conversions before launching campaigns
- **Identify Key Drivers** - Understand which features impact performance most
- **Detect Data Issues** - Automatic multicollinearity detection via VIF analysis
- **Make Data-Driven Decisions** - Cross-validated metrics ensure reliable predictions

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js 14)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │  Upload  │  │  Train   │  │ Predict  │  │     Results      │    │
│  │   Page   │  │   Page   │  │   Page   │  │    Dashboard     │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘    │
└───────┼─────────────┼─────────────┼─────────────────┼───────────────┘
        │             │             │                 │
        ▼             ▼             ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       REST API (FastAPI)                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │ /upload  │  │  /train  │  │ /predict │  │    /results      │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘    │
└───────┼─────────────┼─────────────┼─────────────────┼───────────────┘
        │             │             │                 │
        ▼             ▼             ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     ML Engine (scikit-learn)                        │
│  ┌────────────────┐  ┌─────────────────┐  ┌────────────────────┐   │
│  │ Preprocessing  │  │ Linear Regressor│  │  VIF Analysis      │   │
│  │ & Encoding     │  │ + Cross-Val     │  │  & Diagnostics     │   │
│  └────────────────┘  └─────────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Features

| Feature | Description |
|---------|-------------|
| **CSV Upload** | Drag-and-drop interface with schema validation and data preview |
| **Data Quality Checks** | Automatic outlier detection, missing value handling, type inference |
| **Model Training** | Multivariate linear regression with k-fold cross-validation |
| **VIF Analysis** | Variance Inflation Factor calculation to detect multicollinearity |
| **Predictions** | Single and batch predictions with 95% confidence intervals |
| **Visualizations** | Feature importance charts, residual plots, actual vs predicted |

## Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.109+ | REST API framework |
| Pydantic | 2.5+ | Data validation & serialization |
| scikit-learn | 1.4+ | Machine learning models |
| Pandas | 2.1+ | Data manipulation |
| NumPy | 1.26+ | Numerical computing |
| Statsmodels | - | VIF calculation |
| Uvicorn | 0.27+ | ASGI server |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14.2 | React framework (App Router) |
| React | 18.3 | UI library |
| TypeScript | 5.4 | Type safety |
| Tailwind CSS | 3.4 | Styling |
| Recharts | 2.12 | Data visualization |
| React Dropzone | 14.2 | File upload handling |

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/zleypner/multivariate-linear-regression.git
cd multivariate-linear-regression
```

**2. Set up the backend**

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r ml/requirements.txt
```

**3. Set up the frontend**

```bash
cd frontend
npm install
```

### Running the Application

**Start the backend** (from project root):
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Start the frontend** (in a new terminal):
```bash
cd frontend
npm run dev
```

Access the application:
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Usage Guide

### 1. Upload Campaign Data

Navigate to `/upload` and upload a CSV file with the following schema:

| Column | Type | Description |
|--------|------|-------------|
| `campaign_id` | string | Unique identifier |
| `budget` | number | Campaign budget ($) |
| `audience_type` | enum | `lookalike`, `interest`, `retargeting`, `broad` |
| `creative_type` | enum | `video`, `image`, `carousel` |
| `channel` | enum | `facebook`, `instagram`, `tiktok`, `google`, `youtube` |
| `impressions` | number | Total ad impressions |
| `clicks` | number | Total clicks |
| `ctr` | number | Click-through rate (%) |
| `cpc` | number | Cost per click ($) |
| `conversions` | number | Number of conversions (target) |
| `cpl` | number | Cost per lead ($) |
| `revenue` | number | Total revenue ($) |
| `roas` | number | Return on ad spend |

A sample dataset is available at `data/sample_campaigns.csv`.

### 2. Train the Model

Navigate to `/train`:
1. Select target variable (default: `conversions`)
2. Choose features to include
3. Configure cross-validation folds (default: 5)
4. Click **Train Model**

### 3. Make Predictions

Navigate to `/predict`:
- **Single Prediction**: Enter campaign parameters manually
- **Batch Prediction**: Upload a CSV file for bulk predictions

### 4. Analyze Results

Navigate to `/results` to view:
- Model performance metrics (R², RMSE, MAE)
- Cross-validation scores
- Feature importance ranking
- Actual vs Predicted scatter plot
- Residual distribution analysis
- VIF multicollinearity report

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/upload` | Upload CSV file |
| `GET` | `/api/files` | List uploaded files |
| `DELETE` | `/api/files/{id}` | Delete a file |
| `POST` | `/api/train` | Train regression model |
| `GET` | `/api/train/runs` | List training runs |
| `POST` | `/api/predict` | Batch predictions |
| `POST` | `/api/predict/single` | Single prediction |
| `GET` | `/api/results` | Get latest results |
| `GET` | `/api/results/coefficients` | Model coefficients |
| `GET` | `/api/results/feature-importance` | Feature importance |
| `GET` | `/api/results/vif` | VIF multicollinearity report |

### Example: Single Prediction

```bash
curl -X POST http://localhost:8000/api/predict/single \
  -H "Content-Type: application/json" \
  -d '{
    "budget": 5000,
    "impressions": 150000,
    "clicks": 4500,
    "ctr": 3.0,
    "cpc": 1.11,
    "audience_type": "lookalike",
    "creative_type": "video",
    "channel": "facebook"
  }'
```

**Response:**
```json
{
  "prediction": 127.5,
  "confidence_interval": {
    "lower": 98.2,
    "upper": 156.8
  }
}
```

## Project Structure

```
multivariate-linear-regression/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── config.py          # Configuration settings
│   │   ├── middleware/        # Error handling, CORS
│   │   ├── models/            # Pydantic schemas
│   │   ├── routes/            # API endpoint handlers
│   │   └── services/          # Business logic layer
│   └── requirements.txt
│
├── frontend/                   # Next.js application
│   ├── src/
│   │   ├── app/               # Pages (App Router)
│   │   ├── components/        # Reusable UI components
│   │   ├── context/           # React context providers
│   │   └── lib/               # API client, utilities
│   ├── package.json
│   └── tailwind.config.ts
│
├── ml/                         # Machine learning module
│   ├── model.py               # CampaignRegressionModel class
│   ├── preprocessing.py       # Data preprocessor
│   ├── feature_engineering.py # Feature transformations
│   ├── data_quality.py        # Validation utilities
│   └── utils.py               # Helper functions
│
├── data/                       # Sample datasets
│   ├── sample_campaigns.csv
│   └── schema.json
│
└── docs/                       # Documentation
    └── implementation-tracker.md
```

## Configuration

### Environment Variables

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

**Backend** (environment or `backend/app/config.py`):

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | Campaign Analytics API | Application name |
| `DEBUG` | false | Enable debug mode |
| `CORS_ORIGINS` | ["http://localhost:3000"] | Allowed CORS origins |
| `MAX_UPLOAD_SIZE` | 10485760 | Max upload size (10MB) |

## Model Details

The platform uses **Ordinary Least Squares (OLS) Linear Regression** with the following characteristics:

- **Feature Encoding**: One-hot encoding for categorical variables
- **Feature Scaling**: StandardScaler for numeric features
- **Validation**: K-fold cross-validation (default: 5 folds)
- **Multicollinearity Detection**: VIF > 10 flagged as problematic
- **Confidence Intervals**: Based on RMSE (95% interval)

### Evaluation Metrics

| Metric | Description |
|--------|-------------|
| R² | Coefficient of determination |
| Adjusted R² | R² adjusted for number of predictors |
| RMSE | Root Mean Square Error |
| MAE | Mean Absolute Error |
| CV R² | Cross-validated R² (mean ± std) |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with FastAPI, Next.js, and scikit-learn
</p>
