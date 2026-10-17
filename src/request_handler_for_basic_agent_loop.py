from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Tuple
from src.storage import Storage
from src.agent import SimpleAgent

@dataclass
class FeatureRequest:
    id: str
    description: str
    client: str
    project: str
    timestamp: str
    phase: str
    confidence: str

class RequestHandler:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.agent = SimpleAgent()  # Using the Agent instead of raw detector

    def validate_description(self, description: str) -> Tuple[bool, str]:
        """Validate description is between 10 and 500 characters."""
        desc_len = len(description.strip())
        if desc_len < 10:
            return False, "Description is too short (minimum 10 characters required)."
        if desc_len > 500:
            return False, "Description is too long (maximum 500 characters allowed)."
        return True, ""

    def add_request(self, description: str, client: str, project: str) -> Tuple[bool, str]:
        """Validate input, run the Agent Loop (Observe-Reason-Act), and persist the request."""
        is_valid, err_msg = self.validate_description(description)
        if not is_valid:
            return False, err_msg

        print("\n🤖 [Agent Loop Running] Observing, Reasoning, and Acting...")
        
        # Run through the Agent loop
        agent_result = self.agent.process_request(description, client, project)

        existing_requests = self.storage.load_data()
        new_id = str(len(existing_requests) + 1)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        req = FeatureRequest(
            id=new_id,
            description=description.strip(),
            client=client.strip() or "Unknown Client",
            project=project.strip() or "General Project",
            timestamp=timestamp,
            phase=agent_result["phase"],
            confidence=agent_result["confidence"]
        )

        self.storage.append_record(asdict(req))
        
        # Return success message along with agent's reasoning summary
        return True, f"Successfully created request #{new_id}!\n   ↳ {agent_result['summary']}"

    def get_all_requests(self) -> list:
        return self.storage.load_data()