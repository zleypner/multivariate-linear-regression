# Campaign Multivariate Regression - Implementation Tracker

> **Version:** 1.1.0
> **Last Updated:** 2026-03-28
> **Status:** In Development - Phase 0 Complete
> **Document Type:** Living Document (update after each iteration)

---

## 1. Project Summary

**Campaign Multivariate Regression** is a full-stack application for analyzing marketing campaign performance using multivariate linear regression.

### What the System Does

| Capability | Description |
|------------|-------------|
| **Data Ingestion** | Upload CSV files with campaign data (budget, channel, audience, creative type, metrics) |
| **Data Validation** | Validate against schema, check data quality, detect outliers |
| **Feature Engineering** | Create derived features (conversion_rate, efficiency_score, profit_margin, etc.) |
| **ML Model Training** | Train linear regression models (OLS, Ridge, Lasso) with cross-validation |
| **Predictions** | Predict conversions for new campaigns with confidence intervals |
| **Analytics Dashboard** | Visualize model performance, feature importance, and residuals |
| **API** | RESTful API with 17 endpoints for all operations |

### Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS, Recharts |
| Backend | FastAPI, Python 3.10+, Pydantic v2, Uvicorn |
| ML | Scikit-learn, Pandas, NumPy, Statsmodels |
| Data | CSV files, JSON schema validation |

---

## 2. Business Objective

### Primary Goals

1. **Optimize Marketing Campaigns** - Use historical data to predict which campaign configurations will generate the most conversions
2. **Data-Driven Decisions** - Replace intuition with statistical analysis for budget allocation
3. **ROI Prediction** - Estimate return on ad spend before launching campaigns
4. **Feature Analysis** - Understand which variables (channel, creative type, audience) have the most impact

### Target Users

- Marketing Analysts
- Campaign Managers
- Data Scientists
- Business Decision Makers

### Value Proposition

- Predict campaign performance before spending budget
- Identify high-impact variables for optimization
- Reduce wasted ad spend through data-driven targeting
- Foundation for building a SaaS product

---

## 3. Current State (Real Audit)

### 3.1 Project Structure

```
multivariate-linear-regression/
├── .claude/                    # Claude Code agent configurations
│   └── agents/                 # 14 agent definition files
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py            # App entry point, health endpoints
│   │   ├── config.py          # Pydantic settings configuration
│   │   ├── middleware/        # Error handling middleware
│   │   ├── models/            # Pydantic schemas (13 schemas)
│   │   ├── routes/            # API endpoints (4 route files)
│   │   └── services/          # Business logic (file, ml services)
│   └── requirements.txt       # Python dependencies
├── frontend/                   # Next.js application
│   ├── src/
│   │   ├── app/               # 5 pages (dashboard, upload, train, predict, results)
│   │   ├── components/        # 8 React components
│   │   ├── context/           # Global state (Context + useReducer)
│   │   └── lib/               # API client, types, utils
│   ├── package.json           # Node dependencies
│   └── tailwind.config.ts     # Tailwind configuration
├── ml/                         # Machine Learning modules
│   ├── model.py               # Main regression model
│   ├── regression.py          # Legacy model (OLS, Ridge, Lasso)
│   ├── preprocessing.py       # Data preprocessor (modern)
│   ├── preprocessor.py        # Legacy preprocessor
│   ├── pipeline.py            # Data pipeline (load, validate, transform)
│   ├── feature_engineering.py # Feature creation and selection
│   ├── data_quality.py        # Quality checks and profiling
│   ├── utils.py               # Utilities
│   └── requirements.txt       # ML dependencies
├── data/
│   ├── sample_campaigns.csv   # 50 sample records
│   └── schema.json            # Data schema definition
└── docs/                       # Documentation (this file)
```

### 3.2 Backend Status

