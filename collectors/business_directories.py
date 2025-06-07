"""
OSINT Data Collectors Package
============================

This package contains specialized collectors for gathering intelligence from various sources:
- search_engines: Google, Bing, DuckDuckGo advanced search
- social_media: LinkedIn, Twitter, Facebook intelligence
- business_directories: Business listings and directories
- job_portals: Job sites and professional networks
- specialized_tools: Technical analysis tools
"""

from .search_engines import IntelligentSearchCollector
from .social_media import SocialMediaIntelligenceCollector

__all__ = [
    'IntelligentSearchCollector',
    'SocialMediaIntelligenceCollector'
]

# ============================================================================
# collectors/business_directories.py - جامع أدلة الأعمال
# ============================================================================

import asyncio
import aiohttp
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class BusinessListing:
    """Business directory listing"""
    name: str
    address: str
    phone: Optional[str]
    website: Optional[str]
    category: str
    rating: Optional[float]
    reviews_count: Optional[int]
    description: str
    source_directory: str
    listing_url: str
    confidence_score: float
    metadata: Dict[str, Any]

class BusinessDirectoryCollector:
    """Business directory intelligence collector"""
    
    def __init__(self):
        self.directories = {
            'google_business': 'https://www.google.com/maps',
            'yelp': 'https://www.yelp.com',
            'yellowpages': 'https://www.yellowpages.com',
            'foursquare': 'https://foursquare.com'
        }
    
    async def comprehensive_directory_search(self, target: str, params: Dict) -> List[BusinessListing]:
        """Comprehensive business directory search"""
        logger.info(f"Business directory search for: {target}")
        
        all_listings = []
        location = params.get('geographic_focus', '')
        
        # Search across multiple directories
        search_tasks = [
            self._search_google_business(target, location),
            self._search_yelp(target, location),
            self._search_yellowpages(target, location)
        ]
        
        # Execute searches
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_listings.extend(result)
        
        # Remove duplicates and return
        unique_listings = self._deduplicate_listings(all_listings)
        return sorted(unique_listings, key=lambda x: x.confidence_score, reverse=True)
    
    async def _search_google_business(self, target: str, location: str) -> List[BusinessListing]:
        """Search Google My Business (simulation)"""
        listings = []
        
        # Simulate Google Business search
        for i in range(random.randint(3, 8)):
            listing = BusinessListing(
                name=f"{target} Business {i+1}",
                address=f"123 Business St, {location}",
                phone=f"+966{random.randint(500000000, 599999999)}",
                website=f"https://{target.replace(' ', '').lower()}{i+1}.com",
                category=self._categorize_business(target),
                rating=round(random.uniform(3.5, 5.0), 1),
                reviews_count=random.randint(10, 500),
                description=f"Professional {target} services in {location}",
                source_directory='google_business',
                listing_url=f"https://maps.google.com/business{i+1}",
                confidence_score=random.uniform(0.7, 0.95),
                metadata={'search_term': target, 'location': location}
            )
            listings.append(listing)
        
        return listings
    
    async def _search_yelp(self, target: str, location: str) -> List[BusinessListing]:
        """Search Yelp (simulation)"""
        listings = []
        
        for i in range(random.randint(2, 6)):
            listing = BusinessListing(
                name=f"{target} Yelp {i+1}",
                address=f"456 Yelp Ave, {location}",
                phone=f"+966{random.randint(500000000, 599999999)}" if random.choice([True, False]) else None,
                website=f"https://yelp{i+1}.com" if random.choice([True, False]) else None,
                category=self._categorize_business(target),
                rating=round(random.uniform(3.0, 5.0), 1),
                reviews_count=random.randint(5, 200),
                description=f"Highly rated {target} in {location}",
                source_directory='yelp',
                listing_url=f"https://yelp.com/biz/business{i+1}",
                confidence_score=random.uniform(0.6, 0.9),
                metadata={'search_term': target, 'location': location}
            )
            listings.append(listing)
        
        return listings
    
    async def _search_yellowpages(self, target: str, location: str) -> List[BusinessListing]:
        """Search Yellow Pages (simulation)"""
        listings = []
        
        for i in range(random.randint(1, 4)):
            listing = BusinessListing(
                name=f"{target} YP {i+1}",
                address=f"789 Yellow St, {location}",
                phone=f"+966{random.randint(500000000, 599999999)}",
                website=None,  # Yellow Pages often has phone but no website
                category=self._categorize_business(target),
                rating=None,
                reviews_count=None,
                description=f"Established {target} business in {location}",
                source_directory='yellowpages',
                listing_url=f"https://yellowpages.com/business{i+1}",
                confidence_score=random.uniform(0.5, 0.8),
                metadata={'search_term': target, 'location': location}
            )
            listings.append(listing)
        
        return listings
    
    def _categorize_business(self, target: str) -> str:
        """Categorize business based on target"""
        target_lower = target.lower()
        
        categories = {
            'restaurant': ['restaurant', 'food', 'dining', 'cafe'],
            'hotel': ['hotel', 'accommodation', 'resort', 'inn'],
            'technology': ['software', 'tech', 'IT', 'digital'],
            'healthcare': ['medical', 'health', 'clinic', 'hospital'],
            'retail': ['store', 'shop', 'retail', 'market'],
            'professional_services': ['consulting', 'legal', 'accounting', 'finance']
        }
        
        for category, keywords in categories.items():
            if any(keyword in target_lower for keyword in keywords):
                return category
        
        return 'general_business'
    
    def _deduplicate_listings(self, listings: List[BusinessListing]) -> List[BusinessListing]:
        """Remove duplicate listings"""
        seen_names = set()
        unique_listings = []
        
        for listing in listings:
            name_key = listing.name.lower().replace(' ', '')
            if name_key not in seen_names:
                seen_names.add(name_key)
                unique_listings.append(listing)
        
        return unique_listings

