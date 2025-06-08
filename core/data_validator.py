#!/usr/bin/env python3
"""
Advanced Data Validation System
File Location: core/data_validator.py
Comprehensive validation and quality assessment for OSINT intelligence data
"""

import re
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

# Import validation utilities
from utils.validation_rules import ValidationRules, ValidationResult

logger = logging.getLogger(__name__)

@dataclass
class DataQualityReport:
    """Comprehensive data quality assessment report"""
    total_items: int
    valid_items: int
    invalid_items: int
    overall_quality_score: float
    confidence_distribution: Dict[str, int]
    validation_summary: Dict[str, Any]
    quality_issues: List[str]
    recommendations: List[str]
    data_completeness: float
    source_reliability: Dict[str, float]
    temporal_analysis: Dict[str, Any]
    duplicate_analysis: Dict[str, Any]
    geographic_distribution: Dict[str, int]
    processing_time: float
    timestamp: datetime

@dataclass
class ValidationMetrics:
    """Validation metrics for monitoring"""
    validation_rate: float
    average_confidence: float
    high_confidence_rate: float
    error_rate: float
    most_common_errors: List[Tuple[str, int]]
    validation_time_avg: float
    improvement_suggestions: List[str]

class DataValidator:
    """Advanced data validation and quality assessment system"""
    
    def __init__(self):
        self.validation_rules = ValidationRules()
        
        # Quality thresholds
        self.quality_thresholds = {
            'excellent': 0.9,
            'good': 0.7,
            'acceptable': 0.5,
            'poor': 0.3
        }
        
        # Validation cache for performance
        self.validation_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Statistics tracking
        self.validation_stats = {
            'total_validations': 0,
            'total_errors': 0,
            'validation_times': [],
            'confidence_scores': [],
            'data_types_validated': defaultdict(int)
        }
        
        logger.info("Advanced data validator initialized")
    
    async def comprehensive_validation(self, intelligence_data: List[Dict[str, Any]]) -> DataQualityReport:
        """
        Perform comprehensive validation of intelligence data
        """
        start_time = datetime.now()
        logger.info(f"Starting comprehensive validation of {len(intelligence_data)} items")
        
        if not intelligence_data:
            return self._create_empty_report(start_time)
        
        # Initialize tracking variables
        validation_results = []
        quality_issues = []
        source_reliability = defaultdict(list)
        geographic_distribution = defaultdict(int)
        data_completeness_scores = []
        
        # Validate each data item
        for item in intelligence_data:
            try:
                result = await self._validate_intelligence_item(item)
                validation_results.append(result)
                
                # Track source reliability
                source_method = item.get('source_method', 'unknown')
                source_reliability[source_method].append(result.confidence)
                
                # Track geographic distribution
                location = item.get('geographic_location')
                if location:
                    geographic_distribution[location] += 1
                
                # Calculate completeness for this item
                completeness = self._calculate_item_completeness(item)
                data_completeness_scores.append(completeness)
                
            except Exception as e:
                logger.error(f"Validation error for item: {e}")
                quality_issues.append(f"Validation error: {str(e)}")
                continue
        
        # Calculate overall metrics
        total_items = len(intelligence_data)
        valid_items = sum(1 for r in validation_results if r.is_valid)
        invalid_items = total_items - valid_items
        
        # Overall quality score
        overall_quality = self._calculate_overall_quality_score(validation_results)
        
        # Confidence distribution
        confidence_dist = self._analyze_confidence_distribution(validation_results)
        
        # Validation summary
        validation_summary = self._create_validation_summary(validation_results)
        
        # Data completeness
        avg_completeness = statistics.mean(data_completeness_scores) if data_completeness_scores else 0.0
        
        # Source reliability analysis
        source_reliability_scores = {}
        for source, scores in source_reliability.items():
            if scores:
                source_reliability_scores[source] = statistics.mean(scores)
        
        # Temporal analysis
        temporal_analysis = self._analyze_temporal_patterns(intelligence_data)
        
        # Duplicate analysis
        duplicate_analysis = self._analyze_duplicates(intelligence_data)
        
        # Generate quality issues and recommendations
        quality_issues.extend(self._identify_quality_issues(validation_results, intelligence_data))
        recommendations = self._generate_recommendations(validation_results, quality_issues)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Create comprehensive report
        report = DataQualityReport(
            total_items=total_items,
            valid_items=valid_items,
            invalid_items=invalid_items,
            overall_quality_score=overall_quality,
            confidence_distribution=confidence_dist,
            validation_summary=validation_summary,
            quality_issues=quality_issues,
            recommendations=recommendations,
            data_completeness=avg_completeness,
            source_reliability=source_reliability_scores,
            temporal_analysis=temporal_analysis,
            duplicate_analysis=duplicate_analysis,
            geographic_distribution=dict(geographic_distribution),
            processing_time=processing_time,
            timestamp=datetime.now()
        )
        
        # Update statistics
        self._update_validation_statistics(validation_results, processing_time)
        
        logger.info(f"Validation completed: {valid_items}/{total_items} valid items, "
                   f"overall quality: {overall_quality:.2f}, time: {processing_time:.2f}s")
        
        return report
    
    async def _validate_intelligence_item(self, item: Dict[str, Any]) -> ValidationResult:
        """Validate a single intelligence item"""
        data_type = item.get('data_type', 'unknown')
        value = item.get('value', '')
        
        # Check cache first
        cache_key = f"{data_type}:{value}"
        if cache_key in self.validation_cache:
            cache_entry = self.validation_cache[cache_key]
            if datetime.now() - cache_entry['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cache_entry['result']
        
        # Perform validation based on data type
        result = None
        
        if data_type == 'email':
            result = self.validation_rules.validate_email(value)
        elif data_type == 'phone':
            country = self._detect_country_from_item(item)
            result = self.validation_rules.validate_phone(value, country)
        elif data_type in ['url', 'website']:
            result = self.validation_rules.validate_url(value)
        elif data_type == 'business_profile':
            result = self.validation_rules.validate_business_profile(item)
        elif data_type == 'person_profile':
            result = self.validation_rules.validate_person_profile(item)
        else:
            # Generic validation for unknown types
            result = self._generic_validation(item)
        
        # Cache the result
        self.validation_cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now()
        }
        
        return result
    
    def _detect_country_from_item(self, item: Dict[str, Any]) -> str:
        """Detect country from item context"""
        # Check geographic location
        location = item.get('geographic_location', '')
        if location:
            location_lower = location.lower()
            if any(term in location_lower for term in ['saudi', 'riyadh', 'jeddah']):
                return 'saudi'
            elif any(term in location_lower for term in ['uae', 'dubai', 'abu dhabi']):
                return 'uae'
            elif 'qatar' in location_lower:
                return 'qatar'
            elif 'kuwait' in location_lower:
                return 'kuwait'
        
        return 'international'
    
    def _generic_validation(self, item: Dict[str, Any]) -> ValidationResult:
        """Generic validation for unknown data types"""
        value = item.get('value', '')
        confidence = item.get('confidence', 0.5)
        
        # Basic validation checks
        errors = []
        details = {}
        
        # Check if value exists and is meaningful
        if not value or len(str(value).strip()) < 2:
            errors.append('Empty or too short value')
            details['value_length'] = len(str(value)) if value else 0
        else:
            details['value_length'] = len(str(value))
        
        # Check confidence score
        if confidence < 0.3:
            errors.append('Low confidence score')
        
        details['original_confidence'] = confidence
        
        # Check for required fields
        required_fields = ['data_type', 'source_method', 'timestamp']
        missing_fields = [field for field in required_fields if not item.get(field)]
        
        if missing_fields:
            errors.extend([f'Missing field: {field}' for field in missing_fields])
            details['missing_fields'] = missing_fields
        
        # Calculate validation confidence
        validation_confidence = confidence * (1 - len(errors) * 0.2)
        validation_confidence = max(validation_confidence, 0.0)
        
        is_valid = len(errors) == 0 and validation_confidence >= 0.3
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=validation_confidence,
            validation_type='generic',
            details=details,
            timestamp=datetime.now(),
            errors=errors
        )
    
    def _calculate_overall_quality_score(self, results: List[ValidationResult]) -> float:
        """Calculate overall quality score"""
        if not results:
            return 0.0
        
        # Weight different factors
        validity_weight = 0.4
        confidence_weight = 0.3
        completeness_weight = 0.2
        consistency_weight = 0.1
        
        # Validity score
        validity_score = sum(1 for r in results if r.is_valid) / len(results)
        
        # Average confidence
        confidence_score = sum(r.confidence for r in results) / len(results)
        
        # Completeness score (based on available details)
        completeness_scores = []
        for result in results:
            detail_count = len(result.details) if result.details else 0
            completeness_scores.append(min(detail_count / 5, 1.0))  # Normalize to max 5 details
        completeness_score = sum(completeness_scores) / len(completeness_scores)
        
        # Consistency score (low error rate)
        error_counts = [len(r.errors) for r in results]
        avg_errors = sum(error_counts) / len(error_counts)
        consistency_score = max(1.0 - avg_errors / 5, 0.0)  # Normalize to max 5 errors
        
        # Calculate weighted overall score
        overall_score = (
            validity_score * validity_weight +
            confidence_score * confidence_weight +
            completeness_score * completeness_weight +
            consistency_score * consistency_weight
        )
        
        return overall_score
    
    def _analyze_confidence_distribution(self, results: List[ValidationResult]) -> Dict[str, int]:
        """Analyze confidence score distribution"""
        distribution = {
            'high_confidence': 0,      # >= 0.8
            'medium_confidence': 0,    # 0.5 - 0.8
            'low_confidence': 0,       # 0.3 - 0.5
            'very_low_confidence': 0   # < 0.3
        }
        
        for result in results:
            confidence = result.confidence
            if confidence >= 0.8:
                distribution['high_confidence'] += 1
            elif confidence >= 0.5:
                distribution['medium_confidence'] += 1
            elif confidence >= 0.3:
                distribution['low_confidence'] += 1
            else:
                distribution['very_low_confidence'] += 1
        
        return distribution
    
    def _create_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Create detailed validation summary"""
        if not results:
            return {}
        
        # Group by validation type
        by_type = defaultdict(list)
        for result in results:
            by_type[result.validation_type].append(result)
        
        # Create summary for each type
        type_summaries = {}
        for validation_type, type_results in by_type.items():
            valid_count = sum(1 for r in type_results if r.is_valid)
            avg_confidence = sum(r.confidence for r in type_results) / len(type_results)
            
            type_summaries[validation_type] = {
                'total': len(type_results),
                'valid': valid_count,
                'invalid': len(type_results) - valid_count,
                'success_rate': valid_count / len(type_results),
                'average_confidence': avg_confidence,
                'common_errors': self._get_common_errors(type_results)
            }
        
        # Overall statistics
        total_valid = sum(1 for r in results if r.is_valid)
        overall_confidence = sum(r.confidence for r in results) / len(results)
        
        return {
            'by_type': type_summaries,
            'overall': {
                'total_items': len(results),
                'valid_items': total_valid,
                'success_rate': total_valid / len(results),
                'average_confidence': overall_confidence,
                'validation_types': len(by_type)
            }
        }
    
    def _get_common_errors(self, results: List[ValidationResult]) -> List[Tuple[str, int]]:
        """Get most common errors for a set of results"""
        error_counts = defaultdict(int)
        
        for result in results:
            for error in result.errors:
                error_counts[error] += 1
        
        # Return top 5 most common errors
        return sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _calculate_item_completeness(self, item: Dict[str, Any]) -> float:
        """Calculate completeness score for a single item"""
        # Define expected fields for different data types
        expected_fields = {
            'email': ['value', 'data_type', 'source_method', 'confidence'],
            'phone': ['value', 'data_type', 'source_method', 'confidence'],
            'business_profile': ['value', 'data_type', 'source_method', 'confidence', 'context'],
            'person_profile': ['value', 'data_type', 'source_method', 'confidence', 'context'],
            'default': ['value', 'data_type', 'source_method', 'confidence']
        }
        
        data_type = item.get('data_type', 'default')
        required_fields = expected_fields.get(data_type, expected_fields['default'])
        
        # Count present fields
        present_fields = sum(1 for field in required_fields if item.get(field))
        
        # Base completeness
        completeness = present_fields / len(required_fields)
        
        # Bonus for additional useful fields
        bonus_fields = ['timestamp', 'geographic_location', 'context', 'metadata']
        bonus_count = sum(1 for field in bonus_fields if item.get(field))
        bonus = min(bonus_count * 0.1, 0.2)  # Max 20% bonus
        
        return min(completeness + bonus, 1.0)
    
    def _analyze_temporal_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in the data"""
        timestamps = []
        
        for item in data:
            timestamp = item.get('timestamp')
            if timestamp:
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except:
                        continue
                elif isinstance(timestamp, datetime):
                    pass
                else:
                    continue
                
                timestamps.append(timestamp)
        
        if not timestamps:
            return {'total_items': 0, 'timespan': 0, 'items_with_timestamps': 0}
        
        # Calculate timespan
        min_time = min(timestamps)
        max_time = max(timestamps)
        timespan_hours = (max_time - min_time).total_seconds() / 3600
        
        # Analyze data freshness
        now = datetime.now()
        fresh_items = sum(1 for ts in timestamps if (now - ts).total_seconds() < 3600)  # Last hour
        recent_items = sum(1 for ts in timestamps if (now - ts).total_seconds() < 86400)  # Last day
        
        return {
            'total_items': len(data),
            'items_with_timestamps': len(timestamps),
            'timespan_hours': timespan_hours,
            'oldest_item': min_time.isoformat(),
            'newest_item': max_time.isoformat(),
            'fresh_items': fresh_items,
            'recent_items': recent_items,
            'average_age_hours': sum((now - ts).total_seconds() for ts in timestamps) / len(timestamps) / 3600
        }
    
    def _analyze_duplicates(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze duplicate data"""
        # Create signatures for duplicate detection
        signatures = defaultdict(list)
        
        for i, item in enumerate(data):
            # Create signature based on data type and value
            data_type = item.get('data_type', 'unknown')
            value = str(item.get('value', '')).lower().strip()
            signature = f"{data_type}:{value}"
            signatures[signature].append(i)
        
        # Find duplicates
        duplicates = {sig: indices for sig, indices in signatures.items() if len(indices) > 1}
        
        # Calculate duplicate statistics
        total_items = len(data)
        unique_items = len(signatures)
        duplicate_groups = len(duplicates)
        duplicate_items = sum(len(indices) - 1 for indices in duplicates.values())  # Don't count first occurrence
        
        return {
            'total_items': total_items,
            'unique_items': unique_items,
            'duplicate_groups': duplicate_groups,
            'duplicate_items': duplicate_items,
            'uniqueness_rate': unique_items / total_items if total_items > 0 else 0,
            'largest_duplicate_group': max(len(indices) for indices in duplicates.values()) if duplicates else 0
        }
    
    def _identify_quality_issues(self, results: List[ValidationResult], data: List[Dict[str, Any]]) -> List[str]:
        """Identify quality issues in the data"""
        issues = []
        
        if not results:
            return ['No validation results available']
        
        # Low overall validity
        validity_rate = sum(1 for r in results if r.is_valid) / len(results)
        if validity_rate < 0.5:
            issues.append(f"Low data validity rate: {validity_rate:.1%}")
        
        # Low confidence scores
        avg_confidence = sum(r.confidence for r in results) / len(results)
        if avg_confidence < 0.6:
            issues.append(f"Low average confidence: {avg_confidence:.2f}")
        
        # High error rate
        total_errors = sum(len(r.errors) for r in results)
        error_rate = total_errors / len(results)
        if error_rate > 1.0:
            issues.append(f"High error rate: {error_rate:.1f} errors per item")
        
        # Missing timestamps
        items_with_timestamps = sum(1 for item in data if item.get('timestamp'))
        if items_with_timestamps / len(data) < 0.8:
            issues.append("Many items missing timestamps")
        
        # Inconsistent data types
        data_types = set(item.get('data_type') for item in data)
        if 'unknown' in data_types or None in data_types:
            issues.append("Items with unknown or missing data types")
        
        # Missing source information
        items_with_source = sum(1 for item in data if item.get('source_method'))
        if items_with_source / len(data) < 0.9:
            issues.append("Items missing source method information")
        
        return issues
    
    def _generate_recommendations(self, results: List[ValidationResult], quality_issues: List[str]) -> List[str]:
        """Generate recommendations for improving data quality"""
        recommendations = []
        
        # Based on validation results
        if results:
            validity_rate = sum(1 for r in results if r.is_valid) / len(results)
            avg_confidence = sum(r.confidence for r in results) / len(results)
            
            if validity_rate < 0.7:
                recommendations.append("Improve data collection methods to increase validity rate")
            
            if avg_confidence < 0.7:
                recommendations.append("Enhance confidence scoring algorithms")
                recommendations.append("Use multiple sources for data verification")
            
            # Common error analysis
            all_errors = []
            for result in results:
                all_errors.extend(result.errors)
            
            error_counts = defaultdict(int)
            for error in all_errors:
                error_counts[error] += 1
            
            if error_counts:
                most_common_error = max(error_counts.items(), key=lambda x: x[1])
                recommendations.append(f"Address most common error: {most_common_error[0]}")
        
        # Based on quality issues
        for issue in quality_issues:
            if "timestamp" in issue.lower():
                recommendations.append("Ensure all data collection methods include timestamp information")
            elif "confidence" in issue.lower():
                recommendations.append("Review and calibrate confidence scoring mechanisms")
            elif "validity" in issue.lower():
                recommendations.append("Implement stricter data validation at collection time")
            elif "source" in issue.lower():
                recommendations.append("Mandate source tracking for all data collection")
        
        # General recommendations
        recommendations.extend([
            "Implement real-time validation during data collection",
            "Set up automated quality monitoring and alerts",
            "Regular review and update of validation rules",
            "Consider data enrichment for incomplete records"
        ])
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _create_empty_report(self, start_time: datetime) -> DataQualityReport:
        """Create empty report for no data case"""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return DataQualityReport(
            total_items=0,
            valid_items=0,
            invalid_items=0,
            overall_quality_score=0.0,
            confidence_distribution={},
            validation_summary={},
            quality_issues=['No data provided for validation'],
            recommendations=['Ensure data collection is working properly'],
            data_completeness=0.0,
            source_reliability={},
            temporal_analysis={},
            duplicate_analysis={},
            geographic_distribution={},
            processing_time=processing_time,
            timestamp=datetime.now()
        )
    
    def _update_validation_statistics(self, results: List[ValidationResult], processing_time: float):
        """Update internal validation statistics"""
        self.validation_stats['total_validations'] += len(results)
        self.validation_stats['total_errors'] += sum(len(r.errors) for r in results)
        self.validation_stats['validation_times'].append(processing_time)
        self.validation_stats['confidence_scores'].extend([r.confidence for r in results])
        
        for result in results:
            self.validation_stats['data_types_validated'][result.validation_type] += 1
    
    def get_validation_metrics(self) -> ValidationMetrics:
        """Get current validation metrics"""
        stats = self.validation_stats
        
        if stats['total_validations'] == 0:
            return ValidationMetrics(
                validation_rate=0.0,
                average_confidence=0.0,
                high_confidence_rate=0.0,
                error_rate=0.0,
                most_common_errors=[],
                validation_time_avg=0.0,
                improvement_suggestions=[]
            )
        
        # Calculate metrics
        validation_rate = 1.0  # Assuming all items get validated
        average_confidence = statistics.mean(stats['confidence_scores']) if stats['confidence_scores'] else 0.0
        
        high_confidence_count = sum(1 for score in stats['confidence_scores'] if score >= 0.8)
        high_confidence_rate = high_confidence_count / len(stats['confidence_scores']) if stats['confidence_scores'] else 0.0
        
        error_rate = stats['total_errors'] / stats['total_validations']
        validation_time_avg = statistics.mean(stats['validation_times']) if stats['validation_times'] else 0.0
        
        # Generate improvement suggestions
        suggestions = []
        if average_confidence < 0.7:
            suggestions.append("Improve data source quality to increase average confidence")
        if error_rate > 1.0:
            suggestions.append("Review validation rules to reduce error rate")
        if validation_time_avg > 1.0:
            suggestions.append("Optimize validation performance")
        
        return ValidationMetrics(
            validation_rate=validation_rate,
            average_confidence=average_confidence,
            high_confidence_rate=high_confidence_rate,
            error_rate=error_rate,
            most_common_errors=[],  # Would need error tracking
            validation_time_avg=validation_time_avg,
            improvement_suggestions=suggestions
        )
    
    def clear_validation_cache(self):
        """Clear validation cache"""
        self.validation_cache.clear()
        logger.info("Validation cache cleared")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache usage statistics"""
        return {
            'cache_size': len(self.validation_cache),
            'cache_ttl_seconds': self.cache_ttl,
            'cache_hit_rate': 'Not tracked',  # Would need hit/miss tracking
        }

# Example usage and testing
async def test_data_validator():
    """Test the data validator"""
    validator = DataValidator()
    
    # Sample intelligence data
    sample_data = [
        {
            'data_type': 'email',
            'value': 'john.doe@company.com',
            'confidence': 0.9,
            'source_method': 'website_extraction',
            'timestamp': datetime.now().isoformat(),
            'geographic_location': 'Saudi Arabia'
        },
        {
            'data_type': 'phone',
            'value': '+966501234567',
            'confidence': 0.8,
            'source_method': 'linkedin_extraction',
            'timestamp': datetime.now().isoformat(),
            'geographic_location': 'Saudi Arabia'
        },
        {
            'data_type': 'business_profile',
            'value': 'Tech Solutions LLC',
            'confidence': 0.7,
            'source_method': 'directory_search',
            'timestamp': datetime.now().isoformat(),
            'context': {
                'industry': 'Technology',
                'location': 'Riyadh',
                'website': 'https://techsolutions.com'
            }
        },
        {
            'data_type': 'email',
            'value': 'invalid-email',  # Invalid email
            'confidence': 0.3,
            'source_method': 'automated_extraction',
            'timestamp': datetime.now().isoformat()
        }
    ]
    
    print("=== Data Validator Test ===")
    
    # Perform comprehensive validation
    report = await validator.comprehensive_validation(sample_data)
    
    print(f"\nValidation Report:")
    print(f"Total Items: {report.total_items}")
    print(f"Valid Items: {report.valid_items}")
    print(f"Invalid Items: {report.invalid_items}")
    print(f"Overall Quality Score: {report.overall_quality_score:.2f}")
    print(f"Data Completeness: {report.data_completeness:.2f}")
    print(f"Processing Time: {report.processing_time:.2f}s")
    
    print(f"\nConfidence Distribution:")
    for level, count in report.confidence_distribution.items():
        print(f"  {level}: {count}")
    
    print(f"\nQuality Issues:")
    for issue in report.quality_issues[:3]:
        print(f"  • {issue}")
    
    print(f"\nRecommendations:")
    for rec in report.recommendations[:3]:
        print(f"  • {rec}")
    
    # Get validation metrics
    metrics = validator.get_validation_metrics()
    print(f"\nValidation Metrics:")
    print(f"Average Confidence: {metrics.average_confidence:.2f}")
    print(f"High Confidence Rate: {metrics.high_confidence_rate:.1%}")
    print(f"Error Rate: {metrics.error_rate:.2f}")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_data_validator())