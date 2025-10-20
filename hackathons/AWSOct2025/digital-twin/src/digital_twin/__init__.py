"""
Digital Twin Application Package.

AI-powered digital twin chat application that creates intelligent company representatives.
"""

__version__ = "1.0.0"
__author__ = "Digital Twin Team"
__description__ = "AI-powered digital twin chat application"

from .core import DigitalTwinService, ConfigurationManager
from .ui import main

__all__ = ["DigitalTwinService", "ConfigurationManager", "main"]