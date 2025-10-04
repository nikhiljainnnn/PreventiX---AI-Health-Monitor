from fastapi.exceptions import RequestValidationError
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import numpy as np
import pandas as pd
import shap
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime
import json
import random
import os
import re
from dotenv import load_dotenv
from bson import ObjectId
from fastapi.responses import StreamingResponse
from pdf_generator import generate_health_report_pdf

# Load environment variables
load_dotenv()

# Import MongoDB components
from database import get_predictions_collection, get_tracking_collection, mongodb_client
from auth_routes import router as auth_router
from auth import get_current_active_user
from models import PredictionRecord, TrackingRecord
from tracking_routes import router as tracking_router

# Initialize FastAPI app
app = FastAPI(
    title="PreventiX Advanced API - Clean",
    description="AI-powered health risk prediction with personalized recommendations",
    version="3.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    logger.error(f"Body received: {exc.body}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": str(exc.body)
        }
    )

# Health Input Model
class HealthInput(BaseModel):
    """Comprehensive health input model"""
    age: int = Field(..., ge=18, le=120, description="Age in years")
    gender: int = Field(..., ge=0, le=1, description="Gender: 0=Female, 1=Male")
    bmi: float = Field(..., ge=10, le=80, description="Body Mass Index")
    blood_pressure: float = Field(..., ge=60, le=250, description="Systolic blood pressure")
    cholesterol_level: float = Field(..., ge=50, le=500, description="Total cholesterol level")
    glucose_level: float = Field(..., ge=50, le=500, description="Fasting glucose level")
    physical_activity: float = Field(..., ge=0, le=10, description="Physical activity level (0-10)")
    smoking_status: int = Field(..., ge=0, le=2, description="Smoking status: 0=Never, 1=Former, 2=Current")
    alcohol_intake: int = Field(..., ge=0, le=2, description="Alcohol intake: 0=None, 1=Moderate, 2=Heavy")
    family_history: int = Field(..., ge=0, le=1, description="Family history: 0=No, 1=Yes")
    hba1c: Optional[float] = Field(None, ge=3.0, le=20.0, description="HbA1c level (optional)")
    daily_steps: Optional[int] = Field(None, ge=0, le=50000, description="Daily steps (optional)")
    sleep_hours: Optional[float] = Field(None, ge=0, le=24, description="Sleep hours per night (optional)")
    sleep_quality: Optional[int] = Field(None, ge=1, le=10, description="Sleep quality (1-10, optional)")
    stress_level: Optional[int] = Field(None, ge=1, le=10, description="Stress level (1-10, optional)")

# Prediction Response Model
class PredictionResponse(BaseModel):
    """Enhanced prediction response with realistic confidence levels"""
    diabetes_risk: float = Field(..., description="Diabetes risk percentage")
    hypertension_risk: float = Field(..., description="Hypertension risk percentage")
    diabetes_confidence: str = Field(..., description="Confidence level for diabetes prediction")
    hypertension_confidence: str = Field(..., description="Confidence level for hypertension prediction")
    metabolic_health_score: float = Field(..., description="Metabolic health score (0-100)")
    cardiovascular_health_score: float = Field(..., description="Cardiovascular health score (0-100)")
    personalized_recommendations: Dict[str, Any] = Field(..., description="Personalized recommendations")
    comprehensive_analysis: Dict[str, Any] = Field(..., description="Comprehensive health analysis")
    timestamp: str = Field(..., description="Prediction timestamp")

# Recent Assessment Model
class RecentAssessment(BaseModel):
    """Model for recent assessment data"""
    id: str
    date: str
    diabetes_risk: float
    hypertension_risk: float
    metabolic_health_score: float
    cardiovascular_health_score: float
    overall_score: float
    risk_category_diabetes: str
    risk_category_hypertension: str
    input_data: Optional[Dict[str, Any]] = None

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(tracking_router, prefix="/tracking", tags=["Health Tracking"])

# Global variables for models
diabetes_model = None
hypertension_model = None
feature_scaler = None
fitness_recommendations = None
nutrition_recommendations = None
model_features = None

def load_models():
    """Load ML models and preprocessors"""
    global diabetes_model, hypertension_model, feature_scaler, fitness_recommendations, nutrition_recommendations, model_features
    
    try:
        logger.info("Loading optimized models and preprocessors...")
        
        # Load models
        diabetes_model = joblib.load('diabetes_model_optimized.joblib')
        hypertension_model = joblib.load('hypertension_model_optimized.joblib')
        feature_scaler = joblib.load('feature_scaler_optimized.joblib')
        fitness_recommendations = joblib.load('fitness_recommendations.joblib')
        nutrition_recommendations = joblib.load('nutrition_recommendations.joblib')
        model_features = joblib.load('model_features_optimized.joblib')
        
        logger.info("Optimized models loaded successfully. Features: 18")
        logger.info(f"Model types: Diabetes={type(diabetes_model).__name__}, Hypertension={type(hypertension_model).__name__}")
        
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        raise

# Load models on startup
load_models()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PreventiX Advanced API - Clean Version",
        "version": "3.0.0",
        "status": "active",
        "features": [
            "Health Risk Prediction",
            "Personalized Recommendations", 
            "Health Tracking",
            "PDF Reports"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": {
            "diabetes_model": diabetes_model is not None,
            "hypertension_model": hypertension_model is not None,
            "feature_scaler": feature_scaler is not None
        }
    }

@app.get("/features")
async def get_features():
    """Get available features for health assessment"""
    return {
        "features": [
            "age", "gender", "bmi", "blood_pressure", "cholesterol_level",
            "glucose_level", "physical_activity", "smoking_status", 
            "alcohol_intake", "family_history", "hba1c", "daily_steps",
            "sleep_hours", "sleep_quality", "stress_level"
        ],
        "total_features": 15,
        "required_features": 10,
        "optional_features": 5
    }

# Include the rest of the essential endpoints from the original file
# (prediction, recent assessments, etc.)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
