from setuptools import setup, find_packages
import os

setup(
    name="cryptobot-supremo",
    version="1.0.0",
    description="Sistema completo de trading automatizado com IA",
    author="AnalysisSupreme Team",
    packages=find_packages(),
    package_dir={"": "."},  # Root como source
    python_requires=">=3.11",
    install_requires=[
        "requests>=2.28.0",
        "pandas>=1.5.0",
        "numpy>=1.24.0",
        "python-dotenv>=0.19.0",
        "ccxt>=2.0.0",
        "websocket-client>=1.4.0",
        "ta>=0.10.0",
        "scikit-learn>=1.2.0",
        "tensorflow>=2.11.0",
        "torch>=1.13.0",
        "prometheus-client>=0.15.0",
        "structlog>=22.3.0",
        "matplotlib>=3.6.0",
        "plotly>=5.12.0",
        "sqlalchemy>=1.4.0",
        "redis>=4.4.0",
        "pydantic>=1.10.0",
        "pyyaml>=6.0",
        "aiohttp>=3.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.2.0",
            "pytest-asyncio>=0.20.0", 
            "pytest-cov>=4.0.0",
            "black>=22.12.0",
            "flake8>=6.0.0",
            "mypy>=0.991",
            "isort>=5.11.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "analysissupreme=main:main",
        ],
    },
    zip_safe=False,
    include_package_data=True,
)
