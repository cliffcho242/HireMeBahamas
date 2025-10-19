from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "message": "HireMeBahamas API is running on port 5000"})

@app.route('/api/posts')
def posts():
    return jsonify({"success": True, "posts": [], "message": "Posts endpoint"})

if __name__ == '__main__':
    print("Starting HireMeBahamas backend server...")
    print("Server will be available at http://127.0.0.1:5000")

    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True,
        use_reloader=False,
        debug=False
    )