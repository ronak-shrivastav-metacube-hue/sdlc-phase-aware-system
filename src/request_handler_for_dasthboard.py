import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Tuple
from src.storage import Storage
from src.langchain_agent import LangChainAgent
from src.artifact_generator import ArtifactGenerator
from src.monitoring import AgentMonitor  # <-- Monitoring Import

@dataclass
class FeatureRequest:
    id: str
    description: str
    client: str
    project: str
    timestamp: str
    phase: str
    confidence: str
    artifact_path: str

class RequestHandler:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.agent = LangChainAgent()
        self.artifact_generator = ArtifactGenerator()
        self.monitor = AgentMonitor()  # Initialize Monitor

    def validate_description(self, description: str) -> Tuple[bool, str]:
        """Validate description is between 10 and 500 characters."""
        desc_len = len(description.strip())
        if desc_len < 10:
            return False, "Description is too short (minimum 10 characters required)."
        if desc_len > 500:
            return False, "Description is too long (maximum 500 characters allowed)."
        return True, ""

    def add_request(self, description: str, client: str, project: str) -> Tuple[bool, str]:
        """Validate, time execution, run agent, log metrics, and persist the request."""
        is_valid, err_msg = self.validate_description(description)
        if not is_valid:
            # Log validation failure
            self.monitor.log_interaction(project=project or "Unknown", phase="none", response_time=0.0, success=False, error_msg=err_msg)
            return False, err_msg

        print("\n🤖 [Agent Working & Timing] Processing request...")
        start_time = time.time()
        
        try:
            # 1. Run LangChain Agent
            agent_result = self.agent.process_request(description, client, project)
            detected_phase = agent_result["phase"]

            # 2. Generate artifact
            artifact_path = self.artifact_generator.generate_artifact(
                phase=detected_phase,
                description=description,
                project=project,
                client=client
            )

            response_time = time.time() - start_time

            # Log successful interaction & metrics
            self.monitor.log_interaction(
                project=project,
                phase=detected_phase,
                response_time=response_time,
                success=True
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
                f"Successfully created request #{new_id} (Processed in {response_time:.2f}s)!\n"
                f"   ↳ {agent_result['summary']}\n"
                f"   📄 Artifact Document Saved: `{artifact_path}`"
            )
            return True, summary_msg

        except Exception as e:
            response_time = time.time() - start_time
            error_str = str(e)
            
            # Log failure metrics & error
            self.monitor.log_interaction(
                project=project,
                phase="error",
                response_time=response_time,
                success=False,
                error_msg=error_str
            )
            return False, f"Error processing request: {error_str}"

    def get_all_requests(self) -> list:
        return self.storage.load_data()