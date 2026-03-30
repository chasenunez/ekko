"""
Setup script for EKKO.

Install system-wide with:
    pip install .

Then run from anywhere with:
    ekko
"""

from setuptools import setup, find_packages

setup(
    name="ekko",
    version="1.0.0",
    description="EKKO — scaffold new projects from a template folder.",
    packages=find_packages(),
    # Include every file inside the EXAMPLE template folder.
    include_package_data=True,
    package_data={
        "ekko": ["EXAMPLE/**/*", "EXAMPLE/**/.*"],
    },
    entry_points={
        "console_scripts": [
            "ekko=ekko.main:main",
        ],
    },
    # shutil.copytree with copy_function=shutil.copy2 works on 3.6+.
    python_requires=">=3.6",
)
