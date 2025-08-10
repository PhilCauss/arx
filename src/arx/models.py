"""
Data models for arx
"""

from dataclasses import dataclass
from typing import List


@dataclass
class SecurityAnalysis:
    """Container for security analysis results"""
    malicious_intent: bool
    confidence: float  # 0.0-1.0, model's confidence in classification
    suspicious_patterns: List[str]
    recommendations: List[str]
    analysis: str  # detailed explanation of findings
