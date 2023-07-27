#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

requirements = [
    "textual",
]

setup(
    name="usolitaire",
    version="1.0.2",
    description="Solitaire in your terminal",
    long_description=readme,
    author="Elias Dorneles",
    author_email="eliasdorneles@gmail.com",
    url="https://github.com/eliasdorneles/usolitaire",
    entry_points={
        "console_scripts": {
            "usolitaire = usolitaire.app:main",
        }
    },
    packages=[
        "usolitaire",
    ],
    package_dir={"usolitaire": "usolitaire"},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords="usolitaire",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
