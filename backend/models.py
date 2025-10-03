from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    age: Optional[int] = Field(None, ge=18, le=120)
    gender: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(BaseModel):
    email: EmailStr
    hashed_password: str
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    created_at: datetime
    
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class PredictionRecord(BaseModel):
    user_id: str
    diabetes_risk: float
    hypertension_risk: float
    diabetes_confidence: str
    hypertension_confidence: str
    risk_category_diabetes: str
    risk_category_hypertension: str
    metabolic_health_score: float
    cardiovascular_health_score: float
    input_data: Dict[str, Any]
    recommendations: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TrackingRecord(BaseModel):
    user_id: str
    date: datetime = Field(default_factory=datetime.utcnow)
    daily_steps: Optional[int] = 0
    sleep_hours: Optional[float] = 0
    water_intake: Optional[int] = 0
    gym_hours: Optional[float] = 0
    calories: Optional[int] = 0
    protein_intake: Optional[float] = 0
    weight: Optional[float] = None
    blood_pressure: Optional[int] = None
    glucose_level: Optional[float] = None
    notes: Optional[str] = None

class GoalRecord(BaseModel):
    user_id: str
    goal_type: str
    target_value: float
    current_value: float
    target_date: datetime
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

