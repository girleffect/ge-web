import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md")) as f:
    README = f.read()

with open(os.path.join(here, "requirements.txt")) as f:
    requires = f.read().split("\n")

setup(
    name="geweb",
    version="0.0.1",
    description="geweb",
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author="Praekelt Foundation",
    author_email="dev@praekelt.com",
    url="None",
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    entry_points={},
)
