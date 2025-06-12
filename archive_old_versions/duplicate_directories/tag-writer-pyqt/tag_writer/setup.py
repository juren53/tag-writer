#!/usr/bin/python3
"""
Setup script for tag-writer application.
"""

from setuptools import setup, find_packages

setup(
    name="tag-writer",
    version="0.06b",
    packages=find_packages(),
    install_requires=[
        "wxPython>=4.0.0",
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
    keywords="image, metadata, exif, iptc, wxpython",
    url="https://github.com/yourusername/tag-writer",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics",
    ],
)
