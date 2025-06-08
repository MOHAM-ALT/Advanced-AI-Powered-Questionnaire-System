#!/usr/bin/env python3

"""
Advanced AI Intelligence Analyzer
File Location: core/ai_analyzer.py
AI-Powered Analysis and Intelligent Documentation System
"""

import re
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import logging
from pathlib import Path
import statistics

# Text processing and AI libraries
try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None

logger = logging.getLogger(__name__)

@dataclass
class IntelligenceAnalysis:
    """Comprehensive intelligence analysis result"""
    investigation_id: str
    target_identifier: str
    analysis_timestamp: datetime
    
    # Business Analysis
    business_type: str
    business_confidence: float
    industry_classification: str
    company_size_estimate: str
    target_audience_type: str  # B2B, B2C, Government, Mixed
    
    # Geographic Analysis
    geographic_distribution: Dict[str, int]
    primary_location: str
    secondary_locations: List[str]
    geographic_coverage: str  # Local, Regional, National, International
    
    # Personnel Analysis
    decision_makers: List[Dict[str, Any]]
    key_personnel: List[Dict[str, Any]]
    organizational_structure: Dict[str, Any]
    personnel_count_estimate: int
    
    # Contact Intelligence
    contact_quality_scores: Dict[str, float]
    verified_contacts: List[Dict[str, Any]]
    contact_channels: List[str]
    best_contact_methods: List[str]
    
    # Market Intelligence
    competitive_landscape: Dict[str, Any]
    market_position: str
    growth_indicators: List[str]
    business_opportunities: List[str]
    
    # Technology & Digital Presence
    technology_stack: List[str]
    digital_maturity: str
    online_presence_strength: float
    social_media_activity: Dict[str, Any]
    
    # Risk Assessment
    data_quality_score: float
    information_completeness: float
    verification_status: Dict[str, str]
    confidence_factors: List[str]
    risk_indicators: List[str]
    
    # Insights and Recommendations
    key_insights: List[str]
    actionable_recommendations: List[str]
    follow_up_opportunities: List[str]
    intelligence_gaps: List[str]
    
    # Metadata
    total_data_points: int
    sources_analyzed: List[str]
    analysis_methods_used: List[str]
    processing_time_seconds: float

