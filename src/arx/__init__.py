"""
arx - A secure wrapper around yay package manager
Analyzes packages for malicious intent before installation
"""

__version__ = "1.0.3"
__author__ = "Arx Developer"

from .analyzer import ArxSecurityAnalyzer
from .wrapper import YayWrapper
from .models import SecurityAnalysis

__all__ = ['ArxSecurityAnalyzer', 'YayWrapper', 'SecurityAnalysis']
