import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Callable
import asyncio
import logging
from datetime import datetime

from ..core.questionnaire_system import QuestionnaireSystem, Question, Answer

logger = logging.getLogger(__name__)

class QuestionnaireInterface:
    """Graphical interface for questionnaire system"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Advanced AI-Powered Questionnaire System")
        self.root.geometry("800x600")
        
        self.questionnaire = QuestionnaireSystem()
        self.current_questions: List[Question] = []
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup user interface components"""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Context selection
        self.context_frame = ttk.LabelFrame(self.main_frame, text="Context", padding="5")
        self.context_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.context_var = tk.StringVar()
        contexts = ['business_intelligence', 'lead_generation']
        self.context_combo = ttk.Combobox(
            self.context_frame, 
            textvariable=self.context_var,
            values=contexts,
            state='readonly'
        )
        self.context_combo.grid(row=0, column=0, padx=5)
        self.context_combo.set(contexts[0])
        
        # Target type selection
        self.target_frame = ttk.LabelFrame(self.main_frame, text="Target Type", padding="5")
        self.target_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.target_var = tk.StringVar()
        targets = ['company', 'person', 'domain']
        self.target_combo = ttk.Combobox(
            self.target_frame,
            textvariable=self.target_var,
            values=targets,
            state='readonly'
        )
        self.target_combo.grid(row=0, column=0, padx=5)
        self.target_combo.set(targets[0])
        
        # Start button
        self.start_btn = ttk.Button(
            self.main_frame,
            text="Start Questionnaire",
            command=self._start_questionnaire
        )
        self.start_btn.grid(row=2, column=0, pady=10)
        
        # Questions area
        self.questions_frame = ttk.LabelFrame(self.main_frame, text="Questions", padding="5")
        self.questions_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(
            self.main_frame,
            textvariable=self.status_var
        )
        self.status_label.grid(row=5, column=0, pady=5)
        
    def _start_questionnaire(self):
        """Start new questionnaire session"""
        context = self.context_var.get()
        target_type = self.target_var.get()
        
        # Clear previous questions
        for widget in self.questions_frame.winfo_children():
            widget.destroy()
        
        # Initialize questionnaire
        self.current_questions = self.questionnaire.initialize_questionnaire(context, target_type)
        
        # Display first questions
        self._display_questions(self.current_questions[:3])  # Show first 3 questions
        
        self.status_var.set("Questionnaire started")
        self.progress_var.set(0)
        
    def _display_questions(self, questions: List[Question]):
        """Display questions in UI"""
        for idx, question in enumerate(questions):
            frame = ttk.Frame(self.questions_frame)
            frame.grid(row=idx, column=0, sticky=(tk.W, tk.E), pady=5)
            
            label = ttk.Label(frame, text=question.text)
            label.grid(row=0, column=0, sticky=tk.W)
            
            answer_var = tk.StringVar()
            entry = ttk.Entry(frame, textvariable=answer_var)
            entry.grid(row=1, column=0, sticky=(tk.W, tk.E))
            
            submit_btn = ttk.Button(
                frame,
                text="Submit",
                command=lambda q=question, v=answer_var: self._submit_answer(q, v)
            )
            submit_btn.grid(row=1, column=1, padx=5)
    
    def _submit_answer(self, question: Question, answer_var: tk.StringVar):
        """Submit answer for a question"""
        answer_value = answer_var.get()
        
        if not answer_value:
            messagebox.showwarning("Warning", "Please provide an answer")
            return
        
        # Process answer
        result = self.questionnaire.process_answer(question.id, answer_value)
        
        if not result['status'] == 'success':
            messagebox.showerror("Error", result.get('error', 'Invalid answer'))
            return
        
        # Update progress
        progress = result['session_progress']
        self.progress_var.set(progress['percentage'])
        self.status_var.set(f"Completed: {progress['answered']}/{progress['total']}")
        
        # Show next questions if available
        if result['next_questions']:
            self._display_questions(result['next_questions'][:3])
        else:
            self._show_summary()
    
    def _show_summary(self):
        """Show questionnaire summary"""
        summary = self.questionnaire.get_questionnaire_summary()
        
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Questionnaire Summary")
        summary_window.geometry("600x400")
        
        # Summary text
        text = tk.Text(summary_window, wrap=tk.WORD, padx=10, pady=10)
        text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add summary content
        text.insert(tk.END, "=== Questionnaire Summary ===\n\n")
        
        # Session info
        session = summary['session_info']
        text.insert(tk.END, f"Context: {session['context']}\n")
        text.insert(tk.END, f"Target Type: {session['target_type']}\n")
        text.insert(tk.END, f"Duration: {session['duration']} seconds\n\n")
        
        # Progress
        progress = summary['progress']
        text.insert(tk.END, f"Completion: {progress['percentage']:.1f}%\n")
        text.insert(tk.END, f"Questions Answered: {progress['answered']}/{progress['total']}\n\n")
        
        # Confidence metrics
        confidence = summary['confidence_metrics']
        text.insert(tk.END, f"Average Confidence: {confidence['average_confidence']:.2f}\n")
        text.insert(tk.END, f"High Confidence Answers: {confidence['high_confidence_answers']}\n\n")
        
        # Make text readonly
        text.configure(state='disabled')
        
        # Close button
        ttk.Button(
            summary_window,
            text="Close",
            command=summary_window.destroy
        ).grid(row=1, column=0, pady=10)
    
    def run(self):
        """Start the UI"""
        self.root.mainloop()

def main():
    """Main entry point"""
    logging.basicConfig(level=logging.INFO)
    
    interface = QuestionnaireInterface()
    interface.run()

if __name__ == "__main__":
    main()