class BusinessTypeClassifier:
    """AI-powered business type classification"""
    
    def __init__(self):
        self.business_patterns = self._initialize_business_patterns()
        self.industry_keywords = self._initialize_industry_keywords()
        
    def _initialize_business_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize business classification patterns"""
        return {
            'technology': {
                'keywords': ['software', 'tech', 'IT', 'digital', 'app', 'platform', 'AI', 'machine learning', 'cloud', 'SaaS'],
                'indicators': ['developer', 'engineer', 'CTO', 'technical', 'programming', 'coding', 'development'],
                'business_models': ['B2B', 'B2C', 'SaaS', 'Platform'],
                'confidence_weight': 1.0
            },
            'healthcare': {
                'keywords': ['medical', 'health', 'clinic', 'hospital', 'pharmaceutical', 'biotech', 'healthcare'],
                'indicators': ['doctor', 'nurse', 'medical director', 'physician', 'therapist', 'specialist'],
                'business_models': ['B2C', 'B2B', 'Healthcare'],
                'confidence_weight': 0.95
            },
            'finance': {
                'keywords': ['bank', 'financial', 'investment', 'insurance', 'fintech', 'trading', 'capital'],
                'indicators': ['CFO', 'financial advisor', 'analyst', 'banker', 'trader', 'accountant'],
                'business_models': ['B2B', 'B2C', 'Financial Services'],
                'confidence_weight': 0.9
            },
            'retail': {
                'keywords': ['retail', 'store', 'shop', 'commerce', 'sales', 'merchandise', 'fashion'],
                'indicators': ['sales manager', 'store manager', 'merchandiser', 'buyer', 'cashier'],
                'business_models': ['B2C', 'E-commerce', 'Retail'],
                'confidence_weight': 0.85
            },
            'hospitality': {
                'keywords': ['hotel', 'restaurant', 'tourism', 'travel', 'hospitality', 'catering', 'resort'],
                'indicators': ['chef', 'manager', 'receptionist', 'concierge', 'waiter', 'host'],
                'business_models': ['B2C', 'Hospitality', 'Tourism'],
                'confidence_weight': 0.9
            },
            'manufacturing': {
                'keywords': ['manufacturing', 'factory', 'production', 'industrial', 'supply chain', 'logistics'],
                'indicators': ['production manager', 'engineer', 'operator', 'supervisor', 'quality control'],
                'business_models': ['B2B', 'Manufacturing', 'Industrial'],
                'confidence_weight': 0.85
            },
            'consulting': {
                'keywords': ['consulting', 'advisory', 'strategy', 'management', 'professional services'],
                'indicators': ['consultant', 'advisor', 'partner', 'principal', 'analyst', 'strategist'],
                'business_models': ['B2B', 'Professional Services', 'Consulting'],
                'confidence_weight': 0.8
            },
            'education': {
                'keywords': ['education', 'training', 'university', 'school', 'learning', 'academic'],
                'indicators': ['teacher', 'professor', 'instructor', 'principal', 'dean', 'educator'],
                'business_models': ['B2C', 'Education', 'Training'],
                'confidence_weight': 0.85
            }
        }
    
    def _initialize_industry_keywords(self) -> Dict[str, List[str]]:
        """Initialize industry-specific keywords"""
        return {
            'b2b_indicators': ['enterprise', 'business', 'corporate', 'professional', 'industrial', 'wholesale'],
            'b2c_indicators': ['consumer', 'customer', 'personal', 'individual', 'retail', 'family'],
            'startup_indicators': ['startup', 'founded', 'innovation', 'disruptive', 'emerging', 'new'],
            'enterprise_indicators': ['enterprise', 'corporation', 'multinational', 'global', 'headquarters'],
            'sme_indicators': ['small business', 'local', 'family business', 'independent', 'boutique']
        }
    
    def classify_business_type(self, data_points: List[Dict[str, Any]]) -> Tuple[str, float, Dict[str, Any]]:
        """Classify business type using AI analysis"""
        # Combine all text data for analysis
        combined_text = self._extract_text_content(data_points)
        
        # Score each business type
        type_scores = {}
        detailed_analysis = {}
        
        for business_type, patterns in self.business_patterns.items():
            score = self._calculate_business_type_score(combined_text, patterns)
            type_scores[business_type] = score
            detailed_analysis[business_type] = {
                'score': score,
                'matched_keywords': self._find_matching_keywords(combined_text, patterns['keywords']),
                'matched_indicators': self._find_matching_keywords(combined_text, patterns['indicators'])
            }
        
        # Determine best match
        best_type = max(type_scores, key=type_scores.get)
        confidence = type_scores[best_type]
        
        # Apply confidence adjustments
        confidence *= self.business_patterns[best_type]['confidence_weight']
        
        # Additional context analysis
        context_analysis = self._analyze_business_context(combined_text, data_points)
        
        return best_type, confidence, {
            'detailed_scores': detailed_analysis,
            'context_analysis': context_analysis,
            'confidence_factors': self._get_confidence_factors(best_type, combined_text)
        }
    
    def _extract_text_content(self, data_points: List[Dict[str, Any]]) -> str:
        """Extract all text content from data points"""
        text_parts = []
        
        for data_point in data_points:
            # Extract various text fields
            text_fields = ['value', 'description', 'bio', 'title', 'snippet', 'content', 'name']
            for field in text_fields:
                if field in data_point and data_point[field]:
                    text_parts.append(str(data_point[field]))
            
            # Extract from nested data
            if 'context' in data_point and isinstance(data_point['context'], dict):
                for key, value in data_point['context'].items():
                    if isinstance(value, str):
                        text_parts.append(value)
        
        return ' '.join(text_parts).lower()
    
    def _calculate_business_type_score(self, text: str, patterns: Dict[str, Any]) -> float:
        """Calculate score for a specific business type"""
        score = 0.0
        total_weight = 0.0
        
        # Keyword matching
        keyword_matches = sum(1 for keyword in patterns['keywords'] if keyword in text)
        keyword_score = keyword_matches / len(patterns['keywords'])
        score += keyword_score * 0.6
        total_weight += 0.6
        
        # Indicator matching
        indicator_matches = sum(1 for indicator in patterns['indicators'] if indicator in text)
        indicator_score = indicator_matches / len(patterns['indicators'])
        score += indicator_score * 0.4
        total_weight += 0.4
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _find_matching_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Find matching keywords in text"""
        return [keyword for keyword in keywords if keyword in text]
    
    def _analyze_business_context(self, text: str, data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze business context and characteristics"""
        context = {
            'target_audience': self._determine_target_audience(text),
            'business_model': self._infer_business_model(text),
            'company_size': self._estimate_company_size(text, data_points),
            'maturity_level': self._assess_business_maturity(text),
            'geographic_scope': self._determine_geographic_scope(text, data_points)
        }
        
        return context
    
    def _determine_target_audience(self, text: str) -> str:
        """Determine target audience (B2B, B2C, etc.)"""
        b2b_score = sum(1 for indicator in self.industry_keywords['b2b_indicators'] if indicator in text)
        b2c_score = sum(1 for indicator in self.industry_keywords['b2c_indicators'] if indicator in text)
        
        if b2b_score > b2c_score:
            return 'B2B'
        elif b2c_score > b2b_score:
            return 'B2C'
        else:
            return 'Mixed'
    
    def _infer_business_model(self, text: str) -> str:
        """Infer business model from text analysis"""
        models = {
            'saas': ['saas', 'software as a service', 'subscription', 'cloud platform'],
            'marketplace': ['marketplace', 'platform', 'connect', 'network'],
            'ecommerce': ['ecommerce', 'online store', 'shopping', 'cart'],
            'consulting': ['consulting', 'advisory', 'services', 'expertise'],
            'manufacturing': ['manufacturing', 'production', 'factory', 'assembly']
        }
        
        model_scores = {}
        for model, keywords in models.items():
            score = sum(1 for keyword in keywords if keyword in text)
            model_scores[model] = score
        
        return max(model_scores, key=model_scores.get) if model_scores else 'traditional'
    
    def _estimate_company_size(self, text: str, data_points: List[Dict[str, Any]]) -> str:
        """Estimate company size"""
        # Count employees found
        employee_count = len([dp for dp in data_points if dp.get('data_type') == 'person_profile'])
        
        # Look for size indicators in text
        if any(indicator in text for indicator in ['startup', 'small business', 'boutique']):
            return 'small (1-50)'
        elif any(indicator in text for indicator in ['medium', 'growing', 'expanding']):
            return 'medium (51-500)'
        elif any(indicator in text for indicator in ['enterprise', 'corporation', 'multinational']):
            return 'large (500+)'
        elif employee_count > 20:
            return 'medium-large (100+)'
        elif employee_count > 5:
            return 'small-medium (10-100)'
        else:
            return 'small (1-50)'
    
    def _assess_business_maturity(self, text: str) -> str:
        """Assess business maturity level"""
        if any(indicator in text for indicator in self.industry_keywords['startup_indicators']):
            return 'startup'
        elif any(indicator in text for indicator in ['established', 'founded', 'years', 'experience']):
            return 'established'
        else:
            return 'mature'
    
    def _determine_geographic_scope(self, text: str, data_points: List[Dict[str, Any]]) -> str:
        """Determine geographic scope of business"""
        locations = []
        for dp in data_points:
            if dp.get('geographic_location'):
                locations.append(dp['geographic_location'])
        
        unique_locations = set(locations)
        
        if len(unique_locations) > 5:
            return 'international'
        elif len(unique_locations) > 2:
            return 'regional'
        else:
            return 'local'
    
    def _get_confidence_factors(self, business_type: str, text: str) -> List[str]:
        """Get factors that contribute to confidence in classification"""
        factors = []
        
        patterns = self.business_patterns[business_type]
        matched_keywords = self._find_matching_keywords(text, patterns['keywords'])
        matched_indicators = self._find_matching_keywords(text, patterns['indicators'])
        
        if len(matched_keywords) > 3:
            factors.append(f"Strong keyword alignment ({len(matched_keywords)} matches)")
        
        if len(matched_indicators) > 2:
            factors.append(f"Clear industry indicators ({len(matched_indicators)} matches)")
        
        if business_type in ['technology', 'healthcare', 'finance']:
            factors.append("High-confidence industry with clear patterns")
        
        return factors

class PersonnelAnalyzer:
    """Analyze personnel and organizational structure"""
    
    def __init__(self):
        self.role_hierarchy = self._initialize_role_hierarchy()
        self.decision_maker_patterns = self._initialize_decision_maker_patterns()
    
    def _initialize_role_hierarchy(self) -> Dict[str, int]:
        """Initialize role hierarchy for importance scoring"""
        return {
            'ceo': 100, 'chief executive': 100, 'president': 95, 'founder': 90,
            'cto': 85, 'cfo': 85, 'coo': 85, 'chief': 80,
            'vice president': 75, 'vp': 75, 'director': 70, 'head of': 65,
            'senior manager': 60, 'manager': 50, 'lead': 45, 'senior': 40,
            'coordinator': 30, 'specialist': 25, 'analyst': 20, 'associate': 15
        }
    
    def _initialize_decision_maker_patterns(self) -> Dict[str, List[str]]:
        """Initialize decision maker identification patterns"""
        return {
            'executive': ['ceo', 'president', 'founder', 'chief executive', 'managing director'],
            'senior_management': ['cto', 'cfo', 'coo', 'vp', 'vice president', 'director'],
            'department_heads': ['head of', 'department manager', 'team lead', 'senior manager'],
            'procurement': ['procurement', 'purchasing', 'buyer', 'vendor management'],
            'hr_decision': ['hr manager', 'human resources', 'talent acquisition', 'recruiting'],
            'technical_decision': ['cto', 'technical director', 'engineering manager', 'it director']
        }
    
    def analyze_personnel_structure(self, personnel_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze organizational structure and identify key personnel"""
        
        if not personnel_data:
            return {
                'decision_makers': [],
                'key_personnel': [],
                'organizational_structure': {},
                'personnel_insights': []
            }
        
        # Classify and score personnel
        classified_personnel = self._classify_personnel(personnel_data)
        
        # Identify decision makers
        decision_makers = self._identify_decision_makers(classified_personnel)
        
        # Analyze organizational structure
        org_structure = self._analyze_organizational_structure(classified_personnel)
        
        # Generate insights
        insights = self._generate_personnel_insights(classified_personnel, decision_makers)
        
        return {
            'decision_makers': decision_makers,
            'key_personnel': classified_personnel[:10],  # Top 10
            'organizational_structure': org_structure,
            'personnel_insights': insights,
            'total_personnel_found': len(personnel_data),
            'decision_maker_count': len(decision_makers),
            'department_coverage': len(org_structure.get('departments', {}))
        }
    
    def _classify_personnel(self, personnel_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classify and score personnel by importance"""
        classified = []
        
        for person in personnel_data:
            # Extract title and calculate importance
            title = person.get('title', '').lower()
            name = person.get('name', '')
            
            # Calculate importance score
            importance_score = self._calculate_importance_score(title)
            
            # Determine department
            department = self._determine_department(title)
            
            # Assess decision making power
            decision_power = self._assess_decision_power(title)
            
            classified_person = {
                'name': name,
                'title': person.get('title', ''),
                'normalized_title': title,
                'importance_score': importance_score,
                'department': department,
                'decision_power': decision_power,
                'contact_info': person.get('contact_info', {}),
                'profile_url': person.get('profile_url', ''),
                'location': person.get('location', ''),
                'confidence': person.get('confidence', 0.5),
                'original_data': person
            }
            
            classified.append(classified_person)
        
        # Sort by importance score
        return sorted(classified, key=lambda x: x['importance_score'], reverse=True)
    
    def _calculate_importance_score(self, title: str) -> int:
        """Calculate importance score for a role"""
        score = 10  # Base score
        
        # Check hierarchy
        for role, role_score in self.role_hierarchy.items():
            if role in title:
                score = max(score, role_score)
        
        # Additional scoring factors
        if 'senior' in title:
            score += 10
        if 'lead' in title:
            score += 8
        if 'principal' in title:
            score += 12
        
        return score
    
    def _determine_department(self, title: str) -> str:
        """Determine department from title"""
        departments = {
            'executive': ['ceo', 'president', 'founder', 'chief'],
            'technology': ['cto', 'engineering', 'developer', 'technical', 'it', 'software'],
            'finance': ['cfo', 'finance', 'accounting', 'controller', 'treasurer'],
            'operations': ['coo', 'operations', 'production', 'manufacturing'],
            'sales': ['sales', 'business development', 'account', 'revenue'],
            'marketing': ['marketing', 'brand', 'advertising', 'communications'],
            'hr': ['hr', 'human resources', 'talent', 'recruiting', 'people'],
            'legal': ['legal', 'counsel', 'compliance', 'regulatory'],
            'product': ['product', 'design', 'user experience', 'ux']
        }
        
        for dept, keywords in departments.items():
            if any(keyword in title for keyword in keywords):
                return dept
        
        return 'other'
    
    def _assess_decision_power(self, title: str) -> str:
        """Assess decision making power level"""
        if any(pattern in title for pattern in self.decision_maker_patterns['executive']):
            return 'high'
        elif any(pattern in title for pattern in self.decision_maker_patterns['senior_management']):
            return 'medium-high'
        elif any(pattern in title for pattern in self.decision_maker_patterns['department_heads']):
            return 'medium'
        else:
            return 'low'
    
    def _identify_decision_makers(self, classified_personnel: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify key decision makers"""
        decision_makers = []
        
        for person in classified_personnel:
            if person['decision_power'] in ['high', 'medium-high']:
                decision_makers.append({
                    'name': person['name'],
                    'title': person['title'],
                    'department': person['department'],
                    'decision_power': person['decision_power'],
                    'importance_score': person['importance_score'],
                    'contact_info': person['contact_info'],
                    'profile_url': person['profile_url'],
                    'influence_areas': self._determine_influence_areas(person['title']),
                    'contact_priority': self._calculate_contact_priority(person)
                })
        
        return decision_makers[:15]  # Top 15 decision makers
    
    def _determine_influence_areas(self, title: str) -> List[str]:
        """Determine areas of influence for a decision maker"""
        influence_map = {
            'ceo': ['strategic decisions', 'budget approval', 'partnerships', 'hiring'],
            'cto': ['technology decisions', 'technical partnerships', 'system purchases'],
            'cfo': ['financial decisions', 'budget allocation', 'vendor payments'],
            'coo': ['operational decisions', 'process improvements', 'vendor management'],
            'sales': ['sales tools', 'crm systems', 'sales partnerships'],
            'marketing': ['marketing tools', 'advertising', 'brand partnerships'],
            'hr': ['hr systems', 'recruiting tools', 'employee benefits']
        }
        
        title_lower = title.lower()
        areas = []
        
        for role, influences in influence_map.items():
            if role in title_lower:
                areas.extend(influences)
        
        return areas if areas else ['general business decisions']
    
    def _calculate_contact_priority(self, person: Dict[str, Any]) -> str:
        """Calculate priority for contacting this person"""
        score = person['importance_score']
        
        # Adjust based on contact availability
        if person['contact_info'].get('email'):
            score += 10
        if person['contact_info'].get('phone'):
            score += 5
        
        # Adjust based on decision power
        power_bonus = {'high': 20, 'medium-high': 15, 'medium': 10, 'low': 0}
        score += power_bonus.get(person['decision_power'], 0)
        
        if score >= 80:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'
    
    def _analyze_organizational_structure(self, classified_personnel: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze organizational structure"""
        departments = defaultdict(list)
        hierarchy_levels = defaultdict(int)
        
        for person in classified_personnel:
            departments[person['department']].append(person)
            
            # Count hierarchy levels
            if person['importance_score'] >= 80:
                hierarchy_levels['executive'] += 1
            elif person['importance_score'] >= 60:
                hierarchy_levels['senior_management'] += 1
            elif person['importance_score'] >= 40:
                hierarchy_levels['middle_management'] += 1
            else:
                hierarchy_levels['staff'] += 1
        
        return {
            'departments': dict(departments),
            'hierarchy_levels': dict(hierarchy_levels),
            'largest_department': max(departments.items(), key=lambda x: len(x[1]))[0] if departments else None,
            'management_ratio': (hierarchy_levels['executive'] + hierarchy_levels['senior_management']) / max(len(classified_personnel), 1)
        }
    
    def _generate_personnel_insights(self, classified_personnel: List[Dict[str, Any]], decision_makers: List[Dict[str, Any]]) -> List[str]:
        """Generate insights about personnel structure"""
        insights = []
        
        if len(decision_makers) > 5:
            insights.append(f"Well-represented leadership team with {len(decision_makers)} decision makers identified")
        elif len(decision_makers) > 0:
            insights.append(f"Limited leadership visibility with {len(decision_makers)} decision makers found")
        
        # Department analysis
        departments = defaultdict(int)
        for person in classified_personnel:
            departments[person['department']] += 1
        
        if len(departments) > 4:
            insights.append("Diverse organizational structure across multiple departments")
        
        # Contact availability
        contactable = sum(1 for p in classified_personnel if p['contact_info'].get('email') or p['contact_info'].get('phone'))
        if contactable > len(classified_personnel) * 0.5:
            insights.append(f"Good contact availability - {contactable} out of {len(classified_personnel)} personnel have contact information")
        
        return insights

class ContactQualityAnalyzer:
    """Analyze and score contact information quality"""
    
    def __init__(self):
        self.email_patterns = {
            'business_domains': ['.com', '.org', '.net', '.sa', '.ae', '.gov'],
            'personal_domains': ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'],
            'suspicious_patterns': ['noreply', 'donotreply', 'test', 'temp'],
            'executive_patterns': ['ceo@', 'president@', 'founder@', 'director@']
        }
        
        self.phone_patterns = {
            'saudi_mobile': re.compile(r'^\+?966[5][0-9]{8}$'),
            'saudi_landline': re.compile(r'^\+?966[1-4][0-9]{7}$'),
            'uae_mobile': re.compile(r'^\+?971[5][0-9]{8}$'),
            'international': re.compile(r'^\+[1-9][0-9]{1,14}$')
        }

    def analyze_contact_quality(self, contact_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze quality of contact information"""
        if not contact_data:
            return self._get_empty_analysis()

        email_analysis = self._analyze_emails(contact_data)
        phone_analysis = self._analyze_phones(contact_data)
        overall_quality = self._calculate_overall_quality(email_analysis, phone_analysis)
        
        return {
            'email_analysis': email_analysis,
            'phone_analysis': phone_analysis,
            'overall_quality_score': overall_quality,
            'best_contact_methods': self._determine_best_contact_methods(email_analysis, phone_analysis),
            'verified_contacts': self._identify_verified_contacts(contact_data),
            'contact_recommendations': self._generate_contact_recommendations(email_analysis, phone_analysis)
        }

    def _get_empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure when no data is provided"""
        return {
            'email_analysis': {'total_emails': 0, 'quality_score': 0, 'business_emails': 0},
            'phone_analysis': {'total_phones': 0, 'quality_score': 0, 'mobile_count': 0},
            'overall_quality_score': 0,
            'best_contact_methods': ['general_inquiry'],
            'verified_contacts': [],
            'contact_recommendations': ['Additional research needed to find contact information']
        }

    def _analyze_emails(self, contact_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze email quality"""
        emails = [item for item in contact_data if item.get('type') == 'email']
        
        if not emails:
            return {'total_emails': 0, 'quality_score': 0, 'business_emails': 0}
        
        counts = {
            'business_emails': 0,
            'personal_emails': 0,
            'suspicious_emails': 0,
            'executive_emails': 0
        }
        
        for email_item in emails:
            email = email_item.get('value', '').lower()
            self._categorize_email(email, counts)
        
        quality_score = self._calculate_email_quality(counts, len(emails))
        
        return {
            'total_emails': len(emails),
            **counts,
            'quality_score': quality_score
        }

    def _categorize_email(self, email: str, counts: Dict[str, int]) -> None:
        """Categorize email and update counts"""
        if any(domain in email for domain in self.email_patterns['personal_domains']):
            counts['personal_emails'] += 1
        else:
            counts['business_emails'] += 1
        
        if any(pattern in email for pattern in self.email_patterns['suspicious_patterns']):
            counts['suspicious_emails'] += 1
        
        if any(pattern in email for pattern in self.email_patterns['executive_patterns']):
            counts['executive_emails'] += 1

    def _calculate_email_quality(self, counts: Dict[str, int], total_emails: int) -> float:
        """Calculate email quality score"""
        quality_score = (
            counts['business_emails'] * 0.8 + 
            counts['executive_emails'] * 1.0 - 
            counts['suspicious_emails'] * 0.5
        ) / total_emails
        return max(0, min(1, quality_score))
    
    def _analyze_phones(self, contact_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze phone number quality"""
        phones = [item for item in contact_data if item.get('type') == 'phone']
        
        if not phones:
            return {'total_phones': 0, 'quality_score': 0, 'mobile_count': 0}
        
        mobile_count = 0
        landline_count = 0
        international_count = 0
        valid_format_count = 0
        
        for phone_item in phones:
            phone = phone_item.get('value', '').strip()
            
            # Clean phone number
            cleaned_phone = re.sub(r'[^\d+]', '', phone)
            
            # Check patterns
            if self.phone_patterns['saudi_mobile'].match(cleaned_phone):
                mobile_count += 1
                valid_format_count += 1
            elif self.phone_patterns['saudi_landline'].match(cleaned_phone):
                landline_count += 1
                valid_format_count += 1
            elif self.phone_patterns['uae_mobile'].match(cleaned_phone):
                mobile_count += 1
                valid_format_count += 1
            elif self.phone_patterns['international'].match(cleaned_phone):
                international_count += 1
                valid_format_count += 1
        
        quality_score = valid_format_count / len(phones) if phones else 0
        
        return {
            'total_phones': len(phones),
            'mobile_count': mobile_count,
            'landline_count': landline_count,
            'international_count': international_count,
            'valid_format_count': valid_format_count,
            'quality_score': quality_score
        }
    
    def _calculate_overall_quality(self, email_analysis: Dict, phone_analysis: Dict) -> float:
        """Calculate overall contact quality score"""
        email_weight = 0.6
        phone_weight = 0.4
        
        email_score = email_analysis.get('quality_score', 0) * email_weight
        phone_score = phone_analysis.get('quality_score', 0) * phone_weight
        
        return email_score + phone_score
    
    def _determine_best_contact_methods(self, email_analysis: Dict, phone_analysis: Dict) -> List[str]:
        """Determine best contact methods"""
        methods = []
        
        if email_analysis.get('business_emails', 0) > 0:
            methods.append('business_email')
        
        if email_analysis.get('executive_emails', 0) > 0:
            methods.append('executive_email')
        
        if phone_analysis.get('mobile_count', 0) > 0:
            methods.append('mobile_phone')
        
        if phone_analysis.get('landline_count', 0) > 0:
            methods.append('office_phone')
        
        return methods if methods else ['general_inquiry']
    
    def _identify_verified_contacts(self, contact_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify high-confidence verified contacts"""
        verified = []
        
        for contact in contact_data:
            confidence = contact.get('confidence', 0)
            contact_type = contact.get('type', '')
            
            # High confidence threshold
            if confidence >= 0.8:
                verified.append({
                    'type': contact_type,
                    'value': contact.get('value', ''),
                    'confidence': confidence,
                    'source': contact.get('source_method', ''),
                    'verification_factors': self._get_verification_factors(contact)
                })
        
        return verified
    
    def _get_verification_factors(self, contact: Dict[str, Any]) -> List[str]:
        """Get factors that verify contact quality"""
        factors = []
        
        if contact.get('confidence', 0) >= 0.9:
            factors.append('High confidence source')
        
        if contact.get('source_method') in ['linkedin_profile', 'company_website']:
            factors.append('Professional source')
        
        if contact.get('type') == 'email' and '@' in contact.get('value', ''):
            email = contact['value'].lower()
            if not any(domain in email for domain in self.email_patterns['personal_domains']):
                factors.append('Business email domain')
        
        return factors
    
    def _generate_contact_recommendations(self, email_analysis: Dict, phone_analysis: Dict) -> List[str]:
        """Generate recommendations for contact strategy"""
        recommendations = []
        
        if email_analysis.get('business_emails', 0) > 0:
            recommendations.append("Prioritize business email addresses for professional outreach")
        
        if email_analysis.get('executive_emails', 0) > 0:
            recommendations.append("Direct executive email contacts available for high-level discussions")
        
        if phone_analysis.get('mobile_count', 0) > 0:
            recommendations.append("Mobile numbers available for urgent communications")
        
        if email_analysis.get('quality_score', 0) < 0.5:
            recommendations.append("Consider additional research to find higher-quality contact information")
        
        return recommendations

class IntelligenceAnalyzer:
    """Main AI-powered intelligence analyzer"""
    
    def __init__(self):
        self.business_classifier = BusinessTypeClassifier()
        self.personnel_analyzer = PersonnelAnalyzer()
        self.contact_analyzer = ContactQualityAnalyzer()
        
    async def analyze_intelligence_batch(self, results: List[Dict[str, Any]]) -> IntelligenceAnalysis:
        """
        Comprehensive AI analysis of intelligence batch
        """
        start_time = datetime.now()
        logger.info(f"Starting AI analysis of {len(results)} intelligence items")
        
        # Organize data by type
        organized_data = self._organize_data_by_type(results)
        
        # Business type classification
        business_type, business_confidence, business_details = self.business_classifier.classify_business_type(results)
        
        # Personnel analysis
        personnel_analysis = self.personnel_analyzer.analyze_personnel_structure(
            organized_data.get('person_profiles', [])
        )
        
        # Contact quality analysis
        contact_analysis = self.contact_analyzer.analyze_contact_quality(
            organized_data.get('contact_info', [])
        )
        
        # Geographic analysis
        geographic_analysis = self._analyze_geographic_distribution(results)
        
        # Technology and digital presence analysis
        tech_analysis = self._analyze_technology_presence(results)
        
        # Market intelligence analysis
        market_analysis = self._analyze_market_intelligence(results, business_type)
        
        # Risk assessment
        risk_assessment = self._assess_information_risks(results, contact_analysis)
        
        # Generate insights and recommendations
        insights = self._generate_comprehensive_insights(
            business_details, personnel_analysis, contact_analysis, 
            geographic_analysis, tech_analysis, market_analysis
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Create comprehensive analysis
        analysis = IntelligenceAnalysis(
            investigation_id=self._generate_analysis_id(),
            target_identifier=self._extract_target_identifier(results),
            analysis_timestamp=datetime.now(),
            
            # Business Analysis
            business_type=business_type,
            business_confidence=business_confidence,
            industry_classification=business_details.get('context_analysis', {}).get('business_model', 'traditional'),
            company_size_estimate=business_details.get('context_analysis', {}).get('company_size', 'unknown'),
            target_audience_type=business_details.get('context_analysis', {}).get('target_audience', 'mixed'),
            
            # Geographic Analysis
            geographic_distribution=geographic_analysis['distribution'],
            primary_location=geographic_analysis['primary_location'],
            secondary_locations=geographic_analysis['secondary_locations'],
            geographic_coverage=geographic_analysis['coverage'],
            
            # Personnel Analysis
            decision_makers=personnel_analysis['decision_makers'],
            key_personnel=personnel_analysis['key_personnel'],
            organizational_structure=personnel_analysis['organizational_structure'],
            personnel_count_estimate=personnel_analysis['total_personnel_found'],
            
            # Contact Intelligence
            contact_quality_scores={
                'email_quality': contact_analysis['email_analysis']['quality_score'],
                'phone_quality': contact_analysis['phone_analysis']['quality_score'],
                'overall_quality': contact_analysis['overall_quality_score']
            },
            verified_contacts=contact_analysis['verified_contacts'],
            contact_channels=self._extract_contact_channels(organized_data),
            best_contact_methods=contact_analysis['best_contact_methods'],
            
            # Market Intelligence
            competitive_landscape=market_analysis['competitive_landscape'],
            market_position=market_analysis['market_position'],
            growth_indicators=market_analysis['growth_indicators'],
            business_opportunities=market_analysis['opportunities'],
            
            # Technology & Digital Presence
            technology_stack=tech_analysis['technology_stack'],
            digital_maturity=tech_analysis['digital_maturity'],
            online_presence_strength=tech_analysis['online_presence_score'],
            social_media_activity=tech_analysis['social_media_analysis'],
            
            # Risk Assessment
            data_quality_score=risk_assessment['data_quality_score'],
            information_completeness=risk_assessment['completeness_score'],
            verification_status=risk_assessment['verification_status'],
            confidence_factors=business_details.get('confidence_factors', []),
            risk_indicators=risk_assessment['risk_indicators'],
            
            # Insights and Recommendations
            key_insights=insights['key_insights'],
            actionable_recommendations=insights['recommendations'],
            follow_up_opportunities=insights['follow_up_opportunities'],
            intelligence_gaps=insights['intelligence_gaps'],
            
            # Metadata
            total_data_points=len(results),
            sources_analyzed=list(set(item.get('source_method', 'unknown') for item in results)),
            analysis_methods_used=['business_classification', 'personnel_analysis', 'contact_analysis', 'geographic_analysis'],
            processing_time_seconds=processing_time
        )
        
        logger.info(f"AI analysis completed in {processing_time:.2f} seconds")
        return analysis
    
    def _organize_data_by_type(self, results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Organize data by type for targeted analysis"""
        organized = defaultdict(list)
        
        for item in results:
            data_type = item.get('data_type', 'unknown')
            organized[data_type].append(item)
        
        return dict(organized)
    
    def _generate_analysis_id(self) -> str:
        """Generate unique analysis ID"""
        return f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(datetime.now().microsecond)) % 10000}"
    
    def _extract_target_identifier(self, results: List[Dict[str, Any]]) -> str:
        """Extract target identifier from results"""
        # Look for common identifiers in the data
        for item in results:
            if 'context' in item and isinstance(item['context'], dict):
                if 'target' in item['context']:
                    return item['context']['target']
        
        # Fallback to first meaningful value
        for item in results:
            if item.get('value') and len(item['value']) > 5:
                return item['value'][:50]  # Truncate for readability
        
        return f"investigation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _analyze_geographic_distribution(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze geographic distribution of intelligence"""
        locations = []
        
        for item in results:
            if item.get('geographic_location'):
                locations.append(item['geographic_location'])
            
            # Extract locations from text content
            value = item.get('value', '')
            if isinstance(value, str):
                # Simple location extraction
                location_patterns = [
                    r'\b(riyadh|jeddah|dubai|abu dhabi|doha|kuwait|manama|muscat)\b',
                    r'\b(saudi arabia|uae|qatar|kuwait|bahrain|oman)\b'
                ]
                
                for pattern in location_patterns:
                    matches = re.findall(pattern, value.lower())
                    locations.extend(matches)
        
        # Count occurrences
        location_counts = Counter(locations)
        
        # Determine primary and secondary locations
        primary_location = location_counts.most_common(1)[0][0] if location_counts else 'unknown'
        secondary_locations = [loc for loc, count in location_counts.most_common(5)[1:]]
        
        # Determine coverage
        unique_locations = len(set(locations))
        if unique_locations > 5:
            coverage = 'international'
        elif unique_locations > 2:
            coverage = 'regional'
        else:
            coverage = 'local'
        
        return {
            'distribution': dict(location_counts),
            'primary_location': primary_location,
            'secondary_locations': secondary_locations,
            'coverage': coverage,
            'total_location_mentions': len(locations)
        }
    
    def _analyze_technology_presence(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze technology stack and digital presence"""
        tech_keywords = {
            'cloud': ['aws', 'azure', 'google cloud', 'cloud'],
            'programming': ['python', 'java', 'javascript', 'react', 'angular'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'oracle'],
            'platforms': ['salesforce', 'hubspot', 'microsoft', 'google workspace'],
            'security': ['ssl', 'https', 'encryption', 'security'],
            'mobile': ['ios', 'android', 'mobile app', 'smartphone']
        }
        
        detected_tech = defaultdict(list)
        social_media_mentions = 0
        website_references = 0
        
        for item in results:
            value = item.get('value', '').lower()
            
            # Count social media and web presence
            if any(platform in value for platform in ['linkedin', 'twitter', 'facebook', 'instagram']):
                social_media_mentions += 1
            
            if any(indicator in value for indicator in ['website', 'www.', 'http', '.com']):
                website_references += 1
            
            # Detect technology
            for category, keywords in tech_keywords.items():
                for keyword in keywords:
                    if keyword in value:
                        detected_tech[category].append(keyword)
        
        # Calculate digital maturity
        tech_score = len(detected_tech)
        social_score = min(social_media_mentions / 4, 1)  # Normalize to 0-1
        web_score = min(website_references / 3, 1)
        
        digital_maturity_score = (tech_score * 0.5 + social_score * 0.3 + web_score * 0.2)
        
        if digital_maturity_score > 0.7:
            digital_maturity = 'advanced'
        elif digital_maturity_score > 0.4:
            digital_maturity = 'moderate'
        else:
            digital_maturity = 'basic'
        
        return {
            'technology_stack': list(set([tech for techs in detected_tech.values() for tech in techs])),
            'digital_maturity': digital_maturity,
            'online_presence_score': min(digital_maturity_score, 1.0),
            'social_media_analysis': {
                'mentions': social_media_mentions,
                'platforms_detected': social_media_mentions > 0
            },
            'technology_categories': dict(detected_tech)
        }
    
    def _analyze_market_intelligence(self, results: List[Dict[str, Any]], business_type: str) -> Dict[str, Any]:
        """Analyze market intelligence and business opportunities"""
        growth_indicators = []
        opportunities = []
        competitive_signals = []
        
        # Analyze text content for business intelligence
        combined_text = ' '.join([item.get('value', '') for item in results if isinstance(item.get('value'), str)]).lower()
        
        # Growth indicators
        growth_keywords = ['growing', 'expanding', 'new', 'recent', 'launched', 'funding', 'investment', 'hiring']
        for keyword in growth_keywords:
            if keyword in combined_text:
                growth_indicators.append(f"{keyword.title()} activity detected")
        
        # Business opportunities
        opportunity_patterns = {
            'technology': ['digital transformation', 'automation', 'ai implementation'],
            'healthcare': ['telemedicine', 'digital health', 'patient management'],
            'finance': ['fintech solutions', 'digital banking', 'payment systems'],
            'retail': ['e-commerce', 'online presence', 'customer experience']
        }
        
        if business_type in opportunity_patterns:
            for opportunity in opportunity_patterns[business_type]:
                if any(word in combined_text for word in opportunity.split()):
                    opportunities.append(f"{opportunity.title()} opportunity")
        
        # Competitive landscape
        competitor_keywords = ['competitor', 'rival', 'alternative', 'similar', 'market leader']
        competitive_mentions = sum(1 for keyword in competitor_keywords if keyword in combined_text)
        
        if competitive_mentions > 2:
            market_position = 'competitive market'
        elif competitive_mentions > 0:
            market_position = 'moderate competition'
        else:
            market_position = 'limited competition visible'
        
        return {
            'competitive_landscape': {
                'competition_level': market_position,
                'competitive_mentions': competitive_mentions
            },
            'market_position': market_position,
            'growth_indicators': growth_indicators if growth_indicators else ['No clear growth signals detected'],
            'opportunities': opportunities if opportunities else ['Standard business opportunities apply']
        }
    
    def _assess_information_risks(self, results: List[Dict[str, Any]], contact_analysis: Dict) -> Dict[str, Any]:
        """Assess risks and quality of information"""
        
        # Calculate data quality score
        confidence_scores = [item.get('confidence', 0.5) for item in results]
        avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0.5
        
        # Information completeness
        expected_data_types = ['contact_info', 'business_info', 'person_profiles', 'social_profiles']
        found_data_types = set(item.get('data_type', 'unknown') for item in results)
        completeness = len(found_data_types.intersection(expected_data_types)) / len(expected_data_types)
        
        # Verification status
        verified_count = sum(1 for item in results if item.get('confidence', 0) >= 0.8)
        verification_rate = verified_count / len(results) if results else 0
        
        verification_status = {
            'verified_items': verified_count,
            'total_items': len(results),
            'verification_rate': verification_rate
        }
        
        # Risk indicators
        risk_indicators = []
        
        if avg_confidence < 0.6:
            risk_indicators.append('Low average confidence in data sources')
        
        if completeness < 0.5:
            risk_indicators.append('Incomplete information coverage')
        
        if contact_analysis['overall_quality_score'] < 0.5:
            risk_indicators.append('Poor quality contact information')
        
        if len(results) < 10:
            risk_indicators.append('Limited data points for analysis')
        
        return {
            'data_quality_score': avg_confidence,
            'completeness_score': completeness,
            'verification_status': verification_status,
            'risk_indicators': risk_indicators if risk_indicators else ['No significant risks identified']
        }
    
    def _extract_contact_channels(self, organized_data: Dict[str, List]) -> List[str]:
        """Extract available contact channels"""
        channels = set()
        
        contact_data = organized_data.get('contact_info', [])
        for contact in contact_data:
            contact_type = contact.get('type', '')
            if contact_type == 'email':
                channels.add('email')
            elif contact_type == 'phone':
                channels.add('phone')
            elif contact_type == 'website':
                channels.add('website')
        
        # Check for social media profiles
        if 'social_profiles' in organized_data:
            channels.add('social_media')
        
        return list(channels)
    
    def _generate_comprehensive_insights(self, business_details: Dict, personnel_analysis: Dict, 
                                       contact_analysis: Dict, geographic_analysis: Dict,
                                       tech_analysis: Dict, market_analysis: Dict) -> Dict[str, List[str]]:
        """Generate comprehensive insights and recommendations"""
        
        insights = []
        recommendations = []
        follow_up_opportunities = []
        intelligence_gaps = []
        
        # Business insights
        business_type = business_details.get('context_analysis', {}).get('target_audience', 'mixed')
        if business_type == 'B2B':
            insights.append("B2B focused organization - decision making likely involves multiple stakeholders")
            recommendations.append("Target key decision makers and technical evaluators in sales process")
        elif business_type == 'B2C':
            insights.append("Consumer-focused business - marketing and customer experience are key")
            recommendations.append("Focus on customer-facing teams and marketing decision makers")
        
        # Personnel insights
        decision_makers_count = len(personnel_analysis.get('decision_makers', []))
        if decision_makers_count > 5:
            insights.append(f"Well-represented leadership team with {decision_makers_count} decision makers identified")
            follow_up_opportunities.append("Multiple entry points for business development")
        elif decision_makers_count > 0:
            insights.append(f"Limited leadership visibility - {decision_makers_count} key contacts found")
            intelligence_gaps.append("Additional research needed to identify more decision makers")
        
        # Contact quality insights
        contact_quality = contact_analysis.get('overall_quality_score', 0)
        if contact_quality > 0.7:
            insights.append("High-quality contact information available for direct outreach")
            recommendations.append("Proceed with direct contact strategy")
        elif contact_quality > 0.4:
            insights.append("Moderate contact quality - some verification recommended")
            recommendations.append("Verify contact information before major outreach campaigns")
        else:
            insights.append("Limited reliable contact information found")
            intelligence_gaps.append("Additional contact research required")
        
        # Geographic insights
        coverage = geographic_analysis.get('coverage', 'local')
        if coverage == 'international':
            insights.append("International presence - consider global market approach")
            recommendations.append("Tailor communications for international business context")
        elif coverage == 'regional':
            insights.append("Regional operations - understand local market dynamics")
        
        # Technology insights
        digital_maturity = tech_analysis.get('digital_maturity', 'basic')
        if digital_maturity == 'advanced':
            insights.append("Digitally mature organization with advanced technology adoption")
            recommendations.append("Leverage technology-focused value propositions")
        elif digital_maturity == 'basic':
            insights.append("Limited digital presence - potential for digital transformation opportunities")
            follow_up_opportunities.append("Digital transformation consulting or solutions")
        
        # Market insights
        growth_indicators = market_analysis.get('growth_indicators', [])
        if len(growth_indicators) > 2:
            insights.append("Multiple growth signals detected - organization likely in expansion mode")
            follow_up_opportunities.append("Growth-supporting solutions and services")
        
        return {
            'key_insights': insights,
            'recommendations': recommendations,
            'follow_up_opportunities': follow_up_opportunities,
            'intelligence_gaps': intelligence_gaps
        }
    
    async def quick_analysis(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Quick analysis for immediate insights"""
        if not results:
            return {'summary': {'total_analyzed': 0, 'business_type': 'Unknown'}}
        
        # Quick business type classification
        business_type, confidence, _ = self.business_classifier.classify_business_type(results)
        
        # Quick contact analysis
        contact_items = [item for item in results if item.get('data_type') == 'contact_info']
        contact_quality = len(contact_items) / max(len(results), 1)
        
        # Quick personnel count
        personnel_items = [item for item in results if item.get('data_type') == 'person_profile']
        
        return {
            'summary': {
                'total_analyzed': len(results),
                'business_type': business_type,
                'business_confidence': confidence,
                'contact_items_found': len(contact_items),
                'personnel_found': len(personnel_items),
                'contact_quality_estimate': contact_quality,
                'high_confidence_items': len([item for item in results if item.get('confidence', 0) >= 0.8])
            }
        }
    
    def export_analysis_report(self, analysis: IntelligenceAnalysis, format: str = 'json') -> str:
        """Export analysis report in specified format"""
        if format == 'json':
            return self._export_json_analysis(analysis)
        elif format == 'html':
            return self._export_html_analysis(analysis)
        else:
            return self._export_text_analysis(analysis)
    
    def _export_json_analysis(self, analysis: IntelligenceAnalysis) -> str:
        """Export analysis as JSON"""
        analysis_dict = asdict(analysis)
        
        # Convert datetime objects to strings
        analysis_dict['analysis_timestamp'] = analysis.analysis_timestamp.isoformat()
        
        filename = f"intelligence_analysis_{analysis.target_identifier.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        exports_dir = Path("data/exports")
        exports_dir.mkdir(exist_ok=True)
        
        with open(exports_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_dict, f, indent=2, ensure_ascii=False)
        
        return str(exports_dir / filename)
    
    def _export_html_analysis(self, analysis: IntelligenceAnalysis) -> str:
        """Export analysis as HTML report"""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Intelligence Analysis Report - {target}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #ecf0f1; border-radius: 3px; }}
        .high-score {{ background: #2ecc71; color: white; }}
        .medium-score {{ background: #f39c12; color: white; }}
        .low-score {{ background: #e74c3c; color: white; }}
        .insight {{ background: #3498db; color: white; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .recommendation {{ background: #27ae60; color: white; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        ul {{ list-style-type: none; padding-left: 0; }}
        li {{ margin: 5px 0; padding: 5px; background: #f8f9fa; border-left: 3px solid #007bff; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Intelligence Analysis Report</h1>
        <p>Target: {target}</p>
        <p>Analysis Date: {timestamp}</p>
        <p>Analysis ID: {analysis_id}</p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <div class="metric {business_confidence_class}">Business Type: {business_type} (Confidence: {business_confidence:.1%})</div>
        <div class="metric">Total Data Points: {total_data_points}</div>
        <div class="metric {data_quality_class}">Data Quality: {data_quality:.1%}</div>
        <div class="metric">Personnel Found: {personnel_count}</div>
    </div>
    
    <div class="section">
        <h2>Key Insights</h2>
        {insights_html}
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        {recommendations_html}
    </div>
    
    <div class="section">
        <h2>Contact Intelligence</h2>
        <p>Email Quality: {email_quality:.1%}</p>
        <p>Phone Quality: {phone_quality:.1%}</p>
        <p>Verified Contacts: {verified_contacts}</p>
        <p>Best Contact Methods: {best_methods}</p>
    </div>
    
    <div class="section">
        <h2>Decision Makers</h2>
        {decision_makers_html}
    </div>
    
    <div class="section">
        <h2>Geographic Analysis</h2>
        <p>Primary Location: {primary_location}</p>
        <p>Coverage: {geographic_coverage}</p>
        <p>Secondary Locations: {secondary_locations}</p>
    </div>
    
    <div class="section">
        <h2>Technology & Digital Presence</h2>
        <p>Digital Maturity: {digital_maturity}</p>
        <p>Online Presence Score: {online_presence:.1%}</p>
        <p>Technology Stack: {technology_stack}</p>
    </div>
    
    <div class="section">
        <h2>Follow-up Opportunities</h2>
        {opportunities_html}
    </div>
</body>
</html>
        """
        
        # Generate HTML content
        insights_html = ''.join([f'<div class="insight">{insight}</div>' for insight in analysis.key_insights])
        recommendations_html = ''.join([f'<div class="recommendation">{rec}</div>' for rec in analysis.actionable_recommendations])
        opportunities_html = '<ul>' + ''.join([f'<li>{opp}</li>' for opp in analysis.follow_up_opportunities]) + '</ul>'
        
        decision_makers_html = '<ul>'
        for dm in analysis.decision_makers[:5]:  # Top 5
            decision_makers_html += f'<li><strong>{dm.get("name", "N/A")}</strong> - {dm.get("title", "N/A")} ({dm.get("decision_power", "N/A")} influence)</li>'
        decision_makers_html += '</ul>'
        
        # Determine CSS classes for metrics
        business_confidence_class = 'high-score' if analysis.business_confidence > 0.8 else 'medium-score' if analysis.business_confidence > 0.5 else 'low-score'
        data_quality_class = 'high-score' if analysis.data_quality_score > 0.8 else 'medium-score' if analysis.data_quality_score > 0.5 else 'low-score'
        
        html_content = html_template.format(
            target=analysis.target_identifier,
            timestamp=analysis.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            analysis_id=analysis.investigation_id,
            business_type=analysis.business_type.title(),
            business_confidence=analysis.business_confidence,
            business_confidence_class=business_confidence_class,
            total_data_points=analysis.total_data_points,
            data_quality=analysis.data_quality_score,
            data_quality_class=data_quality_class,
            personnel_count=analysis.personnel_count_estimate,
            insights_html=insights_html,
            recommendations_html=recommendations_html,
            email_quality=analysis.contact_quality_scores.get('email_quality', 0),
            phone_quality=analysis.contact_quality_scores.get('phone_quality', 0),
            verified_contacts=len(analysis.verified_contacts),
            best_methods=', '.join(analysis.best_contact_methods),
            decision_makers_html=decision_makers_html,
            primary_location=analysis.primary_location,
            geographic_coverage=analysis.geographic_coverage,
            secondary_locations=', '.join(analysis.secondary_locations),
            digital_maturity=analysis.digital_maturity.title(),
            online_presence=analysis.online_presence_strength,
            technology_stack=', '.join(analysis.technology_stack[:5]),
            opportunities_html=opportunities_html
        )
        
        filename = f"intelligence_analysis_report_{analysis.target_identifier.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        exports_dir = Path("data/exports")
        exports_dir.mkdir(exist_ok=True)
        
        with open(exports_dir / filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(exports_dir / filename)
    
    def _export_text_analysis(self, analysis: IntelligenceAnalysis) -> str:
        """Export analysis as text summary"""
        summary = f"""
INTELLIGENCE ANALYSIS REPORT
============================

Target: {analysis.target_identifier}
Analysis Date: {analysis.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Investigation ID: {analysis.investigation_id}

EXECUTIVE SUMMARY
=================
Business Type: {analysis.business_type.title()} (Confidence: {analysis.business_confidence:.1%})
Industry: {analysis.industry_classification}
Target Audience: {analysis.target_audience_type}
Company Size: {analysis.company_size_estimate}
Geographic Coverage: {analysis.geographic_coverage}

DATA QUALITY METRICS
=====================
Total Data Points Analyzed: {analysis.total_data_points}
Data Quality Score: {analysis.data_quality_score:.1%}
Information Completeness: {analysis.information_completeness:.1%}
Verified Contacts: {len(analysis.verified_contacts)}

KEY INSIGHTS
============
{chr(10).join(f"• {insight}" for insight in analysis.key_insights)}

ACTIONABLE RECOMMENDATIONS
===========================
{chr(10).join(f"• {rec}" for rec in analysis.actionable_recommendations)}

CONTACT INTELLIGENCE
=====================
Email Quality Score: {analysis.contact_quality_scores.get('email_quality', 0):.1%}
Phone Quality Score: {analysis.contact_quality_scores.get('phone_quality', 0):.1%}
Overall Contact Quality: {analysis.contact_quality_scores.get('overall_quality', 0):.1%}
Best Contact Methods: {', '.join(analysis.best_contact_methods)}

DECISION MAKERS ({len(analysis.decision_makers)} found)
=============
{chr(10).join(f"• {dm.get('name', 'N/A')} - {dm.get('title', 'N/A')} ({dm.get('decision_power', 'N/A')} influence)" for dm in analysis.decision_makers[:10])}

FOLLOW-UP OPPORTUNITIES
=======================
{chr(10).join(f"• {opp}" for opp in analysis.follow_up_opportunities)}

INTELLIGENCE GAPS
==================
{chr(10).join(f"• {gap}" for gap in analysis.intelligence_gaps)}

PROCESSING SUMMARY
==================
Sources Analyzed: {', '.join(analysis.sources_analyzed)}
Processing Time: {analysis.processing_time_seconds:.2f} seconds
Analysis Methods: {', '.join(analysis.analysis_methods_used)}
        """
        
        filename = f"intelligence_analysis_summary_{analysis.target_identifier.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        exports_dir = Path("data/exports")
        exports_dir.mkdir(exist_ok=True)
        
        with open(exports_dir / filename, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        return str(exports_dir / filename)

# Example usage and testing
async def test_ai_analyzer():
    """Test the AI analyzer with sample data"""
    analyzer = IntelligenceAnalyzer()
    
    # Sample intelligence data
    sample_results = [
        {
            'data_type': 'business_profile',
            'value': 'Technology company specializing in AI and software development',
            'confidence': 0.9,
            'source_method': 'linkedin_company',
            'geographic_location': 'Riyadh'
        },
        {
            'data_type': 'person_profile',
            'value': 'Ahmed Al-Rashid',
            'title': 'Chief Technology Officer',
            'confidence': 0.85,
            'source_method': 'linkedin_profile',
            'contact_info': {'email': 'ahmed@techcompany.com'},
            'geographic_location': 'Riyadh'
        },
        {
            'data_type': 'person_profile', 
            'value': 'Sarah Mohammed',
            'title': 'Engineering Manager',
            'confidence': 0.8,
            'source_method': 'linkedin_profile',
            'contact_info': {'phone': '+966501234567'},
            'geographic_location': 'Riyadh'
        },
        {
            'data_type': 'contact_info',
            'value': 'info@techcompany.com',
            'confidence': 0.7,
            'source_method': 'website_extraction'
        },
        {
            'data_type': 'social_profile',
            'value': 'Tech Company official LinkedIn page',
            'confidence': 0.75,
            'source_method': 'linkedin_search'
        }
    ]
    
    print("=== Testing AI Intelligence Analyzer ===")
    
    # Test comprehensive analysis
    analysis = await analyzer.analyze_intelligence_batch(sample_results)
    
    print(f"\nAnalysis Results:")
    print(f"Target: {analysis.target_identifier}")
    print(f"Business Type: {analysis.business_type} (Confidence: {analysis.business_confidence:.1%})")
    print(f"Industry: {analysis.industry_classification}")
    print(f"Company Size: {analysis.company_size_estimate}")
    print(f"Target Audience: {analysis.target_audience_type}")
    print(f"Primary Location: {analysis.primary_location}")
    print(f"Decision Makers Found: {len(analysis.decision_makers)}")
    print(f"Data Quality Score: {analysis.data_quality_score:.1%}")
    
    print(f"\nKey Insights:")
    for insight in analysis.key_insights[:3]:
        print(f"  • {insight}")
    
    print(f"\nRecommendations:")
    for recommendation in analysis.actionable_recommendations[:3]:
        print(f"  • {recommendation}")
    
    print(f"\nProcessing Time: {analysis.processing_time_seconds:.2f} seconds")
    
    # Test quick analysis
    quick_result = await analyzer.quick_analysis(sample_results)
    print(f"\nQuick Analysis Summary:")
    print(f"  Total Items: {quick_result['summary']['total_analyzed']}")
    print(f"  Business Type: {quick_result['summary']['business_type']}")
    print(f"  High Confidence Items: {quick_result['summary']['high_confidence_items']}")
    
    # Test export
    try:
        json_export = analyzer.export_analysis_report(analysis, 'json')
        print(f"\nJSON report exported to: {json_export}")
        
        html_export = analyzer.export_analysis_report(analysis, 'html')
        print(f"HTML report exported to: {html_export}")
        
        text_export = analyzer.export_analysis_report(analysis, 'text')
        print(f"Text summary exported to: {text_export}")
        
    except Exception as e:
        print(f"Export error: {e}")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_ai_analyzer())
