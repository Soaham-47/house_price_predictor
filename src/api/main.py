# Goal: Create a FastAPI app to serve your trained ML model into a web service that anyone 
# (or any system) can call over HTTP.

from fastapi import FastAPI            # Web framework for APIs
from pathlib import Path               # For handling file paths cleanly
from typing import List, Dict, Any     # For type hints (clarity in endpoints)
import pandas as pd                    # To handle incoming JSON as DataFrames
import os                              # Env variables

# Import inference pipeline
from src.inference_pipeline.inference import predict

# ----------------------------
# Config
# ----------------------------
# Removed S3_BUCKET, REGION, and boto3 client

# ----------------------------
# Paths
# ----------------------------
# Point directly to local artifacts. 
# Ensure you have run 'train.py' so these files exist.
MODEL_PATH = Path("models/xgb_best_model.pkl")
TRAIN_FE_PATH = Path("data/processed/feature_engineered_train.csv")

# Load expected training features for alignment
if TRAIN_FE_PATH.exists():
    _train_cols = pd.read_csv(TRAIN_FE_PATH, nrows=1)
    TRAIN_FEATURE_COLUMNS = [c for c in _train_cols.columns if c != "price"]
else:
    print(f"⚠️ Warning: Training features not found at {TRAIN_FE_PATH}. Schema validation disabled.")
    TRAIN_FEATURE_COLUMNS = None

# ----------------------------
# App
# ----------------------------
# Instantiates the FastAPI app.
app = FastAPI(title="Housing Regression API")

# / → simple landing endpoint to confirm API is alive.
@app.get("/")
def root():
    return {"message": "Housing Regression API is running (Local Mode) 🚀"}

# /health → checks if model exists, returns status info (like expected feature count).
@app.get("/health")
def health():
    status: Dict[str, Any] = {"model_path": str(MODEL_PATH)}
    if not MODEL_PATH.exists():
        status["status"] = "unhealthy"
        status["error"] = "Model not found"
    else:
        status["status"] = "healthy"
        if TRAIN_FEATURE_COLUMNS:
            status["n_features_expected"] = len(TRAIN_FEATURE_COLUMNS)
    return status

# Prediction Endpoint: This is the core ML serving endpoint.
@app.post("/predict")
def predict_batch(data: List[dict]):
    if not MODEL_PATH.exists():
        return {"error": f"Model not found at {str(MODEL_PATH)}"}

    df = pd.DataFrame(data)
    if df.empty:
        return {"error": "No data provided"}

    # Run inference using the local model path
    preds_df = predict(df, model_path=MODEL_PATH)

    resp = {"predictions": preds_df["predicted_price"].astype(float).tolist()}
    if "actual_price" in preds_df.columns:
        resp["actuals"] = preds_df["actual_price"].astype(float).tolist()

    return resp

# Batch runner
from src.batch.run_monthly import run_monthly_predictions

# Trigger a monthly batch job via API.
@app.post("/run_batch")
def run_batch():
    # Ensure the batch runner is also not trying to use S3 internally
    preds = run_monthly_predictions()
    return {
        "status": "success",
        "rows_predicted": int(len(preds)),
        "output_dir": "data/predictions/"
    }

# Returns a preview of the most recent batch predictions.
@app.get("/latest_predictions")
def latest_predictions(limit: int = 5):
    pred_dir = Path("data/predictions")
    # Ensure directory exists before globbing
    if not pred_dir.exists():
        return {"error": f"Directory not found: {pred_dir}"}
        
    files = sorted(pred_dir.glob("preds_*.csv"))
    if not files:
        return {"error": "No predictions found"}

    latest_file = files[-1]
    df = pd.read_csv(latest_file)
    return {
        "file": latest_file.name,
        "rows": int(len(df)),
        "preview": df.head(limit).to_dict(orient="records")
    }


"""
🔹 Execution Order / Module Flow

1. Imports (FastAPI, pandas, inference function).
2. Define Local Paths (MODEL_PATH, TRAIN_FE_PATH).
3. Infer schema (TRAIN_FEATURE_COLUMNS) from local CSV.
4. Create FastAPI app (app = FastAPI).
5. Declare endpoints (/, /health, /predict, /run_batch, /latest_predictions).
"""