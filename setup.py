"""
Setup configuration for HAVN Python SDK
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
requirements_path = this_directory / "requirements.txt"
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split("\n")

setup(
    name="havn-sdk",
    version="1.0.9",
    author="Bagus",
    author_email="bagus@intelove.com",
    description="Official Python SDK for HAVN (Hierarchical Associate Voucher Network) API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/havn/havn-python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/havn/havn-python-sdk/issues",
        "Documentation": "https://docs.havn.com",
        "Source Code": "https://github.com/havn/havn-python-sdk",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
            "isort>=5.10.0",
        ],
    },
    keywords="havn, mlm, voucher, api, sdk, webhook, commission, referral",
    include_package_data=True,
    zip_safe=False,
)
