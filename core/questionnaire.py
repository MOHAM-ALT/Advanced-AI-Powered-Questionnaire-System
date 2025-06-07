"""
Advanced AI-Powered Questionnaire System
File Location: core/questionnaire.py
Real implementation with strategic intelligence gathering optimization
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import time

class SearchContext(Enum):
    LEAD_GENERATION = "lead_generation"
    COMPETITOR_ANALYSIS = "competitor_analysis" 
    RECRUITMENT = "recruitment"
    MARKET_RESEARCH = "market_research"
    SECURITY_ASSESSMENT = "security_assessment"
    INVESTMENT_RESEARCH = "investment_research"
    CUSTOMER_RESEARCH = "customer_research"

class IndustryType(Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    RETAIL = "retail"
    HOSPITALITY = "hospitality"
    MANUFACTURING = "manufacturing"
    EDUCATION = "education"
    REAL_ESTATE = "real_estate"
    CONSULTING = "consulting"
    LOGISTICS = "logistics"
    ENERGY = "energy"
    GOVERNMENT = "government"

class UrgencyLevel(Enum):
    IMMEDIATE = "immediate"
    THIS_WEEK = "this_week"
    THIS_MONTH = "this_month"
    NO_RUSH = "no_rush"

class TargetAudienceType(Enum):
    B2B_SMALL = "b2b_small"
    B2B_ENTERPRISE = "b2b_enterprise"
    B2C_INDIVIDUAL = "b2c_individual"
    GOVERNMENT = "government"
    NON_PROFIT = "non_profit"
    MIXED = "mixed"

@dataclass
class SearchProfile:
    """Complete search profile based on questionnaire responses"""
    context: SearchContext
    industry: Optional[IndustryType]
    target_audience: TargetAudienceType
    geographic_scope: str
    geographic_regions: List[str]
    urgency: UrgencyLevel
    data_priorities: List[str]
    budget_range: str
    company_size_focus: str
    decision_maker_levels: List[str]
    competitive_analysis: bool
    technology_focus: bool
    historical_data: bool
    social_media_focus: bool
    financial_data: bool
    custom_requirements: List[str]
    search_depth: str  # quick, standard, comprehensive
    risk_tolerance: str  # low, medium, high

class ProgressIndicator:
    """Progress indicator for questionnaire"""
    
    def __init__(self, total_steps: int):
        self.total_steps = total_steps
        self.current_step = 0
    
    def update(self):
        self.current_step += 1
        progress = (self.current_step / self.total_steps) * 100
        bar_length = 30
        filled = int(bar_length * self.current_step // self.total_steps)
        bar = '=' * filled + '-' * (bar_length - filled)
        print(f'\rProgress: [{bar}] {progress:.1f}% ({self.current_step}/{self.total_steps})', end='', flush=True)
        if self.current_step >= self.total_steps:
            print()  # New line when complete

class AIQuestionnaire:
    """Advanced AI-powered questionnaire system"""
    
    def __init__(self):
        self.profile = None
        self.responses = {}
        self.question_weights = {}
        self.adaptive_questions = {}
        self.load_question_database()
    
    def load_question_database(self):
        """Load comprehensive question database"""
        self.questions_db = {
            "context_identification": {
                "question": "What is your primary objective for this intelligence gathering?",
                "type": "single_choice",
                "required": True,
                "weight": 10,
                "options": {
                    "1": {
                        "text": "Generate sales leads and identify potential customers",
                        "context": SearchContext.LEAD_GENERATION,
                        "follow_up": ["budget_analysis", "decision_maker_focus", "sales_cycle"]
                    },
                    "2": {
                        "text": "Analyze competitors and market positioning",
                        "context": SearchContext.COMPETITOR_ANALYSIS,
                        "follow_up": ["competitive_depth", "market_share", "pricing_analysis"]
                    },
                    "3": {
                        "text": "Find and recruit talent for open positions",
                        "context": SearchContext.RECRUITMENT,
                        "follow_up": ["skill_requirements", "experience_levels", "compensation_data"]
                    },
                    "4": {
                        "text": "Research market opportunities and trends",
                        "context": SearchContext.MARKET_RESEARCH,
                        "follow_up": ["market_size", "trend_analysis", "growth_projections"]
                    },
                    "5": {
                        "text": "Assess security posture and digital footprint",
                        "context": SearchContext.SECURITY_ASSESSMENT,
                        "follow_up": ["vulnerability_assessment", "data_exposure", "threat_analysis"]
                    },
                    "6": {
                        "text": "Evaluate investment opportunities and due diligence",
                        "context": SearchContext.INVESTMENT_RESEARCH,
                        "follow_up": ["financial_analysis", "risk_assessment", "management_evaluation"]
                    },
                    "7": {
                        "text": "Research customers and market segments",
                        "context": SearchContext.CUSTOMER_RESEARCH,
                        "follow_up": ["customer_behavior", "satisfaction_analysis", "loyalty_factors"]
                    }
                }
            },
            
            "industry_identification": {
                "question": "Which industry or sector are you focusing on?",
                "type": "single_choice",
                "required": True,
                "weight": 8,
                "options": {
                    "1": {"text": "Technology and Software", "industry": IndustryType.TECHNOLOGY},
                    "2": {"text": "Healthcare and Medical Services", "industry": IndustryType.HEALTHCARE},
                    "3": {"text": "Financial Services and Banking", "industry": IndustryType.FINANCE},
                    "4": {"text": "Retail and E-commerce", "industry": IndustryType.RETAIL},
                    "5": {"text": "Hospitality and Tourism", "industry": IndustryType.HOSPITALITY},
                    "6": {"text": "Manufacturing and Industrial", "industry": IndustryType.MANUFACTURING},
                    "7": {"text": "Education and Training", "industry": IndustryType.EDUCATION},
                    "8": {"text": "Real Estate and Construction", "industry": IndustryType.REAL_ESTATE},
                    "9": {"text": "Consulting and Professional Services", "industry": IndustryType.CONSULTING},
                    "10": {"text": "Logistics and Transportation", "industry": IndustryType.LOGISTICS},
                    "11": {"text": "Energy and Utilities", "industry": IndustryType.ENERGY},
                    "12": {"text": "Government and Public Sector", "industry": IndustryType.GOVERNMENT},
                    "13": {"text": "Multiple industries or Other", "industry": None}
                }
            },
            
            "target_audience": {
                "question": "What type of organizations or individuals are you targeting?",
                "type": "single_choice",
                "required": True,
                "weight": 7,
                "options": {
                    "1": {
                        "text": "Small to medium businesses (1-500 employees)",
                        "audience": TargetAudienceType.B2B_SMALL,
                        "follow_up": ["smb_budget", "smb_decision_makers"]
                    },
                    "2": {
                        "text": "Large enterprises and corporations (500+ employees)", 
                        "audience": TargetAudienceType.B2B_ENTERPRISE,
                        "follow_up": ["enterprise_budget", "enterprise_procurement"]
                    },
                    "3": {
                        "text": "Individual consumers and end users",
                        "audience": TargetAudienceType.B2C_INDIVIDUAL,
                        "follow_up": ["consumer_demographics", "purchasing_behavior"]
                    },
                    "4": {
                        "text": "Government agencies and public sector",
                        "audience": TargetAudienceType.GOVERNMENT,
                        "follow_up": ["government_level", "procurement_process"]
                    },
                    "5": {
                        "text": "Non-profit organizations and NGOs",
                        "audience": TargetAudienceType.NON_PROFIT,
                        "follow_up": ["nonprofit_funding", "cause_focus"]
                    },
                    "6": {
                        "text": "Mixed or multiple audience types",
                        "audience": TargetAudienceType.MIXED,
                        "follow_up": ["audience_prioritization"]
                    }
                }
            },
            
            "geographic_scope": {
                "question": "What is your geographic scope of interest?",
                "type": "single_choice_with_input",
                "required": True,
                "weight": 6,
                "options": {
                    "1": {"text": "Specific city or metropolitan area", "scope": "city"},
                    "2": {"text": "State or province level", "scope": "state"},
                    "3": {"text": "Country-wide focus", "scope": "country"},
                    "4": {"text": "Regional (multiple countries)", "scope": "regional"},
                    "5": {"text": "Global with no geographic limits", "scope": "global"}
                },
                "follow_up_input": "Please specify the geographic region(s) of interest:"
            },
            
            "urgency_assessment": {
                "question": "What is your timeline for this research?",
                "type": "single_choice",
                "required": True,
                "weight": 5,
                "options": {
                    "1": {
                        "text": "Immediate results needed (today/tomorrow)",
                        "urgency": UrgencyLevel.IMMEDIATE,
                        "search_depth": "quick"
                    },
                    "2": {
                        "text": "This week (time-sensitive project)",
                        "urgency": UrgencyLevel.THIS_WEEK,
                        "search_depth": "standard"
                    },
                    "3": {
                        "text": "Within the next month",
                        "urgency": UrgencyLevel.THIS_MONTH,
                        "search_depth": "comprehensive"
                    },
                    "4": {
                        "text": "No specific deadline (thorough research preferred)",
                        "urgency": UrgencyLevel.NO_RUSH,
                        "search_depth": "comprehensive"
                    }
                }
            },
            
            "data_priorities": {
                "question": "Which types of information are most valuable to you? (Select multiple)",
                "type": "multiple_choice",
                "required": True,
                "weight": 9,
                "max_selections": 6,
                "options": {
                    "1": {"text": "Contact information (emails, phone numbers)", "priority": "contact_info"},
                    "2": {"text": "Key personnel and decision makers", "priority": "decision_makers"},
                    "3": {"text": "Company size, revenue, and financial data", "priority": "financial_data"},
                    "4": {"text": "Technology stack and tools used", "priority": "technology_stack"},
                    "5": {"text": "Social media presence and engagement", "priority": "social_media"},
                    "6": {"text": "Customer reviews and reputation", "priority": "reputation_data"},
                    "7": {"text": "Recent news, press releases, and updates", "priority": "news_monitoring"},
                    "8": {"text": "Competitive intelligence and positioning", "priority": "competitive_intel"},
                    "9": {"text": "Partnership and vendor relationships", "priority": "business_relationships"},
                    "10": {"text": "Physical locations and office addresses", "priority": "location_data"},
                    "11": {"text": "Job postings and hiring patterns", "priority": "hiring_data"},
                    "12": {"text": "Marketing strategies and messaging", "priority": "marketing_intel"}
                }
            }
        }
        
        # Context-specific follow-up questions
        self.context_specific_questions = {
            SearchContext.LEAD_GENERATION: [
                {
                    "id": "budget_analysis",
                    "question": "What is your ideal customer's budget range?",
                    "type": "single_choice",
                    "options": {
                        "1": {"text": "Low budget (Under $10K)", "budget": "low"},
                        "2": {"text": "Medium budget ($10K - $100K)", "budget": "medium"},
                        "3": {"text": "High budget ($100K - $1M)", "budget": "high"},
                        "4": {"text": "Enterprise budget ($1M+)", "budget": "enterprise"},
                        "5": {"text": "Mixed or unsure", "budget": "mixed"}
                    }
                },
                {
                    "id": "decision_maker_focus",
                    "question": "Which decision-making roles are you most interested in?",
                    "type": "multiple_choice",
                    "options": {
                        "1": {"text": "C-Level executives (CEO, CTO, CFO)", "role": "c_level"},
                        "2": {"text": "VPs and Directors", "role": "vp_director"},
                        "3": {"text": "Department managers", "role": "managers"},
                        "4": {"text": "Procurement and purchasing", "role": "procurement"},
                        "5": {"text": "Technical decision makers", "role": "technical"},
                        "6": {"text": "End users and influencers", "role": "end_users"}
                    }
                }
            ],
            
            SearchContext.RECRUITMENT: [
                {
                    "id": "experience_levels",
                    "question": "What experience level are you targeting?",
                    "type": "multiple_choice",
                    "options": {
                        "1": {"text": "Entry level (0-2 years)", "level": "entry"},
                        "2": {"text": "Mid-level (2-5 years)", "level": "mid"},
                        "3": {"text": "Senior level (5-10 years)", "level": "senior"},
                        "4": {"text": "Executive level (10+ years)", "level": "executive"},
                        "5": {"text": "Specialized experts", "level": "expert"}
                    }
                },
                {
                    "id": "skill_requirements",
                    "question": "Are you looking for specific technical skills or certifications?",
                    "type": "text_input",
                    "placeholder": "e.g., Python, AWS, PMP, Six Sigma, etc."
                }
            ],
            
            SearchContext.COMPETITOR_ANALYSIS: [
                {
                    "id": "competitive_depth",
                    "question": "How deep should the competitive analysis be?",
                    "type": "single_choice",
                    "options": {
                        "1": {"text": "Surface level (basic company info)", "depth": "surface"},
                        "2": {"text": "Standard analysis (products, pricing, positioning)", "depth": "standard"},
                        "3": {"text": "Deep dive (strategy, partnerships, weaknesses)", "depth": "deep"},
                        "4": {"text": "Comprehensive (full competitive intelligence)", "depth": "comprehensive"}
                    }
                }
            ]
        }
        
        # Advanced configuration questions
        self.advanced_questions = {
            "search_preferences": {
                "question": "How would you prefer to balance speed vs thoroughness?",
                "type": "single_choice",
                "options": {
                    "1": {"text": "Speed: Quick results, accept some gaps", "preference": "speed"},
                    "2": {"text": "Balanced: Good coverage in reasonable time", "preference": "balanced"},
                    "3": {"text": "Thorough: Comprehensive results, time flexible", "preference": "thorough"}
                }
            },
            
            "risk_tolerance": {
                "question": "What is your tolerance for using advanced data collection methods?",
                "type": "single_choice",
                "options": {
                    "1": {"text": "Conservative: Only basic public sources", "risk": "low"},
                    "2": {"text": "Moderate: Standard OSINT techniques", "risk": "medium"},
                    "3": {"text": "Aggressive: All available legal methods", "risk": "high"}
                }
            }
        }
    
    def start_questionnaire(self) -> Dict:
        """Start the comprehensive questionnaire process"""
        print("Advanced OSINT Intelligence System")
        print("AI-Powered Strategic Configuration")
        print("=" * 50)
        print("This intelligent questionnaire will optimize your search strategy")
        print("for maximum effectiveness and relevance.")
        print()
        
        # Initialize progress tracking
        total_questions = len(self.questions_db) + 5  # Base + estimated follow-ups
        progress = ProgressIndicator(total_questions)
        
        # Core questions
        context = self._ask_context_question()
        progress.update()
        
        industry = self._ask_industry_question()
        progress.update()
        
        target_audience = self._ask_target_audience_question()
        progress.update()
        
        geographic_info = self._ask_geographic_question()
        progress.update()
        
        urgency_info = self._ask_urgency_question()
        progress.update()
        
        data_priorities = self._ask_data_priorities_question()
        progress.update()
        
        # Context-specific follow-up questions
        context_responses = self._ask_context_specific_questions(context)
        
        # Advanced configuration
        advanced_responses = self._ask_advanced_questions()
        
        # Create comprehensive profile
        profile = self._create_search_profile(
            context, industry, target_audience, geographic_info,
            urgency_info, data_priorities, context_responses, advanced_responses
        )
        
        # Generate strategy
        strategy = self._generate_search_strategy(profile)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(profile, strategy)
        
        print("\n" + "=" * 60)
        print("STRATEGIC CONFIGURATION COMPLETE")
        print("=" * 60)
        
        self._display_profile_summary(profile, strategy)
        
        return {
            "profile": profile,
            "strategy": strategy,
            "recommendations": recommendations,
            "estimated_time": self._estimate_processing_time(strategy),
            "confidence_score": self._calculate_confidence_score(profile)
        }
    
    def _ask_context_question(self) -> SearchContext:
        """Ask about research context with smart follow-ups"""
        question_data = self.questions_db["context_identification"]
        
        print(f"\nQuestion 1: {question_data['question']}")
        print("-" * 50)
        
        for key, option in question_data["options"].items():
            print(f"{key}. {option['text']}")
        
        while True:
            choice = input(f"\nSelect option (1-{len(question_data['options'])}): ").strip()
            if choice in question_data["options"]:
                selected = question_data["options"][choice]
                self.responses["context"] = selected
                
                # Smart follow-up based on selection
                if choice in ["1", "2", "3"]:  # Business contexts
                    print(f"\nGreat choice! {selected['text']} is highly effective for ROI-focused intelligence.")
                elif choice in ["4", "5"]:  # Research contexts
                    print(f"\nExcellent! {selected['text']} requires comprehensive data analysis.")
                
                return selected["context"]
            
            print(f"Please select a number between 1 and {len(question_data['options'])}")
    
    def _ask_industry_question(self) -> Optional[IndustryType]:
        """Ask about industry with dynamic insights"""
        question_data = self.questions_db["industry_identification"]
        
        print(f"\nQuestion 2: {question_data['question']}")
        print("-" * 50)
        
        for key, option in question_data["options"].items():
            print(f"{key}. {option['text']}")
        
        while True:
            choice = input(f"\nSelect option (1-{len(question_data['options'])}): ").strip()
            if choice in question_data["options"]:
                selected = question_data["options"][choice]
                self.responses["industry"] = selected
                
                # Industry-specific insights
                industry_insights = {
                    "1": "Technology sector: High digital footprint, strong LinkedIn presence expected",
                    "2": "Healthcare: Regulatory compliance focus, professional networking important",
                    "3": "Finance: Risk-sensitive, comprehensive due diligence recommended",
                    "12": "Government: Public records available, transparency requirements"
                }
                
                if choice in industry_insights:
                    print(f"\nIndustry insight: {industry_insights[choice]}")
                
                return selected.get("industry")
            
            print(f"Please select a number between 1 and {len(question_data['options'])}")
    
    def _ask_target_audience_question(self) -> TargetAudienceType:
        """Ask about target audience with strategic guidance"""
        question_data = self.questions_db["target_audience"]
        
        print(f"\nQuestion 3: {question_data['question']}")
        print("-" * 50)
        
        for key, option in question_data["options"].items():
            print(f"{key}. {option['text']}")
        
        while True:
            choice = input(f"\nSelect option (1-{len(question_data['options'])}): ").strip()
            if choice in question_data["options"]:
                selected = question_data["options"][choice]
                self.responses["target_audience"] = selected
                
                # Audience-specific strategy hints
                audience_strategies = {
                    "1": "SMB Focus: Direct decision makers, cost-conscious, faster decisions",
                    "2": "Enterprise: Complex buying process, multiple stakeholders, formal procurement",
                    "3": "B2C: Consumer behavior patterns, social media heavy, review-driven",
                    "4": "Government: Formal processes, public transparency, budget cycles"
                }
                
                if choice in audience_strategies:
                    print(f"\nStrategy insight: {audience_strategies[choice]}")
                
                return selected["audience"]
            
            print(f"Please select a number between 1 and {len(question_data['options'])}")
    
    def _ask_geographic_question(self) -> Dict:
        """Ask about geographic scope with location validation"""
        question_data = self.questions_db["geographic_scope"]
        
        print(f"\nQuestion 4: {question_data['question']}")
        print("-" * 50)
        
        for key, option in question_data["options"].items():
            print(f"{key}. {option['text']}")
        
        while True:
            choice = input(f"\nSelect option (1-{len(question_data['options'])}): ").strip()
            if choice in question_data["options"]:
                selected = question_data["options"][choice]
                
                # Get specific locations
                print(f"\n{question_data['follow_up_input']}")
                locations_input = input("Locations: ").strip()
                
                # Parse and validate locations
                locations = [loc.strip() for loc in locations_input.split(',') if loc.strip()]
                
                geographic_info = {
                    "scope": selected["scope"],
                    "locations": locations,
                    "scope_text": selected["text"]
                }
                
                self.responses["geographic"] = geographic_info
                
                # Geographic insights
                if locations:
                    print(f"\nGeographic focus confirmed: {', '.join(locations)}")
                    if selected["scope"] == "city":
                        print("City-level targeting: Expect detailed local business data")
                    elif selected["scope"] == "global":
                        print("Global scope: Comprehensive but may require longer processing time")
                
                return geographic_info
            
            print(f"Please select a number between 1 and {len(question_data['options'])}")
    
    def _ask_urgency_question(self) -> Dict:
        """Ask about timeline with resource allocation guidance"""
        question_data = self.questions_db["urgency_assessment"]
        
        print(f"\nQuestion 5: {question_data['question']}")
        print("-" * 50)
        
        for key, option in question_data["options"].items():
            print(f"{key}. {option['text']}")
        
        while True:
            choice = input(f"\nSelect option (1-{len(question_data['options'])}): ").strip()
            if choice in question_data["options"]:
                selected = question_data["options"][choice]
                self.responses["urgency"] = selected
                
                # Timeline-based resource allocation
                time_estimates = {
                    "1": "Quick scan: 5-15 minutes, essential data only",
                    "2": "Standard research: 15-45 minutes, good coverage",
                    "3": "Comprehensive analysis: 30-90 minutes, thorough investigation",
                    "4": "Deep research: 1-3 hours, maximum depth and accuracy"
                }
                
                if choice in time_estimates:
                    print(f"\nTime estimate: {time_estimates[choice]}")
                
                return {
                    "urgency": selected["urgency"],
                    "search_depth": selected["search_depth"],
                    "time_estimate": time_estimates.get(choice, "Variable")
                }
            
            print(f"Please select a number between 1 and {len(question_data['options'])}")
    
    def _ask_data_priorities_question(self) -> List[str]:
        """Ask about data priorities with intelligent suggestions"""
        question_data = self.questions_db["data_priorities"]
        
        print(f"\nQuestion 6: {question_data['question']}")
        print("-" * 50)
        print(f"(Select up to {question_data['max_selections']} options)")
        print()
        
        for key, option in question_data["options"].items():
            print(f"{key}. {option['text']}")
        
        # Smart suggestions based on previous answers
        context = self.responses.get("context", {}).get("context")
        suggestions = self._get_priority_suggestions(context)
        if suggestions:
            print(f"\nSuggested priorities for {context.value if context else 'your context'}: {', '.join(suggestions)}")
        
        while True:
            choices_input = input(f"\nEnter your choices (e.g., 1,3,5): ").strip()
            
            if not choices_input:
                print("Please select at least one data priority")
                continue
            
            try:
                choices = [choice.strip() for choice in choices_input.split(',')]
                
                # Validate choices
                valid_choices = []
                for choice in choices:
                    if choice in question_data["options"]:
                        valid_choices.append(choice)
                    else:
                        print(f"Invalid choice: {choice}")
                
                if not valid_choices:
                    print("No valid choices selected")
                    continue
                
                if len(valid_choices) > question_data["max_selections"]:
                    print(f"Too many selections. Maximum {question_data['max_selections']} allowed.")
                    continue
                
                # Build priority list
                priorities = []
                for choice in valid_choices:
                    option = question_data["options"][choice]
                    priorities.append(option["priority"])
                
                self.responses["data_priorities"] = priorities
                
                print(f"\nSelected priorities: {', '.join(priorities)}")
                return priorities
                
            except Exception as e:
                print("Invalid input format. Please use comma-separated numbers (e.g., 1,3,5)")
    
    def _get_priority_suggestions(self, context: Optional[SearchContext]) -> List[str]:
        """Get intelligent priority suggestions based on context"""
        if not context:
            return []
        
        suggestions_map = {
            SearchContext.LEAD_GENERATION: ["1", "2", "3"],  # Contact info, decision makers, financial data
            SearchContext.RECRUITMENT: ["2", "11", "5"],     # Decision makers, hiring data, social media
            SearchContext.COMPETITOR_ANALYSIS: ["8", "7", "4"], # Competitive intel, news, technology
            SearchContext.MARKET_RESEARCH: ["3", "6", "7"],  # Financial data, reputation, news
            SearchContext.SECURITY_ASSESSMENT: ["4", "10", "1"], # Technology, locations, contact info
            SearchContext.INVESTMENT_RESEARCH: ["3", "2", "9"]   # Financial data, personnel, relationships
        }
        
        return suggestions_map.get(context, [])
    
    def _ask_context_specific_questions(self, context: SearchContext) -> Dict:
        """Ask context-specific follow-up questions"""
        if context not in self.context_specific_questions:
            return {}
        
        print(f"\nContext-Specific Questions for {context.value.replace('_', ' ').title()}")
        print("=" * 50)
        
        responses = {}
        questions = self.context_specific_questions[context]
        
        for i, question in enumerate(questions, 1):
            print(f"\nFollow-up {i}: {question['question']}")
            print("-" * 30)
            
            if question["type"] == "single_choice":
                for key, option in question["options"].items():
                    print(f"{key}. {option['text']}")
                
                while True:
                    choice = input(f"\nSelect option (1-{len(question['options'])}): ").strip()
                    if choice in question["options"]:
                        responses[question["id"]] = question["options"][choice]
                        break
                    print(f"Please select a number between 1 and {len(question['options'])}")
            
            elif question["type"] == "multiple_choice":
                for key, option in question["options"].items():
                    print(f"{key}. {option['text']}")
                
                choices_input = input("\nEnter your choices (e.g., 1,3,5): ").strip()
                if choices_input:
                    choices = [choice.strip() for choice in choices_input.split(',')]
                    selected_options = []
                    for choice in choices:
                        if choice in question["options"]:
                            selected_options.append(question["options"][choice])
                    responses[question["id"]] = selected_options
            
            elif question["type"] == "text_input":
                placeholder = question.get("placeholder", "")
                user_input = input(f"\nYour answer {placeholder}: ").strip()
                if user_input:
                    responses[question["id"]] = {"text": user_input}
        
        return responses
    
    def _ask_advanced_questions(self) -> Dict:
        """Ask advanced configuration questions"""
        print(f"\nAdvanced Configuration")
        print("=" * 30)
        print("Final optimization questions for expert users")
        
        responses = {}
        
        for question_id, question_data in self.advanced_questions.items():
            print(f"\n{question_data['question']}")
            print("-" * 25)
            
            for key, option in question_data["options"].items():
                print(f"{key}. {option['text']}")
            
            while True:
                choice = input(f"\nSelect option (1-{len(question_data['options'])}): ").strip()
                if choice in question_data["options"]:
                    responses[question_id] = question_data["options"][choice]
                    break
                print(f"Please select a number between 1 and {len(question_data['options'])}")
        
        return responses
    
    def _create_search_profile(self, context, industry, target_audience, geographic_info, 
                             urgency_info, data_priorities, context_responses, advanced_responses) -> SearchProfile:
        """Create comprehensive search profile"""
        
        # Extract context-specific data
        budget_range = "unknown"
        company_size_focus = "mixed"
        decision_maker_levels = []
        
        if "budget_analysis" in context_responses:
            budget_range = context_responses["budget_analysis"].get("budget", "unknown")
        
        if "decision_maker_focus" in context_responses:
            decision_maker_levels = [dm.get("role", "") for dm in context_responses["decision_maker_focus"]]
        
        # Advanced settings
        search_depth = urgency_info["search_depth"]
        risk_tolerance = advanced_responses.get("risk_tolerance", {}).get("risk", "medium")
        
        # Determine focus areas
        technology_focus = "technology_stack" in data_priorities
        social_media_focus = "social_media" in data_priorities
        financial_data = "financial_data" in data_priorities
        competitive_analysis = context == SearchContext.COMPETITOR_ANALYSIS
        historical_data = search_depth in ["comprehensive"]
        
        profile = SearchProfile(
            context=context,
            industry=industry,
            target_audience=target_audience,
            geographic_scope=geographic_info["scope"],
            geographic_regions=geographic_info["locations"],
            urgency=urgency_info["urgency"],
            data_priorities=data_priorities,
            budget_range=budget_range,
            company_size_focus=company_size_focus,
            decision_maker_levels=decision_maker_levels,
            competitive_analysis=competitive_analysis,
            technology_focus=technology_focus,
            historical_data=historical_data,
            social_media_focus=social_media_focus,
            financial_data=financial_data,
            custom_requirements=[],
            search_depth=search_depth,
            risk_tolerance=risk_tolerance
        )
        
        return profile
    
    def _generate_search_strategy(self, profile: SearchProfile) -> Dict:
        """Generate optimized search strategy based on profile"""
        strategy = {
            "search_methods": [],
            "data_sources": [],
            "extraction_priorities": [],
            "analysis_depth": profile.search_depth,
            "geographic_filters": profile.geographic_regions,
            "industry_keywords": self._get_industry_keywords(profile.industry),
            "time_allocation": {},
            "risk_level": profile.risk_tolerance,
            "parallel_processing": True,
            "validation_level": "standard"
        }
        
        # Determine search methods based on context
        if profile.context == SearchContext.LEAD_GENERATION:
            strategy["search_methods"] = ["google_dorking", "linkedin_mining", "business_directories", "social_media"]
            strategy["data_sources"] = ["search_engines", "professional_networks", "business_listings"]
        
        elif profile.context == SearchContext.RECRUITMENT:
            strategy["search_methods"] = ["linkedin_comprehensive", "job_boards", "professional_networks", "github_analysis"]
            strategy["data_sources"] = ["linkedin", "indeed", "glassdoor", "github"]
        
        elif profile.context == SearchContext.COMPETITOR_ANALYSIS:
            strategy["search_methods"] = ["company_analysis", "news_monitoring", "technology_analysis", "social_listening"]
            strategy["data_sources"] = ["company_websites", "news_sources", "social_media", "tech_databases"]
        
        elif profile.context == SearchContext.MARKET_RESEARCH:
            strategy["search_methods"] = ["industry_analysis", "trend_monitoring", "financial_research", "consumer_sentiment"]
            strategy["data_sources"] = ["industry_reports", "financial_databases", "social_media", "review_platforms"]
        
        # Add data source priorities based on profile
        if profile.social_media_focus:
            strategy["data_sources"].extend(["twitter", "facebook", "instagram", "youtube"])
        
        if profile.technology_focus:
            strategy["data_sources"].extend(["github", "stackoverflow", "tech_blogs"])
        
        if profile.financial_data:
            strategy["data_sources"].extend(["crunchbase", "bloomberg", "financial_filings"])
        
        # Set extraction priorities
        strategy["extraction_priorities"] = profile.data_priorities
        
        # Time allocation based on urgency
        if profile.urgency == UrgencyLevel.IMMEDIATE:
            strategy["time_allocation"] = {"quick_scan": 0.7, "analysis": 0.3}
            strategy["parallel_processing"] = True
        elif profile.urgency == UrgencyLevel.NO_RUSH:
            strategy["time_allocation"] = {"data_collection": 0.6, "analysis": 0.4}
            strategy["validation_level"] = "comprehensive"
        
        return strategy
    
    def _get_industry_keywords(self, industry: Optional[IndustryType]) -> List[str]:
        """Get industry-specific keywords for search optimization"""
        if not industry:
            return []
        
        keywords_map = {
            IndustryType.TECHNOLOGY: ["software", "tech", "IT", "digital", "platform", "SaaS", "cloud", "AI"],
            IndustryType.HEALTHCARE: ["medical", "health", "clinic", "hospital", "pharmaceutical", "healthcare", "biotech"],
            IndustryType.FINANCE: ["financial", "bank", "investment", "insurance", "fintech", "payments", "trading"],
            IndustryType.RETAIL: ["retail", "store", "ecommerce", "shopping", "consumer", "merchandise"],
            IndustryType.HOSPITALITY: ["hotel", "restaurant", "tourism", "travel", "hospitality", "leisure"],
            IndustryType.MANUFACTURING: ["manufacturing", "industrial", "production", "factory", "supply chain"],
            IndustryType.EDUCATION: ["education", "school", "university", "training", "learning", "academic"],
            IndustryType.REAL_ESTATE: ["real estate", "property", "construction", "development", "housing"],
            IndustryType.CONSULTING: ["consulting", "advisory", "professional services", "strategy"],
            IndustryType.LOGISTICS: ["logistics", "shipping", "transportation", "delivery", "supply chain"],
            IndustryType.ENERGY: ["energy", "oil", "gas", "renewable", "utilities", "power"],
            IndustryType.GOVERNMENT: ["government", "public sector", "municipal", "federal", "agency"]
        }
        
        return keywords_map.get(industry, [])
    
    def _generate_recommendations(self, profile: SearchProfile, strategy: Dict) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Context-specific recommendations
        if profile.context == SearchContext.LEAD_GENERATION:
            recommendations.extend([
                "Focus on decision maker contact information and budget indicators",
                "Look for recent growth signals (hiring, expansion, funding)",
                "Monitor technology adoption patterns for timing opportunities"
            ])
        
        elif profile.context == SearchContext.RECRUITMENT:
            recommendations.extend([
                "Analyze current employment satisfaction indicators",
                "Search for skill-specific keywords and recent certifications",
                "Monitor professional development activities and career progression"
            ])
        
        elif profile.context == SearchContext.COMPETITOR_ANALYSIS:
            recommendations.extend([
                "Monitor recent news and press releases for strategic insights",
                "Analyze pricing pages and service offerings for positioning",
                "Track executive movements and strategic partnerships"
            ])
        
        # Industry-specific recommendations
        if profile.industry == IndustryType.TECHNOLOGY:
            recommendations.extend([
                "Check GitHub profiles and technical contributions",
                "Analyze technology stack and development practices",
                "Monitor developer community engagement"
            ])
        
        elif profile.industry == IndustryType.HEALTHCARE:
            recommendations.extend([
                "Review regulatory compliance and certifications",
                "Check medical publication and research activities",
                "Analyze patient satisfaction and quality metrics"
            ])
        
        # Geographic recommendations
        if profile.geographic_scope == "city":
            recommendations.append("Include local business directories and chamber of commerce data")
        elif profile.geographic_scope == "global":
            recommendations.append("Use multiple regional search engines and local language sources")
        
        # Urgency-based recommendations
        if profile.urgency == UrgencyLevel.IMMEDIATE:
            recommendations.append("Prioritize high-confidence sources and real-time data")
        elif profile.urgency == UrgencyLevel.NO_RUSH:
            recommendations.append("Enable comprehensive validation and historical analysis")
        
        return recommendations
    
    def _estimate_processing_time(self, strategy: Dict) -> str:
        """Estimate processing time based on strategy complexity"""
        base_time = 15  # minutes
        
        # Add time based on search methods
        method_multipliers = {
            "google_dorking": 1.2,
            "linkedin_comprehensive": 2.0,
            "social_media": 1.5,
            "technology_analysis": 1.8,
            "financial_research": 2.2
        }
        
        total_multiplier = 1.0
        for method in strategy.get("search_methods", []):
            total_multiplier += method_multipliers.get(method, 0.5)
        
        # Add time based on data sources
        source_count = len(strategy.get("data_sources", []))
        source_multiplier = 1 + (source_count * 0.1)
        
        # Calculate final estimate
        estimated_minutes = int(base_time * total_multiplier * source_multiplier)
        
        if estimated_minutes < 30:
            return f"{estimated_minutes} minutes"
        else:
            hours = estimated_minutes // 60
            minutes = estimated_minutes % 60
            return f"{hours}h {minutes}m"
    
    def _calculate_confidence_score(self, profile: SearchProfile) -> float:
        """Calculate confidence score for the configuration"""
        score = 0.7  # Base confidence
        
        # Add confidence based on specificity
        if profile.industry:
            score += 0.1
        
        if profile.geographic_regions:
            score += 0.1
        
        if len(profile.data_priorities) >= 3:
            score += 0.1
        
        # Industry-specific confidence adjustments
        high_confidence_industries = [IndustryType.TECHNOLOGY, IndustryType.FINANCE]
        if profile.industry in high_confidence_industries:
            score += 0.05
        
        # Context-specific confidence
        high_confidence_contexts = [SearchContext.LEAD_GENERATION, SearchContext.RECRUITMENT]
        if profile.context in high_confidence_contexts:
            score += 0.05
        
        return min(score, 1.0)
    
    def _display_profile_summary(self, profile: SearchProfile, strategy: Dict):
        """Display comprehensive profile summary"""
        print(f"Context: {profile.context.value.replace('_', ' ').title()}")
        print(f"Industry: {profile.industry.value.title() if profile.industry else 'Mixed Industries'}")
        print(f"Target Audience: {profile.target_audience.value.replace('_', ' ').title()}")
        print(f"Geographic Scope: {profile.geographic_scope.title()}")
        if profile.geographic_regions:
            print(f"Regions: {', '.join(profile.geographic_regions)}")
        print(f"Urgency: {profile.urgency.value.replace('_', ' ').title()}")
        print(f"Search Depth: {profile.search_depth.title()}")
        print(f"Data Priorities ({len(profile.data_priorities)}): {', '.join(profile.data_priorities[:3])}{'...' if len(profile.data_priorities) > 3 else ''}")
        print(f"Search Methods: {', '.join(strategy['search_methods'][:3])}{'...' if len(strategy['search_methods']) > 3 else ''}")
        print(f"Risk Tolerance: {profile.risk_tolerance.title()}")
    
    def export_profile(self, profile: SearchProfile, filename: str = None) -> str:
        """Export profile to JSON file"""
        if not filename:
            timestamp = int(time.time())
            filename = f"search_profile_{profile.context.value}_{timestamp}.json"
        
        profile_data = asdict(profile)
        
        # Convert enums to strings for JSON serialization
        profile_data["context"] = profile.context.value
        if profile.industry:
            profile_data["industry"] = profile.industry.value
        profile_data["target_audience"] = profile.target_audience.value
        profile_data["urgency"] = profile.urgency.value
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
        
        return filename