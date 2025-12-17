#!/usr/bin/env python3
"""
Advanced AI API Endpoints for HireBahamas
REST API for 100x Enhanced AI Capabilities
"""

import asyncio
import base64
import io
import json
import logging
import time
import tracemalloc
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import Blueprint, Flask, jsonify, request
from flask_cors import CORS
from PIL import Image

from advanced_ai_orchestrator import AIConfig, get_ai_orchestrator, initialize_ai_system

# Enable tracemalloc to track memory allocations for debugging
tracemalloc.start()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Tracemalloc enabled for memory tracking")

# Create Flask app
app = Flask(__name__)
CORS(app)

# Create AI Blueprint
ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")

# Global AI Orchestrator
ai_orchestrator = None


def init_ai_orchestrator():
    """Initialize AI orchestrator"""
    global ai_orchestrator
    if ai_orchestrator is None:
        config = AIConfig()
        ai_orchestrator = initialize_ai_system(config)
    return ai_orchestrator


@ai_bp.route("/health", methods=["GET"])
def ai_health_check():
    """AI System Health Check"""
    try:
        orchestrator = init_ai_orchestrator()
        return jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "capabilities": [
                    "user_profile_analysis",
                    "job_matching",
                    "content_generation",
                    "resume_analysis",
                    "career_prediction",
                    "real_time_recommendations",
                ],
            }
        )
    except Exception as e:
        logger.error(f"AI health check error: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@ai_bp.route("/analyze-profile", methods=["POST"])
def analyze_user_profile():
    """Analyze user profile with advanced AI"""
    try:
        data = request.get_json()
        if not data or "user_data" not in data:
            return jsonify({"error": "user_data required"}), 400

        orchestrator = init_ai_orchestrator()

        # Run analysis using asyncio.run() for proper event loop management
        profile = asyncio.run(orchestrator.analyze_user_profile(data["user_data"]))

        return jsonify(
            {
                "success": True,
                "profile": {
                    "user_id": profile.user_id,
                    "skills": profile.skills,
                    "personality_traits": profile.personality_traits,
                    "career_goals": profile.career_goals,
                    "engagement_score": profile.engagement_score,
                    "network_strength": profile.network_strength,
                },
            }
        )

    except Exception as e:
        logger.error(f"Profile analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/job-matching", methods=["POST"])
def intelligent_job_matching():
    """Advanced AI-powered job matching"""
    try:
        data = request.get_json()
        if not data or "user_profile" not in data or "jobs" not in data:
            return jsonify({"error": "user_profile and jobs required"}), 400

        orchestrator = init_ai_orchestrator()

        # Create user profile object
        import numpy as np

        from advanced_ai_orchestrator import UserProfile

        user_data = data["user_profile"]
        profile = UserProfile(
            user_id=user_data["id"],
            skills=user_data.get("skills", []),
            experience=user_data.get("experience", {}),
            preferences=user_data.get("preferences", {}),
            behavior_patterns=user_data.get("behavior_patterns", {}),
            embeddings=np.array(user_data.get("embeddings", [])),
            personality_traits=user_data.get("personality_traits", {}),
            career_goals=user_data.get("career_goals", []),
            network_strength=user_data.get("network_strength", 0.5),
            engagement_score=user_data.get("engagement_score", 0.7),
        )

        # Run job matching using asyncio.run() for proper event loop management
        matches = asyncio.run(orchestrator.intelligent_job_matching(profile, data["jobs"]))

        return jsonify(
            {"success": True, "matches": matches, "total_matches": len(matches)}
        )

    except Exception as e:
        logger.error(f"Job matching error: {e}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/generate-content", methods=["POST"])
def generate_content():
    """AI-powered content generation"""
    try:
        data = request.get_json()
        if not data or "content_type" not in data or "context" not in data:
            return jsonify({"error": "content_type and context required"}), 400

        orchestrator = init_ai_orchestrator()

        # Use asyncio.run() for proper event loop management
        content = asyncio.run(orchestrator.generate_smart_content(
            data["content_type"], data["context"]
        ))

        return jsonify(
            {"success": True, "content": content, "content_type": data["content_type"]}
        )

    except Exception as e:
        logger.error(f"Content generation error: {e}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/analyze-resume", methods=["POST"])
def analyze_resume():
    """AI-powered resume analysis from image"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if not file.filename:
            return jsonify({"error": "No file selected"}), 400

        # Save uploaded file temporarily
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name

        try:
            orchestrator = init_ai_orchestrator()

            # Use asyncio.run() for proper event loop management
            analysis = asyncio.run(orchestrator.analyze_resume_image(temp_path))

            return jsonify({"success": True, "analysis": analysis})

        finally:
            # Clean up temp file
            os.unlink(temp_path)

    except Exception as e:
        logger.error(f"Resume analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/career-prediction", methods=["POST"])
def predict_career():
    """AI-powered career trajectory prediction"""
    try:
        data = request.get_json()
        if not data or "user_profile" not in data:
            return jsonify({"error": "user_profile required"}), 400

        orchestrator = init_ai_orchestrator()

        # Create user profile object
        import numpy as np

        from advanced_ai_orchestrator import UserProfile

        user_data = data["user_profile"]
        profile = UserProfile(
            user_id=user_data["id"],
            skills=user_data.get("skills", []),
            experience=user_data.get("experience", {}),
            preferences=user_data.get("preferences", {}),
            behavior_patterns=user_data.get("behavior_patterns", {}),
            embeddings=np.array(user_data.get("embeddings", [])),
            personality_traits=user_data.get("personality_traits", {}),
            career_goals=user_data.get("career_goals", []),
            network_strength=user_data.get("network_strength", 0.5),
            engagement_score=user_data.get("engagement_score", 0.7),
        )

        # Use asyncio.run() for proper event loop management
        prediction = asyncio.run(orchestrator.predict_career_trajectory(profile))

        return jsonify({"success": True, "prediction": prediction})

    except Exception as e:
        logger.error(f"Career prediction error: {e}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/recommendations", methods=["POST"])
def get_recommendations():
    """Real-time AI-powered recommendations"""
    try:
        data = request.get_json()
        if not data or "user_id" not in data:
            return jsonify({"error": "user_id required"}), 400

        orchestrator = init_ai_orchestrator()

        # Use asyncio.run() for proper event loop management
        recommendations = asyncio.run(orchestrator.real_time_recommendations(
            data["user_id"], data.get("context", {})
        ))

        return jsonify(
            {
                "success": True,
                "recommendations": recommendations,
                "count": len(recommendations),
            }
        )

    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/chat", methods=["POST"])
def ai_chat():
    """AI-powered conversational assistant"""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "message required"}), 400

        orchestrator = init_ai_orchestrator()

        # Use available AI service for chat
        message = data["message"]
        context = data.get("context", {})

        response_text = (
            "I'm sorry, but the AI chat service is not available at the moment."
        )

        # Try OpenAI first (Note: OpenAI client may need async wrapper)
        if orchestrator.openai_available:
            import openai

            # Wrap async OpenAI call with asyncio.run()
            async def get_openai_response():
                response = await openai.ChatCompletion.acreate(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are HireBot, an AI assistant for HireBahamas job platform. Help users with career advice, job searching, and professional development.",
                        },
                        {"role": "user", "content": message},
                    ],
                    temperature=0.7,
                    max_tokens=500,
                )
                return response.choices[0].message.content
            
            response_text = asyncio.run(get_openai_response())

        # Try Claude as fallback
        elif orchestrator.claude_available:
            response = orchestrator.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                system="You are HireBot, an AI assistant for HireBahamas job platform. Help users with career advice, job searching, and professional development.",
                messages=[{"role": "user", "content": message}],
            )
            response_text = response.content[0].text

        return jsonify(
            {
                "success": True,
                "response": response_text,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"AI chat error: {e}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/analytics", methods=["GET"])
def get_analytics():
    """Get AI system analytics"""
    try:
        orchestrator = init_ai_orchestrator()

        # Basic analytics (would be expanded in production)
        analytics = {
            "total_users_analyzed": len(orchestrator.user_cache),
            "total_jobs_processed": len(orchestrator.job_cache),
            "system_health": "excellent",
            "ai_services_status": {
                "openai": orchestrator.openai_available,
                "claude": orchestrator.claude_available,
                "gemini": orchestrator.gemini_available,
                "ocr": orchestrator.ocr_available,
            },
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify({"success": True, "analytics": analytics})

    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/feedback", methods=["POST"])
def submit_feedback():
    """Submit feedback for AI improvements"""
    try:
        data = request.get_json()
        if not data or "feedback" not in data:
            return jsonify({"error": "feedback required"}), 400

        # Store feedback for model improvement
        feedback_data = {
            "feedback": data["feedback"],
            "rating": data.get("rating"),
            "feature": data.get("feature"),
            "user_id": data.get("user_id"),
            "timestamp": datetime.now().isoformat(),
        }

        # In production, this would be stored in database
        logger.info(f"AI Feedback received: {feedback_data}")

        return jsonify(
            {
                "success": True,
                "message": "Thank you for your feedback! It will help improve our AI system.",
            }
        )

    except Exception as e:
        logger.error(f"Feedback submission error: {e}")
        return jsonify({"error": str(e)}), 500


# Register blueprint
app.register_blueprint(ai_bp)


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # Initialize AI system
    init_ai_orchestrator()

    logger.info("🚀 Advanced AI API Server starting...")
    app.run(host="0.0.0.0", port=8009, debug=True, threaded=True)
