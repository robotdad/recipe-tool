#!/usr/bin/env python3
"""
Startup script for Azure App Service deployment.
Sets up environment and launches the document generator app.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path so imports work
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Debug information
print(f"\nPython version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Script directory: {current_dir}")
print(f"\nPython path: {sys.path}")

# List files in current directory
print("\nFiles in current directory:")
for item in current_dir.iterdir():
    print(f"  {item.name}")

# Check if our app directory exists
app_dir = current_dir / "document_generator_app"
print(f"\nApp directory exists: {app_dir.exists()}")
if app_dir.exists():
    print("Files in app directory:")
    for item in app_dir.iterdir():
        print(f"  {item.name}")

if __name__ == "__main__":
    try:
        print("\nAttempting to import document_generator_app.main...")
        from document_generator_app.main import main

        print("Successfully imported main function")
        print("Starting application...\n")
        main()
    except ImportError as e:
        print(f"Import error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
