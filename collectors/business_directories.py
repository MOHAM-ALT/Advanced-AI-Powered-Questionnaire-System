#!/usr/bin/env python3
"""
Business Directories Intelligence Collector
File Location: collectors/business_directories.py
Advanced Business Directory Data Collection with AI Analysis
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
from utils.patterns import SearchPatterns
from utils.validation import ValidationRules

logger = logging.getLogger(__name__)

@dataclass
class BusinessListing:
    """Business directory listing data structure"""
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
    """Advanced business directory intelligence collector"""
    
    CONFIDENCE_WEIGHTS = {
        'completeness': 0.6,
        'consistency': 0.4
    }
    
    def __init__(self):
        self.validation = ValidationRules()
        self.patterns = SearchPatterns()
        self.rate_limiter = RateLimiter()
        self.proxy_manager = ProxyManager()
        
        # Business directory sources
        self.directories = {
            'google_business': {
                'name': 'Google My Business',
                'base_url': 'https://www.google.com/maps',
                'search_pattern': '/search/{query}',
                'weight': 0.9
            },
            'yelp': {
                'name': 'Yelp Business Directory',
                'base_url': 'https://www.yelp.com',
                'search_pattern': '/search?find_desc={query}&find_loc={location}',
                'weight': 0.8
            },
            'yellowpages': {
                'name': 'Yellow Pages',
                'base_url': 'https://www.yellowpages.com',
                'search_pattern': '/search?search_terms={query}&geo_location_terms={location}',
                'weight': 0.7
            },
            'foursquare': {
                'name': 'Foursquare Places',
                'base_url': 'https://foursquare.com',
                'search_pattern': '/explore?mode=url&near={location}&q={query}',
                'weight': 0.6
            }
        }
        
        # Business categories mapping
        self.business_categories = {
            'hospitality': ['hotel', 'restaurant', 'cafe', 'resort', 'inn', 'motel'],
            'technology': ['software', 'tech', 'IT', 'digital', 'computer', 'programming'],
            'healthcare': ['medical', 'health', 'clinic', 'hospital', 'dental', 'pharmacy'],
            'retail': ['store', 'shop', 'market', 'boutique', 'outlet', 'mall'],
            'automotive': ['car', 'auto', 'vehicle', 'garage', 'repair', 'dealership'],
            'finance': ['bank', 'financial', 'insurance', 'investment', 'accounting'],
            'education': ['school', 'university', 'training', 'education', 'learning'],
            'real_estate': ['real estate', 'property', 'housing', 'apartment', 'rental'],
            'professional_services': ['consulting', 'legal', 'marketing', 'advertising'],
            'beauty': ['salon', 'spa', 'beauty', 'cosmetic', 'barber', 'nail']
        }
    
    async def comprehensive_directory_search(self, target: str, params: Dict) -> List[BusinessListing]:
        """
        Comprehensive business directory search across multiple sources
        """
        logger.info(f"Starting comprehensive business directory search for: {target}")
        
        all_listings = []
        location = params.get('geographic_focus', '')
        search_depth = params.get('search_depth', 'standard')
        
        # Determine which directories to search based on depth
        directories_to_search = self._select_directories(search_depth)
        
        # Parallel search across selected directories
        search_tasks = []
        for directory_id in directories_to_search:
            task = self._search_directory(directory_id, target, location, params)
            search_tasks.append(task)
        
        # Execute searches with rate limiting
        try:
            results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_listings.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Directory search error: {result}")
        
        except Exception as e:
            logger.error(f"Error in parallel directory search: {e}")
        
        # Process and deduplicate results
        processed_listings = self._process_listings(all_listings)
        
        # Sort by confidence and relevance
        ranked_listings = self._rank_listings_by_relevance(processed_listings, target, params)
        
        logger.info(f"Directory search completed: {len(ranked_listings)} unique listings found")
        return ranked_listings
    
    def _select_directories(self, search_depth: str) -> List[str]:
        """Select directories based on search depth"""
        if search_depth == 'quick':
            return ['google_business']
        elif search_depth == 'standard':
            return ['google_business', 'yelp']
        else:  # comprehensive
            return list(self.directories.keys())
    
    async def _search_directory(self, directory_id: str, target: str, location: str, params: Dict) -> List[BusinessListing]:
        """Search specific business directory"""
        directory_info = self.directories.get(directory_id)
        if not directory_info:
            return []
        
        logger.info(f"Searching {directory_info['name']} for: {target}")
        
        try:
            await self.rate_limiter.wait_if_needed(directory_id)
            
            # Generate search queries
            search_queries = self._generate_search_queries(target, location)
            
            listings = []
            for query in search_queries[:3]:  # Limit queries per directory
                query_results = await self._perform_directory_search(directory_id, query, location)
                listings.extend(query_results)
                
                # Break if we have enough results
                if len(listings) >= 20:
                    break
            
            # Enhance listings with directory-specific data
            enhanced_listings = self._enhance_directory_listings(listings, directory_id, directory_info)
            
            return enhanced_listings
            
        except Exception as e:
            logger.error(f"Error searching {directory_info['name']}: {e}")
            return []
    
    def _generate_search_queries(self, target: str, location: str) -> List[str]:
        """Generate optimized search queries for directories"""
        queries = []
        
        # Base query
        queries.append(target)
        
        # Query with location
        if location:
            queries.append(f"{target} {location}")
            queries.append(f"{target} in {location}")
        
        # Category-specific queries
        detected_category = self._detect_business_category(target)
        if detected_category:
            category_terms = self.business_categories[detected_category]
            for term in category_terms[:2]:  # Use top 2 related terms
                if term.lower() not in target.lower():
                    queries.append(f"{term} {location}" if location else term)
        
        # Enhanced queries
        if 'hotel' in target.lower() or 'accommodation' in target.lower():
            queries.extend([f"hotels {location}", f"accommodation {location}"])
        elif 'restaurant' in target.lower() or 'dining' in target.lower():
            queries.extend([f"restaurants {location}", f"dining {location}"])
        elif 'tech' in target.lower() or 'software' in target.lower():
            queries.extend([f"technology companies {location}", f"software companies {location}"])
        
        return queries
    
    def _detect_business_category(self, target: str) -> Optional[str]:
        """Detect business category from target"""
        target_lower = target.lower()
        
        for category, keywords in self.business_categories.items():
            if any(keyword in target_lower for keyword in keywords):
                return category
        
        return None
    
    async def _perform_directory_search(self, directory_id: str, query: str, location: str) -> List[BusinessListing]:
        """Perform actual search on specific directory"""
        # This is a simulation of directory search
        # In real implementation, this would make actual HTTP requests
        
        if directory_id == 'google_business':
            return await self._simulate_google_business_search(query, location)
        elif directory_id == 'yelp':
            return await self._simulate_yelp_search(query, location)
        elif directory_id == 'yellowpages':
            return await self._simulate_yellowpages_search(query, location)
        elif directory_id == 'foursquare':
            return await self._simulate_foursquare_search(query, location)
        
        return []
    
    async def _simulate_google_business_search(self, query: str, location: str) -> List[BusinessListing]:
        """Simulate Google My Business search results"""
        listings = []
        
        # Generate realistic business listings
        for i in range(random.randint(5, 12)):
            listing = BusinessListing(
                name=f"{query.title()} Business {i+1}",
                address=f"{random.randint(100, 9999)} Business Street, {location}",
                phone=f"+966{random.randint(500000000, 599999999)}",
                website=f"https://{query.replace(' ', '').lower()}{i+1}.com",
                category=self._detect_business_category(query) or 'general_business',
                rating=round(random.uniform(3.5, 5.0), 1),
                reviews_count=random.randint(10, 500),
                description=f"Professional {query} services in {location}. Established business with excellent customer service.",
                source_directory='google_business',
                listing_url=f"https://maps.google.com/place/business{i+1}",
                confidence_score=random.uniform(0.8, 0.95),
                metadata={
                    'search_query': query,
                    'location': location,
                    'business_hours': '9 AM - 6 PM',
                    'verified': random.choice([True, False]),
                    'popular_times': ['12 PM', '1 PM', '6 PM']
                }
            )
            listings.append(listing)
        
        return listings
    
    async def _simulate_yelp_search(self, query: str, location: str) -> List[BusinessListing]:
        """Simulate Yelp search results"""
        listings = []
        
        for i in range(random.randint(3, 8)):
            listing = BusinessListing(
                name=f"{query} Yelp {i+1}",
                address=f"{random.randint(100, 9999)} Yelp Avenue, {location}",
                phone=f"+966{random.randint(500000000, 599999999)}" if random.choice([True, False]) else None,
                website=f"https://business{i+1}.com" if random.choice([True, False]) else None,
                category=self._detect_business_category(query) or 'general_business',
                rating=round(random.uniform(3.0, 5.0), 1),
                reviews_count=random.randint(5, 200),
                description=f"Highly rated {query} in {location}. Great customer reviews and service quality.",
                source_directory='yelp',
                listing_url=f"https://yelp.com/biz/business{i+1}",
                confidence_score=random.uniform(0.6, 0.9),
                metadata={
                    'search_query': query,
                    'location': location,
                    'price_range': random.choice(['$', '$$', '$$$', '$$$$']),
                    'delivery_available': random.choice([True, False]),
                    'top_reviews': ['Great service', 'Excellent quality', 'Highly recommended']
                }
            )
            listings.append(listing)
        
        return listings
    
    async def _simulate_yellowpages_search(self, query: str, location: str) -> List[BusinessListing]:
        """Simulate Yellow Pages search results"""
        listings = []
        
        for i in range(random.randint(2, 6)):
            listing = BusinessListing(
                name=f"{query} YP {i+1}",
                address=f"{random.randint(100, 9999)} Yellow Street, {location}",
                phone=f"+966{random.randint(500000000, 599999999)}",
                website=None,  # Yellow Pages often has phone but no website
                category=self._detect_business_category(query) or 'general_business',
                rating=None,  # Yellow Pages doesn't always have ratings
                reviews_count=None,
                description=f"Established {query} business in {location}. Contact for professional services.",
                source_directory='yellowpages',
                listing_url=f"https://yellowpages.com/business{i+1}",
                confidence_score=random.uniform(0.5, 0.8),
                metadata={
                    'search_query': query,
                    'location': location,
                    'years_in_business': random.randint(1, 25),
                    'business_type': 'local_business'
                }
            )
            listings.append(listing)
        
        return listings
    
    async def _simulate_foursquare_search(self, query: str, location: str) -> List[BusinessListing]:
        """Simulate Foursquare search results"""
        listings = []
        
        for i in range(random.randint(2, 5)):
            listing = BusinessListing(
                name=f"{query} 4SQ {i+1}",
                address=f"{random.randint(100, 9999)} Square Plaza, {location}",
                phone=f"+966{random.randint(500000000, 599999999)}" if random.choice([True, False]) else None,
                website=f"https://square{i+1}.com" if random.choice([True, False]) else None,
                category=self._detect_business_category(query) or 'general_business',
                rating=round(random.uniform(3.2, 4.8), 1),
                reviews_count=random.randint(8, 150),
                description=f"Popular {query} destination in {location}. Great atmosphere and service.",
                source_directory='foursquare',
                listing_url=f"https://foursquare.com/v/business{i+1}",
                confidence_score=random.uniform(0.6, 0.85),
                metadata={
                    'search_query': query,
                    'location': location,
                    'check_ins': random.randint(50, 2000),
                    'tips_count': random.randint(5, 50),
                    'categories': [self._detect_business_category(query) or 'general']
                }
            )
            listings.append(listing)
        
        return listings
    
    def _enhance_directory_listings(self, listings: List[BusinessListing], directory_id: str, directory_info: Dict) -> List[BusinessListing]:
        """Enhance listings with directory-specific data"""
        enhanced_listings = []
        
        for listing in listings:
            # Apply directory weight to confidence score
            listing.confidence_score *= directory_info['weight']
            
            # Add directory-specific metadata
            listing.metadata['directory_weight'] = directory_info['weight']
            listing.metadata['directory_name'] = directory_info['name']
            listing.metadata['search_timestamp'] = datetime.now().isoformat()
            
            # Validate and clean data
            if self._validate_listing(listing):
                enhanced_listings.append(listing)
        
        return enhanced_listings
    
    def _validate_listing(self, listing: BusinessListing) -> bool:
        """Validate business listing data quality"""
        # Basic validation checks
        if not listing.name or len(listing.name) < 2:
            return False
        
        if not listing.address or len(listing.address) < 10:
            return False
        
        # Validate phone if present
        if listing.phone:
            if not self._validate_phone_number(listing.phone):
                listing.phone = None  # Remove invalid phone
        
        # Validate website if present
        if listing.website:
            if not self._validate_website_url(listing.website):
                listing.website = None  # Remove invalid website
        
        # Check for suspicious patterns
        suspicious_patterns = ['test', 'example', 'sample', 'dummy']
        if any(pattern in listing.name.lower() for pattern in suspicious_patterns):
            return False
        
        return True
    
    def _validate_phone_number(self, phone: str) -> bool:
        """Validate phone number format"""
        # Clean phone number
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Check various phone patterns
        patterns = [
            r'^\+966[5][0-9]{8}$',  # Saudi mobile
            r'^\+966[1-4][0-9]{7}$',  # Saudi landline
            r'^\+971[5][0-9]{8}$',  # UAE mobile
            r'^\+[1-9][0-9]{8,14}$'  # International
        ]
        
        return any(re.match(pattern, cleaned) for pattern in patterns)
    
    def _validate_website_url(self, website: str) -> bool:
        """Validate website URL"""
        # Basic URL validation
        url_pattern = r'^https?://(?:[\w-]+\.)+[\w-]+(?:/[\w-./?%&=]*)?$'
        return bool(re.match(url_pattern, website))
    
    def _process_listings(self, listings: List[BusinessListing]) -> List[BusinessListing]:
        """Process and deduplicate business listings"""
        if not listings:
            return []
        
        # Remove exact duplicates
        unique_listings = self._remove_exact_duplicates(listings)
        
        # Remove similar duplicates (same name, similar address)
        deduplicated_listings = self._remove_similar_duplicates(unique_listings)
        
        # Enhance with additional data
        enhanced_listings = self._enhance_listings_data(deduplicated_listings)
        
        return enhanced_listings
    
    def _remove_exact_duplicates(self, listings: List[BusinessListing]) -> List[BusinessListing]:
        """Remove exact duplicate listings"""
        seen_combinations = set()
        unique_listings = []
        
        for listing in listings:
            # Create unique identifier
            identifier = f"{listing.name.lower().strip()}:{listing.address.lower().strip()}"
            
            if identifier not in seen_combinations:
                seen_combinations.add(identifier)
                unique_listings.append(listing)
        
        logger.info(f"Removed {len(listings) - len(unique_listings)} exact duplicates")
        return unique_listings
    
    def _remove_similar_duplicates(self, listings: List[BusinessListing]) -> List[BusinessListing]:
        """Remove similar duplicate listings using fuzzy matching"""
        if len(listings) <= 1:
            return listings
        
        # Group similar listings
        groups = []
        for listing in listings:
            placed = False
            
            for group in groups:
                # Check similarity with first item in group
                if self._are_listings_similar(listing, group[0]):
                    group.append(listing)
                    placed = True
                    break
            
            if not placed:
                groups.append([listing])
        
        # Select best listing from each group
        deduplicated = []
        for group in groups:
            if len(group) == 1:
                deduplicated.append(group[0])
            else:
                # Select listing with highest confidence
                best_listing = max(group, key=lambda x: x.confidence_score)
                deduplicated.append(best_listing)
        
        logger.info(f"Removed {len(listings) - len(deduplicated)} similar duplicates")
        return deduplicated
    
    def _are_listings_similar(self, listing1: BusinessListing, listing2: BusinessListing) -> bool:
        """Check if two listings are similar"""
        # Name similarity (simple approach)
        name1_words = set(listing1.name.lower().split())
        name2_words = set(listing2.name.lower().split())
        name_overlap = len(name1_words.intersection(name2_words)) / max(len(name1_words), len(name2_words))
        
        # Address similarity
        addr1_words = set(listing1.address.lower().split())
        addr2_words = set(listing2.address.lower().split())
        addr_overlap = len(addr1_words.intersection(addr2_words)) / max(len(addr1_words), len(addr2_words))
        
        # Phone similarity
        phone_match = False
        if listing1.phone and listing2.phone:
            phone_match = listing1.phone == listing2.phone
        
        # Consider similar if high name overlap or same phone
        return name_overlap > 0.7 or phone_match or (name_overlap > 0.5 and addr_overlap > 0.5)
    
    def _enhance_listings_data(self, listings: List[BusinessListing]) -> List[BusinessListing]:
        """Enhance listings with additional computed data"""
        for listing in listings:
            # Calculate completeness score
            listing.metadata['completeness_score'] = self._calculate_completeness_score(listing)
            
            # Add business insights
            listing.metadata['business_insights'] = self._generate_business_insights(listing)
            
            # Normalize rating if present
            if listing.rating:
                listing.metadata['rating_normalized'] = min(listing.rating / 5.0, 1.0)
            
            # Categorize by business size (based on reviews)
            if listing.reviews_count:
                if listing.reviews_count > 200:
                    listing.metadata['business_size'] = 'large'
                elif listing.reviews_count > 50:
                    listing.metadata['business_size'] = 'medium'
                else:
                    listing.metadata['business_size'] = 'small'
        
        return listings
    
    def _calculate_completeness_score(self, listing: BusinessListing) -> float:
        """Calculate data completeness score"""
        total_fields = 8
        filled_fields = 0
        
        if listing.name: filled_fields += 1
        if listing.address: filled_fields += 1
        if listing.phone: filled_fields += 1
        if listing.website: filled_fields += 1
        if listing.category: filled_fields += 1
        if listing.rating: filled_fields += 1
        if listing.reviews_count: filled_fields += 1
        if listing.description: filled_fields += 1
        
        return filled_fields / total_fields
    
    def _generate_business_insights(self, listing: BusinessListing) -> Dict[str, Any]:
        """Generate business insights from listing data"""
        insights = {}
        
        # Contact availability
        contact_methods = []
        if listing.phone: contact_methods.append('phone')
        if listing.website: contact_methods.append('website')
        insights['contact_methods'] = contact_methods
        insights['contact_score'] = len(contact_methods) / 2.0
        
        # Reputation indicators
        if listing.rating and listing.reviews_count:
            if listing.rating >= 4.0 and listing.reviews_count >= 50:
                insights['reputation'] = 'excellent'
            elif listing.rating >= 3.5:
                insights['reputation'] = 'good'
            else:
                insights['reputation'] = 'average'
        
        # Business maturity (based on reviews count)
        if listing.reviews_count:
            if listing.reviews_count > 100:
                insights['maturity'] = 'established'
            elif listing.reviews_count > 20:
                insights['maturity'] = 'developing'
            else:
                insights['maturity'] = 'new'
        
        # Directory presence
        insights['directory_presence'] = listing.source_directory
        insights['source_reliability'] = self.directories[listing.source_directory]['weight']
        
        return insights
    
    def _rank_listings_by_relevance(self, listings: List[BusinessListing], target: str, params: Dict) -> List[BusinessListing]:
        """Rank listings by relevance to search target"""
        if not listings:
            return []
        
        target_words = set(target.lower().split())
        priority_data = params.get('priority_data', [])
        geographic_focus = params.get('geographic_focus', '').lower()
        
        for listing in listings:
            relevance_score = listing.confidence_score
            
            # Name relevance (40% weight)
            name_words = set(listing.name.lower().split())
            name_overlap = len(target_words.intersection(name_words)) / max(len(target_words), 1)
            relevance_score += name_overlap * 0.4
            
            # Geographic relevance (20% weight)
            if geographic_focus and geographic_focus in listing.address.lower():
                relevance_score += 0.2
            
            # Category relevance (15% weight)
            if listing.category:
                category_lower = listing.category.lower()
                if any(word in category_lower for word in target_words):
                    relevance_score += 0.15
            
            # Contact information bonus (10% weight)
            if 'contact_info' in priority_data:
                contact_bonus = 0
                if listing.phone: contact_bonus += 0.05
                if listing.website: contact_bonus += 0.05
                relevance_score += contact_bonus
            
            # Rating and reviews bonus (10% weight)
            if listing.rating and listing.reviews_count:
                rating_score = (listing.rating / 5.0) * (min(listing.reviews_count / 100, 1.0))
                relevance_score += rating_score * 0.1
            
            # Source reliability (5% weight)
            source_weight = self.directories[listing.source_directory]['weight']
            relevance_score += source_weight * 0.05
            
            listing.confidence_score = min(relevance_score, 1.0)
        
        # Sort by relevance score
        return sorted(listings, key=lambda x: x.confidence_score, reverse=True)
    
    async def extract_contact_information(self, listings: List[BusinessListing]) -> List[Dict[str, Any]]:
        """Extract and validate contact information from listings"""
        contacts = []
        
        for listing in listings:
            # Extract email from website if available
            if listing.website:
                emails = await self._extract_emails_from_website(listing.website)
                for email in emails:
                    contacts.append({
                        'type': 'email',
                        'value': email,
                        'source_listing': listing.name,
                        'source_url': listing.listing_url,
                        'confidence': 0.8,
                        'validation_status': 'pending'
                    })
            
            # Add phone contact
            if listing.phone:
                contacts.append({
                    'type': 'phone',
                    'value': listing.phone,
                    'source_listing': listing.name,
                    'source_url': listing.listing_url,
                    'confidence': 0.9,
                    'validation_status': 'valid' if self._validate_phone_number(listing.phone) else 'invalid'
                })
            
            # Add website contact
            if listing.website:
                contacts.append({
                    'type': 'website',
                    'value': listing.website,
                    'source_listing': listing.name,
                    'source_url': listing.listing_url,
                    'confidence': 0.7,
                    'validation_status': 'valid' if self._validate_website_url(listing.website) else 'invalid'
                })
        
        return contacts
    
    async def _extract_emails_from_website(self, website_url: str) -> List[str]:
        """Extract email addresses from website (simulation)"""
        # This would normally scrape the website for email addresses
        # For now, we'll simulate email extraction
        
        emails = []
        domain = urlparse(website_url).netloc
        
        # Common email patterns for businesses
        common_prefixes = ['info', 'contact', 'sales', 'support', 'hello']
        
        for prefix in common_prefixes[:2]:  # Limit to avoid spam
            if random.choice([True, False]):  # Simulate finding email
                emails.append(f"{prefix}@{domain}")
        
        return emails
    
    def get_directory_statistics(self) -> Dict[str, Any]:
        """Get statistics about directory searches"""
        return {
            'supported_directories': list(self.directories.keys()),
            'directory_weights': {k: v['weight'] for k, v in self.directories.items()},
            'supported_categories': list(self.business_categories.keys()),
            'validation_rules': {
                'phone_patterns': ['Saudi', 'UAE', 'International'],
                'required_fields': ['name', 'address'],
                'optional_fields': ['phone', 'website', 'rating']
            }
        }

# Example usage and testing
async def test_business_directory_collector():
    """Test the business directory collector"""
    collector = BusinessDirectoryCollector()
    
    test_queries = [
        "hotels in Riyadh",
        "restaurants in Dubai", 
        "technology companies in Saudi Arabia",
        "medical clinics in Jeddah"
    ]
    
    for query in test_queries:
        print(f"\n=== Testing business directory search for: {query} ===")
        
        params = {
            'geographic_focus': 'Saudi Arabia',
            'search_depth': 'standard',
            'priority_data': ['contact_info', 'business_info'],
            'time_limit': 5
        }
        
        try:
            results = await collector.comprehensive_directory_search(query, params)
            print(f"Found {len(results)} business listings")
            
            # Show top 3 results
            for i, listing in enumerate(results[:3], 1):
                print(f"{i}. {listing.name}")
                print(f"   Address: {listing.address}")
                print(f"   Phone: {listing.phone or 'N/A'}")
                print(f"   Rating: {listing.rating or 'N/A'}")
                print(f"   Source: {listing.source_directory}")
                print(f"   Confidence: {listing.confidence_score:.2f}")
                print(f"   URL: {listing.listing_url}")
                print()
                
            # Extract contact information
            contacts = await collector.extract_contact_information(results)
            print(f"Extracted {len(contacts)} contact information items")
            
            # Show statistics
            stats = collector.get_directory_statistics()
            print(f"Supported directories: {', '.join(stats['supported_directories'])}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_business_directory_collector())