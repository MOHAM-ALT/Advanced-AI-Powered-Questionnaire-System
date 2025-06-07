#!/usr/bin/env python3
"""
Advanced Discovery Engine - Intelligent OSINT Coordinator
File Location: core/discovery_engine.py
The Brain of the OSINT System - Analyzes targets and coordinates multi-source intelligence gathering
"""

import asyncio
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import logging
from pathlib import Path

# Import collectors (will be implemented)
from collectors.search_engines import IntelligentSearchCollector
from collectors.social_media import SocialMediaIntelligenceCollector
from collectors.business_directories import BusinessDirectoryCollector
from collectors.job_portals_collector import JobPortalsCollector
from collectors.specialized_tools_collector import SpecializedToolsCollector

logger = logging.getLogger(__name__)

class TargetType(Enum):
    """Types of intelligence targets"""
    PEOPLE_GROUP = "people_group"  # "unemployed developers in Riyadh"
    BUSINESS_CATEGORY = "business_category"  # "hotels in Riyadh"
    SERVICE_PROVIDERS = "service_providers"  # "conference organizers in Gulf"
    PROFESSIONAL_CATEGORY = "professional_category"  # "delivery drivers"
    DOMAIN_ENTITY = "domain_entity"  # "company.com"
    PERSON_INDIVIDUAL = "person_individual"  # "John Smith CEO"
    TOPIC_RESEARCH = "topic_research"  # "AI companies in Saudi Arabia"
    MIXED_INTELLIGENCE = "mixed_intelligence"  # Complex multi-target research

class IntelligenceScope(Enum):
    """Scope of intelligence gathering"""
    LOCAL = "local"  # City/region level
    NATIONAL = "national"  # Country level
    REGIONAL = "regional"  # Multi-country region
    GLOBAL = "global"  # Worldwide scope

class DataPriority(Enum):
    """Priority levels for different data types"""
    CRITICAL = "critical"  # Contact info, key personnel
    HIGH = "high"  # Business details, roles
    MEDIUM = "medium"  # Background info, context
    LOW = "low"  # Additional context, nice-to-have

@dataclass
class DiscoveryTarget:
    """Enhanced target definition for intelligent discovery"""
    primary_identifier: str  # User input: "hotels in Riyadh"
    target_type: TargetType
    context: str  # From questionnaire: lead_generation, recruitment, etc.
    priority_data: List[str]  # What user wants most
    geographic_focus: str  # "Riyadh", "Saudi Arabia", "Gulf Region"
    industry_keywords: List[str]  # Auto-generated keywords
    urgency_level: str  # "immediate", "standard", "comprehensive"
    intelligence_scope: IntelligenceScope
    search_depth: str  # "quick", "standard", "comprehensive"
    risk_tolerance: str  # "low", "medium", "high"
    custom_requirements: List[str]  # Special requests from user

@dataclass
class IntelligenceResult:
    """Standardized intelligence result"""
    id: str
    investigation_id: int
    data_type: str  # "email", "phone", "business_profile", "person_profile"
    value: str  # The actual data
    confidence: float  # 0.0 to 1.0
    source_method: str  # "google_search", "linkedin_mining", etc.
    source_url: str
    context: Dict[str, Any]  # Additional context about the finding
    timestamp: datetime
    validation_status: str  # "validated", "pending", "failed"
    enrichment_data: Dict[str, Any]  # Additional details
    geographic_location: Optional[str]
    relevance_score: float  # How relevant to the original query

@dataclass
class DiscoveryStrategy:
    """Comprehensive discovery strategy"""
    target: DiscoveryTarget
    collection_methods: List[str]  # Which collectors to use
    search_keywords: List[str]  # Optimized keywords
    source_priorities: Dict[str, int]  # Priority order for sources
    time_allocation: Dict[str, int]  # Minutes per source
    parallel_execution: bool
    validation_level: str  # "basic", "standard", "comprehensive"
    expected_result_types: List[str]
    risk_mitigation: Dict[str, Any]

