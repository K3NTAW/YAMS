import os
import mysql.connector
from dotenv import load_dotenv
import bcrypt

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        load_dotenv()
        self.conn = None
        self.connect()
        self._initialized = True

    def connect(self):
        """Connect to the MySQL database."""
        try:
            self.conn = mysql.connector.connect(
                database=os.getenv('DB_NAME', 'yams_db'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '3306')
            )
            self.conn.autocommit = True
        except Exception as e:
            print(f"Database connection error: {e}")
            self.conn = None

    def authenticate_user(self, username, password):
        """Authenticate a user and return their information."""
        if not self.conn:
            return None

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, username, password_hash, client_id, client_secret 
                FROM users 
                WHERE username = %s
            """, (username,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if not result:
                return None
            
            user_id, username, password_hash, client_id, client_secret = result
            
            if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                # Update last login
                cursor = self.conn.cursor()
                cursor.execute("""
                    UPDATE users 
                    SET last_login = CURRENT_TIMESTAMP 
                    WHERE id = %s
                """, (user_id,))
                self.conn.commit()
                cursor.close()
                
                return {
                    'id': user_id,
                    'username': username,
                    'client_id': client_id,
                    'client_secret': client_secret
                }
            return None
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return None

    def register_user(self, username, password, email, client_id, client_secret):
        """Register a new user."""
        if not self.conn:
            return False, "Database connection error"

        try:
            cursor = self.conn.cursor()
            
            # Check if username exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "Username already exists"
            
            # Check if client_id exists
            cursor.execute("SELECT id FROM users WHERE client_id = %s", (client_id,))
            if cursor.fetchone():
                return False, "Client ID already exists"
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insert new user
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, client_id, client_secret)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, password_hash, email, client_id, client_secret))
            
            self.conn.commit()
            cursor.close()
            return True, None
            
        except Exception as e:
            return False, str(e)

    def get_user_info(self, user_id):
        """Get user information including client credentials."""
        if not self.conn:
            return None

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT username, email, client_id, client_secret, created_at, last_login
                FROM users 
                WHERE id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'username': result[0],
                    'email': result[1],
                    'client_id': result[2],
                    'client_secret': result[3],
                    'created_at': result[4],
                    'last_login': result[5]
                }
            return None
            
        except Exception:
            return None
