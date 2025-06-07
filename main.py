#!/usr/bin/env python3
"""
Advanced OSINT Intelligence System
Main Entry Point - Professional Grade Intelligence Gathering
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Core imports
from core.questionnaire import AIQuestionnaire
from core.discovery_engine import AdvancedDiscoveryEngine
from core.ai_analyzer import IntelligenceAnalyzer
from core.database_manager import DatabaseManager
from utils.rate_limiter import RateLimiter
from utils.proxy_manager import ProxyManager

class AdvancedOSINTSystem:
    """Main OSINT System Controller"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.data_dir = self.project_root / "data"
        self.config_dir = self.project_root / "config"
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        (self.data_dir / "cache").mkdir(exist_ok=True)
        (self.data_dir / "exports").mkdir(exist_ok=True)
        
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
                elif choice == "0":
                    print("\nShutting down Advanced OSINT System...")
                    break
                else:
                    print("Invalid choice. Please try again.")
                
                input("\nPress Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\nSystem interrupted by user. Goodbye!")
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            print("Please check logs for details.")
    
    def _get_banner(self):
        """Get system banner"""
        return """
╔══════════════════════════════════════════════════════════════╗
║                ADVANCED OSINT INTELLIGENCE SYSTEM            ║
║                     Professional Grade v1.0                 ║
║                                                              ║
║  Multi-Source Intelligence • AI-Powered Analysis            ║
║  Business Intelligence • Contact Discovery                  ║
║  Decision Maker Identification • Market Research            ║
╚══════════════════════════════════════════════════════════════╝
"""
    
    def _show_main_menu(self):
        """Show main menu and get user choice"""
        print("\n" + "="*60)
        print("MAIN MENU")
        print("="*60)
        print("1. Guided Investigation (AI-Powered Questions)")
        print("2. Quick Investigation (Direct Search)")
        print("3. Batch Investigation (Multiple Targets)")
        print("4. View Investigation History")
        print("5. System Settings & Configuration")
        print("6. Export Data & Reports")
        print("0. Exit System")
        print("="*60)
        
        return input("Select option: ").strip()
    
    async def _guided_investigation(self):
        """Run guided investigation with AI questionnaire"""
        print("\n" + "="*60)
        print("GUIDED INVESTIGATION MODE")
        print("="*60)
        print("The AI will ask strategic questions to optimize your search.\n")
        
        # Run questionnaire
        questionnaire_result = self.questionnaire.start_questionnaire()
        self.current_profile = questionnaire_result["profile"]
        strategy = questionnaire_result["strategy"]
        
        print(f"\nConfiguration complete!")
        print(f"Search Context: {self.current_profile.context.value}")
        print(f"Industry Focus: {self.current_profile.industry.value if self.current_profile.industry else 'Mixed'}")
        print(f"Geographic Scope: {self.current_profile.geographic_scope}")
        
        # Get target from user
        target_input = input("\nEnter your search target: ").strip()
        if not target_input:
            print("No target provided. Returning to main menu.")
            return
        
        # Create investigation
        investigation_id = self.db_manager.create_investigation(
            query=target_input,
            context=self.current_profile.context.value,
            strategy=strategy
        )
        self.current_investigation = investigation_id
        
        # Run discovery
        await self._execute_discovery(target_input, strategy)
    
    async def _quick_investigation(self):
        """Run quick investigation without questionnaire"""
        print("\n" + "="*60)
        print("QUICK INVESTIGATION MODE")
        print("="*60)
        
        target_input = input("Enter search target: ").strip()
        if not target_input:
            print("No target provided. Returning to main menu.")
            return
        
        search_type = input("Search type (business/people/domain/general): ").strip().lower()
        if search_type not in ["business", "people", "domain", "general"]:
            search_type = "general"
        
        # Create quick strategy
        strategy = {
            "search_sources": ["google_search", "bing_search", "social_media"],
            "analysis_depth": "standard",
            "priority_data": ["contact_info", "business_info"]
        }
        
        # Create investigation
        investigation_id = self.db_manager.create_investigation(
            query=target_input,
            context=search_type,
            strategy=strategy
        )
        self.current_investigation = investigation_id
        
        # Run discovery
        await self._execute_discovery(target_input, strategy)
    
    async def _execute_discovery(self, target: str, strategy: dict):
        """Execute the discovery process"""
        print(f"\nStarting intelligence discovery for: {target}")
        print("This may take 10-30 minutes depending on depth settings...")
        print("="*60)
        
        try:
            # Create discovery target
            from core.discovery_engine import DiscoveryTarget
            
            discovery_target = DiscoveryTarget(
                primary_identifier=target,
                target_type=self._determine_target_type(target),
                context=strategy.get("context", "general"),
                priority_data=strategy.get("priority_data", ["contact_info"]),
                geographic_focus=getattr(self.current_profile, "geographic_scope", ""),
                industry_keywords=strategy.get("search_keywords", [])
            )
            
            # Run comprehensive discovery
            results = await self.discovery_engine.comprehensive_discovery(discovery_target)
            
            # Analyze results with AI
            print("Running AI analysis on collected intelligence...")
            analysis = await self.ai_analyzer.analyze_intelligence_batch(results)
            
            # Save results
            self._save_investigation_results(results, analysis)
            
            # Display summary
            self._display_results_summary(results, analysis)
            
        except Exception as e:
            print(f"Discovery failed: {e}")
            return
    
    def _determine_target_type(self, target: str) -> str:
        """Determine the type of target"""
        if "@" in target:
            return "email"
        elif "." in target and not " " in target:
            return "domain"
        elif any(char.isdigit() for char in target) and "." in target:
            return "ip"
        else:
            return "company"
    
    def _save_investigation_results(self, results: list, analysis: dict):
        """Save investigation results to database"""
        if not self.current_investigation:
            return
        
        try:
            # Save individual results
            for result in results:
                self.db_manager.save_intelligence_result(
                    investigation_id=self.current_investigation,
                    result=result
                )
            
            # Save analysis
            self.db_manager.save_analysis_result(
                investigation_id=self.current_investigation,
                analysis=analysis
            )
            
            # Update investigation status
            self.db_manager.complete_investigation(
                investigation_id=self.current_investigation,
                total_results=len(results)
            )
            
            print(f"Results saved to database (Investigation ID: {self.current_investigation})")
            
        except Exception as e:
            print(f"Failed to save results: {e}")
    
    def _display_results_summary(self, results: list, analysis: dict):
        """Display summary of results"""
        print("\n" + "="*60)
        print("INTELLIGENCE DISCOVERY COMPLETE")
        print("="*60)
        
        # Basic statistics
        print(f"Total Intelligence Items: {len(results)}")
        print(f"Investigation ID: {self.current_investigation}")
        
        # Results by type
        results_by_type = {}
        for result in results:
            data_type = result.data_type
            if data_type not in results_by_type:
                results_by_type[data_type] = []
            results_by_type[data_type].append(result)
        
        print(f"\nResults by Type:")
        for data_type, items in results_by_type.items():
            avg_confidence = sum(item.confidence for item in items) / len(items)
            print(f"  • {data_type.replace('_', ' ').title()}: {len(items)} items (avg confidence: {avg_confidence:.2f})")
        
        # High-confidence findings
        high_confidence = [r for r in results if r.confidence >= 0.8]
        print(f"\nHigh-Confidence Findings ({len(high_confidence)} items):")
        for result in high_confidence[:10]:  # Show top 10
            value_preview = result.value[:50] + "..." if len(result.value) > 50 else result.value
            print(f"  • {result.data_type}: {value_preview} (confidence: {result.confidence:.2f})")
        
        # AI Analysis Summary
        if analysis:
            print(f"\nAI Analysis Summary:")
            summary = analysis.get("summary", {})
            if "business_type" in summary:
                print(f"  • Business Type: {summary['business_type']} (confidence: {summary.get('business_confidence', 0):.2f})")
            if "target_audience" in summary:
                print(f"  • Target Audience: {summary['target_audience']}")
            if "key_insights" in summary:
                print(f"  • Key Insights:")
                for insight in summary["key_insights"][:3]:
                    print(f"    - {insight}")
        
        # Export options
        print(f"\nExport Options:")
        print(f"  1. JSON Export: Available")
        print(f"  2. CSV Export: Available") 
        print(f"  3. HTML Report: Available")
        
        export_choice = input("\nWould you like to export results now? (y/N): ").strip().lower()
        if export_choice == 'y':
            self._export_current_investigation()
    
    def _export_current_investigation(self):
        """Export current investigation"""
        if not self.current_investigation:
            print("No active investigation to export.")
            return
        
        try:
            export_formats = ["json", "csv", "html"]
            print("Available formats: " + ", ".join(export_formats))
            format_choice = input("Select format (json/csv/html): ").strip().lower()
            
            if format_choice not in export_formats:
                format_choice = "json"
            
            export_path = self.db_manager.export_investigation(
                investigation_id=self.current_investigation,
                format=format_choice
            )
            
            print(f"Investigation exported to: {export_path}")
            
        except Exception as e:
            print(f"Export failed: {e}")
    
    async def _batch_investigation(self):
        """Run batch investigation on multiple targets"""
        print("\n" + "="*60)
        print("BATCH INVESTIGATION MODE")
        print("="*60)
        
        # Get targets
        print("Enter targets (one per line, empty line to finish):")
        targets = []
        while True:
            target = input("Target: ").strip()
            if not target:
                break
            targets.append(target)
        
        if not targets:
            print("No targets provided.")
            return
        
        print(f"\nProcessing {len(targets)} targets...")
        
        # Process each target
        for i, target in enumerate(targets, 1):
            print(f"\nProcessing target {i}/{len(targets)}: {target}")
            
            # Create individual investigation
            investigation_id = self.db_manager.create_investigation(
                query=target,
                context="batch_processing",
                strategy={"batch_mode": True}
            )
            
            self.current_investigation = investigation_id
            
            try:
                # Quick discovery for batch mode
                discovery_target = DiscoveryTarget(
                    primary_identifier=target,
                    target_type=self._determine_target_type(target),
                    context="batch",
                    priority_data=["contact_info"],
                    geographic_focus="",
                    industry_keywords=[]
                )
                
                results = await self.discovery_engine.quick_discovery(discovery_target)
                analysis = await self.ai_analyzer.quick_analysis(results)
                
                self._save_investigation_results(results, analysis)
                print(f"  Completed: {len(results)} results found")
                
            except Exception as e:
                print(f"  Failed: {e}")
                continue
        
        print(f"\nBatch processing complete!")
        print(f"All results saved to database.")
    
    def _view_history(self):
        """View investigation history"""
        print("\n" + "="*60)
        print("INVESTIGATION HISTORY")
        print("="*60)
        
        try:
            history = self.db_manager.get_investigation_history(limit=20)
            
            if not history:
                print("No investigations found.")
                return
            
            print(f"Showing last {len(history)} investigations:")
            print()
            
            for inv in history:
                status_icon = "✓" if inv["status"] == "completed" else "⏳"
                print(f"{status_icon} ID: {inv['id']} | Query: {inv['query'][:40]}... | "
                      f"Results: {inv.get('total_results', 0)} | Date: {inv['created_date']}")
            
            # Option to view specific investigation
            inv_id = input("\nEnter investigation ID to view details (or press Enter to return): ").strip()
            if inv_id.isdigit():
                self._view_investigation_details(int(inv_id))
                
        except Exception as e:
            print(f"Failed to load history: {e}")
    
    def _view_investigation_details(self, investigation_id: int):
        """View details of specific investigation"""
        try:
            details = self.db_manager.get_investigation_details(investigation_id)
            
            if not details:
                print("Investigation not found.")
                return
            
            print(f"\nInvestigation Details (ID: {investigation_id})")
            print("="*40)
            print(f"Query: {details['query']}")
            print(f"Context: {details['context']}")
            print(f"Status: {details['status']}")
            print(f"Created: {details['created_date']}")
            print(f"Total Results: {details.get('total_results', 0)}")
            
            if details.get('results'):
                print(f"\nTop Results:")
                for result in details['results'][:10]:
                    print(f"  • {result['data_type']}: {result['value'][:50]}...")
            
        except Exception as e:
            print(f"Failed to load investigation details: {e}")
    
    def _system_settings(self):
        """System settings and configuration"""
        print("\n" + "="*60)
        print("SYSTEM SETTINGS")
        print("="*60)
        
        print("1. Proxy Settings")
        print("2. Rate Limiting")
        print("3. Data Sources Configuration")
        print("4. Export Settings")
        print("5. Database Management")
        print("0. Return to Main Menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            self._configure_proxy()
        elif choice == "2":
            self._configure_rate_limiting()
        elif choice == "3":
            self._configure_data_sources()
        elif choice == "4":
            self._configure_export_settings()
        elif choice == "5":
            self._database_management()
    
    def _configure_proxy(self):
        """Configure proxy settings"""
        print("\nProxy Configuration:")
        print("Current proxy status:", "Enabled" if self.proxy_manager.enabled else "Disabled")
        
        enable = input("Enable proxy rotation? (y/N): ").strip().lower()
        if enable == 'y':
            proxy_list = input("Enter proxy list file path (or press Enter for default): ").strip()
            self.proxy_manager.configure(enabled=True, proxy_file=proxy_list or None)
        else:
            self.proxy_manager.configure(enabled=False)
        
        print("Proxy settings updated.")
    
    def _configure_rate_limiting(self):
        """Configure rate limiting"""
        print("\nRate Limiting Configuration:")
        
        try:
            requests_per_minute = int(input("Requests per minute (current: 30): ") or "30")
            delay_between_requests = float(input("Delay between requests in seconds (current: 2.0): ") or "2.0")
            
            self.rate_limiter.configure(
                requests_per_minute=requests_per_minute,
                delay_between_requests=delay_between_requests
            )
            
            print("Rate limiting settings updated.")
            
        except ValueError:
            print("Invalid input. Settings not changed.")
    
    def _configure_data_sources(self):
        """Configure data sources"""
        print("\nData Sources Configuration:")
        print("This feature will be implemented in the next version.")
    
    def _configure_export_settings(self):
        """Configure export settings"""
        print("\nExport Settings Configuration:")
        print("This feature will be implemented in the next version.")
    
    def _database_management(self):
        """Database management options"""
        print("\nDatabase Management:")
        print("1. View database statistics")
        print("2. Cleanup old data")
        print("3. Export full database")
        print("4. Reset database (WARNING: This will delete all data)")
        
        choice = input("Select option: ").strip()
        
        if choice == "1":
            stats = self.db_manager.get_database_statistics()
            print(f"\nDatabase Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        elif choice == "2":
            days = int(input("Delete data older than X days: ") or "30")
            deleted = self.db_manager.cleanup_old_data(days)
            print(f"Deleted {deleted} old records.")
        elif choice == "3":
            export_path = self.db_manager.export_full_database()
            print(f"Database exported to: {export_path}")
        elif choice == "4":
            confirm = input("Type 'CONFIRM' to reset database: ")
            if confirm == "CONFIRM":
                self.db_manager.reset_database()
                print("Database reset complete.")
            else:
                print("Reset cancelled.")
    
    def _export_data(self):
        """Export data and reports"""
        print("\n" + "="*60)
        print("DATA EXPORT")
        print("="*60)
        
        print("1. Export specific investigation")
        print("2. Export all investigations")
        print("3. Export summary report")
        print("0. Return to Main Menu")
        
        choice = input("Select option: ").strip()
        
        if choice == "1":
            inv_id = input("Enter investigation ID: ").strip()
            if inv_id.isdigit():
                format_choice = input("Format (json/csv/html): ").strip().lower() or "json"
                try:
                    export_path = self.db_manager.export_investigation(int(inv_id), format_choice)
                    print(f"Investigation exported to: {export_path}")
                except Exception as e:
                    print(f"Export failed: {e}")
        elif choice == "2":
            format_choice = input("Format (json/csv/html): ").strip().lower() or "json"
            try:
                export_path = self.db_manager.export_all_investigations(format_choice)
                print(f"All investigations exported to: {export_path}")
            except Exception as e:
                print(f"Export failed: {e}")
        elif choice == "3":
            try:
                export_path = self.db_manager.export_summary_report()
                print(f"Summary report exported to: {export_path}")
            except Exception as e:
                print(f"Export failed: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Advanced OSINT Intelligence System")
    parser.add_argument("--gui", action="store_true", help="Launch GUI mode")
    parser.add_argument("--target", type=str, help="Direct target for quick search")
    parser.add_argument("--batch", type=str, help="Batch file with targets")
    parser.add_argument("--export", type=str, help="Export investigation ID")
    
    args = parser.parse_args()
    
    # Initialize system
    system = AdvancedOSINTSystem()
    
    try:
        if args.gui:
            # Launch GUI mode
            from gui.main_window import launch_gui
            launch_gui(system)
        elif args.target:
            # Quick search mode
            asyncio.run(system._quick_search_mode(args.target))
        elif args.batch:
            # Batch processing mode
            asyncio.run(system._batch_file_mode(args.batch))
        elif args.export:
            # Export mode
            system._export_mode(args.export)
        else:
            # Interactive mode
            asyncio.run(system.run_interactive_mode())
            
    except KeyboardInterrupt:
        print("\nSystem interrupted. Goodbye!")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()