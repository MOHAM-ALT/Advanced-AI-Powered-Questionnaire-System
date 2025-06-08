#!/usr/bin/env python3
"""
Advanced Database Management System
File Location: core/database_manager.py
Comprehensive database operations for OSINT intelligence storage and retrieval
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from contextlib import contextmanager
import threading
import hashlib

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Advanced database management for OSINT intelligence"""
    
    def __init__(self, db_path: Union[str, Path]):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize database
        self.init_database()
        
        # Performance settings
        self._setup_performance_optimizations()
        
        logger.info(f"Database manager initialized: {self.db_path}")
    
    def _setup_performance_optimizations(self):
        """Setup database performance optimizations"""
        with self.get_connection() as conn:
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            
            # Optimize for speed
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys=ON")
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper context management"""
        with self._lock:
            conn = sqlite3.connect(
                self.db_path,
                timeout=30.0,
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
    
    def init_database(self):
        """Initialize database with comprehensive schema"""
        with self.get_connection() as conn:
            # Investigations table - main investigation records
            conn.execute("""
                CREATE TABLE IF NOT EXISTS investigations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    context TEXT NOT NULL,
                    strategy TEXT,
                    status TEXT DEFAULT 'active',
                    created_date TEXT NOT NULL,
                    completed_date TEXT,
                    total_results INTEGER DEFAULT 0,
                    confidence_score REAL DEFAULT 0.0,
                    geographic_focus TEXT,
                    target_type TEXT,
                    urgency_level TEXT,
                    search_depth TEXT,
                    user_notes TEXT,
                    tags TEXT,
                    UNIQUE(query, context, created_date)
                )
            """)
            
            # Intelligence results table - individual intelligence items
            conn.execute("""
                CREATE TABLE IF NOT EXISTS intelligence_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    investigation_id INTEGER NOT NULL,
                    data_type TEXT NOT NULL,
                    value TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    relevance_score REAL DEFAULT 0.0,
                    source_method TEXT NOT NULL,
                    source_url TEXT,
                    context TEXT,
                    timestamp TEXT NOT NULL,
                    validation_status TEXT DEFAULT 'pending',
                    geographic_location TEXT,
                    enrichment_data TEXT,
                    metadata TEXT,
                    hash_signature TEXT,
                    FOREIGN KEY (investigation_id) REFERENCES investigations (id) ON DELETE CASCADE
                )
            """)
            
            # Contact information table - extracted contacts
            conn.execute("""
                CREATE TABLE IF NOT EXISTS contact_information (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    investigation_id INTEGER NOT NULL,
                    intelligence_result_id INTEGER,
                    contact_type TEXT NOT NULL,
                    contact_value TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    validation_status TEXT DEFAULT 'pending',
                    source_context TEXT,
                    extracted_date TEXT NOT NULL,
                    verified_date TEXT,
                    notes TEXT,
                    FOREIGN KEY (investigation_id) REFERENCES investigations (id) ON DELETE CASCADE,
                    FOREIGN KEY (intelligence_result_id) REFERENCES intelligence_results (id) ON DELETE SET NULL,
                    UNIQUE(contact_type, contact_value, investigation_id)
                )
            """)
            
            # Analysis results table - AI analysis outcomes
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    investigation_id INTEGER NOT NULL,
                    analysis_type TEXT NOT NULL,
                    analysis_data TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    processing_time REAL,
                    created_date TEXT NOT NULL,
                    key_insights TEXT,
                    recommendations TEXT,
                    metadata TEXT,
                    FOREIGN KEY (investigation_id) REFERENCES investigations (id) ON DELETE CASCADE
                )
            """)
            
            # Search queries table - track search performance
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    investigation_id INTEGER,
                    query_text TEXT NOT NULL,
                    search_engine TEXT NOT NULL,
                    results_count INTEGER DEFAULT 0,
                    execution_time REAL,
                    timestamp TEXT NOT NULL,
                    success BOOLEAN DEFAULT 1,
                    error_message TEXT,
                    FOREIGN KEY (investigation_id) REFERENCES investigations (id) ON DELETE SET NULL
                )
            """)
            
            # System logs table - audit trail
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    module TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    investigation_id INTEGER,
                    user_id TEXT,
                    additional_data TEXT,
                    FOREIGN KEY (investigation_id) REFERENCES investigations (id) ON DELETE SET NULL
                )
            """)
            
            # Create indexes for performance
            self._create_indexes(conn)
            
            conn.commit()
            logger.info("Database schema initialized successfully")
    
    def _create_indexes(self, conn):
        """Create database indexes for performance optimization"""
        indexes = [
            # Primary search indexes
            "CREATE INDEX IF NOT EXISTS idx_investigations_status ON investigations(status)",
            "CREATE INDEX IF NOT EXISTS idx_investigations_context ON investigations(context)",
            "CREATE INDEX IF NOT EXISTS idx_investigations_date ON investigations(created_date)",
            "CREATE INDEX IF NOT EXISTS idx_investigations_query ON investigations(query)",
            
            # Intelligence results indexes
            "CREATE INDEX IF NOT EXISTS idx_intelligence_investigation ON intelligence_results(investigation_id)",
            "CREATE INDEX IF NOT EXISTS idx_intelligence_type ON intelligence_results(data_type)",
            "CREATE INDEX IF NOT EXISTS idx_intelligence_confidence ON intelligence_results(confidence)",
            "CREATE INDEX IF NOT EXISTS idx_intelligence_source ON intelligence_results(source_method)",
            "CREATE INDEX IF NOT EXISTS idx_intelligence_hash ON intelligence_results(hash_signature)",
            
            # Contact information indexes
            "CREATE INDEX IF NOT EXISTS idx_contacts_investigation ON contact_information(investigation_id)",
            "CREATE INDEX IF NOT EXISTS idx_contacts_type ON contact_information(contact_type)",
            "CREATE INDEX IF NOT EXISTS idx_contacts_validation ON contact_information(validation_status)",
            
            # Analysis results indexes
            "CREATE INDEX IF NOT EXISTS idx_analysis_investigation ON analysis_results(investigation_id)",
            "CREATE INDEX IF NOT EXISTS idx_analysis_type ON analysis_results(analysis_type)",
            "CREATE INDEX IF NOT EXISTS idx_analysis_date ON analysis_results(created_date)",
            
            # Search queries indexes
            "CREATE INDEX IF NOT EXISTS idx_queries_investigation ON search_queries(investigation_id)",
            "CREATE INDEX IF NOT EXISTS idx_queries_engine ON search_queries(search_engine)",
            "CREATE INDEX IF NOT EXISTS idx_queries_timestamp ON search_queries(timestamp)",
            
            # System logs indexes
            "CREATE INDEX IF NOT EXISTS idx_logs_level ON system_logs(level)",
            "CREATE INDEX IF NOT EXISTS idx_logs_module ON system_logs(module)",
            "CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON system_logs(timestamp)"
        ]
        
        for index_sql in indexes:
            try:
                conn.execute(index_sql)
            except Exception as e:
                logger.warning(f"Index creation warning: {e}")
    
    def create_investigation(self, query: str, context: str, strategy: Dict[str, Any]) -> int:
        """Create new investigation record"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO investigations 
                (query, context, strategy, created_date, geographic_focus, target_type, urgency_level, search_depth)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                query,
                context,
                json.dumps(strategy),
                datetime.now().isoformat(),
                strategy.get('geographic_focus', ''),
                strategy.get('target_type', ''),
                strategy.get('urgency_level', 'standard'),
                strategy.get('search_depth', 'standard')
            ))
            
            investigation_id = cursor.lastrowid
            conn.commit()
            
            # Log investigation creation
            self._log_system_event(
                level='INFO',
                module='database_manager',
                message=f'Investigation created: {investigation_id}',
                investigation_id=investigation_id
            )
            
            logger.info(f"Investigation created with ID: {investigation_id}")
            return investigation_id
    
    def save_intelligence_result(self, investigation_id: int, result: Any) -> int:
        """Save intelligence result to database"""
        # Generate hash signature for deduplication
        result_hash = self._generate_result_hash(result)
        
        with self.get_connection() as conn:
            # Check for existing result
            existing = conn.execute(
                "SELECT id FROM intelligence_results WHERE hash_signature = ? AND investigation_id = ?",
                (result_hash, investigation_id)
            ).fetchone()
            
            if existing:
                logger.debug(f"Duplicate result skipped: {result_hash}")
                return existing['id']
            
            # Extract result data
            data_type = getattr(result, 'data_type', 'unknown')
            value = getattr(result, 'value', str(result))
            confidence = getattr(result, 'confidence', 0.5)
            relevance_score = getattr(result, 'relevance_score', 0.0)
            source_method = getattr(result, 'source_method', 'unknown')
            source_url = getattr(result, 'source_url', '')
            context = getattr(result, 'context', {})
            timestamp = getattr(result, 'timestamp', datetime.now())
            validation_status = getattr(result, 'validation_status', 'pending')
            geographic_location = getattr(result, 'geographic_location', None)
            enrichment_data = getattr(result, 'enrichment_data', {})
            metadata = getattr(result, 'metadata', {})
            
            cursor = conn.execute("""
                INSERT INTO intelligence_results 
                (investigation_id, data_type, value, confidence, relevance_score, source_method, 
                 source_url, context, timestamp, validation_status, geographic_location, 
                 enrichment_data, metadata, hash_signature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                investigation_id,
                data_type,
                value,
                confidence,
                relevance_score,
                source_method,
                source_url,
                json.dumps(context) if isinstance(context, dict) else str(context),
                timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp),
                validation_status,
                geographic_location,
                json.dumps(enrichment_data) if isinstance(enrichment_data, dict) else str(enrichment_data),
                json.dumps(metadata) if isinstance(metadata, dict) else str(metadata),
                result_hash
            ))
            
            result_id = cursor.lastrowid
            conn.commit()
            
            logger.debug(f"Intelligence result saved: {result_id}")
            return result_id
    
    def save_contact_information(self, investigation_id: int, contact_data: Dict[str, Any]) -> int:
        """Save contact information"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO contact_information 
                (investigation_id, contact_type, contact_value, confidence, 
                 validation_status, source_context, extracted_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                investigation_id,
                contact_data.get('type', 'unknown'),
                contact_data.get('value', ''),
                contact_data.get('confidence', 0.5),
                contact_data.get('validation_status', 'pending'),
                json.dumps(contact_data.get('context', {})),
                datetime.now().isoformat()
            ))
            
            contact_id = cursor.lastrowid
            conn.commit()
            
            return contact_id
    
    def save_analysis_result(self, investigation_id: int, analysis: Dict[str, Any]) -> int:
        """Save AI analysis result"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO analysis_results 
                (investigation_id, analysis_type, analysis_data, confidence_score, 
                 processing_time, created_date, key_insights, recommendations, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                investigation_id,
                analysis.get('analysis_type', 'comprehensive'),
                json.dumps(analysis.get('data', {})),
                analysis.get('confidence_score', 0.0),
                analysis.get('processing_time', 0.0),
                datetime.now().isoformat(),
                json.dumps(analysis.get('key_insights', [])),
                json.dumps(analysis.get('recommendations', [])),
                json.dumps(analysis.get('metadata', {}))
            ))
            
            analysis_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Analysis result saved: {analysis_id}")
            return analysis_id
    
    def complete_investigation(self, investigation_id: int, total_results: int, confidence_score: float = 0.0) -> bool:
        """Mark investigation as completed"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                UPDATE investigations 
                SET status = 'completed', 
                    completed_date = ?, 
                    total_results = ?,
                    confidence_score = ?
                WHERE id = ?
            """, (
                datetime.now().isoformat(),
                total_results,
                confidence_score,
                investigation_id
            ))
            
            conn.commit()
            updated = cursor.rowcount > 0
            
            if updated:
                self._log_system_event(
                    level='INFO',
                    module='database_manager',
                    message=f'Investigation completed: {investigation_id} ({total_results} results)',
                    investigation_id=investigation_id
                )
                logger.info(f"Investigation {investigation_id} marked as completed")
            
            return updated
    
    def get_investigation_history(self, limit: int = 20, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get investigation history with optional filtering"""
        with self.get_connection() as conn:
            query = """
                SELECT i.*, 
                       COUNT(ir.id) as results_count,
                       COUNT(ci.id) as contacts_count,
                       COUNT(ar.id) as analysis_count
                FROM investigations i
                LEFT JOIN intelligence_results ir ON i.id = ir.investigation_id
                LEFT JOIN contact_information ci ON i.id = ci.investigation_id
                LEFT JOIN analysis_results ar ON i.id = ar.investigation_id
            """
            
            params = []
            if status_filter:
                query += " WHERE i.status = ?"
                params.append(status_filter)
            
            query += """
                GROUP BY i.id
                ORDER BY i.created_date DESC 
                LIMIT ?
            """
            params.append(limit)
            
            cursor = conn.execute(query, params)
            investigations = [dict(row) for row in cursor.fetchall()]
            
            # Parse strategy JSON
            for inv in investigations:
                try:
                    inv['strategy'] = json.loads(inv['strategy']) if inv['strategy'] else {}
                except (json.JSONDecodeError, TypeError):
                    inv['strategy'] = {}
            
            return investigations
    
    def get_investigation_details(self, investigation_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed investigation information"""
        with self.get_connection() as conn:
            # Get investigation basic info
            inv_cursor = conn.execute(
                "SELECT * FROM investigations WHERE id = ?", 
                (investigation_id,)
            )
            investigation = inv_cursor.fetchone()
            
            if not investigation:
                return None
            
            investigation = dict(investigation)
            
            # Parse strategy
            try:
                investigation['strategy'] = json.loads(investigation['strategy']) if investigation['strategy'] else {}
            except (json.JSONDecodeError, TypeError):
                investigation['strategy'] = {}
            
            # Get intelligence results
            results_cursor = conn.execute("""
                SELECT * FROM intelligence_results 
                WHERE investigation_id = ? 
                ORDER BY confidence DESC, relevance_score DESC
                LIMIT 100
            """, (investigation_id,))
            investigation['results'] = [dict(row) for row in results_cursor.fetchall()]
            
            # Get contact information
            contacts_cursor = conn.execute("""
                SELECT * FROM contact_information 
                WHERE investigation_id = ? 
                ORDER BY confidence DESC
            """, (investigation_id,))
            investigation['contacts'] = [dict(row) for row in contacts_cursor.fetchall()]
            
            # Get analysis results
            analysis_cursor = conn.execute("""
                SELECT * FROM analysis_results 
                WHERE investigation_id = ? 
                ORDER BY created_date DESC
            """, (investigation_id,))
            investigation['analysis'] = [dict(row) for row in analysis_cursor.fetchall()]
            
            return investigation
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        with self.get_connection() as conn:
            stats = {}
            
            # Basic counts
            stats["Total Investigations"] = conn.execute("SELECT COUNT(*) FROM investigations").fetchone()[0]
            stats["Completed Investigations"] = conn.execute("SELECT COUNT(*) FROM investigations WHERE status = 'completed'").fetchone()[0]
            stats["Active Investigations"] = conn.execute("SELECT COUNT(*) FROM investigations WHERE status = 'active'").fetchone()[0]
            stats["Total Intelligence Items"] = conn.execute("SELECT COUNT(*) FROM intelligence_results").fetchone()[0]
            stats["Total Contacts"] = conn.execute("SELECT COUNT(*) FROM contact_information").fetchone()[0]
            stats["Total Analysis Results"] = conn.execute("SELECT COUNT(*) FROM analysis_results").fetchone()[0]
            
            # Recent activity
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            stats["Investigations This Week"] = conn.execute(
                "SELECT COUNT(*) FROM investigations WHERE created_date > ?", 
                (week_ago,)
            ).fetchone()[0]
            
            # Data quality metrics
            high_confidence_results = conn.execute(
                "SELECT COUNT(*) FROM intelligence_results WHERE confidence >= 0.8"
            ).fetchone()[0]
            stats["High Confidence Results"] = high_confidence_results
            
            verified_contacts = conn.execute(
                "SELECT COUNT(*) FROM contact_information WHERE validation_status = 'verified'"
            ).fetchone()[0]
            stats["Verified Contacts"] = verified_contacts
            
            # Top data types
            top_data_types = conn.execute("""
                SELECT data_type, COUNT(*) as count 
                FROM intelligence_results 
                GROUP BY data_type 
                ORDER BY count DESC 
                LIMIT 5
            """).fetchall()
            stats["Top Data Types"] = [{"type": row[0], "count": row[1]} for row in top_data_types]
            
            # Top source methods
            top_sources = conn.execute("""
                SELECT source_method, COUNT(*) as count 
                FROM intelligence_results 
                GROUP BY source_method 
                ORDER BY count DESC 
                LIMIT 5
            """).fetchall()
            stats["Top Source Methods"] = [{"source": row[0], "count": row[1]} for row in top_sources]
            
            # Database size
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
            stats["Database Size (MB)"] = round(db_size / (1024 * 1024), 2)
            
            return stats
    
    def search_investigations(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search investigations by query text"""
        with self.get_connection() as conn:
            search_pattern = f"%{search_term}%"
            cursor = conn.execute("""
                SELECT i.*, COUNT(ir.id) as results_count
                FROM investigations i
                LEFT JOIN intelligence_results ir ON i.id = ir.investigation_id
                WHERE i.query LIKE ? OR i.context LIKE ? OR i.tags LIKE ?
                GROUP BY i.id
                ORDER BY i.created_date DESC
                LIMIT ?
            """, (search_pattern, search_pattern, search_pattern, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_results_by_type(self, investigation_id: int, data_type: str) -> List[Dict[str, Any]]:
        """Get intelligence results filtered by data type"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM intelligence_results 
                WHERE investigation_id = ? AND data_type = ?
                ORDER BY confidence DESC, relevance_score DESC
            """, (investigation_id, data_type))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_high_confidence_results(self, investigation_id: int, min_confidence: float = 0.8) -> List[Dict[str, Any]]:
        """Get high confidence results for an investigation"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM intelligence_results 
                WHERE investigation_id = ? AND confidence >= ?
                ORDER BY confidence DESC, relevance_score DESC
            """, (investigation_id, min_confidence))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_result_validation(self, result_id: int, validation_status: str, notes: Optional[str] = None) -> bool:
        """Update validation status of an intelligence result"""
        with self.get_connection() as conn:
            params = [validation_status, result_id]
            query = "UPDATE intelligence_results SET validation_status = ?"
            
            if notes:
                query += ", metadata = json_set(COALESCE(metadata, '{}'), '$.validation_notes', ?)"
                params.insert(-1, notes)
            
            query += " WHERE id = ?"
            
            cursor = conn.execute(query, params)
            conn.commit()
            
            return cursor.rowcount > 0
    
    def add_investigation_tags(self, investigation_id: int, tags: List[str]) -> bool:
        """Add tags to an investigation"""
        with self.get_connection() as conn:
            # Get existing tags
            current_tags = conn.execute(
                "SELECT tags FROM investigations WHERE id = ?", 
                (investigation_id,)
            ).fetchone()
            
            existing_tags = []
            if current_tags and current_tags[0]:
                try:
                    existing_tags = json.loads(current_tags[0])
                except json.JSONDecodeError:
                    existing_tags = []
            
            # Merge tags
            all_tags = list(set(existing_tags + tags))
            
            cursor = conn.execute("""
                UPDATE investigations 
                SET tags = ? 
                WHERE id = ?
            """, (json.dumps(all_tags), investigation_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def export_investigation(self, investigation_id: int, format: str = 'json') -> str:
        """Export investigation data in specified format"""
        investigation = self.get_investigation_details(investigation_id)
        if not investigation:
            raise ValueError(f"Investigation {investigation_id} not found")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        query_safe = investigation['query'].replace(' ', '_').replace('/', '_')[:50]
        
        if format == 'json':
            return self._export_to_json(investigation, query_safe, timestamp)
        elif format == 'csv':
            return self._export_to_csv(investigation, query_safe, timestamp)
        elif format == 'html':
            return self._export_to_html(investigation, query_safe, timestamp)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_to_json(self, investigation: Dict, query_safe: str, timestamp: str) -> str:
        """Export investigation to JSON"""
        filename = f"investigation_{investigation['id']}_{query_safe}_{timestamp}.json"
        exports_dir = Path("data/exports")
        exports_dir.mkdir(exist_ok=True)
        
        # Prepare export data
        export_data = {
            'investigation_summary': {
                'id': investigation['id'],
                'query': investigation['query'],
                'context': investigation['context'],
                'status': investigation['status'],
                'created_date': investigation['created_date'],
                'completed_date': investigation['completed_date'],
                'total_results': investigation['total_results'],
                'confidence_score': investigation['confidence_score']
            },
            'strategy': investigation['strategy'],
            'intelligence_results': investigation['results'],
            'contact_information': investigation['contacts'],
            'analysis_results': investigation['analysis'],
            'export_metadata': {
                'exported_date': datetime.now().isoformat(),
                'export_format': 'json',
                'results_count': len(investigation['results']),
                'contacts_count': len(investigation['contacts'])
            }
        }
        
        with open(exports_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Investigation exported to JSON: {filename}")
        return str(exports_dir / filename)
    
    def _export_to_csv(self, investigation: Dict, query_safe: str, timestamp: str) -> str:
        """Export investigation to CSV"""
        import csv
        
        filename = f"investigation_{investigation['id']}_{query_safe}_{timestamp}.csv"
        exports_dir = Path("data/exports")
        exports_dir.mkdir(exist_ok=True)
        
        with open(exports_dir / filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write investigation header
            writer.writerow(['Investigation Summary'])
            writer.writerow(['ID', investigation['id']])
            writer.writerow(['Query', investigation['query']])
            writer.writerow(['Context', investigation['context']])
            writer.writerow(['Status', investigation['status']])
            writer.writerow(['Created', investigation['created_date']])
            writer.writerow(['Total Results', investigation['total_results']])
            writer.writerow([])
            
            # Write intelligence results
            if investigation['results']:
                writer.writerow(['Intelligence Results'])
                writer.writerow([
                    'Data Type', 'Value', 'Confidence', 'Relevance Score',
                    'Source Method', 'Source URL', 'Timestamp', 'Validation Status'
                ])
                
                for result in investigation['results']:
                    writer.writerow([
                        result['data_type'],
                        result['value'],
                        result['confidence'],
                        result['relevance_score'],
                        result['source_method'],
                        result['source_url'],
                        result['timestamp'],
                        result['validation_status']
                    ])
                
                writer.writerow([])
            
            # Write contact information
            if investigation['contacts']:
                writer.writerow(['Contact Information'])
                writer.writerow([
                    'Type', 'Value', 'Confidence', 'Validation Status', 'Extracted Date'
                ])
                
                for contact in investigation['contacts']:
                    writer.writerow([
                        contact['contact_type'],
                        contact['contact_value'],
                        contact['confidence'],
                        contact['validation_status'],
                        contact['extracted_date']
                    ])
        
        logger.info(f"Investigation exported to CSV: {filename}")
        return str(exports_dir / filename)
    
    def _export_to_html(self, investigation: Dict, query_safe: str, timestamp: str) -> str:
        """Export investigation to HTML report"""
        filename = f"investigation_{investigation['id']}_{query_safe}_{timestamp}.html"
        exports_dir = Path("data/exports")
        exports_dir.mkdir(exist_ok=True)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Investigation Report - {investigation['query']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .result {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-left: 3px solid #007bff; }}
        .high-confidence {{ border-left-color: #28a745; }}
        .medium-confidence {{ border-left-color: #ffc107; }}
        .low-confidence {{ border-left-color: #dc3545; }}
        .contact {{ background: #e8f5e8; border-left-color: #28a745; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .metadata {{ font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>OSINT Investigation Report</h1>
        <p>Investigation ID: {investigation['id']}</p>
        <p>Query: {investigation['query']}</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="section">
        <h2>Investigation Summary</h2>
        <table>
            <tr><th>Context</th><td>{investigation['context']}</td></tr>
            <tr><th>Status</th><td>{investigation['status']}</td></tr>
            <tr><th>Created Date</th><td>{investigation['created_date']}</td></tr>
            <tr><th>Completed Date</th><td>{investigation['completed_date'] or 'Not completed'}</td></tr>
            <tr><th>Total Results</th><td>{investigation['total_results']}</td></tr>
            <tr><th>Confidence Score</th><td>{investigation['confidence_score']:.2f}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Intelligence Results ({len(investigation['results'])} items)</h2>
"""
        
        # Add intelligence results
        for result in investigation['results'][:50]:  # Limit to first 50
            confidence_class = 'high-confidence' if result['confidence'] >= 0.8 else 'medium-confidence' if result['confidence'] >= 0.5 else 'low-confidence'
            
            html_content += f"""
        <div class="result {confidence_class}">
            <h4>{result['data_type'].replace('_', ' ').title()}</h4>
            <p><strong>Value:</strong> {result['value']}</p>
            <p><strong>Source:</strong> {result['source_method']}</p>
            <p><strong>Confidence:</strong> {result['confidence']:.2f} | <strong>Relevance:</strong> {result['relevance_score']:.2f}</p>
            <p class="metadata">URL: <a href="{result['source_url']}" target="_blank">{result['source_url']}</a></p>
            <p class="metadata">Timestamp: {result['timestamp']} | Status: {result['validation_status']}</p>
        </div>
"""
        
        html_content += """
    </div>
    
    <div class="section">
        <h2>Contact Information</h2>
"""
        
        # Add contact information
        for contact in investigation['contacts']:
            html_content += f"""
        <div class="result contact">
            <h4>{contact['contact_type'].title()}</h4>
            <p><strong>Value:</strong> {contact['contact_value']}</p>
            <p><strong>Confidence:</strong> {contact['confidence']:.2f}</p>
            <p class="metadata">Status: {contact['validation_status']} | Extracted: {contact['extracted_date']}</p>
        </div>
"""
        
        html_content += """
    </div>
    
    <div class="section">
        <h2>Export Information</h2>
        <p><strong>Export Date:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        <p><strong>Results Count:</strong> """ + str(len(investigation['results'])) + """</p>
        <p><strong>Contacts Count:</strong> """ + str(len(investigation['contacts'])) + """</p>
        <p><strong>Database:</strong> """ + str(self.db_path) + """</p>
    </div>
</body>
</html>
"""
        
        with open(exports_dir / filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Investigation exported to HTML: {filename}")
        return str(exports_dir / filename)
    
    def export_all_investigations(self, format: str = 'json') -> str:
        """Export all investigations"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"all_investigations_{timestamp}.{format}"
        exports_dir = Path("data/exports")
        exports_dir.mkdir(exist_ok=True)
        
        with self.get_connection() as conn:
            if format == 'json':
                # Get all investigations with their data
                investigations = []
                cursor = conn.execute("SELECT id FROM investigations ORDER BY created_date DESC")
                
                for row in cursor.fetchall():
                    inv_data = self.get_investigation_details(row[0])
                    if inv_data:
                        investigations.append(inv_data)
                
                export_data = {
                    'export_metadata': {
                        'exported_date': datetime.now().isoformat(),
                        'total_investigations': len(investigations),
                        'export_type': 'all_investigations'
                    },
                    'investigations': investigations
                }
                
                with open(exports_dir / filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            elif format == 'csv':
                import csv
                with open(exports_dir / filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Write header
                    writer.writerow([
                        'ID', 'Query', 'Context', 'Status', 'Created Date', 
                        'Completed Date', 'Total Results', 'Confidence Score'
                    ])
                    
                    # Write investigation data
                    cursor = conn.execute("""
                        SELECT id, query, context, status, created_date, 
                               completed_date, total_results, confidence_score
                        FROM investigations 
                        ORDER BY created_date DESC
                    """)
                    
                    for row in cursor.fetchall():
                        writer.writerow(row)
        
        logger.info(f"All investigations exported to {format.upper()}: {filename}")
        return str(exports_dir / filename)
    
    def export_summary_report(self) -> str:
        """Export summary report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"summary_report_{timestamp}.html"
        exports_dir = Path("data/exports")
        exports_dir.mkdir(exist_ok=True)
        
        stats = self.get_database_statistics()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT System Summary Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 5px; border-left: 4px solid #007bff; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Advanced OSINT System - Summary Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Database: {self.db_path}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{stats['Total Investigations']}</div>
            <div>Total Investigations</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['Total Intelligence Items']}</div>
            <div>Intelligence Items</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['Total Contacts']}</div>
            <div>Contact Records</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['High Confidence Results']}</div>
            <div>High Confidence Results</div>
        </div>
    </div>
    
    <h2>Investigation Status</h2>
    <table>
        <tr><th>Status</th><th>Count</th></tr>
        <tr><td>Completed</td><td>{stats['Completed Investigations']}</td></tr>
        <tr><td>Active</td><td>{stats['Active Investigations']}</td></tr>
        <tr><td>This Week</td><td>{stats['Investigations This Week']}</td></tr>
    </table>
    
    <h2>Top Data Types</h2>
    <table>
        <tr><th>Data Type</th><th>Count</th></tr>
