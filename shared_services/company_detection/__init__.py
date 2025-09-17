"""Company Detection Service"""
from .detector import CompanyDetectionService as CompanyDetector
from .detector import CompanyDetectionResult

__all__ = ["CompanyDetector", "CompanyDetectionResult"]