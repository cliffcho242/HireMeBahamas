from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import sys
import traceback

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('minimal_backend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health():
    logger.info("Health endpoint called")
    try:
        return jsonify({
            "status": "healthy", 
            "message": "HireBahamas API is running",
            "timestamp": "2025-09-29"
        })
    except Exception as e:
        logger.error(f"Health endpoint error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/')
def root():
    logger.info("Root endpoint called")
    try:
        return jsonify({
            "message": "Welcome to HireBahamas API",
            "version": "1.0.0",
            "health": "/health"
        })
    except Exception as e:
        logger.error(f"Root endpoint error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {error}")
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    logger.info("Starting minimal Flask backend...")
    logger.info("Server will be available at http://127.0.0.1:8006")
    try:
        from waitress import serve
        serve(app, host='127.0.0.1', port=8006)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)