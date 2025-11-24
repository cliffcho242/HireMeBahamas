"""
Firebase Realtime Database Service

This module provides Firebase Realtime Database integration for HireMeBahamas.
It handles initialization, CRUD operations, and real-time data synchronization.

Setup Instructions:
1. Create a Firebase project at https://console.firebase.google.com/
2. Enable Realtime Database in the Firebase Console
3. Download service account credentials (Project Settings > Service Accounts)
4. Set FIREBASE_CREDENTIALS_PATH and FIREBASE_DATABASE_URL in .env
"""

import os
import logging
from typing import Optional, Dict, Any, List
import firebase_admin
from firebase_admin import credentials, db

logger = logging.getLogger(__name__)


class FirebaseService:
    """Service class for Firebase Realtime Database operations"""
    
    _instance: Optional['FirebaseService'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern to ensure only one Firebase instance"""
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Firebase service if not already initialized"""
        if not self._initialized:
            self._initialize_firebase()
    
    def _initialize_firebase(self) -> None:
        """Initialize Firebase Admin SDK with credentials from environment"""
        try:
            # Get configuration from environment variables
            credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            database_url = os.getenv('FIREBASE_DATABASE_URL')
            
            # Check if Firebase is configured
            if not credentials_path or not database_url:
                logger.warning(
                    "Firebase Realtime Database not configured. "
                    "Set FIREBASE_CREDENTIALS_PATH and FIREBASE_DATABASE_URL to enable Firebase features."
                )
                self._initialized = False
                return
            
            # Check if credentials file exists
            if not os.path.exists(credentials_path):
                logger.warning(
                    f"Firebase credentials file not found at: {credentials_path}. "
                    "Firebase features will be disabled."
                )
                self._initialized = False
                return
            
            # Initialize Firebase app if not already initialized
            if not firebase_admin._apps:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': database_url
                })
                logger.info("Firebase Realtime Database initialized successfully")
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing Firebase: {str(e)}")
            self._initialized = False
    
    def is_available(self) -> bool:
        """Check if Firebase is properly initialized and available"""
        return self._initialized
    
    def get_reference(self, path: str) -> Optional[db.Reference]:
        """
        Get a reference to a specific path in the database
        
        Args:
            path: Database path (e.g., 'users', 'posts', 'messages/room1')
            
        Returns:
            Database reference or None if Firebase is not available
        """
        if not self.is_available():
            logger.warning("Firebase is not available. Cannot get reference.")
            return None
        
        try:
            return db.reference(path)
        except Exception as e:
            logger.error(f"Error getting Firebase reference for path '{path}': {str(e)}")
            return None
    
    def create(self, path: str, data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new record in the database
        
        Args:
            path: Database path where to create the record
            data: Dictionary containing the data to store
            
        Returns:
            The generated key for the new record, or None on error
        """
        if not self.is_available():
            return None
        
        try:
            ref = self.get_reference(path)
            if ref is None:
                return None
            
            new_ref = ref.push(data)
            logger.info(f"Created new record at {path} with key: {new_ref.key}")
            return new_ref.key
        except Exception as e:
            logger.error(f"Error creating record at path '{path}': {str(e)}")
            return None
    
    def read(self, path: str) -> Optional[Any]:
        """
        Read data from the database
        
        Args:
            path: Database path to read from
            
        Returns:
            The data at the specified path, or None on error
        """
        if not self.is_available():
            return None
        
        try:
            ref = self.get_reference(path)
            if ref is None:
                return None
            
            data = ref.get()
            return data
        except Exception as e:
            logger.error(f"Error reading from path '{path}': {str(e)}")
            return None
    
    def update(self, path: str, data: Dict[str, Any]) -> bool:
        """
        Update data at the specified path
        
        Args:
            path: Database path to update
            data: Dictionary containing the fields to update
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            ref = self.get_reference(path)
            if ref is None:
                return False
            
            ref.update(data)
            logger.info(f"Updated data at path: {path}")
            return True
        except Exception as e:
            logger.error(f"Error updating path '{path}': {str(e)}")
            return False
    
    def delete(self, path: str) -> bool:
        """
        Delete data at the specified path
        
        Args:
            path: Database path to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            ref = self.get_reference(path)
            if ref is None:
                return False
            
            ref.delete()
            logger.info(f"Deleted data at path: {path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting path '{path}': {str(e)}")
            return False
    
    def set(self, path: str, data: Any) -> bool:
        """
        Set data at the specified path (overwrites existing data)
        
        Args:
            path: Database path to set
            data: Data to write (can be dict, list, string, number, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            ref = self.get_reference(path)
            if ref is None:
                return False
            
            ref.set(data)
            logger.info(f"Set data at path: {path}")
            return True
        except Exception as e:
            logger.error(f"Error setting data at path '{path}': {str(e)}")
            return False
    
    def query(self, path: str, order_by: str, limit: Optional[int] = None) -> Optional[List[Dict]]:
        """
        Query data with ordering and limiting
        
        Args:
            path: Database path to query
            order_by: Field to order by
            limit: Maximum number of results to return
            
        Returns:
            List of matching records, or None on error
        """
        if not self.is_available():
            return None
        
        try:
            ref = self.get_reference(path)
            if ref is None:
                return None
            
            query = ref.order_by_child(order_by)
            if limit:
                query = query.limit_to_last(limit)
            
            results = query.get()
            if results:
                return [{'key': k, **v} for k, v in results.items()]
            return []
        except Exception as e:
            logger.error(f"Error querying path '{path}': {str(e)}")
            return None


# Create a singleton instance
firebase_service = FirebaseService()
