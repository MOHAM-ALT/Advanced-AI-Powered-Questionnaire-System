#!/usr/bin/env python3
"""
Intelligent Search Engines Collector
File Location: collectors/search_engines.py
Advanced Google Dorking, Bing Intelligence, and Multi-Engine Search
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
class SearchResult:
    """Standardized search result"""
    title: str
    url: str
    snippet: str
    domain: str
    search_engine: str
    keywords_used: List[str]
    confidence_score: float
    timestamp: datetime
    metadata: Dict[str, Any]

class GoogleDorkingEngine:
    """Advanced Google Dorking with 2025 techniques"""
    
    def __init__(self):
        self.dork_patterns = self._initialize_dork_patterns()
        self.user_agents = self._get_user_agents()
        
    def _initialize_dork_patterns(self) -> Dict[str, List[str]]:
        """Initialize comprehensive Google Dorking patterns"""
        return {
            'contact_discovery': [
                'site:{domain} "contact" OR "email" OR "phone" OR "call us"',
                'site:{domain} "@{domain}" -www',
                'site:{domain} filetype:pdf "contact" OR "directory"',
                '"{company}" "email" OR "contact" -site:{domain}',
                '"{company}" "@" site:linkedin.com',
                'site:{domain} "staff" OR "team" OR "employees"',
                'site:{domain} "about us" OR "meet the team"',
                'site:{domain} intitle:"contact" OR intitle:"directory"'
            ],
            
            'employee_discovery': [
                '"{company}" site:linkedin.com/in/',
                '"{company}" "manager" OR "director" OR "CEO" OR "CTO"',
                '"{company}" "@{domain}" site:linkedin.com',
                '"{company}" "works at" OR "employee" site:facebook.com',
                '"{company}" "team member" OR "staff"',
                'site:{domain} "bio" OR "biography" OR "profile"',
                '"{company}" site:twitter.com "CEO" OR "founder"'
            ],
            
            'business_intelligence': [
                '"{company}" "revenue" OR "employees" OR "funding" OR "valuation"',
                '"{company}" "CEO" OR "founder" OR "president" OR "owner"',
                '"{company}" "office" OR "headquarters" OR "location"',
                '"{company}" "news" OR "press release" OR "announcement"',
                '"{company}" "partnership" OR "acquisition" OR "merger"',
                'site:{domain} "investor" OR "funding" OR "capital"',
                '"{company}" "annual report" filetype:pdf'
            ],
            
            'service_discovery': [
                '"{service_type}" "{location}" "contact" OR "phone"',
                '"{service_type}" "{location}" "directory" OR "list"',
                'site:yellowpages.com "{service_type}" "{location}"',
                'site:yelp.com "{service_type}" "{location}"',
                '"{service_type}" "{location}" "company" OR "business"',
                'intitle:"{service_type}" "{location}" contact'
            ],
            
            'job_related': [
                '"{job_title}" "{location}" "resume" OR "CV"',
                'site:linkedin.com "{job_title}" "{location}" "seeking"',
                'site:indeed.com "{job_title}" "{location}"',
                '"{job_title}" "{location}" "available" OR "looking for"',
                'site:bayt.com "{job_title}" "{location}"',
                '"looking for work" "{job_title}" "{location}"'
            ],
            
            'social_media_discovery': [
                '"{company}" site:facebook.com',
                '"{company}" site:twitter.com',
                '"{company}" site:instagram.com',
                '"{company}" site:youtube.com',
                '"{company}" site:tiktok.com',
                'site:linkedin.com/company/{company}'
            ],
            
            'document_discovery': [
                'site:{domain} filetype:pdf "directory" OR "staff"',
                'site:{domain} filetype:doc OR filetype:docx "contact"',
                'site:{domain} filetype:xls OR filetype:xlsx "employees"',
                '"{company}" filetype:pdf "organization chart"',
                'site:{domain} filetype:ppt OR filetype:pptx "team"'
            ],
            
            'vulnerability_discovery': [
                'site:{domain} "admin" OR "login" OR "dashboard"',
                'site:{domain} "database" OR "db" OR "sql"',
                'site:{domain} "config" OR "configuration"',
                'site:{domain} "backup" OR "test" OR "dev"',
                'site:{domain} intitle:"index of"'
            ]
        }
    
    def _get_user_agents(self) -> List[str]:
        """Get realistic user agents for 2025"""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
    
    def generate_dorks(self, target: str, target_type: str, context: str) -> List[str]:
        """Generate contextual Google Dorks"""
        dorks = []
        
        # Parse target for domain extraction
        domain = self._extract_domain(target)
        company = self._extract_company_name(target)
        
        # Select appropriate dork categories
        if target_type == 'people_group':
            categories = ['employee_discovery', 'job_related', 'social_media_discovery']
        elif target_type == 'business_category':
            categories = ['business_intelligence', 'service_discovery', 'contact_discovery']
        elif target_type == 'domain_entity':
            categories = ['contact_discovery', 'employee_discovery', 'document_discovery', 'vulnerability_discovery']
        else:
            categories = ['contact_discovery', 'business_intelligence', 'service_discovery']
        
        # Generate dorks for each category
        for category in categories:
            if category in self.dork_patterns:
                for pattern in self.dork_patterns[category]:
                    # Replace placeholders
                    dork = pattern.format(
                        domain=domain,
                        company=company,
                        service_type=self._extract_service_type(target),
                        location=self._extract_location(target),
                        job_title=self._extract_job_title(target)
                    )
                    dorks.append(dork)
        
        return dorks[:20]  # Limit to top 20 dorks
    
    def _extract_domain(self, target: str) -> str:
        """Extract domain from target"""
        # Look for domain pattern
        domain_match = re.search(r'\b([a-zA-Z0-9-]+\.[a-zA-Z]{2,})\b', target)
        if domain_match:
            return domain_match.group(1)
        return "example.com"  # Default placeholder
    
    def _extract_company_name(self, target: str) -> str:
        """Extract company name from target"""
        # Simple extraction - can be enhanced
        words = target.split()
        if len(words) > 0:
            return words[0]
        return "company"
    
    def _extract_service_type(self, target: str) -> str:
        """Extract service type from target"""
        service_keywords = {
            'hotel': 'hotels', 'restaurant': 'restaurants', 'developer': 'developers',
            'delivery': 'delivery', 'conference': 'conference', 'consulting': 'consulting'
        }
        
        target_lower = target.lower()
        for keyword, service in service_keywords.items():
            if keyword in target_lower:
                return service
        
        return "services"
    
    def _extract_location(self, target: str) -> str:
        """Extract location from target"""
        location_patterns = [
            r'\bin\s+([A-Za-z\s]+?)(?:\s|$)',
            r'\bat\s+([A-Za-z\s]+?)(?:\s|$)',
            r'\bfrom\s+([A-Za-z\s]+?)(?:\s|$)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, target, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "location"
    
    def _extract_job_title(self, target: str) -> str:
        """Extract job title from target"""
        job_keywords = ['developer', 'engineer', 'manager', 'director', 'analyst', 'designer']
        
        target_lower = target.lower()
        for keyword in job_keywords:
            if keyword in target_lower:
                return keyword
        
        return "professional"

class IntelligentSearchCollector:
    """Main intelligent search collector"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.proxy_manager = ProxyManager()
        self.google_dorker = GoogleDorkingEngine()
        self.session = None
        self.results_cache = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def intelligent_multi_engine_search(self, target: str, params: Dict) -> List[SearchResult]:
        """
        Intelligent multi-engine search with advanced techniques
        """
        logger.info(f"Starting intelligent search for: {target}")
        
        async with self:
            all_results = []
            
            # Search engines to use
            engines = ['google', 'bing', 'duckduckgo']
            
            # Parallel search across engines
            search_tasks = []
            for engine in engines:
                task = self._search_engine(engine, target, params)
                search_tasks.append(task)
            
            # Execute searches
            engine_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Process results
            for results in engine_results:
                if isinstance(results, list):
                    all_results.extend(results)
                elif isinstance(results, Exception):
                    logger.error(f"Search engine error: {results}")
            
            # Remove duplicates and rank
            unique_results = self._remove_duplicates(all_results)
            ranked_results = self._rank_results(unique_results, target, params)
            
            logger.info(f"Found {len(ranked_results)} unique results")
            return ranked_results

    async def _search_engine(self, engine: str, target: str, params: Dict) -> List[SearchResult]:
        """Search specific engine"""
        try:
            if engine == 'google':
                return await self._google_search(target, params)
            elif engine == 'bing':
                return await self._bing_search(target, params)
            elif engine == 'duckduckgo':
                return await self._duckduckgo_search(target, params)
        except Exception as e:
            logger.error(f"Error in {engine} search: {e}")
            return []

    async def _google_search(self, target: str, params: Dict) -> List[SearchResult]:
        """Advanced Google search with dorking"""
        results = []
        
        # Generate intelligent dorks
        dorks = self.google_dorker.generate_dorks(
            target, 
            params.get('target_type', 'mixed'),
            params.get('context', 'general')
        )
        
        # Basic search first
        basic_queries = [
            target,
            f'"{target}" contact',
            f'"{target}" email phone',
            f'{target} {params.get("geographic_focus", "")}'
        ]
        
        all_queries = basic_queries + dorks[:10]  # Limit dorks to avoid detection
        
        for query in all_queries:
            try:
                await self.rate_limiter.wait_if_needed('google')
                search_results = await self._perform_google_search(query)
                results.extend(search_results)
                
                # Break if we have enough results
                if len(results) >= 100:
                    break
                    
            except Exception as e:
                logger.error(f"Google search error for '{query}': {e}")
                continue
        
        return results

    async def _perform_google_search(self, query: str) -> List[SearchResult]:
        """Perform actual Google search"""
        headers = {
            'User-Agent': random.choice(self.google_dorker.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Use a more realistic search URL
        url = f"https://www.google.com/search?q={quote(query)}&num=20&hl=en"
        
        try:
            proxy = self.proxy_manager.get_proxy()
            async with self.session.get(url, headers=headers, proxy=proxy) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_google_results(html, query)
                else:
                    logger.warning(f"Google returned status {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Google search request failed: {e}")
            return []

    def _parse_google_results(self, html: str, query: str) -> List[SearchResult]:
        """Parse Google search results"""
        results = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for result containers
        result_containers = soup.find_all(['div'], class_=re.compile(r'g|result'))
        
        for container in result_containers:
            try:
                # Extract title
                title_element = container.find(['h3', 'a'])
                if not title_element:
                    continue
                
                title = title_element.get_text(strip=True)
                
                # Extract URL
                link_element = container.find('a', href=True)
                if not link_element:
                    continue
                
                url = link_element['href']
                if url.startswith('/url?q='):
                    url = url.split('/url?q=')[1].split('&')[0]
                
                # Extract snippet
                snippet_element = container.find(['span', 'div'], class_=re.compile(r'st|snippet'))
                snippet = snippet_element.get_text(strip=True) if snippet_element else ""
                
                # Extract domain
                domain = urlparse(url).netloc
                
                # Calculate confidence score
                confidence = self._calculate_search_confidence(title, snippet, query)
                
                if confidence > 0.3:  # Only include relevant results
                    result = SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        domain=domain,
                        search_engine='google',
                        keywords_used=[query],
                        confidence_score=confidence,
                        timestamp=datetime.now(),
                        metadata={'query': query, 'position': len(results) + 1}
                    )
                    results.append(result)
                    
            except Exception as e:
                logger.debug(f"Error parsing Google result: {e}")
                continue
        
        return results

    async def _bing_search(self, target: str, params: Dict) -> List[SearchResult]:
        """Bing search with business intelligence focus"""
        results = []
        
        # Bing-specific queries
        bing_queries = [
            target,
            f'"{target}" business directory',
            f'"{target}" company profile',
            f'"{target}" contact information',
            f'{target} {params.get("geographic_focus", "")} business'
        ]
        
        for query in bing_queries:
            try:
                await self.rate_limiter.wait_if_needed('bing')
                search_results = await self._perform_bing_search(query)
                results.extend(search_results)
                
                if len(results) >= 50:
                    break
                    
            except Exception as e:
                logger.error(f"Bing search error for '{query}': {e}")
                continue
        
        return results

    async def _perform_bing_search(self, query: str) -> List[SearchResult]:
        """Perform actual Bing search"""
        headers = {
            'User-Agent': random.choice(self.google_dorker.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        url = f"https://www.bing.com/search?q={quote(query)}&count=20"
        
        try:
            proxy = self.proxy_manager.get_proxy()
            async with self.session.get(url, headers=headers, proxy=proxy) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_bing_results(html, query)
                else:
                    return []
        except Exception as e:
            logger.error(f"Bing search request failed: {e}")
            return []

    def _parse_bing_results(self, html: str, query: str) -> List[SearchResult]:
        """Parse Bing search results"""
        results = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Bing result containers
        result_containers = soup.find_all('li', class_='b_algo')
        
        for container in result_containers:
            try:
                # Extract title and URL
                title_element = container.find('h2')
                if not title_element:
                    continue
                
                link_element = title_element.find('a', href=True)
                if not link_element:
                    continue
                
                title = link_element.get_text(strip=True)
                url = link_element['href']
                
                # Extract snippet
                snippet_element = container.find('p') or container.find('div', class_='b_caption')
                snippet = snippet_element.get_text(strip=True) if snippet_element else ""
                
                # Extract domain
                domain = urlparse(url).netloc
                
                # Calculate confidence
                confidence = self._calculate_search_confidence(title, snippet, query)
                
                if confidence > 0.3:
                    result = SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        domain=domain,
                        search_engine='bing',
                        keywords_used=[query],
                        confidence_score=confidence,
                        timestamp=datetime.now(),
                        metadata={'query': query, 'position': len(results) + 1}
                    )
                    results.append(result)
                    
            except Exception as e:
                logger.debug(f"Error parsing Bing result: {e}")
                continue
        
        return results

    async def _duckduckgo_search(self, target: str, params: Dict) -> List[SearchResult]:
        """DuckDuckGo search for privacy-focused results"""
        results = []
        
        # DuckDuckGo queries
        ddg_queries = [
            target,
            f'"{target}" privacy',
            f'{target} {params.get("geographic_focus", "")}'
        ]
        
        for query in ddg_queries:
            try:
                await self.rate_limiter.wait_if_needed('duckduckgo')
                search_results = await self._perform_duckduckgo_search(query)
                results.extend(search_results)
                
                if len(results) >= 30:
                    break
                    
            except Exception as e:
                logger.error(f"DuckDuckGo search error for '{query}': {e}")
                continue
        
        return results

    async def _perform_duckduckgo_search(self, query: str) -> List[SearchResult]:
        """Perform actual DuckDuckGo search"""
        headers = {
            'User-Agent': random.choice(self.google_dorker.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        # DuckDuckGo uses a different approach
        url = f"https://duckduckgo.com/html/?q={quote(query)}"
        
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_duckduckgo_results(html, query)
                else:
                    return []
        except Exception as e:
            logger.error(f"DuckDuckGo search request failed: {e}")
            return []

    def _parse_duckduckgo_results(self, html: str, query: str) -> List[SearchResult]:
        """Parse DuckDuckGo search results"""
        results = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # DuckDuckGo result containers
        result_containers = soup.find_all('div', class_='result')
        
        for container in result_containers:
            try:
                # Extract title and URL
                title_element = container.find('a', class_='result__a')
                if not title_element:
                    continue
                
                title = title_element.get_text(strip=True)
                url = title_element['href']
                
                # Extract snippet
                snippet_element = container.find('a', class_='result__snippet')
                snippet = snippet_element.get_text(strip=True) if snippet_element else ""
                
                # Extract domain
                domain = urlparse(url).netloc
                
                # Calculate confidence
                confidence = self._calculate_search_confidence(title, snippet, query)
                
                if confidence > 0.3:
                    result = SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        domain=domain,
                        search_engine='duckduckgo',
                        keywords_used=[query],
                        confidence_score=confidence,
                        timestamp=datetime.now(),
                        metadata={'query': query, 'position': len(results) + 1}
                    )
                    results.append(result)
                    
            except Exception as e:
                logger.debug(f"Error parsing DuckDuckGo result: {e}")
                continue
        
        return results

    def _calculate_search_confidence(self, title: str, snippet: str, query: str) -> float:
        """Calculate confidence score for search result"""
        score = 0.0
        
        # Extract query terms
        query_terms = set(query.lower().replace('"', '').split())
        title_terms = set(title.lower().split())
        snippet_terms = set(snippet.lower().split())
        
        # Title matches (high weight)
        title_matches = len(query_terms.intersection(title_terms))
        score += (title_matches / len(query_terms)) * 0.6
        
        # Snippet matches (medium weight)
        snippet_matches = len(query_terms.intersection(snippet_terms))
        score += (snippet_matches / len(query_terms)) * 0.3
        
        # Exact phrase matches (bonus)
        if query.lower().replace('"', '') in title.lower():
            score += 0.2
        
        if query.lower().replace('"', '') in snippet.lower():
            score += 0.1
        
        # Contact information indicators (bonus for OSINT)
        contact_indicators = ['email', 'phone', 'contact', 'address', 'tel:', 'mailto:', '@']
        for indicator in contact_indicators:
            if indicator in title.lower() or indicator in snippet.lower():
                score += 0.1
                break
        
        return min(score, 1.0)

    def _remove_duplicates(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            # Normalize URL for comparison
            normalized_url = result.url.lower().rstrip('/')
            
            if normalized_url not in seen_urls:
                seen_urls.add(normalized_url)
                unique_results.append(result)
        
        return unique_results

    def _rank_results(self, results: List[SearchResult], target: str, params: Dict) -> List[SearchResult]:
        """Rank results by relevance and confidence"""
        
        # Calculate enhanced relevance scores
        for result in results:
            relevance_score = result.confidence_score
            
            # Boost based on domain authority (simplified)
            if result.domain in ['linkedin.com', 'facebook.com', 'twitter.com', 'instagram.com']:
                relevance_score += 0.2
            
            # Boost business directories
            business_domains = ['yellowpages.com', 'yelp.com', 'google.com/maps', 'foursquare.com']
            if any(domain in result.domain for domain in business_domains):
                relevance_score += 0.15
            
            # Boost recent results (if we can determine age)
            if 'recent' in result.snippet.lower() or 'new' in result.snippet.lower():
                relevance_score += 0.1
            
            # Geographic relevance
            geographic_focus = params.get('geographic_focus', '').lower()
            if geographic_focus and geographic_focus in result.snippet.lower():
                relevance_score += 0.15
            
            result.confidence_score = min(relevance_score, 1.0)
        
        # Sort by confidence score
        return sorted(results, key=lambda x: x.confidence_score, reverse=True)

    async def specialized_google_dorking(self, target: str, dork_category: str) -> List[SearchResult]:
        """Specialized Google Dorking for specific categories"""
        if dork_category not in self.google_dorker.dork_patterns:
            return []
        
        results = []
        dorks = []
        
        # Get dorks for specific category
        for pattern in self.google_dorker.dork_patterns[dork_category]:
            dork = pattern.format(
                domain=self.google_dorker._extract_domain(target),
                company=self.google_dorker._extract_company_name(target),
                service_type=self.google_dorker._extract_service_type(target),
                location=self.google_dorker._extract_location(target),
                job_title=self.google_dorker._extract_job_title(target)
            )
            dorks.append(dork)
        
        # Execute dorks
        for dork in dorks:
            try:
                await self.rate_limiter.wait_if_needed('google_dorking')
                search_results = await self._perform_google_search(dork)
                results.extend(search_results)
                
                # Limit results to avoid overload
                if len(results) >= 50:
                    break
                    
            except Exception as e:
                logger.error(f"Specialized dorking error: {e}")
                continue
        
        return self._remove_duplicates(results)

    async def extract_contact_information(self, results: List[SearchResult]) -> List[Dict[str, Any]]:
        """Extract contact information from search results"""
        contacts = []
        
        # Patterns for different contact types
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        phone_patterns = {
            'saudi': re.compile(r'(?:\+966|966|0)?(?:5[0-9])\d{7}\b'),
            'uae': re.compile(r'(?:\+971|971|0)?(?:5[0-9])\d{7}\b'),
            'international': re.compile(r'\+?[1-9]\d{1,14}\b')
        }
        
        for result in results:
            # Combine title and snippet for analysis
            text = f"{result.title} {result.snippet}".lower()
            
            # Extract emails
            emails = email_pattern.findall(text)
            for email in emails:
                contacts.append({
                    'type': 'email',
                    'value': email,
                    'source_url': result.url,
                    'source_title': result.title,
                    'confidence': 0.9,
                    'context': 'search_result'
                })
            
            # Extract phone numbers
            for region, pattern in phone_patterns.items():
                phones = pattern.findall(text)
                for phone in phones:
                    contacts.append({
                        'type': 'phone',
                        'value': phone,
                        'region': region,
                        'source_url': result.url,
                        'source_title': result.title,
                        'confidence': 0.8,
                        'context': 'search_result'
                    })
        
        return contacts

    async def search_news_and_mentions(self, target: str, days_back: int = 30) -> List[SearchResult]:
        """Search for recent news and mentions"""
        news_queries = [
            f'"{target}" news',
            f'"{target}" announcement',
            f'"{target}" press release',
            f'"{target}" mentioned'
        ]
        
        results = []
        
        for query in news_queries:
            # Add time restriction for recent results
            time_query = f'{query} after:{(datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")}'
            
            try:
                await self.rate_limiter.wait_if_needed('news_search')
                search_results = await self._perform_google_search(time_query)
                results.extend(search_results)
                
            except Exception as e:
                logger.error(f"News search error: {e}")
                continue
        
        # Filter and rank news results
        news_results = []
        news_domains = ['news.', 'cnn.', 'bbc.', 'reuters.', 'bloomberg.', 'techcrunch.']
        
        for result in results:
            if any(domain in result.domain for domain in news_domains):
                news_results.append(result)
        
        return sorted(news_results, key=lambda x: x.timestamp, reverse=True)

    def get_search_statistics(self) -> Dict[str, Any]:
        """Get search statistics and performance metrics"""
        return {
            'total_searches_performed': getattr(self, '_search_count', 0),
            'engines_used': ['google', 'bing', 'duckduckgo'],
            'average_results_per_search': getattr(self, '_avg_results', 0),
            'cache_hit_rate': len(self.results_cache) / max(getattr(self, '_search_count', 1), 1),
            'last_search_time': getattr(self, '_last_search_time', None),
            'rate_limiting_active': True
        }

# Example usage and testing
async def test_search_collector():
    """Test the search collector"""
    collector = IntelligentSearchCollector()
    
    test_targets = [
        "hotels in Riyadh",
        "software developers in Dubai", 
        "amazon.com",
        "conference organizers Saudi Arabia"
    ]
    
    for target in test_targets:
        print(f"\n=== Testing search for: {target} ===")
        
        params = {
            'target_type': 'business_category',
            'geographic_focus': 'Saudi Arabia',
            'context': 'lead_generation',
            'time_limit': 5
        }
        
        try:
            results = await collector.intelligent_multi_engine_search(target, params)
            print(f"Found {len(results)} results")
            
            # Show top 3 results
            for i, result in enumerate(results[:3], 1):
                print(f"{i}. {result.title}")
                print(f"   URL: {result.url}")
                print(f"   Confidence: {result.confidence_score:.2f}")
                print(f"   Engine: {result.search_engine}")
                print()
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_search_collector())