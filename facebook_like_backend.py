#!/usr/bin/env python3
"""
HireBahamas Facebook-Like Platform with AI User Pattern Analytics
Advanced social media platform with intelligent user behavior tracking
Enhanced with AI System Monitor for auto-healing and error prevention
"""

import hashlib
import json
import logging
import os
import secrets
import sqlite3
import sys
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional

# Security and Performance
import bcrypt
import joblib
import jwt
import numpy as np

# AI and Analytics imports
import pandas as pd

# Core Flask imports
from flask import Flask, jsonify, request, session
from flask_caching import Cache
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit, join_room, leave_room
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# AI System Monitor Integration
try:
    from ai_system_monitor import get_system_health, start_ai_monitor

    AI_MONITOR_AVAILABLE = True
except ImportError:
    AI_MONITOR_AVAILABLE = False
    print("AI System Monitor not available - running without advanced monitoring")


class AIUserAnalytics:
    """Advanced AI system for user behavior pattern analysis"""

    def __init__(self):
        self.user_interactions = defaultdict(list)
        self.user_preferences = defaultdict(dict)
        self.content_engagement = defaultdict(dict)
        self.user_clusters = {}
        self.scaler = StandardScaler()
        self.engagement_model = RandomForestClassifier(n_estimators=100)
        self.model_trained = False

    def track_user_interaction(
        self,
        user_id: str,
        action: str,
        content_id: str = None,
        duration: float = 0,
        metadata: dict = None,
    ):
        """Track user interactions for pattern analysis"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "content_id": content_id,
            "duration": duration,
            "metadata": metadata or {},
        }

        self.user_interactions[user_id].append(interaction)

        # Keep only last 1000 interactions per user for performance
        if len(self.user_interactions[user_id]) > 1000:
            self.user_interactions[user_id] = self.user_interactions[user_id][-1000:]

    def analyze_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze individual user behavior patterns"""
        interactions = self.user_interactions.get(user_id, [])

        if not interactions:
            return {"status": "insufficient_data"}

        # Convert to DataFrame for analysis
        df = pd.DataFrame(interactions)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Calculate behavior metrics
        patterns = {
            "total_interactions": len(interactions),
            "most_active_hour": (
                df["timestamp"].dt.hour.mode().iloc[0] if not df.empty else 0
            ),
            "avg_session_duration": df["duration"].mean(),
            "preferred_actions": df["action"].value_counts().to_dict(),
            "activity_trend": self._calculate_activity_trend(df),
            "engagement_score": self._calculate_engagement_score(df),
            "user_type": self._classify_user_type(df),
        }

        return patterns

    def _calculate_activity_trend(self, df: pd.DataFrame) -> str:
        """Calculate if user activity is increasing, decreasing, or stable"""
        if len(df) < 7:
            return "insufficient_data"

        # Group by day and count interactions
        daily_activity = df.groupby(df["timestamp"].dt.date).size()

        # Simple trend analysis
        recent_avg = daily_activity.tail(3).mean()
        older_avg = daily_activity.head(3).mean()

        if recent_avg > older_avg * 1.2:
            return "increasing"
        elif recent_avg < older_avg * 0.8:
            return "decreasing"
        else:
            return "stable"

    def _calculate_engagement_score(self, df: pd.DataFrame) -> float:
        """Calculate user engagement score (0-100)"""
        if df.empty:
            return 0.0

        # Weighted scoring based on different factors
        action_weights = {
            "post_created": 5,
            "comment_added": 3,
            "like_given": 1,
            "profile_viewed": 2,
            "message_sent": 4,
            "share": 3,
        }

        total_score = 0
        for _, row in df.iterrows():
            action = row["action"]
            duration = row["duration"]
            base_score = action_weights.get(action, 1)

            # Bonus for longer engagement
            duration_bonus = min(duration / 60, 2)  # Max 2x bonus for 1+ minute
            total_score += base_score * (1 + duration_bonus)

        # Normalize to 0-100 scale
        max_possible = len(df) * 10  # Theoretical maximum
        engagement_score = (
            min((total_score / max_possible) * 100, 100) if max_possible > 0 else 0
        )

        return round(engagement_score, 2)

    def _classify_user_type(self, df: pd.DataFrame) -> str:
        """Classify user type based on behavior patterns"""
        if df.empty:
            return "new_user"

        action_counts = df["action"].value_counts()
        total_actions = len(df)

        # Define user types based on behavior
        if action_counts.get("post_created", 0) / total_actions > 0.3:
            return "content_creator"
        elif action_counts.get("comment_added", 0) / total_actions > 0.4:
            return "active_commenter"
        elif action_counts.get("like_given", 0) / total_actions > 0.6:
            return "passive_consumer"
        elif action_counts.get("message_sent", 0) / total_actions > 0.5:
            return "social_connector"
        else:
            return "casual_user"

    def get_content_recommendations(self, user_id: str, limit: int = 10) -> List[Dict]:
        """AI-powered content recommendations based on user patterns"""
        user_patterns = self.analyze_user_patterns(user_id)

        if user_patterns.get("status") == "insufficient_data":
            return self._get_trending_content(limit)

        # Get similar users for collaborative filtering
        similar_users = self._find_similar_users(user_id)

        # Generate recommendations based on user type and preferences
        recommendations = []
        user_type = user_patterns.get("user_type", "casual_user")

        if user_type == "content_creator":
            recommendations.extend(
                self._get_creator_recommendations(user_id, limit // 2)
            )
        elif user_type == "active_commenter":
            recommendations.extend(
                self._get_discussion_recommendations(user_id, limit // 2)
            )
        elif user_type == "social_connector":
            recommendations.extend(
                self._get_social_recommendations(user_id, limit // 2)
            )

        # Fill remaining slots with trending content
        remaining = limit - len(recommendations)
        if remaining > 0:
            recommendations.extend(self._get_trending_content(remaining))

        return recommendations[:limit]

    def _find_similar_users(self, user_id: str, limit: int = 5) -> List[str]:
        """Find users with similar behavior patterns"""
        target_patterns = self.analyze_user_patterns(user_id)
        if target_patterns.get("status") == "insufficient_data":
            return []

        similar_users = []
        target_score = target_patterns.get("engagement_score", 0)
        target_type = target_patterns.get("user_type", "")

        for uid in self.user_interactions.keys():
            if uid == user_id:
                continue

            user_patterns = self.analyze_user_patterns(uid)
            if user_patterns.get("status") == "insufficient_data":
                continue

            # Calculate similarity score
            score_diff = abs(user_patterns.get("engagement_score", 0) - target_score)
            type_match = user_patterns.get("user_type", "") == target_type

            similarity = (100 - score_diff) * (1.5 if type_match else 1.0)
            similar_users.append((uid, similarity))

        # Sort by similarity and return top matches
        similar_users.sort(key=lambda x: x[1], reverse=True)
        return [uid for uid, _ in similar_users[:limit]]

    def _get_trending_content(self, limit: int) -> List[Dict]:
        """Get trending content (placeholder - would fetch from database)"""
        return [
            {
                "type": "trending",
                "title": f"Trending Post {i+1}",
                "engagement_score": 95 - i * 2,
                "category": "general",
            }
            for i in range(limit)
        ]

    def _get_creator_recommendations(self, user_id: str, limit: int) -> List[Dict]:
        """Get recommendations for content creators"""
        return [
            {
                "type": "creator_tool",
                "title": "Advanced Content Analytics",
                "description": "See how your content performs",
                "category": "tools",
            },
            {
                "type": "inspiration",
                "title": "Trending Topics in Your Field",
                "description": "Popular topics to create content about",
                "category": "inspiration",
            },
        ][:limit]

    def _get_discussion_recommendations(self, user_id: str, limit: int) -> List[Dict]:
        """Get recommendations for active commenters"""
        return [
            {
                "type": "discussion",
                "title": "Hot Debate: Tech Trends 2025",
                "comments_count": 45,
                "category": "discussion",
            },
            {
                "type": "discussion",
                "title": "Community Q&A Session",
                "comments_count": 32,
                "category": "community",
            },
        ][:limit]

    def _get_social_recommendations(self, user_id: str, limit: int) -> List[Dict]:
        """Get recommendations for social connectors"""
        return [
            {
                "type": "social",
                "title": "People You May Know",
                "description": "Connect with professionals in your field",
                "category": "networking",
            },
            {
                "type": "event",
                "title": "Virtual Networking Event",
                "description": "Join live networking sessions",
                "category": "events",
            },
        ][:limit]


class FacebookLikePlatform:
    """Main platform class with Facebook-like features"""

    def __init__(self):
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = secrets.token_hex(32)
        self.app.config["CACHE_TYPE"] = "simple"

        # Initialize extensions
        CORS(self.app, origins=["http://localhost:3000", "http://localhost:3001"])
        self.cache = Cache(self.app)
        self.socketio = SocketIO(
            self.app, cors_allowed_origins="*", async_mode="threading"
        )

        # Rate limiting
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
        )

        # AI Analytics
        self.ai_analytics = AIUserAnalytics()

        # AI System Monitor
        self.ai_monitor = None
        if AI_MONITOR_AVAILABLE:
            try:
                self.ai_monitor = start_ai_monitor()
                print("🤖 AI System Monitor activated")
            except Exception as e:
                print(f"AI Monitor failed to start: {e}")

        # Database
        self.db_path = Path("backend/hirebahamas.db")
        self.init_database()

        # Setup routes
        self.setup_routes()
        self.setup_socket_events()

        # Real-time data
        self.active_users = set()
        self.user_rooms = defaultdict(set)

    def init_database(self):
        """Initialize database with Facebook-like schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Enhanced users table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                profile_picture TEXT DEFAULT '',
                cover_photo TEXT DEFAULT '',
                bio TEXT DEFAULT '',
                location TEXT DEFAULT '',
                website TEXT DEFAULT '',
                birth_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_verified BOOLEAN DEFAULT FALSE,
                followers_count INTEGER DEFAULT 0,
                following_count INTEGER DEFAULT 0,
                posts_count INTEGER DEFAULT 0
            )
        """
        )

        # Posts table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                image_url TEXT DEFAULT '',
                video_url TEXT DEFAULT '',
                post_type TEXT DEFAULT 'text',
                privacy_level TEXT DEFAULT 'public',
                likes_count INTEGER DEFAULT 0,
                comments_count INTEGER DEFAULT 0,
                shares_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """
        )

        # Comments table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                parent_comment_id INTEGER DEFAULT NULL,
                likes_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (parent_comment_id) REFERENCES comments (id) ON DELETE CASCADE
            )
        """
        )

        # Likes table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                post_id INTEGER DEFAULT NULL,
                comment_id INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                FOREIGN KEY (comment_id) REFERENCES comments (id) ON DELETE CASCADE,
                UNIQUE(user_id, post_id),
                UNIQUE(user_id, comment_id)
            )
        """
        )

        # Friendships/Follows table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS friendships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                follower_id INTEGER NOT NULL,
                following_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (follower_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (following_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(follower_id, following_id)
            )
        """
        )

        # Messages table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (receiver_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """
        )

        # User interactions for AI (separate from main tables for performance)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id INTEGER NOT NULL,
                duration REAL DEFAULT 0,
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """
        )

        conn.commit()
        conn.close()

        # Create admin user if not exists
        self.create_admin_user()

    def create_admin_user(self):
        """Create default admin user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE email = ?", ("admin@hirebahamas.com",)
        )
        if not cursor.fetchone():
            password_hash = bcrypt.hashpw(
                "AdminPass123!".encode("utf-8"), bcrypt.gensalt()
            )
            cursor.execute(
                """
                INSERT INTO users (email, password_hash, username, full_name, bio)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    "admin@hirebahamas.com",
                    password_hash.decode("utf-8"),
                    "admin",
                    "Platform Administrator",
                    "Welcome to HireBahamas - Your AI-Powered Social Platform! 🚀",
                ),
            )
            conn.commit()

        conn.close()

    def setup_routes(self):
        """Setup all API routes"""

        @self.app.route("/health", methods=["GET"])
        def health_check():
            return jsonify(
                {
                    "status": "healthy",
                    "message": "HireBahamas Facebook-Like Platform is running",
                    "database": str(self.db_path.exists()),
                    "ai_analytics": "active",
                    "ai_monitor": "active" if self.ai_monitor else "disabled",
                    "features": [
                        "posts",
                        "comments",
                        "likes",
                        "messaging",
                        "ai_recommendations",
                    ],
                }
            )

        @self.app.route("/api/system/health", methods=["GET"])
        def system_health():
            """Enhanced health check with AI monitoring data"""
            if AI_MONITOR_AVAILABLE and self.ai_monitor:
                try:
                    health_data = get_system_health()
                    return jsonify(health_data)
                except Exception as e:
                    return jsonify({"error": f"Health check failed: {str(e)}"}), 500
            else:
                return jsonify(
                    {
                        "status": "basic",
                        "message": "AI monitoring not available",
                        "backend": True,
                        "database": self.db_path.exists(),
                    }
                )

        @self.app.route("/api/system/monitor/status", methods=["GET"])
        def monitor_status():
            """Get AI monitor status and statistics"""
            if not AI_MONITOR_AVAILABLE or not self.ai_monitor:
                return jsonify({"error": "AI Monitor not available"}), 503

            try:
                status = {
                    "monitor_active": True,
                    "auto_fix_enabled": self.ai_monitor.auto_fix_enabled,
                    "ai_learning_enabled": self.ai_monitor.ai_learning_enabled,
                    "error_patterns": len(self.ai_monitor.error_patterns),
                    "fix_success_rates": self.ai_monitor.fix_success_rate,
                    "performance_history_length": len(
                        self.ai_monitor.performance_history
                    ),
                    "last_check": (
                        self.ai_monitor.health.last_check.isoformat()
                        if self.ai_monitor.health.last_check
                        else None
                    ),
                }
                return jsonify(status)
            except Exception as e:
                return jsonify({"error": f"Monitor status failed: {str(e)}"}), 500

        @self.app.route("/api/system/monitor/toggle", methods=["POST"])
        def toggle_monitor_features():
            """Toggle AI monitor features"""
            if not AI_MONITOR_AVAILABLE or not self.ai_monitor:
                return jsonify({"error": "AI Monitor not available"}), 503

            data = request.get_json()
            if "auto_fix" in data:
                self.ai_monitor.auto_fix_enabled = bool(data["auto_fix"])
            if "ai_learning" in data:
                self.ai_monitor.ai_learning_enabled = bool(data["ai_learning"])

            return jsonify(
                {
                    "auto_fix_enabled": self.ai_monitor.auto_fix_enabled,
                    "ai_learning_enabled": self.ai_monitor.ai_learning_enabled,
                }
            )

        @self.app.route("/api/auth/login", methods=["POST"])
        @self.limiter.limit("5 per minute")
        def login():
            try:
                data = request.get_json()
                email = data.get("email")
                password = data.get("password")

                if not email or not password:
                    # Log failed attempt to AI monitor
                    if self.ai_monitor:
                        self.ai_monitor.record_error_pattern(
                            "login_missing_credentials", datetime.now()
                        )
                    return jsonify({"error": "Email and password required"}), 400

                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, password_hash, username, full_name 
                    FROM users WHERE email = ?
                """,
                    (email,),
                )

                user = cursor.fetchone()
                conn.close()

                if user and bcrypt.checkpw(
                    password.encode("utf-8"), user[1].encode("utf-8")
                ):
                    # Track successful login
                    self.ai_analytics.track_user_interaction(
                        str(user[0]),
                        "login",
                        duration=0,
                        metadata={"timestamp": datetime.now().isoformat()},
                    )

                    # Log successful login to AI monitor
                    if self.ai_monitor:
                        self.ai_monitor.record_error_pattern(
                            "login_success", datetime.now()
                        )

                    # Generate JWT token
                    token = jwt.encode(
                        {
                            "user_id": user[0],
                            "username": user[2],
                            "exp": datetime.utcnow() + timedelta(days=30),
                        },
                        self.app.config["SECRET_KEY"],
                    )

                    return jsonify(
                        {
                            "token": token,
                            "user": {
                                "id": user[0],
                                "username": user[2],
                                "full_name": user[3],
                                "email": email,
                            },
                        }
                    )
                else:
                    # Log failed credentials to AI monitor
                    if self.ai_monitor:
                        self.ai_monitor.record_error_pattern(
                            "login_invalid_credentials", datetime.now()
                        )
                    return jsonify({"error": "Invalid credentials"}), 401

            except sqlite3.Error as e:
                # Database error - critical for AI monitor
                if self.ai_monitor:
                    self.ai_monitor.record_error_pattern(
                        "login_database_error", datetime.now()
                    )
                return jsonify({"error": "Database error during login"}), 500

            except Exception as e:
                # General error - log to AI monitor
                if self.ai_monitor:
                    self.ai_monitor.record_error_pattern(
                        "login_general_error", datetime.now()
                    )
                return jsonify({"error": "Login system error"}), 500

        @self.app.route("/api/posts", methods=["GET"])
        def get_posts():
            """Get posts with AI-powered recommendations"""
            user_id = self.get_current_user_id()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get regular posts
            cursor.execute(
                """
                SELECT p.id, p.content, p.image_url, p.post_type, p.likes_count, 
                       p.comments_count, p.shares_count, p.created_at,
                       u.username, u.full_name, u.profile_picture
                FROM posts p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.created_at DESC
                LIMIT 20
            """
            )

            posts = []
            for row in cursor.fetchall():
                posts.append(
                    {
                        "id": row[0],
                        "content": row[1],
                        "image_url": row[2],
                        "post_type": row[3],
                        "likes_count": row[4],
                        "comments_count": row[5],
                        "shares_count": row[6],
                        "created_at": row[7],
                        "author": {
                            "username": row[8],
                            "full_name": row[9],
                            "profile_picture": row[10],
                        },
                    }
                )

            conn.close()

            # Add AI recommendations if user is logged in
            recommendations = []
            if user_id:
                recommendations = self.ai_analytics.get_content_recommendations(
                    str(user_id)
                )

                # Track feed view interaction
                self.ai_analytics.track_user_interaction(
                    str(user_id),
                    "feed_viewed",
                    duration=0,
                    metadata={"posts_count": len(posts)},
                )

            return jsonify(
                {
                    "posts": posts,
                    "recommendations": recommendations,
                    "ai_insights": (
                        self.ai_analytics.analyze_user_patterns(str(user_id))
                        if user_id
                        else None
                    ),
                }
            )

        @self.app.route("/api/posts", methods=["POST"])
        def create_post():
            """Create a new post"""
            user_id = self.get_current_user_id()
            if not user_id:
                return jsonify({"error": "Authentication required"}), 401

            data = request.get_json()
            content = data.get("content")
            image_url = data.get("image_url", "")
            post_type = data.get("post_type", "text")

            if not content:
                return jsonify({"error": "Content is required"}), 400

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO posts (user_id, content, image_url, post_type)
                VALUES (?, ?, ?, ?)
            """,
                (user_id, content, image_url, post_type),
            )

            post_id = cursor.lastrowid

            # Update user's post count
            cursor.execute(
                """
                UPDATE users SET posts_count = posts_count + 1 
                WHERE id = ?
            """,
                (user_id,),
            )

            conn.commit()
            conn.close()

            # Track post creation
            self.ai_analytics.track_user_interaction(
                str(user_id),
                "post_created",
                str(post_id),
                duration=len(content) / 10,  # Estimate writing time
                metadata={"post_type": post_type, "content_length": len(content)},
            )

            # Emit real-time update
            self.socketio.emit(
                "new_post",
                {
                    "post_id": post_id,
                    "user_id": user_id,
                    "content": content[:100] + "..." if len(content) > 100 else content,
                },
                broadcast=True,
            )

            return jsonify({"post_id": post_id, "message": "Post created successfully"})

        @self.app.route("/api/posts/<int:post_id>/like", methods=["POST"])
        def like_post(post_id):
            """Like/unlike a post"""
            user_id = self.get_current_user_id()
            if not user_id:
                return jsonify({"error": "Authentication required"}), 401

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if already liked
            cursor.execute(
                """
                SELECT id FROM likes WHERE user_id = ? AND post_id = ?
            """,
                (user_id, post_id),
            )

            existing_like = cursor.fetchone()

            if existing_like:
                # Unlike
                cursor.execute(
                    """
                    DELETE FROM likes WHERE user_id = ? AND post_id = ?
                """,
                    (user_id, post_id),
                )

                cursor.execute(
                    """
                    UPDATE posts SET likes_count = likes_count - 1 WHERE id = ?
                """,
                    (post_id,),
                )

                action = "unlike"
            else:
                # Like
                cursor.execute(
                    """
                    INSERT INTO likes (user_id, post_id) VALUES (?, ?)
                """,
                    (user_id, post_id),
                )

                cursor.execute(
                    """
                    UPDATE posts SET likes_count = likes_count + 1 WHERE id = ?
                """,
                    (post_id,),
                )

                action = "like"

            conn.commit()
            conn.close()

            # Track interaction
            self.ai_analytics.track_user_interaction(
                str(user_id),
                "like_given" if action == "like" else "like_removed",
                str(post_id),
                duration=1,
            )

            return jsonify(
                {"action": action, "message": f"Post {action}d successfully"}
            )

        @self.app.route("/api/user/analytics", methods=["GET"])
        def get_user_analytics():
            """Get AI-powered user analytics"""
            user_id = self.get_current_user_id()
            if not user_id:
                return jsonify({"error": "Authentication required"}), 401

            patterns = self.ai_analytics.analyze_user_patterns(str(user_id))
            recommendations = self.ai_analytics.get_content_recommendations(
                str(user_id)
            )

            return jsonify(
                {
                    "user_patterns": patterns,
                    "recommendations": recommendations,
                    "analytics_summary": {
                        "total_interactions": len(
                            self.ai_analytics.user_interactions.get(str(user_id), [])
                        ),
                        "last_analysis": datetime.now().isoformat(),
                    },
                }
            )

    def setup_socket_events(self):
        """Setup Socket.IO events for real-time features"""

        @self.socketio.on("connect")
        def handle_connect():
            user_id = self.get_current_user_id()
            if user_id:
                self.active_users.add(user_id)
                join_room(f"user_{user_id}")

                # Track connection
                self.ai_analytics.track_user_interaction(
                    str(user_id), "connected", duration=0
                )

                emit("connected", {"message": "Connected to HireBahamas"})

        @self.socketio.on("disconnect")
        def handle_disconnect():
            user_id = self.get_current_user_id()
            if user_id:
                self.active_users.discard(user_id)
                leave_room(f"user_{user_id}")

                # Track disconnection
                self.ai_analytics.track_user_interaction(
                    str(user_id), "disconnected", duration=0
                )

        @self.socketio.on("typing")
        def handle_typing(data):
            user_id = self.get_current_user_id()
            if user_id:
                emit(
                    "user_typing",
                    {"user_id": user_id},
                    broadcast=True,
                    include_self=False,
                )

    def get_current_user_id(self):
        """Get current user ID from JWT token"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(
                token, self.app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            return payload["user_id"]
        except jwt.InvalidTokenError:
            return None

    def run(self, host="127.0.0.1", port=8008, debug=False):
        """Run the platform"""
        print(f"🚀 Starting HireBahamas Facebook-Like Platform...")
        print(f"🤖 AI Analytics: ACTIVE")
        print(f"🌐 Server: http://{host}:{port}")
        print(f"📊 Real-time Features: ENABLED")
        print(f"🔒 Security: JWT + Rate Limiting")

        self.socketio.run(self.app, host=host, port=port, debug=debug)


if __name__ == "__main__":
    platform = FacebookLikePlatform()
    platform.run(debug=True)
