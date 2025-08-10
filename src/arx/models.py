"""
Data models for arx
"""

from dataclasses import dataclass
from typing import List


@dataclass
class SecurityAnalysis:
    """Container for security analysis results"""
    score: int  # 0-100, higher is safer
    malicious_intent: bool
    suspicious_patterns: List[str]
    recommendations: List[str]
    package_name_analysis: str
