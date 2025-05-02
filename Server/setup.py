from setuptools import setup
from glob import glob
import os

modules = glob("./*.py")
module_names = [
    os.path.splitext(os.path.basename(f))[0]
    for f in modules
    if os.path.basename(f) != "setup.py"
]


setup(
    author="Daniel Vargas",
    platforms=["Unix"],
    name="run-httpserver",
    version="1.0",
    py_modules=module_names,
    install_requires=["flask","waitress","colored", "cmd2"], 
    entry_points={
        "console_scripts": [
            "run-httpserver=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.10"
    ]
)
