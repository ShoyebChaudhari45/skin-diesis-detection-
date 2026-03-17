"""
Prediction Routes
=================
Handles image upload, ML prediction, and prediction history.

Endpoints:
    POST /api/predict  — Upload image and get skin disease prediction
    GET  /api/history  — Get user's prediction history
"""

import os
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from pymongo import MongoClient

from backend.config import settings
from backend.utils.auth import get_current_user
from backend.utils.ml_predictor import predictor
from backend.utils.disease_info import get_disease_info

# Create router
router = APIRouter(prefix="/api", tags=["Predictions"])

# MongoDB connection
client = MongoClient(settings.MONGODB_URI)
db = client[settings.DATABASE_NAME]
predictions_collection = db["predictions"]
users_collection = db["users"]

# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}


@router.post("/predict")
async def predict_disease(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a skin image and get AI-based disease prediction.
    
    Process:
        1. Validate uploaded file is an image
        2. Save image to uploads directory
        3. Run CNN model prediction
        4. Get disease information and precautions
        5. Store prediction in MongoDB
        6. Return results to client
    
    Args:
        file: Uploaded image file (jpg, png, bmp)
        current_user: Authenticated user from JWT
    
    Returns:
        Prediction results with disease info and precautions
    """
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file bytes
    image_bytes = await file.read()
    
    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file uploaded"
        )
    
    # Save image to uploads directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as f:
        f.write(image_bytes)
    
    # Run ML prediction
    try:
        prediction = predictor.predict(image_bytes)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )
    
    # Get detailed disease information
    disease_info = get_disease_info(prediction["predicted_class"])
    
    # Build result document
    result = {
        "user_email": current_user["email"],
        "user_name": current_user.get("name", ""),
        "image_filename": unique_filename,
        "original_filename": file.filename,
        "predicted_class": prediction["predicted_class"],
        "confidence": prediction["confidence"],
        "all_predictions": prediction["all_predictions"],
        "disease_info": {
            "full_name": disease_info["full_name"],
            "description": disease_info["description"],
            "severity": disease_info["severity"],
            "precautions": disease_info["precautions"]
        },
        "created_at": datetime.utcnow().isoformat(),
        "timestamp": datetime.utcnow()
    }
    
    # Store in MongoDB
    predictions_collection.insert_one(result)
    
    # Update user prediction count
    users_collection.update_one(
        {"email": current_user["email"]},
        {"$inc": {"predictions_count": 1}}
    )
    
    # Remove MongoDB _id (not JSON serializable)
    result.pop("_id", None)
    result.pop("timestamp", None)
    
    return {
        "success": True,
        "prediction": result
    }


@router.get("/history")
async def get_prediction_history(current_user: dict = Depends(get_current_user)):
    """
    Get prediction history for the current user.
    
    Returns:
        List of past predictions sorted by date (newest first)
    """
    predictions = list(
        predictions_collection.find(
            {"user_email": current_user["email"]},
            {"_id": 0, "timestamp": 0}  # Exclude non-serializable fields
        ).sort("created_at", -1)  # Newest first
    )
    
    return {
        "success": True,
        "count": len(predictions),
        "predictions": predictions
    }
