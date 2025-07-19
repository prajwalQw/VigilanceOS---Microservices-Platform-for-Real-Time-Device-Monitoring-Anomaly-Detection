from fastapi import FastAPI
import uvicorn
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Anomaly Detection Service", version="1.0.0")

class TelemetryData(BaseModel):
    device_id: str
    temperature: Optional[float] = None
    battery: Optional[float] = None
    signal_strength: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None

class AnomalyResult(BaseModel):
    is_anomaly: bool
    confidence: float
    anomaly_score: float

# Global model and scaler
model = None
scaler = None

def load_or_create_model():
    """Load existing model or create a new one"""
    global model, scaler
    
    model_path = os.getenv("MODEL_PATH", "/app/model/anomaly_model.pkl")
    scaler_path = os.getenv("SCALER_PATH", "/app/model/scaler.pkl")
    
    try:
        # Try to load existing model
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        print("Loaded existing anomaly detection model")
    except FileNotFoundError:
        # Create new model with default parameters
        model = IsolationForest(
            contamination=0.1,  # Expect 10% anomalies
            random_state=42,
            n_estimators=100
        )
        scaler = StandardScaler()
        
        # Train with synthetic data
        synthetic_data = generate_synthetic_training_data()
        scaler.fit(synthetic_data)
        scaled_data = scaler.transform(synthetic_data)
        model.fit(scaled_data)
        
        # Save the model
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        print("Created and saved new anomaly detection model")

def generate_synthetic_training_data():
    """Generate synthetic training data for the model"""
    np.random.seed(42)
    n_samples = 1000
    
    # Normal operating ranges
    temperature = np.random.normal(25, 5, n_samples)  # 25°C ± 5°C
    battery = np.random.normal(80, 15, n_samples)     # 80% ± 15%
    signal_strength = np.random.normal(-65, 10, n_samples)  # -65dBm ± 10dBm
    cpu_usage = np.random.normal(50, 20, n_samples)   # 50% ± 20%
    memory_usage = np.random.normal(60, 25, n_samples)  # 60% ± 25%
    disk_usage = np.random.normal(40, 15, n_samples)  # 40% ± 15%
    
    # Add some anomalies
    n_anomalies = int(0.1 * n_samples)
    anomaly_indices = np.random.choice(n_samples, n_anomalies, replace=False)
    
    # Create extreme values for anomalies
    temperature[anomaly_indices[:n_anomalies//3]] = np.random.uniform(90, 120, n_anomalies//3)
    battery[anomaly_indices[n_anomalies//3:2*n_anomalies//3]] = np.random.uniform(0, 10, n_anomalies//3)
    signal_strength[anomaly_indices[2*n_anomalies//3:]] = np.random.uniform(-120, -100, n_anomalies//3)
    
    # Combine into dataset
    data = np.column_stack([
        temperature, battery, signal_strength,
        cpu_usage, memory_usage, disk_usage
    ])
    
    return data

def prepare_features(telemetry: TelemetryData):
    """Prepare features for anomaly detection"""
    features = [
        telemetry.temperature or 25.0,
        telemetry.battery or 80.0,
        telemetry.signal_strength or -65.0,
        telemetry.cpu_usage or 50.0,
        telemetry.memory_usage or 60.0,
        telemetry.disk_usage or 40.0
    ]
    return np.array(features).reshape(1, -1)

@app.on_event("startup")
async def startup_event():
    """Initialize the model on startup"""
    load_or_create_model()

@app.get("/")
async def root():
    return {"message": "Anomaly Detection Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict", response_model=AnomalyResult)
async def predict_anomaly(telemetry: TelemetryData):
    """Predict if telemetry data contains anomalies"""
    if model is None or scaler is None:
        return AnomalyResult(
            is_anomaly=False,
            confidence=0.0,
            anomaly_score=0.0
        )
    
    # Prepare features
    features = prepare_features(telemetry)
    
    # Scale features
    scaled_features = scaler.transform(features)
    
    # Predict anomaly
    prediction = model.predict(scaled_features)[0]
    anomaly_score = model.decision_function(scaled_features)[0]
    
    # Convert to probability-like confidence
    confidence = abs(anomaly_score)
    
    is_anomaly = prediction == -1
    
    return AnomalyResult(
        is_anomaly=is_anomaly,
        confidence=confidence,
        anomaly_score=anomaly_score
    )

@app.post("/retrain")
async def retrain_model():
    """Retrain the model with new synthetic data"""
    global model, scaler
    
    # Generate new training data
    training_data = generate_synthetic_training_data()
    
    # Retrain scaler and model
    scaler.fit(training_data)
    scaled_data = scaler.transform(training_data)
    model.fit(scaled_data)
    
    # Save updated model
    model_path = os.getenv("MODEL_PATH", "/app/model/anomaly_model.pkl")
    scaler_path = os.getenv("SCALER_PATH", "/app/model/scaler.pkl")
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    return {"message": "Model retrained successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)