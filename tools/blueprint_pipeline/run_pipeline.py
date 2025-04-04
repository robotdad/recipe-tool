#!/usr/bin/env python3
"""
Run script for the blueprint pipeline.

This script provides a convenient way to run the blueprint pipeline
from the command line.
"""
import sys
import os

# Add the parent directory to the path to make blueprint_pipeline importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from blueprint_pipeline.blueprint_pipeline import main

if __name__ == "__main__":
    main()
