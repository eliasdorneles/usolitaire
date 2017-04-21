#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'urwid',
]

setup(
    name='usolitaire',
    version='0.2.0',
    description="Solitaire in your terminal",
    long_description=readme,
    author="Elias Dorneles",
    author_email='eliasdorneles@gmail.com',
    url='https://github.com/eliasdorneles/usolitaire',
    entry_points={
        'console_scripts': {
            'usolitaire = usolitaire.app:main',
        }
    },
    packages=[
        'usolitaire',
    ],
    package_dir={'usolitaire':
                 'usolitaire'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='usolitaire',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
