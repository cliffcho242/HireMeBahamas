#!/usr/bin/env python3
"""Check what's deployed on Render"""
import requests

response = requests.get("https://hiremebahamas-backend.render.app/", timeout=10)
print(f"Status: {response.status_code}")
print(f"Content: {response.text[:500]}...")  # First 500 chars
print(f"Headers: {dict(response.headers)}")
