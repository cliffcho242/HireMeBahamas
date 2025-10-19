import uvicorn

if __name__ == '__main__':
    print("Starting HireMeBahamas backend server with Uvicorn...")
    print("Server will be available at http://127.0.0.1:8008")
    print("Press Ctrl+C to stop the server")

    # Start the server with Uvicorn (ASGI server)
    uvicorn.run(
        "final_backend:app",
        host="127.0.0.1",
        port=8008,
        reload=False,
        log_level="info"
    )