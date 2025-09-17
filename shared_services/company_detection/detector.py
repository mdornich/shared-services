"""
Company Detection Service
Extracts company information from email addresses
Ported from aiBA-1 CompanyDetectionService.ts to Python
"""
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class CompanyDetectionResult:
    """Result of company detection from email."""
    company: Optional[str]
    type: str  # 'corporate', 'personal', 'educational', 'government', 'unknown'
    confidence: float  # 0-1
    industry: Optional[str] = None
    website: Optional[str] = None  # Company website URL extracted from email domain
    metadata: Optional[Dict[str, Any]] = None


class CompanyDetectionService:
    """Service for detecting company information from email addresses."""
    
    def __init__(self):
        self.cache: Dict[str, CompanyDetectionResult] = {}
        self.metrics = {
            "total_detections": 0,
            "cache_hits": 0,
            "total_response_time": 0,
            "cache_size": 0
        }
        
        # Personal email providers
        self.personal_providers: Set[str] = {
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com',
            'aol.com', 'protonmail.com', 'yandex.com', 'mail.ru', 'me.com',
            'live.com', 'msn.com', 'yahoo.co.uk', 'yahoo.ca', 'yahoo.fr',
            'googlemail.com', 'outlook.co.uk', 'btinternet.com', 'sky.com'
        }
        
        # Known corporate domains with their info
        self.corporate_info: Dict[str, Dict[str, str]] = {
            'microsoft.com': {'name': 'Microsoft', 'industry': 'Technology'},
            'apple.com': {'name': 'Apple', 'industry': 'Technology'},
            'google.com': {'name': 'Google', 'industry': 'Technology'},
            'amazon.com': {'name': 'Amazon', 'industry': 'Technology'},
            'meta.com': {'name': 'Meta', 'industry': 'Technology'},
            'facebook.com': {'name': 'Facebook', 'industry': 'Technology'},
            'tesla.com': {'name': 'Tesla', 'industry': 'Automotive'},
            'netflix.com': {'name': 'Netflix', 'industry': 'Entertainment'},
            'salesforce.com': {'name': 'Salesforce', 'industry': 'Technology'},
            'oracle.com': {'name': 'Oracle', 'industry': 'Technology'},
            'ibm.com': {'name': 'IBM', 'industry': 'Technology'},
            'adobe.com': {'name': 'Adobe', 'industry': 'Technology'},
            'shopify.com': {'name': 'Shopify', 'industry': 'E-commerce'},
            'stripe.com': {'name': 'Stripe', 'industry': 'Financial Services'},
            'anthropic.com': {'name': 'Anthropic', 'industry': 'AI/Technology'},
            'openai.com': {'name': 'OpenAI', 'industry': 'AI/Technology'}
        }
    
    def detect_from_email(self, email: str) -> CompanyDetectionResult:
        """
        Detect company information from an email address.
        
        Args:
            email: Email address to analyze
            
        Returns:
            CompanyDetectionResult with detection information
        """
        start_time = datetime.now()
        
        # Check cache first
        if email in self.cache:
            self.metrics["cache_hits"] += 1
            self.metrics["total_detections"] += 1
            return self.cache[email]
        
        # Extract domain
        domain_match = re.search(r'@([a-zA-Z0-9.-]+)', email)
        if not domain_match:
            result = CompanyDetectionResult(
                company=None,
                type='unknown',
                confidence=0,
                website=None
            )
            return self._cache_result(email, result, start_time)
        
        domain = domain_match.group(1).lower()
        
        # Check for personal providers
        if domain in self.personal_providers:
            result = CompanyDetectionResult(
                company=self._get_personal_provider_name(domain),
                type='personal',
                confidence=1.0,
                website=None,  # Personal emails don't have company websites
                metadata={'provider': domain}
            )
            return self._cache_result(email, result, start_time)
        
        # Check for educational institutions
        if domain.endswith('.edu') or '.edu.' in domain or \
           domain.endswith('.ac.uk') or '.ac.' in domain:
            result = CompanyDetectionResult(
                company=self._extract_university_name(domain),
                type='educational',
                confidence=0.9,
                industry='Education',
                website=domain  # Educational domain is their website
            )
            return self._cache_result(email, result, start_time)
        
        # Check for government domains
        if domain.endswith('.gov') or domain.endswith('.mil') or '.gov.' in domain:
            result = CompanyDetectionResult(
                company=self._extract_government_name(domain),
                type='government',
                confidence=0.9,
                industry='Government',
                website=domain  # Government domain is their website
            )
            return self._cache_result(email, result, start_time)
        
        # Check known corporate domains
        if domain in self.corporate_info:
            info = self.corporate_info[domain]
            result = CompanyDetectionResult(
                company=info['name'],
                type='corporate',
                confidence=0.8,
                industry=info.get('industry'),
                website=domain  # Corporate domain is their website
            )
            return self._cache_result(email, result, start_time)
        
        # Try to extract company name from domain
        extracted_name = self._extract_company_from_domain(domain)
        result = CompanyDetectionResult(
            company=extracted_name,
            type='corporate',
            confidence=0.6 if extracted_name else 0.2,
            industry=self._infer_industry(domain),
            website=domain if extracted_name else None  # Only set website if we extracted a company
        )
        
        return self._cache_result(email, result, start_time)
    
    def _get_personal_provider_name(self, domain: str) -> str:
        """Get friendly name for personal email provider."""
        providers = {
            'gmail.com': 'Gmail',
            'yahoo.com': 'Yahoo',
            'outlook.com': 'Outlook',
            'hotmail.com': 'Hotmail',
            'icloud.com': 'iCloud',
            'aol.com': 'AOL'
        }
        return providers.get(domain, domain)
    
    def _extract_university_name(self, domain: str) -> str:
        """Extract university name from educational domain."""
        # Remove .edu, .ac.uk etc and format
        name = re.sub(r'\.(edu|ac\.uk|ac\..+)$', '', domain)
        name = name.replace('.', ' ')
        name = ' '.join(word.capitalize() for word in name.split())
        
        # Known mappings
        mappings = {
            'stanford': 'Stanford University',
            'mit': 'MIT',
            'harvard': 'Harvard University',
            'berkeley': 'UC Berkeley',
            'oxford': 'Oxford University',
            'cambridge': 'Cambridge University'
        }
        
        return mappings.get(name.lower(), f"{name} University")
    
    def _extract_government_name(self, domain: str) -> str:
        """Extract government organization name from domain."""
        if 'nasa' in domain:
            return 'NASA'
        if 'state' in domain:
            return 'US State Department'
        if 'army' in domain:
            return 'US Army'
        if 'navy' in domain:
            return 'US Navy'
        if 'airforce' in domain:
            return 'US Air Force'
        
        # Generic extraction
        name = re.sub(r'\.(gov|mil)$', '', domain)
        name = name.replace('.', ' ').upper()
        return name
    
    def _extract_company_from_domain(self, domain: str) -> Optional[str]:
        """Extract company name from generic domain."""
        # Remove common TLDs and subdomains
        clean_domain = re.sub(r'^(www\.|mail\.|email\.)', '', domain)
        clean_domain = re.sub(r'\.(com|org|net|co|io|ai|tech|inc)$', '', clean_domain)
        clean_domain = re.sub(r'\.(co\.uk|com\.au|co\.in)$', '', clean_domain)
        
        if len(clean_domain) < 2:
            return None
        
        # Capitalize first letter
        return clean_domain[0].upper() + clean_domain[1:]
    
    def _infer_industry(self, domain: str) -> Optional[str]:
        """Infer industry from domain keywords."""
        if 'bank' in domain or 'finance' in domain:
            return 'Financial Services'
        if 'tech' in domain or 'ai' in domain or 'software' in domain:
            return 'Technology'
        if 'health' in domain or 'medical' in domain or 'pharma' in domain:
            return 'Healthcare'
        if 'consulting' in domain:
            return 'Consulting'
        if 'law' in domain or 'legal' in domain:
            return 'Legal Services'
        return None
    
    def _cache_result(
        self, 
        email: str, 
        result: CompanyDetectionResult, 
        start_time: datetime
    ) -> CompanyDetectionResult:
        """Cache the detection result with metrics tracking."""
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Update metrics
        self.metrics["total_detections"] += 1
        self.metrics["total_response_time"] += response_time
        self.metrics["cache_size"] = len(self.cache)
        
        # Cache with LRU-like behavior (simple size limit)
        if len(self.cache) > 1000:
            # Remove oldest entry
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        
        self.cache[email] = result
        return result
    
    def get_health(self) -> Dict[str, Any]:
        """Get service health metrics."""
        return {
            "status": "healthy",
            "metrics": {
                "cache_size": len(self.cache),
                "total_detections": self.metrics["total_detections"],
                "cache_hits": self.metrics["cache_hits"],
                "average_response_time": (
                    self.metrics["total_response_time"] / self.metrics["total_detections"]
                    if self.metrics["total_detections"] > 0
                    else 0
                )
            }
        }
    
    def clear_cache(self) -> None:
        """Clear the detection cache."""
        self.cache.clear()
        self.metrics["cache_size"] = 0


# Global instance
company_detection_service = CompanyDetectionService()