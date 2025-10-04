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
    title="PreventiX Advanced API - Optimized",
    description="AI-powered health risk prediction with personalized recommendations (Anti-overfitting optimized)",
    version="2.1.0"
)

# NOW add the exception handler
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PreventiX Advanced API - Optimized",
    description="AI-powered health risk prediction with personalized recommendations (Anti-overfitting optimized)",
    version="2.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication router
app.include_router(auth_router)
app.include_router(tracking_router) 

# Global variables for models and preprocessors
diabetes_model = None
hypertension_model = None
model_features = None
feature_scaler = None
diabetes_explainer = None
hypertension_explainer = None
nutrition_recommendations = None
fitness_recommendations = None

class HealthInput(BaseModel):
    """Comprehensive health input model - Updated for optimized features"""
    # Basic demographics
    age: float = Field(..., ge=0, le=120, description="Age in years")
    gender: float = Field(..., ge=0, le=1, description="Gender (0=Female, 1=Male)")
    
    # Vital signs and measurements
    bmi: float = Field(..., ge=10, le=60, description="Body Mass Index")
    blood_pressure: float = Field(..., ge=80, le=200, description="Systolic blood pressure (mmHg)")
    
    # Blood markers
    cholesterol_level: float = Field(..., ge=100, le=400, description="Total cholesterol (mg/dL)")
    glucose_level: float = Field(..., ge=50, le=300, description="Fasting glucose (mg/dL)")
    
    # Lifestyle factors
    physical_activity: float = Field(..., ge=0, le=10, description="Physical activity level (0-10)")
    smoking_status: float = Field(..., ge=0, le=2, description="Smoking (0=Never, 1=Former, 2=Current)")
    alcohol_intake: float = Field(..., ge=0, le=5, description="Alcohol intake level (0-5)")
    
    # Family history
    family_history: float = Field(..., ge=0, le=1, description="Family history of diabetes/hypertension")
    
    # Optional advanced blood markers
    hba1c: Optional[float] = Field(None, ge=3.0, le=15, description="HbA1c percentage")
    fasting_glucose: Optional[float] = Field(None, ge=50, le=300, description="Alternative fasting glucose measurement")
    
    # Optional fitness and lifestyle metrics
    daily_steps: Optional[float] = Field(7000, ge=0, le=50000, description="Average daily steps")
    sleep_hours: Optional[float] = Field(7, ge=0, le=12, description="Average sleep hours per night")
    sleep_quality: Optional[float] = Field(6, ge=0, le=10, description="Sleep quality rating (0-10)")
    stress_level: Optional[float] = Field(5, ge=0, le=10, description="Stress level rating (0-10)")
    
    # New tracking features
    daily_calories: Optional[float] = Field(2000, ge=500, le=5000, description="Daily calorie intake")
    gym_hours: Optional[float] = Field(0, ge=0, le=8, description="Weekly gym/workout hours")
    walking_steps: Optional[float] = Field(7000, ge=0, le=50000, description="Daily walking steps")
    protein_intake: Optional[float] = Field(50, ge=0, le=300, description="Daily protein intake in grams")
    water_intake: Optional[float] = Field(8, ge=0, le=20, description="Daily water intake in glasses")
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 45,
                "gender": 1,
                "bmi": 28.5,
                "blood_pressure": 135,
                "cholesterol_level": 210,
                "glucose_level": 110,
                "physical_activity": 3,
                "smoking_status": 0,
                "alcohol_intake": 1,
                "family_history": 1,
                "hba1c": 6.2,
                "daily_steps": 6000,
                "sleep_hours": 6.5,
                "stress_level": 7
            }
        }

class PredictionResponse(BaseModel):
    """Enhanced prediction response with realistic confidence levels"""
    # Risk scores and confidence
    diabetes_risk: float
    hypertension_risk: float
    diabetes_confidence: str
    hypertension_confidence: str
    
    # Risk categories
    risk_category_diabetes: str
    risk_category_hypertension: str
    
    # SHAP explanations
    diabetes_shap_values: Dict[str, Any]
    hypertension_shap_values: Dict[str, Any]
    
    # Personalized recommendations
    nutrition_recommendations: Dict[str, List[str]]
    fitness_recommendations: Dict[str, List[str]]
    lifestyle_recommendations: List[str]
    
    # Top risk factors
    top_diabetes_factors: List[Dict[str, Any]]
    top_hypertension_factors: List[Dict[str, Any]]
    
    # Health scores
    metabolic_health_score: float
    cardiovascular_health_score: float
    
    # Model information (renamed to avoid protected namespace)
    model_details: Dict[str, str]
    
    # New enhanced features
    contribution_percentages: Dict[str, Dict[str, float]]
    reasoning_explanations: List[str]
    gamification_points: int
    personalized_insights: List[str]
    
    class Config:
        protected_namespaces = ()


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

# New Q&A Models
class HealthQuestion(BaseModel):
    """Model for health questions"""
    question: str = Field(..., min_length=5, max_length=500, description="User's health question")
    health_data: Optional[Dict[str, Any]] = Field(None, description="User's health assessment data for context")

class HealthAnswer(BaseModel):
    """Model for AI-generated health answers"""
    answer: str = Field(..., description="AI-generated personalized answer")
    confidence: str = Field(..., description="Confidence level (High/Medium/Low)")
    related_factors: List[str] = Field(..., description="Related health factors mentioned")
    follow_up_suggestions: List[str] = Field(..., description="Follow-up suggestions")
    disclaimer: str = Field(..., description="Medical disclaimer")

def safe_float_conversion(value: Any) -> float:
    """Safely convert any value to float for serialization"""
    try:
        if isinstance(value, (np.integer, np.floating)):
            return float(value)
        elif isinstance(value, (int, float)):
            return float(value)
        else:
            return float(str(value))
    except (ValueError, TypeError):
        return 0.0

def safe_convert_dict_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """Safely convert all values in a dictionary to serializable types"""
    converted = {}
    for key, value in data.items():
        if isinstance(value, dict):
            converted[key] = safe_convert_dict_values(value)
        elif isinstance(value, list):
            converted[key] = [safe_float_conversion(item) if isinstance(item, (np.integer, np.floating)) else item for item in value]
        elif isinstance(value, (np.integer, np.floating)):
            converted[key] = safe_float_conversion(value)
        else:
            converted[key] = value
    return converted

def load_models():
    """Load ML models and preprocessors"""
    global diabetes_model, hypertension_model, model_features
    global feature_scaler, diabetes_explainer, hypertension_explainer
    global nutrition_recommendations, fitness_recommendations
    
    try:
        logger.info("Loading optimized models and preprocessors...")
        
        # Load optimized models
        diabetes_model = joblib.load('diabetes_model_optimized.joblib')
        hypertension_model = joblib.load('hypertension_model_optimized.joblib')
        model_features = joblib.load('model_features_optimized.joblib')
        
        # Load preprocessors
        try:
            feature_scaler = joblib.load('feature_scaler_optimized.joblib')
        except FileNotFoundError:
            logger.warning("Optimized scaler not found, trying fallback")
            try:
                feature_scaler = joblib.load('feature_scaler.joblib')
            except FileNotFoundError:
                logger.warning("No scaler found, will use raw features")
                feature_scaler = None
        
        # Load recommendations
        try:
            nutrition_recommendations = joblib.load('nutrition_recommendations.joblib')
            fitness_recommendations = joblib.load('fitness_recommendations.joblib')
        except FileNotFoundError:
            logger.warning("Recommendations not found, using defaults")
            nutrition_recommendations = {}
            fitness_recommendations = {}
        
        # Create SHAP explainers for tree-based models
        logger.info("Creating SHAP explainers...")
        try:
            if hasattr(diabetes_model, 'predict_proba'):
                diabetes_explainer = shap.TreeExplainer(diabetes_model)
                hypertension_explainer = shap.TreeExplainer(hypertension_model)
            else:
                diabetes_explainer = None
                hypertension_explainer = None
                logger.info("Using simplified explanations for non-tree models")
        except Exception as e:
            logger.warning(f"Could not create SHAP explainers: {e}")
            diabetes_explainer = None
            hypertension_explainer = None
        
        logger.info(f"Optimized models loaded successfully. Features: {len(model_features)}")
        logger.info(f"Model types: Diabetes={type(diabetes_model).__name__}, Hypertension={type(hypertension_model).__name__}")
        
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        logger.warning("Please run the optimized train_pipeline.py first to generate all required files")

