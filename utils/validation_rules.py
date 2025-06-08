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
        try:
            format_valid = validators.url(url)
            if format_valid:
                confidence += self.CONFIDENCE_WEIGHTS['url']['format']
                details['format_valid'] = True
            else:
                errors.append('Invalid URL format')
                details['format_valid'] = False
        except:
            # Fallback to regex validation
            format_valid = bool(self.url_pattern.match(url))
            if format_valid:
                confidence += self.CONFIDENCE_WEIGHTS['url']['format']
                details['format_valid'] = True
            else:
                errors.append('Invalid URL format')
                details['format_valid'] = False
        
        # Extract domain from URL
        try:
            extracted = tldextract.extract(url)
            domain = f"{extracted.domain}.{extracted.suffix}"
            details['domain'] = domain
            details['subdomain'] = extracted.subdomain
            details['tld'] = extracted.suffix
            
            # Domain validation
            domain_confidence = self._validate_domain(domain)
            confidence += domain_confidence * 0.2
            details['domain_confidence'] = domain_confidence
            
        except Exception as e:
            errors.append(f'Failed to parse domain: {e}')
            details['domain_parse_error'] = str(e)
        
        # Accessibility check (optional - can be slow)
        # accessibility_valid = self._check_url_accessibility(url)
        # if accessibility_valid:
        #     confidence += self.CONFIDENCE_WEIGHTS['url']['accessibility']
        #     details['is_accessible'] = True
        
        is_valid = format_valid and confidence >= 0.4
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=min(confidence, 1.0),
            validation_type='url',
            details=details,
            timestamp=datetime.now(),
            errors=errors
        )
    
    def validate_business_profile(self, profile: Dict[str, Any]) -> ValidationResult:
        """Validate business profile data"""
        errors = []
        details = {}
        confidence = 0.0
        
        # Required fields
        required_fields = ['name', 'industry', 'location']
        optional_fields = ['description', 'website', 'phone', 'email', 'size']
        
        # Check completeness
        present_fields = sum(1 for field in required_fields if profile.get(field))
        completeness = present_fields / len(required_fields)
        confidence += completeness * self.CONFIDENCE_WEIGHTS['business']['completeness']
        details['completeness'] = completeness
        
        # Check missing required fields
        missing_fields = [field for field in required_fields if not profile.get(field)]
        if missing_fields:
            errors.extend([f'Missing required field: {field}' for field in missing_fields])
        details['missing_fields'] = missing_fields
        
        # Validate individual fields
        field_validations = {}
        
        # Business name validation
        if profile.get('name'):
            name_valid = self._validate_business_name(profile['name'])
            field_validations['name'] = name_valid
            if not name_valid:
                errors.append('Invalid business name format')
        
        # Industry validation
        if profile.get('industry'):
            industry_valid = self._validate_industry(profile['industry'])
            field_validations['industry'] = industry_valid
        
        # Location validation
        if profile.get('location'):
            location_valid = self._validate_location(profile['location'])
            field_validations['location'] = location_valid
        
        # Email validation if present
        if profile.get('email'):
            email_result = self.validate_email(profile['email'])
            field_validations['email'] = email_result.is_valid
            details['email_validation'] = email_result.details
        
        # Phone validation if present
        if profile.get('phone'):
            phone_result = self.validate_phone(profile['phone'])
            field_validations['phone'] = phone_result.is_valid
            details['phone_validation'] = phone_result.details
        
        # Website validation if present
        if profile.get('website'):
            url_result = self.validate_url(profile['website'])
            field_validations['website'] = url_result.is_valid
            details['website_validation'] = url_result.details
        
        # Consistency check
        consistency_score = sum(field_validations.values()) / len(field_validations) if field_validations else 0
        confidence += consistency_score * self.CONFIDENCE_WEIGHTS['business']['consistency']
        details['consistency_score'] = consistency_score
        details['field_validations'] = field_validations
        
        is_valid = completeness >= 0.8 and consistency_score >= 0.7
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=min(confidence, 1.0),
            validation_type='business_profile',
            details=details,
            timestamp=datetime.now(),
            errors=errors
        )
    
    def validate_person_profile(self, profile: Dict[str, Any]) -> ValidationResult:
        """Validate person profile data"""
        errors = []
        details = {}
        confidence = 0.0
        
        # Required fields for person
        required_fields = ['name', 'title']
        optional_fields = ['company', 'location', 'email', 'phone', 'experience']
        
        # Check completeness
        present_fields = sum(1 for field in required_fields if profile.get(field))
        completeness = present_fields / len(required_fields)
        confidence += completeness * 0.5
        details['completeness'] = completeness
        
        # Validate name
        if profile.get('name'):
            name_valid = self._validate_person_name(profile['name'])
            details['name_valid'] = name_valid
            if name_valid:
                confidence += 0.2
        
        # Validate title
        if profile.get('title'):
            title_valid = self._validate_professional_title(profile['title'])
            details['title_valid'] = title_valid
            if title_valid:
                confidence += 0.2
        
        # Email validation if present
        if profile.get('email'):
            email_result = self.validate_email(profile['email'])
            details['email_valid'] = email_result.is_valid
            if email_result.is_valid:
                confidence += 0.1
        
        is_valid = completeness >= 0.5 and confidence >= 0.5
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=min(confidence, 1.0),
            validation_type='person_profile',
            details=details,
            timestamp=datetime.now(),
            errors=errors
        )
    
    def _validate_domain(self, domain: str) -> float:
        """Validate domain and return confidence score"""
        if not domain:
            return 0.0
        
        confidence = 0.5  # Base confidence
        
        try:
            # Check if domain has valid TLD
            extracted = tldextract.extract(domain)
            if extracted.suffix:
                confidence += 0.2
            
            # Check for suspicious TLD
            if f".{extracted.suffix}" in self.suspicious_tlds:
                confidence -= 0.3
            
            # Check domain length (reasonable business domains)
            if 3 <= len(extracted.domain) <= 20:
                confidence += 0.1
            
            return max(0.0, min(confidence, 1.0))
            
        except Exception:
            return 0.1
    
    def _is_business_email(self, email: str, domain: str) -> bool:
        """Check if email appears to be business email"""
        # Not a personal domain
        if domain.lower() in self.personal_domains:
            return False
        
        # Has business-like domain structure
        if '.' not in domain:
            return False
        
        # Local part doesn't look personal
        local_part = email.split('@')[0].lower()
        personal_indicators = ['personal', 'private', 'home', 'family']
        if any(indicator in local_part for indicator in personal_indicators):
            return False
        
        return True
    
    def _check_mx_record(self, domain: str) -> bool:
        """Check if domain has MX record"""
        if domain in self._dns_cache:
            return self._dns_cache[domain]
        
        try:
            dns.resolver.resolve(domain, 'MX')
            self._dns_cache[domain] = True
            return True
        except:
            self._dns_cache[domain] = False
            return False
    
    def _is_suspicious_email(self, email: str) -> bool:
        """Check for suspicious email patterns"""
        email_lower = email.lower()
        return any(pattern in email_lower for pattern in self.suspicious_patterns)
    
    def _validate_business_name(self, name: str) -> bool:
        """Validate business name format"""
        if not name or len(name) < 2:
            return False
        
        # Check for suspicious patterns
        name_lower = name.lower()
        if any(pattern in name_lower for pattern in ['test', 'temp', 'fake', 'example']):
            return False
        
        return True
    
    def _validate_industry(self, industry: str) -> bool:
        """Validate industry field"""
        if not industry or len(industry) < 3:
            return False
        
        # Common industries
        valid_industries = [
            'technology', 'healthcare', 'finance', 'retail', 'hospitality',
            'manufacturing', 'education', 'real estate', 'consulting',
            'logistics', 'energy', 'government', 'automotive', 'agriculture'
        ]
        
        industry_lower = industry.lower()
        return any(valid_ind in industry_lower for valid_ind in valid_industries)
    
    def _validate_location(self, location: str) -> bool:
        """Validate location field"""
        if not location or len(location) < 2:
            return False
        
        # Check for suspicious patterns
        location_lower = location.lower()
        if any(pattern in location_lower for pattern in ['test', 'temp', 'fake', 'unknown']):
            return False
        
        return True
    
    def _validate_person_name(self, name: str) -> bool:
        """Validate person name"""
        if not name or len(name) < 2:
            return False
        
        # Check for reasonable name pattern
        name_pattern = re.compile(r'^[A-Za-z\s.-]+$')
        if not name_pattern.match(name):
            return False
        
        # Should have at least first and last name
        parts = name.split()
        if len(parts) < 2:
            return False
        
        return True
    
    def _validate_professional_title(self, title: str) -> bool:
        """Validate professional title"""
        if not title or len(title) < 3:
            return False
        
        title_lower = title.lower()
        
        # Check for professional keywords
        professional_keywords = [
            'manager', 'director', 'engineer', 'analyst', 'specialist',
            'coordinator', 'supervisor', 'officer', 'assistant', 'associate',
            'consultant', 'advisor', 'representative', 'executive', 'lead'
        ]
        
        return any(keyword in title_lower for keyword in professional_keywords + self.professional_titles)
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return {
            'dns_cache_size': len(self._dns_cache),
            'supported_validations': [
                'email', 'phone', 'url', 'business_profile', 'person_profile'
            ],
            'supported_countries': list(self.phone_patterns.keys()),
            'personal_domains_count': len(self.personal_domains),
            'suspicious_patterns_count': len(self.suspicious_patterns)
        }