#!/usr/bin/env python3
"""
Advanced OSINT Intelligence System
Main Entry Point - Professional Grade Intelligence Gathering
"""

import sys
import os
import asyncio
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Core imports
from core.questionnaire import AIQuestionnaire
from core.discovery_engine import AdvancedDiscoveryEngine, DiscoveryTarget, TargetType
from core.ai_analyzer import IntelligenceAnalyzer
from core.database_manager import DatabaseManager
from utils.rate_limiter import RateLimiter
from utils.proxy_manager import ProxyManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/osint_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class AdvancedOSINTSystem:
    """Main OSINT System Controller"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.data_dir = self.project_root / "data"
        self.config_dir = self.project_root / "config"
        
        # Ensure directories exist
        self._setup_directories()
        
        # Initialize components
        self.questionnaire = AIQuestionnaire()
        self.discovery_engine = AdvancedDiscoveryEngine()
        self.ai_analyzer = IntelligenceAnalyzer()
        self.db_manager = DatabaseManager(self.data_dir / "intelligence.db")
        self.rate_limiter = RateLimiter()
        self.proxy_manager = ProxyManager()
        
        # Current investigation
        self.current_investigation = None
        self.current_profile = None
        
        logger.info("Advanced OSINT System initialized successfully")
    
    def _setup_directories(self):
        """Setup required directories"""
        directories = [
            self.data_dir,
            self.data_dir / "cache",
            self.data_dir / "exports",
            self.project_root / "logs",
            self.config_dir
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True, parents=True)
    
    async def run_interactive_mode(self):
        """Run in interactive command-line mode"""
        print(self._get_banner())
        
        try:
            while True:
                choice = self._show_main_menu()
                
                if choice == "1":
                    await self._guided_investigation()
                elif choice == "2":
                    await self._quick_investigation()
                elif choice == "3":
                    await self._batch_investigation()
                elif choice == "4":
                    self._view_history()
                elif choice == "5":
                    self._system_settings()
                elif choice == "6":
                    self._export_data()
                elif choice == "7":
                    self._database_management()
                elif choice == "8":
                    await self._advanced_search()
                elif choice == "0":
                    print("\nShutting down Advanced OSINT System...")
                    break
                else:
                    print("Invalid choice. Please try again.")
                
                input("\nPress Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\nSystem interrupted by user. Goodbye!")
        except Exception as e:
            logger.error(f"Unexpected error in interactive mode: {e}")
            print(f"\nUnexpected error: {e}")
            print("Please check logs for details.")
    
    def _get_banner(self):
        """Get system banner"""
        return """
╔══════════════════════════════════════════════════════════════╗
║                ADVANCED OSINT INTELLIGENCE SYSTEM            ║
║                     Professional Grade v2.0                 ║
║                                                              ║
║  Multi-Source Intelligence • AI-Powered Analysis            ║
║  Business Intelligence • Contact Discovery                  ║
║  Decision Maker Identification • Market Research            ║
║                                                              ║
║  🔍 Search Engines • 📱 Social Media • 🏢 Directories       ║
║  🤖 AI Analysis • 📊 Reports • 🗄️ Database                 ║
╚══════════════════════════════════════════════════════════════╝

