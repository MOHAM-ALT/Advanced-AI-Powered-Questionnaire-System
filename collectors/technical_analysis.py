#!/usr/bin/env python3
"""
Advanced Technical Analysis Collector
File Location: collectors/technical_analysis.py
Technical infrastructure and security analysis for domains and systems
"""

import asyncio
import aiohttp
import re
import json
import ssl
import socket
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from urllib.parse import urlparse, urljoin
import dns.resolver
import whois
from pathlib import Path

# Import utilities
from utils.rate_limiter import RateLimiter
from utils.proxy_manager import ProxyManager

logger = logging.getLogger(__name__)

@dataclass
class TechnicalProfile:
    """Technical infrastructure profile"""
    domain: str
    ip_addresses: List[str]
    subdomains: List[str]
    dns_records: Dict[str, List[str]]
    ssl_certificate: Dict[str, Any]
    web_technologies: List[str]
    server_info: Dict[str, str]
    security_headers: Dict[str, str]
    open_ports: List[int]
    whois_data: Dict[str, Any]
    hosting_provider: str
    cdn_services: List[str]
    email_security: Dict[str, Any]
    vulnerability_indicators: List[str]
    confidence_score: float
    scan_timestamp: datetime

@dataclass
class SecurityAssessment:
    """Security assessment results"""
    domain: str
    security_score: float
    vulnerabilities: List[Dict[str, Any]]
    security_headers: Dict[str, Any]
    ssl_assessment: Dict[str, Any]
    dns_security: Dict[str, Any]
    email_security: Dict[str, Any]
    exposed_services: List[Dict[str, Any]]
    recommendations: List[str]
    risk_level: str  # low, medium, high, critical
    assessment_date: datetime

