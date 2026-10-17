from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Tuple
from src.storage import Storage
from src.langchain_agent import LangChainAgent
from src.artifact_generator import ArtifactGenerator  # <-- New Import

@dataclass
class FeatureRequest:
    id: str
    description: str
    client: str
    project: str
    timestamp: str
    phase: str
    confidence: str
    artifact_path: str  # <-- Track saved document path

class RequestHandler:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.agent = LangChainAgent()
        self.artifact_generator = ArtifactGenerator()  # Initialize generator

    def validate_description(self, description: str) -> Tuple[bool, str]:
        """Validate description is between 10 and 500 characters."""
        desc_len = len(description.strip())
        if desc_len < 10:
            return False, "Description is too short (minimum 10 characters required)."
        if desc_len > 500:
            return False, "Description is too long (maximum 500 characters allowed)."
        return True, ""

    def add_request(self, description: str, client: str, project: str) -> Tuple[bool, str]:
        """Validate input, run Agent, generate phase document, and persist the request."""
        is_valid, err_msg = self.validate_description(description)
        if not is_valid:
            return False, err_msg

        print("\n🤖 [Agent & Generator Running] Detecting phase & generating artifact document...")
        
        # 1. Run through LangChain Agent
        agent_result = self.agent.process_request(description, client, project)
        detected_phase = agent_result["phase"]

        # 2. Generate phase-specific document artifact
        artifact_path = self.artifact_generator.generate_artifact(
            phase=detected_phase,
            description=description,
            project=project,
            client=client
        )

        existing_requests = self.storage.load_data()
        new_id = str(len(existing_requests) + 1)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        req = FeatureRequest(
            id=new_id,
            description=description.strip(),
            client=client.strip() or "Unknown Client",
            project=project.strip() or "General Project",
            timestamp=timestamp,
            phase=detected_phase,
            confidence=agent_result["confidence"],
            artifact_path=artifact_path
        )

        self.storage.append_record(asdict(req))
        
        summary_msg = (
            f"Successfully created request #{new_id}!\n"
            f"   ↳ {agent_result['summary']}\n"
            f"   📄 Artifact Document Saved: `{artifact_path}`"
        )
        return True, summary_msg

    def get_all_requests(self) -> list:
        return self.storage.load_data()