from setuptools import setup, find_packages
import codecs
import os

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

VERSION = "0.0.6"
DESCRIPTION = "Flask toolkits to boost your development and simplify flask, its featured with AutoSwagger"

# Setting up
setup(
    name="flask-toolkits",
    version=VERSION,
    author="danangjoyoo (Agus Danangjoyo)",
    author_email="<agus.danangjoyo.blog@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=["flask","werkzeug","flask-http-middleware", "pydantic"],
    keywords=['flask', 'middleware', 'http', 'request', "response", "autoswagger", "openapi", "toolkit"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "Typing :: Typed"
    ]
)