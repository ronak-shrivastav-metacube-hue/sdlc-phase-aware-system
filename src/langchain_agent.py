import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class LangChainAgent:
    def __init__(self):
        # Initialize LangChain's ChatOpenAI wrapper with low temperature for consistent classification
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
        
        # Clean local history cache to track recent interactions without import errors
        self.local_history = []
        
        # IMPROVED PROMPT TEMPLATE (Milestone 7) with clear examples and structured format
        self.prompt_template = PromptTemplate(
            input_variables=["description"],
            template="""You are an expert software engineering assistant. Classify the given feature request into exactly one SDLC phase.

Valid Phases & Definitions:
1. requirements - Gathering user stories, feature scoping, and acceptance criteria.
2. design - Planning architecture, wireframes, database schemas, and technical specs.
3. implementation - Writing backend/frontend code, building APIs, and feature development.
4. testing - Running test cases, quality assurance, bug tracking, and validation.
5. deployment - Releasing to production, managing CI/CD pipelines, and monitoring system logs.

Examples:
- "We need a secure user login system" → requirements, High
- "Plan the database tables and entity relationships" → design, High
- "Write the Python code for payment API integration" → implementation, High
- "Test edge cases for checkout and fix bugs" → testing, High
- "Deploy the new build to production server" → deployment, High

Request: "{description}"

Respond strictly in this format: phase_name, confidence (where confidence is High, Medium, or Low)
Example response: implementation, High"""
        )

    def process_request(self, description: str, client: str, project: str) -> dict:
        """Process request using the improved prompt template and parse structured response."""
        valid_phases = ["requirements", "design", "implementation", "testing", "deployment"]
        
        # Format prompt using the improved PromptTemplate
        formatted_prompt = self.prompt_template.format(description=description)

        try:
            # Invoke the LangChain model
            response = self.llm.invoke(formatted_prompt)
            raw_output = response.content.strip()
            
            # Parse structured response (e.g., "implementation, High")
            if "," in raw_output:
                parts = raw_output.split(",")
                predicted_phase = parts[0].strip().lower()
                confidence = parts[1].strip().capitalize()
            else:
                predicted_phase = raw_output.lower()
                confidence = "Medium"
            
            # Validate phase against known list
            if predicted_phase not in valid_phases:
                predicted_phase = "implementation"
                confidence = "Medium"
                
            if confidence not in ["High", "Medium", "Low"]:
                confidence = "High"

        except Exception as e:
            print(f"\n[LangChain API Error]: {str(e)}")
            predicted_phase = "error"
            confidence = "Low"

        advice = self._get_phase_advice(predicted_phase)

        summary = (
            f"Analyzed request for project '{project}' (Client: {client}). "
            f"Classified into phase: **{predicted_phase.upper()}** (Confidence: {confidence}). "
            f"Recommendation: {advice}"
        )

        # Save to local history for CLI option 4
        interaction = {
            "observation": {
                "project": project,
                "description": description
            },
            "reasoning": {
                "phase": predicted_phase,
                "confidence": confidence
            },
            "action_summary": summary
        }
        self.local_history.append(interaction)
        if len(self.local_history) > 2:
            self.local_history.pop(0)  # Keep last 2 interactions

        return {
            "phase": predicted_phase,
            "confidence": confidence,
            "summary": summary
        }

    def _get_phase_advice(self, phase: str) -> str:
        """Provide simple actionable advice based on the detected phase."""
        advice_map = {
            "requirements": "Focus on gathering clear user stories and acceptance criteria before designing.",
            "design": "Create wireframes or technical architecture diagrams and review with stakeholders.",
            "implementation": "Write clean code, follow project style guidelines, and write unit tests.",
            "testing": "Execute test cases, check edge cases, and log bugs thoroughly.",
            "deployment": "Ensure CI/CD pipelines are green, monitor system logs, and prepare release notes."
        }
        return advice_map.get(phase, "Review request details and align with the team.")

    def get_memory_context(self):
        """Retrieve stored conversation history safely."""
        return self.local_history