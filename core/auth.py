"""
Enterprise Authentication and Authorization System
"""
import hashlib
import jwt
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class AuthManager:
    """Enterprise authentication manager"""
    
    def __init__(self, db_path: str = "smart_sene_enterprise.db", 
                 secret_key: str = "your-secret-key"):
        self.db_path = db_path
        self.secret_key = secret_key
        self.token_expiry = timedelta(hours=24)
    
    @contextmanager
    def get_connection(self):
        """Database connection context manager"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error in auth: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return self.hash_password(password) == hashed
    
    def create_user(self, username: str, email: str, password: str, 
                   role: str = "user") -> bool:
        """Create new user account"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                hashed_password = self.hash_password(password)
                
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, role)
                    VALUES (?, ?, ?, ?)
                """, (username, email, hashed_password, role))
                conn.commit()
                
                logger.info(f"User created: {username}")
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"User creation failed: {username} already exists")
            return False
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user credentials"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, username, email, password_hash, role, is_active
                    FROM users WHERE username = ? OR email = ?
                """, (username, username))
                
                user = cursor.fetchone()
                if not user:
                    return None
                
                if not user['is_active']:
                    logger.warning(f"Inactive user login attempt: {username}")
                    return None
                
                if self.verify_password(password, user['password_hash']):
                    # Update last login
                    cursor.execute("""
                        UPDATE users SET last_login = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    """, (user['id'],))
                    conn.commit()
                    
                    return {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email'],
                        'role': user['role']
                    }
                return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def generate_token(self, user_data: Dict[str, Any]) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user_data['id'],
            'username': user_data['username'],
            'role': user_data['role'],
            'exp': datetime.utcnow() + self.token_expiry,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, username, email, role, created_at, last_login, is_active
                    FROM users WHERE id = ?
                """, (user_id,))
                
                user = cursor.fetchone()
                return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    def update_user_role(self, user_id: int, new_role: str) -> bool:
        """Update user role (admin function)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET role = ? WHERE id = ?
                """, (new_role, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating user role: {e}")
            return False
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET is_active = 0 WHERE id = ?
                """, (user_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            return False
    
    def get_all_users(self) -> list:
        """Get all users (admin function)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, username, email, role, created_at, last_login, is_active
                    FROM users ORDER BY created_at DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return []

# Role-based access control
class RoleManager:
    """Manage user roles and permissions"""
    
    ROLES = {
        'admin': {
            'permissions': ['read', 'write', 'delete', 'manage_users', 'system_admin'],
            'description': 'Full system access'
        },
        'manager': {
            'permissions': ['read', 'write', 'analytics', 'team_management'],
            'description': 'Team and analytics management'
        },
        'analyst': {
            'permissions': ['read', 'write', 'analytics'],
            'description': 'Data analysis and reporting'
        },
        'user': {
            'permissions': ['read', 'write'],
            'description': 'Basic user access'
        },
        'viewer': {
            'permissions': ['read'],
            'description': 'Read-only access'
        }
    }
    
    @classmethod
    def has_permission(cls, user_role: str, required_permission: str) -> bool:
        """Check if user role has required permission"""
        if user_role not in cls.ROLES:
            return False
        return required_permission in cls.ROLES[user_role]['permissions']
    
    @classmethod
    def get_role_permissions(cls, role: str) -> list:
        """Get all permissions for a role"""
        return cls.ROLES.get(role, {}).get('permissions', [])
    
    @classmethod
    def get_available_roles(cls) -> list:
        """Get list of available roles"""
        return list(cls.ROLES.keys())

# Global auth manager instance
auth_manager = AuthManager()

# Convenience functions for backward compatibility
def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user (backward compatibility)"""
    return auth_manager.authenticate_user(username, password)

def get_user_role(user_id: int) -> Optional[str]:
    """Get user role (backward compatibility)"""
    user = auth_manager.get_user_by_id(user_id)
    return user['role'] if user else None

def create_default_admin():
    """Create default admin user if none exists"""
    try:
        # Check if any admin exists
        with auth_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
            admin_count = cursor.fetchone()['count']
            
            if admin_count == 0:
                # Create default admin
                success = auth_manager.create_user(
                    username="admin",
                    email="admin@smartsene.com",
                    password="admin123",  # Change this in production!
                    role="admin"
                )
                if success:
                    logger.info("Default admin user created: admin/admin123")
                    return True
        return False
    except Exception as e:
        logger.error(f"Error creating default admin: {e}")
        return False

# Initialize default admin on module import
create_default_admin()
