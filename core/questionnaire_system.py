from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class Question:
    id: str
    text: str
    category: str
    priority: int
    dependencies: List[str]
    validation_rules: Dict[str, any]
    metadata: Dict[str, any]

@dataclass
class Answer:
    question_id: str
    value: str
    confidence: float
    timestamp: datetime
    metadata: Dict[str, any]

class QuestionnaireSystem:
    """Advanced AI-powered questionnaire system"""
    
    def __init__(self):
        self.questions_bank = {}
        self.current_session = {}
        self.ai_analyzer = None
        
    def initialize_questionnaire(self, context: str, target_type: str) -> List[Question]:
        """Initialize questionnaire based on context"""
        questions = self._generate_questions(context, target_type)
        self.current_session = {
            'context': context,
            'target_type': target_type,
            'start_time': datetime.now(),
            'questions': questions,
            'answers': {},
            'state': 'initialized'
        }
        return questions
    
    def process_answer(self, question_id: str, answer_value: str) -> Dict:
        """Process an answer and determine next questions"""
        if question_id not in self.current_session['questions']:
            raise ValueError(f"Invalid question ID: {question_id}")
        
        # Validate answer
        validation_result = self._validate_answer(question_id, answer_value)
        if not validation_result['valid']:
            return validation_result
        
        # Store answer
        answer = Answer(
            question_id=question_id,
            value=answer_value,
            confidence=validation_result['confidence'],
            timestamp=datetime.now(),
            metadata={'validation': validation_result}
        )
        
        self.current_session['answers'][question_id] = answer
        
        # Determine next questions
        next_questions = self._determine_next_questions(answer)
        
        return {
            'status': 'success',
            'next_questions': next_questions,
            'session_progress': self._calculate_progress()
        }
    
    def _generate_questions(self, context: str, target_type: str) -> List[Question]:
        """Generate context-specific questions"""
        base_questions = self._load_base_questions(context)
        enhanced_questions = self._enhance_questions_with_ai(base_questions, target_type)
        return self._prioritize_questions(enhanced_questions)
    
    def _load_base_questions(self, context: str) -> List[Question]:
        """Load base questions for given context"""
        context_questions = {
            'business_intelligence': [
                Question(
                    id='bi_001',
                    text='What is the target company name?',
                    category='basic_info',
                    priority=1,
                    dependencies=[],
                    validation_rules={'required': True, 'min_length': 2},
                    metadata={'purpose': 'identification'}
                ),
                Question(
                    id='bi_002',
                    text='What is the primary industry sector?',
                    category='business_info',
                    priority=1,
                    dependencies=['bi_001'],
                    validation_rules={'required': True},
                    metadata={'purpose': 'classification'}
                ),
                # Add more business intelligence questions
            ],
            'lead_generation': [
                Question(
                    id='lg_001',
                    text='What is the target market segment?',
                    category='market_info',
                    priority=1,
                    dependencies=[],
                    validation_rules={'required': True},
                    metadata={'purpose': 'targeting'}
                ),
                # Add more lead generation questions
            ]
        }
        
        return context_questions.get(context, [])
    
    def _enhance_questions_with_ai(self, questions: List[Question], target_type: str) -> List[Question]:
        """Enhance questions using AI analysis"""
        # Add AI-generated questions based on context and target
        enhanced = questions.copy()
        
        if target_type == 'company':
            enhanced.extend([
                Question(
                    id='ai_001',
                    text='What are the key technologies used by the company?',
                    category='tech_assessment',
                    priority=2,
                    dependencies=['bi_001'],
                    validation_rules={'required': False},
                    metadata={'ai_generated': True}
                ),
                # Add more AI-generated questions
            ])
        
        return enhanced
    
    def _prioritize_questions(self, questions: List[Question]) -> List[Question]:
        """Prioritize questions based on importance and dependencies"""
        return sorted(questions, key=lambda q: (q.priority, len(q.dependencies)))
    
    def _validate_answer(self, question_id: str, answer_value: str) -> Dict:
        """Validate answer against rules"""
        question = self.current_session['questions'][question_id]
        rules = question.validation_rules
        
        # Basic validation
        if rules.get('required', False) and not answer_value:
            return {
                'valid': False,
                'confidence': 0.0,
                'error': 'Answer is required'
            }
        
        if rules.get('min_length') and len(answer_value) < rules['min_length']:
            return {
                'valid': False,
                'confidence': 0.0,
                'error': f"Answer must be at least {rules['min_length']} characters"
            }
        
        # Calculate confidence
        confidence = self._calculate_answer_confidence(answer_value, question)
        
        return {
            'valid': True,
            'confidence': confidence,
            'validation_details': {'rules_passed': list(rules.keys())}
        }
    
    def _calculate_answer_confidence(self, answer: str, question: Question) -> float:
        """Calculate confidence score for an answer"""
        # Base confidence
        confidence = 0.7
        
        # Adjust based on answer characteristics
        if len(answer) > 50:  # Detailed answer
            confidence += 0.1
        
        if question.category == 'basic_info':  # Higher confidence for basic info
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _determine_next_questions(self, answer: Answer) -> List[Question]:
        """Determine next relevant questions based on answer"""
        all_questions = self.current_session['questions']
        answered_questions = set(self.current_session['answers'].keys())
        
        # Find questions whose dependencies are satisfied
        available_questions = []
        for question in all_questions.values():
            if question.id not in answered_questions and \
               all(dep in answered_questions for dep in question.dependencies):
                available_questions.append(question)
        
        return self._prioritize_questions(available_questions)
    
    def _calculate_progress(self) -> Dict:
        """Calculate questionnaire progress"""
        total_questions = len(self.current_session['questions'])
        answered_questions = len(self.current_session['answers'])
        
        return {
            'answered': answered_questions,
            'total': total_questions,
            'percentage': (answered_questions / total_questions) * 100 if total_questions > 0 else 0,
            'remaining': total_questions - answered_questions
        }
    
    def get_questionnaire_summary(self) -> Dict:
        """Get summary of questionnaire session"""
        if not self.current_session:
            return {'status': 'No active session'}
        
        progress = self._calculate_progress()
        
        return {
            'session_info': {
                'context': self.current_session['context'],
                'target_type': self.current_session['target_type'],
                'start_time': self.current_session['start_time'],
                'duration': (datetime.now() - self.current_session['start_time']).seconds
            },
            'progress': progress,
            'answers_summary': self._generate_answers_summary(),
            'confidence_metrics': self._calculate_confidence_metrics()
        }
    
    def _generate_answers_summary(self) -> Dict:
        """Generate summary of answered questions"""
        summary = {}
        
        for question_id, answer in self.current_session['answers'].items():
            question = self.current_session['questions'][question_id]
            summary[question.category] = summary.get(question.category, [])
            summary[question.category].append({
                'question': question.text,
                'answer': answer.value,
                'confidence': answer.confidence
            })
        
        return summary
    
    def _calculate_confidence_metrics(self) -> Dict:
        """Calculate confidence metrics for answers"""
        if not self.current_session['answers']:
            return {'average_confidence': 0.0, 'high_confidence_answers': 0}
        
        confidences = [ans.confidence for ans in self.current_session['answers'].values()]
        avg_confidence = sum(confidences) / len(confidences)
        high_confidence = sum(1 for c in confidences if c >= 0.8)
        
        return {
            'average_confidence': avg_confidence,
            'high_confidence_answers': high_confidence,
            'confidence_distribution': {
                'high': sum(1 for c in confidences if c >= 0.8),
                'medium': sum(1 for c in confidences if 0.5 <= c < 0.8),
                'low': sum(1 for c in confidences if c < 0.5)
            }
        }

# Initialize logging
logging.basicConfig(level=logging.INFO)
