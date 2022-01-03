"""Setup manifest."""

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="space_garbage",
    description="Space Garbage: clean the space",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="0.0.1",
    author="Rouslan Gaisin",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "play-space-garbage = space_garbage.main:main",
        ],
    },
    python_requires='>=3.7',
    url="https://github.com/gaisin/space_garbage",
)
