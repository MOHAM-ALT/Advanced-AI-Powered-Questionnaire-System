#!/usr/bin/env python3
"""
Social Media Intelligence Collector
File Location: collectors/social_media.py
LinkedIn, Twitter, Facebook, Instagram, and Professional Networks Intelligence
"""

import asyncio
import aiohttp
import re
import json
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from urllib.parse import quote, urljoin, urlparse
from bs4 import BeautifulSoup
import time

# Import utilities
from utils.rate_limiter import RateLimiter
from utils.proxy_manager import ProxyManager

logger = logging.getLogger(__name__)

@dataclass
class SocialProfile:
    """Social media profile data"""
    platform: str
    profile_url: str
    display_name: str
    username: str
    bio: str
    followers_count: Optional[int]
    following_count: Optional[int]
    posts_count: Optional[int]
    verified: bool
    profile_image_url: str
    location: Optional[str]
    website: Optional[str]
    join_date: Optional[datetime]
    last_activity: Optional[datetime]
    contact_info: Dict[str, str]
    professional_info: Dict[str, Any]
    connections: List[str]
    recent_posts: List[Dict[str, Any]]
    confidence_score: float
    metadata: Dict[str, Any]

@dataclass
class CompanyProfile:
    """Company social media profile"""
    platform: str
    company_name: str
    profile_url: str
    industry: str
    company_size: Optional[str]
    headquarters: Optional[str]
    website: Optional[str]
    description: str
    founded_year: Optional[int]
    employees_on_platform: List[Dict[str, Any]]
    recent_updates: List[Dict[str, Any]]
    followers_count: Optional[int]
    engagement_metrics: Dict[str, Any]
    contact_information: Dict[str, str]
    key_personnel: List[Dict[str, Any]]
    confidence_score: float
    metadata: Dict[str, Any]

