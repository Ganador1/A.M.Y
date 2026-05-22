#!/usr/bin/env python3
"""
Test script for AXIOM Database Service
Tests the database integration functionality
"""

import sys
import os

# Configure for testing with SQLite in-memory BEFORE importing app modules
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['ENABLE_DATABASE'] = 'true'

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_database
from app.services.database_service import DatabaseService, save_calculation_result
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_service():
    """Test the database service functionality"""
    logger.info("Testing AXIOM Database Service...")

    try:
        # Initialize database
        logger.info("Initializing database...")
        init_database()

        # Test with context manager to keep session alive
        with DatabaseService() as db:
            # Test user operations
            logger.info("Testing user operations...")
            db.create_user(
                username="test_user",
                email="test@example.com",
                hashed_password="hashed_password_123",
                full_name="Test User"
            )
            logger.info("Created user successfully")

            # Test calculation saving
            logger.info("Testing calculation operations...")
            db.save_calculation(
                user_id=1,  # Use a fixed ID for testing
                operation_type="arithmetic",
                operation_name="addition",
                input_data={"a": 5, "b": 3},
                result_data={"result": 8},
                execution_time=0.001
            )
            logger.info("Saved calculation successfully")

            # Test cache operations
            logger.info("Testing cache operations...")
            db.save_cache_result(
                cache_key="test_key_123",
                operation_type="arithmetic",
                input_data={"a": 5, "b": 3},
                result_data={"result": 8},
                ttl_seconds=3600
            )
            logger.info("Saved cache result successfully")

            # Test retrieval
            retrieved_cache = db.get_cache_result("test_key_123")
            if retrieved_cache:
                logger.info("Retrieved cache result successfully")
            else:
                logger.warning("Cache result not found")

            # Test metrics
            logger.info("Testing metrics operations...")
            db.save_metric(
                metric_name="test_metric",
                metric_value=42.5,
                metric_unit="ms"
            )
            logger.info("Saved metric successfully")

        # Test convenience function
        logger.info("Testing convenience functions...")
        success = save_calculation_result(
            user_id=1,  # Use fixed ID
            operation_type="test",
            operation_name="convenience_test",
            input_data={"test": True},
            result_data={"success": True},
            execution_time=0.002
        )
        logger.info(f"Convenience function result: {success}")

        # Test statistics
        with DatabaseService() as db:
            stats = db.get_calculation_stats(user_id=1)  # Use fixed ID
            logger.info(f"Calculation stats: {stats}")

        logger.info("✅ All database tests completed successfully!")

    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = test_database_service()
    sys.exit(0 if success else 1)
