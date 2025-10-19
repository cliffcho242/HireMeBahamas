from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import sqlite3
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
import os
import threading
import time

# Load environment variables from .env file
load_dotenv()

print("Initializing Flask app...")
app = Flask(__name__)

# Production configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Rate limiting configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Caching configuration
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',  # Use Redis in production: 'redis'
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Enhanced CORS configuration for production and development
CORS(app,
     resources={r"/*": {"origins": "*"}},  # Allow all origins for development
     supports_credentials=False,  # Set to False when using wildcard origin
     max_age=3600,  # Cache preflight requests for 1 hour
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-Retry-Count"],
     expose_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
STORIES_FOLDER = os.path.join(UPLOAD_FOLDER, 'stories')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STORIES_FOLDER'] = STORIES_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'webm'}

# Ensure upload directories exist
os.makedirs(STORIES_FOLDER, exist_ok=True)

# Database connection pool for concurrent access
_db_connections = {}
_db_lock = threading.Lock()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Serve uploaded files with caching
@app.route('/uploads/<path:filename>')
@cache.cached(timeout=3600)  # Cache for 1 hour
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Optimized database connection with connection pooling for concurrent access
_db_connections = {}
_db_lock = threading.Lock()

def get_db_connection():
    """Get database connection with proper timeout and error handling"""
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrent access
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA cache_size=1000')  # 1MB cache
    return conn

def close_db_connections():
    """Clean up database connections"""
    pass  # Simplified for now

# Register cleanup on app shutdown
@app.teardown_appcontext
def cleanup_db_connections(exception=None):
    """Clean up database connections on app context teardown"""
    pass  # Simplified for now

# Graceful shutdown handler
# def signal_handler(sig, frame):
#     print('\n⚠️  Shutting down gracefully...')
#     sys.exit(0)

# signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGTERM, signal_handler)

# Database path
DB_PATH = Path(__file__).parent / "hiremebahamas.db"
print(f"Database path: {DB_PATH}")
print(f"Database exists: {DB_PATH.exists()}")

def init_database():
    """Initialize database with all required tables"""
    if not DB_PATH.exists():
        print("📦 Database not found - creating new database...")
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            user_type TEXT DEFAULT 'user',
            location TEXT,
            phone TEXT,
            bio TEXT,
            avatar_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            is_available_for_hire BOOLEAN DEFAULT 0,
            trade TEXT DEFAULT ''
        )''')
        
        # Create posts table
        cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )''')
        
        # Create post_likes table
        cursor.execute('''CREATE TABLE IF NOT EXISTS post_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
            UNIQUE(user_id, post_id)
        )''')
        
        # Create friendships table
        cursor.execute('''CREATE TABLE IF NOT EXISTS friendships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id),
            UNIQUE(sender_id, receiver_id)
        )''')
        
        # Create friend_requests table
        cursor.execute('''CREATE TABLE IF NOT EXISTS friend_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id),
            UNIQUE(sender_id, receiver_id)
        )''')
        
        # Create stories table
        cursor.execute('''CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            image_url TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            video_url TEXT DEFAULT '',
            image_path TEXT DEFAULT '',
            video_path TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )''')
        
        # Create jobs table
        cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            job_type TEXT NOT NULL,
            description TEXT NOT NULL,
            requirements TEXT,
            salary_range TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )''')
        
        # Create default admin user
        print("👤 Creating default admin user...")
        password_hash = bcrypt.hashpw('AdminPass123!'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('''INSERT INTO users 
            (email, password_hash, first_name, last_name, user_type, location, phone, bio, created_at, last_login)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'admin@hiremebahamas.com',
            password_hash,
            'Admin',
            'User',
            'admin',
            'Nassau, Bahamas',
            '+1-242-555-0100',
            'HireMeBahamas Platform Administrator',
            datetime.now(timezone.utc),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
        print("✅ Admin user created: admin@hiremebahamas.com")
    else:
        print("✅ Database already exists")

