#!/usr/bin/env python3
"""
MINIMAL BACKEND TEST
"""

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/api/hireme/available")
def get_available_users():
    return jsonify({"success": True, "users": []})


@app.route("/api/hireme/toggle", methods=["POST"])
def toggle_availability():
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8009, debug=False, use_reloader=False)
