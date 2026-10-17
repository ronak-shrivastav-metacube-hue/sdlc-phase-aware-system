from typing import Dict, Any, List
from src.llm_detector import LLMPhaseDetector

class SimpleAgent:
    def __init__(self):
        self.detector = LLMPhaseDetector()
        # Simple memory to remember the last 2 interactions
        self.memory: List[Dict[str, Any]] = []

    def observe(self, user_input: str, client: str, project: str) -> Dict[str, Any]:
        """Step 1: Collect and structure basic information about the request."""
        observation = {
            "description": user_input.strip(),
            "client": client.strip() or "Unknown Client",
            "project": project.strip() or "General Project"
        }
        return observation

    def reason(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Use the phase detector and context memory to analyze the request."""
        description = observation["description"]
        
        # Call the LLM phase detector
        classification = self.detector.detect_phase(description)
        
        # Generate phase-specific advice or reasoning
        phase = classification["phase"]
        advice = self._get_phase_advice(phase)

        reasoning_result = {
            "phase": phase,
            "confidence": classification["confidence"],
            "advice": advice,
            "recent_history_count": len(self.memory)
        }
        return reasoning_result

    def act(self, observation: Dict[str, Any], reasoning: Dict[str, Any]) -> str:
        """Step 3: Generate a simple summary response and update memory."""
        phase = reasoning["phase"]
        confidence = reasoning["confidence"]
        advice = reasoning["advice"]

        response_summary = (
            f"Analyzed request for project '{observation['project']}' "
            f"(Client: {observation['client']}). "
            f"Classified into phase: **{phase.upper()}** (Confidence: {confidence}). "
            f"Recommendation: {advice}"
        )

        # Save to memory (keeping only the last 2 interactions)
        interaction = {
            "observation": observation,
            "reasoning": reasoning,
            "action_summary": response_summary
        }
        self.memory.append(interaction)
        if len(self.memory) > 2:
            self.memory.pop(0)  # Remove the oldest interaction to keep last 2

        return response_summary

    def process_request(self, description: str, client: str, project: str) -> Dict[str, Any]:
        """The main Agent Loop: Observe -> Reason -> Act."""
        # 1. Observe
        obs = self.observe(description, client, project)
        
        # 2. Reason
        res = self.reason(obs)
        
        # 3. Act
        action_result = self.act(obs, res)

        return {
            "phase": res["phase"],
            "confidence": res["confidence"],
            "summary": action_result,
            "memory_context": self.get_memory_context()
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

    def get_memory_context(self) -> List[Dict[str, Any]]:
        """Return the last remembered interactions."""
        return self.memory