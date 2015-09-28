#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-skd-smoke',
    version='0.1',
    packages=find_packages(exclude=['skd_smoke_tests', 'example_project']),
    description='Smoke tests for django projects.',
    long_description=open('README.rst').read(),
    author='SteelKiwi Development',
    author_email='sales@steelkiwi.com',
    license='MIT',
    url='https://github.com/steelkiwi/django-skd-smoke',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent'])
