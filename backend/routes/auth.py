"""
Authentication Routes
=====================
Handles user signup, login, and profile management.

Endpoints:
    POST /api/signup  — Register a new user
    POST /api/login   — Authenticate and get JWT token
    GET  /api/profile  — Get current user profile
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from pymongo import MongoClient

from backend.config import settings
from backend.utils.auth import (
    hash_password, verify_password, create_access_token, get_current_user
)

# Create router
router = APIRouter(prefix="/api", tags=["Authentication"])

# MongoDB connection
client = MongoClient(settings.MONGODB_URI)
db = client[settings.DATABASE_NAME]
users_collection = db["users"]

# Create unique index on email
users_collection.create_index("email", unique=True)


# ──────────────────────────────────────────────
# Request / Response Models
# ──────────────────────────────────────────────

class SignupRequest(BaseModel):
    """User registration request body."""
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=6, max_length=128, description="Password")


class LoginRequest(BaseModel):
    """User login request body."""
    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class AuthResponse(BaseModel):
    """Authentication response with JWT token."""
    message: str
    token: str
    user: dict


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest):
    """
    Register a new user account.
    
    - Validates email uniqueness
    - Hashes password with bcrypt
    - Creates JWT token
    - Returns token and user info
    """
    # Check if user already exists
    existing_user = users_collection.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )
    
    # Hash password
    hashed_pw = hash_password(request.password)
    
    # Create user document
    user_doc = {
        "name": request.name,
        "email": request.email,
        "password": hashed_pw,
        "role": "user",  # Default role
        "created_at": datetime.utcnow().isoformat(),
        "predictions_count": 0
    }
    
    # Insert into MongoDB
    result = users_collection.insert_one(user_doc)
    
    # Create JWT token
    token = create_access_token({
        "email": request.email,
        "name": request.name,
        "role": "user",
        "user_id": str(result.inserted_id)
    })
    
    return AuthResponse(
        message="Account created successfully",
        token=token,
        user={
            "name": request.name,
            "email": request.email,
            "role": "user"
        }
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    - Verifies email exists
    - Validates password against bcrypt hash
    - Returns JWT token on success
    """
    # Find user by email
    user = users_collection.find_one({"email": request.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create JWT token
    token = create_access_token({
        "email": user["email"],
        "name": user["name"],
        "role": user.get("role", "user"),
        "user_id": str(user["_id"])
    })
    
    return AuthResponse(
        message="Login successful",
        token=token,
        user={
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "user")
        }
    )


@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile information."""
    user = users_collection.find_one(
        {"email": current_user["email"]},
        {"password": 0, "_id": 0}  # Exclude sensitive fields
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"user": user}
