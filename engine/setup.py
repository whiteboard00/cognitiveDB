"""
Setup configuration for the Cognition Engine API

This package provides a complete API service for learning analytics and prediction,
ready for deployment and integration by EdTech companies.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cognition-engine-api",
    version="1.0.0",
    author="Cognition Engine Team",
    author_email="support@cognition-engine.com",
    description="Production-ready learning analytics and prediction API for EdTech platforms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cognition-engine/api",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Framework :: AsyncIO",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18",
            "black>=22.0",
            "isort>=5.10",
            "flake8>=4.0",
            "httpx>=0.24.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "deploy": [
            "gunicorn>=20.0.0",
            "uvicorn[standard]>=0.34.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cognition-api=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.sql", "*.md", "*.txt"],
    },
)
