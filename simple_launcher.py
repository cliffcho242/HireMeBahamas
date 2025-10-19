#!/usr/bin/env python3
"""
Simple launcher for HireMeBahamas backend
"""

from waitress import serve
from final_backend import app

if __name__ == '__main__':
    print("Starting HireMeBahamas with Waitress...")
    serve(app, host='127.0.0.1', port=9999, threads=4)