#!/usr/bin/env python3
"""
Advanced Validation Rules System
File Location: utils/validation_rules.py
Comprehensive validation for intelligence data
"""

import re
import dns.resolver
import socket
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import tldextract
import validators

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Validation result structure"""
    is_valid: bool
    confidence: float
    validation_type: str
    details: Dict[str, Any]
    timestamp: datetime
    errors: List[str]

class ValidationRules:
    """Comprehensive validation rules for OSINT data"""
    
    # Confidence weights for different validation factors
    CONFIDENCE_WEIGHTS = {
        'email': {
            'format': 0.3,
            'domain': 0.2,
            'mx_record': 0.3,
            'business_email': 0.2
        },
        'phone': {
            'format': 0.4,
            'country_code': 0.3,
            'length': 0.3
        },
        'business': {
            'completeness': 0.6,
            'consistency': 0.4
        },
        'url': {
            'format': 0.4,
            'accessibility': 0.6
        }
    }
    
    def __init__(self):
        self._init_patterns()
        self._init_domains()
        self._init_phone_patterns()
        
        # Cache for DNS lookups
        self._dns_cache = {}
        
        logger.info("Validation rules initialized")
    
    def _init_patterns(self):
        """Initialize validation patterns"""
        # Email patterns
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        # URL patterns
        self.url_pattern = re.compile(
            r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        )
        
        # Business name patterns
        self.business_suffixes = [
            'ltd', 'llc', 'inc', 'corp', 'co', 'company', 'corporation',
            'limited', 'sa', 'llc', 'pty', 'gmbh', 'ag', 'spa'
        ]
        
        # Suspicious patterns
        self.suspicious_patterns = [
            'test', 'temp', 'fake', 'dummy', 'example', 'sample',
            'noreply', 'donotreply', 'admin@', 'support@', 'info@'
        ]
        
        # Professional title patterns
        self.professional_titles = [
            'ceo', 'cto', 'cfo', 'coo', 'president', 'director', 'manager',
            'vice president', 'vp', 'head of', 'lead', 'senior', 'chief'
        ]
    
    def _init_domains(self):
        """Initialize domain classification"""
        # Personal email domains
        self.personal_domains = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'aol.com', 'icloud.com', 'live.com', 'msn.com',
            'protonmail.com', 'mail.com', 'yandex.com'
        }
        
        # Business email domains (commonly used by businesses)
        self.business_domains = {
            'company.com', 'business.com', 'enterprise.com'
        }
        
        # Suspicious TLDs
        self.suspicious_tlds = {
            '.tk', '.ml', '.ga', '.cf', '.top', '.click', '.download'
        }
        
        # Government domains
        self.government_domains = {
            '.gov', '.gov.sa', '.gov.ae', '.mil', '.edu'
        }
    
    def _init_phone_patterns(self):
        """Initialize phone number patterns by country"""
        self.phone_patterns = {
            'saudi': {
                'mobile': re.compile(r'^(?:\+966|966|0)?5[0-9]{8}$'),
                'landline': re.compile(r'^(?:\+966|966|0)?[1-4][0-9]{7}$'),
                'country_code': '+966',
                'mobile_length': 9,
                'landline_length': 8
            },
            'uae': {
                'mobile': re.compile(r'^(?:\+971|971|0)?5[0-9]{8}$'),
                'landline': re.compile(r'^(?:\+971|971|0)?[2-4][0-9]{7}$'),
                'country_code': '+971',
                'mobile_length': 9,
                'landline_length': 8
            },
            'qatar': {
                'mobile': re.compile(r'^(?:\+974|974)?[3567][0-9]{7}$'),
                'landline': re.compile(r'^(?:\+974|974)?4[0-9]{7}$'),
                'country_code': '+974',
                'mobile_length': 8,
                'landline_length': 8
            },
            'kuwait': {
                'mobile': re.compile(r'^(?:\+965|965)?[569][0-9]{7}$'),
                'landline': re.compile(r'^(?:\+965|965)?2[0-9]{7}$'),
                'country_code': '+965',
                'mobile_length': 8,
                'landline_length': 8
            },
            'international': {
                'pattern': re.compile(r'^\+?[1-9]\d{1,14}$'),
                'min_length': 7,
                'max_length': 15
            }
        }
    
    def validate_email(self, email: str) -> ValidationResult:
        """Comprehensive email validation"""
        errors = []
        details = {}
        confidence = 0.0
        
        if not email or not isinstance(email, str):
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                validation_type='email',
                details={'error': 'Invalid email input'},
                timestamp=datetime.now(),
                errors=['Invalid email input']
            )
        
        email = email.strip().lower()
        
        # Format validation
        format_valid = bool(self.email_pattern.match(email))
        if format_valid:
            confidence += self.CONFIDENCE_WEIGHTS['email']['format']
            details['format_valid'] = True
        else:
            errors.append('Invalid email format')
            details['format_valid'] = False
        
        # Extract domain
        if '@' in email:
            local_part, domain = email.rsplit('@', 1)
            details['local_part'] = local_part
            details['domain'] = domain
            
            # Domain validation
            domain_confidence = self._validate_domain(domain)
            confidence += domain_confidence * self.CONFIDENCE_WEIGHTS['email']['domain']
            details['domain_confidence'] = domain_confidence
            
            # Check if business email
            is_business = self._is_business_email(email, domain)
            if is_business:
                confidence += self.CONFIDENCE_WEIGHTS['email']['business_email']
                details['is_business_email'] = True
            else:
                details['is_business_email'] = False
            
            # MX record validation
            has_mx = self._check_mx_record(domain)
            if has_mx:
                confidence += self.CONFIDENCE_WEIGHTS['email']['mx_record']
                details['has_mx_record'] = True
            else:
                errors.append('No MX record found')
                details['has_mx_record'] = False
            
            # Suspicious pattern check
            is_suspicious = self._is_suspicious_email(email)
            if is_suspicious:
                confidence *= 0.5  # Reduce confidence for suspicious emails
                errors.append('Suspicious email pattern detected')
                details['is_suspicious'] = True
            else:
                details['is_suspicious'] = False
        
        is_valid = format_valid and confidence >= 0.5
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=min(confidence, 1.0),
            validation_type='email',
            details=details,
            timestamp=datetime.now(),
            errors=errors
        )
    
    def validate_phone(self, phone: str, country: str = 'international') -> ValidationResult:
        """Comprehensive phone number validation"""
        errors = []
        details = {}
        confidence = 0.0
        
        if not phone or not isinstance(phone, str):
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                validation_type='phone',
                details={'error': 'Invalid phone input'},
                timestamp=datetime.now(),
                errors=['Invalid phone input']
            )
        
        # Clean phone number
        original_phone = phone
        cleaned_phone = re.sub(r'[^\d+]', '', phone)
        details['original'] = original_phone
        details['cleaned'] = cleaned_phone
        
        # Country-specific validation
        country_patterns = self.phone_patterns.get(country.lower(), 
                                                 self.phone_patterns['international'])
        
        if country != 'international':
            # Specific country validation
            mobile_valid = country_patterns.get('mobile', re.compile('')).match(cleaned_phone)
            landline_valid = country_patterns.get('landline', re.compile('')).match(cleaned_phone)
            
            if mobile_valid:
                confidence += self.CONFIDENCE_WEIGHTS['phone']['format']
                details['type'] = 'mobile'
                details['format_valid'] = True
            elif landline_valid:
                confidence += self.CONFIDENCE_WEIGHTS['phone']['format']
                details['type'] = 'landline' 
                details['format_valid'] = True
            else:
                errors.append(f'Invalid {country} phone format')
                details['format_valid'] = False
            
            # Country code validation
            country_code = country_patterns.get('country_code', '')
            if cleaned_phone.startswith(country_code.replace('+', '')):
                confidence += self.CONFIDENCE_WEIGHTS['phone']['country_code']
                details['has_country_code'] = True
            else:
                details['has_country_code'] = False
            
        else:
            # International validation
            pattern = country_patterns['pattern']
            if pattern.match(cleaned_phone):
                confidence += self.CONFIDENCE_WEIGHTS['phone']['format']
                details['format_valid'] = True
            else:
                errors.append('Invalid international phone format')
                details['format_valid'] = False
        
        # Length validation
        min_length = country_patterns.get('min_length', 7)
        max_length = country_patterns.get('max_length', 15)
        
        if min_length <= len(cleaned_phone) <= max_length:
            confidence += self.CONFIDENCE_WEIGHTS['phone']['length']
            details['length_valid'] = True
        else:
            errors.append(f'Invalid phone length: {len(cleaned_phone)}')
            details['length_valid'] = False
        
        is_valid = confidence >= 0.5
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=min(confidence, 1.0),
            validation_type='phone',
            details=details,
            timestamp=datetime.now(),
            errors=errors
        )
    
    def validate_url(self, url: str) -> ValidationResult:
        """Comprehensive URL validation"""
        errors = []
        details = {}
        confidence = 0.0
        
        if not url or not isinstance(url, str):
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                validation_type='url',
                details={'error': 'Invalid URL input'},
                timestamp=datetime.now(),
                errors=['Invalid URL input']
            )
        
        url = url.strip()
        details['original_url'] = url
        
        # Format validation using validators library
        format_valid = validators.url(url)
        if format_valid:
            confidence