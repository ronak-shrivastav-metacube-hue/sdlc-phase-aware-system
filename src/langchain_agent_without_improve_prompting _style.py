import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_classic.memory import ConversationBufferMemory  # <-- Updated import
from dotenv import load_dotenv

load_dotenv()

class LangChainAgent:
    def __init__(self):
        # Initialize LangChain's ChatOpenAI wrapper
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
        
        # Setup LangChain ConversationBufferMemory (Milestone 5 requirement)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Setup LangChain PromptTemplate for structured prompt management
        self.prompt_template = PromptTemplate(
            input_variables=["description"],
            template="""Classify this feature request into exactly one SDLC phase:

"{description}"

Phases: requirements, design, implementation, testing, deployment

Respond with just the phase name in lowercase:"""
        )

    def process_request(self, description: str, client: str, project: str) -> dict:
        """Process request using LangChain prompt formatting, LLM invocation, and memory storage."""
        valid_phases = ["requirements", "design", "implementation", "testing", "deployment"]
        
        # Format prompt using LangChain PromptTemplate
        formatted_prompt = self.prompt_template.format(description=description)

        try:
            # Invoke the LangChain model
            response = self.llm.invoke(formatted_prompt)
            predicted_phase = response.content.strip().lower()
            
            if predicted_phase in valid_phases:
                confidence = "High"
            else:
                predicted_phase = "implementation"
                confidence = "Medium"

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

        # Save context to LangChain's ConversationBufferMemory
        self.memory.save_context(
            {"input": description},
            {"output": summary}
        )

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
            """Retrieve stored conversation history in a format compatible with main.py."""
            # Load messages from LangChain memory
            memory_vars = self.memory.load_memory_variables({})
            chat_history = memory_vars.get("chat_history", [])
            
            # Convert LangChain message objects into the dictionary structure expected by main.py
            formatted_interactions = []
            # chat_history contains alternating HumanMessage and AIMessage objects
            for i in range(0, len(chat_history) - 1, 2):
                user_msg = chat_history[i].content
                ai_msg = chat_history[i+1].content
                
                interaction = {
                    "observation": {
                        "project": "TomSchool / Current Project", # fallback label
                        "description": user_msg
                    },
                    "reasoning": {
                        "phase": "detected via llm"
                    },
                    "action_summary": ai_msg
                }
                formatted_interactions.append(interaction)
                
            return formatted_interactions[-2:] # Return last 2 interactions