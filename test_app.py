#!/usr/bin/env python3
"""
Minimal Flask app for Railway deployment testing
"""

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello from Railway!"


@app.route("/health")
def health():
    return "OK"


if __name__ == "__main__":
    app.run(debug=True)
