import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
import bcrypt
import jwt

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hirebahamas.db")
SECRET_KEY = "your-very-secret-and-secure-key" 

# --- Flask App Initialization ---
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-User-Id"],
)

# --- Utility Functions ---
def get_user_id_from_token():
    """Helper to decode user ID from Authorization token."""
    try:
        token = request.headers.get("Authorization").split(" ")[1]
        payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        return payload.get("user_id")
    except (IndexError, AttributeError, jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

# --- Database Initialization ---
def init_database():
    """Initializes the database and creates all necessary tables."""
    print("Initializing database...")
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
            first_name TEXT, last_name TEXT, user_type TEXT, is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Users table checked/created.")

    # Create conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participant_1_id INTEGER NOT NULL,
            participant_2_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (participant_1_id) REFERENCES users (id),
            FOREIGN KEY (participant_2_id) REFERENCES users (id)
        )
    """)
    print("Conversations table checked/created.")

    # Create messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id),
            FOREIGN KEY (sender_id) REFERENCES users (id)
        )
    """)
    print("Messages table checked/created.")

    # Check for admin user
    cursor.execute("SELECT * FROM users WHERE email = ?", ("admin@hiremebahamas.com",))
    if not cursor.fetchone():
        print("Creating admin user...")
        password = "AdminPass123!"
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO users (email, password_hash, first_name, last_name, user_type, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("admin@hiremebahamas.com", hashed_password.decode("utf-8"), "Admin", "User", "admin", True)
        )
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")

    conn.commit()
    conn.close()
    print("Database initialization complete.")

# --- API Endpoints (Auth) ---
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        if not data or not data.get("email") or not data.get("password"):
            return jsonify({"message": "Email and password are required"}), 400
        email, password = data["email"].lower().strip(), data["password"]
        conn = sqlite3.connect(str(DB_PATH)); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,)); user_data = cursor.fetchone(); conn.close()
        if not user_data: return jsonify({"message": "Invalid credentials"}), 401
        user = dict(user_data)
        if not user.get("is_active"): return jsonify({"message": "Account is not active"}), 401
        if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")): return jsonify({"message": "Invalid credentials"}), 401
        token = jwt.encode({"user_id": user["id"], "email": user["email"], "exp": datetime.utcnow() + timedelta(days=30)}, app.config["SECRET_KEY"], algorithm="HS256")
        return jsonify({"access_token": token, "user": {"id": user["id"], "email": user["email"], "first_name": user["first_name"], "last_name": user["last_name"], "user_type": user["user_type"]}, "message": "Login successful"}), 200
    except Exception as e:
        print(f"[Login Error] {e}"); return jsonify({"message": "Internal server error"}), 500

@app.route("/api/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        required = ["email", "password", "first_name", "last_name", "user_type"]
        if not data or not all(field in data for field in required): return jsonify({"message": "Missing required fields"}), 400
        email = data["email"].lower().strip()
        conn = sqlite3.connect(str(DB_PATH)); cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,)); 
        if cursor.fetchone(): conn.close(); return jsonify({"message": "An account with this email already exists"}), 409
        hashed_password = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cursor.execute("INSERT INTO users (email, password_hash, first_name, last_name, user_type) VALUES (?, ?, ?, ?, ?)", (email, hashed_password, data["first_name"], data["last_name"], data["user_type"])); user_id = cursor.lastrowid; conn.commit(); conn.close()
        token = jwt.encode({"user_id": user_id, "email": email, "exp": datetime.utcnow() + timedelta(days=30)}, app.config["SECRET_KEY"], algorithm="HS256")
        return jsonify({"access_token": token, "user": {"id": user_id, "email": email, "first_name": data["first_name"], "last_name": data["last_name"], "user_type": data["user_type"]}, "message": "Registration successful"}), 201
    except Exception as e:
        print(f"[Registration Error] {e}"); return jsonify({"message": "Could not process your request"}), 500