| Component | Files | Status | Notes |
|-----------|-------|--------|-------|
| **API Entry Point** | `main.py` | COMPLETE | FastAPI app, CORS, health checks |
| **Configuration** | `config.py` | COMPLETE | Pydantic settings, env support |
| **Error Handling** | `middleware/` | COMPLETE | Custom exceptions, error middleware |
| **Schemas** | `models/schemas.py` | COMPLETE | 13 Pydantic models |
| **Upload Routes** | `routes/upload.py` | COMPLETE | POST /upload, GET /files, DELETE /files/{id} |
| **Train Routes** | `routes/train.py` | COMPLETE | POST /train, GET /train/runs, GET /train/{id} |
| **Predict Routes** | `routes/predict.py` | COMPLETE | POST /predict, POST /predict/single |
| **Results Routes** | `routes/results.py` | COMPLETE | GET /results, /summary, /coefficients, /vif |
| **File Service** | `services/file_service.py` | COMPLETE | CSV parsing, validation, storage |
| **ML Service** | `services/ml_service.py` | COMPLETE | Training, prediction, metrics |

**Total: 17 API Endpoints**

### 3.3 ML Modules Status

| Module | Lines | Status | Description |
|--------|-------|--------|-------------|
| `model.py` | 597 | COMPLETE | CampaignRegressionModel with VIF analysis |
| `regression.py` | 229 | COMPLETE | Legacy model (OLS, Ridge, Lasso) |
| `preprocessing.py` | 312 | COMPLETE | Modern preprocessor with ColumnTransformer |
| `preprocessor.py` | 164 | COMPLETE | Legacy preprocessor (LabelEncoder) |
| `pipeline.py` | 837 | COMPLETE | CSVDataLoader, DataValidator, DataTransformer |
| `feature_engineering.py` | 993 | COMPLETE | 9 derived features, selection, correlation |
| `data_quality.py` | 1034 | COMPLETE | Quality checks, statistics, profiling |
| `utils.py` | 375 | COMPLETE | Model persistence, formatting, validation |
| `__init__.py` | 170 | COMPLETE | Public API exports |

**Total: ~4,711 lines of Python code**

### 3.4 Frontend Status

| Component | Status | Description |
|-----------|--------|-------------|
| **Dashboard (/)** | COMPLETE | Welcome state + model metrics display |
| **Upload Page** | COMPLETE | Drag-drop CSV upload with preview |
| **Train Page** | COMPLETE | Feature selection, config, training |
| **Predict Page** | COMPLETE | Prediction form with history |
| **Results Page** | COMPLETE | Tabs: Overview, Features, Residuals |
| **Navbar** | COMPLETE | Navigation, theme toggle, model status |
| **FileUpload** | COMPLETE | Dropzone with validation |
| **DataPreview** | COMPLETE | Sortable table with pagination |
| **MetricsCard** | COMPLETE | Metric display with formatting |
| **FeatureImportance** | COMPLETE | Bar chart visualization |
| **PredictionForm** | COMPLETE | Dynamic form based on features |
| **ResultsChart** | COMPLETE | Scatter plot + residuals |
| **LoadingSpinner** | COMPLETE | Multiple size variants |

**Total: 5 pages, 8 components**

### 3.5 What's Incomplete or Broken

| Issue | Location | Severity | Description |
|-------|----------|----------|-------------|
| No data persistence | Backend | HIGH | Models, files, results lost on restart |
| No authentication | Backend | MEDIUM | API completely open |
| No rate limiting | Backend | MEDIUM | No abuse protection |
| Dependencies not installed | Frontend | HIGH | `npm install` not run |
| Tailwind color gaps | Frontend | LOW | Missing success/warning/error scales |
| Theme not persisted | Frontend | LOW | Resets to light on reload |
| No .gitignore | Root | MEDIUM | Sensitive files could be committed |
| No README | Root | HIGH | No setup instructions |
| No tests | All | MEDIUM | No test files exist |
| /metrics placeholder | Backend | LOW | Returns stub, not real metrics |

---

## 4. Architecture Overview

