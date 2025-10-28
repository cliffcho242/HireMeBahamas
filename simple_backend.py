import logging
import sys

from flask import Flask, jsonify
from flask_cors import CORS

# Simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


@app.route("/health")
def health():
    logger.info("Health check called")
    return {"status": "healthy", "message": "API running"}


@app.route("/")
def root():
    logger.info("Root called")
    return {"message": "HireBahamas API", "version": "1.0"}


if __name__ == "__main__":
    print("Starting Flask development server on http://127.0.0.1:8008")
    app.run(host="127.0.0.1", port=8008, debug=False, use_reloader=False)