Welcome to the most advanced OSINT intelligence gathering system.
AI-powered, multi-source, professional-grade intelligence collection.
"""
    
    def _show_main_menu(self):
        """Show main menu and get user choice"""
        print("\n" + "="*70)
        print("MAIN MENU - Advanced OSINT Intelligence System")
        print("="*70)
        print("📋 INVESTIGATION MODES:")
        print("  1. 🧠 Guided Investigation (AI-Powered Questions)")
        print("  2. ⚡ Quick Investigation (Direct Search)")
        print("  3. 📊 Batch Investigation (Multiple Targets)")
        print("  4. 🔍 Advanced Search (Custom Parameters)")
        print()
        print("📁 DATA MANAGEMENT:")
        print("  5. 📖 View Investigation History")
        print("  6. 📤 Export Data & Reports")
        print("  7. 🗄️ Database Management")
        print()
        print("⚙️ SYSTEM:")
        print("  8. 🔧 System Settings & Configuration")
        print("  0. 🚪 Exit System")
        print("="*70)
        
        return input("Select option: ").strip()
    
    async def _guided_investigation(self):
        """Run guided investigation with AI questionnaire"""
        print("\n" + "="*70)
        print("🧠 GUIDED INVESTIGATION MODE")
        print("="*70)
        print("The AI will ask strategic questions to optimize your search.")
        print("This mode provides the best results through intelligent configuration.\n")
        
        try:
            # Run questionnaire
            print("Starting AI-powered questionnaire...")
            questionnaire_result = self.questionnaire.start_questionnaire()
            self.current_profile = questionnaire_result["profile"]
            strategy = questionnaire_result["strategy"]
            
            print(f"\n✅ Configuration complete!")
            print(f"Search Context: {self.current_profile.context.value}")
            print(f"Industry Focus: {self.current_profile.industry.value if self.current_profile.industry else 'Mixed'}")
            print(f"Geographic Scope: {self.current_profile.geographic_scope}")
            print(f"Estimated Time: {questionnaire_result['estimated_time']}")
            
            # Get target from user
            print("\n" + "-"*50)
            target_input = input("Enter your search target: ").strip()
            if not target_input:
                print("❌ No target provided. Returning to main menu.")
                return
            
            # Create investigation in database
            investigation_id = self.db_manager.create_investigation(
                query=target_input,
                context=self.current_profile.context.value,
                strategy=strategy
            )
            self.current_investigation = investigation_id
            
            # Convert profile to discovery strategy
            discovery_strategy = await self.discovery_engine.analyze_target_and_strategize(
                target_input, 
                {
                    'context': self.current_profile.context.value,
                    'data_priorities': self.current_profile.data_priorities,
                    'urgency': self.current_profile.urgency.value,
                    'search_depth': self.current_profile.search_depth,
                    'risk_tolerance': self.current_profile.risk_tolerance,
                    'geographic_focus': ', '.join(self.current_profile.geographic_regions)
                }
            )
            
            # Run discovery
            await self._execute_discovery(target_input, discovery_strategy)
            
        except Exception as e:
            logger.error(f"Guided investigation failed: {e}")
            print(f"❌ Investigation failed: {e}")
    
    async def _quick_investigation(self):
        """Run quick investigation without questionnaire"""
        print("\n" + "="*70)
        print("⚡ QUICK INVESTIGATION MODE")
        print("="*70)
        print("Fast search with basic configuration. Good for immediate results.\n")
        
        target_input = input("Enter search target: ").strip()
        if not target_input:
            print("❌ No target provided. Returning to main menu.")
            return
        
        # Quick configuration
        print("\nQuick Configuration:")
        search_type = input("Search type (business/people/domain/general) [general]: ").strip().lower()
        if search_type not in ["business", "people", "domain", "general"]:
            search_type = "general"
        
        location = input("Geographic focus (optional): ").strip()
        
        # Create quick strategy
        strategy = {
            "search_sources": ["search_engines", "business_directories"],
            "analysis_depth": "standard",
            "priority_data": ["contact_info", "business_info"],
            "geographic_focus": location,
            "urgency_level": "immediate",
            "search_depth": "quick"
        }
        
        # Create investigation
        investigation_id = self.db_manager.create_investigation(
            query=target_input,
            context=search_type,
            strategy=strategy
        )
        self.current_investigation = investigation_id
        
        # Run quick discovery
        try:
            quick_results = await self.discovery_engine.quick_discovery(
                target_input, 
                {'context': search_type, 'geographic_focus': location}
            )
            
            # Quick analysis
            analysis = await self.ai_analyzer.quick_analysis(quick_results)
            
            # Save results
            await self._save_investigation_results(quick_results, analysis)
            
            # Display summary
            self._display_quick_results_summary(quick_results, analysis)
            
        except Exception as e:
            logger.error(f"Quick investigation failed: {e}")
            print(f"❌ Quick investigation failed: {e}")
    
    async def _advanced_search(self):
        """Advanced search with custom parameters"""
        print("\n" + "="*70)
        print("🔍 ADVANCED SEARCH MODE")
        print("="*70)
        print("Custom search with full control over parameters.\n")
        
        target_input = input("Enter search target: ").strip()
        if not target_input:
            print("❌ No target provided.")
            return
        
        # Advanced configuration
        print("\nAdvanced Configuration:")
        
        # Search sources
        print("\nAvailable search sources:")
        print("1. Search Engines (Google, Bing, DuckDuckGo)")
        print("2. Social Media (LinkedIn, Twitter, Facebook)")
        print("3. Business Directories (Yellow Pages, Yelp)")
        print("4. Specialized Tools (Domain analysis, Technical)")
        
        sources_input = input("Select sources (1,2,3,4 or 'all') [all]: ").strip()
        if sources_input.lower() == 'all' or not sources_input:
            selected_sources = ['search_engines', 'social_media', 'business_directories', 'specialized_tools']
        else:
            source_map = {
                '1': 'search_engines',
                '2': 'social_media', 
                '3': 'business_directories',
                '4': 'specialized_tools'
            }
            selected_sources = [source_map[s] for s in sources_input.split(',') if s in source_map]
        
        # Other parameters
        geographic_focus = input("Geographic focus: ").strip()
        search_depth = input("Search depth (quick/standard/comprehensive) [standard]: ").strip() or "standard"
        risk_tolerance = input("Risk tolerance (low/medium/high) [medium]: ").strip() or "medium"
        
        # Data priorities
        print("\nData priorities (select multiple):")
        print("1. Contact Information")
        print("2. Business Profiles")
        print("3. Decision Makers")
        print("4. Social Media Presence")
        print("5. Technical Information")
        
        priorities_input = input("Select priorities (1,2,3,4,5) [1,2]: ").strip() or "1,2"
        priority_map = {
            '1': 'contact_info',
            '2': 'business_profiles',
            '3': 'decision_makers',
            '4': 'social_media',
            '5': 'technical_info'
        }
        selected_priorities = [priority_map[p] for p in priorities_input.split(',') if p in priority_map]
        
        # Create advanced strategy
        strategy = {
            "collection_methods": selected_sources,
            "search_depth": search_depth,
            "risk_tolerance": risk_tolerance,
            "priority_data": selected_priorities,
            "geographic_focus": geographic_focus,
            "parallel_execution": True,
            "validation_level": "comprehensive" if search_depth == "comprehensive" else "standard"
        }
        
        # Create investigation
        investigation_id = self.db_manager.create_investigation(
            query=target_input,
            context="advanced_search",
            strategy=strategy
        )
        self.current_investigation = investigation_id
        
        # Create discovery strategy
        discovery_strategy = await self.discovery_engine.analyze_target_and_strategize(
            target_input,
            {
                'context': 'advanced_search',
                'data_priorities': selected_priorities,
                'urgency': 'standard',
                'search_depth': search_depth,
                'risk_tolerance': risk_tolerance,
                'geographic_focus': geographic_focus
            }
        )
        
        # Execute discovery
        await self._execute_discovery(target_input, discovery_strategy)
    
    async def _execute_discovery(self, target: str, strategy):
        """Execute the discovery process"""
        print(f"\n🚀 Starting intelligence discovery for: {target}")
        print("This may take 10-60 minutes depending on depth settings...")
        print("="*70)
        
        try:
            # Show progress indicator
            print("📡 Initializing discovery engines...")
            
            # Run comprehensive discovery
            results = await self.discovery_engine.comprehensive_discovery(strategy)
            
            print(f"✅ Data collection completed: {len(results)} items found")
            print("🤖 Running AI analysis on collected intelligence...")
            
            # Analyze results with AI
            analysis = await self.ai_analyzer.analyze_intelligence_batch(results)
            
            print("💾 Saving results to database...")
            # Save results
            await self._save_investigation_results(results, analysis)
            
            # Display comprehensive summary
            self._display_comprehensive_results_summary(results, analysis)
            
        except Exception as e:
            logger.error(f"Discovery execution failed: {e}")
            print(f"❌ Discovery failed: {e}")
            import traceback
            traceback.print_exc()
    
    async def _save_investigation_results(self, results: List, analysis: Any):
        """Save investigation results to database"""
        if not self.current_investigation:
            logger.warning("No current investigation to save results to")
            return
        
        try:
            saved_count = 0
            
            # Save individual results
            for result in results:
                try:
                    self.db_manager.save_intelligence_result(
                        investigation_id=self.current_investigation,
                        result=result
                    )
                    saved_count += 1
                except Exception as e:
                    logger.error(f"Failed to save result: {e}")
            
            # Save analysis
            if analysis:
                try:
                    analysis_dict = {
                        'analysis_type': 'comprehensive',
                        'data': analysis.__dict__ if hasattr(analysis, '__dict__') else analysis,
                        'confidence_score': getattr(analysis, 'data_quality_score', 0.0),
                        'processing_time': getattr(analysis, 'processing_time_seconds', 0.0),
                        'key_insights': getattr(analysis, 'key_insights', []),
                        'recommendations': getattr(analysis, 'actionable_recommendations', [])
                    }
                    
                    self.db_manager.save_analysis_result(
                        investigation_id=self.current_investigation,
                        analysis=analysis_dict
                    )
                except Exception as e:
                    logger.error(f"Failed to save analysis: {e}")
            
            # Update investigation status
            confidence_score = getattr(analysis, 'data_quality_score', 0.0) if analysis else 0.0
            self.db_manager.complete_investigation(
                investigation_id=self.current_investigation,
                total_results=saved_count,
                confidence_score=confidence_score
            )
            
            print(f"💾 Results saved: {saved_count} intelligence items")
            print(f"📊 Investigation ID: {self.current_investigation}")
            
        except Exception as e:
            logger.error(f"Failed to save investigation results: {e}")
            print(f"❌ Failed to save results: {e}")
    
    def _display_comprehensive_results_summary(self, results: List, analysis: Any):
        """Display comprehensive summary of results"""
        print("\n" + "="*70)
        print("🎯 INTELLIGENCE DISCOVERY COMPLETE")
        print("="*70)
        
        # Basic statistics
        print(f"📊 Total Intelligence Items: {len(results)}")
        print(f"🆔 Investigation ID: {self.current_investigation}")
        
        if analysis:
            print(f"🤖 AI Analysis Confidence: {getattr(analysis, 'data_quality_score', 0):.1%}")
            print(f"⏱️ Processing Time: {getattr(analysis, 'processing_time_seconds', 0):.1f} seconds")
        
        # Results by type
        if results:
            results_by_type = {}
            for result in results:
                data_type = getattr(result, 'data_type', 'unknown')
                if data_type not in results_by_type:
                    results_by_type[data_type] = []
                results_by_type[data_type].append(result)
            
            print(f"\n📋 Results by Type:")
            for data_type, items in results_by_type.items():
                avg_confidence = sum(getattr(item, 'confidence', 0) for item in items) / len(items)
                print(f"  • {data_type.replace('_', ' ').title()}: {len(items)} items (avg confidence: {avg_confidence:.2f})")
        
        # High-confidence findings
        if results:
            high_confidence = [r for r in results if getattr(r, 'confidence', 0) >= 0.8]
            print(f"\n⭐ High-Confidence Findings ({len(high_confidence)} items):")
            for result in high_confidence[:10]:  # Show top 10
                value = getattr(result, 'value', str(result))
                value_preview = value[:50] + "..." if len(str(value)) > 50 else value
                data_type = getattr(result, 'data_type', 'unknown')
                confidence = getattr(result, 'confidence', 0)
                print(f"  • {data_type}: {value_preview} (confidence: {confidence:.2f})")
        
        # AI Analysis Summary
        if analysis:
            print(f"\n🧠 AI Analysis Summary:")
            
            # Business analysis
            business_type = getattr(analysis, 'business_type', None)
            if business_type:
                business_confidence = getattr(analysis, 'business_confidence', 0)
                print(f"  • Business Type: {business_type.title()} (confidence: {business_confidence:.2f})")
            
            target_audience = getattr(analysis, 'target_audience_type', None)
            if target_audience:
                print(f"  • Target Audience: {target_audience}")
            
            primary_location = getattr(analysis, 'primary_location', None)
            if primary_location:
                print(f"  • Primary Location: {primary_location}")
            
            # Key insights
            insights = getattr(analysis, 'key_insights', [])
            if insights:
                print(f"  • Key Insights:")
                for insight in insights[:3]:
                    print(f"    - {insight}")
            
            # Recommendations
            recommendations = getattr(analysis, 'actionable_recommendations', [])
            if recommendations:
                print(f"  • Recommendations:")
                for rec in recommendations[:3]:
                    print(f"    - {rec}")
        
        # Export options
        print(f"\n📤 Export Options:")
        print(f"  1. JSON Export: Complete data structure")
        print(f"  2. CSV Export: Spreadsheet format") 
        print(f"  3. HTML Report: Professional report")
        
        export_choice = input("\nWould you like to export results now? (y/N): ").strip().lower()
        if export_choice == 'y':
            self._export_current_investigation()
    
    def _display_quick_results_summary(self, results: List, analysis: Dict):
        """Display summary for quick investigation"""
        print("\n" + "="*50)
        print("⚡ QUICK INVESTIGATION COMPLETE")
        print("="*50)
        
        print(f"📊 Found: {len(results)} intelligence items")
        print(f"🆔 Investigation ID: {self.current_investigation}")
        
        if analysis and 'summary' in analysis:
            summary = analysis['summary']
            print(f"🤖 Business Type: {summary.get('business_type', 'Unknown')}")
            print(f"📞 Contact Items: {summary.get('contact_items_found', 0)}")
            print(f"👥 Personnel Found: {summary.get('personnel_found', 0)}")
        
        # Show top results
        if results:
            print(f"\n⭐ Top Results:")
            for i, result in enumerate(results[:5], 1):
                value = getattr(result, 'value', str(result))
                value_preview = value[:40] + "..." if len(str(value)) > 40 else value
                confidence = getattr(result, 'confidence', 0)
                print(f"  {i}. {value_preview} (confidence: {confidence:.2f})")
    
    def _export_current_investigation(self):
        """Export current investigation"""
        if not self.current_investigation:
            print("❌ No active investigation to export.")
            return
        
        try:
            export_formats = ["json", "csv", "html"]
            print("Available formats: " + ", ".join(export_formats))
            format_choice = input("Select format (json/csv/html) [json]: ").strip().lower()
            
            if format_choice not in export_formats:
                format_choice = "json"
            
            export_path = self.db_manager.export_investigation(
                investigation_id=self.current_investigation,
                format=format_choice
            )
            
            print(f"✅ Investigation exported to: {export_path}")
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            print(f"❌ Export failed: {e}")
    
    async def _batch_investigation(self):
        """Run batch investigation on multiple targets"""
        print("\n" + "="*70)
        print("📊 BATCH INVESTIGATION MODE")
        print("="*70)
        print("Process multiple targets efficiently with parallel processing.\n")
        
        # Get targets
        print("Enter targets (one per line, empty line to finish):")
        targets = []
        while True:
            target = input("Target: ").strip()
            if not target:
                break
            targets.append(target)
        
        if not targets:
            print("❌ No targets provided.")
            return
        
        # Batch configuration
        print(f"\n📋 Processing {len(targets)} targets...")
        search_depth = input("Search depth for all (quick/standard) [quick]: ").strip() or "quick"
        location = input("Geographic focus (optional): ").strip()
        
        print(f"\n🚀 Starting batch processing...")
        print("="*50)
        
        results_summary = []
        
        # Process each target
        for i, target in enumerate(targets, 1):
            print(f"\n📍 Processing target {i}/{len(targets)}: {target}")
            
            # Create individual investigation
            strategy = {
                "batch_mode": True,
                "search_depth": search_depth,
                "geographic_focus": location
            }
            
            investigation_id = self.db_manager.create_investigation(
                query=target,
                context="batch_processing",
                strategy=strategy
            )
            
            self.current_investigation = investigation_id
            
            try:
                # Quick discovery for batch mode
                discovery_params = {
                    'context': 'batch',
                    'geographic_focus': location
                }
                
                results = await self.discovery_engine.quick_discovery(target, discovery_params)
                analysis = await self.ai_analyzer.quick_analysis(results)
                
                await self._save_investigation_results(results, analysis)
                
                # Store summary
                results_summary.append({
                    'target': target,
                    'investigation_id': investigation_id,
                    'results_count': len(results),
                    'success': True
                })
                
                print(f"  ✅ Completed: {len(results)} results found")
                
            except Exception as e:
                logger.error(f"Batch target failed: {e}")
                results_summary.append({
                    'target': target,
                    'investigation_id': investigation_id,
                    'results_count': 0,
                    'success': False,
                    'error': str(e)
                })
                print(f"  ❌ Failed: {e}")
                continue
        
        # Display batch summary
        print(f"\n" + "="*50)
        print("📊 BATCH PROCESSING COMPLETE")
        print("="*50)
        
        successful = sum(1 for r in results_summary if r['success'])
        total_results = sum(r['results_count'] for r in results_summary)
        
        print(f"✅ Successful: {successful}/{len(targets)} targets")
        print(f"📊 Total Results: {total_results} intelligence items")
        print(f"🗄️ All results saved to database")
        
        # Show individual results
        print(f"\n📋 Individual Results:")
        for result in results_summary:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['target']}: {result['results_count']} results (ID: {result['investigation_id']})")
    
    def _view_history(self):
        """View investigation history"""
        print("\n" + "="*70)
        print("📖 INVESTIGATION HISTORY")
        print("="*70)
        
        try:
            # Get filter options
            print("Filter options:")
            print("1. All investigations")
            print("2. Completed only")
            print("3. Active only")
            print("4. Recent (last 7 days)")
            
            filter_choice = input("Select filter [1]: ").strip() or "1"
            
            # Apply filters
            status_filter = None
            limit = 20
            
            if filter_choice == "2":
                status_filter = "completed"
            elif filter_choice == "3":
                status_filter = "active"
            elif filter_choice == "4":
                limit = 50  # More recent items
            
            history = self.db_manager.get_investigation_history(
                limit=limit, 
                status_filter=status_filter
            )
            
            if not history:
                print("📭 No investigations found.")
                return
            
            print(f"\n📋 Showing {len(history)} investigations:")
            print("-" * 70)
            
            for inv in history:
                status_icon = "✅" if inv["status"] == "completed" else "⏳" if inv["status"] == "active" else "❌"
                results_count = inv.get('results_count', 0)
                confidence = inv.get('confidence_score', 0)
                
                # Truncate long queries
                query_display = inv['query'][:40] + "..." if len(inv['query']) > 40 else inv['query']
                
                print(f"{status_icon} ID: {inv['id']:3d} | {query_display:43s} | "
                      f"Results: {results_count:3d} | Conf: {confidence:.2f} | {inv['created_date'][:10]}")
            
            # Option to view specific investigation
            print("-" * 70)
            inv_id = input("Enter investigation ID to view details (or press Enter): ").strip()
            if inv_id.isdigit():
                self._view_investigation_details(int(inv_id))
                
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            print(f"❌ Failed to load history: {e}")
    
    def _view_investigation_details(self, investigation_id: int):
        """View details of specific investigation"""
        try:
            details = self.db_manager.get_investigation_details(investigation_id)
            
            if not details:
                print("❌ Investigation not found.")
                return
            
            print(f"\n" + "="*60)
            print(f"📋 Investigation Details (ID: {investigation_id})")
            print("="*60)
            
            print(f"🎯 Query: {details['query']}")
            print(f"📝 Context: {details['context']}")
            print(f"📊 Status: {details['status']}")
            print(f"📅 Created: {details['created_date']}")
            if details.get('completed_date'):
                print(f"✅ Completed: {details['completed_date']}")
            print(f"📈 Total Results: {details.get('total_results', 0)}")
            print(f"🎯 Confidence Score: {details.get('confidence_score', 0):.2f}")
            
            # Strategy information
            strategy = details.get('strategy', {})
            if strategy:
                print(f"\n🔧 Strategy:")
                print(f"  Geographic Focus: {strategy.get('geographic_focus', 'Not specified')}")
                print(f"  Search Depth: {strategy.get('search_depth', 'Not specified')}")
                print(f"  Target Type: {strategy.get('target_type', 'Not specified')}")
            
            # Results breakdown
            results = details.get('results', [])
            if results:
                print(f"\n📊 Results Breakdown:")
                
                # Group by type
                by_type = {}
                for result in results:
                    data_type = result['data_type']
                    if data_type not in by_type:
                        by_type[data_type] = []
                    by_type[data_type].append(result)
                
                for data_type, items in by_type.items():
                    avg_conf = sum(item['confidence'] for item in items) / len(items)
                    print(f"  • {data_type.replace('#!/usr/bin/env python3
"""
Advanced OSINT Intelligence System
Main Entry Point - Professional Grade Intelligence Gathering
"""

import sys
import os
import asyncio
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Core imports
from core.questionnaire import AIQuestionnaire
from core