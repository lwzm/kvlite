#!/usr/bin/env python

from setuptools import setup

name = "kvlite"
author = "lwzm"

with open("README") as f:
    long_description = f.read()


setup(
    name=name,
    version="0.6",
    description="kvlite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=author,
    author_email="{}@qq.com".format(author),
    keywords="kv sqlite key-value".split(),
    url="https://github.com/{}/{}".format(author, name),
    py_modules=["kvlite"],
    classifiers=[
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
    ],
)
