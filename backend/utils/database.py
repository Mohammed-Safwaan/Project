"""
Database utilities for skin lesion detection app
SQLite database for storing predictions and image metadata
"""

import sqlite3
import os
import datetime
import json
import logging
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "skin_lesion_db.sqlite"):
        """
        Initialize database manager
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    def init_database(self):
        """Initialize database with required tables"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Create predictions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image_filename TEXT NOT NULL,
                        image_path TEXT NOT NULL,
                        predicted_class INTEGER NOT NULL,
                        class_name TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        risk_level TEXT NOT NULL,
                        risk_color TEXT NOT NULL,
                        description TEXT NOT NULL,
                        is_malignant BOOLEAN NOT NULL,
                        all_probabilities TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        image_size TEXT,
                        processing_time REAL
                    )
                ''')
                
                # Create index for faster queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_predictions_created_at 
                    ON predictions(created_at DESC)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_predictions_risk_level 
                    ON predictions(risk_level)
                ''')
                
                # Create users table (optional for future use)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def save_prediction(self, prediction_data: Dict, image_info: Dict) -> int:
        """
        Save prediction result to database
        
        Args:
            prediction_data (dict): Prediction results from model
            image_info (dict): Image metadata (filename, path, size, etc.)
            
        Returns:
            int: ID of saved prediction record
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO predictions (
                        image_filename, image_path, predicted_class, class_name,
                        confidence, risk_level, risk_color, description, is_malignant,
                        all_probabilities, image_size, processing_time
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    image_info['filename'],
                    image_info['path'],
                    prediction_data['predicted_class'],
                    prediction_data['class_name'],
                    prediction_data['confidence'],
                    prediction_data['risk_level'],
                    prediction_data['risk_color'],
                    prediction_data['description'],
                    prediction_data['is_malignant'],
                    json.dumps(prediction_data['all_probabilities']),
                    json.dumps(image_info.get('size', {})),
                    image_info.get('processing_time', 0.0)
                ))
                
                prediction_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Prediction saved with ID: {prediction_id}")
                return prediction_id
                
        except Exception as e:
            logger.error(f"Error saving prediction: {str(e)}")
            raise
    
    def get_prediction_by_id(self, prediction_id: int) -> Optional[Dict]:
        """Get single prediction by ID"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM predictions WHERE id = ?
                ''', (prediction_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Error getting prediction: {str(e)}")
            raise
    
    def get_predictions_history(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        Get prediction history with pagination
        
        Args:
            limit (int): Maximum number of records to return
            offset (int): Number of records to skip
            
        Returns:
            List[Dict]: List of prediction records
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM predictions 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
                
                rows = cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting predictions history: {str(e)}")
            raise
    
    def get_predictions_by_risk(self, risk_level: str) -> List[Dict]:
        """Get predictions filtered by risk level (Malignant/Benign)"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM predictions 
                    WHERE risk_level = ? 
                    ORDER BY created_at DESC
                ''', (risk_level,))
                
                rows = cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting predictions by risk: {str(e)}")
            raise
    
    def delete_prediction(self, prediction_id: int) -> bool:
        """Delete prediction record"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM predictions WHERE id = ?
                ''', (prediction_id,))
                
                conn.commit()
                deleted = cursor.rowcount > 0
                
                if deleted:
                    logger.info(f"Prediction {prediction_id} deleted successfully")
                else:
                    logger.warning(f"No prediction found with ID {prediction_id}")
                
                return deleted
                
        except Exception as e:
            logger.error(f"Error deleting prediction: {str(e)}")
            raise
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Total predictions
                cursor.execute('SELECT COUNT(*) as total FROM predictions')
                total = cursor.fetchone()['total']
                
                # Predictions by risk level
                cursor.execute('''
                    SELECT risk_level, COUNT(*) as count 
                    FROM predictions 
                    GROUP BY risk_level
                ''')
                risk_stats = {row['risk_level']: row['count'] for row in cursor.fetchall()}
                
                # Predictions by class
                cursor.execute('''
                    SELECT class_name, COUNT(*) as count 
                    FROM predictions 
                    GROUP BY class_name 
                    ORDER BY count DESC
                ''')
                class_stats = {row['class_name']: row['count'] for row in cursor.fetchall()}
                
                # Recent activity (last 7 days)
                cursor.execute('''
                    SELECT COUNT(*) as recent_count 
                    FROM predictions 
                    WHERE created_at >= datetime('now', '-7 days')
                ''')
                recent_activity = cursor.fetchone()['recent_count']
                
                return {
                    'total_predictions': total,
                    'risk_level_distribution': risk_stats,
                    'class_distribution': class_stats,
                    'recent_activity_7days': recent_activity
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            raise
    
    def _row_to_dict(self, row) -> Dict:
        """Convert SQLite row to dictionary"""
        result = dict(row)
        
        # Parse JSON fields
        if 'all_probabilities' in result and result['all_probabilities']:
            result['all_probabilities'] = json.loads(result['all_probabilities'])
        
        if 'image_size' in result and result['image_size']:
            result['image_size'] = json.loads(result['image_size'])
        
        # Convert boolean fields
        if 'is_malignant' in result:
            result['is_malignant'] = bool(result['is_malignant'])
        
        return result
    
    def cleanup_old_predictions(self, days_old: int = 30) -> int:
        """
        Clean up old prediction records
        
        Args:
            days_old (int): Delete records older than this many days
            
        Returns:
            int: Number of records deleted
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM predictions 
                    WHERE created_at < datetime('now', '-{} days')
                '''.format(days_old))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old prediction records")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error cleaning up old predictions: {str(e)}")
            raise

# Utility function for easy database access
def get_database_manager(db_path: str = None) -> DatabaseManager:
    """Get database manager instance"""
    if db_path is None:
        # Default to backend directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(backend_dir, '..', 'skin_lesion_db.sqlite')
    
    return DatabaseManager(db_path)