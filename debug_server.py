#!/usr/bin/env python3
"""
Simple server launcher for debugging
"""

import logging

from final_backend import app

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    print("Starting server...")
    app.run(host="127.0.0.1", port=9999, debug=True, use_reloader=False, threaded=True)
