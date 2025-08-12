#!/usr/bin/env python3
# encoding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from setuptools import setup, find_packages

setup(
    name='Cybersearch',
    version='0.1.0',
    description='Cybersearch - Aggregated Search Tool (Beta)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Robert',
    author_email='wmc200409@gmail.com',
    url='https://github.com/RobertWang4/Cybersearch',
    packages=find_packages(),
    install_requires=[
		'requests',
        'shodan',
        'mmh3',
        'dicttoxml',
        'python-dotenv',
        'PyYAML',
        'pandas',
        'openpyxl',
    ],
	classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'console_scripts': [
            'Cybersearch=scripts.asset_detection.Cybersearch:main',
        ],
    },
    zip_safe=False,
)