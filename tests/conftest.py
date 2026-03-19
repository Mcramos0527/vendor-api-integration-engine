"""
Pytest configuration and shared fixtures.
"""

import pytest
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