# --- API Endpoints (Messaging) ---
@app.route("/api/messages/conversations", methods=["GET"])
def get_conversations():
    """Fetches all conversations for the logged-in user."""
    user_id = get_user_id_from_token()
    if not user_id: return jsonify({"message": "Authentication required"}), 401
    
    try:
        conn = sqlite3.connect(str(DB_PATH)); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
        query = """
            SELECT c.id, c.participant_1_id, c.participant_2_id,
                   p1.first_name as p1_first, p1.last_name as p1_last,
                   p2.first_name as p2_first, p2.last_name as p2_last,
                   (SELECT content FROM messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message_content,
                   (SELECT created_at FROM messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message_time
            FROM conversations c
            JOIN users p1 ON c.participant_1_id = p1.id
            JOIN users p2 ON c.participant_2_id = p2.id
            WHERE c.participant_1_id = ? OR c.participant_2_id = ?
            ORDER BY c.updated_at DESC
        """
        cursor.execute(query, (user_id, user_id)); rows = cursor.fetchall(); conn.close()
        
        conversations = []
        for row in rows:
            other_participant = dict(row['p2']) if row['participant_1_id'] == user_id else dict(row['p1'])
            conversations.append({
                "id": row["id"],
                "other_participant": {
                    "id": row['participant_2_id'] if row['participant_1_id'] == user_id else row['participant_1_id'],
                    "first_name": row['p2_first'] if row['participant_1_id'] == user_id else row['p1_first'],
                    "last_name": row['p2_last'] if row['participant_1_id'] == user_id else row['p1_last'],
                },
                "last_message": {
                    "content": row["last_message_content"],
                    "created_at": row["last_message_time"],
                }
            })
        return jsonify(conversations), 200
    except Exception as e:
        print(f"[Conversations Error] {e}"); return jsonify({"message": "Could not fetch conversations"}), 500

@app.route("/api/messages/<int:conversation_id>", methods=["GET"])
def get_messages(conversation_id):
    """Fetches all messages for a specific conversation."""
    user_id = get_user_id_from_token()
    if not user_id: return jsonify({"message": "Authentication required"}), 401

    try:
        conn = sqlite3.connect(str(DB_PATH)); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
        # Verify user is part of the conversation
        cursor.execute("SELECT id FROM conversations WHERE id = ? AND (participant_1_id = ? OR participant_2_id = ?)", (conversation_id, user_id, user_id))
        if not cursor.fetchone(): conn.close(); return jsonify({"message": "Not authorized"}), 403
        
        query = """
            SELECT m.id, m.sender_id, m.content, m.created_at, u.first_name, u.last_name
            FROM messages m JOIN users u ON m.sender_id = u.id
            WHERE m.conversation_id = ? ORDER BY m.created_at ASC
        """
        cursor.execute(query, (conversation_id,)); rows = cursor.fetchall(); conn.close()

        messages = [{"id": row["id"], "sender_id": row["sender_id"], "content": row["content"], "created_at": row["created_at"], "sender": {"first_name": row["first_name"], "last_name": row["last_name"]}} for row in rows]
        return jsonify(messages), 200
    except Exception as e:
        print(f"[Messages Error] {e}"); return jsonify({"message": "Could not fetch messages"}), 500

@app.route("/api/messages", methods=["POST"])
def send_message():
    """Sends a new message to a conversation."""
    user_id = get_user_id_from_token()
    if not user_id: return jsonify({"message": "Authentication required"}), 401

    try:
        data = request.get_json()
        if not data or "conversation_id" not in data or "content" not in data:
            return jsonify({"message": "conversation_id and content are required"}), 400
        
        conversation_id, content = data["conversation_id"], data["content"]

        conn = sqlite3.connect(str(DB_PATH)); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
        # Verify user is part of the conversation
        cursor.execute("SELECT id FROM conversations WHERE id = ? AND (participant_1_id = ? OR participant_2_id = ?)", (conversation_id, user_id, user_id))
        if not cursor.fetchone(): conn.close(); return jsonify({"message": "Not authorized"}), 403

        # Insert message and update conversation timestamp
        now = datetime.utcnow()
        cursor.execute("INSERT INTO messages (conversation_id, sender_id, content, created_at) VALUES (?, ?, ?, ?)", (conversation_id, user_id, content, now))
        new_message_id = cursor.lastrowid
        cursor.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conversation_id))
        conn.commit()

        cursor.execute("SELECT first_name, last_name FROM users WHERE id = ?", (user_id,))
        sender_info = cursor.fetchone()
        conn.close()

        # The new message object to be returned
        new_message = {
            "id": new_message_id, "conversation_id": conversation_id, "sender_id": user_id,
            "content": content, "created_at": now.isoformat(),
            "sender": {"first_name": sender_info["first_name"], "last_name": sender_info["last_name"]}
        }
        return jsonify(new_message), 201
    except Exception as e:
        print(f"[Send Message Error] {e}"); return jsonify({"message": "Could not send message"}), 500

# --- Main Execution ---
if __name__ == "__main__":
    init_database()
    print("Starting Flask server on http://0.0.0.0:10000")
    # Use a production-ready server like Gunicorn/Waitress instead of app.run for production
    app.run(host="0.0.0.0", port=10000, debug=True)