from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
import logging

logger = logging.getLogger(__name__)

# MongoDB connection string
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "preventix_db")

# Initialize MongoDB client
try:
    mongodb_client = MongoClient(MONGODB_URL)
    mongodb_client.admin.command('ping')
    logger.info("Successfully connected to MongoDB")
except ConnectionFailure as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise

# Get database
db = mongodb_client[DATABASE_NAME]

# Create indexes
def create_indexes():
    """Create database indexes"""
    try:
        users_collection = db["users"]
        users_collection.create_index("email", unique=True)
        
        predictions_collection = db["predictions"]
        predictions_collection.create_index([("user_id", 1), ("created_at", -1)])
        
        tracking_collection = db["tracking_data"]
        tracking_collection.create_index([("user_id", 1), ("created_at", -1)])
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

# Initialize indexes on startup
create_indexes()

# Collection getters - MUST BE SYNCHRONOUS
def get_users_collection():
    """Get users collection"""
    return db["users"]

def get_predictions_collection():
    """Get predictions collection"""
    return db["predictions"]

def get_tracking_collection():
    """Get tracking collection"""
    return db["tracking_data"]