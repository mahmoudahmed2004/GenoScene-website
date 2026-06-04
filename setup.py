#!/usr/bin/env python3
"""
GenoScene - AI-Powered Forensic Phenotype Prediction System
Setup script for installation and distribution
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="genoscene",
    version="2.1.0",
    author="GenoScene Team",
    author_email="team@genoscene.com",
    description="AI-Powered Forensic Phenotype Prediction System",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/genoscene",
    project_urls={
        "Bug Reports": "https://github.com/your-username/genoscene/issues",
        "Source": "https://github.com/your-username/genoscene",
        "Documentation": "https://genoscene.readthedocs.io",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Legal Industry",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
            "myst-parser>=0.15.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipykernel>=6.0.0",
            "notebook>=6.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "genoscene-predict=src.phenotypicprediction:main",
            "genoscene-mpileup=src.mpileuptocsv:main",
            "genoscene-vcf=src.vcftocsv:main",
            "genoscene-plot-dc=src.plotphenodc:main",
            "genoscene-plot-gl=src.plotphenogl:main",
        ],
    },
    include_package_data=True,
    package_data={
        "genoscene": [
            "data/*.csv",
            "data/*.list",
            "data/face_images/*.png",
            "templates/*.html",
        ],
    },
    keywords=[
        "forensic",
        "phenotype",
        "prediction",
        "dna",
        "genetics",
        "bioinformatics",
        "snp",
        "hirisplex",
        "ai",
        "machine-learning",
    ],
    zip_safe=False,
)
