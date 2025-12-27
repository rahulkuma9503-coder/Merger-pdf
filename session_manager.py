import os
from pymongo import MongoClient
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """Manage user sessions with MongoDB or in-memory fallback"""
    
    def __init__(self):
        self.use_mongodb = False
        self.sessions = {}  # In-memory fallback
        
        # Try to connect to MongoDB
        mongodb_uri = os.getenv('MONGODB_URI')
        if mongodb_uri:
            try:
                self.client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
                self.db = self.client['pdf_bot']
                self.sessions_collection = self.db['sessions']
                
                # Test connection
                self.client.server_info()
                self.use_mongodb = True
                logger.info("Connected to MongoDB")
                
                # Create TTL index for auto-cleanup (sessions expire after 1 hour)
                self.sessions_collection.create_index(
                    "last_activity",
                    expireAfterSeconds=3600
                )
            except Exception as e:
                logger.warning(f"MongoDB connection failed: {e}. Using in-memory storage.")
                self.use_mongodb = False
        else:
            logger.info("No MongoDB URI provided. Using in-memory storage.")
    
    def get_session(self, user_id):
        """
        Get user session data
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            Session dictionary or empty dict if not found
        """
        if self.use_mongodb:
            session = self.sessions_collection.find_one({'user_id': user_id})
            return session if session else {}
        else:
            return self.sessions.get(user_id, {})
    
    def set_state(self, user_id, state):
        """
        Set user's current state
        
        Args:
            user_id: Telegram user ID
            state: Current state string
        """
        if self.use_mongodb:
            self.sessions_collection.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'state': state,
                        'last_activity': datetime.utcnow()
                    }
                },
                upsert=True
            )
        else:
            if user_id not in self.sessions:
                self.sessions[user_id] = {}
            self.sessions[user_id]['state'] = state
    
    def get_state(self, user_id):
        """
        Get user's current state
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            Current state string or None
        """
        session = self.get_session(user_id)
        return session.get('state')
    
    def update_session(self, user_id, key, value):
        """
        Update a specific key in user session
        
        Args:
            user_id: Telegram user ID
            key: Session key to update
            value: Value to set
        """
        if self.use_mongodb:
            self.sessions_collection.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        key: value,
                        'last_activity': datetime.utcnow()
                    }
                },
                upsert=True
            )
        else:
            if user_id not in self.sessions:
                self.sessions[user_id] = {}
            self.sessions[user_id][key] = value
    
    def add_pdf(self, user_id, file_path):
        """
        Add a PDF file to user's session
        
        Args:
            user_id: Telegram user ID
            file_path: Path to the PDF file
        """
        if self.use_mongodb:
            self.sessions_collection.update_one(
                {'user_id': user_id},
                {
                    '$push': {'pdf_files': file_path},
                    '$set': {'last_activity': datetime.utcnow()}
                },
                upsert=True
            )
        else:
            if user_id not in self.sessions:
                self.sessions[user_id] = {}
            if 'pdf_files' not in self.sessions[user_id]:
                self.sessions[user_id]['pdf_files'] = []
            self.sessions[user_id]['pdf_files'].append(file_path)
    
    def clear_session(self, user_id):
        """
        Clear all session data for a user
        
        Args:
            user_id: Telegram user ID
        """
        # Clean up any temporary files
        session = self.get_session(user_id)
        pdf_files = session.get('pdf_files', [])
        for file_path in pdf_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"Error removing file {file_path}: {e}")
        
        if self.use_mongodb:
            self.sessions_collection.delete_one({'user_id': user_id})
        else:
            if user_id in self.sessions:
                del self.sessions[user_id]
    
    def cleanup_expired_sessions(self):
        """
        Cleanup expired sessions (only needed for in-memory storage)
        MongoDB has TTL index for auto-cleanup
        """
        if not self.use_mongodb:
            # Remove sessions older than 1 hour
            current_time = datetime.utcnow()
            expired_users = []
            
            for user_id, session in self.sessions.items():
                last_activity = session.get('last_activity')
                if last_activity and (current_time - last_activity) > timedelta(hours=1):
                    expired_users.append(user_id)
            
            for user_id in expired_users:
                self.clear_session(user_id)