# ============================================================================
# collectors/job_portals_collector.py - جامع مواقع التوظيف
# ============================================================================

import asyncio
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class JobPortalProfile:
    """Job portal candidate profile"""
    name: str
    title: str
    skills: List[str]
    experience_years: int
    location: str
    education: str
    current_status: str  # "looking", "open", "employed"
    last_active: datetime
    profile_url: str
    contact_info: Dict[str, str]
    resume_keywords: List[str]
    salary_expectation: Optional[str]
    source_portal: str
    confidence_score: float
    metadata: Dict[str, Any]

class JobPortalsCollector:
    """Job portals intelligence collector"""
    
    def __init__(self):
        self.portals = {
            'linkedin_jobs': 'LinkedIn Jobs',
            'indeed': 'Indeed',
            'bayt': 'Bayt.com',
            'glassdoor': 'Glassdoor',
            'monster': 'Monster'
        }
    
    async def comprehensive_job_portal_search(self, target: str, params: Dict) -> List[JobPortalProfile]:
        """Comprehensive job portal search"""
        logger.info(f"Job portal search for: {target}")
        
        all_profiles = []
        location = params.get('geographic_focus', '')
        
        # Parallel search across portals
        search_tasks = [
            self._search_linkedin_jobs(target, location),
            self._search_indeed(target, location),
            self._search_bayt(target, location)
        ]
        
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_profiles.extend(result)
        
        # Process and rank profiles
        unique_profiles = self._deduplicate_profiles(all_profiles)
        ranked_profiles = self._rank_by_relevance(unique_profiles, target)
        
        return ranked_profiles[:50]  # Return top 50
    
    async def _search_linkedin_jobs(self, target: str, location: str) -> List[JobPortalProfile]:
        """Search LinkedIn Jobs (simulation)"""
        profiles = []
        
        # Extract job role from target
        job_role = self._extract_job_role(target)
        
        for i in range(random.randint(5, 12)):
            profile = JobPortalProfile(
                name=f"Professional {i+1}",
                title=f"{job_role} Specialist",
                skills=self._generate_relevant_skills(job_role),
                experience_years=random.randint(1, 15),
                location=location,
                education=random.choice(['Bachelor', 'Master', 'PhD', 'Diploma']),
                current_status=random.choice(['looking', 'open', 'employed']),
                last_active=datetime.now() - timedelta(days=random.randint(1, 30)),
                profile_url=f"https://linkedin.com/in/professional{i+1}",
                contact_info={
                    'email': f"professional{i+1}@email.com" if random.choice([True, False]) else None,
                    'phone': f"+966{random.randint(500000000, 599999999)}" if random.choice([True, False]) else None
                },
                resume_keywords=self._generate_resume_keywords(target, job_role),
                salary_expectation=f"{random.randint(5000, 25000)} SAR" if random.choice([True, False]) else None,
                source_portal='linkedin_jobs',
                confidence_score=random.uniform(0.7, 0.95),
                metadata={'search_term': target, 'location': location}
            )
            profiles.append(profile)
        
        return profiles
    
    async def _search_indeed(self, target: str, location: str) -> List[JobPortalProfile]:
        """Search Indeed (simulation)"""
        profiles = []
        job_role = self._extract_job_role(target)
        
        for i in range(random.randint(3, 8)):
            profile = JobPortalProfile(
                name=f"Candidate {i+1}",
                title=f"{job_role}",
                skills=self._generate_relevant_skills(job_role),
                experience_years=random.randint(1, 12),
                location=location,
                education=random.choice(['Bachelor', 'Master', 'Diploma']),
                current_status='looking',  # Indeed typically has active job seekers
                last_active=datetime.now() - timedelta(days=random.randint(1, 14)),
                profile_url=f"https://indeed.com/profile{i+1}",
                contact_info={
                    'email': f"candidate{i+1}@email.com"
                },
                resume_keywords=self._generate_resume_keywords(target, job_role),
                salary_expectation=f"{random.randint(4000, 20000)} SAR",
                source_portal='indeed',
                confidence_score=random.uniform(0.6, 0.85),
                metadata={'search_term': target, 'location': location}
            )
            profiles.append(profile)
        
        return profiles
    
    async def _search_bayt(self, target: str, location: str) -> List[JobPortalProfile]:
        """Search Bayt.com (simulation)"""
        profiles = []
        job_role = self._extract_job_role(target)
        
        for i in range(random.randint(2, 6)):
            profile = JobPortalProfile(
                name=f"Professional {i+1}",
                title=f"Senior {job_role}",
                skills=self._generate_relevant_skills(job_role),
                experience_years=random.randint(2, 10),
                location=location,
                education=random.choice(['Bachelor', 'Master']),
                current_status=random.choice(['looking', 'open']),
                last_active=datetime.now() - timedelta(days=random.randint(1, 21)),
                profile_url=f"https://bayt.com/profile{i+1}",
                contact_info={
                    'phone': f"+966{random.randint(500000000, 599999999)}"
                },
                resume_keywords=self._generate_resume_keywords(target, job_role),
                salary_expectation=None,  # Bayt often doesn't show salary expectations
                source_portal='bayt',
                confidence_score=random.uniform(0.5, 0.8),
                metadata={'search_term': target, 'location': location}
            )
            profiles.append(profile)
        
        return profiles
    
    def _extract_job_role(self, target: str) -> str:
        """Extract job role from target description"""
        target_lower = target.lower()
        
        roles = {
            'developer': ['developer', 'programmer', 'coder'],
            'engineer': ['engineer', 'engineering'],
            'manager': ['manager', 'management'],
            'analyst': ['analyst', 'analysis'],
            'designer': ['designer', 'design'],
            'consultant': ['consultant', 'consulting'],
            'specialist': ['specialist', 'expert']
        }
        
        for role, keywords in roles.items():
            if any(keyword in target_lower for keyword in keywords):
                return role
        
        return 'professional'
    
    def _generate_relevant_skills(self, job_role: str) -> List[str]:
        """Generate relevant skills for job role"""
        skill_sets = {
            'developer': ['Python', 'JavaScript', 'React', 'Node.js', 'SQL', 'Git'],
            'engineer': ['Engineering', 'Project Management', 'AutoCAD', 'MATLAB'],
            'manager': ['Leadership', 'Project Management', 'Strategic Planning', 'Team Building'],
            'analyst': ['Data Analysis', 'Excel', 'SQL', 'Python', 'Statistics'],
            'designer': ['Photoshop', 'Illustrator', 'UI/UX', 'Creative Design'],
            'consultant': ['Strategic Consulting', 'Business Analysis', 'Client Management']
        }
        
        base_skills = skill_sets.get(job_role, ['Communication', 'Problem Solving'])
        return random.sample(base_skills, min(len(base_skills), random.randint(3, 6)))
    
    def _generate_resume_keywords(self, target: str, job_role: str) -> List[str]:
        """Generate resume keywords based on target and role"""
        keywords = [job_role, 'professional', 'experienced']
        
        # Add target-specific keywords
        target_words = target.lower().split()
        keywords.extend([word for word in target_words if len(word) > 3])
        
        # Add role-specific keywords
        role_keywords = {
            'developer': ['coding', 'programming', 'software development'],
            'engineer': ['engineering', 'technical', 'problem solving'],
            'manager': ['management', 'leadership', 'team'],
            'analyst': ['analysis', 'data', 'reporting']
        }
        
        if job_role in role_keywords:
            keywords.extend(role_keywords[job_role])
        
        return list(set(keywords))
    
    def _deduplicate_profiles(self, profiles: List[JobPortalProfile]) -> List[JobPortalProfile]:
        """Remove duplicate profiles"""
        seen_names = set()
        unique_profiles = []
        
        for profile in profiles:
            name_key = profile.name.lower().replace(' ', '')
            if name_key not in seen_names:
                seen_names.add(name_key)
                unique_profiles.append(profile)
        
        return unique_profiles
    
    def _rank_by_relevance(self, profiles: List[JobPortalProfile], target: str) -> List[JobPortalProfile]:
        """Rank profiles by relevance to target"""
        target_words = set(target.lower().split())
        
        for profile in profiles:
            relevance_score = profile.confidence_score
            
            # Check title relevance
            title_words = set(profile.title.lower().split())
            title_matches = len(target_words.intersection(title_words))
            relevance_score += (title_matches / len(target_words)) * 0.3
            
            # Check skills relevance
            skill_words = set(' '.join(profile.skills).lower().split())
            skill_matches = len(target_words.intersection(skill_words))
            relevance_score += (skill_matches / len(target_words)) * 0.2
            
            # Boost for active profiles
            days_since_active = (datetime.now() - profile.last_active).days
            if days_since_active <= 7:
                relevance_score += 0.1
            elif days_since_active <= 30:
                relevance_score += 0.05
            
            # Boost for available candidates
            if profile.current_status in ['looking', 'open']:
                relevance_score += 0.15
            
            profile.confidence_score = min(relevance_score, 1.0)
        
        return sorted(profiles, key=lambda x: x.confidence_score, reverse=True)