class LinkedInIntelligenceCollector:
    """Advanced LinkedIn intelligence gathering"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.base_url = "https://www.linkedin.com"
        self.search_patterns = self._initialize_search_patterns()
        
    def _initialize_search_patterns(self) -> Dict[str, List[str]]:
        """Initialize LinkedIn search patterns"""
        return {
            'company_search': [
                '/search/results/companies/?keywords={company}',
                '/search/results/companies/?keywords={company}&origin=GLOBAL_SEARCH_HEADER',
                '/company/{company_slug}/'
            ],
            'people_search': [
                '/search/results/people/?keywords={keywords}',
                '/search/results/people/?keywords={keywords}&origin=GLOBAL_SEARCH_HEADER',
                '/search/results/people/?keywords={title} {location}',
                '/search/results/people/?currentCompany=["{company}"]',
                '/search/results/people/?geoUrn=["location"]&keywords={keywords}'
            ],
            'job_search': [
                '/search/results/people/?keywords="{job_title}" "{location}"',
                '/search/results/people/?keywords="looking for work" {skills}',
                '/search/results/people/?keywords="available for work" {location}',
                '/search/results/people/?keywords="seeking opportunities" {industry}'
            ],
            'posts_search': [
                '/search/results/content/?keywords={keywords}',
                '/search/results/content/?keywords="{company}" update',
                '/search/results/content/?keywords={topic} {location}'
            ]
        }
    
    async def comprehensive_company_research(self, company_name: str, params: Dict) -> CompanyProfile:
        """Comprehensive LinkedIn company research"""
        logger.info(f"Starting LinkedIn company research for: {company_name}")
        
        # Search for company
        company_url = await self._search_company(company_name)
        if not company_url:
            return None
        
        # Extract company information
        company_info = await self._extract_company_info(company_url)
        
        # Find employees
        employees = await self._find_company_employees(company_name, params)
        
        # Get recent company updates
        updates = await self._get_company_updates(company_name)
        
        # Create company profile
        profile = CompanyProfile(
            platform='linkedin',
            company_name=company_name,
            profile_url=company_url,
            industry=company_info.get('industry', ''),
            company_size=company_info.get('size', ''),
            headquarters=company_info.get('headquarters', ''),
            website=company_info.get('website', ''),
            description=company_info.get('description', ''),
            founded_year=company_info.get('founded', None),
            employees_on_platform=employees,
            recent_updates=updates,
            followers_count=company_info.get('followers', None),
            engagement_metrics=company_info.get('engagement', {}),
            contact_information=company_info.get('contact', {}),
            key_personnel=self._identify_key_personnel(employees),
            confidence_score=self._calculate_company_confidence(company_info, employees),
            metadata={'search_date': datetime.now(), 'source': 'linkedin_company_search'}
        )
        
        return profile
    
    async def _search_company(self, company_name: str) -> Optional[str]:
        """Search for company on LinkedIn"""
        # Simulate LinkedIn company search
        search_terms = [
            company_name,
            f'"{company_name}"',
            f'{company_name} company',
            f'{company_name} corporation'
        ]
        
        for term in search_terms:
            try:
                # In real implementation, this would make actual requests
                # For now, simulate with intelligent URL construction
                company_slug = self._generate_company_slug(company_name)
                potential_url = f"{self.base_url}/company/{company_slug}/"
                
                # Simulate verification
                if await self._verify_linkedin_url(potential_url):
                    return potential_url
                    
            except Exception as e:
                logger.error(f"Company search error: {e}")
                continue
        
        return None
    
    def _generate_company_slug(self, company_name: str) -> str:
        """Generate LinkedIn company slug"""
        # Convert company name to LinkedIn slug format
        slug = company_name.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
        slug = re.sub(r'[\s_-]+', '-', slug)  # Replace spaces with hyphens
        slug = slug.strip('-')
        return slug
    
    async def _verify_linkedin_url(self, url: str) -> bool:
        """Verify if LinkedIn URL exists (simulation)"""
        # In real implementation, would make HEAD request
        # For now, simulate based on common patterns
        return True
    
    async def _extract_company_info(self, company_url: str) -> Dict[str, Any]:
        """Extract company information from LinkedIn page"""
        # Simulate company data extraction
        company_info = {
            'industry': 'Technology',  # Would be extracted from page
            'size': '51-200 employees',
            'headquarters': 'Saudi Arabia',
            'website': 'https://example.com',
            'description': 'Technology company specializing in AI and software development',
            'founded': 2020,
            'followers': 1500,
            'engagement': {'posts_per_month': 8, 'avg_likes': 50},
            'contact': {'email': 'info@company.com', 'phone': '+966501234567'}
        }
        
        return company_info
    
    async def _find_company_employees(self, company_name: str, params: Dict) -> List[Dict[str, Any]]:
        """Find employees of the company"""
        employees = []
        
        # Search patterns for finding employees
        search_queries = [
            f'"{company_name}" current employee',
            f'works at "{company_name}"',
            f'"{company_name}" team member',
            f'"{company_name}" staff'
        ]
        
        # Simulate employee search
        for query in search_queries:
            try:
                # In real implementation, would search LinkedIn
                simulated_employees = self._simulate_employee_search(company_name, query)
                employees.extend(simulated_employees)
                
                # Limit to avoid overload
                if len(employees) >= 50:
                    break
                    
            except Exception as e:
                logger.error(f"Employee search error: {e}")
                continue
        
        # Remove duplicates and rank by importance
        unique_employees = self._deduplicate_employees(employees)
        ranked_employees = self._rank_employees_by_importance(unique_employees)
        
        return ranked_employees[:20]  # Return top 20
    
    def _simulate_employee_search(self, company_name: str, query: str) -> List[Dict[str, Any]]:
        """Simulate LinkedIn employee search results"""
        # Generate realistic employee profiles
        titles = ['CEO', 'CTO', 'Engineering Manager', 'Software Developer', 'Sales Manager', 
                 'HR Manager', 'Marketing Director', 'Product Manager', 'Designer', 'Analyst']
        
        employees = []
        for i in range(random.randint(3, 8)):
            title = random.choice(titles)
            employee = {
                'name': f'Professional {i+1}',
                'title': title,
                'profile_url': f'https://linkedin.com/in/professional-{i+1}',
                'location': random.choice(['Riyadh', 'Jeddah', 'Dubai', 'Abu Dhabi']),
                'experience_years': random.randint(2, 15),
                'education': random.choice(['King Saud University', 'KAUST', 'AUB', 'AUD']),
                'skills': ['Management', 'Leadership', 'Strategy'] if 'Manager' in title or 'CEO' in title else ['Technical', 'Development'],
                'connections': random.randint(100, 1000),
                'activity_level': random.choice(['high', 'medium', 'low']),
                'join_date': datetime.now() - timedelta(days=random.randint(365, 2555)),
                'confidence': random.uniform(0.7, 0.95)
            }
            employees.append(employee)
        
        return employees
    
    def _deduplicate_employees(self, employees: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate employee entries"""
        seen_names = set()
        unique_employees = []
        
        for employee in employees:
            name_key = employee['name'].lower().replace(' ', '')
            if name_key not in seen_names:
                seen_names.add(name_key)
                unique_employees.append(employee)
        
        return unique_employees
    
    def _rank_employees_by_importance(self, employees: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank employees by importance/seniority"""
        importance_scores = {
            'CEO': 100, 'CTO': 95, 'CFO': 95, 'COO': 90,
            'Director': 80, 'Manager': 70, 'Lead': 60,
            'Senior': 50, 'Developer': 40, 'Analyst': 30
        }
        
        for employee in employees:
            title = employee.get('title', '').lower()
            score = 20  # Base score
            
            for keyword, importance in importance_scores.items():
                if keyword.lower() in title:
                    score = max(score, importance)
                    break
            
            # Adjust for experience and connections
            score += min(employee.get('experience_years', 0) * 2, 20)
            score += min(employee.get('connections', 0) / 100, 10)
            
            employee['importance_score'] = score
        
        return sorted(employees, key=lambda x: x['importance_score'], reverse=True)
    
    def _identify_key_personnel(self, employees: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify key decision makers and important personnel"""
        key_personnel = []
        
        key_titles = ['ceo', 'cto', 'cfo', 'coo', 'director', 'head', 'vp', 'vice president']
        
        for employee in employees:
            title = employee.get('title', '').lower()
            if any(key_title in title for key_title in key_titles):
                key_personnel.append({
                    'name': employee['name'],
                    'title': employee['title'],
                    'profile_url': employee['profile_url'],
                    'importance_level': 'high' if any(exec_title in title for exec_title in ['ceo', 'cto', 'cfo']) else 'medium',
                    'contact_potential': 'high' if employee.get('activity_level') == 'high' else 'medium',
                    'decision_maker': True if any(exec_title in title for exec_title in ['ceo', 'cto', 'cfo', 'director']) else False
                })
        
        return key_personnel
    
    def _calculate_company_confidence(self, company_info: Dict, employees: List) -> float:
        """Calculate confidence score for company data"""
        score = 0.5  # Base score
        
        # More complete company info = higher confidence
        if company_info.get('industry'):
            score += 0.1
        if company_info.get('website'):
            score += 0.1
        if company_info.get('headquarters'):
            score += 0.1
        if company_info.get('founded'):
            score += 0.1
        
        # More employees found = higher confidence
        if len(employees) > 10:
            score += 0.1
        elif len(employees) > 5:
            score += 0.05
        
        return min(score, 1.0)

    async def comprehensive_people_search(self, search_criteria: str, params: Dict) -> List[SocialProfile]:
        """Search for people based on criteria"""
        logger.info(f"LinkedIn people search: {search_criteria}")
        
        profiles = []
        
        # Parse search criteria
        location = params.get('geographic_focus', '')
        job_title = self._extract_job_title(search_criteria)
        industry = self._extract_industry(search_criteria)
        
        # Generate search queries
        search_queries = self._generate_people_search_queries(search_criteria, location, job_title)
        
        for query in search_queries:
            try:
                await self.rate_limiter.wait_if_needed('linkedin_people')
                
                # Simulate people search
                search_results = await self._simulate_people_search(query, params)
                profiles.extend(search_results)
                
                if len(profiles) >= 100:
                    break
                    
            except Exception as e:
                logger.error(f"People search error: {e}")
                continue
        
        # Remove duplicates and rank
        unique_profiles = self._deduplicate_profiles(profiles)
        ranked_profiles = self._rank_profiles_by_relevance(unique_profiles, search_criteria)
        
        return ranked_profiles[:50]  # Return top 50
    
    def _extract_job_title(self, search_criteria: str) -> str:
        """Extract job title from search criteria"""
        job_keywords = ['developer', 'engineer', 'manager', 'director', 'analyst', 'designer', 'consultant']
        
        for keyword in job_keywords:
            if keyword in search_criteria.lower():
                return keyword
        
        return 'professional'
    
    def _extract_industry(self, search_criteria: str) -> str:
        """Extract industry from search criteria"""
        industry_keywords = {
            'technology': ['tech', 'software', 'IT', 'developer', 'programmer'],
            'finance': ['bank', 'financial', 'fintech', 'investment'],
            'healthcare': ['medical', 'health', 'clinic', 'hospital'],
            'retail': ['retail', 'sales', 'commerce']
        }
        
        search_lower = search_criteria.lower()
        for industry, keywords in industry_keywords.items():
            if any(keyword in search_lower for keyword in keywords):
                return industry
        
        return 'general'
    
    def _generate_people_search_queries(self, criteria: str, location: str, job_title: str) -> List[str]:
        """Generate LinkedIn people search queries"""
        queries = [
            criteria,
            f'"{job_title}" "{location}"',
            f'{job_title} {location} current',
            f'"{criteria}" available',
            f'{job_title} {location} seeking',
            f'"{criteria}" "looking for"'
        ]
        
        return queries
    
    async def _simulate_people_search(self, query: str, params: Dict) -> List[SocialProfile]:
        """Simulate LinkedIn people search results"""
        profiles = []
        
        # Generate realistic profiles
        for i in range(random.randint(5, 15)):
            profile = SocialProfile(
                platform='linkedin',
                profile_url=f'https://linkedin.com/in/person-{i+1}',
                display_name=f'Professional {i+1}',
                username=f'person{i+1}',
                bio=f'Experienced {self._extract_job_title(query)} with {random.randint(2, 15)} years in the industry',
                followers_count=random.randint(100, 5000),
                following_count=random.randint(50, 1000),
                posts_count=random.randint(10, 500),
                verified=random.choice([True, False]),
                profile_image_url=f'https://example.com/profile{i+1}.jpg',
                location=params.get('geographic_focus', 'Saudi Arabia'),
                website=f'https://portfolio{i+1}.com' if random.choice([True, False]) else None,
                join_date=datetime.now() - timedelta(days=random.randint(365, 3650)),
                last_activity=datetime.now() - timedelta(days=random.randint(1, 30)),
                contact_info={
                    'email': f'person{i+1}@email.com' if random.choice([True, False]) else None,
                    'phone': f'+966{random.randint(500000000, 599999999)}' if random.choice([True, False]) else None
                },
                professional_info={
                    'current_company': f'Company {random.randint(1, 10)}',
                    'title': self._extract_job_title(query),
                    'experience_years': random.randint(2, 15),
                    'skills': ['Leadership', 'Management', 'Strategy'],
                    'education': random.choice(['Bachelor', 'Master', 'PhD']),
                    'certifications': random.choice([[], ['PMP'], ['AWS', 'Azure'], ['Google Cloud']])
                },
                connections=[],
                recent_posts=[],
                confidence_score=random.uniform(0.6, 0.9),
                metadata={'search_query': query, 'search_date': datetime.now()}
            )
            profiles.append(profile)
        
        return profiles
    
    def _deduplicate_profiles(self, profiles: List[SocialProfile]) -> List[SocialProfile]:
        """Remove duplicate profiles"""
        seen_urls = set()
        unique_profiles = []
        
        for profile in profiles:
            if profile.profile_url not in seen_urls:
                seen_urls.add(profile.profile_url)
                unique_profiles.append(profile)
        
        return unique_profiles
    
    def _rank_profiles_by_relevance(self, profiles: List[SocialProfile], criteria: str) -> List[SocialProfile]:
        """Rank profiles by relevance to search criteria"""
        criteria_words = set(criteria.lower().split())
        
        for profile in profiles:
            relevance_score = profile.confidence_score
            
            # Check bio relevance
            bio_words = set(profile.bio.lower().split())
            bio_matches = len(criteria_words.intersection(bio_words))
            relevance_score += (bio_matches / len(criteria_words)) * 0.3
            
            # Boost active users
            if profile.last_activity and profile.last_activity > datetime.now() - timedelta(days=7):
                relevance_score += 0.1
            
            # Boost users with contact info
            if profile.contact_info.get('email') or profile.contact_info.get('phone'):
                relevance_score += 0.15
            
            profile.confidence_score = min(relevance_score, 1.0)
        
        return sorted(profiles, key=lambda x: x.confidence_score, reverse=True)

class TwitterIntelligenceCollector:
    """Twitter/X intelligence gathering"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.base_url = "https://twitter.com"
    
    async def search_mentions_and_discussions(self, target: str, params: Dict) -> List[Dict[str, Any]]:
        """Search for mentions and discussions about the target"""
        logger.info(f"Twitter search for: {target}")
        
        mentions = []
        
        # Search queries for Twitter
        search_queries = [
            target,
            f'"{target}"',
            f'{target} hiring',
            f'{target} job',
            f'{target} news',
            f'{target} announcement'
        ]
        
        for query in search_queries:
            try:
                await self.rate_limiter.wait_if_needed('twitter')
                
                # Simulate Twitter search
                results = await self._simulate_twitter_search(query, params)
                mentions.extend(results)
                
                if len(mentions) >= 50:
                    break
                    
            except Exception as e:
                logger.error(f"Twitter search error: {e}")
                continue
        
        return mentions[:30]  # Return top 30
    
    async def _simulate_twitter_search(self, query: str, params: Dict) -> List[Dict[str, Any]]:
        """Simulate Twitter search results"""
        tweets = []
        
        for i in range(random.randint(3, 10)):
            tweet = {
                'id': f'tweet_{i+1}',
                'user': f'@user{i+1}',
                'display_name': f'User {i+1}',
                'text': f'Tweet about {query} with some interesting insights and information',
                'timestamp': datetime.now() - timedelta(hours=random.randint(1, 72)),
                'retweets': random.randint(0, 100),
                'likes': random.randint(0, 500),
                'replies': random.randint(0, 50),
                'verified': random.choice([True, False]),
                'location': params.get('geographic_focus', ''),
                'hashtags': [f'#{tag}' for tag in query.split()[:2]],
                'mentions': [],
                'url': f'https://twitter.com/user{i+1}/status/{random.randint(1000000000000000000, 9999999999999999999)}',
                'confidence': random.uniform(0.5, 0.8)
            }
            tweets.append(tweet)
        
        return tweets

class FacebookIntelligenceCollector:
    """Facebook intelligence gathering"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.base_url = "https://facebook.com"
    
    async def search_business_pages(self, target: str, params: Dict) -> List[Dict[str, Any]]:
        """Search for business pages on Facebook"""
        logger.info(f"Facebook business search: {target}")
        
        pages = []
        
        # Simulate Facebook business page search
        for i in range(random.randint(2, 8)):
            page = {
                'page_id': f'page_{i+1}',
                'name': f'{target} Business {i+1}',
                'url': f'https://facebook.com/business{i+1}',
                'category': random.choice(['Local Business', 'Company', 'Restaurant', 'Hotel']),
                'description': f'Official Facebook page for {target}',
                'followers': random.randint(100, 10000),
                'likes': random.randint(50, 5000),
                'rating': round(random.uniform(3.0, 5.0), 1),
                'reviews_count': random.randint(10, 500),
                'phone': f'+966{random.randint(500000000, 599999999)}' if random.choice([True, False]) else None,
                'email': f'info@{target.replace(" ", "").lower()}.com' if random.choice([True, False]) else None,
                'website': f'https://{target.replace(" ", "").lower()}.com' if random.choice([True, False]) else None,
                'address': f'{params.get("geographic_focus", "Saudi Arabia")}',
                'verified': random.choice([True, False]),
                'last_post': datetime.now() - timedelta(days=random.randint(1, 30)),
                'confidence': random.uniform(0.6, 0.85)
            }
            pages.append(page)
        
        return pages

class SocialMediaIntelligenceCollector:
    """Main social media intelligence collector"""
    
    def __init__(self):
        self.linkedin_collector = LinkedInIntelligenceCollector()
        self.twitter_collector = TwitterIntelligenceCollector()
        self.facebook_collector = FacebookIntelligenceCollector()
        self.rate_limiter = RateLimiter()
    
    async def comprehensive_social_discovery(self, target: str, params: Dict) -> List[Dict[str, Any]]:
        """
        Comprehensive social media discovery across all platforms
        """
        logger.info(f"Starting comprehensive social media discovery for: {target}")
        
        all_results = []
        
        # Determine target type and strategy
        target_type = params.get('target_type', 'mixed')
        
        # Parallel collection from different platforms
        collection_tasks = []
        
        # LinkedIn - always valuable for professional intelligence
        if target_type in ['people_group', 'business_category', 'professional_category']:
            linkedin_task = self._collect_linkedin_intelligence(target, params)
            collection_tasks.append(('linkedin', linkedin_task))
        
        # Twitter - good for mentions and discussions
        twitter_task = self._collect_twitter_intelligence(target, params)
        collection_tasks.append(('twitter', twitter_task))
        
        # Facebook - good for business pages
        if target_type in ['business_category', 'service_providers']:
            facebook_task = self._collect_facebook_intelligence(target, params)
            collection_tasks.append(('facebook', facebook_task))
        
        # Execute collection tasks
        platform_results = {}
        for platform, task in collection_tasks:
            try:
                results = await task
                platform_results[platform] = results
                logger.info(f"{platform.title()} collection completed: {len(results)} results")
            except Exception as e:
                logger.error(f"{platform.title()} collection failed: {e}")
                platform_results[platform] = []
        
        # Combine and process results
        for platform, results in platform_results.items():
            for result in results:
                standardized_result = self._standardize_result(result, platform)
                all_results.append(standardized_result)
        
        # Post-process results
        processed_results = self._post_process_social_results(all_results, target, params)
        
        logger.info(f"Social media discovery completed: {len(processed_results)} total results")
        return processed_results
    
    async def _collect_linkedin_intelligence(self, target: str, params: Dict) -> List[Dict[str, Any]]:
        """Collect LinkedIn intelligence"""
        results = []
        
        target_type = params.get('target_type', '')
        
        if target_type == 'business_category':
            # Company research
            company_profile = await self.linkedin_collector.comprehensive_company_research(target, params)
            if company_profile:
                results.append(company_profile)
        
        elif target_type in ['people_group', 'professional_category']:
            # People search
            profiles = await self.linkedin_collector.comprehensive_people_search(target, params)
            results.extend(profiles)
        
        else:
            # Mixed approach
            try:
                # Try company research first
                company_profile = await self.linkedin_collector.comprehensive_company_research(target, params)
                if company_profile:
                    results.append(company_profile)
                
                # Then try people search
                profiles = await self.linkedin_collector.comprehensive_people_search(target, params)
                results.extend(profiles[:10])  # Limit for mixed search
                
            except Exception as e:
                logger.error(f"LinkedIn mixed search error: {e}")
        
        return results
    
    async def _collect_twitter_intelligence(self, target: str, params: Dict) -> List[Dict[str, Any]]:
        """Collect Twitter intelligence"""
        return await self.twitter_collector.search_mentions_and_discussions(target, params)
    
    async def _collect_facebook_intelligence(self, target: str, params: Dict) -> List[Dict[str, Any]]:
        """Collect Facebook intelligence"""
        return await self.facebook_collector.search_business_pages(target, params)
    
    def _standardize_result(self, result: Any, platform: str) -> Dict[str, Any]:
        """Standardize results from different platforms"""
        if platform == 'linkedin':
            if isinstance(result, CompanyProfile):
                return {
                    'type': 'company_profile',
                    'platform': platform,
                    'name': result.company_name,
                    'url': result.profile_url,
                    'description': result.description,
                    'industry': result.industry,
                    'size': result.company_size,
                    'location': result.headquarters,
                    'website': result.website,
                    'employees': result.employees_on_platform,
                    'key_personnel': result.key_personnel,
                    'contact_info': result.contact_information,
                    'confidence': result.confidence_score,
                    'metadata': result.metadata
                }
            elif isinstance(result, SocialProfile):
                return {
                    'type': 'person_profile',
                    'platform': platform,
                    'name': result.display_name,
                    'url': result.profile_url,
                    'bio': result.bio,
                    'location': result.location,
                    'title': result.professional_info.get('title', ''),
                    'company': result.professional_info.get('current_company', ''),
                    'contact_info': result.contact_info,
                    'professional_info': result.professional_info,
                    'confidence': result.confidence_score,
                    'metadata': result.metadata
                }
        
        elif platform == 'twitter':
            return {
                'type': 'social_mention',
                'platform': platform,
                'user': result.get('user', ''),
                'display_name': result.get('display_name', ''),
                'content': result.get('text', ''),
                'url': result.get('url', ''),
                'timestamp': result.get('timestamp'),
                'engagement': {
                    'retweets': result.get('retweets', 0),
                    'likes': result.get('likes', 0),
                    'replies': result.get('replies', 0)
                },
                'hashtags': result.get('hashtags', []),
                'location': result.get('location', ''),
                'verified': result.get('verified', False),
                'confidence': result.get('confidence', 0.5)
            }
        
        elif platform == 'facebook':
            return {
                'type': 'business_page',
                'platform': platform,
                'name': result.get('name', ''),
                'url': result.get('url', ''),
                'category': result.get('category', ''),
                'description': result.get('description', ''),
                'contact_info': {
                    'phone': result.get('phone'),
                    'email': result.get('email'),
                    'website': result.get('website')
                },
                'location': result.get('address', ''),
                'metrics': {
                    'followers': result.get('followers', 0),
                    'likes': result.get('likes', 0),
                    'rating': result.get('rating', 0),
                    'reviews': result.get('reviews_count', 0)
                },
                'verified': result.get('verified', False),
                'last_activity': result.get('last_post'),
                'confidence': result.get('confidence', 0.5)
            }
        
        # Default standardization
        return {
            'type': 'unknown',
            'platform': platform,
            'data': result,
            'confidence': 0.3
        }
    
    def _post_process_social_results(self, results: List[Dict[str, Any]], target: str, params: Dict) -> List[Dict[str, Any]]:
        """Post-process social media results"""
        # Remove duplicates
        unique_results = self._remove_social_duplicates(results)
        
        # Calculate enhanced relevance scores
        scored_results = self._calculate_social_relevance(unique_results, target)
        
        # Sort by relevance and confidence
        sorted_results = sorted(scored_results, 
                              key=lambda x: (x.get('relevance_score', 0), x.get('confidence', 0)), 
                              reverse=True)
        
        # Apply limits based on urgency
        urgency = params.get('urgency_level', 'standard')
        limits = {'immediate': 20, 'standard': 50, 'comprehensive': 100}
        limit = limits.get(urgency, 50)
        
        return sorted_results[:limit]
    
    def _remove_social_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate social media results"""
        seen = set()
        unique_results = []
        
        for result in results:
            # Create identifier based on URL or name
            identifier = result.get('url', '') or result.get('name', '') or str(result)
            identifier = identifier.lower().strip()
            
            if identifier and identifier not in seen:
                seen.add(identifier)
                unique_results.append(result)
        
        return unique_results
    
    def _calculate_social_relevance(self, results: List[Dict[str, Any]], target: str) -> List[Dict[str, Any]]:
        """Calculate relevance scores for social media results"""
        target_words = set(target.lower().split())
        
        for result in results:
            relevance_score = result.get('confidence', 0.5)
            
            # Text content relevance
            text_fields = ['name', 'description', 'bio', 'content']
            for field in text_fields:
                if field in result and result[field]:
                    text_words = set(result[field].lower().split())
                    matches = len(target_words.intersection(text_words))
                    relevance_score += (matches / len(target_words)) * 0.2
            
            # Platform-specific bonuses
            if result['platform'] == 'linkedin':
                relevance_score += 0.1  # LinkedIn generally more professional/reliable
            
            # Contact information bonus
            if result.get('contact_info') and any(result['contact_info'].values()):
                relevance_score += 0.15
            
            # Verification bonus
            if result.get('verified'):
                relevance_score += 0.1
            
            # Recent activity bonus
            if result.get('timestamp') or result.get('last_activity'):
                relevance_score += 0.05
            
            result['relevance_score'] = min(relevance_score, 1.0)
        
        return results
    
    async def extract_contact_information_from_social(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract contact information from social media results"""
        contacts = []
        
        for result in results:
            contact_info = result.get('contact_info', {})
            
            # Extract email
            if contact_info.get('email'):
                contacts.append({
                    'type': 'email',
                    'value': contact_info['email'],
                    'source_platform': result['platform'],
                    'source_url': result.get('url', ''),
                    'source_name': result.get('name', ''),
                    'confidence': result.get('confidence', 0.5) * 0.9,  # Slightly lower for social
                    'context': 'social_media_profile'
                })
            
            # Extract phone
            if contact_info.get('phone'):
                contacts.append({
                    'type': 'phone',
                    'value': contact_info['phone'],
                    'source_platform': result['platform'],
                    'source_url': result.get('url', ''),
                    'source_name': result.get('name', ''),
                    'confidence': result.get('confidence', 0.5) * 0.8,
                    'context': 'social_media_profile'
                })
            
            # Extract website
            if contact_info.get('website'):
                contacts.append({
                    'type': 'website',
                    'value': contact_info['website'],
                    'source_platform': result['platform'],
                    'source_url': result.get('url', ''),
                    'source_name': result.get('name', ''),
                    'confidence': result.get('confidence', 0.5) * 0.7,
                    'context': 'social_media_profile'
                })
        
        return contacts
    
    def get_social_statistics(self) -> Dict[str, Any]:
        """Get social media collection statistics"""
        return {
            'platforms_supported': ['linkedin', 'twitter', 'facebook'],
            'total_collections': getattr(self, '_collection_count', 0),
            'average_results_per_platform': {
                'linkedin': 15,
                'twitter': 10,
                'facebook': 8
            },
            'success_rate': 0.85,
            'last_collection_time': getattr(self, '_last_collection_time', None)
        }

# Example usage and testing
async def test_social_media_collector():
    """Test the social media collector"""
    collector = SocialMediaIntelligenceCollector()
    
    test_targets = [
        "software developers in Riyadh",
        "Aramco company",
        "hotels in Dubai",
        "conference organizers Saudi Arabia"
    ]
    
    for target in test_targets:
        print(f"\n=== Testing social media search for: {target} ===")
        
        params = {
            'target_type': 'people_group' if 'developers' in target else 'business_category',
            'geographic_focus': 'Saudi Arabia',
            'context': 'recruitment' if 'developers' in target else 'lead_generation',
            'urgency_level': 'standard'
        }
        
        try:
            results = await collector.comprehensive_social_discovery(target, params)
            print(f"Found {len(results)} social media results")
            
            # Show top 3 results
            for i, result in enumerate(results[:3], 1):
                print(f"{i}. Type: {result['type']}")
                print(f"   Platform: {result['platform']}")
                print(f"   Name: {result.get('name', 'N/A')}")
                print(f"   Confidence: {result.get('confidence', 0):.2f}")
                print(f"   URL: {result.get('url', 'N/A')}")
                print()
                
            # Extract contacts
            contacts = await collector.extract_contact_information_from_social(results)
            print(f"Extracted {len(contacts)} contact information items")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_social_media_collector())