# Initialize database on startup
init_database()

@app.route('/health')
def health():
    """Enhanced health check with system monitoring"""
    try:
        # Test database connection
        conn = get_db_connection()
        conn.execute('SELECT 1')
        db_status = "healthy"
        conn.close()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return jsonify({
        "status": "healthy" if db_status == "healthy" else "degraded",
        "message": "HireMeBahamas API is running",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "concurrency": {
            "active_connections": len(_db_connections),
            "max_connections": 100  # Configurable limit
        }
    })

@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    """Register a new user"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()

        required_fields = ['email', 'password', 'first_name', 'last_name', 'user_type', 'location']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({
                    "success": False,
                    "message": f"{field.replace('_', ' ').title()} is required"
                }), 400

        email = data['email'].strip().lower()
        password = data['password']

        # Validate password strength (minimum 8 characters, at least one number and one letter)
        if len(password) < 8 or not any(c.isdigit() for c in password) or not any(c.isalpha() for c in password):
            return jsonify({
                "success": False,
                "message": "Password must be at least 8 characters with at least one letter and one number"
            }), 400

        # Check if user already exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE LOWER(email) = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                "success": False,
                "message": "User with this email already exists"
            }), 409

        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insert new user
        cursor.execute('''
            INSERT INTO users (email, password_hash, first_name, last_name, user_type, location, phone, bio, is_active, created_at, last_login, is_available_for_hire)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, 0)
        ''', (
            email, password_hash, data['first_name'].strip(), data['last_name'].strip(), 
            data['user_type'], data['location'].strip(), data.get('phone', '').strip(), 
            data.get('bio', '').strip(), datetime.now(timezone.utc), datetime.now(timezone.utc)
        ))

        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Get the created user
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        # Create JWT token
        token_payload = {
            'user_id': user['id'],
            'email': user['email'],
            'exp': datetime.now(timezone.utc) + timedelta(days=7)
        }

        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
            "success": True,
            "message": "Registration successful",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user['id'],
                "email": user['email'],
                "first_name": user['first_name'] or '',
                "last_name": user['last_name'] or '',
                "user_type": user['user_type'] or 'user',
                "location": user['location'] or '',
                "phone": user['phone'] or '',
                "bio": user['bio'] or '',
                "avatar_url": user['avatar_url'] or '',
                "is_available_for_hire": bool(user['is_available_for_hire'])
            }
        }), 201

    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Registration failed"
        }), 500

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    """Authenticate user and return JWT token"""
    print("="*60)
    print("Login endpoint called")
    print(f"Request method: {request.method}")
    print(f"Request origin: {request.headers.get('Origin', 'No origin header')}")
    print(f"Request headers: {dict(request.headers)}")

    if request.method == 'OPTIONS':
        print("OPTIONS request - returning CORS headers")
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Retry-Count')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, 200

    try:
        data = request.get_json()
        print(f"Login data received: {data}")

        if not data or 'email' not in data or 'password' not in data:
            print("ERROR: Missing email or password")
            return jsonify({
                "success": False,
                "message": "Email and password required"
            }), 400

        email = data['email'].strip().lower()
        password = data['password']

        print(f"Attempting login for: {email}")

        # Get database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Find user by email
        cursor.execute('SELECT * FROM users WHERE LOWER(email) = ? AND is_active = 1', (email,))
        user = cursor.fetchone()

        if not user:
            print("User not found")
            conn.close()
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401

        # Verify password
        stored_hash = user['password_hash']
        if not bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            print("Password verification failed")
            conn.close()
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401

        # Update last login
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                      (datetime.now(timezone.utc), user['id']))
        conn.commit()
        conn.close()

        # Create JWT token
        token_payload = {
            'user_id': user['id'],
            'email': user['email'],
            'exp': datetime.now(timezone.utc) + timedelta(days=7)  # 7 days expiration
        }

        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')

        print(f"Login successful for user: {email}")

        return jsonify({
            "success": True,
            "message": "Login successful",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user['id'],
                "email": user['email'],
                "first_name": user['first_name'] or '',
                "last_name": user['last_name'] or '',
                "user_type": user['user_type'] or 'user',
                "location": user['location'] or '',
                "phone": user['phone'] or '',
                "bio": user['bio'] or '',
                "avatar_url": user['avatar_url'] or '',
                "is_available_for_hire": bool(user['is_available_for_hire'])
            }
        }), 200

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Login failed"
        }), 500

@app.route('/api/auth/profile', methods=['GET', 'OPTIONS'])
def get_profile():
    """Get current user profile"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization token required'
            }), 401

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, email, first_name, last_name, user_type, location, phone, bio,
                   avatar_url, created_at, last_login, is_active, is_available_for_hire
            FROM users WHERE id = ?
        ''', (user_id,))

        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        return jsonify({
            'success': True,
            'id': user[0],
            'email': user[1],
            'first_name': user[2] or '',
            'last_name': user[3] or '',
            'user_type': user[4] or 'user',
            'location': user[5] or '',
            'phone': user[6] or '',
            'bio': user[7] or '',
            'avatar_url': user[8] or '',
            'created_at': user[9],
            'last_login': user[10],
            'is_active': bool(user[11]),
            'is_available_for_hire': bool(user[12])
        }), 200

    except Exception as e:
        print(f"Error getting profile: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get profile'
        }), 500

# Posts API endpoints
@app.route('/api/posts', methods=['GET', 'OPTIONS'])
def get_posts():
    """Get all posts"""
    print("GET POSTS ENDPOINT CALLED")
    if request.method == 'OPTIONS':
        return '', 200

    try:
        print("GET POSTS ENDPOINT CALLED")
        print("Getting posts")

        # Test database connection
        conn = get_db_connection()
        print("Database connection successful")
        cursor = conn.cursor()
        print("Cursor created")

        cursor.execute('SELECT COUNT(*) FROM posts')
        count = cursor.fetchone()
        print(f"Posts count: {count}")

        cursor.execute('''
            SELECT
                p.id as id, p.content as content, p.image_url as image_url, p.created_at as created_at,
                u.id as user_id, u.first_name as first_name, u.last_name as last_name, u.email as email, u.user_type as user_type
            FROM posts p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
        ''')
        print("Query executed")

        posts_data = cursor.fetchall()
        print(f"Fetched {len(posts_data)} posts")
        conn.close()
        print("Connection closed")

        # Format posts for frontend
        posts = []
        for row in posts_data:
            posts.append({
                'id': row['id'],
                'content': row['content'],
                'image_url': row['image_url'],
                'created_at': row['created_at'],
                'user': {
                    'id': row['user_id'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'email': row['email'],
                    'user_type': row['user_type']
                },
                'likes_count': 0,  # We'll implement this later
                'comments_count': 0  # We'll implement this later
            })

        print(f"Retrieved {len(posts)} posts")
        return jsonify({
            "success": True,
            "posts": posts,
            "recommendations": [],  # For SocialFeed compatibility
            "ai_insights": {  # For SocialFeed compatibility
                "user_type": "professional",
                "engagement_score": 85,
                "activity_trend": "increasing"
            }
        }), 200

    except Exception as e:
        print(f"Get posts error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Failed to get posts",
            "posts": []  # Always return posts array even on error
        }), 500

@app.route('/api/posts', methods=['POST', 'OPTIONS'])
def create_post():
    """Create a new post"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # Check authentication
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.replace('Bearer ', '')

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        data = request.get_json()
        content = data.get('content', '').strip()

        if not content:
            return jsonify({"success": False, "message": "Content is required"}), 400

        # Insert post into database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO posts (user_id, content, created_at)
            VALUES (?, ?, ?)
        ''', (user_id, content, datetime.utcnow()))

        post_id = cursor.lastrowid
        conn.commit()

        # Get the created post with user info
        cursor.execute('''
            SELECT p.id, p.content, p.created_at, u.first_name, u.last_name, u.email, u.user_type
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = ?
        ''', (post_id,))

        post_row = cursor.fetchone()
        conn.close()

        post = {
            "id": post_row[0],
            "content": post_row[1],
            "created_at": post_row[2],
            "user": {
                "id": user_id,
                "first_name": post_row[3],
                "last_name": post_row[4],
                "email": post_row[5],
                "user_type": post_row[6]
            },
            "likes_count": 0
        }

        print(f"Post created by user {user_id}")
        return jsonify({
            "success": True,
            "message": "Post created successfully",
            "post": post
        }), 201

    except Exception as e:
        print(f"Create post error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Failed to create post"
        }), 500