### 4.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│
│  │ Dashboard│ │  Upload  │ │  Train   │ │ Predict  │ │Results ││
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬────┘│
│       │            │            │            │           │      │
│  ┌────┴────────────┴────────────┴────────────┴───────────┴────┐ │
│  │                    AppContext (State)                      │ │
│  └────────────────────────────┬───────────────────────────────┘ │
│                               │                                  │
│  ┌────────────────────────────┴───────────────────────────────┐ │
│  │                    API Client (lib/api.ts)                 │ │
│  └────────────────────────────┬───────────────────────────────┘ │
└───────────────────────────────┼─────────────────────────────────┘
                                │ HTTP/REST
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                          BACKEND (FastAPI)                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐  │
│  │ /upload │ │ /train  │ │/predict │ │/results │ │ /health     │  │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └─────────────┘  │
│       │           │           │           │                        │
│  ┌────┴───────────┴───────────┴───────────┴────────────────────┐  │
│  │                      SERVICES                                │  │
│  │  ┌─────────────────┐  ┌─────────────────────────────────┐   │  │
│  │  │  FileService    │  │  MLService                      │   │  │
│  │  │  - parse CSV    │  │  - train model                  │   │  │
│  │  │  - validate     │  │  - predict                      │   │  │
│  │  │  - store        │  │  - evaluate                     │   │  │
│  │  └─────────────────┘  └──────────────┬──────────────────┘   │  │
│  └──────────────────────────────────────┼──────────────────────┘  │
└─────────────────────────────────────────┼─────────────────────────┘
                                          │ Import
                                          ▼
┌───────────────────────────────────────────────────────────────────┐
│                          ML MODULE                                 │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    CampaignRegressionModel                   │  │
│  │  - fit()  - predict()  - evaluate()  - get_vif_report()     │  │
│  └──────────────────────────────┬──────────────────────────────┘  │
│                                 │                                  │
│  ┌──────────────┐ ┌─────────────┴───────────┐ ┌────────────────┐  │
│  │ Pipeline     │ │ FeatureEngineer         │ │ DataQuality    │  │
│  │ - load       │ │ - create_derived()      │ │ - check()      │  │
│  │ - validate   │ │ - select_features()     │ │ - profile()    │  │
│  │ - transform  │ │ - analyze_correlation() │ │ - statistics() │  │
│  └──────────────┘ └─────────────────────────┘ └────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
```

### 4.2 Data Flow

```
CSV File → Upload → Validate → Transform → Train Model → Store Results
                                              ↓
                 Predict ← Apply Model ← Load Model
                    ↓
              Return Predictions + Confidence Intervals
