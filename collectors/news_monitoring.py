#!/usr/bin/env python3
"""
Advanced News Monitoring Collector
File Location: collectors/news_monitoring.py
Real-time news and media monitoring for intelligence gathering
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
import feedparser

# Import utilities
from utils.rate_limiter import RateLimiter
from utils.proxy_manager import ProxyManager

logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    """News article data structure"""
    title: str
    url: str
    content: str
    summary: str
    source: str
    author: Optional[str]
    publish_date: datetime
    language: str
    sentiment: str  # positive, negative, neutral
    relevance_score: float
    keywords: List[str]
    entities: List[str]  # People, organizations, locations mentioned
    category: str  # business, technology, politics, etc.
    confidence_score: float
    metadata: Dict[str, Any]

@dataclass
class MediaMention:
    """Media mention data structure"""
    mention_type: str  # article, social_post, press_release, blog
    platform: str
    url: str
    title: str
    content_snippet: str
    mention_context: str
    sentiment: str
    reach_estimate: int
    engagement_metrics: Dict[str, int]
    publish_date: datetime
    confidence_score: float

class NewsMonitoringCollector:
    """Advanced news and media monitoring collector"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.proxy_manager = ProxyManager()
        
        # News sources configuration
        self.news_sources = self._initialize_news_sources()
        
        # Language detection patterns
        self.language_patterns = {
            'arabic': re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+'),
            'english': re.compile(r'[A-Za-z\s]+')
        }
        
        # Sentiment analysis keywords
        self.sentiment_keywords = self._initialize_sentiment_keywords()
        
        # Entity extraction patterns
        self.entity_patterns = self._initialize_entity_patterns()
    
    def _initialize_news_sources(self) -> Dict[str, Dict[str, Any]]:
        """Initialize news sources configuration"""
        return {
            'international': {
                'reuters': {
                    'name': 'Reuters',
                    'base_url': 'https://www.reuters.com',
                    'rss_feeds': [
                        'https://feeds.reuters.com/reuters/businessNews',
                        'https://feeds.reuters.com/reuters/technologyNews',
                        'https://feeds.reuters.com/reuters/worldNews'
                    ],
                    'search_url': 'https://www.reuters.com/search/news?blob={query}',
                    'priority': 10,
                    'language': 'english',
                    'credibility': 9
                },
                'bloomberg': {
                    'name': 'Bloomberg',
                    'base_url': 'https://www.bloomberg.com',
                    'rss_feeds': [
                        'https://feeds.bloomberg.com/markets/news.rss',
                        'https://feeds.bloomberg.com/technology/news.rss'
                    ],
                    'search_url': 'https://www.bloomberg.com/search?query={query}',
                    'priority': 9,
                    'language': 'english',
                    'credibility': 9
                },
                'bbc': {
                    'name': 'BBC News',
                    'base_url': 'https://www.bbc.com',
                    'rss_feeds': [
                        'http://feeds.bbci.co.uk/news/business/rss.xml',
                        'http://feeds.bbci.co.uk/news/technology/rss.xml',
                        'http://feeds.bbci.co.uk/news/world/rss.xml'
                    ],
                    'search_url': 'https://www.bbc.com/search?q={query}',
                    'priority': 8,
                    'language': 'english',
                    'credibility': 8
                }
            },
            'regional': {
                'arab_news': {
                    'name': 'Arab News',
                    'base_url': 'https://www.arabnews.com',
                    'rss_feeds': [
                        'https://www.arabnews.com/taxonomy/term/2/all/feed',
                        'https://www.arabnews.com/taxonomy/term/468/all/feed'
                    ],
                    'search_url': 'https://www.arabnews.com/search/site/{query}',
                    'priority': 9,
                    'language': 'english',
                    'region': 'middle_east',
                    'credibility': 8
                },
                'gulf_news': {
                    'name': 'Gulf News',
                    'base_url': 'https://gulfnews.com',
                    'rss_feeds': [
                        'https://gulfnews.com/business/rss',
                        'https://gulfnews.com/technology/rss'
                    ],
                    'search_url': 'https://gulfnews.com/search?q={query}',
                    'priority': 8,
                    'language': 'english',
                    'region': 'gulf',
                    'credibility': 7
                },
                'al_jazeera': {
                    'name': 'Al Jazeera',
                    'base_url': 'https://www.aljazeera.com',
                    'rss_feeds': [
                        'https://www.aljazeera.com/xml/rss/all.xml',
                        'https://www.aljazeera.com/xml/rss/economy.xml'
                    ],
                    'search_url': 'https://www.aljazeera.com/search/{query}',
                    'priority': 8,
                    'language': 'english',
                    'region': 'middle_east',
                    'credibility': 8
                }
            },
            'tech_focused': {
                'techcrunch': {
                    'name': 'TechCrunch',
                    'base_url': 'https://techcrunch.com',
                    'rss_feeds': [
                        'https://feeds.feedburner.com/TechCrunch/',
                        'https://feeds.feedburner.com/crunchbase-funding'
                    ],
                    'search_url': 'https://search.techcrunch.com/search?query={query}',
                    'priority': 8,
                    'language': 'english',
                    'focus': 'technology',
                    'credibility': 7
                },
                'wired': {
                    'name': 'Wired',
                    'base_url': 'https://www.wired.com',
                    'rss_feeds': [
                        'https://www.wired.com/feed/rss',
                        'https://www.wired.com/feed/category/business/rss'
                    ],
                    'search_url': 'https://www.wired.com/search/?q={query}',
                    'priority': 7,
                    'language': 'english',
                    'focus': 'technology',
                    'credibility': 7
                }
            },
            'business_focused': {
                'financial_times': {
                    'name': 'Financial Times',
                    'base_url': 'https://www.ft.com',
                    'rss_feeds': [
                        'https://www.ft.com/rss/home/us',
                        'https://www.ft.com/rss/companies'
                    ],
                    'search_url': 'https://www.ft.com/search?q={query}',
                    'priority': 9,
                    'language': 'english',
                    'focus': 'business',
                    'credibility': 9
                }
            }
        }
    
    def _initialize_sentiment_keywords(self) -> Dict[str, List[str]]:
        """Initialize sentiment analysis keywords"""
        return {
            'positive': [
                'success', 'growth', 'expansion', 'achievement', 'breakthrough',
                'innovation', 'progress', 'improvement', 'excellent', 'outstanding',
                'profitable', 'revenue', 'gain', 'increase', 'boost', 'upgrade',
                'award', 'recognition', 'partnership', 'acquisition', 'merger'
            ],
            'negative': [
                'failure', 'decline', 'loss', 'crisis', 'problem', 'issue',
                'scandal', 'controversy', 'bankruptcy', 'lawsuit', 'penalty',
                'decrease', 'drop', 'fall', 'recession', 'downturn', 'closure',
                'layoff', 'resignation', 'investigation', 'fraud', 'breach'
            ],
            'neutral': [
                'announcement', 'statement', 'report', 'update', 'information',
                'data', 'analysis', 'study', 'research', 'meeting', 'conference'
            ]
        }
    
    def _initialize_entity_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize entity extraction patterns"""
        return {
            'person': re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'),
            'organization': re.compile(r'\b[A-Z][A-Za-z\s&]+(Inc|Corp|LLC|Ltd|Company|Corporation|Group|Holdings)\b'),
            'location': re.compile(r'\b(Saudi Arabia|UAE|Qatar|Kuwait|Bahrain|Oman|Riyadh|Dubai|Doha|Kuwait City)\b'),
            'money': re.compile(r'\$\d+(?:,\d{3})*(?:\.\d{2})?(?:\s*(?:million|billion|trillion|M|B|T))?'),
            'percentage': re.compile(r'\d+(?:\.\d+)?%')
        }

    async def comprehensive_news_monitoring(self, target: str, params: Dict) -> List[NewsArticle]:
        """
        Comprehensive news monitoring for target entity
        """
        logger.info(f"Starting news monitoring for: {target}")
        
        all_articles = []
        
        # Determine monitoring scope
        monitoring_scope = params.get('monitoring_scope', 'comprehensive')
        time_range = params.get('time_range', 30)  # Days
        languages = params.get('languages', ['english', 'arabic'])
        
        # Generate search keywords
        keywords = self._generate_news_keywords(target, params)
        
        # Select news sources based on scope
        selected_sources = self._select_news_sources(monitoring_scope, params)
        
        # Search across selected sources
        search_tasks = []
        for source_category, sources in selected_sources.items():
            for source_id, source_config in sources.items():
                task = self._search_news_source(source_config, keywords, time_range)
                search_tasks.append(task)
        
        # Execute searches in parallel
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"News search error: {result}")
        
        # Remove duplicates and rank by relevance
        unique_articles = self._remove_duplicate_articles(all_articles)
        ranked_articles = self._rank_articles_by_relevance(unique_articles, target, keywords)
        
        # Filter by time range
        filtered_articles = self._filter_by_time_range(ranked_articles, time_range)
        
        logger.info(f"News monitoring completed: {len(filtered_articles)} articles found")
        return filtered_articles
    
    def _generate_news_keywords(self, target: str, params: Dict) -> List[str]:
        """Generate optimized keywords for news search"""
        keywords = [target]
        
        # Add variations
        if ' ' in target:
            # Try without spaces
            keywords.append(target.replace(' ', ''))
            # Try with quotes for exact match
            keywords.append(f'"{target}"')
        
        # Add context-specific keywords
        context = params.get('context', '')
        if context == 'investment_research':
            keywords.extend(['funding', 'investment', 'IPO', 'acquisition', 'merger'])
        elif context == 'competitor_analysis':
            keywords.extend(['competitor', 'market share', 'competition', 'rival'])
        elif context == 'recruitment':
            keywords.extend(['hiring', 'jobs', 'recruitment', 'employees', 'workforce'])
        elif context == 'lead_generation':
            keywords.extend(['expansion', 'growth', 'new office', 'partnership'])
        
        # Add industry-specific keywords
        industry = params.get('industry', '')
        if industry:
            industry_keywords = {
                'technology': ['tech', 'software', 'AI', 'digital', 'startup'],
                'healthcare': ['medical', 'pharma', 'health', 'biotech'],
                'finance': ['banking', 'fintech', 'financial', 'investment'],
                'energy': ['oil', 'gas', 'renewable', 'energy', 'utilities']
            }
            keywords.extend(industry_keywords.get(industry, []))
        
        return keywords
    
    def _select_news_sources(self, scope: str, params: Dict) -> Dict[str, Dict]:
        """Select appropriate news sources based on scope"""
        if scope == 'quick':
            # Use only high-priority international sources
            return {
                'international': {
                    k: v for k, v in self.news_sources['international'].items() 
                    if v['priority'] >= 9
                }
            }
        elif scope == 'regional':
            # Focus on regional sources
            return {
                'regional': self.news_sources['regional'],
                'international': {
                    k: v for k, v in self.news_sources['international'].items() 
                    if v['priority'] >= 8
                }
            }
        else:  # comprehensive
            return self.news_sources
    
    async def _search_news_source(self, source_config: Dict, keywords: List[str], time_range: int) -> List[NewsArticle]:
        """Search specific news source"""
        articles = []
        
        try:
            await self.rate_limiter.wait_if_needed(f"news_{source_config['name']}")
            
            # Try RSS feeds first (more efficient)
            rss_articles = await self._search_rss_feeds(source_config, keywords, time_range)
            articles.extend(rss_articles)
            
            # If not enough articles from RSS, try web search
            if len(articles) < 5 and 'search_url' in source_config:
                web_articles = await self._search_website(source_config, keywords, time_range)
                articles.extend(web_articles)
            
        except Exception as e:
            logger.error(f"Error searching {source_config['name']}: {e}")
        
        return articles
    
    async def _search_rss_feeds(self, source_config: Dict, keywords: List[str], time_range: int) -> List[NewsArticle]:
        """Search RSS feeds for relevant articles"""
        articles = []
        
        for rss_url in source_config.get('rss_feeds', []):
            try:
                # Parse RSS feed
                feed = feedparser.parse(rss_url)
                
                # Process entries
                for entry in feed.entries[:20]:  # Limit to recent 20 articles
                    article = await self._process_rss_entry(entry, source_config, keywords, time_range)
                    if article:
                        articles.append(article)
                
            except Exception as e:
                logger.error(f"Error parsing RSS feed {rss_url}: {e}")
        
        return articles
    
    async def _process_rss_entry(self, entry, source_config: Dict, keywords: List[str], time_range: int) -> Optional[NewsArticle]:
        """Process individual RSS entry"""
        try:
            # Extract basic information
            title = entry.get('title', '')
            url = entry.get('link', '')
            summary = entry.get('summary', '')
            
            # Check if article is relevant
            relevance_score = self._calculate_article_relevance(title + ' ' + summary, keywords)
            if relevance_score < 0.3:
                return None
            
            # Parse publish date
            publish_date = self._parse_publish_date(entry)
            
            # Check if within time range
            if not self._is_within_time_range(publish_date, time_range):
                return None
            
            # Extract content if needed
            content = await self._extract_article_content(url) if relevance_score > 0.7 else summary
            
            # Analyze sentiment
            sentiment = self._analyze_sentiment(title + ' ' + content)
            
            # Extract entities
            entities = self._extract_entities(title + ' ' + content)
            
            # Detect language
            language = self._detect_language(title + ' ' + content)
            
            # Create article object
            article = NewsArticle(
                title=title,
                url=url,
                content=content,
                summary=summary,
                source=source_config['name'],
                author=entry.get('author'),
                publish_date=publish_date,
                language=language,
                sentiment=sentiment,
                relevance_score=relevance_score,
                keywords=keywords,
                entities=entities,
                category=self._categorize_article(title + ' ' + content),
                confidence_score=source_config.get('credibility', 5) / 10,
                metadata={
                    'rss_feed': True,
                    'source_priority': source_config.get('priority', 5),
                    'source_credibility': source_config.get('credibility', 5)
                }
            )
            
            return article
            
        except Exception as e:
            logger.error(f"Error processing RSS entry: {e}")
            return None
    
    async def _search_website(self, source_config: Dict, keywords: List[str], time_range: int) -> List[NewsArticle]:
        """Search news website directly"""
        articles = []
        
        # Try searching with different keywords
        for keyword in keywords[:3]:  # Limit to avoid rate limiting
            try:
                search_url = source_config['search_url'].format(query=quote(keyword))
                search_results = await self._scrape_search_results(search_url, source_config)
                articles.extend(search_results)
                
            except Exception as e:
                logger.error(f"Error searching website for {keyword}: {e}")
        
        return articles
    
    async def _scrape_search_results(self, search_url: str, source_config: Dict) -> List[NewsArticle]:
        """Scrape search results from news website"""
        articles = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract article links (this would be customized per source)
                        article_links = self._extract_article_links(soup, source_config)
                        
                        # Process each article
                        for link in article_links[:10]:  # Limit results
                            article = await self._process_article_link(link, source_config)
                            if article:
                                articles.append(article)
            
        except Exception as e:
            logger.error(f"Error scraping search results: {e}")
        
        return articles
    
    def _extract_article_links(self, soup: BeautifulSoup, source_config: Dict) -> List[str]:
        """Extract article links from search results page"""
        links = []
        
        # Generic link extraction (would be customized per source)
        for link_element in soup.find_all('a', href=True):
            href = link_element['href']
            
            # Filter for article URLs
            if self._is_article_url(href, source_config):
                if href.startswith('/'):
                    href = urljoin(source_config['base_url'], href)
                links.append(href)
        
        return list(set(links))  # Remove duplicates
    
    def _is_article_url(self, url: str, source_config: Dict) -> bool:
        """Check if URL appears to be an article"""
        # Basic heuristics for article URLs
        article_indicators = [
            '/article/', '/news/', '/story/', '/post/', '/blog/',
            '/2024/', '/2025/', '/business/', '/technology/'
        ]
        
        exclude_patterns = [
            '/search/', '/tag/', '/category/', '/author/',
            '.pdf', '.jpg', '.png', '.gif', 'javascript:'
        ]
        
        url_lower = url.lower()
        
        # Check for article indicators
        has_article_indicator = any(indicator in url_lower for indicator in article_indicators)
        
        # Check for exclusion patterns
        has_exclusion = any(pattern in url_lower for pattern in exclude_patterns)
        
        return has_article_indicator and not has_exclusion
    
    async def _process_article_link(self, url: str, source_config: Dict) -> Optional[NewsArticle]:
        """Process individual article link"""
        try:
            content = await self._extract_article_content(url)
            if not content:
                return None
            
            # Extract article metadata
            metadata = await self._extract_article_metadata(url)
            
            # Create article object
            article = NewsArticle(
                title=metadata.get('title', ''),
                url=url,
                content=content,
                summary=content[:500] + '...' if len(content) > 500 else content,
                source=source_config['name'],
                author=metadata.get('author'),
                publish_date=metadata.get('publish_date', datetime.now()),
                language=self._detect_language(content),
                sentiment=self._analyze_sentiment(content),
                relevance_score=0.6,  # Default for web-scraped articles
                keywords=[],
                entities=self._extract_entities(content),
                category=self._categorize_article(content),
                confidence_score=source_config.get('credibility', 5) / 10,
                metadata={
                    'scraped': True,
                    'source_priority': source_config.get('priority', 5),
                    'source_credibility': source_config.get('credibility', 5)
                }
            )
            
            return article
            
        except Exception as e:
            logger.error(f"Error processing article {url}: {e}")
            return None
    
    async def _extract_article_content(self, url: str) -> Optional[str]:
        """Extract main content from article URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Remove scripts and styles
                        for script in soup(["script", "style", "nav", "footer", "aside"]):
                            script.decompose()
                        
                        # Try to find main content
                        content_selectors = [
                            'article', '.article-content', '.story-body',
                            '.post-content', '.entry-content', '.content',
                            'main', '.main-content'
                        ]
                        
                        content = ''
                        for selector in content_selectors:
                            content_elem = soup.select_one(selector)
                            if content_elem:
                                content = content_elem.get_text(strip=True)
                                break
                        
                        # Fallback to body content
                        if not content:
                            content = soup.get_text(strip=True)
                        
                        return content
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    async def _extract_article_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from article"""
        metadata = {}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract title
                        title_elem = soup.find('title') or soup.find('h1')
                        if title_elem:
                            metadata['title'] = title_elem.get_text(strip=True)
                        
                        # Extract meta tags
                        meta_tags = soup.find_all('meta')
                        for tag in meta_tags:
                            name = tag.get('name', '').lower()
                            property_name = tag.get('property', '').lower()
                            content = tag.get('content', '')
                            
                            if name in ['author', 'dc.creator']:
                                metadata['author'] = content
                            elif name in ['date', 'publish_date'] or property_name == 'article:published_time':
                                metadata['publish_date'] = self._parse_date_string(content)
                            elif name == 'description' or property_name == 'og:description':
                                metadata['description'] = content
        
        except Exception as e:
            logger.error(f"Error extracting metadata from {url}: {e}")
        
        return metadata
    
    def _calculate_article_relevance(self, text: str, keywords: List[str]) -> float:
        """Calculate relevance score for article"""
        if not text or not keywords:
            return 0.0
        
        text_lower = text.lower()
        total_score = 0.0
        
        for keyword in keywords:
            keyword_lower = keyword.lower().strip('"')
            
            # Exact keyword match
            if keyword_lower in text_lower:
                total_score += 1.0
            
            # Partial word matches
            words = keyword_lower.split()
            if len(words) > 1:
                word_matches = sum(1 for word in words if word in text_lower)
                total_score += (word_matches / len(words)) * 0.5
        
        # Normalize by number of keywords
        relevance_score = total_score / len(keywords)
        
        return min(relevance_score, 1.0)
    
    def _parse_publish_date(self, entry) -> datetime:
        """Parse publish date from RSS entry"""
        try:
            # Try different date fields
            date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
            
            for field in date_fields:
                if hasattr(entry, field) and getattr(entry, field):
                    time_struct = getattr(entry, field)
                    return datetime(*time_struct[:6])
            
            # Try string parsing
            date_strings = [entry.get('published', ''), entry.get('updated', '')]
            for date_string in date_strings:
                if date_string:
                    return self._parse_date_string(date_string)
            
        except Exception as e:
            logger.debug(f"Error parsing date: {e}")
        
        return datetime.now()
    
    def _parse_date_string(self, date_string: str) -> datetime:
        """Parse date string in various formats"""
        import dateutil.parser
        
        try:
            return dateutil.parser.parse(date_string)
        except:
            return datetime.now()
    
    def _is_within_time_range(self, publish_date: datetime, time_range: int) -> bool:
        """Check if article is within specified time range"""
        if not publish_date:
            return True  # Include articles without date
        
        cutoff_date = datetime.now() - timedelta(days=time_range)
        return publish_date >= cutoff_date
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text"""
        if not text:
            return 'neutral'
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.sentiment_keywords['positive'] if word in text_lower)
        negative_count = sum(1 for word in self.sentiment_keywords['negative'] if word in text_lower)
        
        if positive_count > negative_count and positive_count > 0:
            return 'positive'
        elif negative_count > positive_count and negative_count > 0:
            return 'negative'
        else:
            return 'neutral'
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text"""
        entities = []
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = pattern.findall(text)
            for match in matches:
                entities.append(f"{entity_type}:{match}")
        
        return list(set(entities))
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text"""
        if not text:
            return 'unknown'
        
        # Simple language detection based on character sets
        arabic_chars = len(self.language_patterns['arabic'].findall(text))
        english_chars = len(self.language_patterns['english'].findall(text))
        
        if arabic_chars > english_chars and arabic_chars > 10:
            return 'arabic'
        elif english_chars > 10:
            return 'english'
        else:
            return 'mixed'
    
    def _categorize_article(self, text: str) -> str:
        """Categorize article by topic"""
        text_lower = text.lower()
        
        categories = {
            'business': ['business', 'company', 'corporate', 'revenue', 'profit', 'financial'],
            'technology': ['technology', 'tech', 'software', 'AI', 'digital', 'innovation'],
            'politics': ['government', 'policy', 'political', 'minister', 'parliament'],
            'economics': ['economy', 'economic', 'market', 'trade', 'investment'],
            'energy': ['oil', 'gas', 'energy', 'renewable', 'solar', 'petroleum'],
            'healthcare': ['health', 'medical', 'hospital', 'medicine', 'pharmaceutical']
        }
        
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        else:
            return 'general'
    
    def _remove_duplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles"""
        seen_urls = set()
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            # Check URL duplicates
            if article.url in seen_urls:
                continue
            
            # Check title similarity (basic)
            title_normalized = article.title.lower().strip()
            if title_normalized in seen_titles:
                continue
            
            seen_urls.add(article.url)
            seen_titles.add(title_normalized)
            unique_articles.append(article)
        
        return unique_articles
    
    def _rank_articles_by_relevance(self, articles: List[NewsArticle], target: str, keywords: List[str]) -> List[NewsArticle]:
        """Rank articles by relevance and credibility"""
        
        for article in articles:
            # Recalculate relevance with full content
            content_relevance = self._calculate_article_relevance(
                article.title + ' ' + article.content, keywords
            )
            
            # Update relevance score
            article.relevance_score = content_relevance
            
            # Boost score based on source credibility
            article.relevance_score *= article.confidence_score
            
            # Boost recent articles
            days_old = (datetime.now() - article.publish_date).days
            if days_old <= 7:
                article.relevance_score *= 1.2
            elif days_old <= 30:
                article.relevance_score *= 1.1
        
        # Sort by relevance score
        return sorted(articles, key=lambda x: x.relevance_score, reverse=True)
    
    def _filter_by_time_range(self, articles: List[NewsArticle], time_range: int) -> List[NewsArticle]:
        """Filter articles by time range"""
        cutoff_date = datetime.now() - timedelta(days=time_range)
        
        return [
            article for article in articles 
            if article.publish_date >= cutoff_date
        ]
    
    async def track_media_mentions(self, entity: str, params: Dict) -> List[MediaMention]:
        """Track media mentions across various platforms"""
        logger.info(f"Tracking media mentions for: {entity}")
        
        mentions = []
        
        # Search news articles
        news_articles = await self.comprehensive_news_monitoring(entity, params)
        
        # Convert articles to mentions
        for article in news_articles:
            mention = MediaMention(
                mention_type='article',
                platform=article.source,
                url=article.url,
                title=article.title,
                content_snippet=article.summary,
                mention_context=self._extract_mention_context(article.content, entity),
                sentiment=article.sentiment,
                reach_estimate=self._estimate_article_reach(article),
                engagement_metrics={},
                publish_date=article.publish_date,
                confidence_score=article.confidence_score
            )
            mentions.append(mention)
        
        # TODO: Add social media mentions, press releases, blogs
        
        return mentions
    
    def _extract_mention_context(self, content: str, entity: str) -> str:
        """Extract context around entity mention"""
        if not content or not entity:
            return ""
        
        # Find entity in content
        entity_lower = entity.lower()
        content_lower = content.lower()
        
        entity_pos = content_lower.find(entity_lower)
        if entity_pos == -1:
            return content[:200] + "..." if len(content) > 200 else content
        
        # Extract context around mention
        start = max(0, entity_pos - 100)
        end = min(len(content), entity_pos + len(entity) + 100)
        
        context = content[start:end]
        if start > 0:
            context = "..." + context
        if end < len(content):
            context = context + "..."
        
        return context
    
    def _estimate_article_reach(self, article: NewsArticle) -> int:
        """Estimate reach of article based on source"""
        # Simple reach estimation based on source credibility and type
        base_reach = {
            'Reuters': 10000000,
            'Bloomberg': 8000000,
            'BBC News': 15000000,
            'Arab News': 2000000,
            'Gulf News': 1500000,
            'Al Jazeera': 5000000,
            'TechCrunch': 3000000,
            'Wired': 2000000,
            'Financial Times': 4000000
        }
        
        return base_reach.get(article.source, 100000)  # Default 100k reach
    
    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Get news monitoring statistics"""
        total_sources = sum(len(category) for category in self.news_sources.values())
        
        return {
            'total_sources': total_sources,
            'source_categories': list(self.news_sources.keys()),
            'supported_languages': ['english', 'arabic'],
            'sentiment_keywords': {
                category: len(keywords) 
                for category, keywords in self.sentiment_keywords.items()
            },
            'entity_patterns': list(self.entity_patterns.keys()),
            'article_categories': [
                'business', 'technology', 'politics', 'economics', 
                'energy', 'healthcare', 'general'
            ]
        }

# Example usage and testing
async def test_news_monitoring():
    """Test news monitoring collector"""
    collector = NewsMonitoringCollector()
    
    test_targets = [
        "Saudi Aramco",
        "artificial intelligence Saudi Arabia",
        "Dubai technology companies",
        "renewable energy Gulf"
    ]
    
    for target in test_targets:
        print(f"\n=== Testing news monitoring for: {target} ===")
        
        params = {
            'monitoring_scope': 'quick',
            'time_range': 7,  # Last 7 days
            'context': 'investment_research',
            'languages': ['english'],
            'industry': 'technology'
        }
        
        try:
            articles = await collector.comprehensive_news_monitoring(target, params)
            print(f"Found {