@app.route('/api/posts/<int:post_id>/like', methods=['POST', 'OPTIONS'])
def like_post(post_id):
    """Like a post"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # Check authentication
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.replace('Bearer ', '')

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        # For now, just return success since we don't have likes table fully implemented
        print(f"Post {post_id} liked by user {user_id}")
        return jsonify({
            "success": True,
            "message": "Post liked successfully"
        }), 200

    except Exception as e:
        print(f"Like post error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Failed to like post"
        }), 500

@app.route('/api/upload/story-file', methods=['POST', 'OPTIONS'])
def upload_story_file():
    """Upload a file for stories (image or video)"""
    print("UPLOAD STORY FILE ENDPOINT CALLED")
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # Check authentication
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.replace('Bearer ', '')

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        if 'file' not in request.files:
            return jsonify({"success": False, "message": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "message": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"success": False, "message": "File type not allowed"}), 400

        # Generate unique filename
        import uuid
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(app.config['STORIES_FOLDER'], unique_filename)

        # Save file
        file.save(file_path)

        # Return file URL
        file_url = f"http://127.0.0.1:8008/uploads/stories/{unique_filename}"

        return jsonify({
            "success": True,
            "file_url": file_url,
            "file_path": f"stories/{unique_filename}"
        }), 201

    except Exception as e:
        print(f"File upload error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Failed to upload file"
        }), 500

@app.route('/api/stories', methods=['GET', 'OPTIONS'])
def get_stories():
    """Get all stories"""
    print("GET STORIES ENDPOINT CALLED")
    if request.method == 'OPTIONS':
        return '', 200

    try:
        print("Getting stories")

        # Test database connection
        conn = get_db_connection()
        print("Database connection successful")
        cursor = conn.cursor()
        print("Cursor created")

        cursor.execute('SELECT COUNT(*) FROM stories')
        count = cursor.fetchone()
        print(f"Stories count: {count}")

        cursor.execute('''
            SELECT
                s.id as id, s.content as content, s.image_path as image_path, s.video_path as video_path, s.created_at as created_at,
                u.id as user_id, u.first_name as first_name, u.last_name as last_name, u.email as email, u.user_type as user_type
            FROM stories s
            JOIN users u ON s.user_id = u.id
            ORDER BY s.created_at DESC
        ''')
        print("Query executed")

        stories_data = cursor.fetchall()
        print(f"Fetched {len(stories_data)} stories")
        conn.close()
        print("Connection closed")

        # Format stories for frontend
        stories = []
        for row in stories_data:
            # Convert file paths to URLs
            image_url = f"http://127.0.0.1:8008/uploads/{row['image_path']}" if row['image_path'] else ''
            video_url = f"http://127.0.0.1:8008/uploads/{row['video_path']}" if row['video_path'] else ''

            stories.append({
                'id': row['id'],
                'content': row['content'],
                'image_url': image_url,
                'video_url': video_url,
                'created_at': row['created_at'],
                'user': {
                    'id': row['user_id'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'email': row['email'],
                    'user_type': row['user_type']
                }
            })

        print(f"Returning {len(stories)} stories")
        return jsonify({
            "success": True,
            "stories": stories
        }), 200

    except Exception as e:
        print(f"Error getting stories: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Failed to get stories"
        }), 500

@app.route('/api/stories', methods=['POST', 'OPTIONS'])
def create_story():
    """Create a new story"""
    print("CREATE STORY ENDPOINT CALLED")
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # Check authentication
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.replace('Bearer ', '')

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        data = request.get_json()
        content = data.get('content', '').strip()
        image_path = data.get('image_path', '').strip()
        video_path = data.get('video_path', '').strip()

        if not content:
            return jsonify({"success": False, "message": "Content is required"}), 400

        # Insert story into database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO stories (user_id, content, image_path, video_path, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, content, image_path, video_path, datetime.utcnow()))

        story_id = cursor.lastrowid
        conn.commit()

        # Get the created story with user info
        cursor.execute('''
            SELECT s.id, s.content, s.image_path, s.video_path, s.created_at, u.first_name, u.last_name, u.email, u.user_type
            FROM stories s
            JOIN users u ON s.user_id = u.id
            WHERE s.id = ?
        ''', (story_id,))

        story_row = cursor.fetchone()
        conn.close()

        # Convert file paths to URLs for response
        image_url = f"http://127.0.0.1:8008/uploads/{story_row[2]}" if story_row[2] else ''
        video_url = f"http://127.0.0.1:8008/uploads/{story_row[3]}" if story_row[3] else ''

        story = {
            "id": story_row[0],
            "content": story_row[1],
            "image_url": image_url,
            "video_url": video_url,
            "created_at": story_row[4],
            "user": {
                "id": user_id,
                "first_name": story_row[5],
                "last_name": story_row[6],
                "email": story_row[7],
                "user_type": story_row[8]
            }
        }

        print(f"Story created by user {user_id}")
        return jsonify({
            "success": True,
            "message": "Story created successfully",
            "story": story
        }), 201

    except Exception as e:
        print(f"Create story error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Failed to create story"
        }), 500

@app.route('/api/hireme/available', methods=['GET', 'OPTIONS'])
def get_available_users():
    """Get users available for hire with optional trade search"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # Get search query parameter
        search_query = request.args.get('search', '').strip().lower()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Build query based on search
        if search_query:
            # Search by trade, first_name, last_name, or bio
            cursor.execute('''
                SELECT id, first_name, last_name, email, user_type, location, phone, bio, avatar_url, created_at, trade
                FROM users
                WHERE is_available_for_hire = 1 AND is_active = 1
                AND (
                    LOWER(trade) LIKE ?
                    OR LOWER(first_name) LIKE ?
                    OR LOWER(last_name) LIKE ?
                    OR LOWER(bio) LIKE ?
                )
                ORDER BY created_at DESC
            ''', (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
        else:
            # Get all available users
            cursor.execute('''
                SELECT id, first_name, last_name, email, user_type, location, phone, bio, avatar_url, created_at, trade
                FROM users
                WHERE is_available_for_hire = 1 AND is_active = 1
                ORDER BY created_at DESC
            ''')

        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'first_name': row[1] or '',
                'last_name': row[2] or '',
                'email': row[3],
                'user_type': row[4] or 'user',
                'location': row[5] or '',
                'phone': row[6] or '',
                'bio': row[7] or '',
                'avatar_url': row[8] or '',
                'created_at': row[9],
                'trade': row[10] or ''
            })

        conn.close()

        return jsonify({
            'success': True,
            'users': users,
            'count': len(users),
            'search_query': search_query
        }), 200

    except Exception as e:
        print(f"Error getting available users: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get available users'
        }), 500

