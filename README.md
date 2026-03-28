# Campaign Multivariate Regression

A full-stack application for analyzing marketing campaign performance using multivariate linear regression. Upload campaign data, train predictive models, and forecast conversions for new campaigns.

## Features

- **Data Upload**: CSV file upload with validation and preview
- **Data Quality**: Automatic validation, outlier detection, missing value handling
- **ML Training**: Linear regression with cross-validation and VIF analysis
- **Predictions**: Single and batch predictions with confidence intervals
- **Dashboard**: Interactive visualizations of model performance and feature importance

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS, Recharts |
| Backend | FastAPI, Python 3.10+, Pydantic v2, Uvicorn |
| ML | Scikit-learn, Pandas, NumPy, Statsmodels |

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- npm or yarn

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd multivariate-linear-regression
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r ml/requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Start the Backend

```bash
# From the project root, with venv activated
cd backend
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Start the Frontend

```bash
# In a new terminal
cd frontend
npm run dev
```

The dashboard will be available at `http://localhost:3000`

## Usage

### 1. Upload Data

Navigate to `/upload` and drag-drop a CSV file with campaign data.

**Required columns:**
- `campaign_id` - Unique identifier
- `budget` - Campaign budget in dollars
- `audience_type` - One of: lookalike, interest, retargeting, broad
- `creative_type` - One of: video, image, carousel
- `channel` - One of: facebook, instagram, tiktok, google, youtube
- `impressions` - Total ad impressions
- `clicks` - Total clicks
- `ctr` - Click-through rate (%)
- `cpc` - Cost per click
- `conversions` - Number of conversions (target variable)
- `cpl` - Cost per lead
- `revenue` - Total revenue
- `roas` - Return on ad spend

A sample file is available at `data/sample_campaigns.csv`.

### 2. Train Model

Navigate to `/train`:
1. Select the target variable (default: conversions)
2. Choose features to include
3. Configure training settings (optional)
4. Click "Train Model"

### 3. Make Predictions

Navigate to `/predict`:
1. Fill in campaign parameters
2. Click "Predict"
3. View predicted conversions with confidence interval

### 4. View Results

Navigate to `/results` to see:
- Model metrics (R², RMSE, MAE)
- Feature importance chart
- Actual vs Predicted scatter plot
- Residuals analysis

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/upload` | Upload CSV file |
| GET | `/api/files` | List uploaded files |
| DELETE | `/api/files/{id}` | Delete file |
| POST | `/api/train` | Train model |
| GET | `/api/train/runs` | List training runs |
| POST | `/api/predict` | Batch prediction |
| POST | `/api/predict/single` | Single prediction |
| GET | `/api/results` | Get latest results |
| GET | `/api/results/coefficients` | Model coefficients |
| GET | `/api/results/feature-importance` | Feature importance |
| GET | `/api/results/vif` | VIF report (multicollinearity) |

Full API documentation available at `/docs` when the backend is running.

## Project Structure

```
multivariate-linear-regression/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py         # App entry point
│   │   ├── config.py       # Configuration
│   │   ├── middleware/     # Error handling
│   │   ├── models/         # Pydantic schemas
│   │   ├── routes/         # API endpoints
│   │   └── services/       # Business logic
│   └── requirements.txt
├── frontend/                # Next.js application
│   ├── src/
│   │   ├── app/            # Pages (App Router)
│   │   ├── components/     # React components
│   │   ├── context/        # State management
│   │   └── lib/            # API client, types
│   └── package.json
├── ml/                      # ML modules
│   ├── model.py            # Regression model
│   ├── preprocessing.py    # Data preprocessing
│   ├── pipeline.py         # Data pipeline
│   ├── feature_engineering.py
│   ├── data_quality.py
│   └── requirements.txt
├── data/                    # Sample data
│   ├── sample_campaigns.csv
│   └── schema.json
└── docs/                    # Documentation
    └── implementation-tracker.md
```

## Development

### Running Tests

```bash
# Backend tests (when available)
cd backend
pytest

# Frontend tests (when available)
cd frontend
npm test
```

### Code Style

- Python: Follow PEP 8
- TypeScript: ESLint with Next.js config

## Environment Variables

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Backend

Configure via environment variables or `backend/app/config.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | Campaign Analytics API | Application name |
| `DEBUG` | false | Debug mode |
| `CORS_ORIGINS` | ["http://localhost:3000"] | Allowed origins |
| `MAX_UPLOAD_SIZE` | 10485760 | Max file size (10MB) |

## Known Limitations

- Data is stored in memory (lost on server restart)
- No authentication (API is open)
- No rate limiting
- Training is synchronous (may timeout for large datasets)

## Documentation

See `docs/implementation-tracker.md` for:
- Detailed architecture overview
- Gap analysis
- Development roadmap
- Technical decisions

## License

MIT