"""
        
        for item in stats['Top Data Types']:
            html_content += f"<tr><td>{item['type']}</td><td>{item['count']}</td></tr>"
        
        html_content += """
    </table>
    
    <h2>Top Source Methods</h2>
    <table>
        <tr><th>Source Method</th><th>Count</th></tr>
"""
        
        for item in stats['Top Source Methods']:
            html_content += f"<tr><td>{item['source']}</td><td>{item['count']}</td></tr>"
        
        html_content += f"""
    </table>
    
    <div style="margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 5px;">
        <p><strong>Database Size:</strong> {stats['Database Size (MB)']} MB</p>
        <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
        
        with open(exports_dir / filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Summary report generated: {filename}")
        return str(exports_dir / filename)
    
    def cleanup_old_data(self, days: int) -> int:
        """Clean up old investigation data"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self.get_connection() as conn:
            # Count investigations to be deleted
            count_cursor = conn.execute(
                "SELECT COUNT(*) FROM investigations WHERE created_date < ? AND status = 'completed'",
                (cutoff_date,)
            )
            count = count_cursor.fetchone()[0]
            
            if count > 0:
                # Delete old investigations (cascading deletes will handle related data)
                conn.execute(
                    "DELETE FROM investigations WHERE created_date < ? AND status = 'completed'",
                    (cutoff_date,)
                )
                
                # Clean up orphaned system logs
                conn.execute(
                    "DELETE FROM system_logs WHERE timestamp < ?",
                    (cutoff_date,)
                )
                
                conn.commit()
                
                self._log_system_event(
                    level='INFO',
                    module='database_manager',
                    message=f'Cleaned up {count} old investigations (older than {days} days)'
                )
                
                logger.info(f"Cleaned up {count} investigations older than {days} days")
            
            return count
    
    def export_full_database(self) -> str:
        """Export full database backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"full_database_backup_{timestamp}.db"
        exports_dir = Path("data/exports")
        exports_dir.mkdir(exist_ok=True)
        
        backup_path = exports_dir / backup_filename
        
        # Copy database file
        import shutil
        shutil.copy2(self.db_path, backup_path)
        
        logger.info(f"Full database backup created: {backup_filename}")
        return str(backup_path)
    
    def reset_database(self) -> bool:
        """Reset database (delete all data)"""
        try:
            with self.get_connection() as conn:
                # Get all table names
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Delete all data from tables
                for table in tables:
                    if table != 'sqlite_sequence':  # Don't delete SQLite internal table
                        conn.execute(f"DELETE FROM {table}")
                
                # Reset sequences
                conn.execute("DELETE FROM sqlite_sequence")
                
                conn.commit()
                
                self._log_system_event(
                    level='WARNING',
                    module='database_manager',
                    message='Database reset performed - all data deleted'
                )
                
                logger.warning("Database reset completed - all data deleted")
                return True
                
        except Exception as e:
            logger.error(f"Database reset failed: {e}")
            return False
    
    def _generate_result_hash(self, result: Any) -> str:
        """Generate hash signature for result deduplication"""
        # Create a hash based on key result properties
        hash_components = [
            getattr(result, 'data_type', 'unknown'),
            getattr(result, 'value', str(result)),
            getattr(result, 'source_method', 'unknown')
        ]
        
        hash_string = '|'.join(str(component) for component in hash_components)
        return hashlib.md5(hash_string.encode('utf-8')).hexdigest()
    
    def _log_system_event(self, level: str, module: str, message: str, 
                         investigation_id: Optional[int] = None, 
                         additional_data: Optional[Dict] = None):
        """Log system events for audit trail"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO system_logs 
                    (level, module, message, timestamp, investigation_id, additional_data)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    level,
                    module,
                    message,
                    datetime.now().isoformat(),
                    investigation_id,
                    json.dumps(additional_data) if additional_data else None
                ))
                conn.commit()
        except Exception as e:
            # Don't let logging errors break the main functionality
            logger.error(f"Failed to log system event: {e}")

# Example usage and testing
def test_database_manager():
    """Test the database manager"""
    db_path = Path("test_intelligence.db")
    
    # Clean up previous test
    if db_path.exists():
        db_path.unlink()
    
    try:
        # Initialize database
        db = DatabaseManager(db_path)
        
        # Test investigation creation
        strategy = {
            'target_type': 'business_category',
            'geographic_focus': 'Riyadh',
            'urgency_level': 'standard',
            'search_depth': 'comprehensive'
        }
        
        inv_id = db.create_investigation("hotels in Riyadh", "lead_generation", strategy)
        print(f"Created investigation: {inv_id}")
        
        # Test saving results
        class MockResult:
            def __init__(self):
                self.data_type = "business_profile"
                self.value = "Luxury Hotel Riyadh"
                self.confidence = 0.85
                self.source_method = "google_search"
                self.source_url = "https://example.com"
                self.context = {"rating": 4.5}
                self.timestamp = datetime.now()
                self.validation_status = "pending"
                self.geographic_location = "Riyadh"
                self.enrichment_data = {}
                self.metadata = {}
                self.relevance_score = 0.9
        
        result_id = db.save_intelligence_result(inv_id, MockResult())
        print(f"Saved result: {result_id}")
        
        # Test contact information
        contact = {
            'type': 'email',
            'value': 'info@luxuryhotel.com',
            'confidence': 0.9,
            'validation_status': 'verified'
        }
        
        contact_id = db.save_contact_information(inv_id, contact)
        print(f"Saved contact: {contact_id}")
        
        # Test analysis result
        analysis = {
            'analysis_type': 'comprehensive',
            'data': {'business_type': 'hospitality'},
            'confidence_score': 0.8,
            'processing_time': 2.5,
            'key_insights': ['High-end hotel', 'Good location'],
            'recommendations': ['Contact directly', 'Check availability']
        }
        
        analysis_id = db.save_analysis_result(inv_id, analysis)
        print(f"Saved analysis: {analysis_id}")
        
        # Complete investigation
        db.complete_investigation(inv_id, 1, 0.85)
        
        # Test queries
        history = db.get_investigation_history(limit=10)
        print(f"Investigation history: {len(history)} items")
        
        details = db.get_investigation_details(inv_id)
        print(f"Investigation details: {details['query']}")
        
        stats = db.get_database_statistics()
        print(f"Database statistics: {stats}")
        
        # Test export
        export_path = db.export_investigation(inv_id, 'json')
        print(f"Exported to: {export_path}")
        
        print("Database manager test completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if db_path.exists():
            db_path.unlink()

if __name__ == "__main__":
    test_database_manager()