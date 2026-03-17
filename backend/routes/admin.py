"""
Admin Routes
=============
Administrative endpoints for viewing users and prediction logs.

Endpoints:
    GET /api/admin/users  — List all registered users
    GET /api/admin/logs   — List all prediction logs
    GET /api/admin/stats  — Get system statistics
"""

from fastapi import APIRouter, Depends
from pymongo import MongoClient

from backend.config import settings
from backend.utils.auth import get_current_user

# Create router
router = APIRouter(prefix="/api/admin", tags=["Admin"])

# MongoDB connection
client = MongoClient(settings.MONGODB_URI)
db = client[settings.DATABASE_NAME]
users_collection = db["users"]
predictions_collection = db["predictions"]


@router.get("/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """
    List all registered users (admin endpoint).
    
    Returns user info without sensitive data (passwords).
    """
    users = list(
        users_collection.find(
            {},
            {"password": 0, "_id": 0}  # Exclude password and _id
        ).sort("created_at", -1)
    )
    
    return {
        "success": True,
        "count": len(users),
        "users": users
    }


@router.get("/logs")
async def get_prediction_logs(current_user: dict = Depends(get_current_user)):
    """
    List all prediction logs (admin endpoint).
    
    Returns all predictions across all users, sorted by date.
    """
    logs = list(
        predictions_collection.find(
            {},
            {"_id": 0, "timestamp": 0}
        ).sort("created_at", -1).limit(100)  # Limit to last 100
    )
    
    return {
        "success": True,
        "count": len(logs),
        "logs": logs
    }


@router.get("/stats")
async def get_system_stats(current_user: dict = Depends(get_current_user)):
    """
    Get system-wide statistics (admin endpoint).
    
    Returns:
        Total users, total predictions, and disease distribution
    """
    total_users = users_collection.count_documents({})
    total_predictions = predictions_collection.count_documents({})
    
    # Get disease distribution using aggregation
    pipeline = [
        {"$group": {
            "_id": "$predicted_class",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    
    disease_stats = list(predictions_collection.aggregate(pipeline))
    disease_distribution = {
        item["_id"]: item["count"] 
        for item in disease_stats 
        if item["_id"] is not None
    }
    
    # Recent predictions (last 5)
    recent = list(
        predictions_collection.find(
            {},
            {"_id": 0, "timestamp": 0, "all_predictions": 0}
        ).sort("created_at", -1).limit(5)
    )
    
    return {
        "success": True,
        "stats": {
            "total_users": total_users,
            "total_predictions": total_predictions,
            "disease_distribution": disease_distribution,
            "recent_predictions": recent
        }
    }