@app.route('/api/hireme/toggle', methods=['POST', 'OPTIONS'])
def toggle_availability():
    """Toggle user's availability for hire"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization token required'
            }), 401

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get current availability status
        cursor.execute('SELECT is_available_for_hire FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        current_status = result[0]
        new_status = 0 if current_status else 1

        # Update availability status
        cursor.execute('UPDATE users SET is_available_for_hire = ? WHERE id = ?', (new_status, user_id))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Availability {"enabled" if new_status else "disabled"}',
            'is_available': bool(new_status)
        }), 200

    except Exception as e:
        print(f"Error toggling availability: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update availability'
        }), 500

# Removed duplicate get_user_profile function - using get_profile instead

@app.route('/api/auth/profile', methods=['PUT', 'OPTIONS'])
def update_profile():
    """Update current user profile"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization token required'
            }), 401

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 401

        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Update user profile
        cursor.execute('''
            UPDATE users SET
                first_name = ?,
                last_name = ?,
                location = ?,
                phone = ?,
                bio = ?,
                last_login = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data.get('first_name'),
            data.get('last_name'),
            data.get('location'),
            data.get('phone'),
            data.get('bio'),
            user_id
        ))

        conn.commit()

        # Get updated user data
        cursor.execute('''
            SELECT id, email, first_name, last_name, user_type, location, phone, bio,
                   avatar_url, created_at, last_login, is_active, is_available_for_hire
            FROM users WHERE id = ?
        ''', (user_id,))

        user = cursor.fetchone()
        conn.close()

        return jsonify({
            'success': True,
            'id': user[0],
            'email': user[1],
            'first_name': user[2] or '',
            'last_name': user[3] or '',
            'user_type': user[4] or 'user',
            'location': user[5] or '',
            'phone': user[6] or '',
            'bio': user[7] or '',
            'avatar_url': user[8] or '',
            'created_at': user[9],
            'last_login': user[10],
            'is_active': bool(user[11]),
            'is_available_for_hire': bool(user[12])
        }), 200

    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update profile'
        }), 500

# Friends endpoints
@app.route('/api/friends/send-request/<int:user_id>', methods=['POST', 'OPTIONS'])
def send_friend_request(user_id):
    """Send a friend request to another user"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization token required'
            }), 401

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            sender_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 401

        if sender_id == user_id:
            return jsonify({
                'success': False,
                'message': 'Cannot send friend request to yourself'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if users exist
        cursor.execute('SELECT id FROM users WHERE id IN (?, ?)', (sender_id, user_id))
        users = cursor.fetchall()
        if len(users) != 2:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        # Check if friendship already exists
        cursor.execute('''
            SELECT status FROM friendships
            WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
        ''', (sender_id, user_id, user_id, sender_id))

        existing = cursor.fetchone()
        if existing:
            status = existing[0]
            if status == 'accepted':
                conn.close()
                return jsonify({
                    'success': False,
                    'message': 'Already friends'
                }), 400
            elif status == 'pending':
                conn.close()
                return jsonify({
                    'success': False,
                    'message': 'Friend request already sent'
                }), 400

        # Create friend request
        cursor.execute('''
            INSERT OR REPLACE INTO friendships (sender_id, receiver_id, status, updated_at)
            VALUES (?, ?, 'pending', CURRENT_TIMESTAMP)
        ''', (sender_id, user_id))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Friend request sent successfully'
        }), 201

    except Exception as e:
        print(f"Error sending friend request: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to send friend request'
        }), 500

@app.route('/api/friends/requests', methods=['GET', 'OPTIONS'])
def get_friend_requests():
    """Get friend requests for current user"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization token required'
            }), 401

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get incoming friend requests
        cursor.execute('''
            SELECT f.id, f.sender_id, f.created_at,
                   u.first_name, u.last_name, u.email, u.avatar_url
            FROM friendships f
            JOIN users u ON f.sender_id = u.id
            WHERE f.receiver_id = ? AND f.status = 'pending'
            ORDER BY f.created_at DESC
        ''', (user_id,))

        requests = []
        for row in cursor.fetchall():
            requests.append({
                'id': row[0],
                'sender_id': row[1],
                'created_at': row[2],
                'sender': {
                    'id': row[1],
                    'first_name': row[3] or '',
                    'last_name': row[4] or '',
                    'email': row[5],
                    'avatar_url': row[6] or ''
                }
            })

        conn.close()

        return jsonify({
            'success': True,
            'requests': requests
        }), 200

    except Exception as e:
        print(f"Error getting friend requests: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get friend requests'
        }), 500

@app.route('/api/friends/respond/<int:request_id>', methods=['POST', 'OPTIONS'])
def respond_to_friend_request(request_id):
    """Accept or decline a friend request"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        action = data.get('action')  # 'accept' or 'decline'

        if action not in ['accept', 'decline']:
            return jsonify({
                'success': False,
                'message': 'Invalid action'
            }), 400

        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization token required'
            }), 401

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if request exists and belongs to user
        cursor.execute('''
            SELECT sender_id FROM friendships
            WHERE id = ? AND receiver_id = ? AND status = 'pending'
        ''', (request_id, user_id))

        result = cursor.fetchone()
        if not result:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Friend request not found'
            }), 404

        sender_id = result[0]

        if action == 'accept':
            # Update friendship status to accepted
            cursor.execute('''
                UPDATE friendships SET status = 'accepted', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (request_id,))
        else:
            # Delete the friend request
            cursor.execute('DELETE FROM friendships WHERE id = ?', (request_id,))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Friend request {action}ed successfully'
        }), 200

    except Exception as e:
        print(f"Error responding to friend request: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to respond to friend request'
        }), 500

