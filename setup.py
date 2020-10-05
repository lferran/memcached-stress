# -*- coding: utf-8 -*-
from os import path

from setuptools import find_packages, setup


def get_requirements(rfile):
    with open(rfile, "r") as f:
        requirements = []
        for line in f.readlines():
            if len(line) == 0 or line[0] == "#" or "://" in line:
                continue
            requirements.append(line.strip())
    return requirements


def version():
    cdir = path.dirname(__file__)
    try:
        VERSION = open(path.join(cdir, "VERSION")).read().strip("\n")
        return VERSION
    except FileNotFoundError:
        return None


setup(
    name="memcached-stress",
    version=version(),
    description="Stress test Guillotina memcached driver",
    long_description="",
    keywords=[],
    author="Ferran Llamas",
    author_email="llamas.arroniz@gmail.com",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    url="http://github.com/lferran/memcached-stress.git",
    license="Private License",
    zip_safe=True,
    include_package_data=True,
    packages=find_packages(),
    namespace_packages=[],
    install_requires=get_requirements("requirements.txt"),
)
