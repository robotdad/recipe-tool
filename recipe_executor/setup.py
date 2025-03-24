"""Setup script for Recipe Executor."""

from setuptools import find_packages, setup

# Read the requirements from the requirements.txt file
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="recipe-executor",
    version="0.1.0",
    description="A robust tool for executing LLM 'recipes' with code-driven reliability",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Anthropic",
    author_email="info@anthropic.com",
    url="https://github.com/anthropics/recipe-executor",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={
        "console_scripts": [
            "recipe-executor=recipe_executor.main:main",
        ],
    },
)