@app.route('/api/friends/list', methods=['GET', 'OPTIONS'])
def get_friends_list():
    """Get list of accepted friends"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization token required'
            }), 401

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get accepted friends (both directions)
        cursor.execute('''
            SELECT DISTINCT
                CASE
                    WHEN f.sender_id = ? THEN f.receiver_id
                    ELSE f.sender_id
                END as friend_id,
                u.first_name, u.last_name, u.email, u.avatar_url, u.is_available_for_hire
            FROM friendships f
            JOIN users u ON (
                CASE
                    WHEN f.sender_id = ? THEN f.receiver_id = u.id
                    ELSE f.sender_id = u.id
                END
            )
            WHERE (f.sender_id = ? OR f.receiver_id = ?) AND f.status = 'accepted'
            ORDER BY u.first_name, u.last_name
        ''', (user_id, user_id, user_id, user_id))

        friends = []
        for row in cursor.fetchall():
            friends.append({
                'id': row[0],
                'first_name': row[1] or '',
                'last_name': row[2] or '',
                'email': row[3],
                'avatar_url': row[4] or '',
                'is_available_for_hire': bool(row[5])
            })

        conn.close()

        return jsonify({
            'success': True,
            'friends': friends,
            'count': len(friends)
        }), 200

    except Exception as e:
        print(f"Error getting friends list: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get friends list'
        }), 500

@app.route('/api/friends/suggestions', methods=['GET', 'OPTIONS'])
def get_friend_suggestions():
    """Get friend suggestions (users not already friends or requested)"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization token required'
            }), 401

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get users who are not already friends or have pending requests
        cursor.execute('''
            SELECT u.id, u.first_name, u.last_name, u.email, u.avatar_url, u.bio, u.location
            FROM users u
            WHERE u.id != ? AND u.is_active = 1
            AND u.id NOT IN (
                SELECT CASE
                    WHEN f.sender_id = ? THEN f.receiver_id
                    ELSE f.sender_id
                END
                FROM friendships f
                WHERE (f.sender_id = ? OR f.receiver_id = ?) AND f.status IN ('pending', 'accepted')
            )
            ORDER BY u.created_at DESC
            LIMIT 10
        ''', (user_id, user_id, user_id, user_id))

        suggestions = []
        for row in cursor.fetchall():
            suggestions.append({
                'id': row[0],
                'first_name': row[1] or '',
                'last_name': row[2] or '',
                'email': row[3],
                'avatar_url': row[4] or '',
                'bio': row[5] or '',
                'location': row[6] or ''
            })

        conn.close()

        return jsonify({
            'success': True,
            'suggestions': suggestions
        }), 200

    except Exception as e:
        print(f"Error getting friend suggestions: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get friend suggestions'
        }), 500

