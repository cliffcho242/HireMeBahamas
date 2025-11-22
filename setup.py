"""
Setup configuration for HireMeBahamas Backend
This file ensures compatibility with build tools that expect setup.py
All dependencies are managed in requirements.txt
"""

from setuptools import setup, find_packages

setup(
    name="hiremebahamas-backend",
    version="1.0.0",
    description="HireMeBahamas Flask Backend API",
    python_requires=">=3.11",
    packages=find_packages(where="backend"),
    package_dir={"": "backend"},
    install_requires=[],  # Dependencies in requirements.txt
    zip_safe=False,
)
