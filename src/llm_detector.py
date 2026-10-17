import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMPhaseDetector:
    def __init__(self):
        # Initialize OpenAI client (it automatically picks up OPENAI_API_KEY from environment)
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)

    def detect_phase(self, description: str) -> dict:
        """
        Classify the feature request description into an SDLC phase using OpenAI.
        Valid phases: requirements, design, implementation, testing, deployment
        """
        valid_phases = ["requirements", "design", "implementation", "testing", "deployment"]
        
        # Fallback if API key is missing or client initialization failed
        if not self.client:
            return {
                "phase": "unknown (API key missing)",
                "confidence": "Low"
            }

        prompt = f"""Classify this feature request into exactly one SDLC phase:

"{description}"

Phases: requirements, design, implementation, testing, deployment

Respond with just the phase name in lowercase:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # or gpt-4o-mini depending on your preference/access
                messages=[
                    {"role": "system", "content": "You are a software engineering assistant that classifies feature requests into SDLC phases accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=10
            )
            
            predicted_phase = response.choices[0].message.content.strip().lower()
            
            # Basic validation of response against known phases
            if predicted_phase in valid_phases:
                confidence = "High"
            else:
                # Try to clean or default if model outputs extra text
                predicted_phase = "implementation"  # safe default fallback
                confidence = "Medium"

            return {
                "phase": predicted_phase,
                "confidence": confidence
            }

        except Exception as e:
            # Error handling for network issues, rate limits, or invalid keys
            print(f"\n[API ERROR]: {str(e)}")
            return {
                "phase": "error (API failure)",
                "confidence": "Low"
            }