#!/usr/bin/env python3
"""
Advanced Proxy Management System
File Location: utils/proxy_manager.py
Intelligent proxy rotation and health monitoring
"""

import asyncio
import aiohttp
import random
import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class ProxyInfo:
    """Proxy information structure"""
    url: str
    protocol: str  # http, https, socks4, socks5
    username: Optional[str] = None
    password: Optional[str] = None
    last_used: float = 0
    success_count: int = 0
    failure_count: int = 0
    response_time: float = 0
    is_working: bool = True
    location: Optional[str] = None

class ProxyManager:
    """Advanced proxy management with health monitoring"""
    
    def __init__(self):
        self.enabled = False
        self.proxies: List[ProxyInfo] = []
        self.current_proxy_index = 0
        self.rotation_strategy = "round_robin"  # round_robin, random, performance
        self.health_check_interval = 300  # 5 minutes
        self.max_failures = 3
        self.timeout = 10
        
        # Health monitoring
        self.last_health_check = 0
        self.working_proxies: List[ProxyInfo] = []
        
        # Load configuration
        self._load_configuration()
    
    def _load_configuration(self):
        """Load proxy configuration from file"""
        config_path = Path("config/proxy_config.json")
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                self.enabled = config.get('enabled', False)
                self.rotation_strategy = config.get('rotation_strategy', 'round_robin')
                self.health_check_interval = config.get('health_check_interval', 300)
                self.max_failures = config.get('max_failures', 3)
                self.timeout = config.get('timeout', 10)
                
                # Load proxy list
                proxy_list = config.get('proxies', [])
                for proxy_data in proxy_list:
                    proxy = ProxyInfo(
                        url=proxy_data['url'],
                        protocol=proxy_data.get('protocol', 'http'),
                        username=proxy_data.get('username'),
                        password=proxy_data.get('password'),
                        location=proxy_data.get('location')
                    )
                    self.proxies.append(proxy)
                
                logger.info(f"Loaded {len(self.proxies)} proxies from configuration")
                
            except Exception as e:
                logger.error(f"Failed to load proxy configuration: {e}")
        
        # If no configuration file, create default
        else:
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default proxy configuration"""
        default_config = {
            "enabled": False,
            "rotation_strategy": "round_robin",
            "health_check_interval": 300,
            "max_failures": 3,
            "timeout": 10,
            "proxies": [
                # Example proxy configurations (commented out)
                # {
                #     "url": "http://proxy1.example.com:8080",
                #     "protocol": "http",
                #     "username": "user1",
                #     "password": "pass1",
                #     "location": "US"
                # },
                # {
                #     "url": "socks5://proxy2.example.com:1080",
                #     "protocol": "socks5",
                #     "location": "EU"
                # }
            ],
            "notes": [
                "Set enabled to true to use proxy rotation",
                "Add your proxy servers to the proxies array",
                "Supported protocols: http, https, socks4, socks5",
                "rotation_strategy options: round_robin, random, performance"
            ]
        }
        
        config_path = Path("config/proxy_config.json")
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        logger.info("Created default proxy configuration file")
    
    def configure(self, enabled: bool = False, proxy_file: Optional[str] = None):
        """Configure proxy manager"""
        self.enabled = enabled
        
        if enabled and proxy_file:
            self.load_proxies_from_file(proxy_file)
        
        logger.info(f"Proxy manager configured: enabled={enabled}, proxies={len(self.proxies)}")
    
    def load_proxies_from_file(self, proxy_file: str):
        """Load proxies from text file (one per line)"""
        try:
            proxy_path = Path(proxy_file)
            if not proxy_path.exists():
                logger.error(f"Proxy file not found: {proxy_file}")
                return
            
            with open(proxy_path, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    proxy = self._parse_proxy_string(line)
                    if proxy:
                        self.proxies.append(proxy)
            
            logger.info(f"Loaded {len(self.proxies)} proxies from file: {proxy_file}")
            
        except Exception as e:
            logger.error(f"Failed to load proxies from file: {e}")
            self.enabled = False
    
    def _parse_proxy_string(self, proxy_string: str) -> Optional[ProxyInfo]:
        """Parse proxy string into ProxyInfo object"""
        try:
            # Support formats:
            # http://proxy:port
            # http://user:pass@proxy:port
            # socks5://proxy:port
            
            if '://' in proxy_string:
                parts = proxy_string.split('://', 1)
                protocol = parts[0]
                rest = parts[1]
            else:
                protocol = 'http'
                rest = proxy_string
            
            # Extract credentials if present
            username = None
            password = None
            
            if '@' in rest:
                auth_part, host_part = rest.rsplit('@', 1)
                if ':' in auth_part:
                    username, password = auth_part.split(':', 1)
                else:
                    username = auth_part
                url = f"{protocol}://{host_part}"
            else:
                url = f"{protocol}://{rest}"
            
            return ProxyInfo(
                url=url,
                protocol=protocol,
                username=username,
                password=password
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse proxy string '{proxy_string}': {e}")
            return None
    
    def add_proxy(self, url: str, protocol: str = 'http', username: str = None, 
                  password: str = None, location: str = None):
        """Add a proxy manually"""
        proxy = ProxyInfo(
            url=url,
            protocol=protocol,
            username=username,
            password=password,
            location=location
        )
        
        self.proxies.append(proxy)
        logger.info(f"Added proxy: {url}")
    
    async def get_proxy(self) -> Optional[str]:
        """Get next proxy based on rotation strategy"""
        if not self.enabled or not self.proxies:
            return None
        
        # Perform health check if needed
        await self._health_check_if_needed()
        
        # Use working proxies if available
        available_proxies = self.working_proxies if self.working_proxies else self.proxies
        
        if not available_proxies:
            logger.warning("No working proxies available")
            return None
        
        # Select proxy based on strategy
        proxy = None
        
        if self.rotation_strategy == "round_robin":
            proxy = available_proxies[self.current_proxy_index % len(available_proxies)]
            self.current_proxy_index = (self.current_proxy_index + 1) % len(available_proxies)
        
        elif self.rotation_strategy == "random":
            proxy = random.choice(available_proxies)
        
        elif self.rotation_strategy == "performance":
            # Sort by success rate and response time
            sorted_proxies = sorted(
                available_proxies,
                key=lambda p: (p.success_count / max(p.success_count + p.failure_count, 1), -p.response_time),
                reverse=True
            )
            proxy = sorted_proxies[0]
        
        if proxy:
            proxy.last_used = time.time()
            return self._format_proxy_url(proxy)
        
        return None
    
    def _format_proxy_url(self, proxy: ProxyInfo) -> str:
        """Format proxy URL for use with aiohttp"""
        if proxy.username and proxy.password:
            # Insert credentials into URL
            parts = proxy.url.split('://', 1)
            if len(parts) == 2:
                protocol, host = parts
                return f"{protocol}://{proxy.username}:{proxy.password}@{host}"
        
        return proxy.url
    
    async def _health_check_if_needed(self):
        """Perform health check if interval has passed"""
        current_time = time.time()
        
        if current_time - self.last_health_check > self.health_check_interval:
            await self._perform_health_check()
            self.last_health_check = current_time
    
    async def _perform_health_check(self):
        """Perform health check on all proxies"""
        logger.info("Starting proxy health check...")
        
        working_proxies = []
        
        # Test each proxy
        tasks = []
        for proxy in self.proxies:
            task = self._test_proxy(proxy)
            tasks.append(task)
        
        # Run tests in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            proxy = self.proxies[i]
            
            if isinstance(result, Exception):
                proxy.failure_count += 1
                proxy.is_working = False
                logger.debug(f"Proxy {proxy.url} failed health check: {result}")
            else:
                is_working, response_time = result
                
                if is_working:
                    proxy.success_count += 1
                    proxy.response_time = response_time
                    proxy.is_working = True
                    working_proxies.append(proxy)
                else:
                    proxy.failure_count += 1
                    proxy.is_working = False
                
                # Disable proxy if too many failures
                if proxy.failure_count >= self.max_failures:
                    proxy.is_working = False
        
        self.working_proxies = working_proxies
        logger.info(f"Health check completed: {len(working_proxies)}/{len(self.proxies)} proxies working")
    
    async def _test_proxy(self, proxy: ProxyInfo) -> Tuple[bool, float]:
        """Test a single proxy"""
        test_url = "https://httpbin.org/ip"
        
        try:
            start_time = time.time()
            
            # Configure proxy for aiohttp
            proxy_url = self._format_proxy_url(proxy)
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(test_url, proxy=proxy_url) as response:
                    if response.status == 200:
                        response_time = time.time() - start_time
                        return True, response_time
                    else:
                        return False, 0
        
        except Exception:
            return False, 0
    
    def mark_proxy_failed(self, proxy_url: str):
        """Mark a proxy as failed"""
        for proxy in self.proxies:
            if self._format_proxy_url(proxy) == proxy_url:
                proxy.failure_count += 1
                
                if proxy.failure_count >= self.max_failures:
                    proxy.is_working = False
                    if proxy in self.working_proxies:
                        self.working_proxies.remove(proxy)
                
                logger.debug(f"Marked proxy as failed: {proxy.url} (failures: {proxy.failure_count})")
                break
    
    def mark_proxy_success(self, proxy_url: str):
        """Mark a proxy as successful"""
        for proxy in self.proxies:
            if self._format_proxy_url(proxy) == proxy_url:
                proxy.success_count += 1
                proxy.is_working = True
                
                if proxy not in self.working_proxies:
                    self.working_proxies.append(proxy)
                
                break
    
    def get_proxy_statistics(self) -> Dict:
        """Get proxy usage statistics"""
        if not self.proxies:
            return {"total_proxies": 0, "working_proxies": 0}
        
        total_proxies = len(self.proxies)
        working_proxies = len([p for p in self.proxies if p.is_working])
        
        total_requests = sum(p.success_count + p.failure_count for p in self.proxies)
        total_successes = sum(p.success_count for p in self.proxies)
        
        success_rate = (total_successes / total_requests) if total_requests > 0 else 0
        
        # Average response time
        response_times = [p.response_time for p in self.proxies if p.response_time > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "enabled": self.enabled,
            "total_proxies": total_proxies,
            "working_proxies": working_proxies,
            "total_requests": total_requests,
            "success_rate": success_rate,
            "average_response_time": avg_response_time,
            "rotation_strategy": self.rotation_strategy,
            "last_health_check": self.last_health_check
        }
    
    def get_proxy_details(self) -> List[Dict]:
        """Get detailed information about all proxies"""
        details = []
        
        for proxy in self.proxies:
            total_requests = proxy.success_count + proxy.failure_count
            success_rate = (proxy.success_count / total_requests) if total_requests > 0 else 0
            
            details.append({
                "url": proxy.url,
                "protocol": proxy.protocol,
                "location": proxy.location,
                "is_working": proxy.is_working,
                "success_count": proxy.success_count,
                "failure_count": proxy.failure_count,
                "success_rate": success_rate,
                "response_time": proxy.response_time,
                "last_used": proxy.last_used
            })
        
        return details
    
    def reset_proxy_statistics(self):
        """Reset all proxy statistics"""
        for proxy in self.proxies:
            proxy.success_count = 0
            proxy.failure_count = 0
            proxy.response_time = 0
            proxy.last_used = 0
            proxy.is_working = True
        
        self.working_proxies = self.proxies.copy()
        logger.info("Proxy statistics reset")
    
    def remove_failed_proxies(self):
        """Remove permanently failed proxies"""
        before_count = len(self.proxies)
        self.proxies = [p for p in self.proxies if p.failure_count < self.max_failures * 2]
        self.working_proxies = [p for p in self.working_proxies if p in self.proxies]
        
        removed_count = before_count - len(self.proxies)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} failed proxies")
    
    async def test_all_proxies(self) -> Dict:
        """Test all proxies and return detailed results"""
        logger.info("Testing all proxies...")
        
        await self._perform_health_check()
        
        results = {
            "total_tested": len(self.proxies),
            "working_count": len(self.working_proxies),
            "failed_count": len(self.proxies) - len(self.working_proxies),
            "proxy_details": self.get_proxy_details()
        }
        
        return results

# Example usage and testing
async def test_proxy_manager():
    """Test the proxy manager"""
    manager = ProxyManager()
    
    # Add some test proxies (these are examples, not real proxies)
    test_proxies = [
        "http://proxy1.example.com:8080",
        "http://user:pass@proxy2.example.com:3128",
        "socks5://proxy3.example.com:1080"
    ]
    
    for proxy_url in test_proxies:
        proxy_info = manager._parse_proxy_string(proxy_url)
        if proxy_info:
            manager.proxies.append(proxy_info)
    
    # Enable proxy manager
    manager.enabled = True
    
    print("=== Proxy Manager Test ===")
    print(f"Loaded {len(manager.proxies)} test proxies")
    
    # Test proxy selection
    for i in range(5):
        proxy = await manager.get_proxy()
        print(f"Selected proxy {i+1}: {proxy}")
    
    # Test health check
    print("\nTesting proxy health...")
    results = await manager.test_all_proxies()
    print(f"Test results: {results}")
    
    # Show statistics
    stats = manager.get_proxy_statistics()
    print(f"\nProxy statistics: {stats}")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_proxy_manager())