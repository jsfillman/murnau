#!/usr/bin/env python3
"""Setup configuration for Murnau synthesizer control interface"""

from setuptools import setup, find_packages
import os

# Read the contents of the README file
def read_long_description():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "Murnau - Cinematic Synthesizer Control Interface"

setup(
    name="murnau",
    version="0.1.0",
    author="Murnau Development Team",
    description="A stylish PyQt6 UI for controlling legato_synth via OSC",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/jsfillman/caelus/murnau",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Synthesis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.0.0",
        "mido>=1.2.0",
        "python-osc>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-qt>=4.0.0",
            "pytest-mock>=3.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "murnau=murnau_ui:main",
            "murnau-melody=melody:main",
            "murnau-ramp-test=ramp_test:main",
        ],
    },
    package_data={
        "murnau": ["../assets/images/*.png"],
    },
    include_package_data=True,
)