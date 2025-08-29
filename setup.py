from setuptools import setup, find_packages

setup(
    name="axis",
    version="0.1.0",
    description="Automated Xenial Intelligence System - Elite Dangerous personal-assistant framework",
    author="thanh-tk",
    packages=find_packages(),
    install_requires=[
        "eliteapi>=0.1.0",
        "websockets>=10.0",
        "requests>=2.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
        ]
    },
    python_requires=">=3.8",
)
