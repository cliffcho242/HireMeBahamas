import json
import os

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS to allow all origins
CORS(
    app,
    resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        }
    },
)

# In-memory data store
users = {
    "admin@hiremebahamas.com": {
        "email": "admin@hiremebahamas.com",
        "password": "AdminPass123!",
        "user_type": "admin",
        "first_name": "Admin",
        "last_name": "User",
    }
}

jobs = []
posts = []


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "message": "Backend is running"}), 200


@app.route("/api/auth/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if email in users and users[email]["password"] == password:
            return (
                jsonify(
                    {
                        "access_token": "demo_token_12345",
                        "user": {
                            "email": email,
                            "user_type": users[email]["user_type"],
                            "first_name": users[email]["first_name"],
                            "last_name": users[email]["last_name"],
                        },
                    }
                ),
                200,
            )

        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        user_type = data.get("user_type", "job_seeker")

        if email in users:
            return jsonify({"error": "User already exists"}), 400

        users[email] = {
            "email": email,
            "password": password,
            "user_type": user_type,
            "first_name": first_name,
            "last_name": last_name,
        }

        return (
            jsonify(
                {
                    "message": "User registered successfully",
                    "user": {
                        "email": email,
                        "user_type": user_type,
                        "first_name": first_name,
                        "last_name": last_name,
                    },
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/jobs", methods=["GET", "POST", "OPTIONS"])
def handle_jobs():
    if request.method == "OPTIONS":
        return "", 200

    if request.method == "GET":
        return jsonify(jobs), 200

    if request.method == "POST":
        try:
            data = request.get_json()
            job = {
                "id": len(jobs) + 1,
                "title": data.get("title"),
                "company": data.get("company"),
                "location": data.get("location"),
                "description": data.get("description"),
                "salary": data.get("salary", "Negotiable"),
                "posted_at": "2025-10-19",
            }
            jobs.append(job)
            return jsonify(job), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/api/posts", methods=["GET", "POST", "OPTIONS"])
def handle_posts():
    if request.method == "OPTIONS":
        return "", 200

    if request.method == "GET":
        return jsonify(posts), 200

    if request.method == "POST":
        try:
            data = request.get_json()
            post = {
                "id": len(posts) + 1,
                "content": data.get("content"),
                "image_url": data.get("image_url"),
                "created_at": "2025-10-19",
                "user": {
                    "id": 1,
                    "first_name": "Admin",
                    "last_name": "User",
                    "email": "admin@hiremebahamas.com",
                },
                "likes_count": 0,
                "is_liked": False,
            }
            posts.append(post)
            return jsonify(post), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500


# Vercel handler
def handler(request, response):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