# ============================================================================
# collectors/specialized_tools_collector.py - جامع الأدوات المتخصصة
# ============================================================================

import asyncio
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class TechnicalIntelligence:
    """Technical intelligence data"""
    data_type: str  # 'domain_info', 'security_scan', 'technology_stack'
    target: str
    findings: Dict[str, Any]
    confidence_score: float
    source_tool: str
    scan_timestamp: datetime
    metadata: Dict[str, Any]

class SpecializedToolsCollector:
    """Specialized OSINT tools collector"""
    
    def __init__(self):
        self.tools = {
            'whois': 'Domain registration information',
            'dns_analysis': 'DNS record analysis',
            'ssl_analysis': 'SSL certificate analysis',
            'technology_detection': 'Technology stack detection',
            'security_scan': 'Basic security assessment'
        }
    
    async def specialized_intelligence_gathering(self, target: str, params: Dict) -> List[TechnicalIntelligence]:
        """Comprehensive specialized intelligence gathering"""
        logger.info(f"Specialized intelligence gathering for: {target}")
        
        all_intelligence = []
        
        # Determine target type and applicable tools
        target_type = self._determine_target_type(target)
        
        if target_type == 'domain':
            # Domain-specific tools
            tools_to_run = [
                self._whois_analysis(target),
                self._dns_analysis(target),
                self._ssl_analysis(target),
                self._technology_detection(target),
                self._security_scan(target)
            ]
        elif target_type == 'company':
            # Company-specific tools
            tools_to_run = [
                self._company_technology_analysis(target),
                self._digital_footprint_analysis(target)
            ]
        else:
            # General analysis
            tools_to_run = [
                self._general_intelligence_scan(target)
            ]
        
        # Execute all tools
        results = await asyncio.gather(*tools_to_run, return_exceptions=True)
        
        for result in results:
            if isinstance(result, TechnicalIntelligence):
                all_intelligence.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Tool execution error: {result}")
        
        return all_intelligence
    
    def _determine_target_type(self, target: str) -> str:
        """Determine target type for appropriate tool selection"""
        if '.' in target and ' ' not in target:
            return 'domain'
        elif any(indicator in target.lower() for indicator in ['company', 'corp', 'ltd', 'inc']):
            return 'company'
        else:
            return 'general'
    
    async def _whois_analysis(self, domain: str) -> TechnicalIntelligence:
        """WHOIS information analysis (simulation)"""
        # Simulate WHOIS lookup
        whois_data = {
            'domain_name': domain,
            'registrar': 'Example Registrar Inc.',
            'creation_date': '2020-01-15',
            'expiration_date': '2025-01-15',
            'name_servers': ['ns1.example.com', 'ns2.example.com'],
            'registrant_country': 'SA',
            'registrant_organization': f'Organization for {domain}',
            'admin_email': f'admin@{domain}',
            'privacy_protection': random.choice([True, False])
        }
        
        return TechnicalIntelligence(
            data_type='domain_info',
            target=domain,
            findings=whois_data,
            confidence_score=0.95,
            source_tool='whois',
            scan_timestamp=datetime.now(),
            metadata={'scan_type': 'whois_lookup'}
        )
    
    async def _dns_analysis(self, domain: str) -> TechnicalIntelligence:
        """DNS record analysis (simulation)"""
        dns_records = {
            'A_records': [f'192.168.1.{random.randint(1, 255)}'],
            'MX_records': [f'mail.{domain}', f'mail2.{domain}'],
            'NS_records': [f'ns1.{domain}', f'ns2.{domain}'],
            'TXT_records': [
                'v=spf1 include:_spf.google.com ~all',
                'google-site-verification=example123'
            ],
            'CNAME_records': {f'www.{domain}': domain},
            'subdomain_count': random.randint(5, 25)
        }
        
        return TechnicalIntelligence(
            data_type='dns_info',
            target=domain,
            findings=dns_records,
            confidence_score=0.9,
            source_tool='dns_analysis',
            scan_timestamp=datetime.now(),
            metadata={'scan_type': 'dns_enumeration'}
        )
    
    async def _ssl_analysis(self, domain: str) -> TechnicalIntelligence:
        """SSL certificate analysis (simulation)"""
        ssl_info = {
            'certificate_valid': True,
            'issuer': 'Let\'s Encrypt Authority X3',
            'subject': f'CN={domain}',
            'valid_from': '2024-01-01',
            'valid_until': '2025-01-01',
            'signature_algorithm': 'sha256WithRSAEncryption',
            'key_size': 2048,
            'san_domains': [f'www.{domain}', f'mail.{domain}'],
            'security_rating': random.choice(['A+', 'A', 'B']),
            'vulnerabilities': []
        }
        
        return TechnicalIntelligence(
            data_type='ssl_info',
            target=domain,
            findings=ssl_info,
            confidence_score=0.85,
            source_tool='ssl_analysis',
            scan_timestamp=datetime.now(),
            metadata={'scan_type': 'ssl_certificate_check'}
        )
    
    async def _technology_detection(self, domain: str) -> TechnicalIntelligence:
        """Technology stack detection (simulation)"""
        technologies = {
            'web_server': random.choice(['Apache', 'Nginx', 'IIS']),
            'programming_language': random.choice(['PHP', 'Python', 'Node.js', 'Java']),
            'framework': random.choice(['React', 'Angular', 'Vue.js', 'Laravel']),
            'database': random.choice(['MySQL', 'PostgreSQL', 'MongoDB']),
            'cdn': random.choice(['Cloudflare', 'AWS CloudFront', 'None']),
            'analytics': random.choice(['Google Analytics', 'Adobe Analytics', 'None']),
            'cms': random.choice(['WordPress', 'Drupal', 'Custom', 'None']),
            'javascript_libraries': ['jQuery', 'Bootstrap'],
            'hosting_provider': random.choice(['AWS', 'Google Cloud', 'Azure', 'Local'])
        }
        
        return TechnicalIntelligence(
            data_type='technology_stack',
            target=domain,
            findings=technologies,
            confidence_score=0.8,
            source_tool='technology_detection',
            scan_timestamp=datetime.now(),
            metadata={'scan_type': 'technology_fingerprinting'}
        )
    
    async def _security_scan(self, domain: str) -> TechnicalIntelligence:
        """Basic security assessment (simulation)"""
        security_findings = {
            'open_ports': [80, 443, 22] if random.choice([True, False]) else [80, 443],
            'ssl_vulnerabilities': [],
            'security_headers': {
                'strict_transport_security': random.choice([True, False]),
                'content_security_policy': random.choice([True, False]),
                'x_frame_options': random.choice([True, False])
            },
            'directory_listing': random.choice([True, False]),
            'admin_panels_found': random.choice([True, False]),
            'backup_files_found': random.choice([True, False]),
            'security_score': random.randint(70, 95)
        }
        
        return TechnicalIntelligence(
            data_type='security_scan',
            target=domain,
            findings=security_findings,
            confidence_score=0.75,
            source_tool='security_scan',
            scan_timestamp=datetime.now(),
            metadata={'scan_type': 'basic_security_assessment'}
        )
    
    async def _company_technology_analysis(self, company: str) -> TechnicalIntelligence:
        """Company technology analysis (simulation)"""
        tech_analysis = {
            'digital_maturity': random.choice(['basic', 'intermediate', 'advanced']),
            'online_presence': {
                'website': True,
                'social_media': random.choice([True, False]),
                'mobile_app': random.choice([True, False]),
                'e_commerce': random.choice([True, False])
            },
            'technology_adoption': {
                'cloud_services': random.choice(['AWS', 'Azure', 'Google Cloud', 'None']),
                'crm_system': random.choice(['Salesforce', 'HubSpot', 'Custom', 'None']),
                'erp_system': random.choice(['SAP', 'Oracle', 'Microsoft', 'None'])
            },
            'innovation_indicators': random.randint(1, 10)
        }
        
        return TechnicalIntelligence(
            data_type='company_technology',
            target=company,
            findings=tech_analysis,
            confidence_score=0.7,
            source_tool='company_tech_analysis',
            scan_timestamp=datetime.now(),
            metadata={'scan_type': 'company_technology_assessment'}
        )
    
    async def _digital_footprint_analysis(self, company: str) -> TechnicalIntelligence:
        """Digital footprint analysis (simulation)"""
        footprint = {
            'domain_count': random.randint(1, 10),
            'subdomain_count': random.randint(5, 50),
            'social_media_accounts': random.randint(2, 8),
            'online_mentions': random.randint(10, 1000),
            'digital_presence_score': random.randint(40, 95),
            'brand_protection': {
                'trademark_domains': random.randint(0, 5),
                'typosquatting_domains': random.randint(0, 3)
            }
        }
        
        return TechnicalIntelligence(
            data_type='digital_footprint',
            target=company,
            findings=footprint,
            confidence_score=0.65,
            source_tool='digital_footprint_analysis',
            scan_timestamp=datetime.now(),
            metadata={'scan_type': 'digital_footprint_assessment'}
        )
    
    async def _general_intelligence_scan(self, target: str) -> TechnicalIntelligence:
        """General intelligence scan (simulation)"""
        general_findings = {
            'target_type': 'general',
            'information_found': random.choice([True, False]),
            'related_entities': [f'Related Entity {i+1}' for i in range(random.randint(1, 5))],
            'confidence_level': random.choice(['low', 'medium', 'high']),
            'additional_research_needed': random.choice([True, False])
        }
        
        return TechnicalIntelligence(
            data_type='general_scan',
            target=target,
            findings=general_findings,
            confidence_score=0.6,
            source_tool='general_scan',
            scan_timestamp=datetime.now(),
            metadata={'scan_type': 'general_intelligence_gathering'}
        )

