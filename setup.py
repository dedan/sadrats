"""
Script for building the example.

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['rats.py']
# DATA_FILES = [('images', ['/shotgun/src/python-api/shotgun_api3/lib/httplib2/cacerts.txt'])]
DATA_FILES = []
OPTIONS = {
    'iconfile':'icon.icns',
    'plist': {'CFBundleShortVersionString':'0.1.0',}
}

setup(
    app=APP,
    name='DedanSuperApp',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)