class AdvancedDiscoveryEngine:
    """
    Intelligent OSINT Discovery Engine
    The brain that analyzes targets and coordinates multi-source intelligence gathering
    """
    
    def __init__(self):
        self.collectors = self._initialize_collectors()
        self.target_patterns = self._load_target_patterns()
        self.keyword_generators = self._initialize_keyword_generators()
        self.active_investigations = {}
        
    def _initialize_collectors(self) -> Dict[str, Any]:
        """Initialize all intelligence collectors"""
        return {
            'search_engines': IntelligentSearchCollector(),
            'social_media': SocialMediaIntelligenceCollector(), 
            'business_directories': BusinessDirectoryCollector(),
            'job_portals': JobPortalsCollector(),
            'specialized_tools': SpecializedToolsCollector()
        }
    
    def _load_target_patterns(self) -> Dict[str, Any]:
        """Load patterns for target type detection"""
        return {
            'people_patterns': [
                r'\b(unemployed|jobless|seeking|looking for work|available)\b.*\b(developers?|engineers?|managers?|workers?)\b',
                r'\b(developers?|engineers?|professionals?)\b.*\b(in|from|at)\b.*\b(riyadh|jeddah|dubai)\b',
                r'\b(job seekers?|candidates?|applicants?)\b',
                r'\b(freelancers?|contractors?|consultants?)\b',
                r'\b(delivery|driver|courier)\b.*\b(workers?|staff|personnel)\b'
            ],
            'business_patterns': [
                r'\b(hotels?|restaurants?|companies?|businesses?)\b.*\b(in|at|from)\b.*\b(riyadh|dubai|saudi)\b',
                r'\b(conference|event|wedding)\b.*\b(organizers?|planners?|companies?)\b',
                r'\b(tech|technology|software|IT)\b.*\b(companies?|firms?|startups?)\b',
                r'\b(retail|shops?|stores?|outlets?)\b'
            ],
            'service_patterns': [
                r'\b(catering|logistics|transportation|delivery)\b.*\b(services?|companies?)\b',
                r'\b(marketing|advertising|consulting)\b.*\b(agencies?|firms?)\b',
                r'\b(legal|law|accounting|finance)\b.*\b(firms?|offices?)\b'
            ],
            'topic_patterns': [
                r'\b(artificial intelligence|AI|machine learning|ML)\b.*\b(companies?|research|development)\b',
                r'\b(renewable energy|solar|wind|green technology)\b',
                r'\b(fintech|blockchain|cryptocurrency|digital banking)\b'
            ]
        }
    
    def _initialize_keyword_generators(self) -> Dict[str, Any]:
        """Initialize intelligent keyword generation"""
        return {
            'synonyms': {
                'hotels': ['accommodation', 'lodging', 'hospitality', 'resorts', 'inns'],
                'restaurants': ['dining', 'eateries', 'food service', 'catering', 'cafes'],
                'developers': ['programmers', 'software engineers', 'coders', 'technical staff'],
                'unemployed': ['jobless', 'seeking employment', 'available for work', 'between jobs'],
                'companies': ['businesses', 'enterprises', 'corporations', 'firms', 'organizations']
            },
            'location_variants': {
                'riyadh': ['الرياض', 'Ar Riyadh', 'Riyadh City', 'KSA Riyadh'],
                'saudi arabia': ['KSA', 'Saudi', 'Kingdom of Saudi Arabia', 'المملكة العربية السعودية'],
                'dubai': ['Dubai UAE', 'Emirates Dubai', 'دبي'],
                'gulf': ['GCC', 'Gulf Region', 'Gulf States', 'Arabian Gulf']
            },
            'industry_terms': {
                'technology': ['tech', 'IT', 'software', 'digital', 'innovation', 'startup'],
                'hospitality': ['tourism', 'travel', 'leisure', 'hospitality industry'],
                'finance': ['banking', 'financial services', 'fintech', 'investment']
            }
        }

    async def analyze_target_and_strategize(self, user_input: str, questionnaire_data: Dict) -> DiscoveryStrategy:
        """
        Analyze user input and create intelligent discovery strategy
        This is the brain function that understands what the user wants
        """
        logger.info(f"Analyzing target: {user_input}")
        
        # Step 1: Detect target type using AI pattern matching
        target_type = self._detect_target_type(user_input)
        
        # Step 2: Extract geographic and industry context
        geographic_info = self._extract_geographic_context(user_input)
        industry_context = self._extract_industry_context(user_input)
        
        # Step 3: Generate intelligent keywords
        keywords = await self._generate_intelligent_keywords(user_input, target_type, industry_context)
        
        # Step 4: Create discovery target
        target = DiscoveryTarget(
            primary_identifier=user_input,
            target_type=target_type,
            context=questionnaire_data.get('context', 'general_research'),
            priority_data=questionnaire_data.get('data_priorities', ['contact_info']),
            geographic_focus=geographic_info['primary_location'],
            industry_keywords=keywords,
            urgency_level=questionnaire_data.get('urgency', 'standard'),
            intelligence_scope=self._determine_scope(geographic_info),
            search_depth=questionnaire_data.get('search_depth', 'standard'),
            risk_tolerance=questionnaire_data.get('risk_tolerance', 'medium'),
            custom_requirements=questionnaire_data.get('custom_requirements', [])
        )
        
        # Step 5: Create optimized strategy
        strategy = await self._create_discovery_strategy(target, questionnaire_data)
        
        logger.info(f"Strategy created: {len(strategy.collection_methods)} methods, {len(strategy.search_keywords)} keywords")
        return strategy

    def _detect_target_type(self, user_input: str) -> TargetType:
        """Intelligent target type detection using pattern matching"""
        input_lower = user_input.lower()
        
        # Check for people/job-related patterns
        for pattern in self.target_patterns['people_patterns']:
            if re.search(pattern, input_lower):
                return TargetType.PEOPLE_GROUP
        
        # Check for business patterns
        for pattern in self.target_patterns['business_patterns']:
            if re.search(pattern, input_lower):
                return TargetType.BUSINESS_CATEGORY
        
        # Check for service patterns
        for pattern in self.target_patterns['service_patterns']:
            if re.search(pattern, input_lower):
                return TargetType.SERVICE_PROVIDERS
        
        # Check for topic patterns
        for pattern in self.target_patterns['topic_patterns']:
            if re.search(pattern, input_lower):
                return TargetType.TOPIC_RESEARCH
        
        # Domain detection
        if re.search(r'\b[a-zA-Z0-9-]+\.[a-zA-Z]{2,}\b', input_lower):
            return TargetType.DOMAIN_ENTITY
        
        # Default to mixed intelligence
        return TargetType.MIXED_INTELLIGENCE

    def _extract_geographic_context(self, user_input: str) -> Dict[str, Any]:
        """Extract geographic information from user input"""
        input_lower = user_input.lower()
        geographic_info = {
            'primary_location': 'global',
            'detected_locations': [],
            'scope': IntelligenceScope.GLOBAL
        }
        
        # Common location patterns
        location_patterns = {
            'riyadh': {'name': 'Riyadh', 'country': 'Saudi Arabia', 'scope': IntelligenceScope.LOCAL},
            'jeddah': {'name': 'Jeddah', 'country': 'Saudi Arabia', 'scope': IntelligenceScope.LOCAL},
            'dubai': {'name': 'Dubai', 'country': 'UAE', 'scope': IntelligenceScope.LOCAL},
            'saudi': {'name': 'Saudi Arabia', 'country': 'Saudi Arabia', 'scope': IntelligenceScope.NATIONAL},
            'uae': {'name': 'UAE', 'country': 'UAE', 'scope': IntelligenceScope.NATIONAL},
            'gulf': {'name': 'Gulf Region', 'country': 'GCC', 'scope': IntelligenceScope.REGIONAL},
            'gcc': {'name': 'GCC Countries', 'country': 'GCC', 'scope': IntelligenceScope.REGIONAL}
        }
        
        for location_key, location_data in location_patterns.items():
            if location_key in input_lower:
                geographic_info['primary_location'] = location_data['name']
                geographic_info['detected_locations'].append(location_data)
                geographic_info['scope'] = location_data['scope']
                break
        
        return geographic_info

    def _extract_industry_context(self, user_input: str) -> List[str]:
        """Extract industry context from user input"""
        input_lower = user_input.lower()
        detected_industries = []
        
        industry_keywords = {
            'technology': ['tech', 'software', 'developer', 'programmer', 'IT', 'AI', 'digital'],
            'hospitality': ['hotel', 'restaurant', 'tourism', 'travel', 'hospitality'],
            'finance': ['bank', 'financial', 'fintech', 'investment', 'accounting'],
            'healthcare': ['medical', 'health', 'clinic', 'hospital', 'pharmaceutical'],
            'retail': ['retail', 'shop', 'store', 'commerce', 'sales'],
            'logistics': ['delivery', 'shipping', 'transport', 'logistics', 'courier'],
            'events': ['conference', 'event', 'wedding', 'catering', 'planning']
        }
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in input_lower for keyword in keywords):
                detected_industries.append(industry)
        
        return detected_industries

    async def _generate_intelligent_keywords(self, user_input: str, target_type: TargetType, industry_context: List[str]) -> List[str]:
        """Generate intelligent search keywords based on context"""
        base_keywords = user_input.split()
        enhanced_keywords = set(base_keywords)
        
        # Add synonyms for each word
        for word in base_keywords:
            word_lower = word.lower()
            if word_lower in self.keyword_generators['synonyms']:
                enhanced_keywords.update(self.keyword_generators['synonyms'][word_lower])
        
        # Add industry-specific terms
        for industry in industry_context:
            if industry in self.keyword_generators['industry_terms']:
                enhanced_keywords.update(self.keyword_generators['industry_terms'][industry])
        
        # Add target-type specific keywords
        if target_type == TargetType.PEOPLE_GROUP:
            enhanced_keywords.update(['professionals', 'staff', 'personnel', 'team', 'employees'])
        elif target_type == TargetType.BUSINESS_CATEGORY:
            enhanced_keywords.update(['company', 'business', 'enterprise', 'organization'])
        elif target_type == TargetType.SERVICE_PROVIDERS:
            enhanced_keywords.update(['services', 'provider', 'agency', 'firm'])
        
        # Add location variants
        for word in base_keywords:
            word_lower = word.lower()
            if word_lower in self.keyword_generators['location_variants']:
                enhanced_keywords.update(self.keyword_generators['location_variants'][word_lower])
        
        return list(enhanced_keywords)

    def _determine_scope(self, geographic_info: Dict) -> IntelligenceScope:
        """Determine the appropriate intelligence scope"""
        return geographic_info.get('scope', IntelligenceScope.GLOBAL)

    async def _create_discovery_strategy(self, target: DiscoveryTarget, questionnaire_data: Dict) -> DiscoveryStrategy:
        """Create comprehensive discovery strategy"""
        
        # Determine collection methods based on target type
        collection_methods = self._select_collection_methods(target)
        
        # Set source priorities
        source_priorities = self._calculate_source_priorities(target, questionnaire_data)
        
        # Calculate time allocation
        time_allocation = self._calculate_time_allocation(target, collection_methods)
        
        # Determine expected result types
        expected_results = self._determine_expected_results(target, questionnaire_data)
        
        strategy = DiscoveryStrategy(
            target=target,
            collection_methods=collection_methods,
            search_keywords=target.industry_keywords,
            source_priorities=source_priorities,
            time_allocation=time_allocation,
            parallel_execution=len(collection_methods) > 2,
            validation_level=self._determine_validation_level(target),
            expected_result_types=expected_results,
            risk_mitigation=self._create_risk_mitigation_plan(target)
        )
        
        return strategy

    def _select_collection_methods(self, target: DiscoveryTarget) -> List[str]:
        """Select appropriate collection methods based on target type"""
        methods = []
        
        # Always include search engines for basic discovery
        methods.append('search_engines')
        
        if target.target_type in [TargetType.PEOPLE_GROUP, TargetType.PROFESSIONAL_CATEGORY]:
            methods.extend(['social_media', 'job_portals'])
        
        if target.target_type in [TargetType.BUSINESS_CATEGORY, TargetType.SERVICE_PROVIDERS]:
            methods.extend(['business_directories', 'social_media'])
        
        if target.target_type == TargetType.DOMAIN_ENTITY:
            methods.extend(['specialized_tools'])
        
        # Add comprehensive sources for deep research
        if target.search_depth == 'comprehensive':
            methods.extend(['specialized_tools'])
        
        return list(set(methods))  # Remove duplicates

    def _calculate_source_priorities(self, target: DiscoveryTarget, questionnaire_data: Dict) -> Dict[str, int]:
        """Calculate priority order for different sources"""
        priorities = {}
        
        # Base priorities
        base_priorities = {
            'search_engines': 10,
            'social_media': 8,
            'business_directories': 7,
            'job_portals': 6,
            'specialized_tools': 5
        }
        
        # Adjust based on target type
        if target.target_type in [TargetType.PEOPLE_GROUP, TargetType.PROFESSIONAL_CATEGORY]:
            base_priorities['social_media'] = 10
            base_priorities['job_portals'] = 9
        
        elif target.target_type in [TargetType.BUSINESS_CATEGORY, TargetType.SERVICE_PROVIDERS]:
            base_priorities['business_directories'] = 10
            base_priorities['search_engines'] = 9
        
        # Adjust based on context
        context = questionnaire_data.get('context', '')
        if context == 'recruitment':
            base_priorities['job_portals'] = 10
            base_priorities['social_media'] = 9
        elif context == 'lead_generation':
            base_priorities['business_directories'] = 10
            base_priorities['search_engines'] = 9
        
        return base_priorities

    def _calculate_time_allocation(self, target: DiscoveryTarget, methods: List[str]) -> Dict[str, int]:
        """Calculate time allocation for each collection method"""
        total_time_map = {
            'immediate': 15,  # 15 minutes total
            'standard': 30,   # 30 minutes total
            'comprehensive': 60  # 60 minutes total
        }
        
        total_time = total_time_map.get(target.urgency_level, 30)
        time_per_method = total_time // len(methods)
        
        allocation = {}
        for method in methods:
            allocation[method] = time_per_method
        
        return allocation

    def _determine_expected_results(self, target: DiscoveryTarget, questionnaire_data: Dict) -> List[str]:
        """Determine what types of results we expect to find"""
        expected = []
        
        # Based on target type
        if target.target_type in [TargetType.PEOPLE_GROUP, TargetType.PROFESSIONAL_CATEGORY]:
            expected.extend(['person_profiles', 'contact_info', 'professional_background'])
        
        elif target.target_type in [TargetType.BUSINESS_CATEGORY, TargetType.SERVICE_PROVIDERS]:
            expected.extend(['business_profiles', 'company_info', 'contact_info', 'reviews'])
        
        # Based on priorities
        priorities = questionnaire_data.get('data_priorities', [])
        if 'contact_info' in priorities:
            expected.extend(['emails', 'phone_numbers'])
        if 'decision_makers' in priorities:
            expected.extend(['management_info', 'key_personnel'])
        if 'social_media' in priorities:
            expected.extend(['social_profiles', 'online_presence'])
        
        return list(set(expected))

    def _determine_validation_level(self, target: DiscoveryTarget) -> str:
        """Determine appropriate validation level"""
        if target.risk_tolerance == 'low':
            return 'comprehensive'
        elif target.risk_tolerance == 'medium':
            return 'standard'
        else:
            return 'basic'

    def _create_risk_mitigation_plan(self, target: DiscoveryTarget) -> Dict[str, Any]:
        """Create risk mitigation plan for the discovery"""
        return {
            'rate_limiting': True,
            'proxy_rotation': target.risk_tolerance in ['medium', 'high'],
            'user_agent_rotation': True,
            'request_delays': {
                'low': 5,    # 5 seconds between requests
                'medium': 3, # 3 seconds between requests  
                'high': 1    # 1 second between requests
            }.get(target.risk_tolerance, 3),
            'max_retries': 3,
            'timeout_seconds': 30
        }

    async def comprehensive_discovery(self, strategy: DiscoveryStrategy) -> List[IntelligenceResult]:
        """
        Execute comprehensive discovery using the strategy
        This is where the magic happens - parallel execution across all sources
        """
        logger.info(f"Starting comprehensive discovery for: {strategy.target.primary_identifier}")
        
        # Initialize investigation tracking
        investigation_id = self._create_investigation_id()
        self.active_investigations[investigation_id] = {
            'strategy': strategy,
            'start_time': datetime.now(),
            'status': 'running',
            'results': []
        }
        
        # Prepare collection tasks
        collection_tasks = []
        
        for method in strategy.collection_methods:
            if method in self.collectors:
                task = self._create_collection_task(
                    method, 
                    strategy, 
                    investigation_id
                )
                collection_tasks.append(task)
        
        # Execute parallel collection
        if strategy.parallel_execution and len(collection_tasks) > 1:
            results = await self._execute_parallel_collection(collection_tasks)
        else:
            results = await self._execute_sequential_collection(collection_tasks)
        
        # Flatten and process results
        all_results = []
        for result_batch in results:
            if isinstance(result_batch, list):
                all_results.extend(result_batch)
            elif result_batch:
                all_results.append(result_batch)
        
        # Apply post-processing
        processed_results = await self._post_process_results(all_results, strategy)
        
        # Update investigation
        self.active_investigations[investigation_id]['status'] = 'completed'
        self.active_investigations[investigation_id]['results'] = processed_results
        self.active_investigations[investigation_id]['end_time'] = datetime.now()
        
        logger.info(f"Discovery completed: {len(processed_results)} results found")
        return processed_results

    def _create_investigation_id(self) -> str:
        """Create unique investigation ID"""
        return f"inv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_investigations)}"

    async def _create_collection_task(self, method: str, strategy: DiscoveryStrategy, investigation_id: str):
        """Create collection task for specific method"""
        collector = self.collectors[method]
        target = strategy.target
        
        # Create method-specific parameters
        params = {
            'keywords': strategy.search_keywords,
            'target_type': target.target_type.value,
            'geographic_focus': target.geographic_focus,
            'priority_data': target.priority_data,
            'time_limit': strategy.time_allocation.get(method, 10),
            'risk_mitigation': strategy.risk_mitigation
        }
        
        # Call appropriate collector method
        if method == 'search_engines':
            return await collector.intelligent_multi_engine_search(target.primary_identifier, params)
        elif method == 'social_media':
            return await collector.comprehensive_social_discovery(target.primary_identifier, params)
        elif method == 'business_directories':
            return await collector.comprehensive_directory_search(target.primary_identifier, params)
        elif method == 'job_portals':
            return await collector.comprehensive_job_portal_search(target.primary_identifier, params)
        elif method == 'specialized_tools':
            return await collector.specialized_intelligence_gathering(target.primary_identifier, params)
        else:
            logger.warning(f"Unknown collection method: {method}")
            return []

    async def _execute_parallel_collection(self, tasks: List) -> List:
        """Execute collection tasks in parallel"""
        logger.info(f"Executing {len(tasks)} collection tasks in parallel")
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Task {i} failed: {result}")
                    processed_results.append([])
                else:
                    processed_results.append(result)
            
            return processed_results
        except Exception as e:
            logger.error(f"Parallel execution failed: {e}")
            return []

    async def _execute_sequential_collection(self, tasks: List) -> List:
        """Execute collection tasks sequentially"""
        logger.info(f"Executing {len(tasks)} collection tasks sequentially")
        
        results = []
        for i, task in enumerate(tasks):
            try:
                result = await task
                results.append(result)
                logger.info(f"Task {i+1}/{len(tasks)} completed")
            except Exception as e:
                logger.error(f"Task {i+1} failed: {e}")
                results.append([])
        
        return results

    async def _post_process_results(self, results: List[IntelligenceResult], strategy: DiscoveryStrategy) -> List[IntelligenceResult]:
        """Post-process and enhance results"""
        if not results:
            return []
        
        logger.info(f"Post-processing {len(results)} results")
        
        # Remove duplicates
        unique_results = self._remove_duplicates(results)
        
        # Calculate relevance scores
        scored_results = self._calculate_relevance_scores(unique_results, strategy)
        
        # Sort by relevance and confidence
        sorted_results = sorted(scored_results, 
                              key=lambda x: (x.relevance_score, x.confidence), 
                              reverse=True)
        
        # Apply result limits based on urgency
        limit_map = {
            'immediate': 50,
            'standard': 200,
            'comprehensive': 1000
        }
        limit = limit_map.get(strategy.target.urgency_level, 200)
        
        return sorted_results[:limit]

    def _remove_duplicates(self, results: List[IntelligenceResult]) -> List[IntelligenceResult]:
        """Remove duplicate results"""
        seen = set()
        unique_results = []
        
        for result in results:
            # Create unique identifier
            identifier = f"{result.data_type}:{result.value.lower().strip()}"
            
            if identifier not in seen:
                seen.add(identifier)
                unique_results.append(result)
        
        logger.info(f"Removed {len(results) - len(unique_results)} duplicates")
        return unique_results

    def _calculate_relevance_scores(self, results: List[IntelligenceResult], strategy: DiscoveryStrategy) -> List[IntelligenceResult]:
        """Calculate relevance scores for results"""
        target_keywords = set(word.lower() for word in strategy.search_keywords)
        geographic_terms = set(word.lower() for word in strategy.target.geographic_focus.split())
        
        for result in results:
            score = 0.0
            
            # Check for keyword matches in value
            value_words = set(result.value.lower().split())
            keyword_matches = len(target_keywords.intersection(value_words))
            score += keyword_matches * 0.3
            
            # Check for geographic relevance
            geographic_matches = len(geographic_terms.intersection(value_words))
            score += geographic_matches * 0.2
            
            # Boost based on data type priority
            if result.data_type in strategy.target.priority_data:
                score += 0.5
            
            # Boost based on confidence
            score += result.confidence * 0.3
            
            # Boost recent results
            if result.timestamp and result.timestamp > datetime.now() - timedelta(days=30):
                score += 0.1
            
            result.relevance_score = min(score, 1.0)
        
        return results

    async def quick_discovery(self, target_input: str, basic_params: Dict) -> List[IntelligenceResult]:
        """
        Quick discovery mode for immediate results
        """
        logger.info(f"Starting quick discovery for: {target_input}")
        
        # Create simplified strategy
        target_type = self._detect_target_type(target_input)
        geographic_info = self._extract_geographic_context(target_input)
        keywords = await self._generate_intelligent_keywords(target_input, target_type, [])
        
        quick_target = DiscoveryTarget(
            primary_identifier=target_input,
            target_type=target_type,
            context=basic_params.get('context', 'quick_search'),
            priority_data=['contact_info', 'basic_info'],
            geographic_focus=geographic_info['primary_location'],
            industry_keywords=keywords,
            urgency_level='immediate',
            intelligence_scope=IntelligenceScope.LOCAL,
            search_depth='quick',
            risk_tolerance='medium',
            custom_requirements=[]
        )
        
        # Use only fast sources
        quick_strategy = DiscoveryStrategy(
            target=quick_target,
            collection_methods=['search_engines'],  # Only fast search
            search_keywords=keywords[:10],  # Limit keywords
            source_priorities={'search_engines': 10},
            time_allocation={'search_engines': 5},  # 5 minutes max
            parallel_execution=False,
            validation_level='basic',
            expected_result_types=['contact_info', 'basic_profiles'],
            risk_mitigation={'rate_limiting': True, 'request_delays': 2}
        )
        
        # Execute quick search
        results = await self.comprehensive_discovery(quick_strategy)
        
        # Return top 20 results for quick mode
        return results[:20]

    def get_discovery_progress(self, investigation_id: str) -> Dict[str, Any]:
        """Get progress information for active investigation"""
        if investigation_id not in self.active_investigations:
            return {'error': 'Investigation not found'}
        
        investigation = self.active_investigations[investigation_id]
        
        progress = {
            'investigation_id': investigation_id,
            'status': investigation['status'],
            'start_time': investigation['start_time'].isoformat(),
            'results_found': len(investigation['results']),
            'strategy_summary': {
                'target': investigation['strategy'].target.primary_identifier,
                'methods': investigation['strategy'].collection_methods,
                'keywords_count': len(investigation['strategy'].search_keywords)
            }
        }
        
        if investigation['status'] == 'completed':
            progress['end_time'] = investigation['end_time'].isoformat()
            progress['duration_seconds'] = (investigation['end_time'] - investigation['start_time']).total_seconds()
        
        return progress

    def get_active_investigations(self) -> List[Dict[str, Any]]:
        """Get list of all active investigations"""
        investigations = []
        
        for inv_id, investigation in self.active_investigations.items():
            investigations.append({
                'investigation_id': inv_id,
                'target': investigation['strategy'].target.primary_identifier,
                'status': investigation['status'],
                'start_time': investigation['start_time'].isoformat(),
                'results_count': len(investigation['results'])
            })
        
        return investigations

    async def cancel_investigation(self, investigation_id: str) -> bool:
        """Cancel an active investigation"""
        if investigation_id not in self.active_investigations:
            return False
        
        investigation = self.active_investigations[investigation_id]
        investigation['status'] = 'cancelled'
        investigation['end_time'] = datetime.now()
        
        logger.info(f"Investigation {investigation_id} cancelled")
        return True

    def export_investigation_results(self, investigation_id: str, format: str = 'json') -> str:
        """Export investigation results in specified format"""
        if investigation_id not in self.active_investigations:
            return None
        
        investigation = self.active_investigations[investigation_id]
        results = investigation['results']
        
        if format == 'json':
            return self._export_to_json(results, investigation)
        elif format == 'csv':
            return self._export_to_csv(results, investigation)
        elif format == 'html':
            return self._export_to_html(results, investigation)
        else:
            return None

    def _export_to_json(self, results: List[IntelligenceResult], investigation: Dict) -> str:
        """Export results to JSON format"""
        export_data = {
            'investigation_summary': {
                'target': investigation['strategy'].target.primary_identifier,
                'start_time': investigation['start_time'].isoformat(),
                'end_time': investigation.get('end_time', datetime.now()).isoformat(),
                'total_results': len(results),
                'status': investigation['status']
            },
            'results': []
        }
        
        for result in results:
            export_data['results'].append({
                'data_type': result.data_type,
                'value': result.value,
                'confidence': result.confidence,
                'relevance_score': result.relevance_score,
                'source_method': result.source_method,
                'source_url': result.source_url,
                'timestamp': result.timestamp.isoformat() if result.timestamp else None,
                'geographic_location': result.geographic_location,
                'context': result.context
            })
        
        filename = f"investigation_{investigation['strategy'].target.primary_identifier.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Save to exports directory
        exports_dir = Path("data/exports")
        exports_dir.mkdir(exist_ok=True)
        
        with open(exports_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return str(exports_dir / filename)

    def _export_to_csv(self, results: List[IntelligenceResult], investigation: Dict) -> str:
        """Export results to CSV format"""
        import csv
        
        filename = f"investigation_{investigation['strategy'].target.primary_identifier.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        exports_dir = Path("data/exports")
        exports_dir.mkdir(exist_ok=True)
        
        with open(exports_dir / filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Data Type', 'Value', 'Confidence', 'Relevance Score', 
                'Source Method', 'Source URL', 'Timestamp', 
                'Geographic Location', 'Validation Status'
            ])
            
            # Write results
            for result in results:
                writer.writerow([
                    result.data_type,
                    result.value,
                    result.confidence,
                    result.relevance_score,
                    result.source_method,
                    result.source_url,
                    result.timestamp.isoformat() if result.timestamp else '',
                    result.geographic_location or '',
                    result.validation_status
                ])
        
        return str(exports_dir / filename)

    def _export_to_html(self, results: List[IntelligenceResult], investigation: Dict) -> str:
        """Export results to HTML report format"""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT Investigation Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
        .summary { background: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .result { border: 1px solid #bdc3c7; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .high-confidence { border-left: 5px solid #27ae60; }
        .medium-confidence { border-left: 5px solid #f39c12; }
        .low-confidence { border-left: 5px solid #e74c3c; }
        .meta { color: #7f8c8d; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Advanced OSINT Investigation Report</h1>
        <p>Target: {target}</p>
        <p>Generated: {timestamp}</p>
    </div>
    
    <div class="summary">
        <h2>Investigation Summary</h2>
        <p><strong>Total Results:</strong> {total_results}</p>
        <p><strong>Investigation Duration:</strong> {duration}</p>
        <p><strong>High Confidence Results:</strong> {high_confidence_count}</p>
        <p><strong>Data Sources Used:</strong> {sources_used}</p>
    </div>
    
    <div class="results">
        <h2>Intelligence Results</h2>
        {results_html}
    </div>
</body>
</html>
        """
        
        # Generate results HTML
        results_html = ""
        high_confidence_count = 0
        sources_used = set()
        
        for result in results:
            if result.confidence >= 0.8:
                confidence_class = "high-confidence"
                high_confidence_count += 1
            elif result.confidence >= 0.5:
                confidence_class = "medium-confidence"
            else:
                confidence_class = "low-confidence"
            
            sources_used.add(result.source_method)
            
            results_html += f"""
            <div class="result {confidence_class}">
                <h3>{result.data_type.replace('_', ' ').title()}</h3>
                <p><strong>Value:</strong> {result.value}</p>
                <p><strong>Confidence:</strong> {result.confidence:.2f} | <strong>Relevance:</strong> {result.relevance_score:.2f}</p>
                <div class="meta">
                    <p><strong>Source:</strong> {result.source_method} | <strong>URL:</strong> <a href="{result.source_url}" target="_blank">View Source</a></p>
                    <p><strong>Location:</strong> {result.geographic_location or 'Unknown'} | <strong>Status:</strong> {result.validation_status}</p>
                </div>
            </div>
            """
        
        # Calculate duration
        start_time = investigation['start_time']
        end_time = investigation.get('end_time', datetime.now())
        duration = str(end_time - start_time).split('.')[0]  # Remove microseconds
        
        # Fill template
        html_content = html_template.format(
            target=investigation['strategy'].target.primary_identifier,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            total_results=len(results),
            duration=duration,
            high_confidence_count=high_confidence_count,
            sources_used=', '.join(sources_used),
            results_html=results_html
        )
        
        filename = f"investigation_report_{investigation['strategy'].target.primary_identifier.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        exports_dir = Path("data/exports")
        exports_dir.mkdir(exist_ok=True)
        
        with open(exports_dir / filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(exports_dir / filename)

    def cleanup_old_investigations(self, days: int = 7) -> int:
        """Clean up investigations older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        
        investigations_to_remove = []
        for inv_id, investigation in self.active_investigations.items():
            if investigation['start_time'] < cutoff_date:
                investigations_to_remove.append(inv_id)
        
        for inv_id in investigations_to_remove:
            del self.active_investigations[inv_id]
            cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} old investigations")
        return cleaned_count

# Example usage and testing
async def test_discovery_engine():
    """Test the discovery engine with sample targets"""
    engine = AdvancedDiscoveryEngine()
    
    # Test targets
    test_targets = [
        "hotels in Riyadh",
        "unemployed developers in Saudi Arabia", 
        "conference organizers in Gulf region",
        "delivery drivers in Dubai"
    ]
    
    sample_questionnaire = {
        'context': 'lead_generation',
        'data_priorities': ['contact_info', 'business_info'],
        'urgency': 'standard',
        'search_depth': 'standard',
        'risk_tolerance': 'medium'
    }
    
    for target in test_targets:
        print(f"\n=== Testing: {target} ===")
        
        # Analyze and create strategy
        strategy = await engine.analyze_target_and_strategize(target, sample_questionnaire)
        
        print(f"Target Type: {strategy.target.target_type.value}")
        print(f"Geographic Focus: {strategy.target.geographic_focus}")
        print(f"Collection Methods: {strategy.collection_methods}")
        print(f"Keywords: {strategy.search_keywords[:5]}...")
        print(f"Expected Results: {strategy.expected_result_types}")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_discovery_engine())