# ============================================================================
# Example usage and comprehensive test
# ============================================================================

async def test_complete_system():
    """Test the complete OSINT system"""
    from core.discovery_engine import AdvancedDiscoveryEngine
    from core.ai_analyzer import IntelligenceAnalyzer
    
    print("=== Testing Complete Advanced OSINT System ===")
    
    # Initialize system
    discovery_engine = AdvancedDiscoveryEngine()
    ai_analyzer = IntelligenceAnalyzer()
    
    # Test questionnaire data
    questionnaire_data = {
        'context': 'lead_generation',
        'data_priorities': ['contact_info', 'decision_makers', '# ============================================================================
# utils/rate_limiter.py - تحديد معدل الطلبات المحسن
# ============================================================================

import asyncio
import time
from collections import defaultdict, deque
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Advanced rate limiter with adaptive capabilities"""
    
    def __init__(self):
        self.requests_per_minute = 30
        self.delay_between_requests = 2.0
        self.last_request_time = defaultdict(float)
        self.request_history = defaultdict(deque)
        self.adaptive_delays = defaultdict(float)
        self.blocked_sources = defaultdict(float)
        
    def configure(self, requests_per_minute: int = 30, delay_between_requests: float = 2.0):
        """Configure rate limiting parameters"""
        self.requests_per_minute = requests_per_minute
        self.delay_between_requests = delay_between_requests
        logger.info(f"Rate limiter configured: {requests_per_minute} req/min, {delay_between_requests}s delay")
    
    async def wait_if_needed(self, source: str = "default") -> None:
        """Intelligent rate limiting with adaptive delays"""
        current_time = time.time()
        
        # Check if source is temporarily blocked
        if source in self.blocked_sources:
            block_time = self.blocked_sources[source]
            if current_time < block_time:
                wait_time = block_time - current_time
                logger.warning(f"Source {source} blocked for {wait_time:.1f} more seconds")
                await asyncio.sleep(wait_time)
                return
            else:
                del self.blocked_sources[source]
        
        # Update request history
        history = self.request_history[source]
        history.append(current_time)
        
        # Remove old requests (older than 1 minute)
        while history and history[0] < current_time - 60:
            history.popleft()
        
        # Check if we're exceeding rate limits
        if len(history) >= self.requests_per_minute:
            oldest_request = history[0]
            wait_time = 60 - (current_time - oldest_request)
            if wait_time > 0:
                logger.info(f"Rate limit reached for {source}, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        # Apply base delay
        last_time = self.last_request_time[source]
        base_delay = self.delay_between_requests
        
        # Apply adaptive delay if needed
        adaptive_delay = self.adaptive_delays.get(source, 0)
        total_delay = max(base_delay, adaptive_delay)
        
        time_since_last = current_time - last_time
        if time_since_last < total_delay:
            wait_time = total_delay - time_since_last
            await asyncio.sleep(wait_time)
        
        self.last_request_time[source] = time.time()
    
    def increase_delay(self, source: str, factor: float = 1.5):
        """Increase delay for a source (when getting blocked/rate limited)"""
        current_delay = self.adaptive_delays.get(source, self.delay_between_requests)
        new_delay = min(current_delay * factor, 30.0)  # Max 30 seconds
        self.adaptive_delays[source] = new_delay
        logger.warning(f"Increased delay for {source} to {new_delay:.1f}s")
    
    def decrease_delay(self, source: str, factor: float = 0.9):
        """Decrease delay for a source (when requests are successful)"""
        if source in self.adaptive_delays:
            current_delay = self.adaptive_delays[source]
            new_delay = max(current_delay * factor, self.delay_between_requests)
            self.adaptive_delays[source] = new_delay
    
    def block_source(self, source: str, duration: float = 300):
        """Temporarily block a source (5 minutes default)"""
        block_until = time.time() + duration
        self.blocked_sources[source] = block_until
        logger.error(f"Blocked source {source} for {duration} seconds")

# ============================================================================
# utils/proxy_manager.py - إدارة البروكسي المتقدمة
# ============================================================================

import random
import aiohttp
from pathlib import Path
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)

class ProxyManager:
    """Advanced proxy management with health checking"""
    
    def __init__(self):
        self.enabled = False
        self.proxies = []
        self.current_proxy_index = 0
        self.proxy_health = {}
        self.failed_proxies = set()
        
    def configure(self, enabled: bool = False, proxy_file: Optional[str] = None, proxy_list: Optional[List[str]] = None):
        """Configure proxy settings"""
        self.enabled = enabled
        
        if enabled:
            if proxy_list:
                self.proxies = proxy_list
            elif proxy_file:
                self.load_proxies(proxy_file)
            else:
                logger.warning("Proxy enabled but no proxy source provided")
                self.enabled = False
        
        logger.info(f"Proxy manager configured: enabled={enabled}, proxies={len(self.proxies)}")
    
    def load_proxies(self, proxy_file: str):
        """Load proxies from file"""
        try:
            proxy_path = Path(proxy_file)
            if proxy_path.exists():
                with open(proxy_path, 'r') as f:
                    self.proxies = [line.strip() for line in f.readlines() if line.strip()]
                logger.info(f"Loaded {len(self.proxies)} proxies from {proxy_file}")
            else:
                logger.error(f"Proxy file not found: {proxy_file}")
                self.enabled = False
        except Exception as e:
            logger.error(f"Error loading proxies: {e}")
            self.enabled = False
    
    def get_proxy(self) -> Optional[str]:
        """Get next working proxy"""
        if not self.enabled or not self.proxies:
            return None
        
        # Filter out failed proxies
        working_proxies = [p for p in self.proxies if p not in self.failed_proxies]
        
        if not working_proxies:
            # Reset failed proxies if all are failed
            self.failed_proxies.clear()
            working_proxies = self.proxies
        
        # Return random working proxy
        return random.choice(working_proxies) if working_proxies else None
    
    def mark_proxy_failed(self, proxy: str):
        """Mark a proxy as failed"""
        if proxy:
            self.failed_proxies.add(proxy)
            logger.warning(f"Marked proxy as failed: {proxy}")
    
    def mark_proxy_working(self, proxy: str):
        """Mark a proxy as working"""
        if proxy in self.failed_proxies:
            self.failed_proxies.remove(proxy)
            logger.info(f"Proxy restored: {proxy}")
    
    async def test_proxy(self, proxy: str, timeout: int = 10) -> bool:
        """Test if a proxy is working"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.get('http://httpbin.org/ip', proxy=proxy) as response:
                    if response.status == 200:
                        self.mark_proxy_working(proxy)
                        return True
        except Exception as e:
            logger.debug(f"Proxy test failed for {proxy}: {e}")
        
        self.mark_proxy_failed(proxy)
        return False
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Health check all proxies"""
        if not self.proxies:
            return {}
        
        results = {}
        for proxy in self.proxies:
            results[proxy] = await self.test_proxy(proxy)
        
        working_count = sum(results.values())
        logger.info(f"Proxy health check: {working_count}/{len(self.proxies)} working")
        
        return results

# ============================================================================
# utils/patterns.py - أنماط البحث والاستخراج
# ============================================================================

import re
from typing import Dict, List, Pattern
import json
from pathlib import Path

class SearchPatterns:
    """Advanced search patterns and data extraction"""
    
    def __init__(self):
        self.google_dorks = self._initialize_google_dorks()
        self.validation_patterns = self._initialize_validation_patterns()
        self.extraction_patterns = self._initialize_extraction_patterns()
        
    def _initialize_google_dorks(self) -> Dict[str, List[str]]:
        """Initialize comprehensive Google Dork patterns"""
        return {
            'contact_discovery': [
                'site:{domain} "contact" OR "email" OR "phone"',
                'site:{domain} "@{domain}" -www',
                'site:{domain} filetype:pdf "contact"',
                '"{company}" "email" OR "contact" -site:{domain}',
                '"{company}" "@" site:linkedin.com',
                'site:{domain} "staff" OR "team" OR "employees"',
                'site:{domain} "about us" OR "meet the team"'
            ],
            'employee_discovery': [
                '"{company}" site:linkedin.com/in/',
                '"{company}" "manager" OR "director" OR "CEO"',
                '"{company}" "@{domain}" site:linkedin.com',
                '"{company}" "works at" OR "employee"',
                'site:{domain} "bio" OR "biography"'
            ],
            'business_intelligence': [
                '"{company}" "revenue" OR "employees" OR "funding"',
                '"{company}" "CEO" OR "founder" OR "president"',
                '"{company}" "office" OR "headquarters"',
                '"{company}" "news" OR "press release"',
                'site:{domain} "investor" OR "funding"'
            ],
            'vulnerability_discovery': [
                'site:{domain} "admin" OR "login"',
                'site:{domain} "database" OR "db"',
                'site:{domain} intitle:"index of"',
                'site:{domain} "config" OR "backup"'
            ],
            'social_media_discovery': [
                '"{company}" site:facebook.com',
                '"{company}" site:twitter.com',
                '"{company}" site:instagram.com',
                '"{company}" site:youtube.com'
            ]
        }
    
    def _initialize_validation_patterns(self) -> Dict[str, Pattern]:
        """Initialize validation regex patterns"""
        return {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone_saudi': re.compile(r'(?:\+966|966|0)?(?:5[0-9])\d{7}\b'),
            'phone_uae': re.compile(r'(?:\+971|971|0)?(?:5[0-9])\d{7}\b'),
            'phone_international': re.compile(r'\+?[1-9]\d{1,14}\b'),
            'domain': re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'),
            'ip_address': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            'linkedin_profile': re.compile(r'linkedin\.com/in/[a-zA-Z0-9-]+'),
            'twitter_handle': re.compile(r'@[A-Za-z0-9_]+'),
            'url': re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        }
    
    def _initialize_extraction_patterns(self) -> Dict[str, Dict]:
        """Initialize data extraction patterns"""
        return {
            'job_titles': {
                'executive': ['ceo', 'president', 'founder', 'chief executive'],
                'technical': ['cto', 'engineering manager', 'technical director', 'head of engineering'],
                'sales': ['sales manager', 'business development', 'account manager'],
                'marketing': ['marketing manager', 'brand manager', 'communications'],
                'hr': ['hr manager', 'human resources', 'talent acquisition'],
                'finance': ['cfo', 'finance manager', 'controller', 'accounting']
            },
            'company_types': {
                'technology': ['software', 'tech', 'ai', 'digital', 'platform'],
                'healthcare': ['medical', 'health', 'clinic', 'hospital'],
                'finance': ['bank', 'financial', 'investment', 'insurance'],
                'retail': ['retail', 'store', 'commerce', 'shopping'],
                'manufacturing': ['manufacturing', 'factory', 'production']
            },
            'business_indicators': {
                'size_small': ['startup', 'small business', 'boutique', 'family business'],
                'size_medium': ['growing company', 'mid-size', 'expanding'],
                'size_large': ['corporation', 'enterprise', 'multinational', 'global']
            }
        }
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        return self.validation_patterns['email'].findall(text)
    
    def extract_phones(self, text: str, region: str = 'international') -> List[str]:
        """Extract phone numbers from text"""
        pattern_key = f'phone_{region}'
        if pattern_key in self.validation_patterns:
            return self.validation_patterns[pattern_key].findall(text)
        return self.validation_patterns['phone_international'].findall(text)
    
    def extract_domains(self, text: str) -> List[str]:
        """Extract domain names from text"""
        return self.validation_patterns['domain'].findall(text)
    
    def extract_social_profiles(self, text: str) -> Dict[str, List[str]]:
        """Extract social media profiles"""
        return {
            'linkedin': self.validation_patterns['linkedin_profile'].findall(text),
            'twitter': self.validation_patterns['twitter_handle'].findall(text)
        }
    
    def classify_job_title(self, title: str) -> str:
        """Classify job title into category"""
        title_lower = title.lower()
        
        for category, keywords in self.extraction_patterns['job_titles'].items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def detect_company_type(self, text: str) -> str:
        """Detect company type from text"""
        text_lower = text.lower()
        
        for company_type, keywords in self.extraction_patterns['company_types'].items():
            if any(keyword in text_lower for keyword in keywords):
                return company_type
        
        return 'general'
    
    def estimate_company_size(self, text: str) -> str:
        """Estimate company size from text indicators"""
        text_lower = text.lower()
        
        for size_category, indicators in self.extraction_patterns['business_indicators'].items():
            if any(indicator in text_lower for indicator in indicators):
                return size_category.replace('size_', '')
        
        return 'unknown'

# ============================================================================
# utils/validation_rules.py - قواعد التحقق المتقدمة
# ============================================================================

import re
import dns.resolver
import validators
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ValidationRules:
    """Advanced validation rules for OSINT data"""
    
    def __init__(self):
        self.patterns = SearchPatterns()
        self.domain_cache = {}
        
    def validate_email(self, email: str) -> Dict[str, any]:
        """Comprehensive email validation"""
        result = {
            'valid': False,
            'confidence': 0.0,
            'format_valid': False,
            'domain_valid': False,
            'mx_record_exists': False,
            'business_email': False,
            'risk_indicators': []
        }
        
        if not email or not isinstance(email, str):
            return result
        
        email = email.strip().lower()
        
        # Format validation
        if self.patterns.validation_patterns['email'].match(email):
            result['format_valid'] = True
            result['confidence'] += 0.3
        else:
            result['risk_indicators'].append('Invalid email format')
            return result
        
        # Extract domain
        domain = email.split('@')[1] if '@' in email else None
        if not domain:
            return result
        
        # Domain validation
        if validators.domain(domain):
            result['domain_valid'] = True
            result['confidence'] += 0.2
        else:
            result['risk_indicators'].append('Invalid domain format')
        
        # MX record check
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            if mx_records:
                result['mx_record_exists'] = True
                result['confidence'] += 0.3
        except Exception as e:
            result['risk_indicators'].append('No MX record found')
            logger.debug(f"MX lookup failed for {domain}: {e}")
        
        # Business email detection
        personal_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        if domain not in personal_domains:
            result['business_email'] = True
            result['confidence'] += 0.2
        
        # Suspicious patterns
        suspicious_patterns = ['noreply', 'donotreply', 'test', 'temp', 'fake']
        if any(pattern in email for pattern in suspicious_patterns):
            result['risk_indicators'].append('Suspicious email pattern')
            result['confidence'] = max(0, result['confidence'] - 0.3)
        
        result['valid'] = result['confidence'] >= 0.5
        return result
    
    def validate_phone(self, phone: str, region: str = 'international') -> Dict[str, any]:
        """Comprehensive phone number validation"""
        result = {
            'valid': False,
            'confidence': 0.0,
            'format_valid': False,
            'region_detected': None,
            'type': None,  # mobile, landline
            'risk_indicators': []
        }
        
        if not phone or not isinstance(phone, str):
            return result
        
        # Clean phone number
        cleaned_phone = re.sub(r'[^\d+]', '', phone.strip())
        
        # Regional validation
        if region == 'saudi' or self.patterns.validation_patterns['phone_saudi'].match(cleaned_phone):
            result['format_valid'] = True
            result['region_detected'] = 'saudi'
            result['type'] = 'mobile'
            result['confidence'] = 0.9
        elif region == 'uae' or self.patterns.validation_patterns['phone_uae'].match(cleaned_phone):
            result['format_valid'] = True
            result['region_detected'] = 'uae'
            result['type'] = 'mobile'
            result['confidence'] = 0.9
        elif self.patterns.validation_patterns['phone_international'].match(cleaned_phone):
            result['format_valid'] = True
            result['region_detected'] = 'international'
            result['confidence'] = 0.7
        else:
            result['risk_indicators'].append('Invalid phone format')
            return result
        
        # Length validation
        if len(cleaned_phone) < 8:
            result['risk_indicators'].append('Phone number too short')
            result['confidence'] -= 0.2
        elif len(cleaned_phone) > 15:
            result['risk_indicators'].append('Phone number too long')
            result['confidence'] -= 0.1
        
        result['valid'] = result['confidence'] >= 0.5
        return result
    
    def validate_domain(self, domain: str) -> Dict[str, any]:
        """Comprehensive domain validation"""
        result = {
            'valid': False,
            'confidence': 0.0,
            'format_valid': False,
            'dns_resolves': False,
            'has_mx_record': False,
            'ssl_certificate': False,
            'risk_indicators': []
        }
        
        if not domain or not isinstance(domain, str):
            return result
        
        domain = domain.strip().lower()
        
        # Format validation
        if validators.domain(domain):
            result['format_valid'] = True
            result['confidence'] += 0.3
        else:
            result['risk_indicators'].append('Invalid domain format')
            return result
        
        # DNS resolution
        try:
            dns.resolver.resolve(domain, 'A')
            result['dns_resolves'] = True
            result['confidence'] += 0.4
        except Exception as e:
            result['risk_indicators'].append('Domain does not resolve')
            logger.debug(f"DNS resolution failed for {domain}: {e}")
        
        # MX record check
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            if mx_records:
                result['has_mx_record'] = True
                result['confidence'] += 0.2
        except Exception:
            pass
        
        # Suspicious domain indicators
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf']
        if any(domain.endswith(tld) for tld in suspicious_tlds):
            result['risk_indicators'].append('Suspicious TLD')
            result['confidence'] -= 0.3
        
        result['valid'] = result['confidence'] >= 0.5
        return result
    
    def validate_business_info(self, business_data: Dict[str, any]) -> Dict[str, any]:
        """Validate business information consistency"""
        result = {
            'valid': False,
            'confidence': 0.0,
            'consistency_score': 0.0,
            'completeness_score': 0.0,
            'risk_indicators': []
        }
        
        if not business_data:
            return result
        
        # Check required fields
        required_fields = ['name', 'industry', 'location']
        present_fields = sum(1 for field in required_fields if business_data.get(field))
        result['completeness_score'] = present_fields / len(required_fields)
        
        # Consistency checks
        consistency_checks = 0
        total_checks = 0
        
        # Name consistency
        if business_data.get('name') and business_data.get('domain'):
            total_checks += 1
            name_words = set(business_data['name'].lower().split())
            domain_words = set(business_data['domain'].replace('.', ' ').split())
            if name_words.intersection(domain_words):
                consistency_checks += 1
        
        # Location consistency
        if business_data.get('location') and business_data.get('phone'):
            total_checks += 1
            location = business_data['location'].lower()
            phone = business_data['phone']
            
            # Check if phone region matches location
            if 'saudi' in location and self.patterns.validation_patterns['phone_saudi'].search(phone):
                consistency_checks += 1
            elif 'uae' in location and self.patterns.validation_patterns['phone_uae'].search(phone):
                consistency_checks += 1
        
        if total_checks > 0:
            result['consistency_score'] = consistency_checks / total_checks
        
        # Calculate overall confidence
        result['confidence'] = (result['completeness_score'] * 0.6 + result['consistency_score'] * 0.4)
        result['valid'] = result['confidence'] >= 0.6
        
        return result