class TechnicalAnalysisCollector:
    """Advanced technical analysis and security assessment collector"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.proxy_manager = ProxyManager()
        
        # Technology detection patterns
        self.tech_patterns = self._initialize_tech_patterns()
        
        # Security header patterns
        self.security_headers = self._initialize_security_headers()
        
        # Vulnerability patterns
        self.vulnerability_patterns = self._initialize_vulnerability_patterns()
        
        # CDN and hosting provider patterns
        self.infrastructure_patterns = self._initialize_infrastructure_patterns()
        
        logger.info("Technical analysis collector initialized")
    
    def _initialize_tech_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize technology detection patterns"""
        return {
            'web_servers': {
                'apache': {
                    'headers': ['Server: Apache', 'X-Powered-By: Apache'],
                    'signatures': ['apache', 'httpd'],
                    'confidence': 0.9
                },
                'nginx': {
                    'headers': ['Server: nginx', 'Server: nginx/'],
                    'signatures': ['nginx'],
                    'confidence': 0.9
                },
                'iis': {
                    'headers': ['Server: Microsoft-IIS', 'X-Powered-By: ASP.NET'],
                    'signatures': ['microsoft-iis', 'asp.net'],
                    'confidence': 0.9
                },
                'cloudflare': {
                    'headers': ['Server: cloudflare', 'CF-RAY'],
                    'signatures': ['cloudflare'],
                    'confidence': 0.8
                }
            },
            'frameworks': {
                'wordpress': {
                    'signatures': ['/wp-content/', '/wp-includes/', 'wp-json'],
                    'meta_tags': ['generator.*wordpress'],
                    'confidence': 0.9
                },
                'drupal': {
                    'signatures': ['/sites/default/', 'drupal.js', 'misc/drupal.js'],
                    'meta_tags': ['generator.*drupal'],
                    'confidence': 0.9
                },
                'joomla': {
                    'signatures': ['/templates/', '/administrator/', 'joomla'],
                    'meta_tags': ['generator.*joomla'],
                    'confidence': 0.8
                },
                'react': {
                    'signatures': ['react', '_next/', '__NEXT_DATA__'],
                    'javascript': ['React.createElement', 'ReactDOM'],
                    'confidence': 0.7
                },
                'angular': {
                    'signatures': ['angular', 'ng-'],
                    'javascript': ['angular.js', 'ng-app'],
                    'confidence': 0.7
                }
            },
            'programming_languages': {
                'php': {
                    'headers': ['X-Powered-By: PHP'],
                    'signatures': ['.php', 'PHPSESSID'],
                    'confidence': 0.8
                },
                'python': {
                    'headers': ['Server: gunicorn', 'Server: uwsgi'],
                    'signatures': ['django', 'flask'],
                    'confidence': 0.7
                },
                'java': {
                    'headers': ['X-Powered-By: Servlet'],
                    'signatures': ['jsessionid', '.jsp'],
                    'confidence': 0.8
                },
                'node_js': {
                    'headers': ['X-Powered-By: Express'],
                    'signatures': ['node.js', 'express'],
                    'confidence': 0.7
                }
            },
            'databases': {
                'mysql': {
                    'error_signatures': ['mysql', 'sql syntax'],
                    'confidence': 0.6
                },
                'postgresql': {
                    'error_signatures': ['postgresql', 'psql'],
                    'confidence': 0.6
                },
                'mongodb': {
                    'signatures': ['mongodb', 'mongo'],
                    'confidence': 0.5
                }
            },
            'analytics': {
                'google_analytics': {
                    'signatures': ['google-analytics', 'gtag', 'UA-'],
                    'confidence': 0.9
                },
                'google_tag_manager': {
                    'signatures': ['googletagmanager', 'GTM-'],
                    'confidence': 0.9
                },
                'facebook_pixel': {
                    'signatures': ['facebook.net/tr', 'fbq('],
                    'confidence': 0.8
                }
            }
        }
    
    def _initialize_security_headers(self) -> Dict[str, Dict[str, Any]]:
        """Initialize security headers to check"""
        return {
            'content_security_policy': {
                'header': 'Content-Security-Policy',
                'importance': 'high',
                'description': 'Prevents XSS and data injection attacks'
            },
            'strict_transport_security': {
                'header': 'Strict-Transport-Security',
                'importance': 'high',
                'description': 'Forces HTTPS connections'
            },
            'x_frame_options': {
                'header': 'X-Frame-Options',
                'importance': 'medium',
                'description': 'Prevents clickjacking attacks'
            },
            'x_content_type_options': {
                'header': 'X-Content-Type-Options',
                'importance': 'medium',
                'description': 'Prevents MIME type sniffing'
            },
            'x_xss_protection': {
                'header': 'X-XSS-Protection',
                'importance': 'low',
                'description': 'Legacy XSS protection'
            },
            'referrer_policy': {
                'header': 'Referrer-Policy',
                'importance': 'medium',
                'description': 'Controls referrer information'
            },
            'permissions_policy': {
                'header': 'Permissions-Policy',
                'importance': 'medium',
                'description': 'Controls browser features'
            }
        }
    
    def _initialize_vulnerability_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize vulnerability detection patterns"""
        return {
            'directory_listing': {
                'signatures': ['Index of /', 'Directory Listing', 'Parent Directory'],
                'severity': 'medium',
                'description': 'Directory listing enabled'
            },
            'default_pages': {
                'signatures': ['Apache2 Ubuntu Default Page', 'IIS Windows Server', 'nginx welcome'],
                'severity': 'low',
                'description': 'Default server pages exposed'
            },
            'admin_panels': {
                'paths': ['/admin', '/administrator', '/wp-admin', '/phpmyadmin'],
                'severity': 'medium',
                'description': 'Admin panels accessible'
            },
            'backup_files': {
                'paths': ['/backup', '/.backup', '/db.sql', '/database.sql'],
                'severity': 'high',
                'description': 'Backup files accessible'
            },
            'config_files': {
                'paths': ['/config', '/.env', '/web.config', '/.htaccess'],
                'severity': 'high',
                'description': 'Configuration files exposed'
            },
            'version_disclosure': {
                'signatures': ['Server: Apache/2.', 'Server: nginx/1.', 'X-Powered-By: PHP/'],
                'severity': 'low',
                'description': 'Server version disclosed'
            }
        }
    
    def _initialize_infrastructure_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize infrastructure detection patterns"""
        return {
            'cdn_providers': {
                'cloudflare': {
                    'headers': ['CF-RAY', 'Server: cloudflare'],
                    'cname_patterns': ['cloudflare.com'],
                    'ip_ranges': ['103.21.244.0/22', '103.22.200.0/22']
                },
                'aws_cloudfront': {
                    'headers': ['X-Amz-Cf-Id', 'X-Amz-Cf-Pop'],
                    'cname_patterns': ['cloudfront.net'],
                    'server_signatures': ['CloudFront']
                },
                'akamai': {
                    'headers': ['X-Akamai-Transformed'],
                    'cname_patterns': ['akamai.net', 'akamaized.net'],
                    'server_signatures': ['AkamaiGHost']
                }
            },
            'hosting_providers': {
                'aws': {
                    'ip_ranges': ['52.', '54.', '18.'],
                    'cname_patterns': ['amazonaws.com'],
                    'indicators': ['aws', 'amazon']
                },
                'google_cloud': {
                    'ip_ranges': ['35.', '34.', '104.'],
                    'cname_patterns': ['googleusercontent.com'],
                    'indicators': ['google', 'gcp']
                },
                'microsoft_azure': {
                    'ip_ranges': ['20.', '40.', '52.'],
                    'cname_patterns': ['azurewebsites.net'],
                    'indicators': ['azure', 'microsoft']
                }
            }
        }

    async def comprehensive_technical_analysis(self, domain: str, params: Dict) -> TechnicalProfile:
        """
        Comprehensive technical analysis of domain infrastructure
        """
        logger.info(f"Starting technical analysis for: {domain}")
        
        # Clean domain input
        domain = self._clean_domain(domain)
        
        # DNS Analysis
        dns_records = await self._comprehensive_dns_analysis(domain)
        ip_addresses = dns_records.get('A', [])
        
        # Subdomain enumeration
        subdomains = await self._enumerate_subdomains(domain, params)
        
        # WHOIS analysis
        whois_data = await self._whois_analysis(domain)
        
        # SSL certificate analysis
        ssl_certificate = await self._ssl_certificate_analysis(domain)
        
        # Web technology detection
        web_technologies = await self._detect_web_technologies(domain)
        
        # Server information extraction
        server_info = await self._extract_server_info(domain)
        
        # Security headers analysis
        security_headers = await self._analyze_security_headers(domain)
        
        # Port scanning (limited and ethical)
        open_ports = await self._basic_port_scan(ip_addresses[0]) if ip_addresses else []
        
        # Hosting and CDN detection
        hosting_provider = await self._detect_hosting_provider(domain, ip_addresses)
        cdn_services = await self._detect_cdn_services(domain)
        
        # Email security analysis
        email_security = await self._analyze_email_security(domain)
        
        # Vulnerability indicators
        vulnerability_indicators = await self._check_vulnerability_indicators(domain)
        
        # Calculate confidence score
        confidence_score = self._calculate_technical_confidence(
            dns_records, ssl_certificate, web_technologies, server_info
        )
        
        profile = TechnicalProfile(
            domain=domain,
            ip_addresses=ip_addresses,
            subdomains=subdomains,
            dns_records=dns_records,
            ssl_certificate=ssl_certificate,
            web_technologies=web_technologies,
            server_info=server_info,
            security_headers=security_headers,
            open_ports=open_ports,
            whois_data=whois_data,
            hosting_provider=hosting_provider,
            cdn_services=cdn_services,
            email_security=email_security,
            vulnerability_indicators=vulnerability_indicators,
            confidence_score=confidence_score,
            scan_timestamp=datetime.now()
        )
        
        logger.info(f"Technical analysis completed for {domain}")
        return profile
    
    def _clean_domain(self, domain: str) -> str:
        """Clean and normalize domain input"""
        # Remove protocol if present
        if '://' in domain:
            domain = urlparse(domain).netloc
        
        # Remove port if present
        if ':' in domain:
            domain = domain.split(':')[0]
        
        # Remove www prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain.lower().strip()
    
    async def _comprehensive_dns_analysis(self, domain: str) -> Dict[str, List[str]]:
        """Comprehensive DNS record analysis"""
        dns_records = {}
        
        # DNS record types to query
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'PTR']
        
        for record_type in record_types:
            try:
                await self.rate_limiter.wait_if_needed(f'dns_{record_type}')
                
                records = await self._dns_lookup(domain, record_type)
                dns_records[record_type] = records
                
            except Exception as e:
                logger.debug(f"DNS lookup failed for {record_type}: {e}")
                dns_records[record_type] = []
        
        return dns_records
    
    async def _dns_lookup(self, domain: str, record_type: str) -> List[str]:
        """Perform DNS lookup for specific record type"""
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 10
            
            answers = resolver.resolve(domain, record_type)
            return [str(answer) for answer in answers]
            
        except Exception:
            return []
    
    async def _enumerate_subdomains(self, domain: str, params: Dict) -> List[str]:
        """Enumerate subdomains using various techniques"""
        subdomains = set()
        
        # Common subdomain wordlist
        common_subdomains = [
            'www', 'mail', 'ftp', 'admin', 'test', 'dev', 'staging', 'api',
            'blog', 'shop', 'store', 'app', 'mobile', 'support', 'help',
            'secure', 'portal', 'dashboard', 'login', 'panel', 'cpanel',
            'webmail', 'email', 'smtp', 'pop', 'imap', 'ns1', 'ns2',
            'cdn', 'static', 'assets', 'img', 'images', 'css', 'js',
            'beta', 'alpha', 'demo', 'preview', 'old', 'new', 'v2'
        ]
        
        # DNS brute force enumeration
        enumeration_depth = params.get('enumeration_depth', 'standard')
        if enumeration_depth == 'comprehensive':
            common_subdomains.extend([
                'vpn', 'git', 'gitlab', 'jenkins', 'ci', 'build',
                'monitoring', 'logs', 'metrics', 'health', 'status'
            ])
        
        # Test common subdomains
        tasks = []
        for subdomain in common_subdomains:
            full_domain = f"{subdomain}.{domain}"
            task = self._check_subdomain_exists(full_domain)
            tasks.append((subdomain, task))
        
        # Execute subdomain checks with rate limiting
        for subdomain, task in tasks:
            try:
                await self.rate_limiter.wait_if_needed('subdomain_enum')
                exists = await task
                if exists:
                    subdomains.add(f"{subdomain}.{domain}")
            except Exception as e:
                logger.debug(f"Subdomain check failed for {subdomain}: {e}")
        
        # Certificate transparency search (simulation)
        ct_subdomains = await self._certificate_transparency_search(domain)
        subdomains.update(ct_subdomains)
        
        return list(subdomains)
    
    async def _check_subdomain_exists(self, subdomain: str) -> bool:
        """Check if subdomain exists via DNS lookup"""
        try:
            await self._dns_lookup(subdomain, 'A')
            return True
        except:
            return False
    
    async def _certificate_transparency_search(self, domain: str) -> List[str]:
        """Search certificate transparency logs for subdomains"""
        # Simulate CT log search (in production, would query actual CT logs)
        common_ct_subdomains = [
            f"mail.{domain}",
            f"www.{domain}",
            f"api.{domain}",
            f"cdn.{domain}",
            f"secure.{domain}"
        ]
        
        # Verify which ones actually exist
        valid_subdomains = []
        for subdomain in common_ct_subdomains:
            if await self._check_subdomain_exists(subdomain):
                valid_subdomains.append(subdomain)
        
        return valid_subdomains
    
    async def _whois_analysis(self, domain: str) -> Dict[str, Any]:
        """Perform WHOIS analysis"""
        try:
            whois_data = whois.whois(domain)
            
            return {
                'domain': domain,
                'registrar': whois_data.registrar,
                'creation_date': whois_data.creation_date,
                'expiration_date': whois_data.expiration_date,
                'updated_date': whois_data.updated_date,
                'name_servers': whois_data.name_servers,
                'status': whois_data.status,
                'emails': whois_data.emails,
                'country': whois_data.country,
                'organization': whois_data.org
            }
            
        except Exception as e:
            logger.error(f"WHOIS lookup failed for {domain}: {e}")
            return {'domain': domain, 'error': str(e)}
    
    async def _ssl_certificate_analysis(self, domain: str) -> Dict[str, Any]:
        """Analyze SSL certificate"""
        ssl_info = {}
        
        try:
            # Get SSL certificate information
            context = ssl.create_default_context()
            
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    ssl_info = {
                        'subject': dict(x[0] for x in cert['subject']),
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'version': cert['version'],
                        'serialNumber': cert['serialNumber'],
                        'notBefore': cert['notBefore'],
                        'notAfter': cert['notAfter'],
                        'subjectAltName': cert.get('subjectAltName', []),
                        'OCSP': cert.get('OCSP', []),
                        'caIssuers': cert.get('caIssuers', []),
                        'crlDistributionPoints': cert.get('crlDistributionPoints', [])
                    }
                    
                    # Calculate certificate validity
                    ssl_info['is_valid'] = self._check_ssl_validity(cert)
                    ssl_info['days_until_expiry'] = self._calculate_cert_expiry_days(cert)
        
        except Exception as e:
            logger.debug(f"SSL analysis failed for {domain}: {e}")
            ssl_info = {'error': str(e), 'ssl_enabled': False}
        
        return ssl_info
    
    def _check_ssl_validity(self, cert: Dict) -> bool:
        """Check if SSL certificate is valid"""
        try:
            from datetime import datetime
            import ssl
            
            not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
            not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            now = datetime.now()
            
            return not_before <= now <= not_after
            
        except:
            return False
    
    def _calculate_cert_expiry_days(self, cert: Dict) -> int:
        """Calculate days until certificate expiry"""
        try:
            from datetime import datetime
            
            not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            now = datetime.now()
            
            return (not_after - now).days
            
        except:
            return -1
    
    async def _detect_web_technologies(self, domain: str) -> List[str]:
        """Detect web technologies used by the domain"""
        technologies = []
        
        try:
            url = f"https://{domain}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    headers = dict(response.headers)
                    html_content = await response.text()
                    
                    # Analyze headers for technology signatures
                    tech_from_headers = self._analyze_headers_for_tech(headers)
                    technologies.extend(tech_from_headers)
                    
                    # Analyze HTML content for technology signatures
                    tech_from_html = self._analyze_html_for_tech(html_content)
                    technologies.extend(tech_from_html)
        
        except Exception as e:
            logger.debug(f"Technology detection failed for {domain}: {e}")
        
        return list(set(technologies))  # Remove duplicates
    
    def _analyze_headers_for_tech(self, headers: Dict[str, str]) -> List[str]:
        """Analyze HTTP headers for technology signatures"""
        technologies = []
        
        for category, tech_dict in self.tech_patterns.items():
            for tech_name, patterns in tech_dict.items():
                # Check header patterns
                header_patterns = patterns.get('headers', [])
                for pattern in header_patterns:
                    for header_name, header_value in headers.items():
                        if pattern.lower() in f"{header_name}: {header_value}".lower():
                            technologies.append(f"{category}:{tech_name}")
                            break
        
        return technologies
    
    def _analyze_html_for_tech(self, html_content: str) -> List[str]:
        """Analyze HTML content for technology signatures"""
        technologies = []
        html_lower = html_content.lower()
        
        for category, tech_dict in self.tech_patterns.items():
            for tech_name, patterns in tech_dict.items():
                # Check signature patterns
                signatures = patterns.get('signatures', [])
                for signature in signatures:
                    if signature.lower() in html_lower:
                        technologies.append(f"{category}:{tech_name}")
                        break
                
                # Check meta tag patterns
                meta_patterns = patterns.get('meta_tags', [])
                for pattern in meta_patterns:
                    if re.search(pattern, html_lower):
                        technologies.append(f"{category}:{tech_name}")
                        break
        
        return technologies
    
    async def _extract_server_info(self, domain: str) -> Dict[str, str]:
        """Extract server information from HTTP headers"""
        server_info = {}
        
        try:
            url = f"https://{domain}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    headers = dict(response.headers)
                    
                    # Extract relevant server headers
                    relevant_headers = [
                        'Server', 'X-Powered-By', 'X-AspNet-Version',
                        'X-Generator', 'X-Drupal-Cache', 'X-Pingback'
                    ]
                    
                    for header in relevant_headers:
                        if header in headers:
                            server_info[header] = headers[header]
                    
                    # Extract additional information
                    server_info['status_code'] = response.status
                    server_info['content_type'] = headers.get('Content-Type', '')
                    server_info['content_length'] = headers.get('Content-Length', '')
        
        except Exception as e:
            logger.debug(f"Server info extraction failed for {domain}: {e}")
            server_info['error'] = str(e)
        
        return server_info
    
    async def _analyze_security_headers(self, domain: str) -> Dict[str, str]:
        """Analyze security headers"""
        security_headers = {}
        
        try:
            url = f"https://{domain}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    headers = dict(response.headers)
                    
                    # Check for each security header
                    for header_id, header_info in self.security_headers.items():
                        header_name = header_info['header']
                        if header_name in headers:
                            security_headers[header_name] = headers[header_name]
                        else:
                            security_headers[header_name] = 'Missing'
        
        except Exception as e:
            logger.debug(f"Security headers analysis failed for {domain}: {e}")
            security_headers['error'] = str(e)
        
        return security_headers
    
    async def _basic_port_scan(self, ip_address: str) -> List[int]:
        """Perform basic port scan on common ports"""
        if not ip_address:
            return []
        
        # Common ports to check
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306]
        open_ports = []
        
        for port in common_ports:
            try:
                await self.rate_limiter.wait_if_needed('port_scan')
                
                # Simple TCP connect scan
                future = asyncio.open_connection(ip_address, port)
                try:
                    reader, writer = await asyncio.wait_for(future, timeout=3)
                    writer.close()
                    await writer.wait_closed()
                    open_ports.append(port)
                except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
                    pass
                    
            except Exception as e:
                logger.debug(f"Port scan error for {ip_address}:{port}: {e}")
        
        return open_ports
    
    async def _detect_hosting_provider(self, domain: str, ip_addresses: List[str]) -> str:
        """Detect hosting provider"""
        if not ip_addresses:
            return 'unknown'
        
        ip = ip_addresses[0]
        
        # Check against known IP ranges and patterns
        for provider, patterns in self.infrastructure_patterns['hosting_providers'].items():
            # Check IP range patterns
            ip_ranges = patterns.get('ip_ranges', [])
            for ip_range in ip_ranges:
                if ip.startswith(ip_range):
                    return provider
        
        # Check WHOIS data for hosting provider
        try:
            # Simple reverse DNS lookup
            hostname = socket.gethostbyaddr(ip)[0]
            
            for provider, patterns in self.infrastructure_patterns['hosting_providers'].items():
                indicators = patterns.get('indicators', [])
                for indicator in indicators:
                    if indicator in hostname.lower():
                        return provider
                        
        except Exception:
            pass
        
        return 'unknown'
    
    async def _detect_cdn_services(self, domain: str) -> List[str]:
        """Detect CDN services"""
        cdn_services = []
        
        try:
            url = f"https://{domain}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    headers = dict(response.headers)
                    
                    # Check headers for