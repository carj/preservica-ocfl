import pathlib
import sys
import os
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text(encoding="utf-8")

PKG = "preservica-ocfl"

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    os.system('python -m build')
    os.system('twine upload dist/*')
    sys.exit()


# This call to setup() does all the work
setup(
    name=PKG,
    version="0.0.1",
    description="Python module for creating a local OCFL storage structure from a Preservica repository",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/carj/preserva-ocfl",
    author="James Carr",
    author_email="drjamescarr@gmail.com",
    license="Apache License 2.0",
    packages=["preservica-ocfl"],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: System :: Archiving",
    ],
    keywords='Preservica API Preservation OCFL Storage',
    install_requires=["pyPreservica", "python-dateutil", "ocflcore"],
    project_urls={
        'Documentation': 'https://github.com/carj/preserva-ocfl',
        'Source': 'https://github.com/carj/preserva-ocfl',
        'Discussion Forum': 'https://github.com/carj/preserva-ocfl',
    }
)
