#!/usr/bin/env python3
"""
Setup script for Agentic Reasoning System SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="agentic-reasoning-system",
    version="1.0.0",
    author="Manish Bhatt",
    author_email="manish.bhatt13212@gmail.com",
    description="Implementation of Bhatt Conjectures for AI Reasoning and Understanding Assessment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/agentic-reasoning-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "agentic-reasoning=agentic_reasoning_system:main",
        ],
    },
    keywords="ai reasoning understanding tautology bhatt conjectures llm openai",
    project_urls={
        "Bug Reports": "https://github.com/your-username/agentic-reasoning-system/issues",
        "Source": "https://github.com/your-username/agentic-reasoning-system",
        "Documentation": "https://github.com/your-username/agentic-reasoning-system/blob/main/README.md",
    },
)