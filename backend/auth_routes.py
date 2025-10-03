from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
import logging

from models import UserRegister, UserLogin, Token, UserResponse
from auth import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    get_current_active_user,
    decode_access_token
)
from database import get_users_collection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister):  # Changed to def (not async)
    """Register a new user"""
    logger.info(f"Registration attempt with data: {user_data.dict()}")
    
    users_collection = get_users_collection()
    
    # Check if user already exists (removed await)
    existing_user = users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    user_dict = {
        "email": user_data.email,
        "hashed_password": hashed_password,
        "full_name": user_data.full_name,
        "age": user_data.age,
        "gender": user_data.gender,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = users_collection.insert_one(user_dict)  # Removed await
    user_id = str(result.inserted_id)
    
    # Create access token
    access_token = create_access_token(data={"sub": user_id})
    
    user_response = UserResponse(
        id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        age=user_data.age,
        gender=user_data.gender,
        created_at=user_dict["created_at"]
    )
    
    logger.info(f"New user registered: {user_data.email}")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@router.post("/login", response_model=Token)
def login(credentials: UserLogin):  # Changed to def (not async)
    """Login user"""
    users_collection = get_users_collection()
    
    # Find user (removed await)
    user = users_collection.find_one({"email": credentials.email})
    
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create access token
    user_id = str(user["_id"])
    access_token = create_access_token(data={"sub": user_id})
    
    user_response = UserResponse(
        id=user_id,
        email=user["email"],
        full_name=user["full_name"],
        age=user.get("age"),
        gender=user.get("gender"),
        created_at=user["created_at"]
    )
    
    logger.info(f"User logged in: {credentials.email}")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_active_user)):  # Changed to def
    """Get current user information"""
    return UserResponse(
        id=current_user["id"],  # Fixed: use "id" not "_id"
        email=current_user["email"],
        full_name=current_user["full_name"],
        age=current_user.get("age"),
        gender=current_user.get("gender"),
        created_at=datetime.utcnow()  # Fixed: current_user from auth doesn't have created_at
    )

@router.put("/me", response_model=UserResponse)
def update_user_profile(  # Changed to def
    full_name: str = None,
    age: int = None,
    gender: str = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Update user profile"""
    users_collection = get_users_collection()
    
    update_data = {"updated_at": datetime.utcnow()}
    
    if full_name:
        update_data["full_name"] = full_name
    if age:
        update_data["age"] = age
    if gender:
        update_data["gender"] = gender
    
    users_collection.update_one(  # Removed await
        {"_id": ObjectId(current_user["id"])},  # Fixed: use "id"
        {"$set": update_data}
    )
    
    updated_user = users_collection.find_one({"_id": ObjectId(current_user["id"])})  # Removed await
    
    return UserResponse(
        id=str(updated_user["_id"]),
        email=updated_user["email"],
        full_name=updated_user["full_name"],
        age=updated_user.get("age"),
        gender=updated_user.get("gender"),
        created_at=updated_user["created_at"]
    )

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str):
    """Refresh access token"""
    try:
        # For simplicity, we'll just decode the existing token and create a new one
        # In a production app, you'd want to implement proper refresh tokens
        payload = decode_access_token(refresh_token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify user still exists
        users_collection = get_users_collection()
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user or not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token = create_access_token(data={"sub": user_id})
        
        user_response = UserResponse(
            id=user_id,
            email=user["email"],
            full_name=user["full_name"],
            age=user.get("age"),
            gender=user.get("gender"),
            created_at=user["created_at"]
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )