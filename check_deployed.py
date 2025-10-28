#!/usr/bin/env python3
"""Check what's deployed on Railway"""
import requests

response = requests.get("https://hiremebahamas-backend.railway.app/")
print(f"Status: {response.status_code}")
print(f"Content: {response.text[:500]}...")  # First 500 chars
print(f"Headers: {dict(response.headers)}")
