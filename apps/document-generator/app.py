#!/usr/bin/env python3
"""
Entry point for Azure App Service - redirects to startup.py
This file helps Oryx detect this as a Python project.
"""
import startup

if __name__ == "__main__":
    # This file exists to help Azure's Oryx build system
    # recognize this as a Python project. The actual
    # application logic is in startup.py
    pass