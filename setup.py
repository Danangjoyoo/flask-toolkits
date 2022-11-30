from setuptools import setup, find_packages
import codecs
import os

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

VERSION = "0.6.11"
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
    install_requires=["flask>=2.0.0","werkzeug>=2.0.0","flask-http-middleware", "pydantic", "python-jose"],
    keywords=['flask', 'middleware', 'http', 'request', "response", "swagger", "openapi", "toolkit"],
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "Typing :: Typed"
    ],
    url="https://github.com/Danangjoyoo/flask-toolkits"

)