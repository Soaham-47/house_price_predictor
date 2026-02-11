## Housing ML end2end Project

## Project Overview

Housing Regression MLE is an end-to-end machine learning pipeline for predicting housing prices using XGBoost. The project follows ML engineering best practices with modular pipelines, experiment tracking via MLflow, containerization, and comprehensive testing. The system includes both a REST API and a Streamlit dashboard for interactive predictions.

## Architecture

The codebase is organized into distinct pipelines following the flow:
`Load → Preprocess → Feature Engineering → Train → Tune → Evaluate → Inference → Batch → Serve`

### Core Modules

- **`src/feature_pipeline/`**: Data loading, preprocessing, and feature engineering
  - `load.py`: Time-aware data splitting (train <2020, eval 2020-21, holdout ≥2022)
  - `preprocess.py`: City normalization, deduplication, outlier removal  
  - `feature_engineering.py`: Date features, frequency encoding (zipcode), target encoding (city_full)

- **`src/training_pipeline/`**: Model training and hyperparameter optimization
  - `train.py`: Baseline XGBoost training with configurable parameters
  - `tune.py`: Optuna-based hyperparameter tuning with MLflow integration
  - `eval.py`: Model evaluation and metrics calculation

- **`src/inference_pipeline/`**: Production inference
  - `inference.py`: Applies same preprocessing/encoding transformations using saved encoders

- **`src/batch/`**: Batch prediction processing
  - `run_monthly.py`: Generates monthly predictions on holdout data

- **`src/api/`**: FastAPI web service
  - `main.py`: REST API with health checks, prediction endpoints, and batch processing

### Web Applications

- **`app.py`**: Streamlit dashboard for interactive housing price predictions
  - Real-time predictions via FastAPI integration
  - Interactive filtering by year, month, and region
  - Visualization of predictions vs actuals with metrics (MAE, RMSE, % Error)
  - Yearly trend analysis with highlighted selected periods


### Data Leakage Prevention

The project implements strict data leakage prevention:
- Time-based splits (not random)
- Encoders fitted only on training data
- Leakage-prone columns dropped before training
- Schema alignment enforced between train/eval/inference

## Common Commands

### Environment Setup
```bash
# Install dependencies using uv
uv sync
```

### Testing
```bash
# Run all tests
pytest

# Run specific test modules  
pytest tests/test_features.py
pytest tests/test_training.py
pytest tests/test_inference.py

# Run with verbose output
pytest -v
```

### Data Pipeline
```bash
# 1. Load and split raw data
python src/feature_pipeline/load.py

# 2. Preprocess splits
python -m src.feature_pipeline.preprocess

# 3. Feature engineering
python -m src.feature_pipeline.feature_engineering
```

### Training Pipeline
```bash
# Train baseline model
python src/training_pipeline/train.py

# Hyperparameter tuning with MLflow
python src/training_pipeline/tune.py

# Model evaluation
python src/training_pipeline/eval.py
```

### Inference
```bash
# Single inference
python src/inference_pipeline/inference.py --input data/raw/holdout.csv --output predictions.csv

# Batch monthly predictions
python src/batch/run_monthly.py
```

### API Service
```bash
# Start FastAPI server locally
uv run uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

### Streamlit Dashboard
```bash
# Start Streamlit dashboard locally
streamlit run app.py --server.address 127.0.0.1
```

### Docker
```bash
# Build API container
docker build -t housing-regression .

# Build Streamlit container  
docker build -t housing-streamlit -f Dockerfile.streamlit .

# Run API container
docker run -p 8000:8000 housing-regression

# Run Streamlit container
docker run -p 8501:8501 housing-streamlit
```

### MLflow Tracking
```bash
# Start MLflow UI (view experiments)
mlflow ui
```

## Key Design Patterns

### Pipeline Modularity
Each pipeline component can be run independently with consistent interfaces. All modules accept configurable input/output paths for testing isolation.

### Encoder Persistence  
Frequency and target encoders are saved as pickle files during training and loaded during inference to ensure consistent transformations.

### Configuration Management
Model parameters, file paths, and pipeline settings use sensible defaults but can be overridden through function parameters or environment variables. Production deployments use AWS environment variables.

### Testing Strategy
- Unit tests for individual pipeline components
- Integration tests for end-to-end pipeline flows  
- Smoke tests for inference pipeline
- All tests use temporary directories to avoid touching production data

## Dependencies

Key production dependencies (see `pyproject.toml`):
- **ML/Data**: `xgboost==3.0.4`, `scikit-learn`, `pandas==2.1.1`, `numpy==1.26.4`
- **API**: `fastapi`, `uvicorn`
- **Dashboard**: `streamlit`, `plotly`
- **Experimentation**: `mlflow`, `optuna`
- **Quality**: `great-expectations`, `evidently`

## File Structure Notes

- **`data/`**: Raw, processed, and prediction data (time-structured, S3-synced)
- **`models/`**: Trained models and encoders (pkl files, S3-synced)
- **`mlruns/`**: MLflow experiment tracking data
- **`configs/`**: YAML configuration files
- **`notebooks/`**: Jupyter notebooks for EDA and experimentation
- **`tests/`**: Comprehensive test suite with sample data
