from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field
from auth import get_current_active_user
from database import get_tracking_collection
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tracking", tags=["tracking"])

class TrackingData(BaseModel):
    daily_steps: Optional[int] = Field(None, ge=0)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    water_intake: Optional[int] = Field(None, ge=0)
    gym_hours: Optional[float] = Field(None, ge=0)
    calories: Optional[int] = Field(None, ge=0)
    protein_intake: Optional[int] = Field(None, ge=0)
    weight: Optional[float] = Field(None, ge=0)
    blood_pressure: Optional[float] = Field(None, ge=0)
    glucose_level: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None

@router.post("/log")
async def log_tracking_data(
    tracking_data: TrackingData,
    current_user: dict = Depends(get_current_active_user)
):
    """Log daily health tracking data"""
    try:
        tracking_collection = get_tracking_collection()
        
        tracking_entry = {
            "user_id": current_user["id"],
            "email": current_user["email"],
            "date": datetime.utcnow().isoformat(),
            **tracking_data.dict(exclude_none=True),
            "created_at": datetime.utcnow()
        }
        
        result = tracking_collection.insert_one(tracking_entry)
        
        logger.info(f"Tracking data logged for user: {current_user['email']}")
        
        return {
            "message": "Tracking data logged successfully",
            "id": str(result.inserted_id),
            "date": tracking_entry["date"]
        }
        
    except Exception as e:
        logger.error(f"Error logging tracking data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log tracking data"
        )

@router.get("/history")
async def get_tracking_history(
    days: int = 30,
    current_user: dict = Depends(get_current_active_user)
):
    """Get tracking history for the user"""
    try:
        tracking_collection = get_tracking_collection()
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query tracking data
        tracking_data = list(tracking_collection.find(
            {
                "user_id": current_user["id"],
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
        ).sort("created_at", -1))
        
        # Convert ObjectId to string
        for entry in tracking_data:
            entry["_id"] = str(entry["_id"])
            entry["created_at"] = entry["created_at"].isoformat()
        
        return {
            "count": len(tracking_data),
            "history": tracking_data
        }
        
    except Exception as e:
        logger.error(f"Error fetching tracking history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tracking history"
        )

@router.get("/goals")
async def get_goals(
    current_user: dict = Depends(get_current_active_user)
):
    """Get user's health goals"""
    # This is a placeholder - you can implement goal setting later
    return {
        "daily_steps": 10000,
        "sleep_hours": 8,
        "water_intake": 8,
        "gym_hours": 1
    }