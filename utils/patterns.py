from typing import Dict, List, Pattern
import re

class SearchPatterns:
    """Centralized search and extraction patterns"""
    
    def __init__(self):
        self.validation_patterns = self._init_validation_patterns()
        self.search_patterns = self._init_search_patterns()
        self.extraction_patterns = self._init_extraction_patterns()
    
    def _init_validation_patterns(self) -> Dict[str, Pattern]:
        """Initialize validation regex patterns"""
        return {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone_saudi': re.compile(r'(?:\+966|966|0)?(?:5[0-9])\d{7}\b'),
            'phone_uae': re.compile(r'(?:\+971|971|0)?(?:5[0-9])\d{7}\b'),
            'phone_international': re.compile(r'\+?[1-9]\d{1,14}\b'),
            # ...other patterns...
        }

    # Move pattern-related methods here
