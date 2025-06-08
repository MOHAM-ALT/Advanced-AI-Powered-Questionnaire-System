from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ValidationRules:
    """Centralized validation rules"""
    
    # Move validation constants here
    CONFIDENCE_WEIGHTS = {
        'completeness': 0.6,
        'consistency': 0.4,
        'format': 0.3,
        'domain': 0.2,
        'mx_record': 0.3,
        'business_email': 0.2
    }

    def __init__(self):
        self._init_patterns()
    
    def _init_patterns(self):
        """Initialize validation patterns"""
        self.required_fields = ['name', 'industry', 'location']
        self.personal_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        self.suspicious_patterns = ['noreply', 'donotreply', 'test', 'temp', 'fake']
        self.suspicious_tlds = ['.tk', '.ml', '.ga', '.cf']

    # Move validation methods here