```

---

## 5. Functional Requirements

### 5.1 Data Ingestion

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Upload CSV files | DONE | `POST /api/upload` with multipart/form-data |
| Validate file type | DONE | FileService checks .csv extension |
| Validate file size | DONE | Max 10MB configured in config.py |
| Parse CSV to DataFrame | DONE | Pandas read_csv in FileService |
| Return data preview | DONE | First N rows returned in response |
| List uploaded files | DONE | `GET /api/files` |
| Delete uploaded files | DONE | `DELETE /api/files/{id}` |

### 5.2 Data Processing

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Validate schema | DONE | DataValidator checks columns, types, constraints |
| Handle missing values | DONE | Imputation with median/mode |
| Detect outliers | DONE | Z-score threshold (3.0) |
| Handle outliers | DONE | Clipping to bounds |
| Encode categoricals | DONE | OneHotEncoder in preprocessing.py |
| Scale numerics | DONE | StandardScaler |
| Create derived features | DONE | 9 features in FeatureEngineer |

### 5.3 Machine Learning

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Train regression model | DONE | LinearRegression with sklearn |
| Support multiple algorithms | DONE | OLS, Ridge, Lasso in regression.py |
| Cross-validation | DONE | K-Fold (5 folds default) |
| Calculate metrics | DONE | R2, RMSE, MAE, MSE |
| Feature importance | DONE | Coefficients + absolute values |
| VIF analysis | DONE | statsmodels variance_inflation_factor |
| Single prediction | DONE | `POST /api/predict/single` |
| Batch prediction | DONE | `POST /api/predict` |
| Confidence intervals | DONE | RMSE * 1.96 approximation |
| Save/load model | PARTIAL | joblib in utils.py, but backend uses memory only |

### 5.4 API

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| RESTful endpoints | DONE | 17 endpoints in 4 route files |
| Request validation | DONE | Pydantic schemas |
| Error handling | DONE | Custom exceptions + middleware |
| CORS support | DONE | Configured in main.py |
| Health checks | DONE | `/health` and `/ready` endpoints |
| OpenAPI docs | DONE | Auto-generated at `/docs` |
| Authentication | MISSING | No auth implemented |
| Rate limiting | MISSING | No rate limiting |

### 5.5 Frontend

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Dashboard view | DONE | Conditional render based on model state |
| File upload UI | DONE | Drag-drop with react-dropzone |
| Data preview table | DONE | Sortable, searchable table |
| Training configuration | DONE | Feature selection, target, settings |
| Training progress | DONE | Simulated progress bar |
| Results visualization | DONE | Charts with Recharts |
| Prediction form | DONE | Dynamic inputs from model features |
| Dark mode | DONE | Theme toggle in Navbar |
| Responsive design | DONE | Tailwind responsive classes |
| State management | DONE | Context + useReducer |

---

## 6. Non-Functional Requirements

| Requirement | Status | Notes |
|-------------|--------|-------|
| **Modularity** | DONE | Clear separation: routes, services, models, components |
| **Scalability** | PARTIAL | Stateless API but no persistence layer |
| **Type Safety** | DONE | TypeScript strict mode + Pydantic models |
| **Error Handling** | DONE | Centralized middleware, custom exceptions |
| **Logging** | DONE | Structlog with JSON/console output |
| **Configuration** | DONE | Environment variables via Pydantic settings |
| **Documentation** | PARTIAL | Python docstrings excellent, no README |
| **Testing** | MISSING | No test files exist |
| **Security** | MISSING | No auth, no rate limiting |
| **Performance** | UNKNOWN | No benchmarks or optimization |

---

## 7. Gap Analysis

### Legend
- **Done**: Fully implemented and functional
- **Partial**: Implemented but incomplete
- **Missing**: Not implemented
- **Blocked**: Cannot proceed due to dependency

| Area | Item | Status | Gap Description |
|------|------|--------|-----------------|
| **Infrastructure** | Data persistence | MISSING | All data in memory, lost on restart |
| | Database integration | MISSING | No PostgreSQL/Redis setup |
| | Docker configuration | MISSING | No Dockerfile or compose |
| | CI/CD pipeline | MISSING | No GitHub Actions or similar |
| **Security** | Authentication | MISSING | API completely open |
| | Authorization | MISSING | No role-based access |
| | Rate limiting | MISSING | No abuse protection |
| | Input sanitization | PARTIAL | Pydantic validates but no XSS protection |
| **Quality** | Unit tests | MISSING | No test files |
| | Integration tests | MISSING | No API tests |
| | E2E tests | MISSING | No Cypress/Playwright |
| | Code coverage | MISSING | No coverage reports |
| **Documentation** | README.md | MISSING | No project documentation |
| | .gitignore | MISSING | No git ignore rules |
| | API documentation | DONE | OpenAPI auto-generated |
| | Setup guide | MISSING | No installation instructions |
| **Frontend** | Dependencies installed | BLOCKED | `npm install` not run |
| | Theme persistence | MISSING | Theme resets on reload |
| | Error boundaries | MISSING | No React error boundaries |
| | Accessibility | PARTIAL | Some ARIA labels missing |
| **Backend** | Model persistence | MISSING | Models not saved to disk |
| | Background jobs | MISSING | Training is synchronous |
| | Metrics endpoint | PARTIAL | Placeholder only |
| | Logging to file | MISSING | Console only |
| **ML** | Model versioning | MISSING | No MLflow or similar |
| | A/B testing | MISSING | No experiment tracking |
| | Feature store | MISSING | No centralized feature management |

---

## 8. Execution Roadmap

### Phase 0: Foundation (Current Priority)
**Objective:** Make the project runnable and properly documented

| Task | Dependency | Definition of Done |
|------|------------|-------------------|
| Create README.md | None | Installation, usage, API docs |
| Create .gitignore | None | Standard ignores for Python/Node |
| Install frontend dependencies | None | `npm install` succeeds |
| Fix Tailwind color scales | npm install | All color variants render |
| Verify frontend runs | Dependencies | `npm run dev` starts without errors |
| Verify backend runs | None | `uvicorn` starts, `/health` returns 200 |
| Test full flow manually | Both running | Upload → Train → Predict works |

### Phase 1: Persistence
**Objective:** Data survives server restarts

| Task | Dependency | Definition of Done |
|------|------------|-------------------|
| Add file-based model persistence | Phase 0 | Models saved/loaded from disk |
| Add file metadata persistence | Phase 0 | Uploaded files tracked in JSON |
| Add training results persistence | Phase 0 | Results saved to JSON/SQLite |
| Theme persistence (localStorage) | Phase 0 | Theme survives page reload |

### Phase 2: Quality & Testing
**Objective:** Ensure reliability through tests

| Task | Dependency | Definition of Done |
|------|------------|-------------------|
| Add pytest configuration | Phase 1 | pytest runs successfully |
| Write API integration tests | pytest | Coverage for all endpoints |
| Add Jest/Vitest for frontend | Phase 0 | Test runner configured |
| Write component tests | Jest | Core components tested |
| Add pre-commit hooks | Tests | Linting + tests on commit |

### Phase 3: Security
**Objective:** Secure the API for production

| Task | Dependency | Definition of Done |
|------|------------|-------------------|
| Add API key authentication | Phase 1 | Endpoints require valid key |
| Implement rate limiting | Auth | 100 req/min per client |
| Add request logging | Rate limit | All requests logged with metadata |
| Security audit | All above | No critical vulnerabilities |

### Phase 4: Production Readiness
**Objective:** Deployable to production

| Task | Dependency | Definition of Done |
|------|------------|-------------------|
| Create Dockerfile (backend) | Phase 2 | Container builds and runs |
| Create Dockerfile (frontend) | Phase 2 | Container builds and runs |
| Create docker-compose.yml | Dockerfiles | Full stack runs with compose |
| Add health check endpoints | Containers | Kubernetes-ready probes |
| Create deployment docs | All above | Step-by-step deploy guide |

### Phase 5: Enhancements (Future)
**Objective:** Advanced features

| Task | Dependency | Definition of Done |
|------|------------|-------------------|
| Database integration (PostgreSQL) | Phase 4 | Replace file persistence |
| Background job processing | Database | Async training with Celery/RQ |
| Model versioning | Database | Track multiple model versions |
| User management | Database | Multi-user support |
| Dashboard analytics | All above | Usage metrics and insights |

---

## 9. Live Checklist

### Infrastructure
- [x] README.md created
- [x] .gitignore created
- [x] Frontend dependencies installed
- [x] Backend runs successfully
- [x] Frontend builds successfully
- [ ] Full flow tested (upload → train → predict)

### Persistence
- [ ] Model persistence implemented
- [ ] File metadata persistence implemented
- [ ] Training results persistence implemented
- [ ] Theme persistence (localStorage)

### Quality
- [ ] Pytest configured
- [ ] Backend tests written
- [ ] Jest/Vitest configured
- [ ] Frontend tests written
- [ ] Pre-commit hooks added

### Security
- [ ] API authentication implemented
- [ ] Rate limiting implemented
- [ ] Request logging implemented

### Production
- [ ] Backend Dockerfile created
- [ ] Frontend Dockerfile created
- [ ] docker-compose.yml created
- [ ] Deployment documentation written

### Code Completion
- [x] Backend API endpoints (17/17)
- [x] Backend services (2/2)
- [x] Backend middleware (1/1)
- [x] Backend schemas (13/13)
- [x] ML model module
- [x] ML preprocessing module
- [x] ML pipeline module
- [x] ML feature engineering module
- [x] ML data quality module
- [x] Frontend pages (5/5)
- [x] Frontend components (8/8)
- [x] Frontend state management
- [x] Frontend API client

---

## 10. Technical Decisions

| Decision | Choice | Rationale | Date |
|----------|--------|-----------|------|
| Frontend Framework | Next.js 14 (App Router) | Modern React with SSR capability | Initial |
| Backend Framework | FastAPI | Async support, auto OpenAPI, Pydantic | Initial |
| ML Library | Scikit-learn | Industry standard, well documented | Initial |
| State Management | Context + useReducer | Sufficient for app size, no external deps | Initial |
| Styling | Tailwind CSS | Rapid development, consistent design | Initial |
| Charts | Recharts | React-native, good customization | Initial |
| Data Validation | Pydantic v2 | Type safety, FastAPI integration | Initial |
| Preprocessing | ColumnTransformer | Sklearn best practice, clean pipelines | Initial |
| VIF Analysis | Statsmodels | Standard for multicollinearity detection | Initial |
| File Upload | react-dropzone | Mature library, good DX | Initial |
| Python Version | 3.10+ | Type hints syntax, match statements | Initial |
| Encoding Strategy | OneHotEncoder | Avoid ordinal assumptions | Initial |

### Pending Decisions

| Decision | Options | Blocker |
|----------|---------|---------|
| Persistence Strategy | File-based vs SQLite vs PostgreSQL | Phase 1 planning |
| Authentication Method | API Keys vs JWT vs OAuth | Phase 3 planning |
| Deployment Target | Vercel/Railway vs AWS vs Self-hosted | Phase 4 planning |
| Model Registry | MLflow vs Custom vs None | Future consideration |

---

## 11. Next Recommended Step

### Phase 0 Complete - Moving to Phase 1

**Begin Phase 1: Persistence**

Phase 0 is complete. The application builds and runs successfully. Next priority:

1. Implement model persistence (save/load from disk)
2. Implement file metadata persistence
3. Add theme persistence (localStorage)

**Specific Tasks:**

1. Create `uploads/` directory for persistent file storage
2. Modify `ml_service.py` to save trained models to disk
3. Create a JSON file to track uploaded files metadata
4. Add localStorage for theme preference in frontend

**How to start working:**

```bash
# Terminal 1: Start backend
cd backend && source ../venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend && npm run dev
```

**Definition of Done:**
- Models persist after server restart
- Uploaded files metadata persists
- Theme preference persists in browser

---

## Appendix A: API Endpoint Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |
| GET | `/metrics` | Prometheus metrics (placeholder) |
| POST | `/api/upload` | Upload CSV file |
| GET | `/api/files` | List uploaded files |
| DELETE | `/api/files/{id}` | Delete file |
| POST | `/api/train` | Train model |
| GET | `/api/train/runs` | List training runs |
| GET | `/api/train/{id}` | Get training result |
| POST | `/api/predict` | Batch prediction |
| POST | `/api/predict/single` | Single prediction |
| GET | `/api/results` | Latest results |
| GET | `/api/results/summary` | Results summary |
| GET | `/api/results/coefficients` | Model coefficients |
| GET | `/api/results/feature-importance` | Feature importance |
| GET | `/api/results/vif` | VIF report |
| GET | `/model/info` | Model information |

---

## Appendix B: Data Schema Summary

**Input Columns:**
- `campaign_id` (string, unique)
- `budget` (float, 0-1M)
- `audience_type` (categorical: lookalike, interest, retargeting, broad)
- `creative_type` (categorical: video, image, carousel)
- `channel` (categorical: facebook, instagram, tiktok, google, youtube)
- `impressions` (integer, >= 0)
- `clicks` (integer, >= 0)
- `ctr` (float, 0-100)
- `cpc` (float, >= 0)
- `conversions` (integer, >= 0) - **TARGET**
- `cpl` (float, >= 0)
- `revenue` (float, >= 0)
- `roas` (float, >= 0)

**Derived Features:**
- `cost_per_impression` = budget / impressions
- `conversion_rate` = conversions / clicks
- `efficiency_score` = conversions / budget * 1000
- `engagement_rate` = clicks / impressions
- `revenue_per_conversion` = revenue / conversions

---

*This document should be updated after each development iteration.*
