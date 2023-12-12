#!/usr/bin/env python3

"""Setuptools setup file."""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Easy-Text-To-Image",
    version="0.1.3",
    author="Drakovek",
    author_email="DrakovekMail@gmail.com",
    description="A Python library to simplify creating images that display text.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Drakovek/EasyTextToImage",
    packages=setuptools.find_packages(),
    install_requires=["Pillow", "Metadata-Magic"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.0'
)
