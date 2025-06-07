#!/usr/bin/python3
"""
Setup script for tag-writer application.

This file handles the installation of the tag-writer package,
including dependencies and command-line entry points.
"""

from setuptools import setup, find_packages
import os
import re

# Read version from package __init__.py
with open(os.path.join('tag_writer', '__init__.py'), 'r') as f:
    version_match = re.search(r"__version__\s*=\s*['\"]([^'\"]*)['\"]", f.read())
    version = version_match.group(1) if version_match else '0.1.0'

# Read long description from README
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name="tag-writer",
    version=version,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyQt6>=6.0.0",
        "Pillow>=8.0.0",
        "pyexiftool>=0.5.0",
    ],
    entry_points={
        "console_scripts": [
            "tag-writer=tag_writer.main:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for editing image metadata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="image, metadata, exif, iptc, pyqt",
    url="https://github.com/yourusername/tag-writer",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
)

