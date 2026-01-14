"""
MongoDB database service
"""
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Optional, List, Dict
from bson import ObjectId

from app.config import settings
from app.utils.logger import logger


class Database:
    """MongoDB database manager"""
    
    client: Optional[AsyncIOMotorClient] = None
    db = None
    
    @classmethod
    async def connect(cls):
        """Connect to MongoDB"""
        try:
            cls.client = AsyncIOMotorClient(settings.mongodb_url)
            cls.db = cls.client[settings.mongodb_db_name]
            
            # Test connection
            await cls.client.admin.command('ping')
            
            logger.info(f"✅ Connected to MongoDB: {settings.mongodb_db_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            # Don't raise - allow app to run without DB if needed
            cls.client = None
            cls.db = None
    
    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB"""
        if cls.client:
            cls.client.close()
            logger.info("Disconnected from MongoDB")
    
    @classmethod
    def is_connected(cls) -> bool:
        """Check if connected to MongoDB"""
        return cls.client is not None and cls.db is not None


class PredictionHistory:
    """
    Service for managing prediction history in MongoDB
    """
    
    COLLECTION_NAME = "predictions"
    
    @classmethod
    async def save_prediction(
        cls,
        image_filename: str,
        prediction_result: Dict,
        processing_time_ms: float
    ) -> Optional[str]:
        """
        Save prediction to database
        
        Args:
            image_filename: Original image filename
            prediction_result: Prediction result dictionary
            processing_time_ms: Processing time in milliseconds
            
        Returns:
            Inserted document ID as string, or None if failed
        """
        if not Database.is_connected():
            logger.warning("MongoDB not connected, skipping save")
            return None
        
        try:
            collection = Database.db[cls.COLLECTION_NAME]
            
            # Prepare document
            document = {
                "image_filename": image_filename,
                "timestamp": datetime.utcnow(),
                "prediction": {
                    "genus": prediction_result["ensemble_prediction"]["genus"],
                    "confidence": prediction_result["ensemble_prediction"]["confidence"],
                    "toxicity": prediction_result["ensemble_prediction"]["toxicity"]["label"],
                    "is_poisonous": prediction_result["ensemble_prediction"]["toxicity"]["is_poisonous"],
                    "warning": prediction_result["ensemble_prediction"]["toxicity"]["warning"]
                },
                "top_predictions": [
                    {
                        "rank": p["rank"],
                        "genus": p["genus"],
                        "confidence": p["confidence"]
                    }
                    for p in prediction_result.get("top_predictions", [])
                ],
                "individual_models": [
                    {
                        "model": m["model"],
                        "genus": m["genus"],
                        "confidence": m["confidence"]
                    }
                    for m in prediction_result.get("individual_models", [])
                ],
                "processing_time_ms": processing_time_ms,
                "metadata": {
                    "ensemble_type": "Soft Voting",
                    "num_models": 3
                }
            }
            
            # Insert document
            result = await collection.insert_one(document)
            
            logger.info(f"Prediction saved to DB: {result.inserted_id}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error saving prediction to DB: {str(e)}")
            return None
    
    @classmethod
    async def get_recent_predictions(
        cls,
        limit: int = 10,
        skip: int = 0
    ) -> List[Dict]:
        """
        Get recent predictions
        
        Args:
            limit: Maximum number of records to return
            skip: Number of records to skip (for pagination)
            
        Returns:
            List of prediction documents
        """
        if not Database.is_connected():
            return []
        
        try:
            collection = Database.db[cls.COLLECTION_NAME]
            
            cursor = collection.find().sort("timestamp", -1).skip(skip).limit(limit)
            
            predictions = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
                # Convert datetime to ISO string for JSON serialization
                if "timestamp" in doc and doc["timestamp"]:
                    doc["timestamp"] = doc["timestamp"].isoformat()
                predictions.append(doc)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error getting recent predictions: {str(e)}")
            return []
    
    @classmethod
    async def get_statistics(cls) -> Dict:
        """
        Get prediction statistics
        
        Returns:
            Dictionary with statistics
        """
        if not Database.is_connected():
            return {
                "total_predictions": 0,
                "poisonous_count": 0,
                "edible_count": 0,
                "avg_confidence": 0
            }
        
        try:
            collection = Database.db[cls.COLLECTION_NAME]
            
            # Total count
            total = await collection.count_documents({})
            
            # Poisonous count
            poisonous = await collection.count_documents({"prediction.is_poisonous": True})
            
            # Edible count
            edible = total - poisonous
            
            # Average confidence
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "avg_confidence": {"$avg": "$prediction.confidence"}
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            avg_confidence = result[0]["avg_confidence"] if result else 0
            
            # Most common genera
            pipeline = [
                {
                    "$group": {
                        "_id": "$prediction.genus",
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            
            cursor = collection.aggregate(pipeline)
            top_genera = await cursor.to_list(length=5)
            
            return {
                "total_predictions": total,
                "poisonous_count": poisonous,
                "edible_count": edible,
                "avg_confidence": round(avg_confidence, 2),
                "top_genera": [
                    {"genus": g["_id"], "count": g["count"]}
                    for g in top_genera
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {
                "total_predictions": 0,
                "poisonous_count": 0,
                "edible_count": 0,
                "avg_confidence": 0,
                "error": str(e)
            }
    
    @classmethod
    async def delete_old_predictions(cls, days: int = 30) -> int:
        """
        Delete predictions older than specified days
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of deleted documents
        """
        if not Database.is_connected():
            return 0
        
        try:
            from datetime import timedelta
            
            collection = Database.db[cls.COLLECTION_NAME]
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await collection.delete_many({"timestamp": {"$lt": cutoff_date}})
            
            logger.info(f"Deleted {result.deleted_count} old predictions")
            
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting old predictions: {str(e)}")
            return 0


