from waitress import serve
from final_backend import app

if __name__ == '__main__':
    print("Starting HireMeBahamas backend server with Waitress...")
    print("Server will be available at http://127.0.0.1:8008")
    print("Press Ctrl+C to stop the server")

    # Start the server with Waitress (production WSGI server)
    serve(app, host='127.0.0.1', port=8008, threads=4)