# ============================================
# JOBS ENDPOINTS
# ============================================

@app.route('/api/jobs', methods=['GET', 'OPTIONS'])
def get_jobs():
    """Get all job postings"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT j.*, u.first_name, u.last_name, u.email, u.avatar_url
            FROM jobs j
            LEFT JOIN users u ON j.user_id = u.id
            WHERE j.status = 'active'
            ORDER BY j.created_at DESC
        ''')

        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                'id': row['id'],
                'title': row['title'],
                'company': row['company'],
                'location': row['location'],
                'job_type': row['job_type'],
                'description': row['description'],
                'requirements': row['requirements'],
                'salary_range': row['salary_range'] or '',
                'created_at': row['created_at'],
                'user': {
                    'first_name': row['first_name'] or '',
                    'last_name': row['last_name'] or '',
                    'email': row['email'],
                    'avatar_url': row['avatar_url'] or ''
                }
            })

        conn.close()

        return jsonify({
            'success': True,
            'jobs': jobs
        }), 200

    except Exception as e:
        print(f"Error getting jobs: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get jobs'
        }), 500

@app.route('/api/jobs', methods=['POST', 'OPTIONS'])
def create_job():
    """Create a new job posting"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization token required'
            }), 401

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 401

        data = request.get_json()

        # Validate required fields
        if not all(k in data for k in ['title', 'company', 'location', 'job_type', 'description']):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO jobs (user_id, title, company, location, job_type, description, requirements, salary_range, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
        ''', (
            user_id,
            data['title'],
            data['company'],
            data['location'],
            data['job_type'],
            data['description'],
            data.get('requirements', ''),
            data.get('salary_range', ''),
            datetime.now(timezone.utc)
        ))

        job_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Job created successfully',
            'job_id': job_id
        }), 201

    except Exception as e:
        print(f"Error creating job: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to create job'
        }), 500

@app.route('/api/jobs/<int:job_id>', methods=['GET', 'OPTIONS'])
def get_job(job_id):
    """Get a specific job posting"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT j.*, u.first_name, u.last_name, u.email, u.avatar_url, u.phone
            FROM jobs j
            LEFT JOIN users u ON j.user_id = u.id
            WHERE j.id = ?
        ''', (job_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({
                'success': False,
                'message': 'Job not found'
            }), 404

        job = {
            'id': row['id'],
            'title': row['title'],
            'company': row['company'],
            'location': row['location'],
            'job_type': row['job_type'],
            'description': row['description'],
            'requirements': row['requirements'],
            'salary_range': row['salary_range'] or '',
            'status': row['status'],
            'created_at': row['created_at'],
            'user': {
                'first_name': row['first_name'] or '',
                'last_name': row['last_name'] or '',
                'email': row['email'],
                'phone': row['phone'] or '',
                'avatar_url': row['avatar_url'] or ''
            }
        }

        return jsonify({
            'success': True,
            'job': job
        }), 200

    except Exception as e:
        print(f"Error getting job: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get job'
        }), 500

if __name__ == '__main__':
    print("Starting HireMeBahamas backend server...")
    print("Server will be available at http://127.0.0.1:9999")

    # Windows-compatible configuration
    app.run(
        host='127.0.0.1',
        port=9999,
        threaded=True,
        use_reloader=False,
        debug=False
    )