# Load models on startup
load_models()


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Welcome to PreventiX Advanced API - Optimized Version",
        "version": "2.1.0",
        "features": {
            "anti_overfitting": "Strong regularization and realistic predictions",
            "model_selection": "Automatic best model selection",
            "confidence_scoring": "Realistic confidence levels",
            "personalized_recommendations": "Based on individual risk factors"
        },
        "endpoints": {
            "/auth/register": "POST - Register new user",
            "/auth/login": "POST - Login user",
            "/predict": "POST - Get comprehensive health risk predictions",
            "/health": "GET - Check API health status",
            "/features": "GET - Get list of model features",
            "/recommendations": "GET - Get general health recommendations",
            "/docs": "GET - Interactive API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    models_loaded = all([
        diabetes_model is not None,
        hypertension_model is not None,
        model_features is not None
    ])
    
    explainers_loaded = all([
        diabetes_explainer is not None,
        hypertension_explainer is not None
    ]) if diabetes_explainer is not None else False
    
    return {
        "status": "healthy" if models_loaded else "models_not_loaded",
        "models_loaded": models_loaded,
        "scaler_loaded": feature_scaler is not None,
        "explainers_loaded": explainers_loaded,
        "features_count": len(model_features) if model_features else 0,
        "model_types": {
            "diabetes": type(diabetes_model).__name__ if diabetes_model else None,
            "hypertension": type(hypertension_model).__name__ if hypertension_model else None
        },
        "sample_features": model_features[:10] if model_features else [],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/features")
async def get_features():
    """Get list of model features and their information"""
    if model_features is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    # Updated feature info based on optimized model
    feature_info = {
        "required_features": [
            "age", "gender", "bmi", "blood_pressure", 
            "cholesterol_level", "glucose_level", 
            "physical_activity", "smoking_status",
            "alcohol_intake", "family_history"
        ],
        "optional_features": [
            "hba1c", "fasting_glucose", "daily_steps", 
            "sleep_hours", "sleep_quality", "stress_level"
        ],
        "engineered_features": [
            "metabolic_syndrome_score", "lifestyle_health_score"
        ],
        "all_model_features": model_features,
        "total_features": len(model_features),
        "feature_engineering_note": "Some features are automatically calculated from input values"
    }
    
    return feature_info

def get_confidence_level(probability: float, feature_quality: Dict) -> str:
    """Calculate confidence level based on probability and feature quality"""
    
    # Base confidence on probability range
    if probability < 0.2 or probability > 0.8:
        base_confidence = "High"
    elif probability < 0.35 or probability > 0.65:
        base_confidence = "Moderate"
    else:
        base_confidence = "Low"
    
    # Adjust based on key feature availability
    key_features_present = 0
    total_key_features = 4
    
    if feature_quality.get('glucose_level_quality', False):
        key_features_present += 1
    if feature_quality.get('bp_quality', False):
        key_features_present += 1
    if feature_quality.get('bmi_quality', False):
        key_features_present += 1
    if feature_quality.get('age_quality', False):
        key_features_present += 1
    
    feature_completeness = key_features_present / total_key_features
    
    if feature_completeness < 0.5:
        return "Low"
    elif feature_completeness < 0.75 and base_confidence == "High":
        return "Moderate"
    else:
        return base_confidence

def calculate_health_scores(features: Dict) -> Dict[str, float]:
    """Calculate metabolic and cardiovascular health scores with realistic ranges"""
    
    # Metabolic health score (0-100)
    metabolic_score = 100
    
    # More nuanced scoring with None checks
    glucose = features.get('glucose_level', 100)
    if glucose is not None and glucose > 126:  # Diabetic range
        metabolic_score -= 30
    elif glucose is not None and glucose > 100:  # Prediabetic range
        metabolic_score -= 15
    
    bmi = features.get('bmi', 25)
    if bmi is not None and bmi > 35:  # Severe obesity
        metabolic_score -= 25
    elif bmi is not None and bmi > 30:  # Obesity
        metabolic_score -= 15
    elif bmi is not None and bmi > 25:  # Overweight
        metabolic_score -= 8
    
    hba1c = features.get('hba1c', 5.7)
    if hba1c is not None and hba1c > 6.5:  # Diabetic
        metabolic_score -= 20
    elif hba1c is not None and hba1c > 5.7:  # Prediabetic
        metabolic_score -= 10
    
    # Cardiovascular health score (0-100)
    cardio_score = 100
    
    bp = features.get('blood_pressure', 120)
    if bp is not None and bp > 140:  # Stage 1 hypertension
        cardio_score -= 25
    elif bp is not None and bp > 130:  # Elevated
        cardio_score -= 15
    elif bp is not None and bp > 120:  # Prehypertension
        cardio_score -= 8
    
    cholesterol = features.get('cholesterol_level', 200)
    if cholesterol is not None and cholesterol > 240:  # High
        cardio_score -= 20
    elif cholesterol is not None and cholesterol > 200:  # Borderline high
        cardio_score -= 10
    
    activity = features.get('physical_activity', 5)
    if activity is not None and activity < 3:
        cardio_score -= 15
    elif activity is not None and activity < 5:
        cardio_score -= 8
    
    smoking = features.get('smoking_status', 0)
    if smoking is not None and smoking == 2:  # Current smoker
        cardio_score -= 20
    elif smoking is not None and smoking == 1:  # Former smoker
        cardio_score -= 5
    
    return {
        'metabolic': max(0, min(100, metabolic_score)),
        'cardiovascular': max(0, min(100, cardio_score))
    }

def get_risk_category(probability: float) -> str:
    """Categorize risk level with more realistic thresholds"""
    if probability < 0.25:
        return "Low Risk"
    elif probability < 0.50:
        return "Moderate Risk"
    elif probability < 0.75:
        return "High Risk"
    else:
        return "Very High Risk"

def prepare_features(health_input: HealthInput) -> tuple[pd.DataFrame, Dict]:
    """Prepare input features for optimized model prediction"""
    
    # Convert input to dictionary
    input_dict = health_input.dict()
    
    # Set defaults for optional features based on optimized model
    if input_dict.get('hba1c') is None:
        # Estimate HbA1c from glucose
        glucose = input_dict['glucose_level']
        if glucose < 100:
            input_dict['hba1c'] = 5.4
        elif glucose < 126:
            input_dict['hba1c'] = 5.9
        else:
            input_dict['hba1c'] = 7.2
    
    if input_dict.get('fasting_glucose') is None:
        input_dict['fasting_glucose'] = input_dict['glucose_level']
    
    # Set defaults for lifestyle features
    input_dict['daily_steps'] = input_dict.get('daily_steps', 7000)
    input_dict['sleep_hours'] = input_dict.get('sleep_hours', 7)
    input_dict['sleep_quality'] = input_dict.get('sleep_quality', 6)
    input_dict['stress_level'] = input_dict.get('stress_level', 5)
    
    # Calculate composite scores (matching training pipeline)
    metabolic_factors = 0
    if input_dict['bmi'] > 30:
        metabolic_factors += 0.25
    if input_dict['glucose_level'] > 100:
        metabolic_factors += 0.25
    if input_dict['cholesterol_level'] > 200:
        metabolic_factors += 0.25
    if input_dict['blood_pressure'] > 120:
        metabolic_factors += 0.25
    
    input_dict['metabolic_syndrome_score'] = metabolic_factors
    
    lifestyle_factors = 0
    if input_dict['physical_activity'] < 3:
        lifestyle_factors += 0.33
    if input_dict['smoking_status'] > 0:
        lifestyle_factors += 0.33
    if input_dict['alcohol_intake'] > 2:
        lifestyle_factors += 0.34
    
    input_dict['lifestyle_health_score'] = min(1.0, lifestyle_factors)
    
    # Create DataFrame with only the features used in the optimized model
    features_df = pd.DataFrame([input_dict])
    
    # Ensure all model features are present
    for feature in model_features:
        if feature not in features_df.columns:
            # Set reasonable defaults for any missing engineered features
            features_df[feature] = 0
    
    # Calculate feature quality metrics
    feature_quality = {
        'glucose_level_quality': 50 <= input_dict['glucose_level'] <= 300,
        'bp_quality': 80 <= input_dict['blood_pressure'] <= 200,
        'bmi_quality': 15 <= input_dict['bmi'] <= 50,
        'age_quality': 18 <= input_dict['age'] <= 100
    }
    
    return features_df[model_features], feature_quality

def get_personalized_recommendations(
    feature_importance: List[tuple],
    input_values: Dict,
    risk_type: str,
    risk_level: float
) -> Dict[str, List[str]]:
    """Get highly personalized recommendations based on user's specific profile and risk factors"""
    
    recommendations = {
        'nutrition': [],
        'fitness': [],
        'lifestyle': []
    }
    
    # Extract user profile for personalization
    age = input_values.get('age', 45)
    gender = input_values.get('gender', 0)
    bmi = input_values.get('bmi', 25)
    blood_pressure = input_values.get('blood_pressure', 120)
    glucose = input_values.get('glucose_level', 100)
    cholesterol = input_values.get('cholesterol_level', 200)
    activity = input_values.get('physical_activity', 5)
    smoking = input_values.get('smoking_status', 0)
    family_history = input_values.get('family_history', 0)
    hba1c = input_values.get('hba1c', 5.7)
    
    # Get top 3 contributing factors
    top_factors = [factor for factor, _ in feature_importance[:3]]
    
    if risk_type == 'diabetes':
        # Highly personalized glucose management
        if any('glucose' in factor for factor in top_factors):
            if glucose >= 200:
                recommendations['nutrition'].extend([
                    f"Your glucose of {glucose} mg/dL requires immediate attention. Focus on very low-carb meals (under 30g carbs per meal)",
                    "Eliminate all sugary drinks and processed foods immediately",
                    "Work with a diabetes educator to learn carbohydrate counting",
                    "Consider a continuous glucose monitor for better tracking"
                ])
            elif glucose >= 126:
                recommendations['nutrition'].extend([
                    f"Your glucose of {glucose} mg/dL indicates diabetes. Follow a consistent carb-controlled diet",
                    "Aim for 45-60g carbs per meal with protein and healthy fats",
                    "Choose low glycemic index foods like quinoa, sweet potatoes, and berries",
                    "Eat at regular intervals to maintain stable blood sugar"
                ])
            elif glucose >= 100:
                recommendations['nutrition'].extend([
                    f"Your glucose of {glucose} mg/dL is in pre-diabetes range. Focus on portion control and timing",
                    "Limit refined carbs and increase fiber intake to 25-30g daily",
                    "Use the plate method: 1/2 non-starchy vegetables, 1/4 lean protein, 1/4 whole grains",
                    "Consider intermittent fasting with medical supervision"
                ])
            else:
                recommendations['nutrition'].extend([
                    f"Your glucose of {glucose} mg/dL is excellent! Maintain your current healthy eating habits",
                    "Continue with balanced meals and regular eating schedule",
                    "Keep monitoring to maintain these healthy levels"
                ])
            
        # Personalized BMI and weight management
        if 'bmi' in top_factors:
            if bmi >= 35:
                recommendations['nutrition'].extend([
                    f"Your BMI of {bmi:.1f} indicates severe obesity. Focus on sustainable weight loss of 1-2 lbs per week",
                    "Create a 500-750 calorie daily deficit through diet and exercise",
                    "Focus on high-protein, high-fiber foods to feel full longer",
                    "Consider working with a registered dietitian for personalized meal planning"
                ])
                recommendations['fitness'].extend([
                    "Start with low-impact exercises like walking, swimming, or cycling",
                    "Aim for 30 minutes of activity daily, even if broken into 10-minute sessions",
                    "Include strength training 2-3 times per week to preserve muscle mass",
                    "Consider working with a certified trainer who specializes in obesity management"
                ])
            elif bmi >= 30:
                recommendations['nutrition'].extend([
                    f"Your BMI of {bmi:.1f} puts you in the obese category. Focus on gradual, sustainable weight loss",
                    "Create a 300-500 calorie daily deficit for steady 1 lb per week weight loss",
                    "Focus on whole foods and limit processed foods",
                    "Use smaller plates and practice mindful eating"
                ])
                recommendations['fitness'].extend([
                    "Aim for 150 minutes of moderate exercise weekly, building up gradually",
                    "Include both cardio and strength training for optimal results",
                    "Find activities you enjoy to maintain long-term consistency",
                    "Consider group fitness classes for motivation and support"
                ])
            elif bmi >= 25:
                recommendations['nutrition'].extend([
                    f"Your BMI of {bmi:.1f} is slightly above optimal. Small changes can make a big difference",
                    "Focus on portion control and reducing calorie-dense foods",
                    "Increase vegetable and lean protein intake",
                    "Limit alcohol and sugary beverages"
                ])
                recommendations['fitness'].extend([
                    "Aim for 30 minutes of moderate exercise most days of the week",
                    "Include both aerobic and strength training",
                    "Take the stairs, park farther away, and find ways to be more active daily"
                ])
            else:
                recommendations['nutrition'].extend([
                    f"Your BMI of {bmi:.1f} is in the healthy range! Maintain your current habits",
                    "Continue with balanced nutrition and regular eating patterns",
                    "Focus on nutrient density rather than weight management"
                ])
                recommendations['fitness'].extend([
                    "Maintain your current activity level - you're doing great!",
                    "Consider adding variety to prevent boredom and plateaus",
                    "Focus on strength training to maintain muscle mass as you age"
                ])
            
        # Age and gender-specific recommendations
        if age >= 65:
            recommendations['lifestyle'].extend([
                "At your age, focus on maintaining muscle mass and bone density",
                "Consider working with a geriatric specialist for age-appropriate care",
                "Regular health screenings become even more important"
            ])
        elif age >= 45:
            recommendations['lifestyle'].extend([
                "You're in a critical prevention window - lifestyle changes now have maximum impact",
                "Focus on stress management and quality sleep",
                "Regular health checkups and monitoring are essential"
            ])
        
        # Gender-specific recommendations
        if gender == 0:  # Female
            recommendations['lifestyle'].extend([
                "Women have unique risk factors - consider hormonal influences on blood sugar",
                "If you're considering pregnancy, optimal glucose control is crucial",
                "Regular gynecological care and bone density monitoring are important"
            ])
        else:  # Male
            recommendations['lifestyle'].extend([
                "Men often develop diabetes at lower BMIs - focus on abdominal fat reduction",
                "Regular prostate and cardiovascular screenings are important",
                "Consider testosterone levels if experiencing fatigue or low energy"
            ])
    
    elif risk_type == 'hypertension':
        # Highly personalized blood pressure management
        if 'blood_pressure' in top_factors:
            if blood_pressure >= 180:
                recommendations['nutrition'].extend([
                    f"Your blood pressure of {blood_pressure} mmHg is critically high. Immediate medical attention required",
                    "Follow a strict low-sodium diet (under 1,500mg daily) with medical supervision",
                    "Focus on potassium-rich foods: bananas, spinach, sweet potatoes, and avocados",
                    "Eliminate all processed foods and restaurant meals immediately"
                ])
                recommendations['lifestyle'].extend([
                    "This is a medical emergency - contact your doctor immediately",
                    "Avoid all strenuous activities until blood pressure is controlled",
                    "Consider stress management techniques like meditation or deep breathing"
                ])
            elif blood_pressure >= 140:
                recommendations['nutrition'].extend([
                    f"Your blood pressure of {blood_pressure} mmHg is high. Follow DASH diet strictly",
                    "Limit sodium to under 2,300mg daily (ideally 1,500mg)",
                    "Increase potassium-rich foods: leafy greens, bananas, and citrus fruits",
                    "Choose fresh, whole foods over processed options"
                ])
                recommendations['fitness'].extend([
                    "Start with gentle exercises like walking or swimming",
                    "Avoid high-intensity activities until blood pressure is controlled",
                    "Aim for 30 minutes of moderate activity most days",
                    "Include stress-reducing activities like yoga or tai chi"
                ])
            elif blood_pressure >= 120:
                recommendations['nutrition'].extend([
                    f"Your blood pressure of {blood_pressure} mmHg is elevated. Focus on prevention",
                    "Limit sodium to under 2,300mg daily",
                    "Increase potassium and magnesium-rich foods",
                    "Choose heart-healthy fats like olive oil and nuts"
                ])
                recommendations['fitness'].extend([
                    "Aim for 150 minutes of moderate exercise weekly",
                    "Include both aerobic and strength training",
                    "Focus on stress management through regular exercise",
                    "Monitor blood pressure before and after exercise"
                ])
            else:
                recommendations['nutrition'].extend([
                    f"Your blood pressure of {blood_pressure} mmHg is excellent! Maintain your current habits",
                    "Continue with heart-healthy eating patterns",
                    "Keep monitoring to maintain these healthy levels"
                ])
                recommendations['fitness'].extend([
                    "Maintain your current activity level - you're doing great!",
                    "Continue with regular exercise for long-term heart health"
                ])
        
        # Age-specific hypertension management
        if age >= 65:
            recommendations['lifestyle'].extend([
                "At your age, blood pressure management becomes even more critical",
                "Consider more frequent monitoring and medication adjustments",
                "Focus on fall prevention and balance exercises"
            ])
        elif age >= 45:
            recommendations['lifestyle'].extend([
                "You're in a critical prevention window for cardiovascular health",
                "Regular blood pressure monitoring is essential",
                "Focus on stress management and quality sleep"
            ])
        
        # Gender-specific recommendations
        if gender == 0:  # Female
            recommendations['lifestyle'].extend([
                "Women's blood pressure can be affected by hormonal changes",
                "Consider pregnancy planning if applicable - blood pressure control is crucial",
                "Regular gynecological care and cardiovascular monitoring are important"
            ])
        else:  # Male
            recommendations['lifestyle'].extend([
                "Men often develop hypertension earlier - you're doing well to monitor this",
                "Regular cardiovascular screenings are important",
                "Consider testosterone levels if experiencing fatigue or low energy"
            ])
    
    # Activity level personalized recommendations
    if 'physical_activity' in top_factors:
        if activity <= 2:
            recommendations['fitness'].extend([
                f"Your activity level of {activity}/10 is very low. Start with just 10 minutes daily",
                "Begin with walking, gentle stretching, or chair exercises",
                "Gradually increase duration and intensity over several weeks",
                "Consider working with a physical therapist if you have mobility issues"
            ])
        elif activity <= 4:
            recommendations['fitness'].extend([
                f"Your activity level of {activity}/10 is below optimal. Build up gradually",
                "Aim for 30 minutes of moderate activity most days",
                "Include both cardio and strength training",
                "Find activities you enjoy to maintain consistency"
            ])
        elif activity <= 7:
            recommendations['fitness'].extend([
                f"Your activity level of {activity}/10 is good. Consider adding variety",
                "Include both aerobic and strength training",
                "Try new activities to prevent boredom",
                "Focus on consistency rather than intensity"
            ])
        else:
            recommendations['fitness'].extend([
                f"Your activity level of {activity}/10 is excellent! Maintain your current routine",
                "Consider adding variety to prevent overuse injuries",
                "Focus on recovery and proper nutrition to support your activity level"
            ])
    
    # Smoking status personalized recommendations
    if smoking == 2:  # Current smoker
        recommendations['lifestyle'].extend([
            "Quitting smoking is the single most important step for your health",
            "Consider nicotine replacement therapy or prescription medications",
            "Join a smoking cessation program for support",
            "Your risk of heart disease and stroke will decrease significantly after quitting"
        ])
    elif smoking == 1:  # Former smoker
        recommendations['lifestyle'].extend([
            "Congratulations on quitting smoking! Your risk continues to decrease over time",
            "Stay vigilant about not relapsing - you've made excellent progress",
            "Your lung function and cardiovascular health will continue to improve"
        ])
    else:
        recommendations['lifestyle'].extend([
            "Excellent job staying smoke-free! This significantly reduces your health risks",
            "Continue to avoid secondhand smoke exposure",
            "Your healthy choice is protecting your heart and lungs"
        ])
    
    # Family history personalized recommendations
    if family_history:
        recommendations['lifestyle'].extend([
            "Given your family history, you have a higher genetic risk",
            "Focus on controllable factors like diet, exercise, and regular checkups",
            "Consider more frequent health screenings",
            "Work closely with your healthcare provider to monitor your health"
        ])
    else:
        recommendations['lifestyle'].extend([
            "With no family history, you have a genetic advantage",
            "Focus on maintaining healthy lifestyle habits to preserve this advantage",
            "Regular health checkups are still important for prevention"
        ])
    
    return recommendations

def get_simple_feature_importance(model, feature_names: List[str], input_values: np.ndarray) -> List[tuple]:
    """Get feature importance for non-tree models"""
    if hasattr(model, 'feature_importances_'):
        # Tree-based models
        importance = list(zip(feature_names, model.feature_importances_))
    elif hasattr(model, 'coef_'):
        # Linear models
        importance = list(zip(feature_names, abs(model.coef_[0])))
    else:
        # Fallback - uniform importance
        importance = list(zip(feature_names, [1.0/len(feature_names)] * len(feature_names)))
    
    return sorted(importance, key=lambda x: x[1], reverse=True)

def calculate_contribution_percentages(feature_importance: List[tuple]) -> Dict[str, float]:
    """Calculate percentage contribution of each factor to the risk"""
    total_importance = sum(imp for _, imp in feature_importance)
    contributions = {}
    
    for feature, importance in feature_importance:
        percentage = (importance / total_importance) * 100 if total_importance > 0 else 0
        contributions[feature] = round(percentage, 1)
    
    return contributions

def safe_compare(value, operator, threshold):
    """Safely compare a value with a threshold, handling None values"""
    if value is None:
        return False
    if operator == '>=':
        return value >= threshold
    elif operator == '>':
        return value > threshold
    elif operator == '<=':
        return value <= threshold
    elif operator == '<':
        return value < threshold
    elif operator == '==':
        return value == threshold
    return False

def analyze_comprehensive_risk_factors(input_data: Dict[str, Any], diabetes_proba: float, hypertension_proba: float) -> Dict[str, Any]:
    """Comprehensive analysis of all risk factors influencing diabetes and hypertension"""
    
    # Extract all input parameters with safe defaults
    age = input_data.get('age')
    gender = input_data.get('gender')
    bmi = input_data.get('bmi')
    blood_pressure = input_data.get('blood_pressure')
    cholesterol = input_data.get('cholesterol_level')
    glucose = input_data.get('glucose_level')
    physical_activity = input_data.get('physical_activity')
    smoking = input_data.get('smoking_status')
    alcohol = input_data.get('alcohol_intake')
    family_history = input_data.get('family_history')
    hba1c = input_data.get('hba1c')
    daily_steps = input_data.get('daily_steps')
    sleep_hours = input_data.get('sleep_hours')
    sleep_quality = input_data.get('sleep_quality')
    stress_level = input_data.get('stress_level')
    
    # Comprehensive risk factor analysis
    risk_analysis = {
        "diabetes_risk_factors": analyze_diabetes_risk_factors(
            age, gender, bmi, glucose, hba1c, physical_activity, 
            smoking, alcohol, family_history, blood_pressure, cholesterol,
            daily_steps, sleep_hours, sleep_quality, stress_level, diabetes_proba
        ),
        "hypertension_risk_factors": analyze_hypertension_risk_factors(
            age, gender, bmi, blood_pressure, cholesterol, physical_activity,
            smoking, alcohol, family_history, glucose, daily_steps, 
            sleep_hours, sleep_quality, stress_level, hypertension_proba
        ),
        "metabolic_health_analysis": analyze_metabolic_health(
            bmi, glucose, hba1c, cholesterol, blood_pressure, physical_activity,
            daily_steps, sleep_hours, stress_level
        ),
        "cardiovascular_health_analysis": analyze_cardiovascular_health(
            age, gender, blood_pressure, cholesterol, bmi, physical_activity,
            smoking, alcohol, stress_level, sleep_hours
        ),
        "lifestyle_impact_analysis": analyze_lifestyle_impact(
            physical_activity, daily_steps, sleep_hours, sleep_quality,
            stress_level, smoking, alcohol, bmi, glucose, blood_pressure
        ),
        "age_gender_considerations": analyze_age_gender_considerations(
            age, gender, diabetes_proba, hypertension_proba, bmi, blood_pressure
        )
    }
    
    return risk_analysis

def analyze_diabetes_risk_factors(age, gender, bmi, glucose, hba1c, physical_activity, 
                                smoking, alcohol, family_history, blood_pressure, cholesterol,
                                daily_steps, sleep_hours, sleep_quality, stress_level, diabetes_proba):
    """Detailed analysis of diabetes risk factors"""
    
    risk_factors = []
    protective_factors = []
    critical_concerns = []
    moderate_concerns = []
    
    # Age and Gender Analysis
    if safe_compare(age, '>', 45):
        risk_factors.append({
            "factor": "Age",
            "value": f"{age} years",
            "impact": "High",
            "explanation": f"At {age} years, you're in the high-risk age group for diabetes. Risk increases significantly after 45.",
            "recommendation": "Focus on preventive measures and regular screening"
        })
    
    if safe_compare(gender, '==', 1) and safe_compare(bmi, '>', 25):  # Male with higher BMI
        risk_factors.append({
            "factor": "Gender + BMI",
            "value": f"Male, BMI {bmi:.1f}",
            "impact": "High",
            "explanation": "Men develop diabetes at lower BMIs than women. Your current BMI puts you at elevated risk.",
            "recommendation": "Target BMI below 25, focus on abdominal fat reduction"
        })
    
    # Glucose and HbA1c Analysis
    if safe_compare(glucose, '>=', 126):
        critical_concerns.append({
            "factor": "Fasting Glucose",
            "value": f"{glucose} mg/dL",
            "impact": "Critical",
            "explanation": "Fasting glucose ≥126 mg/dL indicates diabetes. Immediate medical attention required.",
            "recommendation": "Consult healthcare provider immediately for diabetes management"
        })
    elif safe_compare(glucose, '>=', 100):
        moderate_concerns.append({
            "factor": "Fasting Glucose",
            "value": f"{glucose} mg/dL",
            "impact": "Moderate",
            "explanation": "Fasting glucose 100-125 mg/dL indicates prediabetes. High risk of developing diabetes.",
            "recommendation": "Implement lifestyle changes immediately to prevent progression"
        })
    elif glucose is not None:
        protective_factors.append({
            "factor": "Fasting Glucose",
            "value": f"{glucose} mg/dL",
            "impact": "Protective",
            "explanation": "Normal fasting glucose levels. Continue maintaining healthy lifestyle.",
            "recommendation": "Maintain current healthy habits"
        })
    
    if safe_compare(hba1c, '>=', 6.5):
        critical_concerns.append({
            "factor": "HbA1c",
            "value": f"{hba1c:.1f}%",
            "impact": "Critical",
            "explanation": "HbA1c ≥6.5% indicates diabetes. This reflects average blood sugar over 2-3 months.",
            "recommendation": "Immediate diabetes management required"
        })
    elif safe_compare(hba1c, '>=', 5.7):
        moderate_concerns.append({
            "factor": "HbA1c",
            "value": f"{hba1c:.1f}%",
            "impact": "Moderate",
            "explanation": "HbA1c 5.7-6.4% indicates prediabetes. Elevated risk of diabetes development.",
            "recommendation": "Focus on blood sugar control and weight management"
        })
    
    # BMI Analysis
    if safe_compare(bmi, '>=', 30):
        risk_factors.append({
            "factor": "Obesity",
            "value": f"BMI {bmi:.1f}",
            "impact": "High",
            "explanation": "Obesity (BMI ≥30) is a major diabetes risk factor. Adipose tissue affects insulin sensitivity.",
            "recommendation": "Target 5-10% weight loss for significant diabetes risk reduction"
        })
    elif safe_compare(bmi, '>=', 25):
        moderate_concerns.append({
            "factor": "Overweight",
            "value": f"BMI {bmi:.1f}",
            "impact": "Moderate",
            "explanation": "Overweight status increases diabetes risk, especially with other risk factors.",
            "recommendation": "Aim for BMI below 25 through diet and exercise"
        })
    
    # Physical Activity Analysis
    if safe_compare(physical_activity, '<', 3):
        risk_factors.append({
            "factor": "Physical Inactivity",
            "value": f"{physical_activity}/10",
            "impact": "High",
            "explanation": "Low physical activity reduces insulin sensitivity and increases diabetes risk.",
            "recommendation": "Aim for 150+ minutes moderate exercise weekly"
        })
    elif safe_compare(physical_activity, '>=', 7):
        protective_factors.append({
            "factor": "High Physical Activity",
            "value": f"{physical_activity}/10",
            "impact": "Protective",
            "explanation": "Regular exercise improves insulin sensitivity and reduces diabetes risk.",
            "recommendation": "Continue current activity level"
        })
    
    # Family History
    if safe_compare(family_history, '==', 1):
        risk_factors.append({
            "factor": "Family History",
            "value": "Present",
            "impact": "High",
            "explanation": "Family history of diabetes significantly increases your risk, especially with other factors.",
            "recommendation": "Extra vigilance with lifestyle modifications and regular screening"
        })
    
    # Lifestyle Factors
    if safe_compare(smoking, '>', 0):
        risk_factors.append({
            "factor": "Smoking",
            "value": f"Status {smoking}",
            "impact": "Moderate",
            "explanation": "Smoking increases diabetes risk and complicates blood sugar control.",
            "recommendation": "Quit smoking to reduce diabetes risk"
        })
    
    if safe_compare(alcohol, '>', 3):
        moderate_concerns.append({
            "factor": "High Alcohol Intake",
            "value": f"{alcohol}/5",
            "impact": "Moderate",
            "explanation": "Excessive alcohol can affect blood sugar control and liver function.",
            "recommendation": "Limit alcohol to moderate levels (1-2 drinks/day)"
        })
    
    # Sleep and Stress Analysis
    if safe_compare(sleep_hours, '<', 6):
        risk_factors.append({
            "factor": "Insufficient Sleep",
            "value": f"{sleep_hours} hours",
            "impact": "Moderate",
            "explanation": "Poor sleep affects glucose metabolism and insulin sensitivity.",
            "recommendation": "Aim for 7-9 hours quality sleep nightly"
        })
    
    if safe_compare(stress_level, '>', 7):
        moderate_concerns.append({
            "factor": "High Stress",
            "value": f"{stress_level}/10",
            "impact": "Moderate",
            "explanation": "Chronic stress affects blood sugar control and increases diabetes risk.",
            "recommendation": "Implement stress management techniques"
        })
    
    return {
        "risk_factors": risk_factors,
        "protective_factors": protective_factors,
        "critical_concerns": critical_concerns,
        "moderate_concerns": moderate_concerns,
        "overall_risk_level": "Critical" if critical_concerns else "High" if risk_factors else "Moderate" if moderate_concerns else "Low"
    }

def analyze_hypertension_risk_factors(age, gender, bmi, blood_pressure, cholesterol, physical_activity,
                                     smoking, alcohol, family_history, glucose, daily_steps,
                                     sleep_hours, sleep_quality, stress_level, hypertension_proba):
    """Detailed analysis of hypertension risk factors"""
    
    risk_factors = []
    protective_factors = []
    critical_concerns = []
    moderate_concerns = []
    
    # Blood Pressure Analysis
    if safe_compare(blood_pressure, '>=', 140):
        critical_concerns.append({
            "factor": "Stage 1 Hypertension",
            "value": f"{blood_pressure} mmHg",
            "impact": "Critical",
            "explanation": "Systolic BP ≥140 mmHg indicates hypertension. Immediate attention required.",
            "recommendation": "Consult healthcare provider for blood pressure management"
        })
    elif safe_compare(blood_pressure, '>=', 130):
        moderate_concerns.append({
            "factor": "Elevated Blood Pressure",
            "value": f"{blood_pressure} mmHg",
            "impact": "Moderate",
            "explanation": "Systolic BP 130-139 mmHg indicates elevated blood pressure (Stage 1).",
            "recommendation": "Implement lifestyle changes to prevent progression"
        })
    elif blood_pressure is not None:
        protective_factors.append({
            "factor": "Normal Blood Pressure",
            "value": f"{blood_pressure} mmHg",
            "impact": "Protective",
            "explanation": "Blood pressure within normal range. Continue healthy lifestyle.",
            "recommendation": "Maintain current healthy habits"
        })
    
    # Age and Gender Analysis
    if safe_compare(age, '>', 55):
        risk_factors.append({
            "factor": "Age",
            "value": f"{age} years",
            "impact": "High",
            "explanation": f"At {age} years, you're in the high-risk age group for hypertension.",
            "recommendation": "Focus on blood pressure monitoring and prevention"
        })
    
    if safe_compare(gender, '==', 1) and safe_compare(age, '>', 45):  # Men over 45
        risk_factors.append({
            "factor": "Gender + Age",
            "value": f"Male, {age} years",
            "impact": "Moderate",
            "explanation": "Men have higher hypertension risk, especially after 45.",
            "recommendation": "Regular blood pressure monitoring recommended"
        })
    
    # BMI and Weight Analysis
    if safe_compare(bmi, '>=', 30):
        risk_factors.append({
            "factor": "Obesity",
            "value": f"BMI {bmi:.1f}",
            "impact": "High",
            "explanation": "Obesity significantly increases hypertension risk through multiple mechanisms.",
            "recommendation": "Weight loss of 5-10% can significantly reduce blood pressure"
        })
    elif safe_compare(bmi, '>=', 25):
        moderate_concerns.append({
            "factor": "Overweight",
            "value": f"BMI {bmi:.1f}",
            "impact": "Moderate",
            "explanation": "Overweight status increases hypertension risk.",
            "recommendation": "Aim for BMI below 25"
        })
    
    # Physical Activity Analysis
    if safe_compare(physical_activity, '<', 3):
        risk_factors.append({
            "factor": "Physical Inactivity",
            "value": f"{physical_activity}/10",
            "impact": "High",
            "explanation": "Low physical activity increases hypertension risk.",
            "recommendation": "Aim for 150+ minutes moderate exercise weekly"
        })
    elif safe_compare(physical_activity, '>=', 7):
        protective_factors.append({
            "factor": "High Physical Activity",
            "value": f"{physical_activity}/10",
            "impact": "Protective",
            "explanation": "Regular exercise helps maintain healthy blood pressure.",
            "recommendation": "Continue current activity level"
        })
    
    # Cholesterol Analysis
    if safe_compare(cholesterol, '>=', 240):
        risk_factors.append({
            "factor": "High Cholesterol",
            "value": f"{cholesterol} mg/dL",
            "impact": "High",
            "explanation": "High cholesterol contributes to arterial stiffness and hypertension.",
            "recommendation": "Focus on heart-healthy diet and cholesterol management"
        })
    elif safe_compare(cholesterol, '>=', 200):
        moderate_concerns.append({
            "factor": "Elevated Cholesterol",
            "value": f"{cholesterol} mg/dL",
            "impact": "Moderate",
            "explanation": "Borderline high cholesterol may contribute to hypertension risk.",
            "recommendation": "Monitor cholesterol and maintain heart-healthy diet"
        })
    
    # Lifestyle Factors
    if safe_compare(smoking, '>', 0):
        risk_factors.append({
            "factor": "Smoking",
            "value": f"Status {smoking}",
            "impact": "High",
            "explanation": "Smoking causes immediate blood pressure spikes and long-term damage.",
            "recommendation": "Quit smoking immediately to reduce hypertension risk"
        })
    
    if safe_compare(alcohol, '>', 3):
        moderate_concerns.append({
            "factor": "High Alcohol Intake",
            "value": f"{alcohol}/5",
            "impact": "Moderate",
            "explanation": "Excessive alcohol can raise blood pressure and interfere with medications.",
            "recommendation": "Limit alcohol to moderate levels"
        })
    
    # Stress and Sleep Analysis
    if safe_compare(stress_level, '>', 7):
        risk_factors.append({
            "factor": "High Stress",
            "value": f"{stress_level}/10",
            "impact": "High",
            "explanation": "Chronic stress significantly increases hypertension risk.",
            "recommendation": "Implement stress management techniques"
        })
    
    if safe_compare(sleep_hours, '<', 6):
        moderate_concerns.append({
            "factor": "Insufficient Sleep",
            "value": f"{sleep_hours} hours",
            "impact": "Moderate",
            "explanation": "Poor sleep affects blood pressure regulation.",
            "recommendation": "Aim for 7-9 hours quality sleep"
        })
    
    return {
        "risk_factors": risk_factors,
        "protective_factors": protective_factors,
        "critical_concerns": critical_concerns,
        "moderate_concerns": moderate_concerns,
        "overall_risk_level": "Critical" if critical_concerns else "High" if risk_factors else "Moderate" if moderate_concerns else "Low"
    }

def analyze_metabolic_health(bmi, glucose, hba1c, cholesterol, blood_pressure, physical_activity,
                           daily_steps, sleep_hours, stress_level):
    """Comprehensive metabolic health analysis"""
    
    metabolic_score = 100
    concerns = []
    strengths = []
    
    # BMI Impact
    if safe_compare(bmi, '>=', 30):
        metabolic_score -= 25
        concerns.append("Severe obesity significantly impacts metabolic health")
    elif safe_compare(bmi, '>=', 25):
        metabolic_score -= 10
        concerns.append("Overweight status affects metabolic efficiency")
    elif bmi is not None and 18.5 <= bmi <= 24.9:
        metabolic_score += 5
        strengths.append("Healthy BMI supports optimal metabolic function")
    
    # Glucose Metabolism
    if safe_compare(glucose, '>=', 126):
        metabolic_score -= 30
        concerns.append("Diabetic glucose levels indicate severe metabolic dysfunction")
    elif safe_compare(glucose, '>=', 100):
        metabolic_score -= 15
        concerns.append("Prediabetic glucose levels suggest metabolic stress")
    elif glucose is not None:
        strengths.append("Normal glucose levels indicate healthy metabolism")
    
    # HbA1c Analysis
    if safe_compare(hba1c, '>=', 6.5):
        metabolic_score -= 25
        concerns.append("Elevated HbA1c indicates poor long-term glucose control")
    elif safe_compare(hba1c, '>=', 5.7):
        metabolic_score -= 10
        concerns.append("Borderline HbA1c suggests metabolic stress")
    
    # Physical Activity Impact
    if safe_compare(physical_activity, '>=', 7):
        metabolic_score += 10
        strengths.append("High physical activity enhances metabolic efficiency")
    elif safe_compare(physical_activity, '<', 3):
        metabolic_score -= 15
        concerns.append("Low physical activity reduces metabolic health")
    
    # Sleep Impact
    if safe_compare(sleep_hours, '<', 6):
        metabolic_score -= 10
        concerns.append("Insufficient sleep disrupts metabolic hormones")
    elif sleep_hours is not None and 7 <= sleep_hours <= 9:
        strengths.append("Adequate sleep supports metabolic health")
    
    # Stress Impact
    if safe_compare(stress_level, '>', 7):
        metabolic_score -= 10
        concerns.append("High stress levels disrupt metabolic balance")
    
    return {
        "metabolic_score": max(0, min(100, metabolic_score)),
        "concerns": concerns,
        "strengths": strengths,
        "recommendations": [
            "Focus on weight management if BMI > 25",
            "Implement regular exercise routine",
            "Ensure adequate sleep (7-9 hours)",
            "Manage stress through relaxation techniques",
            "Monitor blood glucose regularly"
        ]
    }

def analyze_cardiovascular_health(age, gender, blood_pressure, cholesterol, bmi, physical_activity,
                                smoking, alcohol, stress_level, sleep_hours):
    """Comprehensive cardiovascular health analysis"""
    
    cardio_score = 100
    concerns = []
    strengths = []
    
    # Blood Pressure Impact
    if safe_compare(blood_pressure, '>=', 140):
        cardio_score -= 30
        concerns.append("Hypertension significantly increases cardiovascular risk")
    elif safe_compare(blood_pressure, '>=', 130):
        cardio_score -= 15
        concerns.append("Elevated blood pressure increases cardiovascular risk")
    elif blood_pressure is not None:
        strengths.append("Normal blood pressure supports cardiovascular health")
    
    # Cholesterol Impact
    if safe_compare(cholesterol, '>=', 240):
        cardio_score -= 20
        concerns.append("High cholesterol increases cardiovascular risk")
    elif safe_compare(cholesterol, '>=', 200):
        cardio_score -= 10
        concerns.append("Borderline high cholesterol may affect cardiovascular health")
    elif cholesterol is not None:
        strengths.append("Normal cholesterol levels support heart health")
    
    # BMI Impact
    if safe_compare(bmi, '>=', 30):
        cardio_score -= 20
        concerns.append("Obesity increases cardiovascular workload")
    elif safe_compare(bmi, '>=', 25):
        cardio_score -= 10
        concerns.append("Overweight status affects cardiovascular efficiency")
    
    # Physical Activity Impact
    if safe_compare(physical_activity, '>=', 7):
        cardio_score += 15
        strengths.append("Regular exercise strengthens cardiovascular system")
    elif safe_compare(physical_activity, '<', 3):
        cardio_score -= 20
        concerns.append("Physical inactivity weakens cardiovascular system")
    
    # Smoking Impact
    if safe_compare(smoking, '>', 0):
        cardio_score -= 25
        concerns.append("Smoking severely damages cardiovascular system")
    elif smoking is not None:
        strengths.append("Non-smoking status protects cardiovascular health")
    
    # Age and Gender Considerations
    if safe_compare(age, '>', 55):
        cardio_score -= 10
        concerns.append("Age increases cardiovascular risk")
    
    if safe_compare(gender, '==', 1) and safe_compare(age, '>', 45):
        concerns.append("Men have higher cardiovascular risk after 45")
    
    # Stress Impact
    if safe_compare(stress_level, '>', 7):
        cardio_score -= 10
        concerns.append("High stress increases cardiovascular risk")
    
    return {
        "cardiovascular_score": max(0, min(100, cardio_score)),
        "concerns": concerns,
        "strengths": strengths,
        "recommendations": [
            "Maintain blood pressure below 130/80 mmHg",
            "Keep cholesterol levels optimal",
            "Engage in regular cardiovascular exercise",
            "Avoid smoking and limit alcohol",
            "Manage stress effectively"
        ]
    }

def analyze_lifestyle_impact(physical_activity, daily_steps, sleep_hours, sleep_quality,
                           stress_level, smoking, alcohol, bmi, glucose, blood_pressure):
    """Comprehensive lifestyle impact analysis"""
    
    lifestyle_score = 100
    positive_factors = []
    negative_factors = []
    
    # Physical Activity Analysis
    if safe_compare(physical_activity, '>=', 7):
        lifestyle_score += 15
        positive_factors.append("Excellent physical activity level")
    elif safe_compare(physical_activity, '>=', 5):
        lifestyle_score += 5
        positive_factors.append("Good physical activity level")
    elif safe_compare(physical_activity, '<', 3):
        lifestyle_score -= 20
        negative_factors.append("Insufficient physical activity")
    
    # Daily Steps Analysis
    if safe_compare(daily_steps, '>=', 10000):
        lifestyle_score += 10
        positive_factors.append("Excellent daily step count")
    elif safe_compare(daily_steps, '>=', 7000):
        lifestyle_score += 5
        positive_factors.append("Good daily step count")
    elif safe_compare(daily_steps, '<', 5000):
        lifestyle_score -= 10
        negative_factors.append("Low daily step count")
    
    # Sleep Analysis
    if sleep_hours is not None and 7 <= sleep_hours <= 9:
        lifestyle_score += 10
        positive_factors.append("Optimal sleep duration")
    elif safe_compare(sleep_hours, '<', 6):
        lifestyle_score -= 15
        negative_factors.append("Insufficient sleep duration")
    
    if safe_compare(sleep_quality, '>=', 8):
        lifestyle_score += 5
        positive_factors.append("Good sleep quality")
    elif safe_compare(sleep_quality, '<', 5):
        lifestyle_score -= 10
        negative_factors.append("Poor sleep quality")
    
    # Stress Management
    if safe_compare(stress_level, '<=', 3):
        lifestyle_score += 10
        positive_factors.append("Excellent stress management")
    elif safe_compare(stress_level, '>', 7):
        lifestyle_score -= 15
        negative_factors.append("High stress levels")
    
    # Lifestyle Risk Factors
    if safe_compare(smoking, '>', 0):
        lifestyle_score -= 25
        negative_factors.append("Smoking significantly impacts health")
    
    if safe_compare(alcohol, '>', 3):
        lifestyle_score -= 10
        negative_factors.append("High alcohol consumption")
    
    return {
        "lifestyle_score": max(0, min(100, lifestyle_score)),
        "positive_factors": positive_factors,
        "negative_factors": negative_factors,
        "recommendations": [
            "Aim for 10,000+ daily steps",
            "Engage in 150+ minutes moderate exercise weekly",
            "Maintain 7-9 hours quality sleep",
            "Implement stress management techniques",
            "Avoid smoking and limit alcohol"
        ]
    }

def analyze_age_gender_considerations(age, gender, diabetes_proba, hypertension_proba, bmi, blood_pressure):
    """Age and gender-specific risk considerations"""
    
    considerations = []
    
    # Age-specific considerations
    if age < 30:
        considerations.append({
            "category": "Young Adult",
            "message": "Early intervention is crucial. Lifestyle changes now have maximum impact.",
            "focus": "Prevention and healthy habit formation"
        })
    elif age < 45:
        considerations.append({
            "category": "Middle Age",
            "message": "Critical prevention window. Small changes now prevent major health issues later.",
            "focus": "Risk factor management and regular screening"
        })
    elif age < 65:
        considerations.append({
            "category": "Pre-Senior",
            "message": "High-risk period for chronic diseases. Aggressive prevention needed.",
            "focus": "Comprehensive health management"
        })
    else:
        considerations.append({
            "category": "Senior",
            "message": "Focus on maintaining current health and preventing complications.",
            "focus": "Health maintenance and complication prevention"
        })
    
    # Gender-specific considerations
    if gender == 1:  # Male
        considerations.append({
            "category": "Male Health",
            "message": "Men develop diabetes at lower BMIs and have higher cardiovascular risk.",
            "focus": "BMI management and cardiovascular prevention"
        })
    else:  # Female
        considerations.append({
            "category": "Female Health",
            "message": "Hormonal changes can affect diabetes and cardiovascular risk.",
            "focus": "Hormonal health and regular monitoring"
        })
    
    # Combined risk assessment
    if diabetes_proba > 0.3 or hypertension_proba > 0.4:
        considerations.append({
            "category": "High Risk",
            "message": "Multiple risk factors present. Comprehensive intervention needed.",
            "focus": "Multi-factorial risk reduction"
        })
    
    return considerations

def generate_reasoning_explanations(
    diabetes_risk: float, 
    hypertension_risk: float, 
    top_factors: List[Dict], 
    input_values: Dict
) -> List[str]:
    """Generate highly personalized reasoning explanations for the risk predictions"""
    explanations = []
    
    # Extract user profile for personalized explanations
    age = input_values.get('age', 45)
    gender = input_values.get('gender', 0)
    bmi = input_values.get('bmi', 25)
    blood_pressure = input_values.get('blood_pressure', 120)
    glucose = input_values.get('glucose_level', 100)
    activity = input_values.get('physical_activity', 5)
    smoking = input_values.get('smoking_status', 0)
    family_history = input_values.get('family_history', 0)
    
    gender_text = "woman" if gender == 0 else "man"
    
    # Highly personalized diabetes reasoning
    if diabetes_risk > 0.7:
        explanations.append(f"As a {age}-year-old {gender_text}, your diabetes risk of {diabetes_risk:.1%} is high. This is primarily driven by your {top_factors[0]['feature'].replace('_', ' ')} ({top_factors[0]['value']}), which has the strongest impact on your risk.")
        explanations.append(f"Your {top_factors[1]['feature'].replace('_', ' ')} and {top_factors[2]['feature'].replace('_', ' ')} are also significant contributors. At your age, immediate lifestyle changes are crucial.")
    elif diabetes_risk > 0.3:
        explanations.append(f"At {age} years old, your diabetes risk of {diabetes_risk:.1%} is moderate. Your {top_factors[0]['feature'].replace('_', ' ')} is the primary factor, but your {top_factors[1]['feature'].replace('_', ' ')} and {top_factors[2]['feature'].replace('_', ' ')} also contribute.")
        explanations.append(f"Small lifestyle changes could significantly reduce this risk. You're in a critical prevention window at {age}.")
    else:
        explanations.append(f"Excellent news! As a {age}-year-old {gender_text}, your diabetes risk of {diabetes_risk:.1%} is low. Your current {top_factors[0]['feature'].replace('_', ' ')} and lifestyle factors are protective.")
        explanations.append(f"Continue maintaining these healthy habits to preserve this low risk.")
    
    # Highly personalized hypertension reasoning
    if hypertension_risk > 0.7:
        explanations.append(f"Your hypertension risk of {hypertension_risk:.1%} is high, primarily due to your {top_factors[0]['feature'].replace('_', ' ')} ({top_factors[0]['value']}). At your age of {age}, this is concerning and requires immediate attention.")
        explanations.append(f"Your {top_factors[1]['feature'].replace('_', ' ')} and {top_factors[2]['feature'].replace('_', ' ')} are also contributing factors. Blood pressure management is crucial for your long-term health.")
    elif hypertension_risk > 0.3:
        explanations.append(f"Your hypertension risk of {hypertension_risk:.1%} is moderate. Your {top_factors[0]['feature'].replace('_', ' ')} is the main concern, with {top_factors[1]['feature'].replace('_', ' ')} and {top_factors[2]['feature'].replace('_', ' ')} also playing a role.")
        explanations.append(f"At {age}, focusing on blood pressure management is crucial for long-term health. Small lifestyle changes could significantly reduce this risk.")
    else:
        explanations.append(f"Great job! Your hypertension risk of {hypertension_risk:.1%} is low. Your {top_factors[0]['feature'].replace('_', ' ')} and other lifestyle factors are working in your favor.")
        explanations.append(f"Keep up these healthy habits to maintain this low risk.")
    
    # Age-specific explanations
    if age >= 65:
        explanations.append(f"At {age}, you're in a high-risk age group for both diabetes and hypertension. However, your current risk levels suggest you're managing your health well. Continue with regular monitoring and preventive care.")
    elif age >= 45:
        explanations.append(f"At {age}, you're entering a critical prevention window. Your current risk levels are manageable, but this is the perfect time to optimize your lifestyle for long-term health.")
    elif age >= 30:
        explanations.append(f"At {age}, you have an excellent opportunity to establish healthy habits that will protect you long-term. Your current risk levels are very manageable.")
    else:
        explanations.append(f"Your young age of {age} gives you a significant advantage in preventing chronic diseases. Your current risk levels are excellent - focus on maintaining these healthy habits.")
    
    # Gender-specific explanations
    if gender == 0:  # Female
        explanations.append("As a woman, you have unique risk factors to consider. Hormonal changes throughout life can affect both diabetes and hypertension risk. Regular health screenings and maintaining a healthy lifestyle are especially important.")
    else:  # Male
        explanations.append("As a man, you may be at higher risk for developing these conditions at younger ages. Your current risk levels suggest you're doing well, but continued vigilance with lifestyle factors is important.")
    
    # Family history explanations
    if family_history:
        explanations.append("Given your family history, you have a higher genetic predisposition to these conditions. However, your current risk levels suggest that your lifestyle choices are effectively managing this genetic risk. Continue focusing on controllable factors.")
    else:
        explanations.append("With no family history, you have a genetic advantage. Your current risk levels reflect this advantage, but maintaining healthy lifestyle habits is still crucial for long-term health.")
    
    # Activity level explanations
    if activity <= 3:
        explanations.append(f"Your activity level of {activity}/10 is below optimal and contributes to your risk. Increasing physical activity could significantly improve your health outcomes and reduce your risk levels.")
    elif activity >= 7:
        explanations.append(f"Your high activity level of {activity}/10 is excellent and is helping to protect you from these conditions. This is one of your strongest protective factors.")
    else:
        explanations.append(f"Your activity level of {activity}/10 is good. Consider increasing it slightly to further reduce your risk and improve your overall health.")
    
    # Smoking status explanations
    if smoking == 2:  # Current smoker
        explanations.append("Your smoking status is significantly increasing your risk for both diabetes and hypertension. Quitting smoking would be the single most important step you could take to improve your health.")
    elif smoking == 1:  # Former smoker
        explanations.append("Congratulations on quitting smoking! This is significantly reducing your risk compared to if you were still smoking. Your risk continues to decrease the longer you stay smoke-free.")
    else:
        explanations.append("Your non-smoking status is one of your strongest protective factors. This significantly reduces your risk for both diabetes and hypertension.")
    
    return explanations

def calculate_gamification_points(input_values: Dict, recommendations_followed: List[str] = None) -> int:
    """Calculate gamification points based on health metrics and recommendations followed"""
    points = 0
    
    # Base points for good metrics
    if input_values.get('physical_activity', 0) >= 5:
        points += 50
    if input_values.get('daily_steps', 0) >= 10000:
        points += 30
    if input_values.get('sleep_hours', 0) >= 7:
        points += 20
    if input_values.get('water_intake', 0) >= 8:
        points += 15
    if input_values.get('protein_intake', 0) >= 60:
        points += 25
    
    # Bonus points for following recommendations
    if recommendations_followed:
        points += len(recommendations_followed) * 10
    
    return points

def generate_personalized_insights(input_values: Dict, risk_scores: Dict) -> List[str]:
    """Generate highly personalized insights based on user's specific profile and risk factors"""
    insights = []
    
    # Extract user profile
    age = input_values.get('age', 45)
    gender = input_values.get('gender', 0)
    bmi = input_values.get('bmi', 25)
    blood_pressure = input_values.get('blood_pressure', 120)
    glucose = input_values.get('glucose_level', 100)
    cholesterol = input_values.get('cholesterol_level', 200)
    activity = input_values.get('physical_activity', 5)
    smoking = input_values.get('smoking_status', 0)
    family_history = input_values.get('family_history', 0)
    hba1c = input_values.get('hba1c', 5.7)
    
    # Gender-specific insights
    gender_text = "woman" if gender == 0 else "man"
    
    # Age-specific personalized insights
    if age >= 65:
        insights.append(f"As a {age}-year-old {gender_text}, you're in a high-risk age group. Focus on preventive care and regular monitoring.")
    elif age >= 45:
        insights.append(f"At {age} years old, you're entering a critical period for chronic disease prevention. Early intervention is key.")
    elif age >= 30:
        insights.append(f"At {age}, you have a great opportunity to establish healthy habits that will protect you long-term.")
    else:
        insights.append(f"Your young age of {age} gives you a significant advantage in preventing chronic diseases.")
    
    # BMI-specific personalized insights
    if bmi >= 35:
        insights.append(f"Your BMI of {bmi:.1f} indicates severe obesity. Weight loss of 10-15% could dramatically reduce your health risks.")
    elif bmi >= 30:
        insights.append(f"Your BMI of {bmi:.1f} puts you in the obese category. Even a 5-10% weight loss would significantly improve your health.")
    elif bmi >= 25:
        insights.append(f"Your BMI of {bmi:.1f} is slightly above the healthy range. Small lifestyle changes could bring you to optimal health.")
    elif 18.5 <= bmi <= 24.9:
        insights.append(f"Excellent! Your BMI of {bmi:.1f} is in the healthy range. Keep up the great work!")
    else:
        insights.append(f"Your BMI of {bmi:.1f} is below the healthy range. Consider consulting a healthcare provider about healthy weight gain.")
    
    # Blood pressure personalized insights
    if blood_pressure >= 180:
        insights.append(f"Your blood pressure of {blood_pressure} mmHg is critically high. Immediate medical attention is recommended.")
    elif blood_pressure >= 140:
        insights.append(f"Your blood pressure of {blood_pressure} mmHg is high. Lifestyle changes and possibly medication may be needed.")
    elif blood_pressure >= 120:
        insights.append(f"Your blood pressure of {blood_pressure} mmHg is elevated. Focus on diet, exercise, and stress management.")
    else:
        insights.append(f"Your blood pressure of {blood_pressure} mmHg is excellent! Continue your current lifestyle.")
    
    # Glucose personalized insights
    if glucose >= 200:
        insights.append(f"Your glucose level of {glucose} mg/dL is very high. This suggests diabetes and requires immediate medical attention.")
    elif glucose >= 126:
        insights.append(f"Your glucose level of {glucose} mg/dL indicates diabetes. Work with your doctor on a management plan.")
    elif glucose >= 100:
        insights.append(f"Your glucose level of {glucose} mg/dL is in the pre-diabetes range. Focus on carbohydrate control and exercise.")
    else:
        insights.append(f"Your glucose level of {glucose} mg/dL is in the healthy range. Keep up your current habits!")
    
    # HbA1c personalized insights (if available)
    if hba1c is not None:
        if hba1c >= 6.5:
            insights.append(f"Your HbA1c of {hba1c}% indicates diabetes. This requires medical management and lifestyle changes.")
        elif hba1c >= 5.7:
            insights.append(f"Your HbA1c of {hba1c}% suggests pre-diabetes. Focus on weight management and regular exercise.")
        else:
            insights.append(f"Your HbA1c of {hba1c}% is in the normal range. Continue your healthy lifestyle!")
    
    # Activity level personalized insights
    if activity <= 2:
        insights.append(f"Your activity level of {activity}/10 is very low. Start with just 10 minutes of daily walking to build momentum.")
    elif activity <= 4:
        insights.append(f"Your activity level of {activity}/10 is below optimal. Aim for 150 minutes of moderate exercise weekly.")
    elif activity <= 7:
        insights.append(f"Your activity level of {activity}/10 is good. Consider adding strength training twice weekly.")
    else:
        insights.append(f"Your activity level of {activity}/10 is excellent! You're doing great with your fitness routine.")
    
    # Smoking personalized insights
    if smoking == 2:  # Current smoker
        insights.append("Quitting smoking is the single most important step you can take for your health. Consider nicotine replacement therapy.")
    elif smoking == 1:  # Former smoker
        insights.append("Congratulations on quitting smoking! Your risk continues to decrease the longer you stay smoke-free.")
    else:
        insights.append("Great job staying smoke-free! This significantly reduces your risk of heart disease and cancer.")
    
    # Family history personalized insights
    if family_history:
        insights.append("Given your family history, you have a higher genetic risk. Focus on controllable factors like diet, exercise, and regular checkups.")
    else:
        insights.append("With no family history, you have a genetic advantage. Focus on maintaining healthy lifestyle habits.")
    
    # Cholesterol personalized insights
    if cholesterol >= 240:
        insights.append(f"Your cholesterol of {cholesterol} mg/dL is high. Focus on a heart-healthy diet and consider medication.")
    elif cholesterol >= 200:
        insights.append(f"Your cholesterol of {cholesterol} mg/dL is borderline high. Dietary changes could help lower it.")
    else:
        insights.append(f"Your cholesterol of {cholesterol} mg/dL is in a healthy range. Keep up your current lifestyle!")
    
    # Risk-specific personalized insights
    diabetes_risk = risk_scores.get('diabetes_risk', 0)
    hypertension_risk = risk_scores.get('hypertension_risk', 0)
    
    if diabetes_risk > 0.7:
        insights.append(f"Your diabetes risk of {diabetes_risk:.1%} is high. Focus on weight loss, exercise, and blood sugar monitoring.")
    elif diabetes_risk > 0.3:
        insights.append(f"Your diabetes risk of {diabetes_risk:.1%} is moderate. Small lifestyle changes can significantly reduce this risk.")
    
    if hypertension_risk > 0.7:
        insights.append(f"Your hypertension risk of {hypertension_risk:.1%} is high. Focus on sodium reduction, exercise, and stress management.")
    elif hypertension_risk > 0.3:
        insights.append(f"Your hypertension risk of {hypertension_risk:.1%} is moderate. Blood pressure monitoring and lifestyle changes are key.")
    
    return insights

def analyze_what_if_scenario(scenario: str, current_values: Dict) -> Dict[str, Any]:
    """Analyze 'what if' scenarios for health improvements with personalized predictions"""
    scenario_lower = scenario.lower()
    
    # Extract current user profile
    age = current_values.get('age', 45)
    gender = current_values.get('gender', 0)
    bmi = current_values.get('bmi', 25)
    blood_pressure = current_values.get('blood_pressure', 120)
    glucose = current_values.get('glucose_level', 100)
    activity = current_values.get('physical_activity', 5)
    smoking = current_values.get('smoking_status', 0)
    family_history = current_values.get('family_history', 0)
    
    gender_text = "woman" if gender == 0 else "man"
    
    # Protein intake scenarios
    if "protein" in scenario_lower and ("increase" in scenario_lower or "more" in scenario_lower):
        current_protein = current_values.get('protein_intake', 50)
        recommended_protein = max(60, bmi * 1.2)  # 1.2g per kg body weight
        
        return {
            "scenario": f"Increased Protein Intake for {age}-year-old {gender_text}",
            "current_protein": f"{current_protein}g daily",
            "recommended_protein": f"{recommended_protein:.0f}g daily",
            "potential_benefits": [
                f"Better blood sugar control (especially important at your glucose level of {glucose} mg/dL)",
                "Improved muscle mass and metabolism (crucial at age {age})",
                "Enhanced satiety and weight management (helpful for your BMI of {bmi:.1f})",
                "Better recovery from exercise"
            ],
            "personalized_impact": f"For a {age}-year-old with BMI {bmi:.1f}, increasing protein could reduce diabetes risk by 8-12%",
            "implementation_tips": [
                "Add lean protein to each meal (chicken, fish, beans, Greek yogurt)",
                "Aim for 20-30g protein per meal",
                "Consider protein supplements if needed",
                "Monitor blood sugar response to protein-rich meals"
            ],
            "timeline": "Expect to see benefits within 2-4 weeks of consistent protein intake"
        }
    
    # Exercise scenarios
    elif "exercise" in scenario_lower or "workout" in scenario_lower or "activity" in scenario_lower:
        current_activity = activity
        recommended_activity = min(8, current_activity + 2)
        
        return {
            "scenario": f"Increased Exercise for {age}-year-old {gender_text}",
            "current_activity": f"{current_activity}/10",
            "recommended_activity": f"{recommended_activity}/10",
            "potential_benefits": [
                f"Lower blood pressure (your current {blood_pressure} mmHg could improve by 5-10 points)",
                f"Improved insulin sensitivity (helpful for your glucose level of {glucose} mg/dL)",
                "Better cardiovascular health",
                f"Potential weight loss (could help with your BMI of {bmi:.1f})"
            ],
            "personalized_impact": f"For a {age}-year-old with current activity level {current_activity}/10, increasing exercise could reduce diabetes risk by 15-25% and hypertension risk by 10-20%",
            "recommended_exercise": [
                "Start with 30 minutes of moderate activity 5 days/week",
                "Include both cardio and strength training",
                "Consider walking, swimming, or cycling for low-impact options",
                "Gradually increase intensity over 4-6 weeks"
            ],
            "age_considerations": f"At {age}, focus on joint-friendly activities and proper warm-up/cool-down",
            "timeline": "Blood pressure improvements may be seen within 2-3 weeks, diabetes risk reduction within 2-3 months"
        }
    
    # Weight loss scenarios
    elif "weight" in scenario_lower or "lose" in scenario_lower or "bmi" in scenario_lower:
        current_weight = bmi * 1.7 * 1.7  # Approximate weight from BMI
        target_bmi = max(22, bmi - 2)
        weight_loss_needed = current_weight * 0.1  # 10% weight loss
        
        return {
            "scenario": f"Weight Loss for {age}-year-old {gender_text}",
            "current_bmi": f"{bmi:.1f}",
            "target_bmi": f"{target_bmi:.1f}",
            "weight_loss_needed": f"{weight_loss_needed:.1f} lbs",
            "potential_benefits": [
                f"Significant reduction in diabetes risk (your current glucose of {glucose} mg/dL could improve)",
                f"Lower blood pressure (your {blood_pressure} mmHg could drop by 5-15 points)",
                "Improved cholesterol levels",
                "Better joint health and mobility"
            ],
            "personalized_impact": f"For a {age}-year-old with BMI {bmi:.1f}, losing 10% of body weight could reduce diabetes risk by 30-50% and hypertension risk by 20-30%",
            "recommended_approach": [
                f"Create a 500-calorie daily deficit for 1 lb/week loss",
                "Focus on whole foods and portion control",
                "Include both cardio and strength training",
                "Aim for 7-9 hours of quality sleep"
            ],
            "age_considerations": f"At {age}, gradual weight loss (1-2 lbs/week) is safer and more sustainable",
            "timeline": "Significant health improvements typically seen within 3-6 months of sustained weight loss"
        }
    
    # Blood pressure scenarios
    elif "blood pressure" in scenario_lower or "pressure" in scenario_lower:
        return {
            "scenario": f"Blood Pressure Management for {age}-year-old {gender_text}",
            "current_bp": f"{blood_pressure} mmHg",
            "target_bp": "Less than 120/80 mmHg",
            "potential_benefits": [
                "Reduced risk of heart disease and stroke",
                "Better kidney function",
                "Improved overall cardiovascular health",
                "Reduced medication needs"
            ],
            "personalized_impact": f"For a {age}-year-old with BP {blood_pressure} mmHg, lifestyle changes could reduce hypertension risk by 20-40%",
            "recommended_actions": [
                "Follow DASH diet (limit sodium to 2,300mg daily)",
                "Increase potassium-rich foods (bananas, spinach, avocados)",
                "Engage in regular aerobic exercise",
                "Manage stress through meditation or yoga",
                "Limit alcohol intake"
            ],
            "age_considerations": f"At {age}, blood pressure management becomes increasingly important for long-term health",
            "timeline": "Blood pressure improvements may be seen within 2-4 weeks of lifestyle changes"
        }
    
    # Sleep scenarios
    elif "sleep" in scenario_lower:
        current_sleep = current_values.get('sleep_hours', 7)
        return {
            "scenario": f"Improved Sleep for {age}-year-old {gender_text}",
            "current_sleep": f"{current_sleep} hours",
            "recommended_sleep": "7-9 hours nightly",
            "potential_benefits": [
                "Better blood sugar control",
                "Improved blood pressure regulation",
                "Enhanced immune function",
                "Better stress management"
            ],
            "personalized_impact": f"For a {age}-year-old, improving sleep could reduce diabetes risk by 10-15% and hypertension risk by 8-12%",
            "sleep_hygiene_tips": [
                "Maintain consistent sleep schedule",
                "Create cool, dark, quiet bedroom environment",
                "Avoid screens 1 hour before bed",
                "Limit caffeine after 2 PM",
                "Consider relaxation techniques"
            ],
            "timeline": "Sleep quality improvements typically seen within 1-2 weeks of consistent sleep hygiene"
        }
    
    # Stress management scenarios
    elif "stress" in scenario_lower:
        current_stress = current_values.get('stress_level', 5)
        return {
            "scenario": f"Stress Management for {age}-year-old {gender_text}",
            "current_stress": f"{current_stress}/10",
            "target_stress": "3-5/10",
            "potential_benefits": [
                "Lower blood pressure",
                "Better blood sugar control",
                "Improved sleep quality",
                "Enhanced overall well-being"
            ],
            "personalized_impact": f"For a {age}-year-old with stress level {current_stress}/10, stress management could reduce both diabetes and hypertension risk by 10-20%",
            "stress_reduction_techniques": [
                "Daily meditation or deep breathing (10-15 minutes)",
                "Regular physical exercise",
                "Time management and prioritization",
                "Social support and connection",
                "Professional counseling if needed"
            ],
            "timeline": "Stress reduction benefits typically seen within 2-4 weeks of consistent practice"
        }
    
    # General health improvement
    else:
        return {
            "scenario": f"General Health Improvement for {age}-year-old {gender_text}",
            "current_profile": f"BMI: {bmi:.1f}, BP: {blood_pressure} mmHg, Glucose: {glucose} mg/dL",
            "potential_benefits": [
                "Reduced inflammation throughout the body",
                "Better overall health markers",
                "Improved quality of life and energy",
                "Enhanced longevity and vitality"
            ],
            "personalized_impact": f"For a {age}-year-old {gender_text}, comprehensive lifestyle changes could reduce diabetes risk by 20-40% and hypertension risk by 15-30%",
            "comprehensive_approach": [
                "Balanced, nutrient-dense diet",
                "Regular physical activity (150 min/week moderate + 2 strength sessions)",
                "Adequate sleep (7-9 hours nightly)",
                "Stress management and relaxation",
                "Regular health checkups and monitoring"
            ],
            "age_considerations": f"At {age}, you're in a critical window for preventing chronic diseases. Lifestyle changes now have maximum impact.",
            "timeline": "Comprehensive health improvements typically seen within 3-6 months of consistent lifestyle changes"
        }


@app.post("/predict", response_model=PredictionResponse)
async def predict_health_risks(health_input: HealthInput, current_user: dict = Depends(get_current_active_user)):
    """
    Comprehensive health risk prediction with optimized models and realistic confidence scoring
    """
    if not all([diabetes_model, hypertension_model, model_features]):
        raise HTTPException(
            status_code=503,
            detail="Optimized models not loaded. Please run the optimized train_pipeline.py first."
        )
    
    try:
        # Prepare features
        input_df, feature_quality = prepare_features(health_input)
        
        # Apply preprocessing if available
        if feature_scaler is not None:
            input_array = feature_scaler.transform(input_df)
        else:
            input_array = input_df.values
        
        # Get predictions - ensure they are Python floats
        diabetes_proba = safe_float_conversion(diabetes_model.predict_proba(input_array)[0, 1])
        hypertension_proba = safe_float_conversion(hypertension_model.predict_proba(input_array)[0, 1])
        
        # Get confidence levels
        diabetes_confidence = get_confidence_level(diabetes_proba, feature_quality)
        hypertension_confidence = get_confidence_level(hypertension_proba, feature_quality)
        
        # Get feature importance and SHAP values
        diabetes_importance = get_simple_feature_importance(diabetes_model, model_features, input_array)
        hypertension_importance = get_simple_feature_importance(hypertension_model, model_features, input_array)
        
        # Try to get SHAP values if explainers are available
        diabetes_shap_dict = {}
        hypertension_shap_dict = {}
        
        if diabetes_explainer is not None and hypertension_explainer is not None:
            try:
                diabetes_shap = diabetes_explainer.shap_values(input_array)
                hypertension_shap = hypertension_explainer.shap_values(input_array)
                
                # Handle different SHAP output formats
                if isinstance(diabetes_shap, list):
                    diabetes_shap = diabetes_shap[1][0]  # Binary classification, positive class
                    hypertension_shap = hypertension_shap[1][0]
                else:
                    diabetes_shap = diabetes_shap[0]
                    hypertension_shap = hypertension_shap[0]
                
                diabetes_shap_dict = {
                    "base_value": safe_float_conversion(diabetes_explainer.expected_value),
                    "feature_contributions": {
                        feature: safe_float_conversion(value)
                        for feature, value in zip(model_features, diabetes_shap)
                    },
                    "feature_values": {
                        feature: safe_float_conversion(input_df[feature].iloc[0])
                        for feature in model_features
                    }
                }
                
                hypertension_shap_dict = {
                    "base_value": safe_float_conversion(hypertension_explainer.expected_value),
                    "feature_contributions": {
                        feature: safe_float_conversion(value)
                        for feature, value in zip(model_features, hypertension_shap)
                    },
                    "feature_values": {
                        feature: safe_float_conversion(input_df[feature].iloc[0])
                        for feature in model_features
                    }
                }
                
            except Exception as e:
                logger.warning(f"SHAP calculation failed: {e}, using feature importance")
                # Fallback to feature importance
                diabetes_shap_dict = {
                    "feature_contributions": {feat: safe_float_conversion(imp) for feat, imp in diabetes_importance},
                    "explanation_type": "feature_importance"
                }
                hypertension_shap_dict = {
                    "feature_contributions": {feat: safe_float_conversion(imp) for feat, imp in hypertension_importance},
                    "explanation_type": "feature_importance"
                }
        else:
            # Use feature importance as explanation
            diabetes_shap_dict = {
                "feature_contributions": {feat: safe_float_conversion(imp) for feat, imp in diabetes_importance},
                "explanation_type": "feature_importance"
            }
            hypertension_shap_dict = {
                "feature_contributions": {feat: safe_float_conversion(imp) for feat, imp in hypertension_importance},
                "explanation_type": "feature_importance"
            }
        
        # Get personalized recommendations
        input_values = health_input.dict()
        diabetes_recs = get_personalized_recommendations(
            diabetes_importance, input_values, 'diabetes', diabetes_proba
        )
        hypertension_recs = get_personalized_recommendations(
            hypertension_importance, input_values, 'hypertension', hypertension_proba
        )
        
        # Get comprehensive risk factor analysis
        comprehensive_analysis = analyze_comprehensive_risk_factors(
            input_values, diabetes_proba, hypertension_proba
        )
        
        # Combine unique recommendations
        combined_nutrition = list(dict.fromkeys(  # Remove duplicates while preserving order
            diabetes_recs['nutrition'][:3] + hypertension_recs['nutrition'][:3]
        ))
        combined_fitness = list(dict.fromkeys(
            diabetes_recs['fitness'][:3] + hypertension_recs['fitness'][:3]
        ))
        combined_lifestyle = list(dict.fromkeys(
            diabetes_recs['lifestyle'] + hypertension_recs['lifestyle']
        ))
        
        # Calculate health scores
        health_scores = calculate_health_scores(input_values)
        
        # Prepare top factors with values and importance
        top_diabetes_factors = [
            {
                "feature": feat,
                "importance": safe_float_conversion(imp),
                "value": safe_float_conversion(input_df[feat].iloc[0]) if feat in input_df.columns else None
            }
            for feat, imp in diabetes_importance[:5]
        ]
        
        top_hypertension_factors = [
            {
                "feature": feat,
                "importance": safe_float_conversion(imp),
                "value": safe_float_conversion(input_df[feat].iloc[0]) if feat in input_df.columns else None
            }
            for feat, imp in hypertension_importance[:5]
        ]
        
        # Calculate new enhanced features
        diabetes_contributions = calculate_contribution_percentages(diabetes_importance)
        hypertension_contributions = calculate_contribution_percentages(hypertension_importance)
        
        # Generate reasoning explanations
        reasoning_explanations = generate_reasoning_explanations(
            diabetes_proba, hypertension_proba, top_diabetes_factors, input_values
        )
        
        # Calculate gamification points
        gamification_points = calculate_gamification_points(input_values)
        
        # Generate personalized insights
        risk_scores = {"diabetes": diabetes_proba, "hypertension": hypertension_proba}
        personalized_insights = generate_personalized_insights(input_values, risk_scores)
        
        # Prepare response with all values properly converted
        response_data = {
            "diabetes_risk": round(diabetes_proba, 3),
            "hypertension_risk": round(hypertension_proba, 3),
            "diabetes_confidence": diabetes_confidence,
            "hypertension_confidence": hypertension_confidence,
            "risk_category_diabetes": get_risk_category(diabetes_proba),
            "risk_category_hypertension": get_risk_category(hypertension_proba),
            "diabetes_shap_values": safe_convert_dict_values(diabetes_shap_dict),
            "hypertension_shap_values": safe_convert_dict_values(hypertension_shap_dict),
            "nutrition_recommendations": {
                "primary": combined_nutrition[:4],
                "secondary": combined_nutrition[4:8] if len(combined_nutrition) > 4 else []
            },
            "fitness_recommendations": {
                "primary": combined_fitness[:3],
                "secondary": combined_fitness[3:6] if len(combined_fitness) > 3 else []
            },
            "lifestyle_recommendations": combined_lifestyle[:5],
            "top_diabetes_factors": top_diabetes_factors,
            "top_hypertension_factors": top_hypertension_factors,
            "metabolic_health_score": round(health_scores['metabolic'], 1),
            "cardiovascular_health_score": round(health_scores['cardiovascular'], 1),
            "comprehensive_analysis": comprehensive_analysis,
            "model_details": {
                "diabetes_model": type(diabetes_model).__name__,
                "hypertension_model": type(hypertension_model).__name__,
                "version": "optimized_v2.1",
                "anti_overfitting": "enabled"
            },
            # New enhanced features
            "contribution_percentages": {
                "diabetes": diabetes_contributions,
                "hypertension": hypertension_contributions
            },
            "reasoning_explanations": reasoning_explanations,
            "gamification_points": gamification_points,
            "personalized_insights": personalized_insights
        }
        
        # Create response object
        response = PredictionResponse(**response_data)
        
        logger.info(f"Prediction successful - Diabetes: {diabetes_proba:.1%} ({diabetes_confidence}), Hypertension: {hypertension_proba:.1%} ({hypertension_confidence})")
        
        # Save prediction to database
        try:
            logger.info("Attempting to save prediction to database")
            predictions_collection = get_predictions_collection()
            prediction_record = {
                "user_id": current_user["id"],  # Use authenticated user ID
                "input_data": health_input.dict(),
                "diabetes_risk": diabetes_proba,
                "hypertension_risk": hypertension_proba,
                "diabetes_confidence": diabetes_confidence,
                "hypertension_confidence": hypertension_confidence,
                "risk_category_diabetes": get_risk_category(diabetes_proba),
                "risk_category_hypertension": get_risk_category(hypertension_proba),
                "metabolic_health_score": response.metabolic_health_score,
                "cardiovascular_health_score": response.cardiovascular_health_score,
                "created_at": datetime.now()
            }
            
            logger.info(f"Prediction record prepared: {prediction_record}")
            result = predictions_collection.insert_one(prediction_record)
            logger.info(f"Prediction saved to database with ID: {result.inserted_id}")
            
        except Exception as db_error:
            logger.error(f"Failed to save prediction to database: {db_error}")
            logger.error(f"Database error details: {str(db_error)}")
            # Don't fail the request if database save fails
        
        return response
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.get("/predictions/history")
async def get_prediction_history(limit: int = 10, current_user: dict = Depends(get_current_active_user)):
    """Get user's prediction history"""
    try:
        predictions_collection = get_predictions_collection()
        
        cursor = predictions_collection.find(
            {"user_id": str(current_user["_id"])}
        ).sort("created_at", -1).limit(limit)
        
        predictions = await cursor.to_list(length=limit)
        
        for pred in predictions:
            pred["_id"] = str(pred["_id"])
        
        return {
            "total": len(predictions),
            "predictions": predictions
        }
        
    except Exception as e:
        logger.error(f"Error fetching prediction history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")

@app.get("/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_active_user)):
    """Get dashboard statistics"""
    try:
        predictions_collection = get_predictions_collection()
        
        latest_prediction = await predictions_collection.find_one(
            {"user_id": str(current_user["_id"])},
            sort=[("created_at", -1)]
        )
        
        total_predictions = await predictions_collection.count_documents(
            {"user_id": str(current_user["_id"])}
        )
        
        stats = {
            "total_predictions": total_predictions,
            "latest_diabetes_risk": latest_prediction.get("diabetes_risk") if latest_prediction else None,
            "latest_hypertension_risk": latest_prediction.get("hypertension_risk") if latest_prediction else None,
            "metabolic_health_score": latest_prediction.get("metabolic_health_score") if latest_prediction else None,
            "cardiovascular_health_score": latest_prediction.get("cardiovascular_health_score") if latest_prediction else None,
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stats")

# [Keep all your other existing endpoints: get_general_recommendations, analyze_what_if_scenario_endpoint,
#  get_tracking_goals, update_tracking_data, search_food_database]

@app.get("/predictions/{prediction_id}/download-pdf")
def download_prediction_pdf(
    prediction_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Download prediction report as PDF"""
    try:
        predictions_collection = get_predictions_collection()
        
        # Find the prediction
        prediction = predictions_collection.find_one({
            "_id": ObjectId(prediction_id),
            "user_id": current_user["id"]
        })
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        # Generate PDF
        user_info = {
            "name": current_user.get("email", "User"),
            "email": current_user.get("email", "")
        }
        
        pdf_buffer = generate_health_report_pdf(prediction, user_info)
        
        # Return PDF as download
        filename = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@app.post("/predict/download-pdf", response_class=StreamingResponse)
def download_latest_prediction_pdf(
    health_input: HealthInput,
    current_user: dict = Depends(get_current_active_user)
):
    """Generate and download PDF for the current prediction"""
    try:
        # Make prediction (reuse prediction logic or call predict endpoint internally)
        # For simplicity, you can get the latest prediction from DB
        predictions_collection = get_predictions_collection()
        
        latest_prediction = predictions_collection.find_one(
            {"user_id": current_user["id"]},
            sort=[("created_at", -1)]
        )
        
        if not latest_prediction:
            raise HTTPException(status_code=404, detail="No predictions found")
        
        user_info = {
            "name": current_user.get("email", "User"),
            "email": current_user.get("email", "")
        }
        
        pdf_buffer = generate_health_report_pdf(latest_prediction, user_info)
        
        filename = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@app.post("/predict/current-pdf", response_class=StreamingResponse)
async def download_current_prediction_pdf(
    health_data: dict,
    current_user: dict = Depends(get_current_active_user)
):
    """Generate and download PDF for current prediction without saving to DB"""
    try:
        # Debug logging
        logger.info(f"PDF download request received for user: {current_user.get('email', 'unknown')}")
        logger.info(f"Health data received: {health_data}")
        logger.info(f"Health data keys: {list(health_data.keys()) if health_data else 'None'}")
        
        # Convert raw health data to HealthInput model
        try:
            health_input = HealthInput(**health_data)
            logger.info(f"Successfully converted health data to HealthInput model")
        except Exception as e:
            logger.error(f"Error validating health data: {e}")
            logger.error(f"Health data that failed validation: {health_data}")
            raise HTTPException(status_code=422, detail=f"Invalid health data format: {str(e)}")
        
        # Make prediction first
        if not all([diabetes_model, hypertension_model, model_features]):
            raise HTTPException(
                status_code=503,
                detail="Models not loaded. Please try again later."
            )
        
        # Prepare features
        input_df, feature_quality = prepare_features(health_input)
        
        # Apply preprocessing if available
        if feature_scaler is not None:
            input_array = feature_scaler.transform(input_df)
        else:
            input_array = input_df.values
        
        # Get predictions
        diabetes_proba = safe_float_conversion(diabetes_model.predict_proba(input_array)[0, 1])
        hypertension_proba = safe_float_conversion(hypertension_model.predict_proba(input_array)[0, 1])
        
        # Get confidence levels
        diabetes_confidence = get_confidence_level(diabetes_proba, feature_quality)
        hypertension_confidence = get_confidence_level(hypertension_proba, feature_quality)
        
        # Get feature importance
        diabetes_importance = get_simple_feature_importance(diabetes_model, model_features, input_array)
        hypertension_importance = get_simple_feature_importance(hypertension_model, model_features, input_array)
        
        # Get personalized recommendations
        input_values = health_input.dict()
        diabetes_recs = get_personalized_recommendations(
            diabetes_importance, input_values, 'diabetes', diabetes_proba
        )
        hypertension_recs = get_personalized_recommendations(
            hypertension_importance, input_values, 'hypertension', hypertension_proba
        )
        
        # Combine recommendations
        combined_nutrition = list(dict.fromkeys(
            diabetes_recs['nutrition'][:3] + hypertension_recs['nutrition'][:3]
        ))
        combined_fitness = list(dict.fromkeys(
            diabetes_recs['fitness'][:3] + hypertension_recs['fitness'][:3]
        ))
        combined_lifestyle = list(dict.fromkeys(
            diabetes_recs['lifestyle'] + hypertension_recs['lifestyle']
        ))
        
        # Calculate health scores
        health_scores = calculate_health_scores(input_values)
        
        # Prepare top factors
        top_diabetes_factors = [
            {
                "feature": feat,
                "importance": safe_float_conversion(imp),
                "value": safe_float_conversion(input_df[feat].iloc[0]) if feat in input_df.columns else None
            }
            for feat, imp in diabetes_importance[:5]
        ]
        
        top_hypertension_factors = [
            {
                "feature": feat,
                "importance": safe_float_conversion(imp),
                "value": safe_float_conversion(input_df[feat].iloc[0]) if feat in input_df.columns else None
            }
            for feat, imp in hypertension_importance[:5]
        ]
        
        # Generate personalized insights
        risk_scores = {"diabetes": diabetes_proba, "hypertension": hypertension_proba}
        personalized_insights = generate_personalized_insights(input_values, risk_scores)
        
        # Create comprehensive analysis
        comprehensive_analysis = {
            "risk_factors": {
                "diabetes": top_diabetes_factors,
                "hypertension": top_hypertension_factors
            },
            "health_scores": {
                "metabolic": round(health_scores['metabolic'], 1),
                "cardiovascular": round(health_scores['cardiovascular'], 1)
            },
            "recommendations": {
                "nutrition": combined_nutrition,
                "fitness": combined_fitness,
                "lifestyle": combined_lifestyle
            },
            "insights": personalized_insights
        }
        
        # Create prediction data for PDF
        prediction_data = {
            "input_data": input_values,  # Add the input data
            "comprehensive_analysis": comprehensive_analysis,  # Add comprehensive analysis
            "diabetes_risk": round(diabetes_proba, 3),
            "hypertension_risk": round(hypertension_proba, 3),
            "diabetes_confidence": diabetes_confidence,
            "hypertension_confidence": hypertension_confidence,
            "risk_category_diabetes": get_risk_category(diabetes_proba),
            "risk_category_hypertension": get_risk_category(hypertension_proba),
            "nutrition_recommendations": {
                "primary": combined_nutrition[:4],
                "secondary": combined_nutrition[4:8] if len(combined_nutrition) > 4 else []
            },
            "fitness_recommendations": {
                "primary": combined_fitness[:3],
                "secondary": combined_fitness[3:6] if len(combined_fitness) > 3 else []
            },
            "lifestyle_recommendations": combined_lifestyle[:5],
            "top_diabetes_factors": top_diabetes_factors,
            "top_hypertension_factors": top_hypertension_factors,
            "metabolic_health_score": round(health_scores['metabolic'], 1),
            "cardiovascular_health_score": round(health_scores['cardiovascular'], 1),
            "personalized_insights": personalized_insights
        }
        
        # Generate PDF
        user_info = {
            "name": current_user.get("email", "User"),
            "email": current_user.get("email", "")
        }
        
        logger.info(f"About to generate PDF with prediction_data keys: {list(prediction_data.keys())}")
        logger.info(f"User info: {user_info}")
        
        try:
            pdf_buffer = generate_health_report_pdf(prediction_data, user_info)
            logger.info("PDF generated successfully")
        except Exception as pdf_error:
            logger.error(f"Error in generate_health_report_pdf: {pdf_error}")
            logger.error(f"PDF error type: {type(pdf_error)}")
            import traceback
            logger.error(f"PDF generation traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(pdf_error)}")
        
        filename = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

def analyze_health_question(question: str, health_data: Dict[str, Any], prediction_result: Dict[str, Any] = None) -> HealthAnswer:
    """AI-powered analysis of health questions based on user's specific health data"""
    
    try:
        logger.info(f"analyze_health_question called with question: {question[:50]}...")
        logger.info(f"analyze_health_question received health_data: {health_data}")
        logger.info(f"analyze_health_question received prediction_result: {prediction_result}")
        
        # Ensure health_data is not None and is a dictionary
        if health_data is None:
            health_data = {}
        elif not isinstance(health_data, dict):
            logger.warning(f"Health data is not a dictionary: {type(health_data)}")
            health_data = {}
        
        # Ensure prediction_result is not None and is a dictionary
        if prediction_result is None:
            prediction_result = {}
        elif not isinstance(prediction_result, dict):
            logger.warning(f"Prediction result is not a dictionary: {type(prediction_result)}")
            prediction_result = {}
        
        # Check if we have meaningful health data
        if not health_data or len(health_data) == 0:
            logger.warning("No health data provided, proceeding with general health advice")
            # Don't return early, continue with general health advice
        
        # Log health data for debugging
        logger.info(f"Health data keys: {list(health_data.keys()) if health_data else 'None'}")
        logger.info(f"Health data sample: {dict(list(health_data.items())[:3]) if health_data else 'None'}")
        logger.info(f"Prediction result keys: {list(prediction_result.keys()) if prediction_result else 'None'}")
            
        # Extract key health metrics with safe defaults and validation
        try:
            age = float(health_data.get('age', 45))
            gender = "Male" if float(health_data.get('gender', 0)) == 1 else "Female"
            bmi = float(health_data.get('bmi', 25))
            blood_pressure = float(health_data.get('blood_pressure', 120))
            glucose = float(health_data.get('glucose_level', 100))
            cholesterol = float(health_data.get('cholesterol_level', 200))
            activity = float(health_data.get('physical_activity', 5))
            smoking = float(health_data.get('smoking_status', 0))
            family_history = float(health_data.get('family_history', 0))
        except (ValueError, TypeError) as e:
            logger.error(f"Error extracting health data: {e}")
            # Use safe defaults
            age = 45
            gender = "Male"
            bmi = 25
            blood_pressure = 120
            glucose = 100
            cholesterol = 200
            activity = 5
            smoking = 0
            family_history = 0
        
        # Convert smoking status to text with bounds checking
        smoking_int = int(smoking)
        if smoking_int < 0 or smoking_int > 2:
            smoking_int = 0
        smoking_status = ["Never", "Former", "Current"][smoking_int]
        
        # Analyze question keywords and intent
        question_lower = question.lower()
        
        # Risk assessment questions
        if any(word in question_lower for word in ['risk', 'chance', 'probability', 'likely', 'develop']):
            if any(word in question_lower for word in ['diabetes', 'diabetic', 'blood sugar', 'glucose']):
                return analyze_diabetes_risk_question(question, health_data, prediction_result)
            elif any(word in question_lower for word in ['hypertension', 'blood pressure', 'high blood pressure', 'bp']):
                return analyze_hypertension_risk_question(question, health_data, prediction_result)
            else:
                return analyze_general_risk_question(question, health_data, prediction_result)
        
        # Lifestyle and prevention questions
        elif any(word in question_lower for word in ['prevent', 'avoid', 'reduce', 'lower', 'improve']):
            return analyze_prevention_question(question, health_data, prediction_result)
        
        # Diet and nutrition questions
        elif any(word in question_lower for word in ['diet', 'food', 'eat', 'nutrition', 'meal', 'carb', 'sugar']):
            return analyze_nutrition_question(question, health_data, prediction_result)
        
        # Exercise and fitness questions
        elif any(word in question_lower for word in ['exercise', 'workout', 'fitness', 'activity', 'gym', 'cardio']):
            return analyze_fitness_question(question, health_data, prediction_result)
        
        # General health questions
        else:
            return analyze_general_health_question(question, health_data, prediction_result)
        
    except Exception as e:
        logger.error(f"Error in analyze_health_question: {e}")
        # Return a safe fallback response
        return HealthAnswer(
            answer="I apologize, but I'm having trouble processing your question right now. Please try again or contact support if the issue persists.",
            confidence="Low",
            related_factors=[],
            follow_up_suggestions=[
                "Try rephrasing your question",
                "Check if you have completed a health assessment",
                "Contact support if the issue continues"
            ],
            disclaimer="This is a fallback response due to a technical issue. Please try again."
        )

def analyze_diabetes_risk_question(question: str, health_data: Dict[str, Any], prediction_result: Dict[str, Any] = None) -> HealthAnswer:
    """Analyze diabetes-related questions with detailed personalized insights"""
    
    # Log the specific health data being analyzed
    logger.info(f"Analyzing diabetes risk for specific health data: {health_data}")
    
    age = health_data.get('age', 45)
    bmi = health_data.get('bmi', 25)
    glucose = health_data.get('glucose_level', 100)
    family_history = health_data.get('family_history', 0)
    activity = health_data.get('physical_activity', 5)
    hba1c = health_data.get('hba1c', None)
    blood_pressure = health_data.get('blood_pressure', 120)
    cholesterol = health_data.get('cholesterol_level', 200)
    smoking = health_data.get('smoking_status', 0)
    alcohol = health_data.get('alcohol_intake', 0)
    sleep_hours = health_data.get('sleep_hours', 7)
    stress_level = health_data.get('stress_level', 5)
    
    # Get prediction results if available
    diabetes_risk = prediction_result.get('diabetes_risk', 0) if prediction_result else 0
    diabetes_confidence = prediction_result.get('diabetes_confidence', 'Unknown') if prediction_result else 'Unknown'
    
    # Ensure diabetes_risk is a valid number
    try:
        diabetes_risk = float(diabetes_risk) if diabetes_risk is not None else 0
    except (ValueError, TypeError):
        logger.warning(f"Invalid diabetes_risk value: {diabetes_risk}, using 0")
        diabetes_risk = 0
    
    # Get hypertension risk with type checking
    hypertension_risk = prediction_result.get('hypertension_risk', 0) if prediction_result else 0
    try:
        hypertension_risk = float(hypertension_risk) if hypertension_risk is not None else 0
    except (ValueError, TypeError):
        logger.warning(f"Invalid hypertension_risk value: {hypertension_risk}, using 0")
        hypertension_risk = 0
    
    # Detailed risk factor analysis
    risk_factors = []
    risk_scores = []
    
    # BMI Analysis
    if bmi > 30:
        risk_factors.append(f"Obesity (BMI: {bmi:.1f}) - Major diabetes risk factor")
        risk_scores.append(3)
    elif bmi > 25:
        risk_factors.append(f"Overweight (BMI: {bmi:.1f}) - Moderate diabetes risk")
        risk_scores.append(2)
    else:
        risk_factors.append(f"Healthy weight (BMI: {bmi:.1f}) - Low diabetes risk")
        risk_scores.append(0)
    
    # Glucose Analysis
    if glucose > 126:
        risk_factors.append(f"Elevated blood glucose ({glucose} mg/dL) - Pre-diabetic range")
        risk_scores.append(3)
    elif glucose > 100:
        risk_factors.append(f"Borderline glucose ({glucose} mg/dL) - Pre-diabetic risk")
        risk_scores.append(2)
    else:
        risk_factors.append(f"Normal glucose ({glucose} mg/dL) - Good metabolic health")
        risk_scores.append(0)
    
    # HbA1c Analysis (if available)
    if hba1c:
        if hba1c >= 6.5:
            risk_factors.append(f"Elevated HbA1c ({hba1c}%) - Diabetes range")
            risk_scores.append(4)
        elif hba1c >= 5.7:
            risk_factors.append(f"Pre-diabetic HbA1c ({hba1c}%) - Increased risk")
            risk_scores.append(3)
        else:
            risk_factors.append(f"Normal HbA1c ({hba1c}%) - Good long-term glucose control")
            risk_scores.append(0)
    
    # Family History
    if family_history:
        risk_factors.append("Family history of diabetes - Genetic predisposition")
        risk_scores.append(2)
    else:
        risk_factors.append("No family history of diabetes - Lower genetic risk")
        risk_scores.append(0)
    
    # Physical Activity
    if activity < 3:
        risk_factors.append(f"Low physical activity ({activity}/10) - Major diabetes risk")
        risk_scores.append(3)
    elif activity < 6:
        risk_factors.append(f"Moderate physical activity ({activity}/10) - Some diabetes risk")
        risk_scores.append(1)
    else:
        risk_factors.append(f"Good physical activity ({activity}/10) - Protective against diabetes")
        risk_scores.append(0)
    
    # Age Factor
    if age > 65:
        risk_factors.append(f"Age {age} - Higher diabetes risk with age")
        risk_scores.append(2)
    elif age > 45:
        risk_factors.append(f"Age {age} - Moderate diabetes risk with age")
        risk_scores.append(1)
    else:
        risk_factors.append(f"Age {age} - Lower diabetes risk")
        risk_scores.append(0)
    
    # Additional Risk Factors
    if blood_pressure > 140:
        risk_factors.append(f"High blood pressure ({blood_pressure} mmHg) - Diabetes risk")
        risk_scores.append(1)
    
    if smoking > 0:
        risk_factors.append(f"Smoking history - Increases diabetes risk")
        risk_scores.append(1)
    
    if sleep_hours < 6:
        risk_factors.append(f"Insufficient sleep ({sleep_hours} hours) - Diabetes risk")
        risk_scores.append(1)
    
    if stress_level > 7:
        risk_factors.append(f"High stress level ({stress_level}/10) - Diabetes risk")
        risk_scores.append(1)
    
    # Calculate total risk score
    total_risk_score = sum(risk_scores)
    
    # Generate detailed personalized response
    if total_risk_score >= 8 or diabetes_risk > 0.5:
        confidence = "High"
        answer = f"""**Your Diabetes Risk Assessment: HIGH RISK**

Based on your specific health assessment, you have multiple significant diabetes risk factors:
{chr(10).join([f"• {factor}" for factor in risk_factors if "risk" in factor.lower() and "protective" not in factor.lower()])}

**Your Assessment Results:**
• **Predicted Diabetes Risk: {diabetes_risk:.1%}** (Based on your specific health profile)
• **Risk Category: {diabetes_confidence}**
• **Metabolic Health Score: {prediction_result.get('metabolic_health_score', 'N/A') if prediction_result else 'N/A'}**

**Immediate Actions Needed:**
• Schedule a comprehensive diabetes screening (HbA1c, fasting glucose, oral glucose tolerance test)
• Consult with an endocrinologist or diabetes specialist
• Consider medication if lifestyle changes aren't sufficient
• Monitor blood glucose levels daily

**Your Specific Risk Factors:**
• BMI: {bmi:.1f} ({'Obesity' if bmi > 30 else 'Overweight' if bmi > 25 else 'Normal weight'})
• Blood Glucose: {glucose} mg/dL ({'Pre-diabetic' if glucose > 100 else 'Normal'})
• Physical Activity: {activity}/10 ({'Low' if activity < 3 else 'Moderate' if activity < 6 else 'Good'})
• Age: {age} years ({'High risk age' if age > 65 else 'Moderate risk age' if age > 45 else 'Lower risk age'})"""
        
    elif total_risk_score >= 4 or diabetes_risk > 0.2:
        confidence = "Moderate"
        answer = f"""**Your Diabetes Risk Assessment: MODERATE RISK**

You have some diabetes risk factors that need attention:
{chr(10).join([f"• {factor}" for factor in risk_factors if "risk" in factor.lower() and "protective" not in factor.lower()])}

**Your Assessment Results:**
• **Predicted Diabetes Risk: {diabetes_risk:.1%}** (Based on your specific health profile)
• **Risk Category: {diabetes_confidence}**
• **Metabolic Health Score: {prediction_result.get('metabolic_health_score', 'N/A') if prediction_result else 'N/A'}**

**Immediate Actions Needed:**
• Get an HbA1c test within 3 months
• Focus on weight management if BMI > 25
• Increase physical activity to at least 150 minutes/week
• Improve diet quality (reduce refined carbs, increase fiber)

**Your Specific Profile:**
• BMI: {bmi:.1f} - {'Needs improvement' if bmi > 25 else 'Good'}
• Blood Glucose: {glucose} mg/dL - {'Monitor closely' if glucose > 100 else 'Normal'}
• Physical Activity: {activity}/10 - {'Needs improvement' if activity < 6 else 'Good'}
• Age: {age} years - {'Monitor closely' if age > 45 else 'Lower risk'}"""
        
    else:
        confidence = "Low"
        answer = f"""**Your Diabetes Risk Assessment: LOW RISK**

Excellent! Your current health profile shows low diabetes risk:
{chr(10).join([f"• {factor}" for factor in risk_factors if "protective" in factor.lower() or "good" in factor.lower() or "normal" in factor.lower()])}

**Your Assessment Results:**
• **Predicted Diabetes Risk: {diabetes_risk:.1%}** (Based on your specific health profile)
• **Risk Category: {diabetes_confidence}**
• **Metabolic Health Score: {prediction_result.get('metabolic_health_score', 'N/A') if prediction_result else 'N/A'}**

**Maintain Your Healthy Habits:**
• Continue regular physical activity ({activity}/10 is great!)
• Maintain healthy weight (BMI {bmi:.1f} is good)
• Keep blood glucose in normal range ({glucose} mg/dL is excellent)
• Regular health checkups every 1-2 years

**Your Healthy Profile:**
• BMI: {bmi:.1f} - Excellent
• Blood Glucose: {glucose} mg/dL - Normal
• Physical Activity: {activity}/10 - Good
• Age: {age} years - {'Monitor as you age' if age > 45 else 'Lower risk age'}"""
    
    # Personalized follow-up suggestions
    follow_up_suggestions = []
    if total_risk_score >= 8:
        follow_up_suggestions = [
            "Schedule immediate diabetes screening with your doctor",
            "Consider working with a diabetes educator",
            "Start daily blood glucose monitoring",
            "Discuss medication options with your healthcare provider"
        ]
    elif total_risk_score >= 4:
        follow_up_suggestions = [
            "Get HbA1c test within 3 months",
            "Start a structured exercise program",
            "Consider working with a nutritionist",
            "Monitor blood glucose monthly"
        ]
    else:
        follow_up_suggestions = [
            "Continue current healthy lifestyle",
            "Get annual health checkups",
            "Maintain regular physical activity",
            "Consider preventive health measures"
        ]
    
    return HealthAnswer(
        answer=answer,
        confidence=confidence,
        related_factors=risk_factors[:5],
        follow_up_suggestions=follow_up_suggestions,
        disclaimer="This assessment is for informational purposes only and should not replace professional medical advice. Consult your healthcare provider for personalized medical guidance."
    )

def analyze_hypertension_risk_question(question: str, health_data: Dict[str, Any], prediction_result: Dict[str, Any] = None) -> HealthAnswer:
    """Analyze hypertension-related questions with detailed personalized insights"""
    age = health_data.get('age', 45)
    blood_pressure = health_data.get('blood_pressure', 120)
    bmi = health_data.get('bmi', 25)
    cholesterol = health_data.get('cholesterol_level', 200)
    glucose = health_data.get('glucose_level', 100)
    family_history = health_data.get('family_history', 0)
    activity = health_data.get('physical_activity', 5)
    smoking = health_data.get('smoking_status', 0)
    alcohol = health_data.get('alcohol_intake', 0)
    sleep_hours = health_data.get('sleep_hours', 7)
    stress_level = health_data.get('stress_level', 5)
    
    # Detailed risk factor analysis
    risk_factors = []
    risk_scores = []
    
    # Blood Pressure Analysis
    if blood_pressure >= 140:
        risk_factors.append(f"Stage 2 Hypertension ({blood_pressure} mmHg) - High risk")
        risk_scores.append(4)
    elif blood_pressure >= 130:
        risk_factors.append(f"Stage 1 Hypertension ({blood_pressure} mmHg) - Elevated risk")
        risk_scores.append(3)
    elif blood_pressure >= 120:
        risk_factors.append(f"Elevated blood pressure ({blood_pressure} mmHg) - Pre-hypertension")
        risk_scores.append(2)
    else:
        risk_factors.append(f"Normal blood pressure ({blood_pressure} mmHg) - Good cardiovascular health")
        risk_scores.append(0)
    
    # BMI Analysis
    if bmi > 30:
        risk_factors.append(f"Obesity (BMI: {bmi:.1f}) - Major hypertension risk")
        risk_scores.append(3)
    elif bmi > 25:
        risk_factors.append(f"Overweight (BMI: {bmi:.1f}) - Moderate hypertension risk")
        risk_scores.append(2)
    else:
        risk_factors.append(f"Healthy weight (BMI: {bmi:.1f}) - Lower hypertension risk")
        risk_scores.append(0)
    
    # Age Factor
    if age > 65:
        risk_factors.append(f"Age {age} - High hypertension risk with age")
        risk_scores.append(3)
    elif age > 45:
        risk_factors.append(f"Age {age} - Moderate hypertension risk with age")
        risk_scores.append(2)
    else:
        risk_factors.append(f"Age {age} - Lower hypertension risk")
        risk_scores.append(0)
    
    # Family History
    if family_history:
        risk_factors.append("Family history of hypertension - Genetic predisposition")
        risk_scores.append(2)
    else:
        risk_factors.append("No family history of hypertension - Lower genetic risk")
        risk_scores.append(0)
    
    # Physical Activity
    if activity < 3:
        risk_factors.append(f"Low physical activity ({activity}/10) - Major hypertension risk")
        risk_scores.append(3)
    elif activity < 6:
        risk_factors.append(f"Moderate physical activity ({activity}/10) - Some hypertension risk")
        risk_scores.append(1)
    else:
        risk_factors.append(f"Good physical activity ({activity}/10) - Protective against hypertension")
        risk_scores.append(0)
    
    # Additional Risk Factors
    if cholesterol > 240:
        risk_factors.append(f"High cholesterol ({cholesterol} mg/dL) - Hypertension risk")
        risk_scores.append(2)
    elif cholesterol > 200:
        risk_factors.append(f"Borderline cholesterol ({cholesterol} mg/dL) - Some hypertension risk")
        risk_scores.append(1)
    
    if glucose > 126:
        risk_factors.append(f"Elevated glucose ({glucose} mg/dL) - Hypertension risk")
        risk_scores.append(2)
    elif glucose > 100:
        risk_factors.append(f"Borderline glucose ({glucose} mg/dL) - Some hypertension risk")
        risk_scores.append(1)
    
    if smoking > 0:
        risk_factors.append(f"Smoking history - Major hypertension risk")
        risk_scores.append(3)
    
    if alcohol > 3:
        risk_factors.append(f"High alcohol intake ({alcohol}/5) - Hypertension risk")
        risk_scores.append(2)
    elif alcohol > 1:
        risk_factors.append(f"Moderate alcohol intake ({alcohol}/5) - Some hypertension risk")
        risk_scores.append(1)
    
    if sleep_hours < 6:
        risk_factors.append(f"Insufficient sleep ({sleep_hours} hours) - Hypertension risk")
        risk_scores.append(2)
    
    if stress_level > 7:
        risk_factors.append(f"High stress level ({stress_level}/10) - Hypertension risk")
        risk_scores.append(2)
    
    # Calculate total risk score
    total_risk_score = sum(risk_scores)
    
    # Generate detailed personalized response
    if total_risk_score >= 10:
        confidence = "High"
        answer = f"""**Your Hypertension Risk Assessment: HIGH RISK**

Based on your health profile, you have multiple significant hypertension risk factors:
{chr(10).join([f"• {factor}" for factor in risk_factors if "risk" in factor.lower() and "protective" not in factor.lower()])}

**Immediate Actions Needed:**
• Schedule immediate blood pressure monitoring (daily for 1 week)
• Consult with a cardiologist or hypertension specialist
• Consider medication if lifestyle changes aren't sufficient
• Monitor blood pressure at home daily

**Your Specific Risk Factors:**
• Blood Pressure: {blood_pressure} mmHg ({'Stage 2 Hypertension' if blood_pressure >= 140 else 'Stage 1 Hypertension' if blood_pressure >= 130 else 'Elevated' if blood_pressure >= 120 else 'Normal'})
• BMI: {bmi:.1f} ({'Obesity' if bmi > 30 else 'Overweight' if bmi > 25 else 'Normal weight'})
• Physical Activity: {activity}/10 ({'Low' if activity < 3 else 'Moderate' if activity < 6 else 'Good'})
• Age: {age} years ({'High risk age' if age > 65 else 'Moderate risk age' if age > 45 else 'Lower risk age'})"""
        
    elif total_risk_score >= 5:
        confidence = "Moderate"
        answer = f"""**Your Hypertension Risk Assessment: MODERATE RISK**

You have some hypertension risk factors that need attention:
{chr(10).join([f"• {factor}" for factor in risk_factors if "risk" in factor.lower() and "protective" not in factor.lower()])}

**Immediate Actions Needed:**
• Monitor blood pressure weekly for 1 month
• Focus on weight management if BMI > 25
• Increase physical activity to at least 150 minutes/week
• Reduce sodium intake to < 2,300mg/day

**Your Specific Profile:**
• Blood Pressure: {blood_pressure} mmHg - {'Needs monitoring' if blood_pressure >= 120 else 'Good'}
• BMI: {bmi:.1f} - {'Needs improvement' if bmi > 25 else 'Good'}
• Physical Activity: {activity}/10 - {'Needs improvement' if activity < 6 else 'Good'}
• Age: {age} years - {'Monitor closely' if age > 45 else 'Lower risk'}"""
        
    else:
        confidence = "Low"
        answer = f"""**Your Hypertension Risk Assessment: LOW RISK**

Excellent! Your current health profile shows low hypertension risk:
{chr(10).join([f"• {factor}" for factor in risk_factors if "protective" in factor.lower() or "good" in factor.lower() or "normal" in factor.lower()])}

**Maintain Your Healthy Habits:**
• Continue regular physical activity ({activity}/10 is great!)
• Maintain healthy weight (BMI {bmi:.1f} is good)
• Keep blood pressure in normal range ({blood_pressure} mmHg is excellent)
• Regular health checkups every 1-2 years

**Your Healthy Profile:**
• Blood Pressure: {blood_pressure} mmHg - Excellent
• BMI: {bmi:.1f} - Good
• Physical Activity: {activity}/10 - Good
• Age: {age} years - {'Monitor as you age' if age > 45 else 'Lower risk age'}"""
    
    # Personalized follow-up suggestions
    follow_up_suggestions = []
    if total_risk_score >= 10:
        follow_up_suggestions = [
            "Schedule immediate blood pressure evaluation with your doctor",
            "Consider working with a hypertension specialist",
            "Start daily blood pressure monitoring at home",
            "Discuss medication options with your healthcare provider"
        ]
    elif total_risk_score >= 5:
        follow_up_suggestions = [
            "Monitor blood pressure weekly for 1 month",
            "Start a structured exercise program",
            "Consider working with a nutritionist for DASH diet",
            "Reduce sodium intake to < 2,300mg/day"
        ]
    else:
        follow_up_suggestions = [
            "Continue current healthy lifestyle",
            "Get annual health checkups",
            "Maintain regular physical activity",
            "Consider preventive health measures"
        ]
    
    return HealthAnswer(
        answer=answer,
        confidence=confidence,
        related_factors=risk_factors[:5],
        follow_up_suggestions=follow_up_suggestions,
        disclaimer="This assessment is for informational purposes only and should not replace professional medical advice. Consult your healthcare provider for personalized medical guidance."
    )

def analyze_prevention_question(question: str, health_data: Dict[str, Any], prediction_result: Dict[str, Any] = None) -> HealthAnswer:
    """Analyze prevention-focused questions"""
    age = health_data.get('age', 45)
    bmi = health_data.get('bmi', 25)
    activity = health_data.get('physical_activity', 5)
    
    prevention_strategies = []
    
    if bmi > 25:
        prevention_strategies.append("weight management through a balanced diet and regular exercise")
    
    if activity < 5:
        prevention_strategies.append("increasing physical activity to at least 150 minutes per week")
    
    prevention_strategies.extend([
        "maintaining a healthy diet rich in fruits, vegetables, and whole grains",
        "limiting processed foods and added sugars",
        "managing stress through relaxation techniques",
        "getting adequate sleep (7-9 hours nightly)",
        "avoiding smoking and limiting alcohol consumption"
    ])
    
    answer = f"Based on your health profile, here are key prevention strategies: {'. '.join(prevention_strategies[:4])}. These lifestyle modifications can significantly reduce your risk of chronic diseases."
    
    return HealthAnswer(
        answer=answer,
        confidence="High",
        related_factors=["lifestyle factors", "preventive measures"],
        follow_up_suggestions=[
            "Set specific, achievable health goals",
            "Track your progress regularly",
            "Consider working with a healthcare provider or nutritionist"
        ],
        disclaimer="This assessment is for informational purposes only and should not replace professional medical advice."
    )

def analyze_nutrition_question(question: str, health_data: Dict[str, Any], prediction_result: Dict[str, Any] = None) -> HealthAnswer:
    """Analyze nutrition-related questions with detailed personalized recommendations"""
    age = health_data.get('age', 45)
    bmi = health_data.get('bmi', 25)
    glucose = health_data.get('glucose_level', 100)
    blood_pressure = health_data.get('blood_pressure', 120)
    cholesterol = health_data.get('cholesterol_level', 200)
    activity = health_data.get('physical_activity', 5)
    hba1c = health_data.get('hba1c', None)
    family_history = health_data.get('family_history', 0)
    smoking = health_data.get('smoking_status', 0)
    alcohol = health_data.get('alcohol_intake', 0)
    sleep_hours = health_data.get('sleep_hours', 7)
    stress_level = health_data.get('stress_level', 5)
    
    # Calculate personalized nutrition needs
    base_calories = 2000 if age < 50 else 1800
    if bmi > 30:
        calorie_target = base_calories - 500  # Weight loss
    elif bmi > 25:
        calorie_target = base_calories - 250  # Moderate weight loss
    else:
        calorie_target = base_calories  # Maintenance
    
    # Protein needs based on activity and age
    protein_needs = 1.2 if activity > 6 else 1.0
    if age > 65:
        protein_needs += 0.2  # Higher protein for older adults
    
    # Detailed nutrition analysis
    nutrition_priorities = []
    specific_recommendations = []
    foods_to_emphasize = []
    foods_to_limit = []
    
    # Blood Sugar Management
    if glucose > 126 or (hba1c and hba1c >= 6.5):
        nutrition_priorities.append("Diabetes Management")
        specific_recommendations.extend([
            "Follow a consistent carbohydrate meal plan",
            "Aim for 45-60g carbs per meal, 15-30g for snacks",
            "Choose low glycemic index foods",
            "Space meals 3-4 hours apart"
        ])
        foods_to_emphasize.extend([
            "Non-starchy vegetables (broccoli, spinach, bell peppers)",
            "Lean proteins (chicken, fish, tofu)",
            "Healthy fats (avocado, nuts, olive oil)",
            "High-fiber foods (berries, beans, quinoa)"
        ])
        foods_to_limit.extend([
            "Refined carbohydrates (white bread, pasta, rice)",
            "Sugary drinks and desserts",
            "Fruit juices and dried fruits",
            "Processed snacks"
        ])
    elif glucose > 100 or (hba1c and hba1c >= 5.7):
        nutrition_priorities.append("Pre-Diabetes Prevention")
        specific_recommendations.extend([
            "Focus on whole, unprocessed foods",
            "Limit added sugars to < 25g daily",
            "Include protein with every meal",
            "Choose complex carbohydrates"
        ])
        foods_to_emphasize.extend([
            "Whole grains (brown rice, oats, quinoa)",
            "Legumes (beans, lentils, chickpeas)",
            "Non-starchy vegetables",
            "Lean proteins"
        ])
        foods_to_limit.extend([
            "Sugary beverages",
            "White bread and pasta",
            "Candy and desserts",
            "Fruit juices"
        ])
    
    # Blood Pressure Management
    if blood_pressure >= 130:
        nutrition_priorities.append("Hypertension Management")
        specific_recommendations.extend([
            "Follow DASH diet principles",
            "Limit sodium to < 2,300mg daily (ideally < 1,500mg)",
            "Increase potassium-rich foods",
            "Limit alcohol to 1 drink/day for women, 2 for men"
        ])
        foods_to_emphasize.extend([
            "Leafy greens (spinach, kale, arugula)",
            "Potassium-rich fruits (bananas, oranges, melons)",
            "Low-fat dairy products",
            "Nuts and seeds (unsalted)"
        ])
        foods_to_limit.extend([
            "Processed and canned foods",
            "Fast food and restaurant meals",
            "Salted snacks and crackers",
            "High-sodium condiments"
        ])
    
    # Weight Management
    if bmi > 30:
        nutrition_priorities.append("Weight Loss")
        specific_recommendations.extend([
            f"Create a {calorie_target - 500} calorie deficit daily",
            "Focus on high-volume, low-calorie foods",
            "Eat protein with every meal to preserve muscle",
            "Practice portion control using smaller plates"
        ])
        foods_to_emphasize.extend([
            "Non-starchy vegetables (unlimited)",
            "Lean proteins (chicken breast, fish, Greek yogurt)",
            "High-fiber foods (berries, apples, vegetables)",
            "Water and herbal teas"
        ])
        foods_to_limit.extend([
            "High-calorie beverages",
            "Fried foods and fast food",
            "Large portions of starchy foods",
            "High-calorie snacks"
        ])
    elif bmi > 25:
        nutrition_priorities.append("Weight Management")
        specific_recommendations.extend([
            f"Moderate calorie reduction to {calorie_target} calories daily",
            "Focus on nutrient density",
            "Practice mindful eating",
            "Include regular physical activity"
        ])
    
    # Cholesterol Management
    if cholesterol > 240:
        nutrition_priorities.append("Cholesterol Management")
        specific_recommendations.extend([
            "Limit saturated fat to < 7% of daily calories",
            "Increase soluble fiber intake",
            "Include plant sterols and stanols",
            "Choose lean proteins and fish"
        ])
        foods_to_emphasize.extend([
            "Oatmeal and high-fiber cereals",
            "Fatty fish (salmon, mackerel, sardines)",
            "Nuts and seeds (walnuts, almonds)",
            "Fruits and vegetables"
        ])
        foods_to_limit.extend([
            "Red meat and processed meats",
            "Full-fat dairy products",
            "Fried foods",
            "Trans fats and hydrogenated oils"
        ])
    
    # Age-Specific Recommendations
    if age > 65:
        nutrition_priorities.append("Aging Health")
        specific_recommendations.extend([
            "Increase protein intake to preserve muscle mass",
            "Focus on calcium and vitamin D for bone health",
            "Include B12-rich foods or supplements",
            "Stay hydrated with 8+ glasses of water daily"
        ])
        foods_to_emphasize.extend([
            "Lean proteins (fish, poultry, beans)",
            "Dairy products (milk, yogurt, cheese)",
            "Leafy greens (spinach, kale)",
            "Berries and citrus fruits"
        ])
    
    # Activity-Based Adjustments
    if activity > 7:
        specific_recommendations.extend([
            "Increase carbohydrate intake for energy",
            "Include pre and post-workout nutrition",
            "Stay well-hydrated during exercise",
            "Focus on recovery nutrition"
        ])
        foods_to_emphasize.extend([
            "Complex carbohydrates (sweet potatoes, quinoa)",
            "Lean proteins for muscle repair",
            "Hydrating foods (watermelon, cucumbers)",
            "Anti-inflammatory foods (berries, turmeric)"
        ])
    
    # Generate comprehensive response
    if nutrition_priorities:
        answer = f"""**Your Personalized Nutrition Plan**

**Primary Focus Areas:**
{chr(10).join([f"• {priority}" for priority in nutrition_priorities])}

**Your Health Profile:**
• BMI: {bmi:.1f} ({'Obesity' if bmi > 30 else 'Overweight' if bmi > 25 else 'Healthy weight'})
• Blood Glucose: {glucose} mg/dL ({'Pre-diabetic' if glucose > 100 else 'Normal'})
• Blood Pressure: {blood_pressure} mmHg ({'High' if blood_pressure >= 130 else 'Normal'})
• Cholesterol: {cholesterol} mg/dL ({'High' if cholesterol > 240 else 'Normal'})
• Physical Activity: {activity}/10 ({'High' if activity > 7 else 'Moderate' if activity > 4 else 'Low'})

**Specific Recommendations:**
{chr(10).join([f"• {rec}" for rec in specific_recommendations[:6]])}

**Foods to Emphasize:**
{chr(10).join([f"• {food}" for food in foods_to_emphasize[:8]])}

**Foods to Limit:**
{chr(10).join([f"• {food}" for food in foods_to_limit[:6]])}

**Daily Targets:**
• Calories: {calorie_target} per day
• Protein: {protein_needs:.1f}g per kg body weight
• Fiber: 25-35g daily
• Water: 8+ glasses daily"""
    else:
        answer = f"""**Your Nutrition Assessment: EXCELLENT FOUNDATION**

Your current health profile shows good metabolic health:
• BMI: {bmi:.1f} - Healthy weight
• Blood Glucose: {glucose} mg/dL - Normal
• Blood Pressure: {blood_pressure} mmHg - Normal
• Cholesterol: {cholesterol} mg/dL - Normal

**Maintain Your Healthy Habits:**
• Continue eating whole, unprocessed foods
• Maintain balanced macronutrients
• Stay hydrated with water
• Include regular physical activity

**Daily Targets:**
• Calories: {calorie_target} per day
• Protein: {protein_needs:.1f}g per kg body weight
• Focus on variety and moderation"""
    
    # Personalized follow-up suggestions
    follow_up_suggestions = [
        "Consider working with a registered dietitian for personalized meal planning",
        "Track your food intake for 1-2 weeks to identify patterns",
        "Gradually implement changes rather than making drastic shifts",
        "Monitor your health markers regularly to assess progress"
    ]
    
    if bmi > 25:
        follow_up_suggestions.append("Focus on sustainable weight loss of 1-2 pounds per week")
    if blood_pressure >= 130:
        follow_up_suggestions.append("Consider the DASH diet for blood pressure management")
    if glucose > 100:
        follow_up_suggestions.append("Monitor carbohydrate intake and blood sugar response")
    
    return HealthAnswer(
        answer=answer,
        confidence="High",
        related_factors=nutrition_priorities[:3],
        follow_up_suggestions=follow_up_suggestions,
        disclaimer="This nutrition advice is for informational purposes only and should not replace professional medical or nutritional guidance. Consult with a registered dietitian for personalized meal planning."
    )

def analyze_fitness_question(question: str, health_data: Dict[str, Any], prediction_result: Dict[str, Any] = None) -> HealthAnswer:
    """Analyze fitness-related questions with detailed personalized exercise plans"""
    age = health_data.get('age', 45)
    bmi = health_data.get('bmi', 25)
    blood_pressure = health_data.get('blood_pressure', 120)
    glucose = health_data.get('glucose_level', 100)
    cholesterol = health_data.get('cholesterol_level', 200)
    activity = health_data.get('physical_activity', 5)
    family_history = health_data.get('family_history', 0)
    smoking = health_data.get('smoking_status', 0)
    sleep_hours = health_data.get('sleep_hours', 7)
    stress_level = health_data.get('stress_level', 5)
    daily_steps = health_data.get('daily_steps', 7000)
    
    # Calculate personalized fitness needs
    fitness_priorities = []
    exercise_recommendations = []
    intensity_guidelines = []
    frequency_guidelines = []
    specific_exercises = []
    precautions = []
    
    # Current Fitness Level Assessment
    if activity >= 8:
        fitness_level = "Advanced"
        base_weekly_minutes = 300
    elif activity >= 6:
        fitness_level = "Intermediate"
        base_weekly_minutes = 200
    elif activity >= 4:
        fitness_level = "Beginner"
        base_weekly_minutes = 150
    else:
        fitness_level = "Sedentary"
        base_weekly_minutes = 100
    
    # Health-Specific Exercise Priorities
    if bmi > 30:
        fitness_priorities.append("Weight Loss")
        exercise_recommendations.extend([
            "Focus on low-impact cardio to protect joints",
            "Include strength training to preserve muscle mass",
            "Start with 20-30 minutes of moderate activity",
            "Gradually increase duration and intensity"
        ])
        specific_exercises.extend([
            "Walking (start with 10-15 minutes)",
            "Swimming or water aerobics",
            "Cycling (stationary or outdoor)",
            "Light strength training with body weight"
        ])
        precautions.extend([
            "Avoid high-impact activities initially",
            "Listen to your body and rest when needed",
            "Consider working with a trainer for proper form"
        ])
    elif bmi > 25:
        fitness_priorities.append("Weight Management")
        exercise_recommendations.extend([
            "Combine cardio and strength training",
            "Aim for 150-300 minutes of moderate activity weekly",
            "Include high-intensity interval training (HIIT)",
            "Focus on building lean muscle mass"
        ])
        specific_exercises.extend([
            "Brisk walking or jogging",
            "Strength training 2-3 times per week",
            "HIIT workouts 1-2 times per week",
            "Yoga or Pilates for flexibility"
        ])
    
    # Blood Pressure Management
    if blood_pressure >= 130:
        fitness_priorities.append("Blood Pressure Control")
        exercise_recommendations.extend([
            "Focus on aerobic exercises for cardiovascular health",
            "Include moderate-intensity activities",
            "Avoid high-intensity exercises initially",
            "Include stress-reducing activities"
        ])
        specific_exercises.extend([
            "Walking, cycling, or swimming",
            "Yoga and meditation",
            "Tai chi or gentle stretching",
            "Breathing exercises"
        ])
        precautions.extend([
            "Monitor blood pressure before and after exercise",
            "Avoid heavy lifting or straining",
            "Stop if you feel dizzy or short of breath"
        ])
    
    # Blood Sugar Management
    if glucose > 100:
        fitness_priorities.append("Blood Sugar Control")
        exercise_recommendations.extend([
            "Include both aerobic and resistance training",
            "Exercise after meals to help with glucose control",
            "Aim for consistency rather than intensity",
            "Include post-meal walks"
        ])
        specific_exercises.extend([
            "Walking after meals (10-15 minutes)",
            "Resistance training 2-3 times per week",
            "Aerobic activities (cycling, swimming)",
            "Balance and flexibility exercises"
        ])
        precautions.extend([
            "Monitor blood sugar before and after exercise",
            "Keep glucose tablets or snacks available",
            "Stay hydrated during exercise"
        ])
    
    # Age-Specific Recommendations
    if age > 65:
        fitness_priorities.append("Aging Health")
        exercise_recommendations.extend([
            "Focus on balance and flexibility",
            "Include strength training to prevent muscle loss",
            "Low-impact activities to protect joints",
            "Regular physical activity for cognitive health"
        ])
        specific_exercises.extend([
            "Walking or gentle hiking",
            "Water aerobics or swimming",
            "Light strength training with resistance bands",
            "Balance exercises (tai chi, yoga)"
        ])
        precautions.extend([
            "Start slowly and progress gradually",
            "Focus on proper form over intensity",
            "Include warm-up and cool-down periods"
        ])
    elif age > 50:
        fitness_priorities.append("Midlife Health")
        exercise_recommendations.extend([
            "Maintain muscle mass with strength training",
            "Include cardiovascular exercises",
            "Focus on bone health with weight-bearing activities",
            "Include flexibility and mobility work"
        ])
        specific_exercises.extend([
            "Moderate-intensity cardio (brisk walking, cycling)",
            "Strength training 2-3 times per week",
            "Yoga or Pilates for flexibility",
            "Weight-bearing exercises (walking, dancing)"
        ])
    
    # Current Activity Level Adjustments
    if activity < 3:
        fitness_priorities.append("Building Exercise Habit")
        exercise_recommendations.extend([
            "Start with 10-15 minutes of light activity",
            "Focus on consistency over intensity",
            "Choose activities you enjoy",
            "Set realistic, achievable goals"
        ])
        specific_exercises.extend([
            "Short walks around the neighborhood",
            "Gentle stretching or yoga",
            "Household activities (gardening, cleaning)",
            "Dancing to music at home"
        ])
    elif activity < 6:
        fitness_priorities.append("Increasing Activity")
        exercise_recommendations.extend([
            "Gradually increase duration and intensity",
            "Add variety to prevent boredom",
            "Include both cardio and strength training",
            "Set progressive goals"
        ])
        specific_exercises.extend([
            "Brisk walking or jogging",
            "Bodyweight exercises",
            "Cycling or swimming",
            "Group fitness classes"
        ])
    else:
        fitness_priorities.append("Optimizing Performance")
        exercise_recommendations.extend([
            "Include high-intensity training",
            "Focus on sport-specific training",
            "Include recovery and rest days",
            "Monitor performance metrics"
        ])
        specific_exercises.extend([
            "HIIT workouts",
            "Advanced strength training",
            "Sport-specific drills",
            "Cross-training activities"
        ])
    
    # Generate comprehensive response
    if fitness_priorities:
        answer = f"""**Your Personalized Fitness Plan**

**Primary Focus Areas:**
{chr(10).join([f"• {priority}" for priority in fitness_priorities])}

**Your Health Profile:**
• Current Activity Level: {activity}/10 ({fitness_level})
• BMI: {bmi:.1f} ({'Obesity' if bmi > 30 else 'Overweight' if bmi > 25 else 'Healthy weight'})
• Blood Pressure: {blood_pressure} mmHg ({'High' if blood_pressure >= 130 else 'Normal'})
• Blood Glucose: {glucose} mg/dL ({'Pre-diabetic' if glucose > 100 else 'Normal'})
• Age: {age} years ({'Senior' if age > 65 else 'Midlife' if age > 50 else 'Young adult'})

**Exercise Recommendations:**
{chr(10).join([f"• {rec}" for rec in exercise_recommendations[:6]])}

**Specific Exercises for You:**
{chr(10).join([f"• {exercise}" for exercise in specific_exercises[:8]])}

**Weekly Schedule:**
• Aerobic Exercise: {base_weekly_minutes} minutes per week
• Strength Training: 2-3 times per week
• Flexibility/Mobility: Daily stretching
• Balance Training: 2-3 times per week (if 65+)

**Intensity Guidelines:**
• Moderate Intensity: You can talk but not sing
• Vigorous Intensity: You can say a few words but not a sentence
• Start at 60-70% of maximum heart rate
• Progress gradually over 4-6 weeks

**Important Precautions:**
{chr(10).join([f"• {precaution}" for precaution in precautions[:4]])}"""
    else:
        answer = f"""**Your Fitness Assessment: EXCELLENT FOUNDATION**

Your current health profile shows good fitness potential:
• Activity Level: {activity}/10 ({fitness_level})
• BMI: {bmi:.1f} - Healthy weight
• Blood Pressure: {blood_pressure} mmHg - Normal
• Blood Glucose: {glucose} mg/dL - Normal

**Maintain Your Active Lifestyle:**
• Continue your current exercise routine
• Include variety to prevent plateaus
• Focus on progressive overload
• Include recovery and rest days

**Weekly Schedule:**
• Aerobic Exercise: {base_weekly_minutes} minutes per week
• Strength Training: 2-3 times per week
• Flexibility: Daily stretching
• Active Recovery: Light activities on rest days"""
    
    # Personalized follow-up suggestions
    follow_up_suggestions = [
        "Start with activities you enjoy to build consistency",
        "Track your progress with a fitness app or journal",
        "Consider working with a personal trainer for proper form",
        "Listen to your body and adjust intensity as needed"
    ]
    
    if activity < 4:
        follow_up_suggestions.append("Start with just 10 minutes daily and build up gradually")
    if bmi > 25:
        follow_up_suggestions.append("Focus on sustainable weight loss through consistent exercise")
    if blood_pressure >= 130:
        follow_up_suggestions.append("Monitor blood pressure and consult your doctor before starting")
    if age > 65:
        follow_up_suggestions.append("Include balance and flexibility exercises for fall prevention")
    
    return HealthAnswer(
        answer=answer,
        confidence="High",
        related_factors=fitness_priorities[:3],
        follow_up_suggestions=follow_up_suggestions,
        disclaimer="This fitness advice is for informational purposes only and should not replace professional medical or fitness guidance. Consult with your healthcare provider before starting any new exercise program."
    )

def analyze_general_health_question(question: str, health_data: Dict[str, Any], prediction_result: Dict[str, Any] = None) -> HealthAnswer:
    """Analyze general health questions"""
    age = health_data.get('age', 45)
    bmi = health_data.get('bmi', 25)
    blood_pressure = health_data.get('blood_pressure', 120)
    glucose = health_data.get('glucose_level', 100)
    
    health_summary = f"Based on your health assessment (Age: {age}, BMI: {bmi:.1f}, Blood Pressure: {blood_pressure} mmHg, Glucose: {glucose} mg/dL), "
    
    if bmi > 30 or blood_pressure >= 140 or glucose >= 126:
        health_summary += "you have some health markers that need attention. Focus on lifestyle modifications including diet, exercise, and stress management. Consider consulting with healthcare providers for personalized guidance."
        confidence = "High"
    elif bmi > 25 or blood_pressure >= 130 or glucose >= 100:
        health_summary += "you have some elevated health markers. Small lifestyle changes can make a significant difference. Focus on maintaining a healthy weight, regular exercise, and a balanced diet."
        confidence = "Moderate"
    else:
        health_summary += "your health markers are generally in good ranges. Continue maintaining your healthy lifestyle habits and regular health checkups."
        confidence = "Low"
    
    return HealthAnswer(
        answer=health_summary,
        confidence=confidence,
        related_factors=["overall health", "lifestyle factors"],
        follow_up_suggestions=[
            "Continue regular health monitoring",
            "Maintain consistent healthy habits",
            "Schedule regular checkups with your healthcare provider"
        ],
        disclaimer="This assessment is for informational purposes only and should not replace professional medical advice."
    )

def analyze_general_risk_question(question: str, health_data: Dict[str, Any], prediction_result: Dict[str, Any] = None) -> HealthAnswer:
    """Analyze general risk assessment questions"""
    age = health_data.get('age', 45)
    bmi = health_data.get('bmi', 25)
    blood_pressure = health_data.get('blood_pressure', 120)
    glucose = health_data.get('glucose_level', 100)
    family_history = health_data.get('family_history', 0)
    
    risk_factors = []
    protective_factors = []
    
    # Assess risk factors
    if age > 45:
        risk_factors.append("age over 45")
    if bmi > 30:
        risk_factors.append("obesity")
    elif bmi > 25:
        risk_factors.append("overweight")
    if blood_pressure >= 140:
        risk_factors.append("high blood pressure")
    if glucose >= 126:
        risk_factors.append("elevated blood glucose")
    if family_history:
        risk_factors.append("family history of chronic diseases")
    
    # Assess protective factors
    if bmi < 25:
        protective_factors.append("healthy weight")
    if blood_pressure < 120:
        protective_factors.append("normal blood pressure")
    if glucose < 100:
        protective_factors.append("normal blood glucose")
    if not family_history:
        protective_factors.append("no family history of chronic diseases")
    
    if len(risk_factors) > len(protective_factors):
        answer = f"Your health profile shows several risk factors: {', '.join(risk_factors[:3])}. However, you also have some protective factors: {', '.join(protective_factors[:2])}. Focus on addressing the modifiable risk factors through lifestyle changes."
        confidence = "High"
    elif len(risk_factors) == len(protective_factors):
        answer = f"Your health profile shows a balance of risk factors ({', '.join(risk_factors[:2])}) and protective factors ({', '.join(protective_factors[:2])}). Continue maintaining your healthy habits while addressing areas for improvement."
        confidence = "Moderate"
    else:
        answer = f"Your health profile shows good protective factors: {', '.join(protective_factors[:3])}. Continue maintaining these healthy habits to preserve your good health status."
        confidence = "High"
    
    return HealthAnswer(
        answer=answer,
        confidence=confidence,
        related_factors=risk_factors[:3] + protective_factors[:2],
        follow_up_suggestions=[
            "Focus on modifiable risk factors",
            "Maintain protective factors",
            "Regular health monitoring"
        ],
        disclaimer="This assessment is for informational purposes only and should not replace professional medical advice."
    )


@app.get("/assessments/recent", response_model=List[RecentAssessment])
async def get_recent_assessments(limit: int = 10, current_user: dict = Depends(get_current_active_user)):
    """Get user's recent health assessments"""
    try:
        logger.info("Fetching recent assessments")
        predictions_collection = get_predictions_collection()
        
        # Fetch recent assessments for the authenticated user
        logger.info(f"Searching for assessments for user: {current_user['id']}")
        
        recent_assessments = list(predictions_collection.find(
            {"user_id": current_user["id"]},
            sort=[("created_at", -1)],
            limit=limit
        ))
        
        logger.info(f"Found {len(recent_assessments)} assessments")
        
        if not recent_assessments:
            logger.info("No assessments found")
            return []
        
        # Format the data for response
        formatted_assessments = []
        for assessment in recent_assessments:
            logger.info(f"Processing assessment {assessment.get('_id')} with input_data: {assessment.get('input_data')}")
            # Calculate overall score (average of metabolic and cardiovascular scores)
            metabolic_score = assessment.get("metabolic_health_score", 0)
            cardiovascular_score = assessment.get("cardiovascular_health_score", 0)
            overall_score = round((metabolic_score + cardiovascular_score) / 2, 1)
            
            formatted_assessment = RecentAssessment(
                id=str(assessment["_id"]),
                date=assessment["created_at"].strftime("%Y-%m-%d"),
                diabetes_risk=round(assessment.get("diabetes_risk", 0) * 100, 1),
                hypertension_risk=round(assessment.get("hypertension_risk", 0) * 100, 1),
                metabolic_health_score=round(metabolic_score, 1),
                cardiovascular_health_score=round(cardiovascular_score, 1),
                overall_score=overall_score,
                risk_category_diabetes=assessment.get("risk_category_diabetes", "Unknown"),
                risk_category_hypertension=assessment.get("risk_category_hypertension", "Unknown"),
                input_data=assessment.get("input_data", {})
            )
            formatted_assessments.append(formatted_assessment)
        
        logger.info(f"Retrieved {len(formatted_assessments)} recent assessments")
        logger.info(f"Sample assessment input_data: {formatted_assessments[0].input_data if formatted_assessments else 'No assessments'}")
        return formatted_assessments
        
    except Exception as e:
        logger.error(f"Error fetching recent assessments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch recent assessments: {str(e)}")

# Q&A Helper Function
def generate_personalized_health_answer(question: str, health_data: Dict[str, Any]) -> HealthAnswer:
    """Generate personalized health answers based on user's health data"""
    try:
        # Debug logging
        logger.info(f"generate_personalized_health_answer called with question: {question[:50]}...")
        logger.info(f"Health data received: {health_data}")
        logger.info(f"Health data type: {type(health_data)}")
        logger.info(f"Health data keys: {list(health_data.keys()) if health_data else 'None'}")
        logger.info(f"Diabetes risk in health_data: {health_data.get('diabetes_risk', 'NOT FOUND')}")
        logger.info(f"Hypertension risk in health_data: {health_data.get('hypertension_risk', 'NOT FOUND')}")
        
        # Additional debugging for risk scores
        if 'diabetes_risk' in health_data:
            diabetes_raw = health_data.get('diabetes_risk')
            diabetes_converted = diabetes_raw * 100 if diabetes_raw <= 1.0 else diabetes_raw
            logger.info(f"Main Q&A - Diabetes: {diabetes_raw} -> {diabetes_converted}%")
        
        if 'hypertension_risk' in health_data:
            hypertension_raw = health_data.get('hypertension_risk')
            hypertension_converted = hypertension_raw * 100 if hypertension_raw <= 1.0 else hypertension_raw
            logger.info(f"Main Q&A - Hypertension: {hypertension_raw} -> {hypertension_converted}%")
        
        # Extract key health metrics with safe defaults and type conversion
        try:
            age = float(health_data.get('age', 45))
            gender = "Male" if float(health_data.get('gender', 0)) == 1 else "Female"
            bmi = float(health_data.get('bmi', 25))
            blood_pressure = float(health_data.get('blood_pressure', 120))
            glucose = float(health_data.get('glucose_level', 100))
            cholesterol = float(health_data.get('cholesterol_level', 200))
            activity = float(health_data.get('physical_activity', 5))
            smoking = int(health_data.get('smoking_status', 0))
            family_history = int(health_data.get('family_history', 0))
            alcohol = int(health_data.get('alcohol_intake', 0))
            sleep_hours = float(health_data.get('sleep_hours', 7))
            stress_level = float(health_data.get('stress_level', 5))
            
            # Log extracted values
            logger.info(f"Extracted values - age: {age}, gender: {gender}, bmi: {bmi}, bp: {blood_pressure}, glucose: {glucose}")
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting health data values: {e}")
            logger.error(f"Health data values: {health_data}")
            # Use safe defaults
            age = 45
            gender = "Male"
            bmi = 25
            blood_pressure = 120
            glucose = 100
            cholesterol = 200
            activity = 5
            smoking = 0
            family_history = 0
            alcohol = 0
            sleep_hours = 7
            stress_level = 5
        
        # Analyze question type and generate personalized response
        question_lower = question.lower()
        
        # Diabetes-related questions
        if any(word in question_lower for word in ['diabetes', 'diabetic', 'blood sugar', 'glucose', 'sugar', 'insulin', 'prediabetes']):
            return generate_diabetes_answer(question, health_data, age, gender, bmi, glucose, activity, smoking, family_history)
        
        # Hypertension-related questions
        elif any(word in question_lower for word in ['hypertension', 'blood pressure', 'high blood pressure', 'bp', 'heart', 'cardiovascular']):
            return generate_hypertension_answer(question, health_data, age, gender, bmi, blood_pressure, cholesterol, activity, smoking)
        
        # Nutrition-related questions
        elif any(word in question_lower for word in ['diet', 'food', 'eat', 'nutrition', 'meal', 'carb', 'sugar', 'dietary', 'nutrients']):
            return generate_nutrition_answer(question, health_data, bmi, glucose, cholesterol, activity)
        
        # Exercise-related questions
        elif any(word in question_lower for word in ['exercise', 'workout', 'fitness', 'activity', 'gym', 'cardio', 'strength', 'training']):
            return generate_fitness_answer(question, health_data, age, bmi, activity, blood_pressure)
        
        # Sleep-related questions
        elif any(word in question_lower for word in ['sleep', 'insomnia', 'rest', 'fatigue', 'tired', 'energy', 'sleeping']):
            return generate_sleep_answer(question, health_data, age, sleep_hours, stress_level, activity)
        
        # Mental health questions
        elif any(word in question_lower for word in ['stress', 'anxiety', 'mental', 'mood', 'depression', 'wellbeing', 'mental health', 'psychological']):
            return generate_mental_health_answer(question, health_data, age, stress_level, sleep_hours, activity)
        
        # Lifestyle questions
        elif any(word in question_lower for word in ['lifestyle', 'habits', 'routine', 'daily', 'prevention', 'wellness', 'healthy living']):
            return generate_lifestyle_answer(question, health_data, age, gender, bmi, activity, smoking, alcohol, sleep_hours)
        
        # Medication questions
        elif any(word in question_lower for word in ['medication', 'drugs', 'treatment', 'therapy', 'supplements', 'vitamins', 'pills']):
            return generate_medication_answer(question, health_data, age, gender, bmi, blood_pressure, glucose, cholesterol)
        
        # Symptoms questions
        elif any(word in question_lower for word in ['symptoms', 'signs', 'warning', 'alerts', 'pain', 'discomfort', 'feeling']):
            return generate_symptoms_answer(question, health_data, age, gender, bmi, blood_pressure, glucose, cholesterol)
        
        # General health questions
        else:
            return generate_general_health_answer(question, health_data, age, gender, bmi, blood_pressure, glucose, activity)
            
    except Exception as e:
        logger.error(f"Error generating health answer: {e}")
        return HealthAnswer(
            answer="I apologize, but I'm having trouble processing your question right now. Please try again.",
            confidence="Low",
            related_factors=[],
            follow_up_suggestions=["Try rephrasing your question", "Contact support if the issue continues"],
            disclaimer="This is a fallback response due to a technical issue."
        )

def generate_diabetes_answer(question: str, health_data: Dict, age: int, gender: str, bmi: float, glucose: float, activity: float, smoking: int, family_history: int) -> HealthAnswer:
    """Generate personalized diabetes-related answers"""
    
    # Analyze risk factors
    risk_factors = []
    if bmi > 30:
        risk_factors.append(f"obesity (BMI: {bmi:.1f})")
    elif bmi > 25:
        risk_factors.append(f"overweight (BMI: {bmi:.1f})")
    
    if glucose > 126:
        risk_factors.append(f"elevated blood glucose ({glucose} mg/dL)")
    elif glucose > 100:
        risk_factors.append(f"pre-diabetic glucose levels ({glucose} mg/dL)")
    
    if activity < 3:
        risk_factors.append("low physical activity")
    
    if smoking > 0:
        risk_factors.append("smoking history")
    
    if family_history:
        risk_factors.append("family history of diabetes")
    
    if age > 45:
        risk_factors.append("age over 45")
    
    # Get actual diabetes risk from assessment results
    diabetes_risk_raw = health_data.get('diabetes_risk', 0)
    
    # Convert decimal to percentage if needed (0.852 -> 85.2)
    if diabetes_risk_raw <= 1.0:
        diabetes_risk = diabetes_risk_raw * 100
    else:
        diabetes_risk = diabetes_risk_raw
    
    # Debug logging
    logger.info(f"Diabetes Q&A - Raw risk score: {diabetes_risk_raw}")
    logger.info(f"Diabetes Q&A - Converted risk score: {diabetes_risk}")
    logger.info(f"Diabetes Q&A - Health data keys: {list(health_data.keys()) if health_data else 'None'}")
    
    # Generate personalized response based on actual risk score
    if diabetes_risk >= 70:
        confidence = "High"
        answer = f"""**Your Diabetes Risk Assessment: VERY HIGH RISK**

🚨 CRITICAL: Your actual diabetes risk is {diabetes_risk:.1f}% - This is VERY HIGH and requires immediate attention.

**Your Specific Risk Factors:**
• BMI: {bmi:.1f} ({'Obesity' if bmi > 30 else 'Overweight' if bmi > 25 else 'Normal weight'})
• Blood Glucose: {glucose} mg/dL ({'Pre-diabetic' if glucose > 100 else 'Normal'})
• Physical Activity: {activity}/10 ({'Low' if activity < 3 else 'Moderate' if activity < 6 else 'Good'})
• Age: {age} years ({'High risk age' if age > 65 else 'Moderate risk age' if age > 45 else 'Lower risk age'})

**IMMEDIATE ACTIONS REQUIRED:**
• Schedule a comprehensive diabetes screening (HbA1c, fasting glucose) IMMEDIATELY
• Consult with an endocrinologist or diabetes specialist within 1-2 weeks
• Consider diabetes medication as recommended by your doctor
• Monitor blood glucose levels daily
• Implement strict dietary changes immediately"""
    elif diabetes_risk >= 50:
        confidence = "High"
        answer = f"""**Your Diabetes Risk Assessment: HIGH RISK**

⚠️ Your actual diabetes risk is {diabetes_risk:.1f}% - This is HIGH and needs urgent attention.

**Your Specific Risk Factors:**
• BMI: {bmi:.1f} ({'Obesity' if bmi > 30 else 'Overweight' if bmi > 25 else 'Normal weight'})
• Blood Glucose: {glucose} mg/dL ({'Pre-diabetic' if glucose > 100 else 'Normal'})
• Physical Activity: {activity}/10 ({'Low' if activity < 3 else 'Moderate' if activity < 6 else 'Good'})
• Age: {age} years ({'High risk age' if age > 65 else 'Moderate risk age' if age > 45 else 'Lower risk age'})

**URGENT ACTIONS NEEDED:**
• Schedule a comprehensive diabetes screening (HbA1c, fasting glucose) within 2 weeks
• Consult with an endocrinologist or diabetes specialist
• Focus on weight management if BMI > 25
• Increase physical activity to at least 150 minutes/week
• Monitor blood glucose levels regularly"""
        
    elif diabetes_risk >= 25:
        confidence = "Medium"
        answer = f"""**Your Diabetes Risk Assessment: MODERATE RISK**

Your actual diabetes risk is {diabetes_risk:.1f}% - This is MODERATE and needs attention.

**Your Specific Profile:**
• BMI: {bmi:.1f} - {'Needs improvement' if bmi > 25 else 'Good'}
• Blood Glucose: {glucose} mg/dL - {'Monitor closely' if glucose > 100 else 'Normal'}
• Physical Activity: {activity}/10 - {'Needs improvement' if activity < 6 else 'Good'}
• Age: {age} years - {'Monitor closely' if age > 45 else 'Lower risk'}

**Recommended Actions:**
• Get an HbA1c test within 3 months
• Focus on weight management if BMI > 25
• Increase physical activity to at least 150 minutes/week
• Improve diet quality (reduce refined carbs, increase fiber)"""
        
    else:
        confidence = "High"
        answer = f"""**Your Diabetes Risk Assessment: LOW RISK**

✅ Good news! Your actual diabetes risk is {diabetes_risk:.1f}% - This is LOW.

**Your Healthy Profile:**
• BMI: {bmi:.1f} - Excellent
• Blood Glucose: {glucose} mg/dL - Normal
• Physical Activity: {activity}/10 - Good
• Age: {age} years - Lower risk

**Maintain Your Healthy Habits:**
• Continue regular physical activity ({activity}/10 is great!)
• Maintain healthy weight (BMI {bmi:.1f} is good)
• Keep blood glucose in normal range ({glucose} mg/dL is excellent)
• Regular health checkups every 1-2 years"""
    
    return HealthAnswer(
        answer=answer,
        confidence=confidence,
        related_factors=risk_factors[:3] if risk_factors else ["healthy lifestyle"],
        follow_up_suggestions=[
            "Schedule regular health checkups",
            "Monitor your health metrics",
            "Maintain healthy lifestyle habits"
        ],
        disclaimer="This assessment is for informational purposes only and should not replace professional medical advice."
    )

def generate_hypertension_answer(question: str, health_data: Dict, age: int, gender: str, bmi: float, blood_pressure: float, cholesterol: float, activity: float, smoking: int) -> HealthAnswer:
    """Generate personalized hypertension-related answers"""
    
    # Get actual hypertension risk from assessment results
    hypertension_risk_raw = health_data.get('hypertension_risk', 0)
    
    # Convert decimal to percentage if needed (0.887 -> 88.7)
    if hypertension_risk_raw <= 1.0:
        hypertension_risk = hypertension_risk_raw * 100
    else:
        hypertension_risk = hypertension_risk_raw
    
    # Debug logging
    logger.info(f"Hypertension Q&A - Raw risk score: {hypertension_risk_raw}")
    logger.info(f"Hypertension Q&A - Converted risk score: {hypertension_risk}")
    logger.info(f"Hypertension Q&A - Health data keys: {list(health_data.keys()) if health_data else 'None'}")
    
    # Analyze risk factors
    risk_factors = []
    if blood_pressure >= 140:
        risk_factors.append(f"high blood pressure ({blood_pressure} mmHg)")
    elif blood_pressure >= 130:
        risk_factors.append(f"elevated blood pressure ({blood_pressure} mmHg)")
    
    if bmi > 30:
        risk_factors.append(f"obesity (BMI: {bmi:.1f})")
    elif bmi > 25:
        risk_factors.append(f"overweight (BMI: {bmi:.1f})")
    
    if cholesterol > 240:
        risk_factors.append(f"high cholesterol ({cholesterol} mg/dL)")
    
    if activity < 3:
        risk_factors.append("low physical activity")
    
    if smoking > 0:
        risk_factors.append("smoking history")
    
    if age > 65:
        risk_factors.append("age over 65")
    
    # Generate personalized response based on actual risk score
    if hypertension_risk >= 70:
        confidence = "High"
        answer = f"""**Your Hypertension Risk Assessment: VERY HIGH RISK**

🚨 CRITICAL: Your actual hypertension risk is {hypertension_risk:.1f}% - This is VERY HIGH and requires immediate attention.

**Your Specific Risk Factors:**
• Blood Pressure: {blood_pressure} mmHg ({'High' if blood_pressure >= 140 else 'Elevated' if blood_pressure >= 130 else 'Normal'})
• BMI: {bmi:.1f} ({'Obesity' if bmi > 30 else 'Overweight' if bmi > 25 else 'Normal weight'})
• Cholesterol: {cholesterol} mg/dL ({'High' if cholesterol > 240 else 'Borderline' if cholesterol > 200 else 'Normal'})
• Physical Activity: {activity}/10 ({'Low' if activity < 3 else 'Moderate' if activity < 6 else 'Good'})

**IMMEDIATE ACTIONS REQUIRED:**
• Consult with a cardiologist or hypertension specialist IMMEDIATELY
• Consider blood pressure medication as recommended by your doctor
• Monitor blood pressure multiple times daily
• Implement strict DASH diet immediately
• Reduce sodium intake to < 1,500mg/day"""
    elif hypertension_risk >= 50:
        confidence = "High"
        answer = f"""**Your Hypertension Risk Assessment: HIGH RISK**

⚠️ Your actual hypertension risk is {hypertension_risk:.1f}% - This is HIGH and needs urgent attention.

**Your Specific Risk Factors:**
• Blood Pressure: {blood_pressure} mmHg ({'High' if blood_pressure >= 140 else 'Elevated' if blood_pressure >= 130 else 'Normal'})
• BMI: {bmi:.1f} ({'Obesity' if bmi > 30 else 'Overweight' if bmi > 25 else 'Normal weight'})
• Cholesterol: {cholesterol} mg/dL ({'High' if cholesterol > 240 else 'Borderline' if cholesterol > 200 else 'Normal'})
• Physical Activity: {activity}/10 ({'Low' if activity < 3 else 'Moderate' if activity < 6 else 'Good'})

**URGENT ACTIONS NEEDED:**
• Consult with a cardiologist or hypertension specialist within 1-2 weeks
• Consider medication if lifestyle changes aren't sufficient
• Monitor blood pressure daily
• Focus on heart-healthy diet (DASH diet recommended)"""
        
    elif hypertension_risk >= 25:
        confidence = "Medium"
        answer = f"""**Your Hypertension Risk Assessment: MODERATE RISK**

Your actual hypertension risk is {hypertension_risk:.1f}% - This is MODERATE and needs attention.

**Your Specific Profile:**
• Blood Pressure: {blood_pressure} mmHg - {'Monitor closely' if blood_pressure >= 130 else 'Normal'}
• BMI: {bmi:.1f} - {'Needs improvement' if bmi > 25 else 'Good'}
• Cholesterol: {cholesterol} mg/dL - {'Monitor closely' if cholesterol > 200 else 'Normal'}
• Physical Activity: {activity}/10 - {'Needs improvement' if activity < 6 else 'Good'}

**Recommended Actions:**
• Get regular blood pressure monitoring
• Focus on weight management if BMI > 25
• Increase physical activity to at least 150 minutes/week
• Adopt heart-healthy diet (reduce sodium, increase fruits/vegetables)"""
        
    else:
        confidence = "High"
        answer = f"""**Your Hypertension Risk Assessment: LOW RISK**

✅ Good news! Your actual hypertension risk is {hypertension_risk:.1f}% - This is LOW.

**Your Healthy Profile:**
• Blood Pressure: {blood_pressure} mmHg - Normal
• BMI: {bmi:.1f} - Excellent
• Cholesterol: {cholesterol} mg/dL - Normal
• Physical Activity: {activity}/10 - Good

**Maintain Your Healthy Habits:**
• Continue regular physical activity ({activity}/10 is great!)
• Maintain healthy weight (BMI {bmi:.1f} is good)
• Keep blood pressure in normal range ({blood_pressure} mmHg is excellent)
• Regular health checkups every 1-2 years"""
    
    return HealthAnswer(
        answer=answer,
        confidence=confidence,
        related_factors=risk_factors[:3] if risk_factors else ["healthy lifestyle"],
        follow_up_suggestions=[
            "Monitor blood pressure regularly",
            "Maintain heart-healthy lifestyle",
            "Schedule regular health checkups"
        ],
        disclaimer="This assessment is for informational purposes only and should not replace professional medical advice."
    )

def generate_nutrition_answer(question: str, health_data: Dict, bmi: float, glucose: float, cholesterol: float, activity: float) -> HealthAnswer:
    """Generate personalized nutrition-related answers"""
    
    # Analyze nutritional needs
    if bmi > 30:
        focus = "weight management and blood sugar control"
        recommendations = [
            "Focus on portion control and calorie reduction",
            "Increase fiber intake (25-30g daily)",
            "Limit refined carbohydrates and added sugars",
            "Include lean proteins and healthy fats"
        ]
    elif bmi > 25:
        focus = "weight management and metabolic health"
        recommendations = [
            "Moderate calorie reduction for weight loss",
            "Increase vegetable and fruit intake",
            "Choose whole grains over refined grains",
            "Include regular protein with meals"
        ]
    else:
        focus = "maintaining healthy weight and preventing disease"
        recommendations = [
            "Maintain balanced macronutrient intake",
            "Continue current healthy eating patterns",
            "Focus on nutrient-dense foods",
            "Stay hydrated with water"
        ]
    
    # Add specific recommendations based on health metrics
    if glucose > 100:
        recommendations.append("Monitor carbohydrate intake and blood sugar response")
    if cholesterol > 200:
        recommendations.append("Limit saturated fats and increase omega-3 fatty acids")
    if activity < 5:
        recommendations.append("Consider meal timing around physical activity")
    
    answer = f"""**Personalized Nutrition Recommendations**

Based on your health profile, here are tailored nutrition recommendations:

**Your Current Status:**
• BMI: {bmi:.1f} ({'Obesity' if bmi > 30 else 'Overweight' if bmi > 25 else 'Normal weight'})
• Blood Glucose: {glucose} mg/dL ({'Pre-diabetic' if glucose > 100 else 'Normal'})
• Cholesterol: {cholesterol} mg/dL ({'High' if cholesterol > 240 else 'Borderline' if cholesterol > 200 else 'Normal'})
• Physical Activity: {activity}/10 ({'Low' if activity < 3 else 'Moderate' if activity < 6 else 'Good'})

**Focus Area: {focus.title()}**

**Personalized Recommendations:**
{chr(10).join([f"• {rec}" for rec in recommendations])}

**Sample Meal Plan:**
• Breakfast: Whole grain cereal with berries and nuts
• Lunch: Grilled chicken salad with mixed vegetables
• Dinner: Baked fish with quinoa and steamed broccoli
• Snacks: Greek yogurt with fruit, or raw vegetables with hummus"""
    
    return HealthAnswer(
        answer=answer,
        confidence="High",
        related_factors=["nutrition", "diet", "weight management"],
        follow_up_suggestions=[
            "Consider consulting a registered dietitian",
            "Track your food intake and symptoms",
            "Monitor your health metrics regularly"
        ],
        disclaimer="This nutrition advice is for informational purposes only and should not replace professional medical or nutritional guidance."
    )

def generate_fitness_answer(question: str, health_data: Dict, age: int, bmi: float, activity: float, blood_pressure: float) -> HealthAnswer:
    """Generate personalized fitness-related answers"""
    
    # Analyze fitness needs
    if activity < 3:
        intensity = "low to moderate"
        focus = "building a consistent exercise routine"
        recommendations = [
            "Start with 10-15 minutes of daily walking",
            "Gradually increase to 30 minutes, 5 days per week",
            "Include strength training 2-3 times per week",
            "Focus on consistency over intensity"
        ]
    elif activity < 6:
        intensity = "moderate to vigorous"
        focus = "increasing exercise intensity and variety"
        recommendations = [
            "Aim for 150 minutes of moderate-intensity exercise weekly",
            "Include both cardio and strength training",
            "Add flexibility and balance exercises",
            "Consider interval training for efficiency"
        ]
    else:
        intensity = "moderate to high"
        focus = "maintaining and optimizing your fitness routine"
        recommendations = [
            "Continue your current exercise routine",
            "Add variety to prevent plateaus",
            "Focus on recovery and injury prevention",
            "Consider advanced training techniques"
        ]
    
    # Add age-specific recommendations
    if age > 65:
        recommendations.append("Include balance and flexibility exercises for fall prevention")
    if blood_pressure >= 130:
        recommendations.append("Monitor blood pressure during exercise and consult your doctor")
    
    answer = f"""**Personalized Fitness Recommendations**

Based on your health profile, here are tailored exercise recommendations:

**Your Current Status:**
• Age: {age} years
• BMI: {bmi:.1f} ({'Obesity' if bmi > 30 else 'Overweight' if bmi > 25 else 'Normal weight'})
• Current Activity Level: {activity}/10 ({'Low' if activity < 3 else 'Moderate' if activity < 6 else 'Good'})
• Blood Pressure: {blood_pressure} mmHg ({'High' if blood_pressure >= 140 else 'Elevated' if blood_pressure >= 130 else 'Normal'})

**Focus Area: {focus.title()}**

**Recommended Exercise Intensity: {intensity.title()}**

**Personalized Recommendations:**
{chr(10).join([f"• {rec}" for rec in recommendations])}

**Sample Weekly Schedule:**
• Monday: Cardio (30-45 minutes)
• Tuesday: Strength training (30 minutes)
• Wednesday: Active recovery (walking, yoga)
• Thursday: Cardio (30-45 minutes)
• Friday: Strength training (30 minutes)
• Saturday: Fun activity (sports, hiking)
• Sunday: Rest or light stretching"""
    
    return HealthAnswer(
        answer=answer,
        confidence="High",
        related_factors=["exercise", "fitness", "physical activity"],
        follow_up_suggestions=[
            "Start slowly and gradually increase intensity",
            "Listen to your body and rest when needed",
            "Consider working with a fitness professional"
        ],
        disclaimer="This fitness advice is for informational purposes only and should not replace professional medical or fitness guidance."
    )

def generate_general_health_answer(question: str, health_data: Dict, age: int, gender: str, bmi: float, blood_pressure: float, glucose: float, activity: float) -> HealthAnswer:
    """Generate personalized general health answers"""
    
    # Analyze overall health status
    health_score = 0
    factors = []
    
    # BMI analysis
    if 18.5 <= bmi <= 24.9:
        health_score += 20
        factors.append("healthy weight")
    elif 25 <= bmi <= 29.9:
        health_score += 15
        factors.append("slightly overweight")
    else:
        health_score += 10
        factors.append("weight management needed")
    
    # Blood pressure analysis
    if blood_pressure < 120:
        health_score += 20
        factors.append("normal blood pressure")
    elif blood_pressure < 130:
        health_score += 15
        factors.append("elevated blood pressure")
    else:
        health_score += 10
        factors.append("high blood pressure")
    
    # Glucose analysis
    if glucose < 100:
        health_score += 20
        factors.append("normal blood glucose")
    elif glucose < 126:
        health_score += 15
        factors.append("pre-diabetic glucose")
    else:
        health_score += 10
        factors.append("elevated blood glucose")
    
    # Activity analysis
    if activity >= 7:
        health_score += 20
        factors.append("high physical activity")
    elif activity >= 4:
        health_score += 15
        factors.append("moderate physical activity")
    else:
        health_score += 10
        factors.append("low physical activity")
    
    # Age consideration
    if age < 40:
        health_score += 20
    elif age < 60:
        health_score += 15
    else:
        health_score += 10
    
    # Generate response based on health score
    if health_score >= 80:
        confidence = "High"
        answer = f"""**Your Overall Health Status: EXCELLENT**

Congratulations! Your health profile shows excellent overall health.

**Your Health Strengths:**
• BMI: {bmi:.1f} - Healthy weight
• Blood Pressure: {blood_pressure} mmHg - Normal
• Blood Glucose: {glucose} mg/dL - Normal
• Physical Activity: {activity}/10 - Active lifestyle
• Age: {age} years - Young and healthy

**Key Health Factors:**
{', '.join(factors[:3])}

**Maintain Your Excellent Health:**
• Continue your current healthy lifestyle
• Regular health checkups every 1-2 years
• Stay active and maintain your exercise routine
• Keep up your healthy eating habits"""
        
    elif health_score >= 60:
        confidence = "Medium"
        answer = f"""**Your Overall Health Status: GOOD**

Your health profile shows good overall health with some areas for improvement.

**Your Health Profile:**
• BMI: {bmi:.1f} ({'Obesity' if bmi > 30 else 'Overweight' if bmi > 25 else 'Normal weight'})
• Blood Pressure: {blood_pressure} mmHg ({'High' if blood_pressure >= 140 else 'Elevated' if blood_pressure >= 130 else 'Normal'})
• Blood Glucose: {glucose} mg/dL ({'Pre-diabetic' if glucose > 100 else 'Normal'})
• Physical Activity: {activity}/10 ({'Low' if activity < 3 else 'Moderate' if activity < 6 else 'Good'})

**Key Health Factors:**
{', '.join(factors[:3])}

**Areas for Improvement:**
• Focus on maintaining healthy weight
• Increase physical activity if needed
• Monitor blood pressure and glucose levels
• Regular health checkups annually"""
        
    else:
        confidence = "High"
        answer = f"""**Your Overall Health Status: NEEDS ATTENTION**

Your health profile shows several areas that need attention and improvement.

**Your Health Profile:**
• BMI: {bmi:.1f} ({'Obesity' if bmi > 30 else 'Overweight' if bmi > 25 else 'Normal weight'})
• Blood Pressure: {blood_pressure} mmHg ({'High' if blood_pressure >= 140 else 'Elevated' if blood_pressure >= 130 else 'Normal'})
• Blood Glucose: {glucose} mg/dL ({'Pre-diabetic' if glucose > 100 else 'Normal'})
• Physical Activity: {activity}/10 ({'Low' if activity < 3 else 'Moderate' if activity < 6 else 'Good'})

**Key Health Factors:**
{', '.join(factors[:3])}

**Priority Actions:**
• Consult with healthcare providers
• Focus on lifestyle modifications
• Increase physical activity gradually
• Improve diet quality
• Regular health monitoring"""
    
    return HealthAnswer(
        answer=answer,
        confidence=confidence,
        related_factors=factors[:3],
        follow_up_suggestions=[
            "Schedule regular health checkups",
            "Monitor your health metrics",
            "Consider lifestyle modifications",
            "Consult healthcare providers as needed"
        ],
        disclaimer="This assessment is for informational purposes only and should not replace professional medical advice."
    )

# New Clean Q&A Endpoints
@app.post("/health/ask-question", response_model=HealthAnswer)
async def ask_health_question(
    question_data: HealthQuestion,
    current_user: dict = Depends(get_current_active_user)
):
    """AI-powered health Q&A based on user's latest health assessment"""
    try:
        logger.info(f"Processing health question: {question_data.question[:50]}...")
        
        # Get user's latest health assessment if not provided
        if not question_data.health_data:
            predictions_collection = get_predictions_collection()
            latest_prediction = predictions_collection.find_one(
                {"user_id": str(current_user["_id"])},
                sort=[("created_at", -1)]
            )
            if latest_prediction:
                question_data.health_data = latest_prediction.get("input_data", {})
            else:
                raise HTTPException(status_code=404, detail="No health assessment data found. Please complete a health assessment first.")
        
        # Generate personalized answer based on health data
        answer = generate_personalized_health_answer(question_data.question, question_data.health_data)
        
        logger.info(f"Successfully generated answer for user {current_user['email']}")
        return answer
        
    except Exception as e:
        logger.error(f"Error processing health question: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")


# Test endpoint removed for security - all endpoints now require authentication

# Debug endpoint removed for security - could expose user data

# @app.post("/debug/save-test")  # Removed for security
async def debug_save_test(health_input: HealthInput):
    """Debug endpoint to test saving without authentication"""
    try:
        logger.info("Testing database save without authentication")
        predictions_collection = get_predictions_collection()
        
        # Create a test record
        test_record = {
            "user_id": "test_user_123",
            "input_data": health_input.dict(),
            "diabetes_risk": 0.25,
            "hypertension_risk": 0.35,
            "diabetes_confidence": "Moderate",
            "hypertension_confidence": "Moderate",
            "risk_category_diabetes": "Moderate Risk",
            "risk_category_hypertension": "Moderate Risk",
            "metabolic_health_score": 75.0,
            "cardiovascular_health_score": 70.0,
            "created_at": datetime.now()
        }
        
        result = predictions_collection.insert_one(test_record)
        logger.info(f"Test record saved with ID: {result.inserted_id}")
        
        return {
            "status": "success",
            "inserted_id": str(result.inserted_id),
            "message": "Test record saved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to save test record: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }

@app.post("/analyze/comprehensive")
async def get_comprehensive_analysis(health_input: HealthInput):
    """Get comprehensive risk factor analysis for health assessment"""
    try:
        if not all([diabetes_model, hypertension_model, model_features]):
            raise HTTPException(
                status_code=503,
                detail="Models not loaded. Please try again later."
            )
        
        # Prepare input data
        input_dict = health_input.dict()
        input_df, feature_quality = prepare_features(health_input)
        
        # Get predictions
        diabetes_proba = diabetes_model.predict_proba(input_df)[0][1]
        hypertension_proba = hypertension_model.predict_proba(input_df)[0][1]
        
        # Get comprehensive analysis
        comprehensive_analysis = analyze_comprehensive_risk_factors(
            input_dict, diabetes_proba, hypertension_proba
        )
        
        return {
            "status": "success",
            "comprehensive_analysis": comprehensive_analysis,
            "diabetes_risk": round(diabetes_proba * 100, 1),
            "hypertension_risk": round(hypertension_proba * 100, 1),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def generate_sleep_answer(question: str, health_data: Dict, age: int, sleep_hours: float, stress_level: float, activity: float) -> HealthAnswer:
    """Generate personalized sleep-related answers"""
    
    # Analyze sleep patterns
    sleep_quality = "good" if 7 <= sleep_hours <= 9 else "needs improvement"
    factors = []
    
    if sleep_hours < 6:
        factors.append("insufficient sleep duration")
    elif sleep_hours > 9:
        factors.append("excessive sleep duration")
    else:
        factors.append("adequate sleep duration")
    
    if stress_level > 7:
        factors.append("high stress affecting sleep quality")
    elif stress_level < 4:
        factors.append("low stress levels")
    
    if activity < 3:
        factors.append("low physical activity affecting sleep")
    elif activity > 7:
        factors.append("high activity levels promoting better sleep")
    
    # Generate personalized response
    if "sleep" in question.lower() or "insomnia" in question.lower():
        answer = f"Based on your profile, you're getting {sleep_hours:.1f} hours of sleep per night. "
        
        if 7 <= sleep_hours <= 9:
            answer += "This is within the recommended range for adults. "
        elif sleep_hours < 7:
            answer += "This is below the recommended 7-9 hours for adults. "
        else:
            answer += "This exceeds the typical adult sleep needs. "
        
        if stress_level > 6:
            answer += f"Your high stress level ({stress_level}/10) may be affecting sleep quality. "
            answer += "Consider stress management techniques like meditation, deep breathing, or gentle yoga before bed. "
        
        if activity < 3:
            answer += "Increasing your physical activity during the day can improve sleep quality at night. "
        
        answer += "Maintain a consistent sleep schedule and create a relaxing bedtime routine."
    
    elif "tired" in question.lower() or "fatigue" in question.lower():
        answer = f"Your sleep duration of {sleep_hours:.1f} hours may be contributing to fatigue. "
        
        if sleep_hours < 7:
            answer += "Try to get 7-9 hours of quality sleep each night. "
        elif stress_level > 6:
            answer += "High stress levels can cause fatigue even with adequate sleep. "
        
        answer += "Ensure your bedroom is cool, dark, and quiet for optimal sleep quality."
    
    else:
        answer = f"Your current sleep pattern shows {sleep_quality} sleep habits. "
        if sleep_hours < 7:
            answer += "Aim for 7-9 hours of sleep for optimal health and energy levels."
        else:
            answer += "Continue maintaining good sleep hygiene for overall health."
    
    return HealthAnswer(
        answer=answer,
        confidence="High",
        related_factors=factors,
        follow_up_suggestions=[
            "Ask about sleep hygiene tips",
            "Learn stress management techniques",
            "Get exercise recommendations for better sleep",
            "Understand sleep disorders and when to seek help"
        ],
        disclaimer="Sleep advice is general guidance. Consult a healthcare provider for persistent sleep issues."
    )

def generate_mental_health_answer(question: str, health_data: Dict, age: int, stress_level: float, sleep_hours: float, activity: float) -> HealthAnswer:
    """Generate personalized mental health answers"""
    
    # Analyze mental health factors
    factors = []
    mental_health_score = 0
    
    if stress_level < 4:
        factors.append("low stress levels")
        mental_health_score += 20
    elif stress_level > 7:
        factors.append("high stress levels")
        mental_health_score -= 15
    
    if sleep_hours >= 7:
        factors.append("adequate sleep for mental health")
        mental_health_score += 15
    else:
        factors.append("insufficient sleep affecting mental health")
        mental_health_score -= 10
    
    if activity >= 5:
        factors.append("good physical activity for mental wellbeing")
        mental_health_score += 15
    elif activity < 3:
        factors.append("low activity affecting mental health")
        mental_health_score -= 10
    
    # Generate personalized response
    if "stress" in question.lower() or "anxiety" in question.lower():
        answer = f"Your stress level is {stress_level}/10. "
        
        if stress_level > 7:
            answer += "This is quite high and may be affecting your overall wellbeing. "
            answer += "Consider stress management techniques like deep breathing, meditation, or talking to a counselor. "
        elif stress_level < 4:
            answer += "You're managing stress well! Continue your current stress management strategies. "
        else:
            answer += "This is a moderate stress level. Consider preventive stress management techniques. "
        
        if activity < 3:
            answer += "Regular physical activity can significantly reduce stress levels. "
        if sleep_hours < 7:
            answer += "Adequate sleep is crucial for stress management. "
    
    elif "depression" in question.lower() or "mood" in question.lower():
        answer = f"Based on your lifestyle factors: "
        
        if activity >= 5:
            answer += "Your good activity level supports positive mood. "
        else:
            answer += "Increasing physical activity can boost mood and mental health. "
        
        if sleep_hours >= 7:
            answer += "Adequate sleep is essential for emotional wellbeing. "
        else:
            answer += "Poor sleep can negatively impact mood and mental health. "
        
        if stress_level > 6:
            answer += "High stress can contribute to mood changes. Consider stress reduction techniques. "
        
        answer += "If you're experiencing persistent mood changes, consider speaking with a mental health professional."
    
    else:
        answer = f"Your mental health factors show: "
        if mental_health_score >= 30:
            answer += "good mental health indicators. Continue your current lifestyle habits. "
        else:
            answer += "some areas for improvement. Focus on stress management, adequate sleep, and regular physical activity. "
        
        answer += "Mental health is as important as physical health - don't hesitate to seek professional support when needed."
    
    return HealthAnswer(
        answer=answer,
        confidence="High",
        related_factors=factors,
        follow_up_suggestions=[
            "Learn stress management techniques",
            "Get sleep improvement tips",
            "Find mental health resources",
            "Understand when to seek professional help"
        ],
        disclaimer="Mental health advice is general guidance. Seek professional help for persistent mental health concerns."
    )

def generate_lifestyle_answer(question: str, health_data: Dict, age: int, gender: str, bmi: float, activity: float, smoking: int, alcohol: int, sleep_hours: float) -> HealthAnswer:
    """Generate personalized lifestyle answers"""
    
    # Analyze lifestyle factors
    factors = []
    lifestyle_score = 0
    
    if smoking == 0:
        factors.append("non-smoker")
        lifestyle_score += 20
    else:
        factors.append("smoking habit - major health risk")
        lifestyle_score -= 20
    
    if alcohol == 0:
        factors.append("no alcohol consumption")
        lifestyle_score += 10
    elif alcohol <= 2:
        factors.append("moderate alcohol consumption")
        lifestyle_score += 5
    else:
        factors.append("high alcohol consumption")
        lifestyle_score -= 10
    
    if activity >= 5:
        factors.append("active lifestyle")
        lifestyle_score += 15
    elif activity >= 3:
        factors.append("moderately active")
        lifestyle_score += 10
    else:
        factors.append("sedentary lifestyle")
        lifestyle_score -= 15
    
    if 7 <= sleep_hours <= 9:
        factors.append("good sleep habits")
        lifestyle_score += 10
    else:
        factors.append("sleep pattern needs improvement")
        lifestyle_score -= 5
    
    # Generate personalized response
    if "lifestyle" in question.lower() or "habits" in question.lower():
        answer = f"Your lifestyle profile shows: "
        
        if smoking == 0:
            answer += "excellent choice to avoid smoking. "
        else:
            answer += "smoking is a major health risk that should be addressed. "
        
        if alcohol <= 2:
            answer += "Your alcohol consumption appears moderate. "
        else:
            answer += "Consider reducing alcohol consumption for better health. "
        
        if activity >= 5:
            answer += "Great job maintaining an active lifestyle! "
        else:
            answer += "Increasing physical activity will significantly benefit your health. "
        
        answer += "Focus on maintaining healthy habits: regular exercise, balanced nutrition, adequate sleep, and stress management."
    
    elif "prevention" in question.lower():
        answer = f"Based on your {age}-year-old {gender.lower()} profile, key prevention strategies include: "
        
        if smoking > 0:
            answer += "Quitting smoking is the most important step. "
        if activity < 5:
            answer += "Regular physical activity (150 minutes/week) is crucial. "
        if bmi > 25:
            answer += "Maintaining a healthy weight through diet and exercise. "
        
        answer += "Regular health screenings, stress management, and adequate sleep are also essential for prevention."
    
    else:
        answer = f"Your lifestyle factors indicate "
        if lifestyle_score >= 40:
            answer += "good overall lifestyle choices. Continue your healthy habits! "
        else:
            answer += "several areas for improvement. Focus on the most impactful changes first. "
        
        answer += "Small, consistent changes in daily habits can lead to significant long-term health benefits."
    
    return HealthAnswer(
        answer=answer,
        confidence="High",
        related_factors=factors,
        follow_up_suggestions=[
            "Get personalized exercise recommendations",
            "Learn about healthy nutrition habits",
            "Understand smoking cessation resources",
            "Find stress management techniques"
        ],
        disclaimer="Lifestyle advice is general guidance. Consult healthcare providers for personalized recommendations."
    )

def generate_medication_answer(question: str, health_data: Dict, age: int, gender: str, bmi: float, blood_pressure: float, glucose: float, cholesterol: float) -> HealthAnswer:
    """Generate personalized medication-related answers"""
    
    # Analyze medication needs
    factors = []
    medication_considerations = []
    
    if blood_pressure >= 140:
        medication_considerations.append("blood pressure medication may be needed")
    if glucose >= 126:
        medication_considerations.append("diabetes medication may be required")
    if cholesterol >= 240:
        medication_considerations.append("cholesterol medication may be beneficial")
    
    if age >= 65:
        factors.append("age-related medication considerations")
    if bmi > 30:
        factors.append("weight-related medication adjustments may be needed")
    
    # Generate personalized response
    if "medication" in question.lower() or "drug" in question.lower():
        answer = f"Based on your health profile: "
        
        if medication_considerations:
            answer += f"Your health indicators suggest {', '.join(medication_considerations[:2])}. "
            answer += "However, medication decisions should always be made with your healthcare provider. "
        else:
            answer += "Your current health indicators don't suggest immediate medication needs. "
            answer += "Focus on lifestyle modifications first. "
        
        answer += "Never start, stop, or change medications without consulting your doctor."
    
    elif "supplement" in question.lower() or "vitamin" in question.lower():
        answer = f"Based on your {age}-year-old profile: "
        
        if age >= 50:
            answer += "You may benefit from vitamin D and B12 supplements. "
        if health_data.get('physical_activity', 5) < 3:
            answer += "Consider omega-3 supplements for heart health. "
        if health_data.get('sleep_hours', 7) < 7:
            answer += "Magnesium supplements may help with sleep. "
        
        answer += "Always consult your healthcare provider before starting any supplements, especially if you take medications."
    
    else:
        answer = f"Your health profile suggests "
        if medication_considerations:
            answer += "potential medication needs that should be discussed with your healthcare provider. "
        else:
            answer += "good health indicators that may not require medications at this time. "
        
        answer += "Regular monitoring and lifestyle modifications are key to maintaining health."
    
    return HealthAnswer(
        answer=answer,
        confidence="Medium",
        related_factors=factors,
        follow_up_suggestions=[
            "Discuss medication options with your doctor",
            "Learn about medication interactions",
            "Understand supplement safety",
            "Get regular health monitoring"
        ],
        disclaimer="This is not medical advice. Always consult healthcare providers for medication decisions."
    )

def generate_symptoms_answer(question: str, health_data: Dict, age: int, gender: str, bmi: float, blood_pressure: float, glucose: float, cholesterol: float) -> HealthAnswer:
    """Generate personalized symptoms-related answers"""
    
    # Analyze potential symptoms based on health data
    factors = []
    warning_signs = []
    
    if blood_pressure >= 140:
        warning_signs.append("high blood pressure symptoms like headaches, dizziness")
    if glucose >= 126:
        warning_signs.append("diabetes symptoms like increased thirst, frequent urination")
    if bmi > 30:
        warning_signs.append("obesity-related symptoms like joint pain, fatigue")
    
    if age >= 50:
        factors.append("age-related symptom monitoring")
    if gender == "Male":
        factors.append("male-specific health symptoms to watch")
    else:
        factors.append("female-specific health symptoms to monitor")
    
    # Generate personalized response
    if "symptom" in question.lower() or "sign" in question.lower():
        answer = f"Based on your health profile, be aware of: "
        
        if warning_signs:
            answer += f"{', '.join(warning_signs[:2])}. "
        else:
            answer += "general health symptoms like persistent fatigue, unexplained weight changes, or unusual pain. "
        
        answer += "If you experience any concerning symptoms, consult your healthcare provider promptly."
    
    elif "warning" in question.lower() or "alert" in question.lower():
        answer = f"Your health indicators suggest monitoring for: "
        
        if blood_pressure >= 130:
            answer += "cardiovascular symptoms like chest pain, shortness of breath. "
        if glucose >= 100:
            answer += "diabetes symptoms like excessive thirst, frequent urination, blurred vision. "
        if bmi > 25:
            answer += "weight-related symptoms like joint pain, sleep apnea. "
        
        answer += "Seek immediate medical attention for severe symptoms like chest pain, difficulty breathing, or severe headache."
    
    else:
        answer = f"Your {age}-year-old {gender.lower()} profile suggests monitoring for age and gender-appropriate symptoms. "
        answer += "Regular health checkups and awareness of your body's changes are important for early detection of health issues."
    
    return HealthAnswer(
        answer=answer,
        confidence="Medium",
        related_factors=factors,
        follow_up_suggestions=[
            "Learn about emergency symptoms",
            "Understand when to seek immediate care",
            "Get regular health screenings",
            "Track symptoms and patterns"
        ],
        disclaimer="This is not medical advice. Seek immediate medical attention for severe or concerning symptoms."
    )

# Test endpoint for debugging risk conversion
@app.get("/debug/risk-conversion")
async def debug_risk_conversion():
    """Debug endpoint to test risk score conversion"""
    test_data = {
        "diabetes_risk": 0.852,
        "hypertension_risk": 0.887
    }
    
    # Test conversion logic
    diabetes_raw = test_data.get('diabetes_risk', 0)
    diabetes_converted = diabetes_raw * 100 if diabetes_raw <= 1.0 else diabetes_raw
    
    hypertension_raw = test_data.get('hypertension_risk', 0)
    hypertension_converted = hypertension_raw * 100 if hypertension_raw <= 1.0 else hypertension_raw
    
    return {
        "diabetes_raw": diabetes_raw,
        "diabetes_converted": diabetes_converted,
        "hypertension_raw": hypertension_raw,
        "hypertension_converted": hypertension_converted,
        "diabetes_risk_level": "VERY HIGH" if diabetes_converted >= 70 else "HIGH" if diabetes_converted >= 50 else "MODERATE" if diabetes_converted >= 25 else "LOW",
        "hypertension_risk_level": "VERY HIGH" if hypertension_converted >= 70 else "HIGH" if hypertension_converted >= 50 else "MODERATE" if hypertension_converted >= 25 else "LOW"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)